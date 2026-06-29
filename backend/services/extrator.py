from typing import Any, Dict

from backend.processors import ProcessadorBase, SicrediProcessor


class ProcessadorFactory:
    @staticmethod
    def criar(banco: str) -> ProcessadorBase:
        banco_normalizado = banco.lower()
        if banco_normalizado == "sicredi":
            return SicrediProcessor()
        raise ValueError(f"Banco não suportado: {banco}")


def extrair_dados_comprovante(texto: str, banco: str = "sicredi") -> Dict[str, Any]:
    processador = ProcessadorFactory.criar(banco)
    dados = processador.extrair_dados(texto)
    return dados
