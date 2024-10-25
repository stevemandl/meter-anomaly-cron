// handler.ts
import axios from "axios";
import { Lambda, SNS } from "aws-sdk";
import * as db from "../tslib/anomalyDB"

const API_KEY: string | undefined = process.env.EMCS_API_KEY;
const SECRET_TOKEN: string | undefined = process.env.SECRET_TOKEN;
const SAM_STAGE: string | undefined = process.env.SAM_STAGE;
const REPORT_URL: string = "https://portal.emcs.cornell.edu/d/broken_meter_ticket_report/broken-meter-ticket-report";


// when running offline, use the localhost endpoint
let endpoint = "https://lambda.us-east-1.amazonaws.com",
    sslEnabled = true;
if (process.env.IS_OFFLINE) {
    endpoint = "http://localhost:3001";
    sslEnabled = false;
}
const lambda = new Lambda({
    apiVersion: "2015-03-31",
    endpoint,
    sslEnabled
});
const sns = new SNS({ apiVersion: "2010-03-31", endpoint, sslEnabled });

// forms the URL for the EMCS API that returns the json representation of an object
function emcsURL(point: string) {
    return `https://www.emcs.cornell.edu/${point}?api=${API_KEY}&cmd=json`;
}

// the configuration of the various algorithms with the objListPoint containing the list of meters for this algorithm,
// and the fn name indicating the path relative to the base URL for the lambda functions
// TODO: store this externally
const algorithms: AlgorithmCfg[] = [
    {
        objListPoint: "MeterAnomaly.longTermVariance.PointList",
        fn: "longTermVariance",
        service: "meter-anomaly-py",
    },
    {
        objListPoint: "MeterAnomaly.LowDeltaT.PointList",
        fn: "lowDeltaT",
        service: "meter-anomaly-py",
    },
    {
        objListPoint: "MeterAnomaly.sparseData.PointList",
        fn: "sparseData",
        service: "meter-anomaly-py",
    },
    {
        objListPoint: "MeterAnomaly.stuckTwoDay.PointList",
        fn: "stuckTwoDay",
        service: "meter-anomaly-py",
    },
];

// fetchPoints(cfg)
// fetches the objectList from the EMCS API,
// returns a list of point names for the Algorithm
export async function fetchPoints(cfg: AlgorithmCfg): Promise<string[]> {
    const URL = emcsURL(cfg.objListPoint);
    try{
        const { data } = await axios.get<ObjList>(URL)
        // EMCS API responses are text/plain ,so we need to manually
        // convert single quotes to double, then parse
        console.log(`EMCS url ${URL} returned object list: ${data.objectList}`);
        if (data.objectList){
            const objArray: string[] = JSON.parse(data.objectList.replace(/'/g, '"'));
            return objArray;
        }
    }
    catch(err) {
        console.error(`Error fetching ${URL}: ${err.message}`);
    }
    return [];
}

// invokeLambda()
// invoke lambda function
export async function invokeLambda(
    service: string,
    uri: string,
    pointName: string
) {
    const params: Lambda.InvocationRequest = {
        FunctionName: `${service}-${SAM_STAGE}-${uri}`,
        InvocationType: "RequestResponse",
        Payload: JSON.stringify({ body: { pointName } }),
    };
    try {
        const response: Lambda.InvocationResponse = await lambda
            .invoke(params)
            .promise();
        console.log("got response ", JSON.stringify(response))
        const responseBody = JSON.parse("" + response.Payload?.toString());
        console.log("returning responseBody", responseBody);
        return responseBody;
    } catch (error) {
        return {"error": `AWS error invoking lambda: ${error.message}`};
    }
}

// run()
// main entry point for the cron runner
export async function run(event, context) {
    // log the time this was called
    const time = new Date();
    console.log(`Handler ran at ${time}`);
    // see https://github.com/luin/ioredis#special-note-aws-elasticache-clusters-with-tls

    // get a list of known open anomalies
    const anomalyList = await db.getAnomalies();
    const knownAnomalies = Object.fromEntries(
        anomalyList.map((a) => [`${a.algorithm}:${a.point}`, a])
    );

    // create a (flattened) list of invokeLambda parameters for all of the configured algorithms
    const lambdaParams = (
        await Promise.all(
            algorithms.map(async (cfg: AlgorithmCfg) => {
                const objectList: string[] = await fetchPoints(cfg);
                return objectList.map((point) => ({
                    service: cfg.service,
                    uri: cfg.fn,
                    pointName: point,
                }));
            })
        )
    ).flat(2);
    // collect the results from all of the async lambda calls
    const results = await Promise.allSettled(
        lambdaParams.map(async (param) => {
            const lambdaResult = await invokeLambda(
                param.service,
                param.uri,
                param.pointName
            );
            const invokeKey = `${param.uri}:${param.pointName}`;
            if (Object.keys(lambdaResult).length > 0) {
                // anomaly detected; store it
                const ts = time.getTime();
                const anomaly: MeterAnomaly = {
                    ...lambdaResult,
                    point: param.pointName,
                    algorithm: param.uri
                };
                const anomID = await db.addAnomaly(anomaly);
                console.log("added anomaly", anomID)
                // check if this is a known anomaly
                if (invokeKey in knownAnomalies) {
                    return null;
                }
                else{
                    return anomaly;
                }
            } else {
                // clear anomaly
                await db.clearAllAnomalies(param.uri, param.pointName);
            }
            return null;
        })
    );
    //make the report
    const report = results
        .filter((r) => r.status != "fulfilled" || r.value) // only results with errors or responses
        .map((r) => {
            // get the value or the reason
            if (r.status == "fulfilled") {
                return JSON.stringify(r.value);
            } else {
                // rejected
                return r.reason;
            }
        })
        .sort();
    if (report.length > 0){
        // make this pretty and deliver it to an e-mail list using SNS:
        // Create publish parameters
        const Message = `Meter Anomaly Report for ${time.toLocaleString()}:
        ${report.join("\n")}

        To see the list of known anomalies, see ${REPORT_URL}.
        To configure points assigned to anomaly detection algorithms, see https://www.emcs.cornell.edu/MeterAnomalyConfig.
        `;
        const params = {
            Message,
            TopicArn: "arn:aws:sns:us-east-1:498547149247:emcs-meter-anomalies",
        };
        // Await promise
        var publishText = await sns.publish(params).promise();
        // Handle promise's fulfilled/rejected states
        console.log("Report MessageID is " + publishText.MessageId);
    }
    else{
        console.log("Empty Report");
    }
}
