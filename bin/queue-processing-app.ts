#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib/core';
import {QueueStack} from "../lib/stacks/queue-stack";

const app = new cdk.App();

new QueueStack(app, "QueueStack");

