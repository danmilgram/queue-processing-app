import * as cdk from "aws-cdk-lib";

import { ApiStack } from "../lib/stacks/api-stack";
import { ProcessorStack } from "../lib/stacks/processor-stack";
import { QueueStack } from "../lib/stacks/queue-stack";

const app = new cdk.App();

const queueStack = new QueueStack(app, "QueueStack");

new ApiStack(app, "ApiStack", {
  taskQueue: queueStack.taskQueue,
});

new ProcessorStack(app, "ProcessorStack", {
  taskQueue: queueStack.taskQueue,
});
