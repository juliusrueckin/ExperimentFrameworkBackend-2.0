import unittest
import json

import httmock

from param import Parameters

class TestParameters(unittest.TestCase):

    def setUp(self):
        with open("tests/param_config.json","r") as file:
            config = json.load(file)
        self.params = Parameters.parse_params(config)

    def test_parse_parameters(self):
        expected_names = ["a", "b"]
        self.assertCountEqual(expected_names, self.params.names)
        expected_parametrizations = [(1,4),(1,5),(2,4),(2,5)]
        self.assertCountEqual(expected_parametrizations, self.params.parametrizations)
