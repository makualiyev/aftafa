import unittest

from aftafa.client.ozon.client import (
    OzonSellerClient,
    OzonSellerClientAuth
)
from aftafa.common.loader import (
    JSONlLoader,
    JSONLoader,
    FileLoader
)



class TestLoader(unittest.TestCase):
    def test_file_loader(self) -> None:
        f_loader: FileLoader = FileLoader(output_path='test-samples')
        f_loader.load(data=b'aftafa ver 0.0.1a')
        
    def test_json_loader(self) -> None:
        json_loader: JSONLoader = JSONLoader(output_path='test-samples')
        json_loader.load(data={"proj": "aftafa ver 0.0.1a", "os": "windows"})

    def test_jsonl_loader(self) -> None:
        jsonl_loader: JSONlLoader = JSONlLoader(output_path='test-samples', jsonpath='')
        jsonl_loader.load(data=[{"project" :"opensource"}, {"project" :"proprietary"}])
        
        
if __name__ == '__main__':
    unittest.main()
