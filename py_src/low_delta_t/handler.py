"""
low_delta_t/handler.py
"""

from datetime import timedelta
import numpy as np
from requests.exceptions import ConnectionError as RequestConnectionError, HTTPError
from python_lib.utils import parse_event, fetch_trends, build_index, build_df, AnomalyError, MeterAnomaly, now

# the minimum acceptable length of the datapoints array
MIN_DATAPOINTS_LENGTH = int(7 * 24)
RECENT_DAYS = 2
ALGORITHM = "low_delta_t"
ANOMALY_THRESHOLD = 0.6

def run(event, _context):
    """
    handler.run - the lambda function entry point
    """
    # start out with blank payload
    payload = {}
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    print(f"{ALGORITHM} run with params {params}")

    end_time = params.get("timeStamp")
    year_ago = end_time - timedelta(365)
    start_time = end_time - timedelta(RECENT_DAYS)
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
            point=point_name, start_time=year_ago, end_time=end_time, additional= ["aggH"]
        ))
        # fetch recent period STEMP, RTEMP, FLOW, TONS, OAT
        recent_points = (stemp_name, rtemp_name, flow_name, tons_name, oat_name)
        recent = fetch_trends(points=recent_points,start_time=start_time, end_time=end_time)

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
        weighted_actual_dt = None
        weighted_model_dt = None
        model_dt = np.mean(model_df["DT_PRED"])
        if np.sum(model_df[flow_name]) > 0:
            weighted_actual_dt = np.average(model_df[rtemp_name] - model_df[stemp_name], weights=model_df[flow_name])
            weighted_model_dt = np.average(model_df["DT_PRED"], weights=model_df[flow_name])
        if actual_dt < model_dt * ANOMALY_THRESHOLD:
            actual_pct = actual_dt / model_dt
            desc = f"DeltaT/ModelDT below expectations {actual_dt:.2f}/{model_dt:.2f} weighted: {weighted_actual_dt:.2f}/{weighted_model_dt:.2f}"
            payload = MeterAnomaly(point_name, ALGORITHM, now().isoformat(), desc, actual_pct, ANOMALY_THRESHOLD, start_time.isoformat(), end_time.isoformat())
    except RequestConnectionError as err:
        payload["error"] = err.response.text
    except AnomalyError as err:
        desc = f"Error: {err}"
        payload = MeterAnomaly(point_name, ALGORITHM, now().isoformat(), desc, start_ts=start_time.isoformat(), end_ts=end_time.isoformat())
         
    except HTTPError as err:
        payload["error"] = err.response.text
        if err.response.status_code == 400:
            try:  # have to try decoding json
                if err.response.json()["error"] == "No data":
                    payload = MeterAnomaly(
                        point_name,
                        ALGORITHM,
                        now().isoformat(),
                        "No data for the period.",
                        0,
                        MIN_DATAPOINTS_LENGTH,
                        start_time.isoformat(),
                        end_time.isoformat(),
                    )
            except ValueError:
                pass
    return payload