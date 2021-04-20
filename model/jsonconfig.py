import json

from . import  observable

class JsonBasedConfig(observable.Observable):
    _topics = ['change']
    def __init__(self, config_file) -> None:
        with open(config_file) as f:
            self.config = json.load(f)
        #self.app = app
        self.config_file = config_file
        
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get_config(self, path):
        current = self.try_path(self.config, path)
        if current is None:
            return self.get_default_config(path)
        else:
            return current
            
    def get_default_config(self, path):
        return self.try_path(self.config['default'], path)
        
    def set_config(self, path, value):
        d = self.config
        for k in path[:-1]:
            d = d.setdefault(k, {})
        d[path[-1]] = value
        self.save()
        self.notify('change', path, value)
    
    @staticmethod
    def try_path(d, path):
        for k in path:
            if k in d:
                d = d[k]
            else:
                return None
        return d