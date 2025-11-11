import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as iam from "aws-cdk-lib/aws-iam";

interface IamRoleStackProps extends cdk.StackProps {
  readonly description?: string;
  readonly policyStatements?: iam.PolicyStatement[];
}

export class IamRoleStack extends cdk.Stack {
  public readonly iamLambdaRole: iam.Role;
  constructor(scope: Construct, id: string, props: IamRoleStackProps) {
    super(scope, id, props);

    this.iamLambdaRole = new iam.Role(this, "CommandCenterLambda-iam-role", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      description: props.description,
    });

    // Attach policy statements from external policy files
    if (props.policyStatements) {
      props.policyStatements.forEach((statement) => {
        this.iamLambdaRole.addToPolicy(statement);
      });
    }
  }
}
