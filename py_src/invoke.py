#!/usr/bin/env python
"""
invoke.py
script to invoke a python meter-anomaly algorithm
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import re
import importlib
import time

FN_RE = r"(?P<pkg>\w+)/(?P<subpkg>\w+)\.(?P<fn>\w+)"

if __name__ == "__main__":
    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "function",
        type=str,
        help="function name, (e.g. python_template/handler.run)",
    )

    parser.add_argument(
        "pointName",
        type=str,
        help="pointName (e.g. BakerLab.STM.Flow)",
    )

    parser.add_argument(
        "-t",
        "--timeStamp",
        type=str,
        help="timeStamp (e.g. 'Jan 5, 2022' or 1676005200)",
    )

    args = parser.parse_args()
    print(
        f"\ninvoke.py arguments:\n    function: {args.function}, pointName: {args.pointName}, timeStamp: {args.timeStamp} "
    )
    event = {"body": {"pointName": args.pointName}}
    if args.timeStamp is not None:
        event["body"]["timeStamp"] = args.timeStamp
    m = re.search(FN_RE, args.function)
    assert m

    pkg = importlib.import_module(f"{m.group('pkg')}.{m.group('subpkg')}")
    fn = getattr(pkg, m.group("fn"))
    print(f"Calling function ...")
    start = time.time()
    result = fn(event, None)
    end = time.time()
    print(f"Received response: '{result}'")
    if result["statusCode"] == 200:
        print("Algorithm executed without an error")
    if result["body"]:
        print(f"ANOMALY DETECTED: {result['body']}")
    else:
        print("No anomaly was detected")
    print(f"Function elapsed run time (seconds): '{end-start:.3}'.\n")
