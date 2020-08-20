#!/usr/bin/python
#coding: utf8

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

def triggerWebhook(pool, amount, thresold, lastReports):
    endpoint = os.environ.get('DISCORD_ENDPOINT')
    if not endpoint:
        return
    reports = "\n".join([f"**{x['date']}:** {x['amount']} _({x['level']})_" for x in lastReports][::-1])
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

def monitorPool(pool: str):
    if pool not in POOLS.keys():
        raise Exception(f"unknown pool {pool}")
    endpoint = 'https://www.strasbourg.eu/lieu/-/entity/sig/' + POOLS[pool]
    thresold = int(os.environ.get('THRESHOLD', 100))
    passedThresold = None
    lastReports = []
    while True:
        html = requests.get(endpoint, headers=HEADERS).text
        try:
            chunk = html.split('<div class="crowded-amount')[1]
            amount = int(chunk.split('>')[1].split('</div')[0].strip().replace('-', '0'))
            level = chunk.split('"')[0].strip()
            now = datetime.datetime.now()
            if passedThresold is None:
                passedThresold = amount < thresold
            if amount < thresold and not passedThresold:
                passedThresold = True
                triggerWebhook(pool, amount, thresold, lastReports)
            elif amount > thresold and passedThresold:
                passedThresold = False

            lastReports.append(dict(date=now, amount=amount, level=level))
            if (len(lastReports) > 5):
                lastReports.pop(0)
            if os.environ.get('DEBUG', '0') == '1':
                print(now, amount, level)
            filename = "reports/"+os.environ.get('FILENAME', f"{pool}-report-{now.strftime('%Y-%m-%d')}.csv")
            exists = os.path.isfile(filename)
            with open(filename, 'a') as f:
                if not exists:
                    f.write("date,amount,level\n")
                f.write(f"{now.isoformat()},{amount},{level}\n")
        except KeyError:
            raise Exception('could not find amount, stopping here')
        time.sleep(int(os.environ.get('FREQUENCY', 300)))

if __name__ == '__main__':
    monitorPool(sys.argv[1] if len(sys.argv) > 1 else os.environ.get('POOL','wacken'))
