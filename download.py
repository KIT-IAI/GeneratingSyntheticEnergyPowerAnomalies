import os
import requests

import pandas as pd


OPSD_URL = 'https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv'
OPSD_KEEP = [
    'utc_timestamp',
    'DE_load_actual_entsoe_transparency',
]


def download(url, output):
    r = requests.get(url)
    with open(output, "wb") as file:
        file.write(r.content)


def load_csv(path):
    with open(path, 'rb') as file:
        pkl = pd.read_csv(file)
        file.close()
    return pkl


def main():
    download(OPSD_URL, 'opsd.csv')
    opsd = load_csv('opsd.csv')
    opsd = opsd[OPSD_KEEP]
    opsd['utc_timestamp'] = pd.to_datetime(opsd['utc_timestamp'])
    opsd.set_index('utc_timestamp', inplace=True)
    opsd.index = opsd.index.tz_convert(None)
    opsd = opsd.iloc[1:]
    opsd.to_csv('opsd.csv')
    print(opsd.describe())
    print(opsd)


if __name__ == '__main__':
    main()
