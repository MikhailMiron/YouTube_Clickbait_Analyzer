import os
from tabulate import tabulate
import csv
import logging
import copy
import operator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)





class ClickbaitAnalyzer:
    TITLE = "title"
    CTR = "ctr"
    RETENTION = "retention_rate"
    VIEWS = "views"
    LIKES = "likes"
    WATCH_TIME = "avg_watch_time"

    COLUMN_NAME_TITLE = {
        TITLE: str,
        CTR: float,
        RETENTION: int,
        VIEWS: int,
        LIKES: int,
        WATCH_TIME: float
    }

    def __init__(self, files=None):
        self.data = []
        if files:
            for file_path in files:
                self.load(file_path)



    def copy(self):
        new_table = ClickbaitAnalyzer()
        new_table.data = copy.deepcopy(self.data)
        logger.info("Table copy created successfully")
        return new_table


    def append(self, row):
        try:
            if len(row) != len(self.COLUMN_NAME_TITLE):
                raise ValueError(f"Expected {len(self.COLUMN_NAME_TITLE)} columns per row: {row}")
            converted_row = []
            for value, target_type in zip(row, self.COLUMN_NAME_TITLE.values()):
                converted_value = target_type(value)
                converted_row.append(converted_value)
            self.data.append(converted_row)
            logger.info(f"New row added to table {converted_row}")
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
        except Exception as e:
            logger.error(f"Something went completely wrong: {e}")


    def load(self, filename):
        extension = os.path.splitext(filename)[1]
        if extension == ".csv":
            self._load_csv(filename)
        else:
            logger.error(f"Unexpected file extension '{filename}': {extension}")


    def _load_csv(self, filename):
        try:

            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    self.append(row)
                logger.info(f"File {filename} uploaded successfully")
        except FileNotFoundError:
            logger.error(f"File '{filename}' not found")
        except Exception as e:
            logger.error(f"Unexpected error while reading file '{filename}': {e}")


    def sort_data(self, column_name=None, reverse=False):
        if not self.data:
            logger.warning("Attempted to sort an empty table. Skipping.")
            return
        try:
            if  column_name and column_name not in self.COLUMN_NAME_TITLE.keys():
                raise ValueError(f"Column name '{column_name}' not found")
            column_index = 0
            if column_name:
                column_index = list(self.COLUMN_NAME_TITLE.keys()).index(column_name)
            self.data.sort(key=lambda x: x[column_index], reverse=reverse)
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")



    def filter_by(self, column_name, threshold, mode="gt"):
        ops = {
            "gt": operator.gt,  # >
            "lt": operator.lt,  # <
            "ge": operator.ge,  # >=
            "le": operator.le  # <=
        }
        try:
            if column_name not in self.COLUMN_NAME_TITLE:
                raise ValueError(f"Column '{column_name}' not found in configuration")
            if mode not in ops:
                raise ValueError(f"Invalid mode '{mode}'. Available: {list(ops.keys())}")
            column_index = list(self.COLUMN_NAME_TITLE.keys()).index(column_name)
            op_func = ops[mode]
            target_type = self.COLUMN_NAME_TITLE[column_name]
            typed_threshold = target_type(threshold)
            initial_count = len(self.data)
            self.data = [row for row in self.data if op_func(row[column_index], typed_threshold)]
            logger.info(
                f"Filter applied: {column_name} {mode} {typed_threshold}. "
                f"Rows kept: {len(self.data)} (Removed {initial_count - len(self.data)})"
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Filter error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during filtering: {e}")


    def show(self, show_cols=None):
        if not self.data:
            print("No data")
        elif show_cols is None:
            print(tabulate(self.data, headers=list(self.COLUMN_NAME_TITLE.keys()), tablefmt="fancy_grid"))
        else:
            all_columns = list(self.COLUMN_NAME_TITLE.keys())
            headers = [c for c in show_cols if c in self.COLUMN_NAME_TITLE]
            indices = [all_columns.index(c) for c in headers]
            filtered_data = [[row[i] for i in indices] for row in self.data]
            print(tabulate(filtered_data, headers=headers, tablefmt="fancy_grid"))


    def clear(self):
        self.data = []
        logger.info(f"Clearing table")



    def report(self, report):
        if report == "clickbait":
            self.clickbait()
        elif report == "default":
            self.default()


    def clickbait(self):
        report_table = self.copy()
        report_table.filter_by(self.CTR, 15, "gt")
        report_table.filter_by(self.RETENTION, 40, "lt")
        report_table.sort_data(self.CTR, True)
        report_table.show([self.TITLE, self.CTR, self.RETENTION])


    def default(self):
        self.show()
