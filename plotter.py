import matplotlib.pyplot as plt
from plot import Plot

class Plotter():
    def __init__(self, config, path, name, names, param_names):
        plots = config["plots"] if "plots" in config else []
        self.plotlist = [Plot.parse_plot(desc) for desc in plots]
        self.path = path
        self.name = name
        self.results = {key:[] for key in names}
        for key in param_names:
            self.results[key] = []

    def save_complete(self, par_alloc, result):
        for key, value in result.items():
            self.results[key].append(value)
        for var in par_alloc.split(","):
            assign = var.split("=")
            self.results[assign[0]].append(float(assign[1]))

    def plot(self):
        for plot in self.plotlist:
            plot.create_plot(self.path, self.results)
        
