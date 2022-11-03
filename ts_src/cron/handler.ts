// handler.ts
import axios from "axios";
import { Lambda, SNS } from "aws-sdk";
import Redis from "ioredis";
import { AlgorithmCfg, ObjList } from "../types";


const API_KEY: string | undefined = process.env.EMCS_API_KEY;
const SECRET_TOKEN: string | undefined = process.env.SECRET_TOKEN;
const FUNCTION_BASE: string | undefined = process.env.FUNCTION_BASE;

// when running offline, use the localhost endpoint
const lambda = new Lambda({
    apiVersion: "2015-03-31",
    endpoint: process.env.IS_OFFLINE
        ? "http://localhost:3002"
        : "https://lambda.us-east-1.amazonaws.com",
});

// forms the URL for the EMCS API that returns the json representation of an object
function emcsURL(point: string) {
    return `https://www.emcs.cornell.edu/${point}?api=${API_KEY}&cmd=json`;
}

// the configuration of the various algorithms with the objListPoint containing the list of meters for this algorithm,
// and the fn name indicating the path relative to the base URL for the lambda functions
// TODO: store this externally
const algorithms: AlgorithmCfg[] = [
    { objListPoint: "MeterAnomaly.testTemplateHandler.PointList", fn: "testTemplateHandler" },
    { objListPoint: "MeterAnomaly.pythonTemplate.PointList", fn: "pythonTemplate" },
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

// invokeLambda()
// invoke lambda function
export async function invokeLambda(uri: string, pointName: string) {
    const params: Lambda.InvocationRequest = {
        FunctionName: `${FUNCTION_BASE}${uri}`,
        InvocationType: "RequestResponse",
        Payload: JSON.stringify({ body: { pointName } }),
    };
    try {
        const response: Lambda.InvocationResponse = await lambda
            .invoke(params)
            .promise();
        const responseBody = JSON.parse("" + response.Payload?.toString());
        return responseBody.body;
    } catch (error) {
        return `AWS error invoking lambda: ${error.message}`;
    }
}

// run()
// main entry point for the cron runner
export async function run(event, context) {
    // log the time this was called
    const time = new Date();
    console.log(`Handler ran at ${time}`);
    const redis = new Redis({
        port: 6379,
        host: "redis.emcs.cucloud.net",
        username: "cn",
        password: "cfYRp36reQ9dNqOMmZ4Laj0w",
        db: 0,
      });
    
    // create a (flattened) list of invokeLambda parameters for all of the configured algorithms
    const lambdaParams = (
        await Promise.all(
            algorithms.map(async (cfg: AlgorithmCfg) => {
                const objectList: string[] = await fetchPoints(cfg);
                return objectList.map((point) => ({
                    uri: cfg.fn,
                    pointName: point,
                }));
            })
        )
    ).flat(2);
    // collect the results from all of the async lambda calls
    const results = await Promise.allSettled(
        lambdaParams.map(async (param) => {
            const lambdaResult = await invokeLambda(param.uri, param.pointName);
            const invokeKey = `${param.uri}:${param.pointName}`;
            if (lambdaResult){
                // update elasicache state if necessary; remember when the anomaly was first detected
                if (await redis.hsetnx("meter-anomalies", invokeKey, time.getTime())){
                    // prepend the function name to the results to be consistent
                    return `${invokeKey} ${lambdaResult}`;
                }
            }
            else{
                // clear anomaly
                await redis.hdel("meter-anomalies", invokeKey);
            }
            await redis.quit();
            return null;
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
        .sort()
        .join("\n");
        // make this pretty and deliver it to an e-mail list using SNS:
        // Create publish parameters
        var params = {
          Message: `Meter Anomaly Report for ${time.toLocaleString()}:\n${report}`, /* required */
          TopicArn: 'arn:aws:sns:us-east-1:498547149247:emcs-meter-anomalies'
        };
        // create SNS service object
        const sns = new SNS({apiVersion: '2010-03-31'});
        // Await promise
        var publishText = await sns.publish(params).promise();
        // Handle promise's fulfilled/rejected states
        console.log("Report MessageID is " + publishText.MessageId);
}
