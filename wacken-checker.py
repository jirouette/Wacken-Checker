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

def monitorPool(pool: str):
    if pool not in POOLS.keys():
        raise Exception(f"unknown pool {pool}")
    endpoint = 'https://www.strasbourg.eu/lieu/-/entity/sig/' + POOLS[pool]
    while True:
        html = requests.get(endpoint, headers={'User-Agent': "jr's Wacken Checker https://github.com/jirouette/wacken-checker"}).text
        try:
            chunk = html.split('<div class="crowded-amount')[1]
            amount = chunk.split('>')[1].split('</div')[0].strip().replace('-', '0')
            level = chunk.split('"')[0].strip()
            now = datetime.datetime.now()
            if os.environ.get('DEBUG', '0') == '1':
                print(now, amount, level)
            filename = os.environ.get('FILENAME', f"{pool}-report-{now.strftime('%Y-%m-%d')}.csv")
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
