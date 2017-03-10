import matplotlib.pyplot as plt

class Plot():
    @classmethod
    def parsePlot(cls,desc):
        x = desc["x"]
        y_list = desc["y"]
        fmt = desc["format"] if "format" in desc else None
        return cls(x, y_list,fmt)
    
    def __init__(self,x,y_list,fmt=None):
        self.x = x
        self.y_list = y_list
        self.format = fmt

    def create_plot(self, path, data):
        if self.format is None:
            for y in self.y_list:
                plt.plot(data[self.x], data[y])
        else:
            for i in range(0,len(self.y_list)):
                plt.plot(data[self.x], data[self.y_list[i]], self.format[i])
        plt.savefig(path + str(self.x) + str(self.y_list) + ".pdf")
        plt.clf()

class Plotter():
    def __init__(self, plots, path, name, names, param_names):
        self.plotlist = [Plot.parsePlot(desc) for desc in plots]
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
        