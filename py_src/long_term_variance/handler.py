"""
long_term_variance/handler.py
"""

from datetime import timedelta
import numpy as np
import pandas as pd
from requests.exceptions import ConnectionError as RequestConnectionError, HTTPError
from python_lib.utils import parse_event, fetch_trends, build_index, build_df, AnomalyError

# the window size we are analyzing. The assumption is the consumption is 
# normally similar across this period and for the same period one year prior 
RECENT_DAYS = 7
# the minimum acceptable length of the datapoints array
MIN_DATAPOINTS_LENGTH = int(RECENT_DAYS * 24 * 0.6)
# if the magnitude of the z score is greater than this, it's anomolous
Z_SCORE_THRESHOLD = 3.0
ANOMALY_PORTION = 0.5

def run(event, _context):
    """
    handler.run - the lambda function entry point
    """


    # start out with blank response
    response = {"statusCode": 200, "body": ""}
    # parse event and ensure timeStamp and pointName are present
    params = parse_event(event)
    print(f"long_term_variance run with params {params}")

    now = params.get("timeStamp")
    year_ago = now - timedelta(365)
    two_years_ago = now - timedelta(365*2)
    start_time = now - timedelta(RECENT_DAYS)
    one_year_st = year_ago - timedelta(RECENT_DAYS)
    two_year_st = two_years_ago - timedelta(RECENT_DAYS)
    point_name = params.get("pointName")
    try:
        # read recent data, prior year, and prior 2 year
        # fetch recent 
        df = build_df(fetch_trends(
            point=point_name, start_time=start_time, end_time=now ))
        year1 = fetch_trends(
            point=point_name, start_time=one_year_st, end_time=year_ago )
        year2 = fetch_trends(
            point=point_name, start_time=two_year_st, end_time=two_years_ago )
        a = np.array(year1[0]["datapoints"] + year2[0]["datapoints"])
        if (a.size < MIN_DATAPOINTS_LENGTH*2) or (df.size < MIN_DATAPOINTS_LENGTH):
            # not enough data to determine anomaly
            return response
        t_df = pd.DataFrame.from_records(a, columns = ("previous", "ts"), index="ts")
        t_df.index = pd.to_datetime(t_df.index, unit='ms'
        )
        df = df.merge(t_df, how="outer", on="ts").interpolate()
        # add column to separate time of day into 8 bins
        df["hour"] = df.index.hour
        # 8 three-hour bins to aggregate the data
        hourbins = np.array(range(0,24,3))
        df["hourbin"] = np.digitize(df["hour"], bins= hourbins)
        # compute mean and std of prior, compute z score for recent
        result = df.groupby(["hourbin"], as_index=False).agg({"previous": ["mean", "std"], point_name: ["mean"]})
        result.columns=['bin','prev_mean','prev_std','curr_mean']
        result["z"]=(result["curr_mean"] - result["prev_mean"])/result["prev_std"]
        print(result)
        anomoly_count = result.loc[lambda x: np.abs(x["z"]) > Z_SCORE_THRESHOLD]["z"].size
        # return anomaly if magnitude of z score is greater than threshold
        if anomoly_count > (hourbins.size * ANOMALY_PORTION):
            raise(AnomalyError(f"z score over {Z_SCORE_THRESHOLD} for more than {ANOMALY_PORTION:.0%} over past {RECENT_DAYS} relative to past 2 years"))
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
