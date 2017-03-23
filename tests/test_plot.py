import unittest
import json
import os
import numpy as np

from plot import Plot

class TestPlot(unittest.TestCase):

    def setUp(self):
        with open("tests/plot_config.json","r") as file:
            config = json.load(file)
        self.plot = Plot.parse_plot(config)
        with open("tests/plot_format_config.json","r") as file:
            config = json.load(file)
        self.plot_format = Plot.parse_plot(config)
    
    def tearDown(self):
        if os.path.isfile("tests/x['x²', 'x³'].pdf"):
            os.remove("tests/x['x²', 'x³'].pdf")
        if os.path.isfile("tests/x['x³'].pdf"):
            os.remove("tests/x['x³'].pdf")

    def test_parse_plot(self):
        self.assertTrue(self.plot.x == "x" and len(self.plot.y_list) == 2 and not self.plot.format,
            msg="Error parsing plot axis information")
        self.assertTrue(self.plot_format.format is not None, msg = "Error parsing format values")

    def test_create_plot(self):
        plot_data = {"x":[1,2],"x²":[1,4],"x³":[1,8]}
        plots = self.plot.create_plot("tests/", plot_data)
        squared = plots[0].get_xydata()
        self.assertTrue([1,1] == list(squared[0]) and [2,4] == list(squared[1]),
            msg = "wrong data was used for the first plot")
        cubed = plots[1].get_xydata()
        self.assertTrue([1,1] == list(cubed[0]) and [2,8] == list(cubed[1]),
            msg = "wrong data was used for the first plot")
        self.assertTrue(os.path.isfile("tests/x['x²', 'x³'].pdf"), msg="Plot was not saved to disk")

    def test_create_formatted_plot(self):
        plot_data = {"x":[1,2],"x³":[1,8]}
        plots = self.plot_format.create_plot("tests/", plot_data)
        self.assertEqual('o', plots[0].get_marker(), msg="Marker type differs from format")
        self.assertEqual('y', plots[0].get_markerfacecolor(), msg= "Marker color differs from format")


