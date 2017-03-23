import matplotlib.pyplot as plt

class Plot():
    """Extract the definition for a plot with format options and draw it when given experiment data."""
    @classmethod
    def parse_plot(cls,config):
        """Extract the plot definition and return an instance of Plot."""
        x = config["x"]
        y_list = config["y"]
        fmt = config["format"] if "format" in config else None
        return cls(x, y_list,fmt)
    
    def __init__(self,x,y_list,fmt=None):
        self.x = x
        self.y_list = y_list
        self.format = fmt

    def create_plot(self, path, data):
        """Create plot given data and save resulting image to location given by path."""
        plots = None
        if self.format is None:
            plots = [plt.plot(data[self.x], data[y]) for y in self.y_list]
        else:
            plots = [plt.plot(data[self.x], data[self.y_list[i]], self.format[i]) 
                for i in range(0,len(self.format))]
        plt.savefig(path + str(self.x) + str(self.y_list) + ".pdf")
        plt.clf()
        return [plot for plt_list in plots for plot in plt_list]
