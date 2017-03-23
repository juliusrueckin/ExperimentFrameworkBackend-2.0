import unittest
import json
import os

from writer import CSVWriter

class TestParser(unittest.TestCase):

    def setUp(self):
        self.writer = CSVWriter("tests/", "test", "A=hello", "echo 1", ["number", "value1"])

    def tearDown(self):
        os.remove("tests/results.csv")
        pass

    def test_create_csv(self):
        self.writer.file.close()
        self.assertTrue(os.path.isfile("tests/results.csv"))
        self.compare_files("tests/header_expected.csv", "wrong csv header created")

    def test_save_complete(self):
        self.writer.save_complete("a=1", {"number": 11.245, "value1": "example"})
        self.writer.file.close()
        self.compare_files("tests/save_completed.csv", "save complete failed")

    def test_save_fail(self):
        self.writer.save_fail("a=1","timeout")
        self.writer.file.close()
        self.compare_files("tests/save_failed.csv", "save fail failed")

    def test_add_run_data(self):
        self.writer.file.close()
        entry = {}
        expected = {"cmd":"echo 1", "env": "A=hello", "name": "test", "timestamp": self.writer.time}
        self.writer.add_run_data(entry)
        self.assertEqual(expected, entry, msg = "wrong metadata is added to entry")

    def compare_files(self,expected_file, msg):
        with open(expected_file,"r") as file:
            expected = file.read().replace("<t>", str(self.writer.time))
            with open("tests/results.csv","r") as file2:
                actual = file2.read()
                self.assertMultiLineEqual(expected, actual, msg=msg)

    

