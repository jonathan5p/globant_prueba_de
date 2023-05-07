from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct

class NetworkingStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_config: dict,
        app_prefix: str,
        stack_config: dict,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
        self.env_config = env_config
        self.stack_config = stack_config
        self.app_prefix = app_prefix
        self.main()

    def main(self) -> None:
        
        # Configuration of the subnets deploy in the project VPC
        subnet_config = [{ "cidrMask": 24, 
                           "name": "auroradb-private-subnet2", 
                           "subnetType": ec2.SubnetType.PRIVATE_WITH_EGRESS},
                        { "cidrMask": 24, 
                           "name": "auroradb-public-subnet", 
                           "subnetType": ec2.SubnetType.PUBLIC}]
        
        # Project VPC creation
        self.project_vpc = ec2.Vpc(self, self.app_prefix + "vpc",ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
                                    vpc_name = self.app_prefix + "vpc",
                                    subnet_configuration=subnet_config,
                                    max_azs=self.stack_config.get("max_azs")
                                   )

        # Security group assign to all DMS related instances (replication instance, bastion instance)
        self.lambda_sg = ec2.SecurityGroup(self,
                                        self.app_prefix + "lambda_sg",
                                        vpc = self.project_vpc,
                                        allow_all_outbound = True,
                                        description = "api lambda security group"
                                       )

        # Security group assign to the Aurora MySQL DB
        self.auroradb_sg = ec2.SecurityGroup(self,
                                             self.app_prefix + "AuroraDBSG",
                                             vpc = self.project_vpc,
                                             allow_all_outbound = True,
                                             description = "AuroraDB SG"
                                            ) 

        # Allow traffic from the DMS security group to the Aurora DB security group
        self.auroradb_sg.connections.allow_from(self.lambda_sg,
                                                port_range= ec2.Port.tcp(3306),
                                                description = "Allow access from the api lambda to the mysql db"
                                               )
        
        # Attach glue interface endpoint to the project vpc to allow secure traffic between resources in the vpc and glue service
        self.project_vpc.add_interface_endpoint(self.app_prefix + "GlueInterfaceEndpoint",
                                                 service=ec2.InterfaceVpcEndpointAwsService.GLUE)