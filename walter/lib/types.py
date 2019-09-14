import json


class Database:
    def __init__(self, config_obj):
        self.driver = config_obj['driver']
        self.username = config_obj['username']
        self.password = config_obj['password']
        self.name = config_obj['name']
        self.port = config_obj['port']
        self.host = config_obj['host']


class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        with open(config_file) as json_file:
            config = json.load(json_file)
            json_file.close()

        self.database = Database(config["database"])
        self.project_dir = config['project_dir']
        self.complete_dir = config['complete_dir']
        self.incomplete_dir = config['incomplete_dir']
        self.init = config['init']

    def write(self):
        with open(self.config_file, "w") as json_file:
            json_file.write(json.dumps(
                self, indent=4, sort_keys=True, default=lambda obj: obj.__dict__))
            json_file.close()


class Project:
    def __init__(self, obj):
        self.id = obj['id']
        self.name = obj['name']
        self.language = obj['language']
        self.complete = False
        if obj['complete']:
            self.complete = True

    def __iter__(self):
        data = [self.id, self.name, self.language, self.complete]
        for i in data:
            yield i
