"""
 stuck_two_day_spec.py
"""
import json
from requests.exceptions import HTTPError
from requests.models import Response
from stuck_two_day.handler import run
# See swagger docs at https://app.swaggerhub.com/apis/Cornell-BACSI/EMCS-portal/1.0.0

# stuck.json contains the response from the following JSON request body:
"""
{
   "range": {
     "from": "2024-06-02",
     "to": "2024-06-09"
   },
   "targets": [
     {
       "target": "AnnaComstockHouse.STM.M22-V/AverageMassFlow"
     }
   ]
 }
"""
stuck_value_testcase = open('stuck_two_day/test_cases/stuck.json')

# not_stuck.json contains the response from the following JSON request body:
""" 
{
   "range": {
     "from": "2022-03-01",
     "to": "2022-03-08"
   },
   "targets": [
     {
       "target": "UrisHall.Elec.480v.PowerScout3037/kW_System"
     }
   ]
}
"""
noanomaly_testcase = open('stuck_two_day/test_cases/not_stuck.json')

def test_nobarf(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    mocker.patch(
        "stuck_two_day.handler.fetch_trends",
        return_value= [{"datapoints": []}],
    )
    
    result = run(event, None)
    assert "statusCode" in result
    # this algorithm is not checking for missing data; only stuck data
    # so an empty dataset is not detected as a stuck anomaly
    assert not result.get("body")


def test_handle400(mocker):
    r = Response()
    r.status_code = 400
    r._content = b'{"error":"No data"}'
    mocker.patch(
        "stuck_two_day.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "no data" in result.get("body")


def test_barf(mocker):
    r = Response()
    r.status_code = 400
    r._content = b"qwerty"
    mocker.patch(
        "stuck_two_day.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "qwerty" in result.get("body")

def test_noanomly(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(noanomaly_testcase)
    mocker.patch(
        "stuck_two_day.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "" == result.get("body")

def test_stuck_value(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    data = json.load(stuck_value_testcase)
    mocker.patch(
        "stuck_two_day.handler.fetch_trends",
        return_value = data,
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "stuck at value" in result.get("body")
    
