# python_template/handler.py
from datetime import timedelta, datetime
from requests.exceptions import ConnectionError as RequestConnectionError, HTTPError
from python_lib.utils import parse_event, fetch_trends, MeterAnomaly

# the minimum acceptable length of the datapoints array
MIN_DATAPOINTS_LENGTH = int(30 * 24 * 0.9)
ALGORITHM = "python_template"

def run(event, _context):
    """
    handler.run - the lambda function entry point
    """
    # start out with blank payload
    payload = {}
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    print(f"python_template handler run with params {params}")
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
        if isinstance(trend_response, list):
            # this is the logic in the anomaly detection:
            if len(trend_response[0]["datapoints"]) < MIN_DATAPOINTS_LENGTH:
                desc = "Missing more than 10% of values for the period."
                payload = MeterAnomaly(
                    point_name,
                    ALGORITHM,
                    datetime.now().isoformat(),
                    desc,
                    len(trend_response[0]["datapoints"]),
                    MIN_DATAPOINTS_LENGTH,
                    start_time.isoformat(),
                    end_time.isoformat(),
                )
        else:  # response should always be a list
            payload = MeterAnomaly(
                point_name,
                ALGORITHM,
                datetime.now().isoformat(),
                "unexpected error: missing response list for the period",
                start_ts=start_time.isoformat(),
                end_ts=end_time.isoformat(),
            )
    except RequestConnectionError as err:
        payload["error"] = err.response.text
    except HTTPError as err:
        payload["error"] = err.response.text
        if err.response.status_code == 400:
            try:  # have to try decoding json
                if err.response.json()["error"] == "No data":
                    payload = MeterAnomaly(
                        point_name,
                        ALGORITHM,
                        datetime.now().isoformat(),
                        "No data for the period.",
                        0,
                        MIN_DATAPOINTS_LENGTH,
                        start_time.isoformat(),
                        end_time.isoformat(),
                    )
            except ValueError:
                pass
    return payload
