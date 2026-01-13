import { Stack, StackProps, Duration } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as sqs from "aws-cdk-lib/aws-sqs";

export class QueueStack extends Stack {
  public readonly taskQueue: sqs.Queue;
  public readonly deadLetterQueue: sqs.Queue;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    this.deadLetterQueue = new sqs.Queue(this, "TaskDeadLetterQueue", {
      queueName: "task-dlq.fifo",
      fifo: true,
      retentionPeriod: Duration.days(14),
    });

    this.taskQueue = new sqs.Queue(this, "TaskQueue", {
      queueName: "task-queue.fifo",
      fifo: true,
      contentBasedDeduplication: true,
      visibilityTimeout: Duration.seconds(30),
      deadLetterQueue: {
        queue: this.deadLetterQueue,
        maxReceiveCount: 5,
      },
    });
  }
}
