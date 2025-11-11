import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecr from "aws-cdk-lib/aws-ecr";

interface LambdaStackProps extends cdk.StackProps {
  readonly ecrRepositoryArn: string;
  readonly imageTag: string;
  readonly lambdaIamRole: iam.IRole;
  readonly vpcId?: string;
  readonly subnets?: string[];
  readonly tags: { [key: string]: string };
  readonly functionName?: string;
  readonly description?: string;
}

export class LambdaStack extends cdk.Stack {
  public readonly lambdaFunction: lambda.DockerImageFunction;

  constructor(scope: Construct, id: string, props: LambdaStackProps) {
    super(scope, id, props);

    const vpc = props.vpcId
      ? ec2.Vpc.fromLookup(this, "Vpc", { vpcId: props.vpcId })
      : undefined;

    const vpcSubnets =
      props.subnets && vpc
        ? {
            subnets: props.subnets.map((subnetId, index) =>
              ec2.Subnet.fromSubnetId(this, `Subnet${index}`, subnetId)
            ),
          }
        : undefined;

    const ecrRepository = ecr.Repository.fromRepositoryArn(
      this,
      "EcrRepository-CommandCenterLambda",
      props.ecrRepositoryArn
    );

    this.lambdaFunction = new lambda.DockerImageFunction(
      this,
      `${props.functionName}`,
      {
        functionName: props.functionName,
        description: props.description,
        code: lambda.DockerImageCode.fromEcr(ecrRepository, {
          tagOrDigest: props.imageTag,
        }),
        role: props.lambdaIamRole,
        memorySize: 512,
        vpc,
        vpcSubnets,
        timeout: cdk.Duration.minutes(5),
        environment: {
          env: JSON.stringify(props.tags),
        },
      }
    );
    ecrRepository.grantPull(props.lambdaIamRole);
  }
}
