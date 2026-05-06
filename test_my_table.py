import pytest
import logging
from models import ClickbaitAnalyzer, COLUMN_NAME_TITLE


@pytest.fixture
def table():
    return ClickbaitAnalyzer()


@pytest.fixture
def table_success():
    return ClickbaitAnalyzer()


def test_append_success(table):
    row = ["Я бросил IT и стал фермером", "18.2", "35", "45200", "1240", "4.2"]
    table.append(row)
    assert len(table.data) == 1
    assert table.data[0] == ["Я бросил IT и стал фермером", 18.2, 35, 45200, 1240, 4.2]
    types = list(COLUMN_NAME_TITLE.values())
    for value, target_type in zip(table.data[0], types):
        assert isinstance(value, target_type)


def test_append_wrong_length(table):
    row1 = ["18.2", "35", "45200", "1240", "4.2"]
    row2 = ["Как я спал по 4 часа и ничего не понял", "22.5", "28", "128700", "3150"]
    table.append(row1)
    table.append(row2)
    assert len(table.data) == 0


def test_append_type_error(table):
    row = ["Я бросил IT и стал фермером", "18.2", "35.5", "45200", "1240", "4.2"]
    table.append(row)
    assert len(table.data) == 0


def test_append_logging(table, caplog):
    with caplog.at_level(logging.ERROR):
        table.append(["Я бросил IT и стал фермером", "18.2", "qwer", "45200", "1240", "4.2"])
    assert "Data validation error:" in caplog.text


def test_load_success(table):
    table.load("test.csv")
    assert len(table.data) == 100


def test_load_unexpected_file_extension(table, caplog):
    with caplog.at_level(logging.ERROR):
        table.load("test_my_table.py")
    assert "Unexpected file extension 'test_my_table.py': .py" in caplog.text


def test_load_csv_file_not_found(table, caplog):
    with caplog.at_level(logging.ERROR):
        table.load("file_not_found.csv")
    assert "File 'file_not_found.csv' not found" in caplog.text


def test_sort_data_success(table, table_success):
    table.load("test.csv")
    table.sort_data("ctr", True)
    table_success.load("test_sort.csv")
    assert table.data == table_success.data


def test_sort_data_data_validation_error(table, caplog):
    with caplog.at_level(logging.ERROR):
        table.load("test.csv")
        table.sort_data("qwert", True)
    assert "Data validation error: Column name 'qwert' not found" in caplog.text


def test_filter_by_validation_error(table, caplog):
    with caplog.at_level(logging.ERROR):
        table.load("test.csv")
        table.filter_by("qwert", 15, "greater")
    assert "Filter error: Column 'qwert' not found in configuration" in caplog.text

def test_filter_by(table, table_success):
    table.load("test.csv")
    table.filter_by("ctr", 15, "greater")
    table.filter_by("retention_rate", 40, "less")
    assert len(table.data) == 34


def test_show_default(table, capsys):
    row = ["Я бросил IT и стал фермером", "18.2", "35", "45200", "1240", "4.2"]
    table.append(row)
    table.default()
    captured = capsys.readouterr()
    assert "Я бросил IT и стал фермером" in captured.out
    assert "╒" in captured.out
    assert "title" in captured.out
    assert "ctr" in captured.out
    assert "retention_rate" in captured.out
    assert "views" in captured.out
    assert "likes" in captured.out
    assert "avg_watch_time" in captured.out


def test_show_clickbait(table, capsys):
    table.load("test.csv")
    table.clickbait()
    captured = capsys.readouterr()
    assert "title" in captured.out
    assert "ctr" in captured.out
    assert "retention_rate" in captured.out
    assert "views" not in captured.out
    assert "likes" not in captured.out
    assert "avg_watch_time" not in captured.out


def test_show_no_data(table, capsys):
    table.show()
    captured = capsys.readouterr()
    assert captured.out == "No data\n"