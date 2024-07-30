import unittest

from aftafa.utils.helpers import timeit


class TestUtilsHelpers(unittest.TestCase):

    def test_timeit_wrapper(self):
        @timeit
        def calculate_something(num):
            total = sum((x for x in range(0, num**2)))
            return total
        
        calculate_something(10)
        calculate_something(10000)
        
        


if __name__ == '__main__':
    unittest.main()
