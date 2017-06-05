import yaml, os


class ConfigMixin(object):
    def _get_config(self, config_file_name='cryptotrader2_config.yml'):
        # get absolut path to config file
        conf_file_abs_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            config_file_name)

        # load configuration
        with open(conf_file_abs_path)as conf:
            return yaml.load(conf)
