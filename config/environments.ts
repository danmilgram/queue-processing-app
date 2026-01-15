export type EnvironmentName = "dev" | "staging" | "prod";

export interface AppConfig {
  readonly environment: EnvironmentName;

  readonly api: {
    readonly corsAllowedOrigins: string[];
    readonly timeoutSeconds: number;
  };

  readonly queue: {
    readonly visibilityTimeoutSeconds: number;
    readonly maxReceiveCount: number;
    readonly retentionPeriodDays: number;
  };

  readonly processor: {
    readonly timeoutSeconds: number;
    readonly batchSize: number;
  };
}
