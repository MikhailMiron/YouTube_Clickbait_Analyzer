from models import ClickbaitAnalyzer
import argparse

REPORT_TYPE_CLICKBAIT = ["clickbait", "default"]


def main():
    parser = argparse.ArgumentParser(description="A CLI application for processing CSV files with YouTube video metrics.")
    parser.add_argument("--files", nargs="+", required=True, help="List of CSV files to process.")
    parser.add_argument("--report", choices=REPORT_TYPE_CLICKBAIT, help="Report title.", default="default")

    args = parser.parse_args()
    table = ClickbaitAnalyzer(args.files)
    table.report(args.report)


if __name__ == '__main__':
    main()

