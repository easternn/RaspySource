import logging
import logging.config
import yaml

source_path = ''
with open(source_path + '/modules/loggin-config.yml', 'r') as logconf:
    logging_config = yaml.load(logconf, Loader=yaml.FullLoader)
logging_config.config.dictConfig(config)
logger = logging_config.getLogger('Logger')