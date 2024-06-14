"""
 same_value/handler.py
"""

from datetime import timedelta
from requests.exceptions import ConnectionError as RequestConnectionError, HTTPError

from python_lib.utils import parse_event, fetch_trends

# the minimum acceptable length of the datapoints array
MIN_DATAPOINTS_LENGTH = 100


def run(event, _context):
    """
    handler.run - the lambda function entry point
    """
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    print(f"Same_value_algorithm handler run with params {params}")
    end_time = params.get("timeStamp")
    start_time = end_time - timedelta(7)
    point_name = params.get("pointName")
    try:
        # fetch the trends
        trend_response = fetch_trends(
            point=point_name, start_time=start_time, end_time=end_time
        )
        # at this point, status_code must be 200 or an exception would be raised
        # data should always be there, but just to be on the safe side, make an if statement
        if isinstance(trend_response, list):
            # this is the logic in the anomaly detection:
            datapoints = trend_response[0]["datapoints"]
            if len(datapoints) > MIN_DATAPOINTS_LENGTH:
                values = [p[0] for p in datapoints]
                if all(p == values[0] for p in values):
                    response[
                        "body"
                    ] = f"""{point_name} is stuck at value {values[0]} 
                    for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"""
        else:  # response should always be a list
            response["body"] = (
                f"{point_name} unexpected error: missing response list for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
            )
    except RequestConnectionError as err:
        response["body"] = (
            f"{point_name} ConnectionError: {err.response.text} {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
        )
    except HTTPError as err:
        response["body"] = (
            f"{point_name} {err.response.text} for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
        )
        if err.response.status_code == 400:
            try:  # have to try decoding json
                if err.response.json()["error"] == "No data":
                    response["body"] = (
                        f"{point_name} has no data for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"
                    )
            except ValueError:
                pass
    return response
