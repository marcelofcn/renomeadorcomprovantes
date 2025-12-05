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

import os
import re
from pathlib import Path
import pdfplumber  # type: ignore
from PyPDF2 import PdfReader, PdfWriter  # type: ignore


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
    elif "bradesco" in texto_lower or "data de débito" in texto_lower or "data de crédito" in texto_lower:
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
    
    Args:
        texto (str): Texto extraído do PDF
        
    Returns:
        tuple: (descricao, valor, data)
    """
    linhas = texto.splitlines()
    
    print("\n[DEPURAÇÃO BRADESCO] Linhas extraídas:")
    for i, linha in enumerate(linhas):
        print(f"Linha {i + 1}: '{linha.strip()}'")
    
    descricao = "sem_descricao"
    valor = "0.00"
    data = ""
    
    # Procurar pela descrição
    for i, linha in enumerate(linhas):
        linha_strip = linha.strip()
        # Procurar por "Descrição:" ou "Descricao:"
        if re.match(r"descri[cç][aã]o\s*:?", linha_strip, re.I):
            print(f"[DEPURAÇÃO BRADESCO] Encontrou 'Descrição' na linha {i + 1}")
            
            # A descrição pode estar na mesma linha ou na próxima
            descricao_match = re.search(r"descri[cç][aã]o\s*:?\s*(.+)", linha_strip, re.I)
            if descricao_match and descricao_match.group(1).strip():
                descricao = descricao_match.group(1).strip()
                print(f"[DEPURAÇÃO BRADESCO] Descrição encontrada na mesma linha: '{descricao}'")
            elif i + 1 < len(linhas):
                # Verificar próxima linha
                proxima_linha = linhas[i + 1].strip()
                if proxima_linha and not re.match(r"(valor|data|r\$)", proxima_linha, re.I):
                    descricao = proxima_linha
                    print(f"[DEPURAÇÃO BRADESCO] Descrição encontrada na linha seguinte: '{descricao}'")
            break
    
    # Procurar pelo "Valor Total" (campo específico do Bradesco)
    for linha in linhas:
        # Padrões para encontrar "Valor Total"
        valor_match = re.search(r"valor\s+total\s*:?\s*r?\$?\s*([\d.,]+)", linha, re.I)
        if valor_match:
            valor_raw = valor_match.group(1)
            # Converter para formato float
            if ',' in valor_raw:
                valor = valor_raw.replace('.', '').replace(',', '.')
            else:
                valor = valor_raw
            print(f"[DEPURAÇÃO BRADESCO] Valor Total encontrado: '{valor_raw}' -> '{valor}'")
            break
    
    # Procurar pela "Data de débito" ou "Data de crédito"
    for linha in linhas:
        data_match = re.search(r"data\s+de\s+(d[ée]bito|cr[ée]dito)\s*:?\s*(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})", linha, re.I)
        if data_match:
            _, dia, mes, ano = data_match.groups()
            meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                    'jul', 'ago', 'set', 'out', 'nov', 'dez']
            try:
                mes_num = int(mes)
                if 1 <= mes_num <= 12:
                    data = f"{dia.zfill(2)}_{meses[mes_num-1]}"
                    print(f"[DEPURAÇÃO BRADESCO] Data encontrada: '{data_match.group()}' -> '{data}'")
                    break
            except:
                continue
    
    # Limpar e formatar a descrição
    descricao = re.sub(r'[^a-zA-Z0-9\s_]', '', descricao)
    descricao = "_".join(descricao.split())
    
    print(f"[DEPURAÇÃO BRADESCO] Resultado final - Descrição: '{descricao}', Valor: '{valor}', Data: '{data}'")
    
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


def renomear_arquivos_na_pasta(pasta="."):
    """
    Renomeia todos os arquivos PDF na pasta especificada.
    
    Args:
        pasta (str): Caminho da pasta a processar (padrão: pasta atual)
    """
    pasta_path = Path(pasta)
    arquivos_pdf = list(pasta_path.glob("*.pdf"))
    
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
            
            # Evitar sobrescrever arquivos
            contador = 1
            while novo_caminho.exists():
                nome_base = nome_sugerido.replace('.pdf', '')
                novo_caminho = arquivo.parent / f"{nome_base}_{contador}.pdf"
                contador += 1
            
            try:
                arquivo.rename(novo_caminho)
                print(f"✅ Renomeado com sucesso!")
                print(f"   De: {nome_original}")
                print(f"   Para: {novo_caminho.name}\n")
                processados += 1
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
    print("\n" + "="*60)
    print("RENOMEADOR INTELIGENTE DE COMPROVANTES - v6")
    print("="*60)
    
    # Processar arquivos na pasta atual
    renomear_arquivos_na_pasta()


if __name__ == "__main__":
    main()
