import unittest

from aftafa.client.odata.client import ODataClient, ODataClientAuth
from aftafa.common.loader import JSONLoader, JSONlLoader



class TestODataClient(unittest.TestCase):

    def test_odata_client(self):
        with ODataClient(user='dummy') as client:
            with client.request(
                        'GET',
                        'http://localhost/test1/odata/standard.odata/$metadata'
                    ) as response:
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(response.headers['Content-Type'].split(';')[0], 'application/xml')

        # JSONLoader(data=data, output_path=r'E:\__temp').load()
        # JSONlLoader(data=data.get('result'), output_path=r'E:\__temp').load()



if __name__ == '__main__':
    unittest.main()
