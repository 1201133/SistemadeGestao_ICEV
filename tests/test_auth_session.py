import importlib
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch


class AuthSessionTest(unittest.TestCase):
    def setUp(self):
        import auth

        self.auth = importlib.reload(auth)

    def test_verificar_senha_hash_valida_e_invalida(self):
        senha = "SenhaForte@123"
        hash_gerado = self.auth.bcrypt.hashpw(senha.encode("utf-8"), self.auth.bcrypt.gensalt()).decode("utf-8")

        self.assertTrue(self.auth.verificar_senha_hash(senha, hash_gerado))
        self.assertFalse(self.auth.verificar_senha_hash("senha-errada", hash_gerado))
        self.assertFalse(self.auth.verificar_senha_hash(senha, "hash-invalido"))
        self.assertFalse(self.auth.verificar_senha_hash(senha, ""))

    def test_verificar_login_retorna_usuario_quando_credenciais_sao_validas(self):
        senha = "SenhaSegura@123"
        hash_gerado = self.auth.bcrypt.hashpw(senha.encode("utf-8"), self.auth.bcrypt.gensalt()).decode("utf-8")

        with patch.object(self.auth, "USUARIOS_HASHES", {"diacono01": hash_gerado}), patch.object(
            self.auth, "NIVEIS_ACESSO", {"diacono01": "diacono"}
        ), patch.object(self.auth, "NOMES_USUARIOS", {"diacono01": "Diacono Teste"}):
            usuario = self.auth.verificar_login("diacono01", senha)

        self.assertEqual(
            usuario,
            {
                "usuario": "diacono01",
                "nome": "Diacono Teste",
                "nivel": "diacono",
            },
        )

    def test_verificar_login_falha_para_usuario_inexistente_ou_hash_ausente(self):
        with patch.object(self.auth, "USUARIOS_HASHES", {}):
            self.assertIsNone(self.auth.verificar_login("inexistente", "123"))

        with patch.object(self.auth, "USUARIOS_HASHES", {"diacono01": None}):
            self.assertIsNone(self.auth.verificar_login("diacono01", "123"))

    def test_login_esta_bloqueado_e_minutos_restantes(self):
        agora = datetime(2026, 5, 24, 12, 0, 0)
        bloqueado_ate = agora + timedelta(minutes=10, seconds=1)

        self.assertTrue(self.auth.login_esta_bloqueado(bloqueado_ate, agora))
        self.assertEqual(self.auth.minutos_restantes_bloqueio(bloqueado_ate, agora), 11)
        self.assertFalse(self.auth.login_esta_bloqueado(agora, agora))
        self.assertEqual(self.auth.minutos_restantes_bloqueio(agora, agora), 0)
        self.assertFalse(self.auth.login_esta_bloqueado(None, agora))

    def test_registrar_falha_login_bloqueia_na_quinta_tentativa(self):
        agora = datetime(2026, 5, 24, 12, 0, 0)

        estado = self.auth.registrar_falha_login(3, agora)
        self.assertEqual(estado["tentativas"], 4)
        self.assertIsNone(estado["bloqueado_ate"])

        estado = self.auth.registrar_falha_login(4, agora)
        self.assertEqual(estado["tentativas"], 5)
        self.assertEqual(estado["bloqueado_ate"], agora + timedelta(minutes=15))

    def test_sessao_expirada_apos_trinta_minutos_de_inatividade(self):
        agora = datetime(2026, 5, 24, 12, 30, 1)
        ultima_atividade = "2026-05-24T12:00:00"

        self.assertTrue(self.auth.sessao_expirada(ultima_atividade, agora))
        self.assertFalse(self.auth.sessao_expirada("2026-05-24T12:05:00", agora))
        self.assertFalse(self.auth.sessao_expirada(None, agora))
        self.assertFalse(self.auth.sessao_expirada("data-invalida", agora))


if __name__ == "__main__":
    unittest.main()
