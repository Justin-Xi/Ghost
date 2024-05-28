import unittest

from utils.singleton import singleton


class TestSingleton(unittest.TestCase):

    def test_singleton_instance(self):
        @singleton
        class MyClass:
            pass

        obj1 = MyClass()
        obj2 = MyClass()

        self.assertIs(obj1, obj2)


if __name__ == '__main__':
    unittest.main()
