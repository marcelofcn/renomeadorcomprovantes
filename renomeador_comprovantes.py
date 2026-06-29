#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renomeador Inteligente de Comprovantes Sicredi + Bradesco - VERSÃO 6
Renomeia arquivos como: DESCRICAO_VALOR_DATA.pdf
Organiza em pastas por data para facilitar a localização
Formatos suportados (exemplos):
- PIX: PENSAO_ALIMENTICIA_AP511704_613,54_09_jun.pdf
- Boleto: INSTALACAO_0150774922_REF_MAI2_237,20_09_jun.pdf
- Consumo: CONTA_LUZ_MAIO_150,30_15_mai.pdf
- Bradesco: Usa campo "Descrição" + "Valor Total" + "Data de débito"
- DARF: DARF_123456789_1.234,56_15_mar.pdf (Número do Documento + Valor Total + Data do Pagamento)
"""

import argparse
import os
import re
import unicodedata
from pathlib import Path
import pdfplumber  # type: ignore
from PyPDF2 import PdfReader, PdfWriter  # type: ignore


def normalizar_acentos(texto):
    """Remove acentos e caracteres especiais, preservando a legibilidade."""
    # Normalizar Unicode (NFD = decomposição)
    nfd = unicodedata.normalize('NFD', texto)
    # Remover diacríticos
    sem_acentos = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    # Manter apenas letras, números e espaços
    limpo = re.sub(r'[^a-zA-Z0-9\s]', '', sem_acentos)
    return limpo


def identificar_tipo_comprovante(texto):
    """
    Identifica o tipo de comprovante baseado em palavras-chave no texto.
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        str: Tipo do comprovante (darf, bradesco, pix, boleto, consumo, desconhecido)
    """
    texto_lower = texto.lower()
    
    # Identificando comprovante DARF (verificar primeiro por ser mais específico)
    if "comprovante da pagamento de darf" in texto_lower or "comprovante de pagamento de darf" in texto_lower:
        return "darf"
    # Identificando comprovante Bradesco
    elif "bradesco" in texto_lower or "data de débito" in texto_lower or "data de crédito" in texto_lower or "comprovante de transação bancária" in texto_lower:
        return "bradesco"
    # Identificando comprovante de pagamento PIX
    elif "comprovante de pagamento pix" in texto_lower:
        return "pix"
    elif "razão social do beneficiário" in texto_lower:
        return "boleto"
    elif "nome da empresa" in texto_lower:
        return "consumo"
    else:
        return "desconhecido"


def extrair_dados_bradesco(texto):
    """
    Função específica para extrair dados de comprovantes Bradesco.
    Suporta: utilidades (água/luz), impostos (DARF), boletos.
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        tuple: (descricao, valor, data)
    """
    linhas = texto.splitlines()
    
    descricao = "sem_descricao"
    valor = "0.00"
    data = ""
    
    # ============ EXTRAÇÃO DE DESCRIÇÃO ============
    # 1. Procurar por "Descrição:" (DARF/Impostos)
    for i, linha in enumerate(linhas):
        if re.search(r"descri[cç][aã]o\s*:?", linha, re.I):
            descricao_match = re.search(r"descri[cç][aã]o\s*:?\s*(.+)", linha, re.I)
            if descricao_match and descricao_match.group(1).strip():
                descricao = descricao_match.group(1).strip()
                break
    
    # 2. Se não achou, procurar por "Nome Fantasia", "Beneficiário Final"
    if descricao == "sem_descricao":
        for i, linha in enumerate(linhas):
            if re.search(r"nome\s+fantasia|benefici[aá]rio\s+final", linha, re.I):
                for j in range(i + 1, len(linhas)):
                    proxima = linhas[j].strip()
                    if proxima and not re.search(r"cpf|cnpj|data|valor", proxima, re.I):
                        descricao = proxima
                        break
                if descricao != "sem_descricao":
                    break
    
    # 3. Se não achou, procurar por tipos de serviço (Água, Luz, etc.)
    if descricao == "sem_descricao":
        for linha in linhas:
            if re.search(r"água|luz|telefone|gás|gas", linha, re.I) and not re.search(r"valor|data|r\$", linha, re.I):
                descricao = linha.strip()
                break
    
    # 4. Se não achou, procurar por Concessionária
    if descricao == "sem_descricao":
        for linha in linhas:
            if re.search(r"concession[aá]ria\s*:?", linha, re.I):
                concessionaria_match = re.search(r"concession[aá]ria\s*:?\s*(.+)", linha, re.I)
                if concessionaria_match:
                    descricao = concessionaria_match.group(1).strip()
                    break
    
    # 5. Fallback: pegar primeira linha relevante
    if descricao == "sem_descricao":
        for linha in linhas:
            linha_strip = linha.strip()
            if linha_strip and not re.search(r"^(comprovante|data|agência|banco|conta|código|referência|autenticação|n°|n\u00ba)", linha_strip, re.I):
                descricao = linha_strip
                break
    
    # ============ EXTRAÇÃO DE VALOR ============
    # 1. Procurar por "Valor total:" (mais específico)
    for linha in linhas:
        if re.search(r"valor\s+total\s*:?", linha, re.I):
            valor_match = re.search(r"r?\$?\s*([\d.,]+)", linha, re.I)
            if valor_match:
                valor_raw = valor_match.group(1).strip()
                if re.search(r'\d+[.,]\d+', valor_raw) or re.search(r'\d{3,}', valor_raw):
                    if ',' in valor_raw:
                        valor = valor_raw.replace('.', '').replace(',', '.')
                    else:
                        valor = valor_raw
                    try:
                        if float(valor) > 1.0:
                            break
                    except ValueError:
                        valor = "0.00"
    
    # 2. Procurar por "Valor do pagamento:" (segunda opção)
    if valor == "0.00":
        for linha in linhas:
            if re.search(r"valor\s+do\s+pagamento\s*:?", linha, re.I):
                valor_match = re.search(r"r?\$?\s*([\d.,]+)", linha, re.I)
                if valor_match:
                    valor_raw = valor_match.group(1).strip()
                    if re.search(r'\d+[.,]\d+', valor_raw):
                        if ',' in valor_raw:
                            valor = valor_raw.replace('.', '').replace(',', '.')
                        else:
                            valor = valor_raw
                        try:
                            if float(valor) > 1.0:
                                break
                        except ValueError:
                            valor = "0.00"
    
    # 3. Procurar por "Valor principal:" (terceira opção)
    if valor == "0.00":
        for linha in linhas:
            if re.search(r"valor\s+principal\s*:?", linha, re.I):
                valor_match = re.search(r"r?\$?\s*([\d.,]+)", linha, re.I)
                if valor_match:
                    valor_raw = valor_match.group(1).strip()
                    if re.search(r'\d+[.,]\d+', valor_raw):
                        if ',' in valor_raw:
                            valor = valor_raw.replace('.', '').replace(',', '.')
                        else:
                            valor = valor_raw
                        try:
                            if float(valor) > 1.0:
                                break
                        except ValueError:
                            valor = "0.00"
    
    # 4. Procurar por padrão genérico "Valor R$"
    if valor == "0.00":
        for linha in linhas:
            if re.search(r"valor\s+r?\$", linha, re.I):
                valor_match = re.search(r"r?\$?\s*([\d.,]+)", linha, re.I)
                if valor_match:
                    valor_raw = valor_match.group(1).strip()
                    if re.search(r'\d+[.,]\d+', valor_raw):
                        if ',' in valor_raw:
                            valor = valor_raw.replace('.', '').replace(',', '.')
                        else:
                            valor = valor_raw
                        try:
                            if float(valor) > 1.0:
                                break
                        except ValueError:
                            valor = "0.00"
    
    # ============ EXTRAÇÃO DE DATA ============
    # Procurar por "Data de débito:", "Data de vencimento:", "Data da operação:"
    for linha in linhas:
        data_match = re.search(r"data\s+(?:de|do|da)\s+(?:d[ée]bito|vencimento|op[eé]ração|operacao)\s*:?\s*(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})", linha, re.I)
        if data_match:
            dia, mes, ano = data_match.groups()
            meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                    'jul', 'ago', 'set', 'out', 'nov', 'dez']
            try:
                mes_num = int(mes)
                if 1 <= mes_num <= 12:
                    data = f"{dia.zfill(2)}_{meses[mes_num-1]}"
                    break
            except:
                continue
    
    # Limpar e formatar a descrição
    descricao = normalizar_acentos(descricao)
    descricao = "_".join(descricao.split()).upper()
    if not descricao or descricao == "":
        descricao = "SEM_DESCRICAO"
    
    return descricao, valor, data


def extrair_dados_darf(texto):
    """
    Função específica para extrair dados de comprovantes DARF do Sicredi.
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        tuple: (descricao, valor, data)
    """
    linhas = texto.splitlines()
    
    print("\n[DEPURAÇÃO DARF] Linhas extraídas:")
    for i, linha in enumerate(linhas):
        print(f"Linha {i + 1}: '{linha.strip()}'")
    
    descricao = "DARF"
    valor = "0.00"
    data = ""
    
    # No DARF, os valores aparecem ANTES dos rótulos
    # Procurar pelo "Número do Documento:" e pegar linha ANTERIOR
    for i, linha in enumerate(linhas):
        if re.search(r"n[uú]mero\s+do\s+documento\s*:?", linha, re.I):
            print(f"[DEPURAÇÃO DARF] Encontrou 'Número do Documento' na linha {i + 1}")
            # O número está na linha ANTERIOR
            if i > 0:
                linha_anterior = linhas[i - 1].strip()
                # Extrair apenas números
                numero_doc = re.sub(r'\D', '', linha_anterior)
                if numero_doc:
                    descricao = f"DARF_{numero_doc}"
                    print(f"[DEPURAÇÃO DARF] Número do Documento encontrado na linha anterior: '{numero_doc}'")
            break
    
    # Procurar pelo "Valor Total (R$):" e pegar linha ANTERIOR
    for i, linha in enumerate(linhas):
        if re.search(r"valor\s+total\s*\(\s*r\$\s*\)\s*:?", linha, re.I):
            print(f"[DEPURAÇÃO DARF] Encontrou 'Valor Total (R$)' na linha {i + 1}")
            # O valor está na linha ANTERIOR
            if i > 0:
                linha_anterior = linhas[i - 1].strip()
                # Extrair valor com vírgula e pontos
                valor_match = re.search(r"([\d.,]+)", linha_anterior)
                if valor_match:
                    valor_raw = valor_match.group(1)
                    # Converter para formato float
                    if ',' in valor_raw:
                        valor = valor_raw.replace('.', '').replace(',', '.')
                    else:
                        valor = valor_raw
                    print(f"[DEPURAÇÃO DARF] Valor Total encontrado na linha anterior: '{valor_raw}' -> '{valor}'")
            break
    
    # Procurar pela "Data do Pagamento:" e pegar linha ANTERIOR
    for i, linha in enumerate(linhas):
        if re.search(r"data\s+do\s+pagamento\s*:?", linha, re.I):
            print(f"[DEPURAÇÃO DARF] Encontrou 'Data do Pagamento' na linha {i + 1}")
            # A data está na linha ANTERIOR
            if i > 0:
                linha_anterior = linhas[i - 1].strip()
                data_match = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", linha_anterior)
                if data_match:
                    dia, mes, ano = data_match.groups()
                    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                            'jul', 'ago', 'set', 'out', 'nov', 'dez']
                    try:
                        mes_num = int(mes)
                        if 1 <= mes_num <= 12:
                            data = f"{dia.zfill(2)}_{meses[mes_num-1]}"
                            print(f"[DEPURAÇÃO DARF] Data do Pagamento encontrada na linha anterior: '{linha_anterior}' -> '{data}'")
                    except:
                        pass
            break
    
    print(f"[DEPURAÇÃO DARF] Resultado final - Descrição: '{descricao}', Valor: '{valor}', Data: '{data}'")
    
    return descricao, valor, data


def extrair_dados_pix(texto):
    """
    Função específica para extrair dados de comprovantes PIX.
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        tuple: (descricao, valor, data)
    """
    linhas = texto.splitlines()
    
    print("\n[DEPURAÇÃO PIX] Linhas extraídas:")
    for i, linha in enumerate(linhas):
        print(f"Linha {i + 1}: '{linha.strip()}'")
    
    descricao = "sem_descricao"
    valor = "0.00"
    data = ""
    
    # Procurar pela linha com "Comprovante de Pagamento Pix"
    idx_comprovante = -1
    for i, linha in enumerate(linhas):
        if "comprovante de pagamento pix" in linha.lower():
            idx_comprovante = i
            print(f"[DEPURAÇÃO PIX] Encontrou 'Comprovante de Pagamento Pix' na linha {i + 1}")
            break
    
    if idx_comprovante >= 0:
        # Procurar a descrição na próxima linha não vazia
        for i in range(idx_comprovante + 1, len(linhas)):
            linha_atual = linhas[i].strip()
            if linha_atual and not linha_atual.lower().startswith("valor") and not linha_atual.lower().startswith("realizado em"):
                descricao = linha_atual
                print(f"[DEPURAÇÃO PIX] Descrição encontrada na linha {i + 1}: '{descricao}'")
                break
        
        # Procurar o valor em qualquer linha que contenha "valor"
        for linha in linhas:
            if "valor" in linha.lower() and "r$" in linha.lower():
                padroes_valor = [
                    r"valor[:\s]*r\$\s*([\d.,]+)",
                    r"r\$\s*([\d.,]+)",
                    r"([\d.,]+)"
                ]
                
                for padrao in padroes_valor:
                    valor_match = re.search(padrao, linha, re.I)
                    if valor_match:
                        valor_raw = valor_match.group(1)
                        if ',' in valor_raw:
                            valor = valor_raw.replace('.', '').replace(',', '.')
                        else:
                            valor = valor_raw
                        print(f"[DEPURAÇÃO PIX] Valor encontrado: '{valor_raw}' -> '{valor}'")
                        break
                
                if valor != "0.00":
                    break
        
        # Procurar a data no campo "Realizado em:"
        for linha in linhas:
            if "realizado em" in linha.lower():
                padroes_data = [
                    r"realizado em[:\s]*(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})",
                    r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})"
                ]
                
                for padrao in padroes_data:
                    data_match = re.search(padrao, linha, re.I)
                    if data_match:
                        dia, mes, ano = data_match.groups()
                        meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                                'jul', 'ago', 'set', 'out', 'nov', 'dez']
                        try:
                            mes_num = int(mes)
                            if 1 <= mes_num <= 12:
                                data = f"{dia.zfill(2)}_{meses[mes_num-1]}"
                                print(f"[DEPURAÇÃO PIX] Data encontrada: '{linha}' -> '{data}'")
                                break
                        except:
                            continue
                
                if data:
                    break
    
    # Limpar e formatar a descrição
    descricao = re.sub(r'[^a-zA-Z0-9\s_]', '', descricao)
    descricao = "_".join(descricao.split())
    
    print(f"[DEPURAÇÃO PIX] Resultado final - Descrição: '{descricao}', Valor: '{valor}', Data: '{data}'")
    
    return descricao, valor, data


def extrair_dados_boleto(texto):
    """
    Função específica para extrair dados de comprovantes de Boleto.
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        tuple: (descricao, valor, data)
    """
    linhas = texto.splitlines()
    
    print("\n[DEPURAÇÃO BOLETO] Linhas extraídas:")
    for i, linha in enumerate(linhas):
        print(f"Linha {i + 1}: '{linha.strip()}'")
    
    descricao = "sem_descricao"
    valor = "0.00"
    data = ""
    
    # Procurar pela "Razão Social do Beneficiário"
    for i, linha in enumerate(linhas):
        if "razão social do beneficiário" in linha.lower() or "razao social do beneficiario" in linha.lower():
            print(f"[DEPURAÇÃO BOLETO] Encontrou 'Razão Social' na linha {i + 1}")
            # A razão social normalmente está na próxima linha
            if i + 1 < len(linhas):
                descricao = linhas[i + 1].strip()
                print(f"[DEPURAÇÃO BOLETO] Razão Social encontrada: '{descricao}'")
            break
    
    # Procurar pelo valor
    for linha in linhas:
        if "valor" in linha.lower() and "r$" in linha.lower():
            valor_match = re.search(r"r?\$?\s*([\d.,]+)", linha, re.I)
            if valor_match:
                valor_raw = valor_match.group(1)
                if ',' in valor_raw:
                    valor = valor_raw.replace('.', '').replace(',', '.')
                else:
                    valor = valor_raw
                print(f"[DEPURAÇÃO BOLETO] Valor encontrado: '{valor_raw}' -> '{valor}'")
                break
    
    # Procurar pela data de vencimento ou pagamento
    for linha in linhas:
        if "vencimento" in linha.lower() or "pagamento" in linha.lower():
            data_match = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})", linha)
            if data_match:
                dia, mes, ano = data_match.groups()
                meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                        'jul', 'ago', 'set', 'out', 'nov', 'dez']
                try:
                    mes_num = int(mes)
                    if 1 <= mes_num <= 12:
                        data = f"{dia.zfill(2)}_{meses[mes_num-1]}"
                        print(f"[DEPURAÇÃO BOLETO] Data encontrada: '{linha}' -> '{data}'")
                        break
                except:
                    continue
    
    # Limpar e formatar a descrição
    descricao = re.sub(r'[^a-zA-Z0-9\s_]', '', descricao)
    descricao = "_".join(descricao.split())
    
    print(f"[DEPURAÇÃO BOLETO] Resultado final - Descrição: '{descricao}', Valor: '{valor}', Data: '{data}'")
    
    return descricao, valor, data


def extrair_dados_consumo(texto):
    """
    Função específica para extrair dados de comprovantes de Consumo (Luz, Água, etc).
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        tuple: (descricao, valor, data)
    """
    linhas = texto.splitlines()
    
    print("\n[DEPURAÇÃO CONSUMO] Linhas extraídas:")
    for i, linha in enumerate(linhas):
        print(f"Linha {i + 1}: '{linha.strip()}'")
    
    descricao = "sem_descricao"
    valor = "0.00"
    data = ""
    
    # Procurar pelo "Nome da Empresa"
    for i, linha in enumerate(linhas):
        if "nome da empresa" in linha.lower():
            print(f"[DEPURAÇÃO CONSUMO] Encontrou 'Nome da Empresa' na linha {i + 1}")
            if i + 1 < len(linhas):
                descricao = linhas[i + 1].strip()
                print(f"[DEPURAÇÃO CONSUMO] Nome da Empresa encontrado: '{descricao}'")
            break
    
    # Procurar pelo valor total
    for linha in linhas:
        if "total" in linha.lower() and ("r$" in linha.lower() or "valor" in linha.lower()):
            valor_match = re.search(r"r?\$?\s*([\d.,]+)", linha, re.I)
            if valor_match:
                valor_raw = valor_match.group(1)
                if ',' in valor_raw:
                    valor = valor_raw.replace('.', '').replace(',', '.')
                else:
                    valor = valor_raw
                print(f"[DEPURAÇÃO CONSUMO] Valor encontrado: '{valor_raw}' -> '{valor}'")
                break
    
    # Procurar pela data
    for linha in linhas:
        if "vencimento" in linha.lower() or "data" in linha.lower():
            data_match = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})", linha)
            if data_match:
                dia, mes, ano = data_match.groups()
                meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                        'jul', 'ago', 'set', 'out', 'nov', 'dez']
                try:
                    mes_num = int(mes)
                    if 1 <= mes_num <= 12:
                        data = f"{dia.zfill(2)}_{meses[mes_num-1]}"
                        print(f"[DEPURAÇÃO CONSUMO] Data encontrada: '{linha}' -> '{data}'")
                        break
                except:
                    continue
    
    # Limpar e formatar a descrição
    descricao = re.sub(r'[^a-zA-Z0-9\s_]', '', descricao)
    descricao = "_".join(descricao.split())
    
    print(f"[DEPURAÇÃO CONSUMO] Resultado final - Descrição: '{descricao}', Valor: '{valor}', Data: '{data}'")
    
    return descricao, valor, data


def formatar_valor_saida(valor_str):
    """
    Formata o valor para o formato de saída (1.234,56).
    
    Args:
        valor_str (str): Valor no formato interno (1234.56)
        
    Returns:
        str: Valor formatado (1.234,56)
    """
    try:
        valor_float = float(valor_str)
        # Formatar com separador de milhar e vírgula decimal
        valor_formatado = f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return valor_formatado
    except:
        return valor_str


def processar_pdf(caminho_pdf):
    """
    Processa um arquivo PDF e retorna o nome sugerido.
    
    Args:
        caminho_pdf (str): Caminho do arquivo PDF
        
    Returns:
        str: Nome sugerido para o arquivo ou None se falhar
    """
    print(f"\n{'='*60}")
    print(f"Processando: {caminho_pdf}")
    print(f"{'='*60}")
    
    try:
        # Extrair texto do PDF
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() + "\n"
        
        # Identificar tipo de comprovante
        tipo = identificar_tipo_comprovante(texto_completo)
        print(f"\nTipo identificado: {tipo.upper()}")
        
        # Extrair dados conforme o tipo
        if tipo == "darf":
            descricao, valor, data = extrair_dados_darf(texto_completo)
        elif tipo == "bradesco":
            descricao, valor, data = extrair_dados_bradesco(texto_completo)
        elif tipo == "pix":
            descricao, valor, data = extrair_dados_pix(texto_completo)
        elif tipo == "boleto":
            descricao, valor, data = extrair_dados_boleto(texto_completo)
        elif tipo == "consumo":
            descricao, valor, data = extrair_dados_consumo(texto_completo)
        else:
            print("⚠️  Tipo de comprovante não reconhecido!")
            return None
        
        # Validar dados extraídos
        if not descricao or descricao == "sem_descricao":
            print("⚠️  Descrição não encontrada!")
            return None
        
        if not data:
            print("⚠️  Data não encontrada!")
            return None
        
        # Formatar valor para saída
        valor_formatado = formatar_valor_saida(valor)
        
        # Montar nome do arquivo
        nome_sugerido = f"{descricao}_{valor_formatado}_{data}.pdf"
        
        print(f"\n✅ Nome sugerido: {nome_sugerido}")
        
        return nome_sugerido
        
    except Exception as e:
        print(f"❌ Erro ao processar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def mover_para_processados(arquivo_path):
    """
    Move um arquivo para a pasta data/processados/.
    
    Args:
        arquivo_path (Path): Caminho do arquivo a mover
        
    Returns:
        bool: True se movido com sucesso, False caso contrário
    """
    try:
        # Definir pasta de processados
        pasta_processados = Path(__file__).resolve().parent / "data" / "processados"
        pasta_processados.mkdir(parents=True, exist_ok=True)
        
        # Novo caminho no diretório processados
        novo_caminho = pasta_processados / arquivo_path.name
        
        # Evitar sobrescrever arquivos
        contador = 1
        while novo_caminho.exists():
            nome_base = arquivo_path.stem
            novo_caminho = pasta_processados / f"{nome_base}_{contador}.pdf"
            contador += 1
        
        # Mover arquivo
        arquivo_path.rename(novo_caminho)
        print(f"📂 Movido para: {novo_caminho}")
        return True
    except Exception as e:
        print(f"❌ Erro ao mover arquivo: {str(e)}")
        return False


def renomear_arquivos_na_pasta(pasta="."):
    """
    Renomeia todos os arquivos PDF na pasta especificada e move para processados.
    
    Args:
        pasta (str): Caminho da pasta a processar (padrão: pasta atual)
    """
    pasta_path = Path(pasta)
    arquivos_pdf = [
        arquivo for arquivo in pasta_path.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() == ".pdf"
    ]
    
    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return
    
    print(f"\n📁 Encontrados {len(arquivos_pdf)} arquivos PDF\n")
    
    processados = 0
    falhas = 0
    
    for arquivo in arquivos_pdf:
        nome_original = arquivo.name
        
        # Pular se já parece ter sido renomeado
        if re.match(r".+_[\d.,]+_\d{2}_[a-z]{3}\.pdf", nome_original, re.I):
            print(f"⏭️  Pulando (já renomeado): {nome_original}")
            continue
        
        nome_sugerido = processar_pdf(str(arquivo))
        
        if nome_sugerido:
            novo_caminho = arquivo.parent / nome_sugerido
            
            # Evitar sobrescrever arquivos na pasta temporária
            contador = 1
            while novo_caminho.exists():
                nome_base = nome_sugerido.replace('.pdf', '')
                novo_caminho = arquivo.parent / f"{nome_base}_{contador}.pdf"
                contador += 1
            
            try:
                # Renomear na pasta original
                arquivo.rename(novo_caminho)
                print(f"✅ Renomeado com sucesso!")
                print(f"   De: {nome_original}")
                print(f"   Para: {novo_caminho.name}")
                
                # Mover para pasta processados
                if mover_para_processados(novo_caminho):
                    processados += 1
                else:
                    # Se falhar ao mover, renomear de volta
                    novo_caminho.rename(arquivo.parent / nome_original)
                    falhas += 1
                print()
            except Exception as e:
                print(f"❌ Erro ao renomear: {str(e)}\n")
                falhas += 1
        else:
            falhas += 1
    
    # Resumo
    print(f"\n{'='*60}")
    print(f"RESUMO:")
    print(f"✅ Processados com sucesso: {processados}")
    print(f"❌ Falhas: {falhas}")
    print(f"📊 Total: {len(arquivos_pdf)}")
    print(f"{'='*60}\n")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Renomeador Inteligente de Comprovantes")
    parser.add_argument(
        "--folder",
        type=str,
        default=".",
        help="Caminho da pasta que contém os PDFs (padrão: pasta atual)"
    )
    args = parser.parse_args()

    print("\n" + "="*60)
    print("RENOMEADOR INTELIGENTE DE COMPROVANTES - v6")
    print(f"Pasta alvo: {args.folder}")
    print("="*60)
    
    renomear_arquivos_na_pasta(args.folder)


if __name__ == "__main__":
    main()
