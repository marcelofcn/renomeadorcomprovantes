from backend.services.extrator import ProcessadorFactory
from backend.processors.sicredi import SicrediProcessor


def test_factory_returns_sicredi_processor():
    processor = ProcessadorFactory.criar("sicredi")
    assert isinstance(processor, SicrediProcessor)


def test_sicredi_processor_extracts_boleto_fields():
    texto = """
    Comprovante de Pagamento
    Data do Pagamento: 05/06/2026
    Valor Pago (R$): 9.743,70
    Descrição do Pagamento:
    NF 7313356 AP 541858
    """

    processor = SicrediProcessor()
    dados = processor.extrair_dados(texto)

    assert dados["banco"] == "SICREDI"
    assert dados["tipo"] == "BOLETO"
    assert dados["descricao"] == "NF_7313356_AP_541858"
    assert dados["valor"] == 9743.70
    assert dados["data"] == "05_jun"


def test_sicredi_processor_extracts_tributo_fields():
    texto = """
    Associado: COMUNIDADE CANCAO NOVA ASSOCIACAO INTERNACIONAL PRIVADA DE FIEIS
    Cooperativa: 0710
    Conta Corrente: 28203-5
    Impresso em 26/06/2026 15:43:56
    Tributos
    Solicitante:
    Maria
    Número de Controle:3186591564
    Tipo de Pagamento:Órgãos Governamentais
    Nome da Empresa:SEFAZ BAHIA ICMS - COD. BARRA
    Código de Barras:858600000071577600052028606091939850222707591930
    Data do Pagamento:09/06/2026
    Hora do Pagamento:13:18
    Valor Total (R$):757,76
    Descrição do Pagamento:
    Autenticação Eletrônica:
    ICMS DD ap 542519
    68CF.BC60.559E.DA12.527E.1FEA.FFB5.6724
    """

    processor = SicrediProcessor()
    dados = processor.extrair_dados(texto)

    assert dados["banco"] == "SICREDI"
    assert dados["tipo"] == "TRIBUTO"
    assert dados["valor"] == 757.76
    assert dados["data"] == "09_jun"
    assert "ICMS" in dados["descricao"]
