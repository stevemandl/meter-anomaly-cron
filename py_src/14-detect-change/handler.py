# 14-detect-change/handler.py
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, HTTPError

from python_lib.utils import parse_event, fetch_trends
import json


def run(event, context):
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    now = datetime.now()
    print(f"detect change from prior year run at {now} with event {event}")
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    end_time = params.get("timeStamp")
    start_time = end_time - timedelta(30)
    prior_end_time = end_time - timedelta(365)
    prior_start_time = prior_end_time - timedelta(30)
    point_name = params.get("pointName")
    try:
        # fetch the trends
        current_trend_response = fetch_trends(
            point=point_name, start_time=start_time, end_time=end_time
        )
        prior_trend_response = fetch_trends(
            point=point_name, start_time=prior_start_time, end_time=prior_end_time
        )
        if type(current_trend_response) is list and type(prior_trend_response) is list:
            # assume lists of numbers
            current_total = sum([x[1] for x in current_trend_response[0]["datapoints"]])
            prior_total = sum([x[1] for x in prior_trend_response[0]["datapoints"]])
            
            # this is the logic in the anomaly detection:
            if current_total > prior_total * 2:
                response[
                    "body"
                ] = f"{point_name} consumption is more than double from prior year for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
        else:  # response should always be a list
            response[
                "body"
            ] = f"{point_name} unexpected error: missing response list for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M} or 1 year prior"
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
