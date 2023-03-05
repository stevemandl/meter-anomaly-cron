# python_template/handler.py
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, HTTPError
from python_lib.utils import parse_event, fetch_trends
import json
import pandas as pd


def run(event, context):
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    now = datetime.now()
    # print(f"testTemplate run at {now} with event {event}")
    # parse event and ensure timeStamp and pointName are present
    print(event)
    params = parse_event(event)
    end_time = params.get("timeStamp")
    start_time = end_time - timedelta(hours=2920)
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
            # print(trend_response)

            data = trend_response[0]['datapoints'] # the timestamps are multiplied by 1000 for some reason?

            dt = int(timedelta(hours=24).total_seconds()*1000)
            num_missing = 0
            where_missing = []
            total = int((data[len(data)-1][1] - data[0][1])/dt)
            for i in range(len(data) - 1):
                # print((data[i+1][1] - data[i][1])/dt)
                if data[i+1][1] - data[i][1] != dt:
                    num_missing += int((data[i+1][1] - data[i][1])/dt)
                    where_missing.append((data[i][1], data[i+1][1]))
            if num_missing > 0:
                s = f"{point_name} is missing more than {int((num_missing / total)*100)}% of values for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}. \n They are missing for the following time period(s):\n"
                output = [s]
                for duration in where_missing:
                    output.append(f' - From {datetime.fromtimestamp(duration[0]//1000):%Y-%m-%d %H:%M} to {datetime.fromtimestamp(duration[1]//1000):%Y-%m-%d %H:%M}')
                response[
                    "body"
                ] = ''.join(output)
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
