import re
import unicodedata
from typing import Any, Dict

from backend.processors.base import ProcessadorBase


class SicrediProcessor(ProcessadorBase):
    BANCO_NOME = "SICREDI"
    TIPOS_SUPORTADOS = ("BOLETO", "PIX", "TRIBUTO")

    def extrair_dados(self, texto: str) -> Dict[str, Any]:
        texto_lower = texto.lower()
        
        if "tributo" in texto_lower:
            tipo = "TRIBUTO"
        elif "pix" in texto_lower:
            tipo = "PIX"
        else:
            tipo = "BOLETO"

        descricao, valor, data = self._extrair_dados_boleto(texto)
        return {
            "banco": self.BANCO_NOME,
            "tipo": tipo,
            "descricao": descricao,
            "valor": valor,
            "data": data,
        }

    def validar(self, dados: Dict[str, Any]) -> bool:
        return bool(dados.get("descricao") and dados.get("valor") and dados.get("data"))

    def _extrair_dados_boleto(self, texto: str) -> tuple[str, float, str]:
        linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
        descricao = "SEM_DESCRICAO"
        valor = 0.0
        data = "00_jan"

        texto_lower = texto.lower()
        eh_tributo = "tributo" in texto_lower

        beneficiario = self._encontrar_beneficiario(linhas)
        descricao_linha = self._encontrar_descricao(linhas)

        if eh_tributo:
            if descricao_linha and descricao_linha != "SEM_DESCRICAO":
                descricao = descricao_linha
            elif beneficiario:
                descricao = beneficiario
        else:
            if descricao_linha and descricao_linha != "SEM_DESCRICAO" and self._parece_descricao_complementar(descricao_linha):
                descricao = descricao_linha
            elif beneficiario:
                descricao = beneficiario

        for linha in linhas:
            valor_match = re.search(r"valor[^\n\r]*?([\d.,]+)", linha, re.I)
            if valor_match:
                valor_str = valor_match.group(1).replace(".", "").replace(",", ".")
                valor = float(valor_str)
                break

        for padrao in [
            r"data\s+do\s+pagamento",
            r"data\s+da\s+operação",
            r"data\s+da\s+operacao",
        ]:
            for linha in linhas:
                data_match = re.search(rf"{padrao}\s*:?\s*(\d{{2}})/(\d{{2}})/(\d{{4}})", linha, re.I)
                if data_match:
                    data = self._converter_data(f"{data_match.group(1)}/{data_match.group(2)}/{data_match.group(3)}")
                    break
            if data != "00_jan":
                break

        if data == "00_jan":
            for linha in linhas:
                if re.search(r"impresso", linha, re.I):
                    continue
                data_match = re.search(r"(\d{2})/(\d{2})/(\d{4})", linha)
                if data_match:
                    data = self._converter_data(data_match.group(0))
                    break

        return descricao, valor, data

    def _encontrar_beneficiario(self, linhas: list[str]) -> str:
        for idx, linha in enumerate(linhas):
            if re.search(r"raz[aã]o\s+social\s+do\s+benefici[aá]rio", linha, re.I):
                restante = self._extrair_conteudo_apartir_de_linha(linha)
                if restante:
                    return restante
                if idx + 1 < len(linhas):
                    proxima = linhas[idx + 1]
                    if not self._eh_metadado(proxima):
                        return self._normalizar(proxima)

        for linha in linhas:
            if re.search(r"raz[aã]o\s+social", linha, re.I):
                restante = self._extrair_conteudo_apartir_de_linha(linha)
                if restante:
                    return restante

        for linha in linhas:
            if re.search(r"associado|nome\s+do\s+pagador", linha, re.I):
                restante = self._extrair_conteudo_apartir_de_linha(linha)
                if restante:
                    return restante

        return ""

    def _encontrar_descricao(self, linhas: list[str]) -> str:
        for idx, linha in enumerate(linhas):
            linha_lower = linha.lower()
            if re.search(r"descri[cç][aã]o(?:\s+do\s+pagamento)?", linha_lower, re.I):
                if ":" in linha:
                    restante = linha.split(":", 1)[1].strip()
                    if restante:
                        return self._normalizar(restante)
                if idx + 1 < len(linhas):
                    proxima = linhas[idx + 1]
                    if not self._eh_metadado(proxima):
                        return self._normalizar(proxima)
                if idx + 2 < len(linhas):
                    proxima = linhas[idx + 2]
                    if not self._eh_metadado(proxima) and proxima.upper().startswith(("ICMS", "ISS", "DARF", "NF", "AP")):
                        return self._normalizar(proxima)
                if idx + 3 < len(linhas):
                    proxima = linhas[idx + 3]
                    if not self._eh_metadado(proxima) and proxima.upper().startswith(("ICMS", "ISS", "DARF", "NF", "AP")):
                        return self._normalizar(proxima)

        for linha in linhas:
            if self._eh_metadado(linha):
                continue
            descricao = self._normalizar(linha)
            if descricao and descricao != "SEM_DESCRICAO":
                if descricao.upper().startswith("NF") or any(char.isdigit() for char in descricao):
                    return descricao
                if self._parece_beneficiario(linha):
                    return descricao

        return "SEM_DESCRICAO"

    def _extrair_conteudo_apartir_de_linha(self, linha: str) -> str:
        match = re.search(r"(?:raz[aã]o\s+social(?:\s+do\s+benefici[aá]rio)?|associado|nome\s+do\s+pagador|benefici[aá]rio)\s*[:\-]?\s*(.+)", linha, re.I)
        if match:
            return self._normalizar(match.group(1).strip())
        return ""

    def _eh_metadado(self, linha: str) -> bool:
        if not linha:
            return True
        return bool(re.search(r"^(comprovante|data|valor|descri[cç][aã]o|c[óo]digo|conta|cooperativa|impresso|boleto|associado|nome\s+do\s+pagador|benefici[aá]rio|raz[aã]o\s+social|tributo|autentica[cç][aã]o|eletr[oô]nica|n[uú]mero\s+de\s+controle|tipo\s+de\s+pagamento|hora\s+do|solicitante|nome\s+da\s+empresa)", linha, re.I))

    def _parece_descricao_complementar(self, descricao: str) -> bool:
        return any(char.isdigit() for char in descricao) or descricao.upper().startswith("NF")

    def _parece_beneficiario(self, linha: str) -> bool:
        return bool(re.search(r"comercio|ltda|sa|s\.a|associacao|cooperativa|facil|sdb|empresa", linha, re.I))

    def _normalizar(self, texto: str) -> str:
        if not texto:
            return "SEM_DESCRICAO"
        nfd = unicodedata.normalize("NFD", texto)
        sem_acentos = "".join(char for char in nfd if unicodedata.category(char) != "Mn")
        limpo = re.sub(r"[^a-zA-Z0-9\s]", "", sem_acentos)
        return limpo.strip().replace(" ", "_").upper()

    def _converter_data(self, data_str: str) -> str:
        meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
        try:
            dia, mes, _ano = data_str.split("/")
            return f"{dia}_{meses[int(mes) - 1]}"
        except Exception:
            return "00_jan"
