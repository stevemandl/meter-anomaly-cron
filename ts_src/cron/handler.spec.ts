// handler.test.ts
import axios from "axios";
import { Lambda, SNS } from "aws-sdk";

import { run, invokeLambda, fetchPoints } from "./handler";
import * as db from "../tslib/anomalyDB";

jest.mock("axios");
const mockedAxios = jest.mocked(axios);
const mockLambdaInvoke = (new Lambda()).invoke;
const mockSNSPublish = (new SNS()).publish;
const resp = { data: "test123" };
jest.mock("aws-sdk", () => {
  const mLambda = {
    invoke: jest.fn(() => {
      return {
        promise: jest.fn(() => {
          return { Payload: JSON.stringify(resp) };
        }),
      };
    }),
  };
  const mSNS = {
    publish: jest.fn(() => {
      return {
        promise: jest.fn(() => {
          return { MessageId: "test-message-id" };
        }),
      };
    }),
  };
  return { Lambda: jest.fn(() => mLambda), SNS: jest.fn(() => mSNS) };
});
jest.mock("../tslib/anomalyDB");

describe("root handler testing", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.EMCS_API_KEY = "test-api-key";
    process.env.SAM_STAGE = "test";
  });

  test("runs all anomaly detections successfully", async () => {
    // Mock fetchPoints
    mockedAxios.get.mockResolvedValue({ data: { objectList: "['Point1', 'Point2']" } });
    // Mock getAnomalies
    (db.getAnomalies as jest.Mock).mockResolvedValue([]);
 
    // Mock addAnomaly
    (db.addAnomaly as jest.Mock).mockResolvedValue("test-anomaly-id");

    await run({}, {});

    expect(mockedAxios.get).toHaveBeenCalledTimes(4); // Once for each algorithm
    expect(mockLambdaInvoke).toHaveBeenCalledTimes(8); // Twice for each point (2) and each algorithm (4)
    expect(db.addAnomaly).toHaveBeenCalledTimes(8);
    expect(mockSNSPublish).toHaveBeenCalledTimes(1);
  });

  test("handles errors in fetchPoints", async () => {
    mockedAxios.get.mockRejectedValue(new Error("API error"));
    // Mock getAnomalies
    (db.getAnomalies as jest.Mock).mockResolvedValue([]);

    await run({}, {});

    expect(mockedAxios.get).toHaveBeenCalled();
    expect(mockLambdaInvoke).not.toHaveBeenCalled();
  });

  test("object list is returned", async () => {
    const objName = "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
      objList = {
        status: "in-service",
        name: "MeterAnomaly.Test.PointList",
        objectList: `['${objName}']`,
      };
    const resp = { data: objList };
    mockedAxios.get.mockResolvedValue(resp);
    const cfg = {
      objListPoint: "MeterAnomaly.Test.PointList",
      fn: "testTemplate",
    };
    expect(await fetchPoints(cfg)).toStrictEqual([objName]);
  });

  test("invokeLambda works", async () => {
    mockedAxios.get.mockResolvedValue(resp);
    const lambdaResult = await invokeLambda("foo", "bar", "biff");
    expect(lambdaResult).toStrictEqual(resp);
  });
  
  test("does not send report when no anomalies detected", async () => {
    mockedAxios.get.mockResolvedValue({ data: { objectList: "['Point1']" } });
    
    mockLambdaInvoke.mockImplementation(() => ({
      promise: jest.fn().mockResolvedValue({
        Payload: "{}"
      })
    }));

    await run({}, {});

    expect(mockedAxios.get).toHaveBeenCalledTimes(4);
    expect(mockLambdaInvoke).toHaveBeenCalledTimes(4);
    expect(mockSNSPublish).not.toHaveBeenCalled();
  });

  test("handles errors in invokeLambda", async () => {
    mockedAxios.get.mockResolvedValue({ data: { objectList: "['Point1']" } });
    
    mockLambdaInvoke.mockImplementation(() => ({
      promise: jest.fn().mockRejectedValue(new Error("Lambda error"))
    }));

    await run({}, {});

    expect(mockedAxios.get).toHaveBeenCalledTimes(4);
    expect(mockLambdaInvoke).toHaveBeenCalledTimes(4);
    expect(mockSNSPublish).toHaveBeenCalledTimes(1);
  });
});
