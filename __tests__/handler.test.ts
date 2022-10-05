// handler.test.ts
import axios from "axios";
import { run, fetchPoints } from "../handler";

jest.mock("axios");
const mockedAxios = jest.mocked(axios);
test("correct greeting is generated", async () => {
  const objList = {
    status: "in-service",
    name: "MeterAnomaly.Test.PointList",
    objectList: ['KlarmanHall.Elec.Solar.PowerScout3037/kW_System'],
  };
  const resp = { data: objList };
  mockedAxios.get.mockResolvedValue(resp);
  const cfg = {
    objListPoint: "MeterAnomaly.Test.PointList",
    fn: async (pointName: string) => {
      throw new Error("Not Implemented Yet");
    },
  };
  expect(await fetchPoints(cfg)).toBe(objList.objectList);
});
