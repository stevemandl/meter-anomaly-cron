import axios from "axios";
import { AlgParams, TrendArray, TrendResponse } from "../types";

export const PORTAL_API_URL: string | undefined = process.env.PORTAL_API_URL;
const queryUrl = `${PORTAL_API_URL}query`;

// parseEvent
// takes an event passed to the lambda function, returns the params that are useful to the algorithm
// this is where the generic pre-processing and validation of the parameters should be done,
// so the algorithms can assume a valid date and a pointName that is a string
export const parseEvent: (event: { body: string | object }) => AlgParams = (
  event
) => {
  var body;
  if (typeof event.body == "string") {
    body = JSON.parse(event.body);
  } else if (typeof event.body == "object") {
    body = event.body;
  }
  if (body.timeStamp) {
    // make a Date from the timestamp
    body.timeStamp = new Date(body.timeStamp);
  } else {
    // default to now
    body.timeStamp = new Date();
  }
  if (isNaN(body.timeStamp.valueOf())) {
    // the algorithms can't work with invalid dates
    throw new Error("Invalid timeStamp");
  }
  return body;
};

// fetchTrends
// gets trends from the portal trend API
export const fetchTrends: (
  pointNameOrNames: string[] | string,
  startTime: Date,
  endTime?: Date
) => Promise<TrendResponse> = async (
  pointNameOrNames: string[] | string, // accepts a single pointName or an array
  startTime: Date, // required startTime
  endTime: Date = new Date() // optional endTime, defaults to now
) => {
  const empty: string[] = [],
    pointNames = empty.concat(pointNameOrNames), // ensure parameter is array
    // the query request
    requestData = {
      range: { from: startTime.toISOString(), to: endTime.toISOString() },
      targets: pointNames.map((point) => ({
        target: point,
        payload: { additional: [] },
        type: "timeseries",
      })),
    };
  let trendResponse: TrendResponse = {};
  // await the raw response
  console.log(`posting to ${queryUrl} with ${JSON.stringify(requestData)}`)
  const response = await axios.post<TrendArray>(queryUrl, requestData, {
    timeout: 3000,
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (response && response.data) {
    trendResponse.data = response.data;
  }
  return trendResponse;
};
