import unittest
from pathlib import Path

from aftafa.common.pipeline import Pipeline
from aftafa.common.resource import FileResource, ExcelResource, JSONResource, EmailResource
from aftafa.common.loader import JSONLoader, JSONlLoader, FileLoader


class TestPipeline(unittest.TestCase):

    def test_file_to_json_pipeline(self):
        pass

    def test_json_to_json_pipeline(self):
        pass

    def test_json_to_jsonl_pipeline_with_jsonpath(self):
        pass

    def test_txt_to_jsonl_pipeline(self):
        pass

    def test_email_to_file_pipeline(self):
        pass

    def test_excel_to_jsonl_pipeline(self):
        pass


if __name__ == '__main__':
    unittest.main()
