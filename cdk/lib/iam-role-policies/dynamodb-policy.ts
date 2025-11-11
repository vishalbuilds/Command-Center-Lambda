import * as iam from "aws-cdk-lib/aws-iam";

export function DynamoDBPolicy(resources: string[]): iam.PolicyStatement[] {
  return [
    new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
      ],
      resources: resources,
    }),
  ];
}
