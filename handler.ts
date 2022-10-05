// handler.ts
import axios from "axios";

import testTemplate from "./testTemplate";
import { AlgorithmCfg, ObjList } from "./types";

const API_KEY: string | undefined = process.env.EMCS_API_KEY;
const SECRET_TOKEN: string | undefined = process.env.SECRET_TOKEN;

function emcsURL(point: string) {
  return `https://www.emcs.cornell.edu/${point}?api=${API_KEY}&cmd=json`;
}

const algorithms: AlgorithmCfg[] = [
  { objListPoint: "MeterAnomaly.Test.PointList", fn: testTemplate },
];

// applyPoints(cfg)
// fetches the objectList from the EMCS API,
// then returns a list of tasks (promises) that apply the algorithm function to the object points
export async function fetchPoints(cfg: AlgorithmCfg) {
  const URL = emcsURL(cfg.objListPoint);
  const { data } = await axios.get<ObjList>(URL);
  return data.objectList;
}

// auth()
// simple authorizer
export async function auth(event) {
  const isAuthorized = event.headers.authorization === SECRET_TOKEN;
  return { isAuthorized };
}

// run()
// main entry point for the cron runner
export async function run(event, context, callback) {
  // log the time this was called
  const time = new Date();
  console.log(`Handler ran at ${time}`);
  // create a list of tasks for all of the configured algorithms
  const tasks = algorithms
    .map(async (cfg: AlgorithmCfg) => {
      const objectList = await fetchPoints(cfg);
      return objectList.map((point) => cfg.fn(point));
    })
    .flat(2);
  Promise.allSettled(tasks).then((values) => {
    console.log(`All tasks completed at ${new Date()}`);
    console.log(`Values: ${JSON.stringify(values)}`);
  });
}
