# python_template/handler.py
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, HTTPError

from python_lib.utils import parse_event, fetch_trends
import json


def run(event, context):
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    now = datetime.now()
    WINDOW_SIZE = weeks=1 
    MAX_ERROR = 10 #try with different error values (in decimal values)
    # print(f"testTemplate run at {now} with event {event}")
    # parse event and ensure timeStamp and pointName are present

    # Fetch datetime for previous year
    last_year_date = datetime.now() - datetime.timedelta(years=1)

    params = parse_event(event)

    end_time = params.get("timeStamp")
    start_time = end_time - timedelta(WINDOW_SIZE) 
    point_name = params.get("pointName")

    start_time_last_year = last_year_date - timedelta(WINDOW_SIZE) 
    #point name is already fetched
    
    try:
        # fetch the trends
        trend_response = fetch_trends(
            point=point_name, start_time=start_time, end_time=end_time
        )
        trend_response_last_year = fetch_trends(
            point=point_name, start_time=start_time_last_year, end_time=last_year_date
        )
        # at this point, status_code must be 200 or an exception would be raised
        # data should always be there, but just to be on the safe side, make an if statement
        if type(trend_response) is list and type(trend_response_last_year) is list: 
            
            #first average the meter values for the current year
            sum = 0
            for i in range(len(trend_response[0]["datapoints"])): 
                sum = sum + trend_response[0]["datapoints"][i][0]
            meter_value_average_curr = sum / (len(trend_response[0]["datapoints"]))
            
            #then average the meter values for the past year 
            sum = 0
            for i in range(len(trend_response_last_year[0]["datapoints"])): 
                sum = sum + trend_response_last_year[0]["datapoints"][i][0]
            meter_value_average_last_year = sum / (len(trend_response_last_year[0]["datapoints"]))

            #calculate the percent difference between two years 
            percent_diff = (abs(meter_value_average_curr - meter_value_average_last_year) / meter_value_average_last_year)*100
            # this is the logic in the anomaly detection:
            if (percent_diff > MAX_ERROR):
                response[
                    "body"
                ] = f"{point_name} deviates by {percent_diff}% from the previous year's \
                    data for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M} \
                    which is {percent_diff - MAX_ERROR} greater than the maximum error allowed of {MAX_ERROR}"
            else: 
                response[
                    "body"
                ] = f"No anomaly detected for {point_name} for the period {start_time:%Y-%m-%d %H:%M} to {end_time:%Y-%m-%d %H:%M}"

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