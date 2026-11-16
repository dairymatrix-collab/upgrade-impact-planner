import { oldApi, safeApi } from "demo-lib";

export function run(input) {
  return oldApi(input) + safeApi(input);
}
