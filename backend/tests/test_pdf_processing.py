import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PyPDF2 import PdfWriter

from backend.services.pdf_processing import build_filename_from_text, process_pdf_file


class PdfProcessingTests(unittest.TestCase):
    def test_build_filename_from_text_uses_short_safe_name(self):
        texto = """
        Comprovante de Transação Bancária
        Boleto de Cobrança
        Data da operação: 23/06/2026
        Razão Social SDB COMERCIO DE ALIMENTOS LTDA
        Descrição: NF 1119853 AP 543595
        Valor total: R$ 730,75
        """

        nome = build_filename_from_text(texto, 730.75)

        self.assertTrue(nome.endswith('.pdf'))
        self.assertLessEqual(len(nome), 120)
        self.assertIn('23062026', nome)
        self.assertIn('SDB', nome.upper())
        self.assertIn('1119853', nome)
        self.assertIn('543595', nome)
        self.assertIn('730.75', nome)

    def test_build_filename_from_text_uses_pagamento_sicredi(self):
        texto = """
        Associado: COMUNIDADE CANCAO NOVA ASSOCIACAO INTERNACIONAL PRIVADA DE FIEIS
        Data do Pagamento: 05/06/2026
        Valor Pago (R$): 9.743,70
        Descrição do Pagamento: NF 7313356 AP 541858
        """

        nome = build_filename_from_text(texto, 9743.70)

        self.assertIn('05062026', nome)
        self.assertIn('NF', nome.upper())
        self.assertIn('7313356', nome)
        self.assertIn('541858', nome)
        self.assertIn('9743.70', nome)

    def test_build_filename_from_text_extracts_sicredi_boleto_description_from_next_line(self):
        texto = """
        Comprovante de Pagamento
        Data do Pagamento: 05/06/2026
        Valor Pago (R$): 9.743,70
        Descrição do Pagamento
        NF 7313356 AP 541858
        """

        nome = build_filename_from_text(texto, 9743.70)

        self.assertIn('05062026', nome)
        self.assertIn('NF', nome.upper())
        self.assertIn('7313356', nome)
        self.assertIn('541858', nome)
        self.assertIn('9743.70', nome)

    def test_build_filename_from_text_uses_simple_sicredi_boleto_fields(self):
        texto = """
        Comprovante de Pagamento
        Data do Pagamento: 05/06/2026
        Valor Pago (R$): 9.743,70
        Descrição do Pagamento
        NF 7313356 AP 541858
        """

        nome = build_filename_from_text(texto, 9743.70)

        self.assertIn('05062026', nome)
        self.assertIn('NF', nome.upper())
        self.assertIn('7313356', nome)
        self.assertIn('541858', nome)
        self.assertIn('9743.70', nome)

    def test_identify_and_extract_sicredi_boleto_with_separate_description_line(self):
        texto = """
        Associado: COMUNIDADE CANCAO NOVA ASSOCIACAO INTERNACIONAL PRIVADA DE FIEIS
        Cooperativa: 0710
        Conta Corrente: 28203-5
        Impresso em 25/06/2026 08:59:31
        Boletos
        Data do Pagamento: 05/06/2026
        Valor Pago (R$): 9.743,70
        Descrição do Pagamento:
        NF 7313356 AP 541858
        """

        from backend.services.pdf_processing import identificar_tipo_comprovante, extrair_dados_boleto

        self.assertEqual(identificar_tipo_comprovante(texto), 'BOLETO')
        descricao, valor, data = extrair_dados_boleto(texto)

        self.assertEqual(descricao, 'NF_7313356_AP_541858')
        self.assertEqual(valor, 9743.70)
        self.assertEqual(data, '05_jun')

    def test_build_filename_prefers_beneficiary_legal_name(self):
        texto = """
        Nome do Pagador: COMUNIDADE CANCAO NOVA ASSOCIACAO INTERNACIONAL PRIVADA DE FIEIS
        Razão Social do Beneficiário: COMPRE FACIL COMERCIO DE PRODUTOS ALIM L
        Data do Pagamento: 05/06/2026
        Valor Pago (R$): 9.743,70
        """

        nome = build_filename_from_text(texto, 9743.70)

        self.assertIn('COMPRE_FACIL', nome.upper())
        self.assertNotIn('COMUNIDADE', nome.upper())

    def test_process_pdf_file_splits_multpage_pdf_into_one_file_per_page(self):
        with TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / 'lote.pdf'
            output_dir = Path(tmpdir) / 'processed'
            output_dir.mkdir(parents=True, exist_ok=True)

            writer = PdfWriter()
            writer.add_blank_page(width=200, height=200)
            writer.add_blank_page(width=200, height=200)
            with open(source_path, 'wb') as f:
                writer.write(f)

            with patch('backend.services.pdf_processing.PROCESSED_DIR', output_dir):
                resultados = process_pdf_file(source_path, 'lote.pdf', None)

            self.assertEqual(len(resultados), 2)
            self.assertEqual(len(list(output_dir.glob('*.pdf'))), 2)


if __name__ == '__main__':
    unittest.main()
