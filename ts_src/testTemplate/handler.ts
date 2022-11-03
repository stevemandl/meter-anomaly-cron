// testTemplate/handler.ts
/******* 
  template anomaly detection algorithm:
  Counts the number of trended points in the last 30 days,
  and reports an anomaly if there are more than 10% missing trend values
  assuming hourly (default aggregation) trend readings for the entire period
*******/

import { Algorithm, AlgParams, TrendResponse } from "../types";
import { parseEvent, fetchTrends } from "../tslib/utils";

export const run: Algorithm = async (event) => {
  // default response has empty body
  let response = { statusCode: 200, body: "" };
  const now = new Date();
  console.log(`testTemplate run at ${now.toLocaleString()}`);
  // parse and validate the parameters out of the event
  const params: AlgParams = parseEvent(event);
  // endTime defaults to now, overridden if a timeStamp is passed to the lambda call
  const endTime = params.timeStamp,
    // startTime is 30 days prior for this algorithm
    // 2592000000 = 30 * 24 * 60 * 60 * 1000
    startTime = new Date(endTime.getTime() - 2592000000);
  try {
    // fetch the trends for this pointName in the time range specified
    const trends: TrendResponse = await fetchTrends(
      params.pointName,
      startTime,
      endTime
    );
    if (trends.data) {
      // 720 hours in 30 days
      // 648 is 90% of 720
      if (trends.data[0].datapoints.length < 648) {
        response.body = `missing more than 10% of values for the period ${startTime.toLocaleString()} to ${endTime.toLocaleString()}`;
      }
    }
    return response;
  } catch (error) {
    // datasource returns 400 status when there is no data
    if (
      error.response &&
      error.response.status == 400 &&
      error.response.data &&
      error.response.data.error == "No data"
    ) {
      response.body = `has no data for the period ${startTime.toLocaleString()} to ${endTime.toLocaleString()}`;
      return response;
    }
    response.body = `testTemplate caught error: ${error.message} status code: ${error.response.status}`;
    return response;
  }
};

export default { run };
