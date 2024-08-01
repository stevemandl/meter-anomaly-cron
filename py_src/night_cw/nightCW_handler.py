# python_template/handler.py
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, HTTPError
import numpy as np
from scipy.stats import norm
from python_lib.utils import parse_event, fetch_trends
import json


def run(event, context):
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    now = datetime.now()
    # print(f"testTemplate run at {now} with event {event}")
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    end_time = params.get("timeStamp")
    start_time = end_time - timedelta(30)
    point_name = params.get("pointName")
    try:
        # fetch the trends
        trend_response = fetch_trends(
            point=point_name, start_time=start_time, end_time=end_time
        )
        # at this point, status_code must be 200 or an exception would be raised
        # data should always be there, but just to be on the safe side, make an if statement
        datapoints = trend_response[0]["datapoints"]
        target_range = 7
        #target_range is the number of back from today that are being considered
        threshhold = 0.3
        #threshhold is the cumulative distribution percentage that is the baseline
        for i in range(target_range):
            datapoints.pop()
        #removes the target data from the data that will be used to create the baseline
        baseload = datapoints.ppf(threshhold)
        #.ppf function returns the value at the cumulative distribution threshhold
        target = trend_response[0]["datapoints"][(len(datapoints)-1):]
        #extracts the target points from the trend response
        if target.ppf(threshhold) > baseload:
            response[
                "body"
                ] = f"""{point_name} has a baseload {target.ppf(threshhold)} which is greater than the previous baseload{baseload}
                    for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"""
        #returns the response when the target baseload has increased.
    except ConnectionError as err:
        response[
            "body"
        ] = f"{point_name} ConnectionError: {err.response.text} {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
    except HTTPError as err:
        response[
            "body"
        ] = f"{point_name} {err.response.text} for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
        if err.response.status_code == 400:
            try:  # have to try decoding json
                if err.response.json()["error"] == "No data":
                    response[
                        "body"
                    ] = f"{point_name} has no data for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
            except ValueError as e:
                pass
    return response
