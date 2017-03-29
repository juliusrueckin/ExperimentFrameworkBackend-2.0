import matplotlib.pyplot as plt
from plot import Plot

class Plotter():
    """This class collects results and parameters from experiments and generates plots over it."""
    def __init__(self, config, names, param_names, path):
        plots = config["plots"] if "plots" in config else []
        self.plotlist = [Plot.parse_plot(desc) for desc in plots]
        self.results = {key:[] for key in names}
        self.path = path
        for key in param_names:
            self.results[key] = []

    def start_experiment(self, command):
        pass

    def save_complete(self, par_alloc, result):
        """Add the results and parameter configuration to the plot data."""
        for key, value in result.items():
            self.results[key].append(value)
        for var in par_alloc.split(","):
            assign = var.split("=")
            self.results[assign[0]].append(float(assign[1]))

    def save_fail(self, par_alloc, error):
        """Do nothing."""
        pass

    def finish_experiment(self):
        """Create the plots defined in the configuration using the collected plot data."""
        for plot in self.plotlist:
            plot.create_plot(self.path, self.results)
        
