import unittest
import json

from parser import Parser

class TestParser(unittest.TestCase):

    def setUp(self):
        with open("tests/parser_config.json","r") as file:
            config = json.load(file)
        self.parser = Parser.parse_outputs(config)

    def test_parse_outputs(self):      
        self.assertEqual(2, len(self.parser.outputs), msg = "not all outputs are extracted")

    def test_names(self):
        self.assertEqual(["value1", "number"], self.parser.names(),
            msg="error extracting output names")

    def test_parse(self):
        result = self.parser.parse("example pattern -11.245")
        self.assertEqual({"value1": "le", "number":"-11.245"}, result,
            msg="error extracting variables")
        result = self.parser.parse("-11.245")
        self.assertEqual({"value1": None, "number": "-11.245"}, result,
            msg="missing values are not filled with None")

    


