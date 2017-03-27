import unittest
import json
import os
import numpy as np

from plotter import Plotter

class TestPlotter(unittest.TestCase):

    def setUp(self):
        with open("tests/plotter_config.json","r") as file:
            config = json.load(file)
        self.plotter = Plotter(config, ["x²","abs"],["a"],"tests/")

    def tearDown(self):
        if os.path.isfile("tests/a['x²'].pdf"):
            os.remove("tests/a['x²'].pdf")
        if os.path.isfile("tests/a['x²', 'abs'].pdf"):
            os.remove("tests/a['x²', 'abs'].pdf")

    def test__init__(self):
        self.assertEqual(2, len(self.plotter.plotlist), msg="Error parsing the list of two plots")
        self.assertEqual({"a":[], "x²":[], "abs":[]}, self.plotter.results,
            msg="Error creating the dictionary to store plot data")

    def test_save_complete(self):
        self.plotter.save_complete("a=-2", {"x²":4, "abs":2})
        self.assertEqual({"a":[-2], "x²":[4], "abs":[2]},self.plotter.results,
            msg="Wrong update of result dictionary after a completed run")

    def test_save_fail(self):
        self.plotter.save_fail("a=1", "timeout")
        self.assertEqual({"a":[], "x²":[], "abs":[]}, self.plotter.results,
            msg="Plot data changed after a failed run")

    def test_finish_experiment(self):
        self.plotter.save_complete("a=-2", {"x²":4, "abs":2})
        self.plotter.save_complete("a=1", {"x²":1, "abs":1})
        self.plotter.finish_experiment()
        self.assertTrue(os.path.isfile("tests/a['x²'].pdf")
            and os.path.isfile("tests/a['x²', 'abs'].pdf"),
            msg="Plotter did not create both configured plots")

