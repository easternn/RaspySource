import logging
import logging.config
import yaml

source_path = '<PATH>'
with open(source_path + '/logging-config.yml', 'r') as logconf:
    logging_config = yaml.load(logconf, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
logger = logging.getLogger('logger')