import unittest
from modules.payload_generator import PayloadGenerator

class TestPayloadGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = PayloadGenerator()

    def test_generate_reverse_shell_valid(self):
        payload = self.generator.generate_reverse_shell("192.168.1.100", 4444, "php")
        self.assertIn("192.168.1.100", payload)
        self.assertIn("4444", payload)
        self.assertIn("passthru", payload)
        self.assertNotIn("exec", payload)

    def test_generate_reverse_shell_invalid_host(self):
        with self.assertRaises(ValueError):
            self.generator.generate_reverse_shell("127.0.0.1; rm -rf /", 4444, "bash")

    def test_generate_reverse_shell_invalid_port(self):
        with self.assertRaises(ValueError):
            self.generator.generate_reverse_shell("127.0.0.1", -1, "bash")

        with self.assertRaises(ValueError):
            self.generator.generate_reverse_shell("127.0.0.1", "notaport", "bash")

    def test_generate_bind_shell_valid(self):
        payload = self.generator.generate_bind_shell(8080, "bash")
        self.assertIn("8080", payload)

    def test_generate_bind_shell_invalid_port(self):
        with self.assertRaises(ValueError):
            self.generator.generate_bind_shell(99999, "bash")

if __name__ == '__main__':
    unittest.main()
