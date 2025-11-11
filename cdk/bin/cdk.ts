#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { LambdaStack } from "../lib/lambda-stack";
import { IamRoleStack } from "../lib/iam-role-stack";
import { ConnectPolicy } from "../lib/iam-role-policies/connect-policy";
import { DynamoDBPolicy } from "../lib/iam-role-policies/dynamodb-policy";
import { S3Policy } from "../lib/iam-role-policies/s3-policy";

// App
const app = new cdk.App();

/**
 * Get context values passed via CLI:
 * Example:
 * cdk deploy \
 *   -c infraVersion=infraVersion-1 \
 *   -c awsAccount=123456789012 \
 *   -c region=us-east-1 \
 *   -c env=dev \
 *   -c ecrRepositoryArn=arn:aws:ecr:us-east-1:123456789012:repository/Command-Center-Lambda
 *   -c imageTag=imageTag
 */
const infraVersion = app.node.tryGetContext("infraVersion") || "infraVersion-1";
const awsAccount = app.node.tryGetContext("awsAccount") || "123456789012";
const region = app.node.tryGetContext("region") || "us-east-1";
const environment = app.node.tryGetContext("env") || "dev";
const ecrRepositoryArn =
  app.node.tryGetContext("ecrRepositoryArn") ||
  "arn:aws:ecr:us-east-1:123456789012:repository/Command-Center-Lambda";
const imageTag = app.node.tryGetContext("imageTag") || "latest";

//cdk env
const cdkEnv = {
  env: {
    account: awsAccount,
    region: region,
  },
};

// Get the full deployment config from cdk.json
const cdkContext = app.node.tryGetContext(infraVersion);
const cdkRegionContext = cdkContext[region];

// Get universal tags
const cdkTags = app.node.tryGetContext("cdkTags");
const universalTags: Record<string, string> = {
  Owner: cdkTags.owner,
  GitHub: cdkTags.gitHub,
  Email: cdkTags.email,
  Repository: cdkTags.repository,
  Description: cdkTags.description,
  InfraVersion: infraVersion,
  Environment: environment,
  Region: region,
};

const lambdaTags: Record<string, string> = {
  functionName: cdkRegionContext.lambda.functionName,
  vpcId: cdkRegionContext.vpc.vpcId,
  subnets: (cdkRegionContext.vpc.subnets || []).join(","),
  description: cdkRegionContext.lambda.description,
  ecrRepositoryArn: ecrRepositoryArn,
  imageTag: imageTag,
  ...(cdkRegionContext.lambda.envVar || {}),
};

const policies = [
  ...ConnectPolicy(cdkRegionContext.connect.resources),
  ...DynamoDBPolicy(cdkRegionContext.dynamoDB.resources),
  ...S3Policy(cdkRegionContext.s3.resources),
];

const iamRoleStack = new IamRoleStack(
  app,
  `iam-role-${lambdaTags.functionName}-${universalTags.Environment}-${universalTags.Region}-${universalTags.InfraVersion}`,
  {
    description: `iam-role for lambda function ${lambdaTags.functionName} in environment ${universalTags.Environment} for region ${universalTags.Region} with infra version ${universalTags.InfraVersion}`,
    policyStatements: policies,
    ...cdkEnv,
  }
);

// Lambda stack
new LambdaStack(
  app,
  `lambda-${lambdaTags.functionName}-${universalTags.Environment}`,
  {
    ecrRepositoryArn: ecrRepositoryArn,
    imageTag: imageTag,
    lambdaIamRole: iamRoleStack.iamLambdaRole,
    vpcId: cdkRegionContext.vpc.vpcId,
    subnets: cdkRegionContext.vpc.subnets,
    functionName: cdkRegionContext.lambda.functionName,
    description: cdkRegionContext.lambda.description,
    tags: lambdaTags,
    ...cdkEnv,
  }
);

// Apply tags to all stacks
Object.entries(universalTags).forEach(([key, value]) => {
  cdk.Tags.of(app).add(key, value);
});
