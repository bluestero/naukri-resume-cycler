import os
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta


class LogManager():

    #-Init function for the base initialization-#
    def __init__(
            self,
            log_filename: str,
            debug: bool = False,
            log_filepath: str = None,
            main_dir: str = os.getcwd(),
            log_formatter: str = "%(asctime)s - %(levelname)s : %(message)s"):
        """
        Creates and returns a logger object.\n
        The path where it is created is based on the main_dir.\n
        The logger name and log file is based on the file_name parameter passed.

        Parameters
        ----------
        `log_filename: str`
            The name of the logger object.
        `debug: bool`
            Sets the level of log from INFO to DEBUG. Default value is False.
        `log_filepath: str`
            The path of the logger file. Default is <main_dir> / <log_filename>.log.
        `main_dir : str`
            The directory path where the log file will be saved. Default is the current working directory.
        `log_formatter: str`
            Can set custom log formatter. Default value is %(asctime)s - %(levelname)s : %(message)s.

        Returns
        -------
        `logger : logging.Logger`
            The logger object based on the given parameters.
        """

        #-Creating the logger object using given information-#
        self.logger = logging.getLogger(log_filename)

        #-Closing any already opened handlers-#
        for handler in self.logger.handlers:
            handler.close()

        #-Setting the log_filepath if not given-#
        if not log_filepath:
            log_filepath = main_dir / f"{log_filename}.log"

        #-Adding the file_handler with the relative path main_dir/main.log-#
        file_handler = logging.FileHandler(log_filepath, mode = "w")

        #-Setting level to DEBUG if debug flag is on else INFO-#
        self.logger.setLevel(logging.DEBUG) if debug else self.logger.setLevel(logging.INFO)

        #-Setting formatter-#
        formatter = logging.Formatter(log_formatter, "%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


    #-Static function to find recent date-#
    @staticmethod
    def __is_recent(date: str, days: int):

        #-Convert input date string to datetime object-#
        input_date = datetime.strptime(date, '%Y-%m-%d').date()

        #-Get today's date-#
        today = datetime.now().date()

        # Calculate the difference in days
        date_difference = today - input_date

        #-Return the bool value of difference of days-#
        return date_difference < timedelta(days = days)


    #-Function to archive the log in a separate archived logs file-#
    def archive_logs(self, archive_filepath: str = None, log_rotation: int = 0, reset_counter = False) -> None:
        """
        Archives the log files and maintains a run history.\n
        Appends the log data, timestamp, and run counter to the archive log file for indexing.\n
        Supportes flexible log rotation and counter resetting.

        Parameters
        ----------
        `archive_filepath : str`
            The path of the log archive. Default is <log_filename>_archive.log.
        `log_rotation: int`
            Removes outdated logs by given number of days. Default is 0.
        `reset_counter: bool`
            Resets the counter if set to True. Default value is False.
        """

        #-Creating archive filepath if not given-#
        if not archive_filepath:
            log_name = os.path.basename(log_filepath)[:-4]
            archive_filepath = os.path.join(os.path.dirname(log_filepath), f"{log_name}_archive.log")

        #-Creating archive.log if does not exist-#
        if not os.path.exists(archive_filepath):
            with open(archive_filepath, 'w') as archive_file:
                pass

        #-Opening the archive.log file in append+ mode-#
        with open(archive_filepath, 'r+') as archive_file:

            #-Base objects-#
            log_entries = []
            is_valid = lambda x: x.strip() != ''
            re_date = re.compile(r"\d\d\d\d-\d\d-\d\d")
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            double_line_separator = "=" * 120 + "\n" + "=" * 120

            #-If log_rotation is given, adding condition to filter out outdated entries-#
            if log_rotation:
                is_valid = lambda x: x.strip() != '' and is_recent(re_date.findall(x)[-1], log_rotation)

            #-Reading the data and spltting it by the separator-#
            lines = archive_file.read().strip().split(double_line_separator)

            #-If data is present, it will process and filter out the data based on given flags-#
            if lines:
                log_entries = [data.strip() for index, data in enumerate(lines) if is_valid(data)]

            #-Resetting the counter if reset_counter is true-#
            if reset_counter:
                log_entries = [re.sub(r'\| RUN NO : \d+', f"| RUN NO : {index + 1}", entry) for index, entry in enumerate(log_entries)]

            #-Determine the run counter based on the last line-#
            counter = int(log_entries[-1].split()[-1]) + 1 if any(lines) else 1

            #-Open and read the csv2sql.log file-#
            with open(log_filepath, 'r') as log:
                log_data = log.read()

            #-Storing the new log data, timestamp, and run counter to the archive.log file-#
            log_entries.append(f"{log_data}{time} | RUN NO : {counter}")
            archive_file.seek(0)
            archive_file.truncate()
            archive_file.write(f"\n{double_line_separator}\n\n".join(log_entries))


logs_manager = LogManager()