import unittest

from utils.ada_enum import Result, State


class TestEnums(unittest.TestCase):
    def test_string_output(self):
        self.assertEqual(State.CREATED.name, "CREATED")
        self.assertEqual(Result.SUCCESSFUL.name, "SUCCESSFUL")

    def test_error_code_output(self):
        self.assertEqual(State.CREATED.value, 0)
        self.assertEqual(Result.SUCCESSFUL.value, 0)


if __name__ == '__main__':
    unittest.main()
