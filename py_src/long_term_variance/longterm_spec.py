from python_template.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json


anom_3 = open('long_term_reading_variance/test_cases/one_month_oldest.json')
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
anom_2 = open('long_term_reading_variance/test_cases/one_month_old.json')
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

anom_1 = open('long_term_reading_variance/test_cases/one_month_new.json')
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
noanom_3 = open('long_term_reading_variance/test_cases/noanom_oldest.json')
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
noanom_2 = open('long_term_reading_variance/test_cases/noanom_old.json')
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
noanom_1 = open('long_term_reading_variance/test_cases/noanom_new.json')
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



def test_onetime(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    #data_current contains the current data from when the algorithm was executed
    #data1 contains the data from the previous year
    #data2 contains the data from two years prior
    data_current = json.load(noanom_1)
    data1 = [{"datapoints": []}]
    data2 = json.load(noanom_3)
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect = [data_current, data1, data2]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "missing timeframe" == result.get("body")
    
def test_anom(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    #data_current contains the current data from when the algorithm was executed
    #data1 contains the data from the previous year
    #data2 contains the data from two years prior
    
    data_current = json.load(anom_1)
    data1 = json.load(anom_2)
    data2 = json.load(anom_3)
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect = [data_current, data1, data2]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "anomaly detected" == result.get("body")
    
def test_noanom(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    #data_current contains the current data from when the algorithm was executed
    #data1 contains the data from the previous year
    #data2 contains the data from two years prior
    data_current = json.load(noanom_1)
    data1 = json.load(noanom_2)
    data2 = json.load(noanom_3)
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect = [data_current, data1, data2]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body") 
