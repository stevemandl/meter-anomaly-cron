// handler.test.ts
import axios from "axios";
import { run, invokeLambda, fetchPoints, auth } from "../handler";

jest.mock("axios");
const mockedAxios = jest.mocked(axios);
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

test("authorizer works", async () => {
  process.env.SECRET_TOKEN = "testSecret";
  const event = {
    headers: {
      authorization: process.env.SECRET_TOKEN,
    },
  };
  expect((await auth(event)).isAuthorized);
});

test("invokeLambda works", async () => {
  const resp = { data: "test123" };
  mockedAxios.request.mockResolvedValue(resp);
  const lambdaResult = await invokeLambda("foo", "bar");
  expect(lambdaResult).toBe(resp.data);
});
