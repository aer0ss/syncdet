import yaml

_config = None

def _populate_defaults(config_data):
    """
    Populates any missing fields in the 'actors' array if those
    fields have a default specified in 'actor_defaults'.
    """
    try:
        defaults = config_data['actor_defaults']
        if len(defaults) == 0:
            # No defaults, nothing to do here
            return
    except KeyError:
        # No defaults specified, so nothing to do here
        return

    if 'actors' not in config_data:
        raise Exception('no actors defined')

    for actor in config_data['actors']:
        for k, v in defaults.iteritems():
            if k not in actor:
                actor[k] = v

def load(config_path):
    """ Loads a configuration object from a YAML file. Can be called at most once. """
    global _config

    if _config:
        raise Exception("the config file can be loaded at most once")

    config_file = open(config_path, 'r')
    try:
        data = yaml.load(config_file)

        # Fill in the parameters for each client that were
        # left blank and have defaults specified
        _populate_defaults(data)

        # Create the new configuration object
        _config = _Config(data)
    finally:
        config_file.close()

def get():
    """ Returns the loaded configuration object, or raises an exception if one was not loaded. """
    if not _config:
        raise Exception("configuration file not loaded")
    return _config

class _Config(object):
    def __init__(self, data):
        """
        Creates a Config object that contains the controller's network address and the
        actor specifications.
        """
        self.controller_address = data["controller_address"]
        self.actors = data["actors"]
