#!/usr/bin/python
#coding: utf8

from typing import List, Tuple
import requests
import time
import datetime
import sys
import os
import os.path

POOLS = {
    'schiltigheim': '401_SPO_2',
    'hautepierre': '402_SPO_3',
    'hardt': '403_SPO_4',
    'kibitzenau': '404_SPO_5',
    'robertsau': '405_SPO_6',
    'lingolsheim': '406_SPO_7',
    'ostwald': '407_SPO_8',
    'wacken': '408_SPO_9'
}

HEADERS = {
    'User-Agent': "jr's Wacken Checker https://github.com/jirouette/wacken-checker"
}

lastReports = []
passedThreshold = False

class Report(object):
    def __init__(self, date: str, amount: int, level: str) -> None:
        self.date = date
        self.amount = amount
        self.level = level

def triggerWebhook(pool: str, amount: int, thresold: int, lastReports: List[Report]) -> None:
    endpoint = os.environ.get('DISCORD_ENDPOINT')
    if not endpoint:
        return
    reports = "\n".join([f"**{x.date}:** {x.amount} _({x.level})_" for x in lastReports][::-1])
    payload = {
        'embeds': [
            {
                'title': f"Currently {amount} persons are in {pool}",
                'description': f"Threshold: {thresold}\nOther reports\n"+reports
            }
        ]
    }
    x = requests.post(endpoint, json=payload, headers=HEADERS)
    print(x.text)

def checkThreshold(pool: str, report: Report):
    global passedThreshold
    global lastReports
    threshold = int(os.environ.get('THRESHOLD', 100))
    if passedThreshold is None:
        passedThreshold = report.amount < threshold
    if report.amount < threshold and not passedThreshold:
        passedThreshold = True
        triggerWebhook(pool, report.amount, threshold, lastReports)
    elif report.amount > threshold and passedThreshold:
        passedThreshold = False

def fetchData(pool: str) -> Tuple[int, str]:
    endpoint = 'https://www.strasbourg.eu/lieu/-/entity/sig/' + POOLS[pool]
    html = requests.get(endpoint, headers=HEADERS).text
    try:
        chunk = html.split('<div class="crowded-amount')[1]
        amount = int(chunk.split('>')[1].split('</div')[0].strip().replace('-', '0'))
        level = chunk.split('"')[0].strip()
        return amount, level
    except KeyError:
        raise Exception('could not find amount nor level, stopping here')

def writeIntoCsv(pool: str, report: Report) -> None:
    filename = "reports/"+os.environ.get('FILENAME', f"{pool}-report-{report.date.strftime('%Y-%m-%d')}.csv")
    exists = os.path.isfile(filename)
    with open(filename, 'a') as f:
        if not exists:
            f.write("date,amount,level\n")
        f.write(f"{report.date.isoformat()},{report.amount},{report.level}\n")

def monitorPool(pool: str) -> None:
    global lastReports
    if pool not in POOLS.keys():
        raise Exception(f"unknown pool {pool}")
    while True:
        # Fetching and preparing data
        amount, level = fetchData(pool)
        now = datetime.datetime.now()
        report = Report(date=now, amount=amount, level=level)

        # Ignoring moment where the pool is closed
        if level == "grey":
            time.sleep(int(os.environ.get('FREQUENCY', 300)))
            continue

        # Checking threshold
        checkThreshold(pool, report)

        # Saving last 5 reports
        lastReports.append(report)
        if (len(lastReports) > 5):
            lastReports.pop(0)

        # Saving to CSV
        if os.environ.get('DEBUG', '0') == '1':
            print(report.date, report.amount, report.level)
        writeIntoCsv(pool, report)

        # Now sleeping
        time.sleep(int(os.environ.get('FREQUENCY', 300)))

if __name__ == '__main__':
    monitorPool(sys.argv[1] if len(sys.argv) > 1 else os.environ.get('POOL','wacken'))
