#!/usr/bin/env node
import "source-map-support/register";

import { App } from "aws-cdk-lib";

import { devConfig } from "../config/dev";
import { AppConfig } from "../config/environments";
import { prodConfig } from "../config/prod";
import { ApiStack } from "../lib/stacks/api-stack";
import { ProcessorStack } from "../lib/stacks/processor-stack";
import { QueueStack } from "../lib/stacks/queue-stack";

const app = new App();

/**
 * Resolve environment from context:
 * cdk synth -c env=dev
 * cdk synth -c env=prod
 */
const envName = app.node.tryGetContext("env") ?? "dev";

const config: AppConfig = (() => {
  switch (envName) {
    case "prod":
      return prodConfig;
    case "dev":
    default:
      return devConfig;
  }
})();

/**
 * Stack environment
 * ✔ No hardcoded account/region
 */
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const queueStack = new QueueStack(app, `QueueStack-${config.environment}`, {
  env,
  config,
});

const processorStack = new ProcessorStack(
  app,
  `ProcessorStack-${config.environment}`,
  {
    env,
    config,
    taskQueue: queueStack.taskQueue,
  }
);

new ApiStack(app, `ApiStack-${config.environment}`, {
  env,
  config,
  taskQueue: queueStack.taskQueue,
});
