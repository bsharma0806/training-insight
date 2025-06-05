import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

def parse_tcx(file):
    tree = ET.parse(file)
    root = tree.getroot()
    ns = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    data = []
    for trackpoint in root.findall('.//ns:Trackpoint', ns):
        time = trackpoint.find('ns:Time', ns)
        hr = trackpoint.find('ns:HeartRateBpm/ns:Value', ns)
        cad = trackpoint.find('ns:Cadence', ns)
        dist = trackpoint.find('ns:DistanceMeters', ns)
        ele = trackpoint.find('ns:AltitudeMeters', ns)
        data.append({
            'time': datetime.fromisoformat(time.text[:-1]) if time is not None else None,
            'heart_rate': int(hr.text) if hr is not None else None,
            'cadence': int(cad.text) if cad is not None else None,
            'distance': float(dist.text) if dist is not None else None,
            'elevation': float(ele.text) if ele is not None else None
        })
    return pd.DataFrame(data)
