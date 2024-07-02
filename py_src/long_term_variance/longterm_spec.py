from python_template.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json

# }
five_months_old = open('long_term_reading_variance/Testcases/five_months_old.json')
"""
five_months_old.json is a file containing the swagger JSON response from the following query 
{
  "range": {
    "from": "2019-04-01T19:38:47.334Z",
    "to": "2019-04-30T19:38:47.334Z"
  },
  "interval": "30s",
  "intervalMs": 5500,
  "maxDataPoints": 50,
  "targets": [
    {
      "target": "BakerLab.Elec.South.PowerScout3/kW_System"
    }
  ]
}
"""
five_months_new = open('long_term_reading_variance/Testcases/five_months_new.json')
"""
five_months_new.json is a file containing the swagger JSON response from the following query 
{
  "range": {
    "from": "2020-04-01T19:38:47.334Z",
    "to": "2020-04-30T19:38:47.334Z"
  },
  "interval": "30s",
  "intervalMs": 5500,
  "maxDataPoints": 50,
  "targets": [
    {
      "target": "BakerLab.Elec.South.PowerScout3/kW_System"
    }
  ]
}
"""

one_month_old = open('long_term_reading_variance/Testcases/one_month_old.json')
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

one_month_new = open('long_term_reading_variance/Testcases/one_month_new.json')
"""
one_month_old.json is a file containing the swagger JSON response from the following query 
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

def test_onetime(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    #data1 contains the data from the previous year 
    #data2 contains the data from the target year
    data1 = json.load(five_months_old)
    data2 = [{"datapoints": []}]
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect = [data1, data2]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "missing timeframe" == result.get("body")
    
def test_five_months(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    #data1 contains the data from the previous year 
    #data2 contains the data from the target year
    data1 = json.load(five_months_old)
    data2 = json.load(five_months_new)
    
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect = [data1, data2]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "anomaly detected" == result.get("body")
    
def test_one_month(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    #data1 contains the data from the previous year 
    #data2 contains the data from the target year
    
    data1 = json.load(one_month_old)
    data2 = json.load(one_month_new)
    
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect = [data1, data2]
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "anomaly detected" == result.get("body")
