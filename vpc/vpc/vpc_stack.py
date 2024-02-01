from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct


class VpcStack(Stack):
    """
    A class representing a stack for creating VPC and associated subnets.

    Attributes:
    - scope: Construct: The parent of this construct (scope).
    - construct_id: str: The identifier for the construct.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes a new VpcStack instance.

        Args:
        - scope (Construct): The parent of this construct (scope).
        - construct_id (str): The identifier for the construct.
        - **kwargs: Additional keyword arguments for the Stack constructor.
        """
        super().__init__(scope, construct_id, **kwargs)

    def create_vpc_and_subnets(
        self, name: str, region: str, cidr: str
    ) -> None:
        """
        Creates a VPC with associated subnets based on provided parameters.

        Args:
        - name (str): The name of the VPC.
        - region (str): The region where the VPC will be created.
        - cidr (str): The CIDR block for the VPC.

        Returns:
        - None
        """
        new_vpc = ec2.Vpc(
            self,
            id=f"vpc-{name}-{region}",
            vpc_name=f"vpc-{name}-{region}",
            cidr=f"{cidr}",
            max_azs=3,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                # Public subnets
                ec2.SubnetConfiguration(
                    name="snet-public-subnet-01",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                    map_public_ip_on_launch=True,
                ),
                # Private with internet subnets
                ec2.SubnetConfiguration(
                    name="snet-private-internet-subnet-01",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24,
                ),
                # Private subnet
                ec2.SubnetConfiguration(
                    name="snet-private-subnet-01",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
            nat_gateways=1,
        )
