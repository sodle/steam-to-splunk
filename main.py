#!/usr/bin/env python3
"""Scrape Steam purchase history into Splunk.
Visit https://store.steampowered.com/account/history and save the HTML page to disk, then run this script.

Usage:
    main.py <html_file> [--hec-url=<url>] [--hec-token=<token>] [--index=<index>]

Options:
    -h --help           Show this help.
    -v --version        Show version.
    --hec-url=<url>     Splunk HTTP Event Collector URL [default: https://localhost:8088/services/collector/event].
    --hec-token=<token> Splunk HEC Token (if blank, pulled from SPLUNK_HEC_TOKEN environment variable).
    --index=<index>     Splunk index to send data to [default: steam].

"""
import json
import os
import sys
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import Tag

import requests
import numpy as np

from docopt import docopt


def parse_row(row: Tag, steam_username: str, index: str) -> object:
    record = {}

    items = row.find("td", {"class": "wht_items"}).find_all("div")
    record["items"] = [i.text.strip().split("\t")[0] for i in items]

    record["type"] = row.find("td", {"class": "wht_type"}).find("div").text

    total_col = row.find("td", {"class": "wht_total"})
    total_strings = list(total_col.stripped_strings)
    total_amt = float(total_strings[0].replace("$", "").replace(",", ""))
    if len(total_strings) == 2 and total_strings[1] == "Credit":
        total_amt *= -1
    if record["type"] == "Refund":
        total_amt *= -1
    record["total"] = total_amt

    timestamp_col = row.find("td", {"class": "wht_date"})
    record["date"] = timestamp_col.text

    event = {
        "time": datetime.strptime(record["date"], "%b %d, %Y").timestamp(),
        "event": json.dumps(record, indent=2),
        "host": "store.steampowered.com",
        "sourcetype": "steam:purchase",
        "source": steam_username,
        "index": index
    }

    return event


def main():
    args = docopt(__doc__, version="0.0.1")

    steam_html_path = args.get("<html_file>")
    hec_url = args.get("--hec-url")
    index = args.get("--index")

    hec_token = args.get("--hec-token")
    if hec_token is None:
        hec_token = os.environ.get("SPLUNK_HEC_TOKEN")
    if hec_token is None:
        sys.stderr.write("No HEC token provided! "
                         "Please set either the --hec-token argument or the SPLUNK_HEC_TOKEN environment variable!")
        sys.exit(1)

    with open(steam_html_path, encoding="utf8") as steam_page:
        steam_soup = BeautifulSoup(steam_page)

    steam_username = steam_soup.find("span", {"class": "persona"}).text

    steam_table = steam_soup.find("table")
    steam_rows = steam_table.find_all("tr", {"class": "wallet_table_row"})

    steam_events = [parse_row(row, steam_username, index) for row in steam_rows]
    steam_chunks = np.array_split(steam_events, 20)

    for chunk in steam_chunks:
        requests.post(hec_url, data=json.dumps(chunk.tolist()),
                      headers={"Authorization": f"Splunk {hec_token}"},
                      verify=False).raise_for_status()


if __name__ == "__main__":
    main()
