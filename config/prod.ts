import { AppConfig } from "./environments";

export const prodConfig: AppConfig = {
  environment: "prod",

  api: {
    corsAllowedOrigins: ["*"], // In production, specify allowed origins
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
