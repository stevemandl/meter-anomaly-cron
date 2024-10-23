
type DateOnly = `${number}-${number}`;
type TimeOnly = `${number}:${number}:${number}`;
type TzOp = '+' | '-';
type TimeZone = 'Z' | `${TzOp}${number}` | `${TzOp}${number}:${number}`;
type DateISO = DateOnly | `${DateOnly}T${TimeOnly}${TimeZone}` | `${DateOnly}T${TimeOnly}.${number}${TimeZone}`;

type MeterAnomaly = {
    point: string,
    algorithm: string,
    anomaly_ts: DateISO,
    clear_ts: DateISO,
    other_points: string[],
    calculated_score: number,
    anomaly_threshold_score: number,
    descscription: string,
    start_ts: DateISO,
    end_ts: DateISO,
};

type Algorithm = (event: {
    body: string;
}) => Promise<{ statusCode: number; body: string }>;

type AlgParams = { pointName: string; timeStamp: Date };

type AlgorithmCfg = {
    objListPoint: string;
    fn: string;
    service: string;
};

type ObjList = {
    name: string;
    objectList: string; // EMCS API responses are text/plain, so we need to manually parse
};

type TrendTimeseries = {
    target: string;
    datapoints: [number, number][];
    metric?: string;
};

type TrendArray = TrendTimeseries[];

type TrendResponse = {
    error?: any;
    data?: TrendArray;
};
