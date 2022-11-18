# python_lib/utils_spec.py

from python_lib.utils import parse_event, fetch_trends
from datetime import datetime
from requests.models import Response
import pytest


def test_parse_event():
    event = {"body": {"pointName": "foo"}}
    result = parse_event(event)
    assert "pointName" in result
    assert "timeStamp" in result
    assert "foo" == result.get("pointName")


def test_parse_event_ts_str():
    event = {"body": {"pointName": "ts", "timeStamp": "2022-10-05T23:58:47.390Z"}}
    result = parse_event(event)
    assert "pointName" in result
    assert "timeStamp" in result
    assert "ts" == result.get("pointName")


def test_parse_event_ts_int():
    event = {"body": {"pointName": "ts", "timeStamp": 1666802986}}
    result = parse_event(event)
    assert "pointName" in result
    assert "timeStamp" in result
    assert "ts" == result.get("pointName")


def test_parse_event_ts_bogus():
    event = {"body": {"pointName": "ts", "timeStamp": {}}}
    with pytest.raises(RuntimeError):
        result = parse_event(event)


def test_parse_event_missing_point():
    event = {"body": {}}
    with pytest.raises(RuntimeError):
        result = parse_event(event)


def test_fetch_trends_barf():
    with pytest.raises(TypeError):
        result = fetch_trends("foo", ["bar"])


def test_fetch_trends(mocker):
    r = Response()
    r.status_code = 200
    r._content = b'{ "data": [{ "datapoints": [] }] }'
    mocker.patch("python_lib.utils.requests.post", return_value=r)
    result = fetch_trends("foo", start_time=datetime.now())
    assert "data" in result
