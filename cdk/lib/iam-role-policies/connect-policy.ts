import * as iam from "aws-cdk-lib/aws-iam";

export function ConnectPolicy(resources: string[]): iam.PolicyStatement[] {
  return [
    new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        "connect:StartOutboundVoiceContact",
        "connect:StopContact",
        "connect:GetContactAttributes",
      ],
      resources: resources,
    }),
  ];
}
