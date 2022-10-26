// testTemplate/handler.test.ts
import { run } from "./handler";
import * as utils from "../tslib/utils";

jest.mock("../tslib/utils", () => {
    const originalUtils = jest.requireActual("../tslib/utils");
    return {
        __esModule: true,
        ...originalUtils,
        fetchTrends: jest.fn(() => ({ data: [{ datapoints: [] }] })),
    };
});
const mockedUtils = jest.mocked(utils);
test("doesn't barf", async () => {
    const event = {
        body: '{"pointName":"KlarmanHall.Elec.Solar.PowerScout3037/kW_System","timeStamp":"2022-10-05T23:58:47.390Z"}',
    };
    const result = await run(event);
    expect(result).toHaveProperty("statusCode");
    expect(result.body).toMatch("missing");
});

test("handles 400 no data", async () => {
    mockedUtils.fetchTrends.mockRejectedValue({
        response: { status: 400, data: { error: "No data" } },
        message: "whatever",
    });
    const event = { body: '{"pointName":"foo"}' };
    const result = await run(event);
    expect(result).toHaveProperty("statusCode");
    expect(result.body).toMatch("no data");
});

test("barfs when it should", async () => {
    mockedUtils.fetchTrends.mockRejectedValue({
        response: { status: 400 },
        message: "qwerty",
    });
    const event = { body: '{"pointName":"foo"}' };
    const result = await run(event);
    expect(result).toHaveProperty("statusCode");
    expect(result.body).toMatch("qwerty");
});
