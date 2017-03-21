import re
import time
import collections

Output = collections.namedtuple('Output', ['name', 'regex', 'group'])

class Parser():
    @classmethod
    def parse_outputs(cls,config):
        desc = config["outputs"] if "outputs" in config else []
        outputs = [Output(o["name"],o["pattern"],o["group"]) for o in desc]
        return cls(outputs)

    def __init__(self,outputs):
        self.outputs = outputs

    def parse(self, output):
        result = {}
        for (name, pattern, group) in self.outputs:
            result[name] = None
            m = re.search(pattern, output)
            if m is not None:
                result[name] = m.group(group)
        return result

    def names(self):
        return [o.name for o in self.outputs]
            
        

