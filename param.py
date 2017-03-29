import itertools

class Parameters():
    "This class reads parameters and offers their names and their cross product off parametrizations"""
    @classmethod
    def parse_params(cls, config):
        par = config["params"] if "params" in config else []
        param_names = [p["name"] for p in par]
        params = [x["value"] for x in par]
        param_list = [perm for perm in itertools.product(*params)]
        return cls(param_names, param_list)

    def __init__(self, names=[], parametrizations=[]):
        self.names = names
        self.parametrizations = parametrizations
