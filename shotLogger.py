#!/usr/bin/env python3

import os
import logging
import logging.config

class Logger():
    def __init__(self):
        if 'SOLOLINK_SANDBOX' in os.environ:
            config_path = os.path.join(os.path.dirname(__file__), 'sim/shotmanager.sandbox.conf')
        else:
            config_path = "/etc/shotmanager.conf"

        try:
            if os.path.exists(config_path):
                logging.config.fileConfig(config_path)
            else:
                logging.basicConfig(level=logging.INFO)
        except Exception:
            logging.basicConfig(level=logging.INFO)
        self.xlog = logging.getLogger("shot")

    def log(self, data):
        self.xlog.info(str(data).replace("\0", ""))

logger = Logger()
