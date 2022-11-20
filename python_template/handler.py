# python_template/handler.py
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, HTTPError

from python_lib.utils import parse_event, fetch_trends
import json
import numpy as np


def run(event, context):
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    now = datetime.now()
    print(f"testTemplate run at {now} with event {event}")
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
        if type(trend_response) is list:
            # this is the logic in the anomaly detection:

            # Spotty Data Check
            if len(trend_response[0]["datapoints"]) < 648:
                response[
                    "body"
                ] = f"{point_name} is missing more than 10% of values for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"

            # Ignoring significant increases in nighttime baseline on CW meters as Cole does not think this is useful

            # Stuck at Same Reading
            sampleSize = 5

            def GetSpacedElements(array, numElems=4):
                out = array[np.round(np.linspace(
                    0, len(array)-1, numElems)).astype(int)]
                return out
            spacedArray = GetSpacedElements(
                trend_response[0]["datapoints"], sampleSize)

            def all_same(items):
                return all(x == items[0] for x in items)
            if all_same(spacedArray):
                response[
                    "body"
                ] = f"{point_name} is stuck at the same reading for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"

            # Significant changes in ratio of meter reading to cooling degrees(or enthalpy)
            end_time_last_week = end_time - timedelta(10080)
            start_time_last_week = end_time_last_week - timedelta(30)
            trend_past_response = fetch_trends(
                point=point_name, start_time=start_time_last_week, end_time=end_time_last_week
            )
            current_mean = np.mean(trend_response[0]["datapoints"])
            # change index
            past_mean = np.mean(trend_past_response[0]["datapoints"])
            ratio = current_mean/past_mean
            if ratio < 0.5 or ratio > 2:
                response[
                    "body"
                ] = f"{point_name} is significantly different from {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M} compared to last week's readings for cooling degrees"

            # Significant changes in ratio of meter reading to heating degrees
            end_time_last_week = end_time - timedelta(10080)
            start_time_last_week = end_time_last_week - timedelta(30)
            trend_past_response = fetch_trends(
                point=point_name, start_time=start_time_last_week, end_time=end_time_last_week
            )
            current_mean = np.mean(trend_response[1]["datapoints"])
            # change index
            past_mean = np.mean(trend_past_response[1]["datapoints"])
            ratio = current_mean/past_mean
            if ratio < 0.5 or ratio > 2:
                response[
                    "body"
                ] = f"{point_name} is significantly different from {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M} compared to last week's readings for heating degrees"

            # Significant changes in ratio of meter reading to year ago
            end_time_last_year = end_time - timedelta(31536000)
            start_time_last_year = end_time_last_week - timedelta(30)
            trend_past_response = fetch_trends(
                point=point_name, start_time=start_time_last_week, end_time=end_time_last_year
            )
            for i in range(len(trend_past_response)):
                current_mean_now = np.mean(trend_response[i]["datapoints"])
            # change index
                past_mean_year = np.mean(trend_past_response[i]["datapoints"])
                ratio = current_mean_now/past_mean_year
                if ratio < 0.5 or ratio > 2:
                    response[
                        "body"
                    ] = f"{point_name} Energy type {i} is significantly different from {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M} compared to last year's readings for heating degrees"

        else:  # response should always be a list
            response[
                "body"
            ] = f"{point_name} unexpected error: missing response list for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
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


"""
Possible changes to the handler:
Obvious faults: 
WhiteHall 
    Electric March 2022
    Steep drop in electricity consumption when no building improvements have been made
Rhodes Hall
    No reading between April 18th and some time in May
    Network Operations Center (NOC) Chilled Water detection was not working either  
Rhodes seems to be implemented but need to implement WhiteHall!
"""
