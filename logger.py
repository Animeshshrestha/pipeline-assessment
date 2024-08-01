from __future__ import annotations

import logging
import os
from datetime import datetime

from config import settings


class Logger:
    """
    General Logger class to save the log to the desired folder
    with time as file name
    """

    def __init__(self):
        self.log_dir = settings.LOGGING_DIR
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.setup_log_directory()
        self.setup_handlers()

    def setup_log_directory(self):
        """
        Created the directory based on current date and
        file on date if directory and file does not exists.
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.log_path = os.path.join(self.log_dir, current_date)
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        self.log_file = os.path.join(self.log_path, f'{current_date}.log')

    def setup_handlers(self):
        """
        Sets up the file and console handlers for logging,
        ensuring no duplicate handlers are added.
        """
        if not self.logger.hasHandlers():
            # File handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


logger = Logger()
