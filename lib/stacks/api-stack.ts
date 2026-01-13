import * as cdk from "aws-cdk-lib";
import * as path from "path";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigwv2 from "aws-cdk-lib/aws-apigatewayv2";
import * as integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as iam from "aws-cdk-lib/aws-iam";
import * as sqs from "aws-cdk-lib/aws-sqs";

import { Stack, StackProps, Duration } from "aws-cdk-lib";
import { Construct } from "constructs";

interface ApiStackProps extends StackProps {
    taskQueue: sqs.Queue;
}

export class ApiStack extends Stack {
    constructor(scope: Construct, id: string, props: ApiStackProps) {
        super(scope, id, props);

        const apiLambda = new lambda.Function(this, "ApiLambda", {
            runtime: lambda.Runtime.PYTHON_3_11,
            handler: "app.handler",
            code: lambda.Code.fromAsset(
                path.join(__dirname, "../../services/api"),
                {
                    bundling: {
                        image: lambda.Runtime.PYTHON_3_11.bundlingImage,
                        command: [
                            "bash",
                            "-c",
                            [
                                "pip install -r requirements.txt -t /asset-output",
                                "cp -au . /asset-output",
                            ].join(" && "),
                        ],
                    },
                }
            ),
            timeout: Duration.seconds(10),
            environment: {
                QUEUE_URL: props.taskQueue.queueUrl,
            },
        });

        // Least-privilege permission: only send messages
        apiLambda.addToRolePolicy(
            new iam.PolicyStatement({
                actions: ["sqs:SendMessage"],
                resources: [props.taskQueue.queueArn],
            })
        );

        const httpApi = new apigwv2.HttpApi(this, "TaskApi", {
            corsPreflight: {
                allowHeaders: ["Content-Type"],
                allowMethods: [apigwv2.CorsHttpMethod.POST],
                allowOrigins: ["*"],
            },
        });

        httpApi.addRoutes({
            path: "/tasks",
            methods: [apigwv2.HttpMethod.POST],
            integration: new integrations.HttpLambdaIntegration(
                "TaskApiIntegration",
                apiLambda
            ),
        });

        new cdk.CfnOutput(this, "ApiUrl", {
            value: httpApi.apiEndpoint,
            description: "Base URL for Task API",
        });

    }
}
