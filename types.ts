// types.ts

export type Algorithm = (pointName: string, startTime?: Date) => Promise<void>;

export type AlgorithmCfg = {
  objListPoint: string;
  fn: Algorithm;
};

export type ObjList = {
  name: string;
  objectList: string[];
};

export type ObjListResponse = {
  data: ObjList;
};
