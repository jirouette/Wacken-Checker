# Wacken Checker

This project monitors how many people are currently in the swimming-pools of Strasbourg, France, and write it in a CSV file. 

## Installation

```bash
pip install
python wacken-checker.py <pool> # e.g. 'schiltigheim'
```

## Usage

List of pools:
- `schiltigheim` : Centre Nautique de Schiltigheim _(48.6123770720720, 7.72908979086701)_
- `hautepierre` : Piscine de Hautepierre _(48.5983064284019, 7.69324795811826)_
- `hardt` : Piscine de la Hardt _(48.5304900493167, 7.70187167930799)_
- `kibitzenau` : Piscine de la Kibitzenau _(48.5574641069371, 7.76380840638018)_
- `robertsau` : Piscine de la Robertsau _(48.6173032255352, 7.78917997795127)_
- `lingolsheim` : Piscine de Lingolsheim _(48.5628668947217, 7.68157667603039)_
- `ostwald` : Piscine de Ostwald _(48.5473112963048, 7.71203524662106)_
- `wacken` : Pisicne du Wacken _(48.6011130870981, 7.76750947125112)_

You can also define the following environment vars:

- `DEBUG` : if `1`, it will print the result to the output in addition to writing to a CSV file
- `FILENAME` : define the file where the results will be saved. Default : `{pool}-report.csv` were pool is the codename of the selected pool
- `POOL` : define the selected pool (will be overrided by the first argument if it exists)
- `FREQUENCY` : frequency of the monitoring, in seconds. Default : 300sec (5min).

## Next steps

- Add Docker support
- Add the level of the current amount (green, orange, red, black)
- Add notifications integrations (Discord, Mattermost, ...)
