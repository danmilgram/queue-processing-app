import { Stack, StackProps, Duration } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sqs from "aws-cdk-lib/aws-sqs";
import * as eventSources from "aws-cdk-lib/aws-lambda-event-sources";

interface ProcessorStackProps extends StackProps {
  taskQueue: sqs.Queue;
}

export class ProcessorStack extends Stack {
  constructor(scope: Construct, id: string, props: ProcessorStackProps) {
    super(scope, id, props);

    const processorLambda = new lambda.Function(this, "TaskProcessorLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "handler.handle",
      code: lambda.Code.fromAsset("services/processor"),
      timeout: Duration.seconds(30),
    });

    // Allow Lambda to consume messages from the queue
    props.taskQueue.grantConsumeMessages(processorLambda);

    // SQS event source with strict ordering
    processorLambda.addEventSource(
      new eventSources.SqsEventSource(props.taskQueue, {
        batchSize: 1, // critical for FIFO ordering
      })
    );
  }
}
