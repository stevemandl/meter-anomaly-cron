from long_term_variance.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json


anom_3 = open('long_term_variance/test_cases/one_month_oldest.json')
"""
one_month_oldest.json is a file containing the swagger JSON response from the following query 
{
  "range": {
    "from": "2019-8-19",
    "to": "2019-9-18"
  },
  "targets": [
    {
      "target": "CarpenterHall.CW.FP/TONS"
    }
  ]
}
"""
anom_2 = open('long_term_variance/test_cases/one_month_old.json')
"""
one_month_old.json is a file containing the swagger JSON response from the following query 
{
  "range": {
    "from": "2020-8-19",
    "to": "2020-9-18"
  },
  "targets": [
    {
      "target": "CarpenterHall.CW.FP/TONS"
    }
  ]
}
"""

anom_1 = open('long_term_variance/test_cases/one_month_new.json')
"""
one_month_new.json is a file containing the swagger JSON response from the following query 
{
  "range": {
    "from": "2021-8-19",
    "to": "2021-9-18"
  },
  "targets": [
    {
      "target": "CarpenterHall.CW.FP/TONS"
    }
  ]
}
"""
noanom_3 = open('long_term_variance/test_cases/noanom_oldest.json')
"""
noanom_oldest.json is a file containing the swagger JSON response from the following query 
{
   "range": {
     "from": "2021-07-01",
     "to": "2021-07-30"
   },
   "targets": [
     {
       "target": "BartonHall.CW.FP/TONS"
     }
   ]
}
"""
noanom_2 = open('long_term_variance/test_cases/noanom_old.json')
"""
noanom_old.json is a file containing the swagger JSON response from the following query 
{
   "range": {
     "from": "2022-07-01",
     "to": "2022-07-30"
   },
   "targets": [
     {
       "target": "BartonHall.CW.FP/TONS"
     }
   ]
}
"""
noanom_1 = open('long_term_variance/test_cases/noanom_new.json')
"""
noanom_new.json is a file containing the swagger JSON response from the following query 
{
   "range": {
     "from": "2023-07-01",
     "to": "2023-07-30"
   },
   "targets": [
     {
       "target": "BartonHall.CW.FP/TONS"
     }
   ]
}
"""

data_noanom_1 = json.load(noanom_1)
data_noanom_2 = json.load(noanom_2)
data_noanom_3 = json.load(noanom_3)
data_anom_1 = json.load(anom_1)
data_anom_2 = json.load(anom_2)
data_anom_3 = json.load(anom_3)


def test_onetime(mocker):
    event = {
        "body": {
            "pointName": "BartonHall.CW.FP/TONS",
            "timeStamp": "2023-07-30",
        }
    }
    #data_current contains the current data from when the algorithm was executed
    #data1 contains the data from the previous year
    #data2 contains the data from two years prior
    data1 = [{"datapoints": []}]
    mocker.patch(
        "long_term_variance.handler.fetch_trends",
        side_effect = [data_noanom_1, data1, data_noanom_3]
    )
    result = run(event, None)
    assert "statusCode" in result
    # if not enough data is present to be conclusive, 
    # we expect the algorithm to return no anomaly
    assert "" == result.get("body")
    
def test_anom(mocker):
    event = {
        "body": {
            "pointName": "CarpenterHall.CW.FP/TONS",
            "timeStamp": "2021-9-18",
        }
    }
    #data_current contains the current data from when the algorithm was executed
    #data1 contains the data from the previous year
    #data2 contains the data from two years prior
    
    mocker.patch(
        "long_term_variance.handler.fetch_trends",
        side_effect = [data_anom_1, data_anom_2, data_anom_3]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "Anomaly Detected" in result.get("body")
    
def test_noanom(mocker):
    event = {
        "body": {
            "pointName": "BartonHall.CW.FP/TONS",
            "timeStamp": "2023-07-30",
        }
    }
    #data_current contains the current data from when the algorithm was executed
    #data1 contains the data from the previous year
    #data2 contains the data from two years prior
    mocker.patch(
        "long_term_variance.handler.fetch_trends",
        side_effect = [data_noanom_1, data_noanom_2, data_noanom_3]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body") 
