import os
from tabulate import tabulate
import csv
import logging
import operator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)


COLUMN_NAME_TITLE = {
    "title" : str,
    "ctr" : float,
    "retention_rate" : int,
    "views" : int,
    "likes" : int,
    "avg_watch_time" : float
}


class ClickbaitAnalyzer:
    #COLUMNS = ["title", "ctr", "retention_rate", "views", "likes", "avg_watch_time"]
    #TYPES = [str, float, int, int, int, float]


    def __init__(self, files=None):
        self.data = []
        if files:
            for file_path in files:
                self.load(file_path)


    def append(self, row):
        try:
            if len(row) != len(COLUMN_NAME_TITLE):
                raise ValueError(f"Expected {len(COLUMN_NAME_TITLE)} columns per row: {row}")
            converted_row = []
            for value, target_type in zip(row, COLUMN_NAME_TITLE.values()):
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
        try:
            if not self.data:
                raise ValueError("No data")
            if  column_name and column_name not in COLUMN_NAME_TITLE.keys():
                raise ValueError(f"Column name '{column_name}' not found")
            column_index = 0
            if column_name:
                column_index = list(COLUMN_NAME_TITLE.keys()).index(column_name)
            self.data.sort(key=lambda x: x[column_index], reverse=reverse)
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")



    def filter_by(self, column_name, threshold, mode="greater"):
        ops = {
            "greater": operator.gt,  # >
            "less": operator.lt,  # <
            "ge": operator.ge,  # >=
            "le": operator.le  # <=
        }
        try:
            if column_name not in COLUMN_NAME_TITLE:
                raise ValueError(f"Column '{column_name}' not found in configuration")
            if mode not in ops:
                raise ValueError(f"Invalid mode '{mode}'. Available: {list(ops.keys())}")
            column_index = list(COLUMN_NAME_TITLE.keys()).index(column_name)
            op_func = ops[mode]
            target_type = COLUMN_NAME_TITLE[column_name]
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
            print(tabulate(self.data, headers=list(COLUMN_NAME_TITLE.keys()), tablefmt="fancy_grid"))
        else:
            all_columns = list(COLUMN_NAME_TITLE.keys())
            indices = [all_columns.index(c) for c in show_cols if c in COLUMN_NAME_TITLE]
            headers = [all_columns[i] for i in indices]
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
        self.filter_by("ctr", 15, "greater")
        self.filter_by("retention_rate", 40, "less")
        self.sort_data("ctr", True)
        self.show(["title", "ctr", "retention_rate"])


    def default(self):
        self.show()
