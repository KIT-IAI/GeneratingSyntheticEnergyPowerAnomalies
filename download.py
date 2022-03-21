import requests

import zipfile


OPSD_URL = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip'
OPSD_KEEP = [
    'utc_timestamp',
    'DE_load_actual_entsoe_transparency',
]


def download(url):
    r = requests.get(url)
    with open(OPSD_URL.split('/')[-1], "wb") as file:
        file.write(r.content)

    with zipfile.ZipFile('LD2011_2014.txt.zip', 'r') as archive:
        archive.extractall('.')


if __name__ == '__main__':
    download(OPSD_URL)
