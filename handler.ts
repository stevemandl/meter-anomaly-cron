import testTemplate from "./testTemplate";
import axios from "axios";

type AlgorithmCfg = {
  objListPoint: string;
  function: (pointName: string) => Promise<{ error?: string }>;
};

type ObjList = {
  name: string;
  objectList: string[];
}

type ObjListResponse = {
  data: ObjList;
}

const API_KEY: string | undefined = process.env.EMCS_API_KEY;

function emcsURL(point: string){
  return `https://www.emcs.cornell.edu/${point}?api=${API_KEY}&cmd=json`;
}

const algorithms: AlgorithmCfg[] = [
  { objListPoint: "MeterAnomaly.Test.PointList", function: testTemplate },
];

// applyPoints(cfg)
// fetches the objectList from the EMCS API, 
// then returns a list of tasks (promises) that apply the algorithm function to the object points 
async function applyPoints(cfg: AlgorithmCfg) {
  const URL = emcsURL(cfg.objListPoint);
  const {data} = await axios.get<ObjList>(URL);
  return data.objectList.map(cfg.function);
}

// run()
// main entry point for the cron runner
export async function run(event, context, callback) {
  // log the time this was called
  const time = new Date();
  console.log(`Handler ran at ${time}`);
  // create a list of tasks
  const tasks = algorithms.map(applyPoints).flat(2);
  Promise.all(tasks)
    .catch((e) => {console.error(`Task errors ${e.message}`); })
    .then( () => {console.log(`All tasks completed at ${new Date}`); })

}
