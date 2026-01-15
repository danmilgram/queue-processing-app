import { Duration, Stack, StackProps } from "aws-cdk-lib";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

import { AppConfig } from "../../config/environments";

interface QueueStackProps extends StackProps {
  readonly config: AppConfig;
}

export class QueueStack extends Stack {
  public readonly taskQueue: sqs.Queue;
  public readonly deadLetterQueue: sqs.Queue;

  constructor(scope: Construct, id: string, props: QueueStackProps) {
    super(scope, id, props);

    this.deadLetterQueue = new sqs.Queue(this, "TaskDeadLetterQueue", {
      queueName: `task-dlq-${props.config.environment}.fifo`,
      fifo: true,
      retentionPeriod: Duration.days(props.config.queue.retentionPeriodDays),
    });

    this.taskQueue = new sqs.Queue(this, "TaskQueue", {
      queueName: `task-queue-${props.config.environment}.fifo`,
      fifo: true,
      contentBasedDeduplication: true,
      visibilityTimeout: Duration.seconds(props.config.queue.visibilityTimeoutSeconds),
      deadLetterQueue: {
        queue: this.deadLetterQueue,
        maxReceiveCount: props.config.queue.maxReceiveCount,
      },
    });
  }
}
