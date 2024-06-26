"""
low_delta_t/handler.py
"""

from datetime import timedelta
import numpy as np
from requests.exceptions import ConnectionError as RequestConnectionError, HTTPError
from python_lib.utils import parse_event, fetch_trends, build_index, build_df

# the minimum acceptable length of the datapoints array
MIN_DATAPOINTS_LENGTH = int(7 * 24)
RECENT_DAYS = 2

def run(event, _context):
    """
    handler.run - the lambda function entry point
    """
    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    print(f"low_delta_t run with params {params}")

    now = params.get("timeStamp")
    year_ago = now - timedelta(365)
    start_time = now - timedelta(RECENT_DAYS)
    point_name = params.get("pointName")
    if not point_name.endswith("/TONS"):
        response["body"] = f"{point_name} does not end with /TONS"
        return response
    device_name = point_name[:-5]
    stemp_name = f"{device_name}/STEMP"
    rtemp_name = f"{device_name}/RTEMP"
    flow_name = f"{device_name}/FLOW"
    tons_name = point_name
    oat_name = "GameFarmRoadWeatherStation.TAVG_H_F"
    try:
        # fetch previous year's tons for the meter
        tons = build_index(fetch_trends(
            point=point_name, start_time=year_ago, end_time=now, additional= ["aggH"]
        ))
        # fetch recent period STEMP, RTEMP, FLOW, TONS, OAT
        recent_points = (stemp_name, rtemp_name, flow_name, tons_name, oat_name)
        recent = fetch_trends(points=recent_points,start_time=start_time, end_time=now)

        # compute estimated design load from max(tons) over past year
        max_tons = max(tons[point_name].values())
        model_df = build_df(recent)
        # model partial load ratio for the recent period from all fetched data
        model_df["PLR"] = model_df[tons_name] / max_tons
        # model partial temperature ratio
        model_df["PT"] = (model_df[oat_name] - model_df[stemp_name]) / 41
        # DTpred = PLR^0.173 * PT^0.067 * 15.603
        model_df["DT_PRED"] =  (model_df["PLR"] ** 0.173) * (model_df["PT"] ** 0.067) * 15.603
        # compare actual delta-t with modeled normal, and detect anomaly if it falls below model by more than variance
        actual_dt = np.sum(model_df[rtemp_name] - model_df[stemp_name])
        model_dt = np.sum(model_df["DT_PRED"])
        # at this point, status_code must be 200 or an exception would be raised
        # data should always be there, but just to be on the safe side, make an if statement
        response[ "body" ] = f"""{point_name} actual_dt {actual_dt} model_dt {model_dt} for the period {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
    except RequestConnectionError as err:
        response[
            "body"
        ] = f"""{point_name} ConnectionError:
             {err.response.text} {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
    except HTTPError as err:
        response[
            "body"
        ] = f"""{point_name} {err.response.text} 
            for the period {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
        if err.response.status_code == 400:
            try:  # have to try decoding json
                if err.response.json()["error"] == "No data":
                    response[
                        "body"
                    ] = f"""{point_name} has no data 
                        for the period {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
            except ValueError:
                pass
    return response
