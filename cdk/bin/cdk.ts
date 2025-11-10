#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { LambdaStack } from "../lib/lambda-stack";
import { IamRoleStack } from "../lib/iam-role-stack";
import { ConnectPolicy } from "../lib/iam-policy-connect";
import { DynamoDBPolicy } from "../lib/iam-policy-dynamodb";
import { S3Policy } from "../lib/iam-policy-s3";

//app
const app = new cdk.App();

//lambda+ context
const lambdaTags = app.node.tryGetContext("tags");
const lambdaDetails = app.node.tryGetContext("details");
const vpcDetails = app.node.tryGetContext("vpc");

//universal tags
const tags = {
  Owner: lambdaTags["Owner"],
  Environment: lambdaTags["Environment"],
  GitHubUsername: lambdaTags["GitHubUsername"],
  FunctionName: lambdaDetails["FunctionName"],
  FunctionDescription: lambdaDetails["description"],
  Vpc: vpcDetails["vpc"],
  Subnet: vpcDetails["subnet"],
};

//policies resourse
const connectResources = app.node.tryGetContext("connect");
const dynamoDBResources = app.node.tryGetContext("dynamoDB");
const s3Resources = app.node.tryGetContext("s3");

//Iam policy stack list
const policies = [
  ...ConnectPolicy(connectResources),
  ...DynamoDBPolicy(dynamoDBResources),
  ...S3Policy(s3Resources),
];

//Iam role context
const iamRole = app.node.tryGetContext("iamRole");

//Iam role stack
const iamRoleStack = new IamRoleStack(
  app,
  `iam-role-${iamRole["roleName"]}-${lambdaTags["Environment"]}`,
  {
    description: iamRole["description"],
    iamRoleName: iamRole["roleName"],
    policyStatements: policies,
    tags,
  }
);

//lambda stack
new LambdaStack(
  app,
  `lambda-${lambdaDetails["FunctionName"]}-${lambdaTags["Environment"]}`,
  {
    containerImage: "test",
    lambdaIamRole: iamRoleStack.iamLambdaRole,
    vpcId: vpcDetails["vpc"],
    subnets: vpcDetails["subnet"],
    functionName: lambdaDetails["FunctionName"],
    description: lambdaDetails["description"],
    tags,
  }
);
