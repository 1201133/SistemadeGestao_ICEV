import os
import tempfile
import unittest
import importlib
from pathlib import Path


class AuthorizationScopeTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_scope.db"
        os.environ["DATABASE_NAME"] = str(self.db_path)

        # Reload modules after setting DATABASE_NAME so each test gets a fresh temporary DB.
        import config
        import permissions
        import database_membros
        import database_newsletter
        import database_calendario
        import database

        importlib.reload(config)
        importlib.reload(permissions)
        importlib.reload(database_membros)
        importlib.reload(database_newsletter)
        importlib.reload(database_calendario)
        importlib.reload(database)

        from database import init_db
        from database import adicionar_lancamento, obter_lancamentos, atualizar_lancamento, excluir_lancamento
        from database_newsletter import (
            criar_newsletter,
            listar_newsletters,
            atualizar_newsletter,
            excluir_newsletter,
        )
        from database_calendario import (
            criar_evento,
            listar_eventos,
            atualizar_evento,
            excluir_evento,
        )

        self.init_db = init_db
        self.adicionar_lancamento = adicionar_lancamento
        self.obter_lancamentos = obter_lancamentos
        self.atualizar_lancamento = atualizar_lancamento
        self.excluir_lancamento = excluir_lancamento
        self.criar_newsletter = criar_newsletter
        self.listar_newsletters = listar_newsletters
        self.atualizar_newsletter = atualizar_newsletter
        self.excluir_newsletter = excluir_newsletter
        self.criar_evento = criar_evento
        self.listar_eventos = listar_eventos
        self.atualizar_evento = atualizar_evento
        self.excluir_evento = excluir_evento

        self.init_db()

    def tearDown(self):
        os.environ.pop("DATABASE_NAME", None)
        self.temp_dir.cleanup()

    def test_lancamentos_respeitam_escopo_por_usuario(self):
        self.assertTrue(
            self.adicionar_lancamento("2026-05-24", "Alice", 100.0, "Pix", "Dizimo", "diacono01")
        )
        self.assertTrue(
            self.adicionar_lancamento("2026-05-24", "Bruno", 200.0, "Pix", "Oferta", "diacono02")
        )

        lancamentos_admin = self.obter_lancamentos()
        lancamentos_diacono01 = self.obter_lancamentos("diacono01", "diacono")
        lancamentos_diacono02 = self.obter_lancamentos("diacono02", "diacono")

        self.assertEqual(len(lancamentos_admin), 2)
        self.assertEqual(len(lancamentos_diacono01), 1)
        self.assertEqual(lancamentos_diacono01[0][2], "Alice")
        self.assertEqual(len(lancamentos_diacono02), 1)
        self.assertEqual(lancamentos_diacono02[0][2], "Bruno")

        id_alice = lancamentos_diacono01[0][0]
        id_bruno = lancamentos_diacono02[0][0]

        self.assertTrue(
            self.atualizar_lancamento(
                id_alice,
                "2026-05-24",
                "Alice Atualizada",
                150.0,
                "Pix",
                "Dizimo",
                usuario="diacono01",
            )
        )
        self.assertFalse(
            self.atualizar_lancamento(
                id_bruno,
                "2026-05-24",
                "Bruno Invadido",
                250.0,
                "Pix",
                "Oferta",
                usuario="diacono01",
            )
        )
        self.assertTrue(
            self.atualizar_lancamento(
                id_bruno,
                "2026-05-24",
                "Bruno Admin",
                250.0,
                "Pix",
                "Oferta",
            )
        )
        self.assertFalse(self.excluir_lancamento(id_bruno, usuario="diacono01"))
        self.assertTrue(self.excluir_lancamento(id_bruno))

    def test_newsletters_respeitam_escopo_por_usuario(self):
        id_diacono01 = self.criar_newsletter(
            "Aviso 1",
            "2026-05-24",
            "Resumo 1",
            "Conteudo 1",
            "Assunto 1",
            "diacono01",
            True,
        )
        id_diacono02 = self.criar_newsletter(
            "Aviso 2",
            "2026-05-25",
            "Resumo 2",
            "Conteudo 2",
            "Assunto 2",
            "diacono02",
            True,
        )

        self.assertIsNotNone(id_diacono01)
        self.assertIsNotNone(id_diacono02)
        self.assertEqual(len(self.listar_newsletters(criado_por="diacono01")), 1)
        self.assertEqual(len(self.listar_newsletters(criado_por="diacono02")), 1)
        self.assertEqual(len(self.listar_newsletters()), 2)

        self.assertFalse(
            self.atualizar_newsletter(
                id_diacono02,
                "Aviso 2",
                "2026-05-25",
                "Resumo 2",
                "Alteracao indevida",
                "Assunto 2",
                True,
                criado_por="diacono01",
            )
        )
        self.assertTrue(
            self.atualizar_newsletter(
                id_diacono02,
                "Aviso 2 Admin",
                "2026-05-25",
                "Resumo 2",
                "Alteracao admin",
                "Assunto 2",
                True,
            )
        )
        self.assertFalse(self.excluir_newsletter(id_diacono02, criado_por="diacono01"))
        self.assertTrue(self.excluir_newsletter(id_diacono02))

    def test_eventos_respeitam_escopo_por_usuario(self):
        id_diacono01 = self.criar_evento(
            "Evento 1",
            "Descricao 1",
            "Templo",
            "2026-05-24T10:00:00",
            "2026-05-24T11:00:00",
            False,
            "#111111",
            "diacono01",
        )
        id_diacono02 = self.criar_evento(
            "Evento 2",
            "Descricao 2",
            "Templo",
            "2026-05-25T10:00:00",
            "2026-05-25T11:00:00",
            False,
            "#222222",
            "diacono02",
        )

        self.assertIsNotNone(id_diacono01)
        self.assertIsNotNone(id_diacono02)
        self.assertEqual(len(self.listar_eventos(criado_por="diacono01")), 1)
        self.assertEqual(len(self.listar_eventos(criado_por="diacono02")), 1)
        self.assertEqual(len(self.listar_eventos()), 2)

        self.assertFalse(
            self.atualizar_evento(
                id_diacono02,
                "Evento 2",
                "Descricao 2",
                "Templo",
                "2026-05-25T10:00:00",
                "2026-05-25T11:00:00",
                False,
                "#333333",
                criado_por="diacono01",
            )
        )
        self.assertTrue(
            self.atualizar_evento(
                id_diacono02,
                "Evento 2 Admin",
                "Descricao 2",
                "Templo",
                "2026-05-25T10:00:00",
                "2026-05-25T11:00:00",
                False,
                "#333333",
            )
        )
        self.assertFalse(self.excluir_evento(id_diacono02, criado_por="diacono01"))
        self.assertTrue(self.excluir_evento(id_diacono02))


if __name__ == "__main__":
    unittest.main()
