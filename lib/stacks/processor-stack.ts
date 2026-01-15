import * as path from "path";

import { Duration, Stack, StackProps } from "aws-cdk-lib";
import * as eventSources from "aws-cdk-lib/aws-lambda-event-sources";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

import { AppConfig } from "../../config/environments";

interface ProcessorStackProps extends StackProps {
  readonly config: AppConfig;
  readonly taskQueue: sqs.Queue;
}

export class ProcessorStack extends Stack {
  constructor(scope: Construct, id: string, props: ProcessorStackProps) {
    super(scope, id, props);

    const processorLambda = new lambda.Function(this, "TaskProcessorLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.processor.handler.handle",
      code: lambda.Code.fromAsset(path.join(__dirname, "../../"), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_11.bundlingImage,
          command: [
            "bash",
            "-c",
            [
              "pip install -r services/processor/requirements.txt -t /asset-output",
              "cp -au services /asset-output/",
            ].join(" && "),
          ],
        },
      }),
      timeout: Duration.seconds(props.config.processor.timeoutSeconds),
      environment: {
        ENVIRONMENT: props.config.environment,
      },
    });

    // Allow Lambda to consume messages from the queue
    props.taskQueue.grantConsumeMessages(processorLambda);

    // SQS event source with strict ordering
    processorLambda.addEventSource(
      new eventSources.SqsEventSource(props.taskQueue, {
        batchSize: props.config.processor.batchSize,
      })
    );
  }
}
