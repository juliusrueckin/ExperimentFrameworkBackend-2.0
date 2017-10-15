import re
import time
import collections

Output = collections.namedtuple('Output', ['name', 'regex', 'group'])

class Parser():
    """This class extracts experiment observations out of strings based on regular expressions.""" 
    @classmethod
    def parse_outputs(cls,config):
        """Create the parser object from its json specification"""
        desc = config["csv"]["outputs"] if config["csv"]["outputs"] is not None else []
        outputs = [Output(o["name"],o["pattern"],o["group"]) for o in desc]
        return cls(outputs)

    def __init__(self,outputs=[]):
        """Create an instance for a list of output variables, default is an empty list"""
        self.outputs = outputs

    def parse(self, output_text):
        """Extract variables from a given text and return the values in a dictionary, filling missing values with None"""
        result = {}
        for (name, pattern, group) in self.outputs:
            result[name] = None
            m = re.search(pattern, output_text)
            if m is not None:
                result[name] = m.group(group)
        return result

    def names(self):
        """Return a list of all names of output variables"""
        return [o.name for o in self.outputs]