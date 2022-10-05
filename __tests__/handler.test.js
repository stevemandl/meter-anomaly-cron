// handler.test.js
import axios from 'axios';
import handler from '../handler';

jest.mock('axios');

test('correct greeting is generated', () => {
    const objList = {"status": "in-service", "name": "MeterAnomaly.Test.PointList", "objectList": "['KlarmanHall.Elec.Solar.PowerScout3037/kW_System']"};
    const resp = {data: objList};
    axios.get.mockResolvedValue(resp);
    expect(handler.getLocalGreeting("en")).toBe("Hello!");
    expect(handler.getLocalGreeting("fr")).toBe("🌊");
});