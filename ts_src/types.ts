// types.ts

export type Algorithm = (event: {
  body: string;
}) => Promise<{ statusCode: number; body: string }>;

export type AlgParams = { pointName: string; timeStamp: Date };

export type AlgorithmCfg = {
  objListPoint: string;
  fn: string;
  service: string;
};

export type ObjList = {
  name: string;
  objectList: string; // EMCS API responses are text/plain, so we need to manually parse
};

export type TrendTimeseries = {
  target: string;
  datapoints: [number, number][];
  metric?: string;
};

export type TrendArray = TrendTimeseries[];

export type TrendResponse = {
  error?: any;
  data?: TrendArray;
};
