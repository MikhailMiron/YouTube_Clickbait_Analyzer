from models import MyTable
import argparse

def main():
    parser = argparse.ArgumentParser(description="A CLI application for processing CSV files with YouTube video metrics.")
    parser.add_argument("--files", nargs="+", required=True, help="List of CSV files to process.")
    parser.add_argument("--report", choices=["clickbait"], help="Report title.", default="standard")

    args = parser.parse_args()
    table = MyTable()
    for file in args.files:
        table.load(file)
    table.report(args.report)


if __name__ == '__main__':
    main()

