# python_lib/utils_spec.py

from pandas.api import types
from datetime import datetime
from requests.models import Response
import pytest
from python_lib.utils import parse_event, fetch_trends, build_index, build_df


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

def test_build_index():
    empty_trends = [{ "target": "A", "datapoints": [] }]
    empty_idx = build_index(empty_trends)
    assert not empty_idx
    single_trends = [{ "target": "A", "datapoints": [[ 1.5, 1000 ], [3.5, 1600 ]] }]
    single_idx = build_index(single_trends)
    assert "A" in single_idx
    assert single_idx["A"][1000] == 1.5
    multi_trends = [{ "target": "A", "datapoints": [[ 1.5, 5000 ], [3.5, 5600 ]] },{ "target": "B", "datapoints": [[ 2.5, 2000 ], [4.5, 2600 ]] }]
    multi_idx = build_index(multi_trends)
    assert "A" in multi_idx and "B" in multi_idx
    assert multi_idx["A"][5000] == 1.5
    assert multi_idx["B"][2600] == 4.5

def test_build_df():
    empty_trends = [{ "target": "A", "datapoints": [] }]
    empty_df = build_df(empty_trends)
    assert empty_df.empty
    multi_trends = [{ "target": "A", "datapoints": [[ 1.5, 3600000 ], [3.5, 7200000 ]] },{ "target": "B", "datapoints": [[ 2.5, 3600000 ], [4.5, 3660000 ]] }]
    multi_df = build_df(multi_trends)
    assert multi_df.iloc[1,0] == 2.5
    assert multi_df.iloc[2,1] == 4.5
    assert types.is_datetime64_any_dtype(multi_df.index)