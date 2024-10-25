from python_template.handler import run
from requests.exceptions import HTTPError
from requests.models import Response
import json

# See swagger docs at https://app.swaggerhub.com/apis/Cornell-BACSI/EMCS-portal/1.0.0

# actual_testcase.json contains the response from the following JSON request body:
"""
 {
   "range": {
     "from": "2023-07-01T19:38:47.334Z",
     "to": "2023-07-30T19:38:47.334Z"
   },
   "interval": "30s",
   "intervalMs": 5500,
   "maxDataPoints": 50,
   "targets": [
     {
       "target": "DayHall.Elec.PowerScout3/kWsystem"
     }
   ]
 }
"""
actual_testcase = open('python_template/test_cases/actual_testcase.json')

# noanomaly_testcase.json contains the response from the following JSON request body:
""" {
   "panelId": "Q-1599986187842-0.164611811105138-0",
   "range": {
     "from": "2021-03-01T19:38:47.334Z",
     "to": "2021-03-30T19:38:47.334Z"
   },
   "interval": "30s",
   "intervalMs": 5500,
   "maxDataPoints": 50,
   "targets": [
     {
       "target": "StatlerHotel.Elec.PowerScout3/kWsystem"
     }
   ],
   "group": "string",
   "from": "2021-10-20T19:38:47.334Z",
   "to": "2021-10-21T19:38:47.334Z"
 }
"""
noanomaly_testcase = open('python_template/test_cases/noanomaly_testcase.json')

def test_nobarf(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value= [{"datapoints": []}],
    )
    
    result = run(event, None)
    assert "point" in result
    assert "description" in result
    assert "Missing more than 10%" in result["description"]



def test_handle400(mocker):
    r = Response()
    r.status_code = 400
    r._content = b'{"error":"No data"}'
    mocker.patch(
        "python_template.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "No data" in result["description"]
    

def test_barf(mocker):
    r = Response()
    r.status_code = 400
    r._content = b"qwerty"
    mocker.patch(
        "python_template.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "qwerty" in result["error"]



def test_actual(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
   
    data = json.load(actual_testcase)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value= data,
    )
    result = run(event, None)
    assert "Missing more than 10%" in result["description"]

def test_noanomly(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(noanomaly_testcase)
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert not result
