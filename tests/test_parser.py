import unittest
import json

from parser import Parser

class TestParser(unittest.TestCase):

    def setUp(self):
        with open("tests/parser_config.json","r") as file:
            self.config = json.load(file)

    def test_parse_outputs(self):
        parser = Parser.parse_outputs(self.config)
        self.assertEqual(2, len(parser.outputs), msg = "not all outputs are extracted")

    def test_names(self):
        parser = Parser.parse_outputs(self.config)
        self.assertEqual(["value1", "number"], parser.names(), msg="error extracting output names")

    def test_parse(self):
        parser = Parser.parse_outputs(self.config)
        result = parser.parse("example pattern -11.245")
        self.assertEqual({"value1": "le", "number":"-11.245"}, result,
            msg="error extracting variables")
        result = parser.parse("-11.245")
        self.assertEqual({"value1": None, "number": "-11.245"}, result,
            msg="missing values are not filled with None")

    


