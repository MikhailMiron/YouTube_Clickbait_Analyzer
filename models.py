import os
from tabulate import tabulate
import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

class MyTable:
    COLUMNS = ["title", "ctr", "retention_rate", "views", "likes", "avg_watch_time"]
    TYPES = [str, float, int, int, int, float]


    def __init__(self):
        self.data = []


    def append(self, row):
        try:
            if len(row) != len(self.COLUMNS):
                raise ValueError(f"Expected {len(self.COLUMNS)} columns per row: {row}")
            converted_row = []
            for value, target_type in zip(row, self.TYPES):
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
            column_index = 0
            if not column_name:
                column_index = 0
            elif column_name not in self.COLUMNS:
                raise ValueError(f"Column name '{column_name}' not found")
            else:
                column_index = self.COLUMNS.index(column_name)
            self.data.sort(key=lambda x: x[column_index], reverse=reverse)
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")


    def remove_if_less(self, column_name, threshold):
        try:
            if column_name not in self.COLUMNS:
                raise ValueError(f"Column name '{column_name}' not found")
            column_index = self.COLUMNS.index(column_name)
            self.data = [row for row in self.data if row[column_index] > threshold]
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")


    def remove_if_greater(self, column_name, threshold):
        try:
            if column_name not in self.COLUMNS:
                raise ValueError(f"Column name '{column_name}' not found")
            column_index = self.COLUMNS.index(column_name)
            self.data = [row for row in self.data if row[column_index] <threshold]
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")


    def show(self, show_cols=None):
        if not self.data:
            print("No data")
        elif show_cols is None:
            print(tabulate(self.data, headers=self.COLUMNS, tablefmt="fancy_grid"))
        else:
            indices = [self.COLUMNS.index(c) for c in show_cols if c in self. COLUMNS]
            headers = [self.COLUMNS[i] for i in indices]
            filtered_data = []
            for row in self.data:
                filtered_data.append([row[i] for i in indices])
            print(tabulate(filtered_data, headers=headers, tablefmt="fancy_grid"))


    def clear(self):
        self.data = []
        logger.info(f"Clearing table")



    def report(self, report):
        if report == "clickbait":
            self.clickbait()
        elif report == "standard":
            self.standard()


    def clickbait(self):
        self.remove_if_less("ctr", 15)
        self.remove_if_greater("retention_rate", 40)
        self.sort_data("ctr", True)
        self.show(["title", "ctr", "retention_rate"])


    def standard(self):
        self.show()
