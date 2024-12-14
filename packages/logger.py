from datetime import datetime

import logging
import os


# create Logs directory
if not os.path.exists("Logs"):
    os.mkdir("Logs")

# Configure logger
logging.basicConfig(filename=datetime.now().strftime('Logs/Log-%Y.%m.%d.log'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d\t%(name)s\t%(levelname)s\t%(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("VoiceChangeClient")
