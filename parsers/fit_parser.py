from fitparse import FitFile
import pandas as pd

def parse_fit(file):
    fitfile = FitFile(file)
    records = []
    for record in fitfile.get_messages('record'):
        data = {}
        for d in record:
            data[d.name] = d.value
        records.append(data)
    return pd.DataFrame(records)
