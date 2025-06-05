import gpxpy
import pandas as pd

def parse_gpx(file):
    gpx = gpxpy.parse(file)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    'time': point.time,
                    'lat': point.latitude,
                    'lon': point.longitude,
                    'elevation': point.elevation
                })
    return pd.DataFrame(data)
