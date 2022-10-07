// handler.ts
import axios, { AxiosRequestConfig } from "axios";
import { AlgorithmCfg, ObjList } from "./types";

const API_KEY: string | undefined = process.env.EMCS_API_KEY;
const SECRET_TOKEN: string | undefined = process.env.SECRET_TOKEN;
const FUNCTION_BASE_URL: string | undefined = process.env.FUNCTION_BASE_URL;

// forms the URL for the EMCS API that returns the json representation of an object
function emcsURL(point: string) {
  return `https://www.emcs.cornell.edu/${point}?api=${API_KEY}&cmd=json`;
}

// the configuration of the various algorithms with the objListPoint containing the list of meters for this algorithm,
// and the fn name indicating the path relative to the base URL for the lambda functions
const algorithms: AlgorithmCfg[] = [
  { objListPoint: "MeterAnomaly.Test.PointList", fn: "testTemplate" },
];

// fetchPoints(cfg)
// fetches the objectList from the EMCS API,
// returns a list of point names for the Algorithm
export async function fetchPoints(cfg: AlgorithmCfg): Promise<string[]> {
  const URL = emcsURL(cfg.objListPoint);
  const { data } = await axios.get<ObjList>(URL);
  // EMCS API responses are text/plain ,so we need to manually
  // convert single quotes to double, then parse
  const objArray: string[] = JSON.parse(data.objectList.replace(/'/g, '"'));
  return objArray;
}

// auth()
// simple authorizer checks if the x-api-key header matches the SECRET_TOKEN
export async function auth(event) {
  const isAuthorized = event.headers.authorization === SECRET_TOKEN;
  return { isAuthorized };
}

// invokeLambda()
// invoke lambda function
export async function invokeLambda(uri: string, pointName: string) {
  //TODO: rewrite to invoke lambda using AWS SDK
  console.log(`invokeLambda uri: ${uri} point: ${pointName}`);
  const cfg: AxiosRequestConfig = {
    data: { pointName },
    url: `${FUNCTION_BASE_URL}${uri}`,
    timeout: 30000,
    headers: {
      "Content-Type": "application/json",
      "x-api-key": SECRET_TOKEN,
    },
    method: "post",
  };
  try {
    let response = await axios.request<string>(cfg);
    return response.data;
  } catch (error) {
    return `axios error invoking lambda: ${error.message}`;
  }
}

// run()
// main entry point for the cron runner
export async function run(event, context) {
  // log the time this was called
  const time = new Date();
  console.log(`Handler ran at ${time}`);
  // create a (flattened) list of invokeLambda parameters for all of the configured algorithms
  const lambdaParams = (
    await Promise.all(
      algorithms.map(async (cfg: AlgorithmCfg) => {
        const objectList: string[] = await fetchPoints(cfg);
        return objectList.map((point) => ({ uri: cfg.fn, pointName: point }));
      })
    )
  ).flat(2);
  // collect the results from all of the async lambda calls
  const results = await Promise.allSettled(
    lambdaParams.map(async (param) => {
      const lambdaResult = await invokeLambda(param.uri, param.pointName);
      // prepend the function name to the results to be consistent
      return lambdaResult ? `${param.uri}: ${lambdaResult}` : null;
    })
  );
  //make the report
  const report = results
    .filter((r) => r.status != "fulfilled" || r.value) // only results with errors or responses
    .map((r) => {
      // get the value or the reason
      if (r.status == "fulfilled") {
        return r.value;
      } else {
        // rejected
        return r.reason;
      }
    })
    .join("\n");
  console.log(`Report:\n ${report}`);
}
