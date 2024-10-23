"""
low_delta_t/handler.py
"""

from datetime import timedelta
import numpy as np
from requests.exceptions import ConnectionError as RequestConnectionError, HTTPError
from python_lib.utils import parse_event, fetch_trends, build_index, build_df, AnomalyError

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
    device_name = point_name[:-4]
    if point_name.endswith("TONS"):
        stemp_name = f"{device_name}STEMP"
        rtemp_name = f"{device_name}RTEMP"
        flow_name = f"{device_name}FLOW"
    elif point_name.endswith("Tons"):
        stemp_name = f"{device_name}STemp"
        rtemp_name = f"{device_name}RTemp"
        flow_name = f"{device_name}Flow"
    else:
        raise(AnomalyError(f"{point_name} does not end with TONS"))
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
        if any(x not in model_df for x in recent_points):
            raise(AnomalyError(f"Missing trends from {recent_points}"))
        # model partial load ratio for the recent period from all fetched data
        model_df["PLR"] = model_df[tons_name] / max_tons
        # model partial temperature ratio
        model_df["PT"] = (model_df[oat_name] - model_df[stemp_name]) / 41
        # DTpred = PLR^0.173 * PT^0.067 * 15.603
        model_df["DT_PRED"] =  (model_df["PLR"] ** 0.173) * (model_df["PT"] ** 0.067) * 15.603
        # compare actual delta-t with modeled normal, and detect anomaly if it falls below model by more than variance
        actual_dt = np.mean(model_df[rtemp_name] - model_df[stemp_name])
        weighted_actual_dt = np.average(model_df[rtemp_name] - model_df[stemp_name], weights=model_df[flow_name])
        model_dt = np.mean(model_df["DT_PRED"])
        weighted_model_dt = np.average(model_df["DT_PRED"], weights=model_df[flow_name])
        if actual_dt < model_dt * 0.9:
            actual_pct = actual_dt / model_dt
            response[ "body" ] = f"""{point_name} actual_pct {actual_pct:.2%} {actual_dt:.2f}/{model_dt:.2f} weighted {weighted_actual_dt:.2f}/{weighted_model_dt:.2f} for the period {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
    except RequestConnectionError as err:
        response[
            "body"
        ] = f"""{point_name} ConnectionError:
             {err.response.text} {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
    except AnomalyError as err:
        response[
            "body"
        ] = f"""{point_name} Error: {err} {start_time:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M}"""
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
