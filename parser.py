import re
import time

class Parser():

    def __init__(self,outputs):
        self.results={}
        self.expr = []
        self.count = 0
        for output in outputs:
            self.results[output["name"]]=None
            self.expr.append((output["name"], output["pattern"], output["group"]))

    def parse(self, output):
        for (name, pattern, group) in self.expr:
            m = re.search(pattern, output)
            if m is not None:
                self.results[name] = m.group(group)
        result = dict(self.results)
        for key in self.results:
            self.results[key]=None
        return result

    def names(self):
        return self.results.keys()
            
        

