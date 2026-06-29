import os
import re
import unicodedata
from pathlib import Path
from typing import Any
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from sqlalchemy.orm import Session
from backend.models.comprovante import Comprovante

# Pasta de dados na raiz do projeto
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processados"

def normalizar_para_nome_arquivo(texto):
    """Limpa ruídos técnicos, remove duplicatas e sufixos de bancos."""
    if not texto or len(texto.strip()) < 1: return ""
    
    # 1. Cortar ruídos técnicos e labels
    ruido = [
        r"NOSSO\s+NUMERO.*", r"DATA\s+DE.*", r"REFERENCIA.*", r"RES\.SEF.*", 
        r"AUTENTICACAO.*", r"VALOR\s+PRINCIPAL.*", r"IMPOSTO\s*/?\s*TAXAS?", 
        r"DESCRI[CÇ][AÃ]O:?", r"DESCRI.*", r"EMPRESA\s*/\s*[ÓO]RG[ãa]O:?", 
        r"NUMERO\s+DARE.*", r"NUMERO.*", r"TIPO\s+DE.*", r"VALOR\s+DO.*",
        r"COD\s+BARRAS.*", r"COD\s+BARR.*", r"BARRAS.*", r"\bCOD\b.*", r"HORA\s+DA.*"
    ]
    texto_limpo = texto
    for padrao in ruido:
        texto_limpo = re.sub(padrao, "", texto_limpo, flags=re.I)

    # 2. Padronização de nomes comuns
    substituicoes = {
        "PREFEITURA MUNICIPAL DE ": "PREF_",
        "P.M ": "PREF_",
        "SEFAZ ": "SEFAZ_",
        "GOVERNO DO ESTADO DE ": "GOV_",
    }
    for original, novo in substituicoes.items():
        texto_limpo = texto_limpo.replace(original, novo)

    # 3. Normalização Unicode (remover acentos)
    nfd = unicodedata.normalize('NFD', texto_limpo)
    sem_acentos = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    # 4. Limpeza de pontuação e caracteres especiais
    limpo = re.sub(r'[^a-zA-Z0-9\s]', ' ', sem_acentos)
    
    # 5. Filtro de palavras irrelevantes e duplicatas
    palavras_ignore = ["DA", "DO", "DE", "OS", "AS", "PARA", "SOCIAL", "RAZAO", "BENEFICIARIO", "FINAL", "INFORMAR", "INFORMADO", "NUMERO", "PAGTO", "CONTA"]
    tokens_vistos = set()
    resultado_tokens = []
    
    for p in limpo.split():
        p_up = p.upper()
        # Ignora lixo, números longos (IDs) e palavras repetidas
        if p_up not in palavras_ignore and (not p.isdigit() or len(p) < 5) and len(p_up) > 1:
            if p_up == "DAR" and "DARE" in tokens_vistos: continue
            if p_up not in tokens_vistos:
                resultado_tokens.append(p_up)
                tokens_vistos.add(p_up)
    
    res = "_".join(resultado_tokens)
    return res[:25].rstrip("_")

def extrair_data_iso(texto):
    """Detecta datas de pagamento/débito e retorna AAAA-MM-DD"""
    texto_sem_cabecalho = re.sub(r"Impresso em.*", "", texto, flags=re.I)
    match = re.search(r"(?:Data\s+do\s+Pagamento|Data\s+de\s+d[ée]bito|Data\s+da\s+Transação)\s*:?\s*(\d{2}/\d{2}/\d{4})", texto_sem_cabecalho, re.I)
    if not match:
        match = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto_sem_cabecalho)
    if match:
        dia, mes, ano = match.group(1).split('/') if '/' in match.group(1) else match.groups()
        return f"{ano}-{mes}-{dia}"
    return "0000-00-00"

def extrair_dados_bradesco(texto_pagina):
    dados = {"identificador": "", "valor": 0.0, "data_iso": "0000-00-00", "tipo": "BOLETO", "conta": "00000-0", "bank": "BRADESCO"}
    re_conta = re.search(r"Conta:\s*([\d-]+)", texto_pagina)
    if re_conta: dados["conta"] = re_conta.group(1)
    
    re_val = re.search(r"(?:Valor do pagamento|Valor total|Valor)\s*:?\s*R\$\s*([\d.,]+)", texto_pagina, re.I)
    if not re_val:
        valores = re.findall(r"R\$\s*([\d.,]+)", texto_pagina)
        if valores: dados["valor"] = float(valores[-1].replace('.', '').replace(',', '.'))
    else:
        dados["valor"] = float(re_val.group(1).replace('.', '').replace(',', '.'))

    # Scanner de segurança para Bradesco
    orgaos = ["SEFAZ/BA", "SEFAZ/DF", "MT-SEFAZ", "SP/SEFAZ", "SEFAZ/CE", "CURITIBA", "SAO J.CAMPOS", "BRASILGAS", "SABESP", "DAE", "DARE", "DAR "]
    scanner_result = ""
    for o in orgaos:
        if o in texto_pagina.upper(): scanner_result += " " + o

    re_desc = re.search(r"Descri[cç][aã]o:\s*([^\n\r]+)", texto_pagina, re.I)
    re_org = re.search(r"(?:Empresa\s*/\s*[ÓO]rg[ãa]o|Concession[aá]ria):\s*([^\n\r]+)", texto_pagina, re.I)
    
    bruto = f"{scanner_result} {re_desc.group(1) if re_desc else ''} {re_org.group(1) if re_org else ''}"
    bruto = re.sub(r"COMUNIDADE.*", "", bruto, flags=re.I).strip()

    dados["identificador"] = normalizar_para_nome_arquivo(bruto)
    if not dados["identificador"]: dados["identificador"] = "PAGAMENTO"
    dados["data_iso"] = extrair_data_iso(texto_pagina)
    return dados

def extrair_dados_sicredi(texto_pagina):
    dados = {"identificador": "", "valor": 0.0, "data_iso": "0000-00-00", "tipo": "BOLETO", "conta": "00000-0", "bank": "SICREDI"}
    re_conta = re.search(r"Conta Corrente\s*:\s*([\d-]+)", texto_pagina, re.I)
    if re_conta: dados["conta"] = re_conta.group(1)
    
    re_val = re.search(r"(?:Valor Total|Valor Pago)\s*\(R\$\)\s*:\s*([\d.,]+)", texto_pagina, re.I)
    if not re_val:
        valores = re.findall(r"(\d{1,3}(?:\.\d{3})*,\d{2})", texto_pagina)
        if valores: dados["valor"] = float(valores[-1].replace('.', '').replace(',', '.'))
    else:
        dados["valor"] = float(re_val.group(1).replace('.', '').replace(',', '.'))
    
    texto_low = texto_pagina.lower()
    nome = ""
    if "pagamento de darf" in texto_low:
        dados["tipo"] = "DARF"
        doc_numbers = re.findall(r"\n(\d{10,20})\n", texto_pagina)
        nome = f"DARF_{doc_numbers[0]}" if doc_numbers else "DARF"
    elif "contas de consumo" in texto_low or "tributos" in texto_low:
        re_emp = re.search(r"Nome da Empresa\s*[:\-]\s*([^\n\r]+)", texto_pagina, re.I)
        nome = re_emp.group(1).strip() if re_emp else "CONSUMO"
        dados["tipo"] = "TRIBUTO" if "tributos" in texto_low else "CONSUMO"
    else:
        re_ben_f = re.search(r"Nome\s+do\s+Benefici[aá]rio\s+Final\s*:\s*(.*)", texto_pagina, re.I)
        re_ben_s = re.search(r"Raz[aã]o\s+Social\s+do\s+Benefici[aá]rio\s*:\s*(.*)", texto_pagina, re.I)
        nome = re_ben_f.group(1) if re_ben_f else (re_ben_s.group(1) if re_ben_s else "")

    dados["identificador"] = normalizar_para_nome_arquivo(nome)
    if not dados["identificador"]: dados["identificador"] = "PAGAMENTO"
    dados["data_iso"] = extrair_data_iso(texto_pagina)
    return dados

def process_pdf_file(file_path: Path, original_name: str, db: Session, banco_escolhido: str):
    processados_dir = Path(PROCESSED_DIR)
    processados_dir.mkdir(parents=True, exist_ok=True)
    stats = {"total": 0, "sucesso": 0, "duplicado": 0, "erro": 0, "detalhes": []}
    reader = PdfReader(str(file_path))

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            texto = page.extract_text() or ""
            info = extrair_dados_bradesco(texto) if banco_escolhido == "BRADESCO" else extrair_dados_sicredi(texto)

            if info["valor"] == 0 or info["data_iso"] == "0000-00-00":
                stats["erro"] += 1; continue

            # Trava de Duplicidade (Data, Banco, Conta, Valor e Identificador Final)
            id_final = info["identificador"][:25].rstrip("_")
            if db:
                ja_existe = db.query(Comprovante).filter(
                    Comprovante.bank == info["bank"], Comprovante.source_path == info["conta"],
                    Comprovante.date == info["data_iso"], Comprovante.amount == info["valor"],
                    Comprovante.description == id_final
                ).first()
                if ja_existe: stats["duplicado"] += 1; continue

            valor_str = f"{info['valor']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            nome_arquivo = f"{info['data_iso']}_{info['bank']}_{id_final}_{valor_str}.pdf"
            caminho_destino = processados_dir / re.sub(r'[\\/*?:"<>|]', "", nome_arquivo)

            count = 1
            while caminho_destino.exists():
                caminho_destino = processados_dir / f"{caminho_destino.stem}_{count}.pdf"
                count += 1

            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            with open(caminho_destino, "wb") as f: writer.write(f)

            novo_c = Comprovante(
                original_filename=original_name, saved_filename=caminho_destino.name,
                description=id_final, bank=info["bank"], comprovante_type=info["tipo"],
                amount=info["valor"], date=info["data_iso"], source_path=info["conta"], page_number=i + 1
            )
            db.add(novo_c); db.commit()
            stats["sucesso"] += 1
            stats["detalhes"].append(caminho_destino.name)

    if file_path.exists(): os.remove(file_path)
    return stats

def listar_comprovantes(db: Session):
    registros = db.query(Comprovante).order_by(Comprovante.date.desc(), Comprovante.created_at.desc()).limit(100).all()
    return [{"id": c.id, "saved_filename": c.saved_filename, "description": c.description, "amount": c.amount, "date": c.date, "account": c.source_path, "type": c.comprovante_type, "bank": c.bank} for c in registros]
