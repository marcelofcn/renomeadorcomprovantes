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
    """Limpa ruídos técnicos, códigos de bancos (ex: 78414067) e preserva o nome real."""
    if not texto: return ""
    
    # 1. Eliminar termos técnicos e códigos de instituições conhecidos
    ruido = [
        r"NOSSO\s+NUMERO.*", r"DATA\s+DE.*", r"REFERENCIA.*", r"RES\.SEF.*", 
        r"AUTENTICACAO.*", r"VALOR\s+PRINCIPAL.*", r"IMPOSTO\s*/?\s*TAXAS?", 
        r"DESCRI[CÇ][AÃ]O:?", r"DESCRI.*", r"EMPRESA\s*/\s*[ÓO]RG[ãa]O:?", 
        r"NUMERO\s+DARE.*", r"NUMERO.*", r"TIPO\s+DE.*", r"VALOR\s+DO.*",
        r"COD\s+BARRAS.*", r"COD\s+BARR.*", r"BARRAS.*", r"\b78414067\b", r"\b00000000\b"
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
        "COOP SICREDI VANGUARDA PR/SP/RJ": "SICREDI",
        "BANCO DO BRASIL": "BB"
    }
    for original, novo in substituicoes.items():
        texto_limpo = texto_limpo.replace(original, novo)

    # 3. Normalização Unicode (acentos)
    nfd = unicodedata.normalize('NFD', texto_limpo)
    sem_acentos = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    limpo = re.sub(r'[^a-zA-Z0-9\s]', ' ', sem_acentos)
    
    # 4. Filtro de palavras: Remove lixo e duplicatas
    palavras_ignore = ["DA", "DO", "DE", "OS", "AS", "PARA", "SOCIAL", "RAZAO", "BENEFICIARIO", "FINAL", "INFORMAR", "INFORMADO", "NUMERO", "PAGTO", "CONTA"]
    tokens_vistos = set()
    resultado_tokens = []
    
    for p in limpo.split():
        p_up = p.upper()
        # Regra: ignora lixo, números longos (>8 dígitos) e duplicados
        if p_up not in palavras_ignore and (not p.isdigit() or len(p) < 9) and (len(p_up) > 1 or p_up == "J"):
            if p_up not in tokens_vistos:
                resultado_tokens.append(p_up)
                tokens_vistos.add(p_up)
    
    res = "_".join(resultado_tokens)
    return res[:30].rstrip("_")

def extrair_data_iso(texto, banco_escolhido=""):
    """Detecta a data real do pagamento."""
    texto_util = texto
    if banco_escolhido == "BANCO_DO_BRASIL":
        linhas = texto.split('\n')
        if len(linhas) > 10: texto_util = "\n".join(linhas[10:])
    else:
        texto_util = re.sub(r"Impresso em.*", "", texto, flags=re.I)

    match = re.search(r"(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})", texto_util)
    if match:
        dia, mes, ano = match.groups()
        return f"{ano}-{mes}-{dia}"
    return "0000-00-00"

def identificar_banco_pelo_texto(texto):
    """Valida a seleção do usuário contra o conteúdo do PDF."""
    texto_topo = texto[:1000].upper()
    if "ASSOCIADO:" in texto_topo and "COOPERATIVA:" in texto_topo: return "SICREDI"
    if "BRADESCO" in texto_topo or "OFFICE BANKING BRAD" in texto_topo: return "BRADESCO"
    if "BANCO DO BRASIL" in texto_topo or "SISBB" in texto_topo: return "BANCO_DO_BRASIL"
    return "DESCONHECIDO"

def extrair_dados_bb(texto_pagina):
    """Extração SISBB (IPVA, Transferências, PIX)"""
    dados = {"identificador": "", "valor": 0.0, "data_iso": "0000-00-00", "tipo": "BOLETO", "conta": "00000-0", "bank": "BANCO_DO_BRASIL", "dest_bank": "", "dest_account": ""}
    re_conta = re.search(r"CONTA:\s*([\d.X-]+)", texto_pagina, re.I)
    if re_conta: dados["conta"] = re_conta.group(1).replace(".", "")
    re_val = re.search(r"(?:TOTAL|VALOR TOTAL|VALOR:)\s*(?:R\$)?\s*([\d.,]+)", texto_pagina, re.I)
    if re_val: dados["valor"] = float(re_val.group(1).replace('.', '').replace(',', '.'))
    dados["data_iso"] = extrair_data_iso(texto_pagina, "BANCO_DO_BRASIL")
    
    if "IPVA" in texto_pagina.upper():
        dados["tipo"] = "TRIBUTO"; dados["identificador"] = "IPVA_SEFAZ_SP"
    else:
        re_nome = re.search(r"(?:PAGO PARA:|CLIENTE:|TRANSFERIDO PARA:)\s*([^\n\r]+)", texto_pagina, re.I)
        nome_dest = re_nome.group(1).strip() if re_nome else "TRANSF"
        if any(x in texto_pagina.upper() for x in ["04.251.333", "C C NOVA", "COMUNIDADE CANCAO NOVA"]):
            dados["tipo"] = "TRANSFERENCIA_INTERNA"
            re_banco_dest = re.search(r"INSTITUICAO:\s*([^\n\r]+)", texto_pagina, re.I)
            re_conta_dest = re.search(r"CONTA:\s*([\d.X-]+)", texto_pagina[texto_pagina.find("PARA"):], re.I)
            dados["dest_bank"] = re_banco_dest.group(1).strip() if re_banco_dest else "BB"
            dados["dest_account"] = re_conta_dest.group(1).replace(".", "") if re_conta_dest else ""
            dados["identificador"] = f"TRANSF_{normalizar_para_nome_arquivo(dados['dest_bank'])}"
        else:
            dados["tipo"] = "PIX"; dados["identificador"] = normalizar_para_nome_arquivo(nome_dest)
    return dados

def extrair_dados_bradesco(texto_pagina):
    """Extração Bradesco (Pix, Boleto, Consumo)"""
    dados = {"identificador": "PAGAMENTO", "valor": 0.0, "data_iso": "0000-00-00", "tipo": "BOLETO", "conta": "00000-0", "bank": "BRADESCO", "dest_bank": "", "dest_account": ""}
    re_conta = re.search(r"Conta\s*:\s*([\d-]+)", texto_pagina, re.I)
    if re_conta: dados["conta"] = re_conta.group(1)
    re_val = re.search(r"(?:Valor|Valor total|Valor do pagamento)\s*:?\s*R\$\s*([\d.,]+)", texto_pagina, re.I)
    if re_val: dados["valor"] = float(re_val.group(1).replace('.', '').replace(',', '.'))
    
    re_conc = re.search(r"Concession[aá]ria\s*:\s*([^\n\r]+)", texto_pagina, re.I)
    re_desc = re.search(r"Descri[cç][aã]o:\s*([^\n\r]+)", texto_pagina, re.I)
    nome = re_conc.group(1).strip() if re_conc else (re_desc.group(1).strip() if re_desc else "PAGAMENTO")
    if re_conc: dados["tipo"] = "CONSUMO"

    if "PIX" in texto_pagina.upper():
        re_cnpj_dest = re.search(r"CPF/CNPJ:\s*([\d./-]+)", texto_pagina)
        if re_cnpj_dest and "04.251.333" in re_cnpj_dest.group(1):
            dados["tipo"] = "TRANSFERENCIA_INTERNA"
            re_banco_dest = re.search(r"Institui[cç][ãa]o destino:\s*(.*?)\n", texto_pagina, re.I)
            re_conta_dest = re.search(r"Dados de quem\s+recebeu.*?Conta:\s*([\d-]+)", texto_pagina, re.S | re.I)
            dados["dest_bank"] = re_banco_dest.group(1).strip() if re_banco_dest else ""
            dados["dest_account"] = re_conta_dest.group(1).strip() if re_conta_dest else ""

    dados["identificador"] = normalizar_para_nome_arquivo(nome)
    dados["data_iso"] = extrair_data_iso(texto_pagina, "BRADESCO")
    return dados

def extrair_dados_sicredi(texto_pagina):
    """Extração Sicredi (DARF, Consumo, Boletos)"""
    dados = {"identificador": "PAGAMENTO", "valor": 0.0, "data_iso": "0000-00-00", "tipo": "BOLETO", "conta": "00000-0", "bank": "SICREDI", "dest_bank": "", "dest_account": ""}
    re_conta = re.search(r"Conta Corrente\s*:\s*([\d-]+)", texto_pagina, re.I)
    if re_conta: dados["conta"] = re_conta.group(1)
    re_val = re.search(r"(?:Valor Total|Valor Pago)\s*\(R\$\)\s*:\s*([\d.,]+)", texto_pagina, re.I)
    if re_val: dados["valor"] = float(re_val.group(1).replace('.', '').replace(',', '.'))
    
    texto_low = texto_pagina.lower()
    if "pagamento de darf" in texto_low:
        dados["tipo"] = "DARF"
        doc = re.findall(r"\n(\d{10,20})\n", texto_pagina)
        nome = f"DARF_{doc[0]}" if doc else "DARF"
    elif "contas de consumo" in texto_low or "tributos" in texto_low:
        re_emp = re.search(r"Nome da Empresa\s*[:\-]\s*([^\n\r]+)", texto_pagina, re.I)
        match_trib = re.search(r"(IPTU|IPVA|ISS|ICMS|DAS|DARE|DAE|VIVO|CLARO|BRASILGAS|SABESP)", texto_pagina, re.I)
        nome = f"{re_emp.group(1) if re_emp else ''} {match_trib.group(1) if match_trib else ''}"
        dados["tipo"] = "TRIBUTO" if "tributos" in texto_low else "CONSUMO"
    else:
        re_ben_f = re.search(r"Nome\s+do\s+Benefici[aá]rio\s+Final\s*:\s*(.*)", texto_pagina, re.I)
        re_ben_s = re.search(r"Raz[aã]o\s+Social\s+do\s+Benefici[aá]rio\s*:\s*(.*)", texto_pagina, re.I)
        nome = re_ben_f.group(1) if re_ben_f else (re_ben_s.group(1) if re_ben_s else "PAGAMENTO")
    
    dados["identificador"] = normalizar_para_nome_arquivo(nome)
    dados["data_iso"] = extrair_data_iso(texto_pagina, "SICREDI")
    return dados

def process_pdf_file(file_path: Path, original_name: str, db: Session, banco_escolhido: str):
    processados_dir = Path(PROCESSED_DIR); processados_dir.mkdir(parents=True, exist_ok=True)
    stats = {"total": 0, "sucesso": 0, "duplicado": 0, "erro": 0, "detalhes": [], "banco_invalido": False}
    reader = PdfReader(str(file_path)); stats["total"] = len(reader.pages)
    with pdfplumber.open(file_path) as pdf:
        # Trava de Segurança
        primeira_p = pdf.pages[0].extract_text() or ""
        banco_det = identificar_banco_pelo_texto(primeira_p)
        if banco_det != "DESCONHECIDO" and banco_det != banco_escolhido:
            stats["banco_invalido"] = True; stats["banco_detectado"] = banco_det; return stats

        for i, page in enumerate(pdf.pages):
            texto = page.extract_text() or ""
            if banco_escolhido == "BANCO_DO_BRASIL": info = extrair_dados_bb(texto)
            elif banco_escolhido == "BRADESCO": info = extrair_dados_bradesco(texto)
            else: info = extrair_dados_sicredi(texto)

            if info["valor"] == 0 or info["data_iso"] == "0000-00-00":
                stats["erro"] += 1; continue

            id_final = info["identificador"]
            if db:
                ja_existe = db.query(Comprovante).filter(Comprovante.bank == info["bank"], Comprovante.source_path == info["conta"], Comprovante.date == info["data_iso"], Comprovante.amount == info["valor"], Comprovante.description == id_final).first()
                if ja_existe: stats["duplicado"] += 1; continue

            val_fmt = f"{info['valor']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            nome_arq = f"{info['data_iso']}_{info['bank']}_{id_final}_{val_fmt}.pdf"
            caminho_dest = processados_dir / re.sub(r'[\\/*?:"<>|]', "", nome_arq)
            
            count = 1
            while caminho_dest.exists():
                caminho_dest = processados_dir / f"{caminho_dest.stem}_{count}.pdf"; count += 1

            writer = PdfWriter(); writer.add_page(reader.pages[i])
            with open(caminho_dest, "wb") as f: writer.write(f)
            db.add(Comprovante(original_filename=original_name, saved_filename=caminho_dest.name, description=id_final, bank=info["bank"], comprovante_type=info["tipo"], amount=info["valor"], date=info["data_iso"], source_path=info["conta"], dest_bank=info.get("dest_bank"), dest_account=info.get("dest_account"), page_number=i + 1))
            db.commit(); stats["sucesso"] += 1; stats["detalhes"].append(caminho_dest.name)
    if file_path.exists(): os.remove(file_path)
    return stats

def listar_comprovantes(db: Session):
    registros = db.query(Comprovante).order_by(Comprovante.date.desc(), Comprovante.created_at.desc()).limit(100).all()
    return [{"id": c.id, "saved_filename": c.saved_filename, "description": c.description, "amount": c.amount, "date": c.date, "account": c.source_path, "type": c.comprovante_type, "bank": c.bank, "dest_bank": c.dest_bank, "dest_account": c.dest_account} for c in registros]