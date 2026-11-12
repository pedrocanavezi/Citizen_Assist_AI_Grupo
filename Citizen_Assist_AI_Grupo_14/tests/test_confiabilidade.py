"""Falhas de arquivo, extensão da base e precisão das alternativas."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from consulta import CAMINHO_BASE, buscar, carregar_base


class Arquivos(unittest.TestCase):
    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.arquivo = Path(pasta.name) / "base.json"
        self.registros = json.loads(CAMINHO_BASE.read_text(encoding="utf-8"))

    def gravar(self, registros):
        self.arquivo.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")

    def test_arquivo_ausente(self):
        with self.assertRaisesRegex(ValueError, "ausente"):
            carregar_base(self.arquivo)

    def test_conteudo_ilegivel(self):
        for dados in [b"", b"  ", b"[]", b"{}", b"{", b"\xff"]:
            with self.subTest(dados=dados), self.assertRaises(ValueError):
                self.arquivo.write_bytes(dados)
                carregar_base(self.arquivo)

    def test_registros_inconsistentes(self):
        for campo, valor in [("fonte", ""), ("palavras_chave", "CPF"), ("relacionados", ["ZZ99"]),
                             ("url", "sem-link"), ("verificacao", "2026-02-30"),
                             ("id", "GOV01"), ("relacionados", ["CPF01"])]:
            with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                registros = copy.deepcopy(self.registros)
                registros[0][campo] = valor
                self.gravar(registros)
                carregar_base(self.arquivo)

    def test_novo_tema_somente_no_json(self):
        novo = dict(self.registros[0], id="NOV01", tema="Exemplo de teste",
                    subtema="Consulta simulada", pergunta="Onde encontrar um mapa fictício?",
                    palavras_chave=["mapa fictício"], relacionados=[])
        self.gravar([*self.registros, novo])
        base = carregar_base(self.arquivo)
        self.assertEqual(base["arvore"]["Exemplo de teste"]["Consulta simulada"], ["NOV01"])
        self.assertEqual(buscar(base, "Mapa fictício?"), ("resposta", ["NOV01"]))

    def test_pergunta_ambigua_sem_preferir_ordem(self):
        self.gravar(list(reversed(self.registros)))
        estado, ids = buscar(carregar_base(self.arquivo), "certidão eleitoral")
        self.assertEqual(estado, "ambigua")
        self.assertEqual(set(ids), {"ELE03", "ELE04"})


if __name__ == "__main__":
    unittest.main()
