# python_template/handler.py
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, HTTPError

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
        if type(trend_response) is list:
            # this is the logic in the anomaly detection:
            if len(trend_response[0]["datapoints"]) < 648:
                response[
                    "body"
                ] = f"{point_name} is missing more than 10% of values for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
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