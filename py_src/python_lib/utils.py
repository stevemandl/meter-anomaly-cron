# python_lib/utils.py
# generic utility functions

import os
from datetime import datetime
from dateutil import parser
import requests
import numpy as np
import pandas as pd

# globals
PORTAL_API_URL = os.environ.get("PORTAL_API_URL", "/")
QUERY_URL = f"{PORTAL_API_URL}query"

class AnomalyError(Exception):
    "Anomaly Exception class"

def parse_event(event):
    """
    :param dict event: passed in by the lambda environment
    """
    if not "body" in event:
        raise RuntimeError("body is a required attribute in event")
    body = event.get("body").copy()
    if not "pointName" in body:
        raise RuntimeError("pointName is a required attribute in event.body")
    if "timeStamp" in body:
        ts = body["timeStamp"]
        if type(ts) is str:
            if ts.isnumeric():
                body["timeStamp"] = datetime.fromtimestamp(float(ts))
            else:
                body["timeStamp"] = parser.parse(ts)
        else:
            if type(ts) is int or type(ts) is float:
                body["timeStamp"] = datetime.fromtimestamp(float(ts))
            else: raise RuntimeError("invalid timeStamp")
    else:
        body["timeStamp"] = datetime.now()
    return body


def fetch_trends(point=None, points=None, start_time=None, end_time=datetime.now(), additional=[]):
    """Returns trend response(s) for all of the points provided in the time range specified
    :param string point: cannot be provided with points
    :param list points: cannot be provided with point
    :param datetime start_time: required
    :param datetime end_time: optional, defaults to now()
    :param list additional : optional additional data to pass to API, defaults to []
    """
    # ensure points is a list
    if point and points:
        raise TypeError("Can't supply both point and points parameters")
    if not points:
        points = [point]
    targets = [
        {"target": p, "payload": {"additional": additional}, "type": "timeseries"}
        for p in points
    ]
    request_data = {
        "range": {"from": start_time.isoformat(), "to": end_time.isoformat()},
        "targets": targets,
    }
    request_headers = {"Content-Type": "application/json"}
    raw_response = requests.post(QUERY_URL, json=request_data, headers=request_headers)
    raw_response.raise_for_status()

    return raw_response.json()

def build_index(response):
    """
    Returns a dict with target names as indexes to dictionaries of data values indexed by their timestamps
    :expects a trend response in the format returned by the fetch_trends function
    :param empty response returns an empty dict
    
    """
    index = {}
    for (_, entry) in enumerate(response):
        data= {}
        for (_, time) in enumerate(entry["datapoints"]):
            data[time[1]] = time[0]
            index.update({entry["target"]:data})
    return(index)

def build_df(response, interpolate = True):
    """ 
    converts response to dataframe
    keyword arguments:
    response - a trend response like one returned by fetch_trends()
    interpolate - optional, defalut=True. If true, the columns are interpolated
    """
    df = pd.DataFrame()
    for t in response:
        a = np.array(t["datapoints"])
        if a.size == 0:
            continue
        t_df = pd.DataFrame.from_records(a, columns = (t["target"], "ts"), index="ts")
        if df.empty:
            df = t_df
        else:
            df = df.merge(t_df, how="outer", on="ts")
    df.index = pd.to_datetime(df.index, unit='ms')
    if interpolate:
        return df.interpolate()
    return df
