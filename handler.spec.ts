// handler.test.ts
import axios from "axios";
import { Lambda } from "aws-sdk";

import { run, invokeLambda, fetchPoints } from "./handler";

jest.mock("axios");
const mockedAxios = jest.mocked(axios);
jest.mock("aws-sdk", () => {
  const mLambda = {
    invoke: jest.fn(() => {
      return {
        promise: jest.fn(() => {
          return { Payload: '{"body":{"data": "test123"}}' };
        }),
      };
    }),
  };
  return { Lambda: jest.fn(() => mLambda) };
});

describe("root handler testing", () => {

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
    const resp = { data: "test123" };

    const lambdaResult = await invokeLambda("foo", "bar");
    expect(lambdaResult).toStrictEqual(resp);
    expect(Lambda).toBeCalledWith({
      apiVersion: "2015-03-31",
      endpoint: "https://lambda.us-east-1.amazonaws.com",
    });
  });
});
