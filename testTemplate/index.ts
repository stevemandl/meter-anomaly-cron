// index.ts

import { Algorithm } from "../types";

const run: Algorithm = async (event) => {
  const time = new Date();
  console.log(`testTemplate run at ${time}`);
  throw new Error("Not Implemented Yet");
};

export default run;