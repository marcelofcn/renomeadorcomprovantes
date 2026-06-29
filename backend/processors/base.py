from abc import ABC, abstractmethod
from typing import Any, Dict


class ProcessadorBase(ABC):
    """Base para processadores de comprovantes por banco."""

    BANCO_NOME: str = ""
    TIPOS_SUPORTADOS: tuple[str, ...] = ()

    @abstractmethod
    def extrair_dados(self, texto: str) -> Dict[str, Any]:
        """Extrai os dados principais do texto do comprovante."""

    @abstractmethod
    def validar(self, dados: Dict[str, Any]) -> bool:
        """Valida se a estrutura extraída faz sentido."""
