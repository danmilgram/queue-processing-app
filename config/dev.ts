import { AppConfig } from "./environments";

export const devConfig: AppConfig = {
  environment: "dev",

  api: {
    corsAllowedOrigins: ["*"],
    timeoutSeconds: 10,
  },

  queue: {
    visibilityTimeoutSeconds: 180,
    maxReceiveCount: 5,
    retentionPeriodDays: 14,
  },

  processor: {
    timeoutSeconds: 30,
    batchSize: 1,
  },
};
