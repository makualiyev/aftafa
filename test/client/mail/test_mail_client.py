import unittest

from aftafa.client.mail.client import YandexMailClient


class TestYandexMailClient(unittest.TestCase):
    def test_base_functionality(self):
        client = YandexMailClient(user='dummy')
        pass


if __name__ == '__main__':
    unittest.main()
