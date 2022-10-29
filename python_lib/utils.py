# python_lib/utils.py
# generic utility functions

import os
from datetime import datetime
from dateutil import parser
import requests
import math

# globals
PORTAL_API_URL = os.environ.get("PORTAL_API_URL", "/")
QUERY_URL = f"{PORTAL_API_URL}query"


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
            body["timeStamp"] = parser.parse(ts)
        else:
            if type(ts) is int or type(ts) is float:
                body["timeStamp"] = datetime.fromtimestamp
            else:
                raise RuntimeError("invalid timeStamp")
    else:
        body["timeStamp"] = datetime.now()
    return body


def fetch_trends(point=None, points=None, start_time=None, end_time=datetime.now()):
    """Returns trend response(s) for all of the points provided in the time range specified
    :param string point: cannot be provided with points
    :param list points: cannot be provided with point
    :param datetime start_time: required
    :param datetime end_time: optional, defaults to now()
    """
    # ensure points is a list
    if point and points:
        raise TypeError("Can't supply both point and points parameters")
    if not points:
        points = [point]
    targets = [
        {"target": p, "payload": {"additional": []}, "type": "timeseries"}
        for p in points
    ]
    request_data = {
        "range": {"from": start_time.isoformat(), "to": end_time.isoformat()},
        "targets": targets,
    }
    request_headers = {"Content-Type": "application/json"}
    raw_response = requests.post(
        QUERY_URL, json=request_data, headers=request_headers)
    raw_response.raise_for_status()

    return raw_response.json()
