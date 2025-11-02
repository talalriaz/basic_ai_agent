import yaml

def load_config():
    try:
        with open("config/config.yaml", 'r') as file:
            configuration = yaml.safe_load(file)
            return configuration 
    except yaml.YAMLError as exc:
        print('Exception occured in reading yaml',exc)