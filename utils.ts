import axios from "axios";
import { AlgParams, TrendArray, TrendResponse } from "./types";

export const PORTAL_API_URL: string | undefined = process.env.PORTAL_API_URL;
const queryUrl = `${PORTAL_API_URL}query`;
const axiosInstance = axios.create({
  baseURL: queryUrl,
  timeout: 3000,
  headers: {
    "Content-Type": "application/json",
  },
});

// parseEvent
// takes an event passed from the API gateway, returns the params that are useful to the algorithm
// this is where the generic pre-processing and validation of the parameters should be done,
// so the algorithms can assume a valid date and a pointName that is a string
export const parseEvent: (event: { body: string }) => AlgParams = (event) => {
  let { pointName, timeStamp } = JSON.parse(event.body);
  if (timeStamp) {
    // make a Date from the timestamp
    timeStamp = new Date(timeStamp);
  } else {
    // default to now
    timeStamp = new Date();
  }
  if (isNaN(timeStamp.valueOf())) {
    // the algorithms can't work with invalid dates
    throw new Error("Invalid timeStamp");
  }
  return { pointName, timeStamp };
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
  const response = await axiosInstance.request<TrendArray>({
    data: requestData,
    method: "post",
  });
  if (response && response.data) {
    trendResponse.data = response.data;
  }
  return trendResponse;
};
