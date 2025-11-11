import * as cdk from "aws-cdk-lib";
import { Template } from "aws-cdk-lib/assertions";
import { IamRoleStack } from "../lib/iam-role-stack";
import { ConnectPolicy } from "../lib/iam-role-policies/iam-policy-connect";

describe("IamRoleStack", () => {
  test("Creates IAM Role with Lambda service principal", () => {
    const app = new cdk.App();
    const stack = new IamRoleStack(app, "TestStack", {
      iamRoleName: "TestLambdaRole",
      description: "Test role for Lambda",
    });

    const template = Template.fromStack(stack);

    template.hasResourceProperties("AWS::IAM::Role", {
      AssumeRolePolicyDocument: {
        Statement: [
          {
            Action: "sts:AssumeRole",
            Effect: "Allow",
            Principal: {
              Service: "lambda.amazonaws.com",
            },
          },
        ],
      },
    });

    expect(template.toJSON()).toMatchSnapshot();
  });

  test("Attaches policy statements when provided", () => {
    const app = new cdk.App();
    const connectPolicies = ConnectPolicy(["arn:aws:connect:*:*:instance/*"]);

    const stack = new IamRoleStack(app, "TestStack", {
      iamRoleName: "TestLambdaRole",
      policyStatements: connectPolicies,
    });

    const template = Template.fromStack(stack);

    template.hasResourceProperties("AWS::IAM::Policy", {
      PolicyDocument: {
        Statement: [
          {
            Action: [
              "connect:StartOutboundVoiceContact",
              "connect:StopContact",
              "connect:GetContactAttributes",
            ],
            Effect: "Allow",
            Resource: "arn:aws:connect:*:*:instance/*",
          },
        ],
      },
    });

    expect(template.toJSON()).toMatchSnapshot();
  });

  test("Applies tags when provided", () => {
    const app = new cdk.App();
    const stack = new IamRoleStack(app, "TestStack", {
      iamRoleName: "TestLambdaRole",
      tags: {
        Environment: "test",
        Project: "CDK",
      },
    });

    const template = Template.fromStack(stack);
    template.resourceCountIs("AWS::IAM::Role", 1);
    expect(template.toJSON()).toMatchSnapshot();
  });
});

describe("ConnectPolicy", () => {
  test("Creates policy with correct Connect actions", () => {
    const policies = ConnectPolicy([
      "arn:aws:connect:us-east-1:123456789012:instance/test",
    ]);

    expect(policies).toHaveLength(1);
    expect(policies[0].toStatementJson()).toMatchObject({
      Effect: "Allow",
      Action: [
        "connect:StartOutboundVoiceContact",
        "connect:StopContact",
        "connect:GetContactAttributes",
      ],
      Resource: "arn:aws:connect:us-east-1:123456789012:instance/test",
    });
  });
});
