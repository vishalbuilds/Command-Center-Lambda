import * as iam from "aws-cdk-lib/aws-iam";

export function S3Policy(resources: string[]): iam.PolicyStatement[] {
  return [
    new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      resources: resources,
    }),
  ];
}
