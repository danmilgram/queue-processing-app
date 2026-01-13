import * as cdk from "aws-cdk-lib";
import { QueueStack } from "../lib/stacks/queue-stack";
import { ApiStack } from "../lib/stacks/api-stack";

const app = new cdk.App();

const queueStack = new QueueStack(app, "QueueStack");

new ApiStack(app, "ApiStack", {
  taskQueue: queueStack.taskQueue,
});
