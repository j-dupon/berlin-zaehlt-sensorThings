import logging
import json
import os

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Logger():

  def __init__(self):
    self.formatter = logging.Formatter(
      CONFIG["logging"]["format"],
      style = CONFIG["logging"]["style"],
      datefmt = CONFIG["logging"]["datefmt"]
      )
    
    if not os.path.exists(CONFIG["logging"]["path"]):
      os.makedirs(CONFIG["logging"]["path"])

    error_logger = logging.getLogger("error")
    self.err = self.setup_logger(error_logger, f'{CONFIG["logging"]["path"]}err.log', logging.WARNING)

    default_logger = logging.getLogger(__name__)
    self.log = self.setup_logger(default_logger, f'{CONFIG["logging"]["path"]}info.log', logging.DEBUG)

  def setup_logger(self, logger, log_file, level):
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(self.formatter)
    handler_all = logging.FileHandler(f'{CONFIG["logging"]["path"]}all.log')
    handler_all.setFormatter(self.formatter)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(handler_all)

    return logger

log = Logger()