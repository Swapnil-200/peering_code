from aws_cdk import (
    # Duration,
    Stack,
    aws_rds as rds,
    aws_ec2 as ec2,
    SecretValue as sv,
)
from constructs import Construct
import os


class RdsInstanceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name: str,
        multi_az: bool,
        engine: str,
        instance_type: str,
        storage: int,
        username: str,
        password: str,
        port: int,
        vpc_id: str,
        id: str,
        subnet_group_name: str,
        allowed_ports: list,
        **kwargs,
    ) -> None:
        """
        Initialize an RDS Instance Stack.

        Args:
        - scope (Construct): The parent Construct instantiating this class.
        - construct_id (str): The ID of this Construct.
        - name (str): The name of the RDS instance.
        - multi_az (bool): Whether the RDS instance should be multi-AZ.
        - engine (str): The engine for the RDS instance.
        - instance_type (str): The EC2 instance type for the RDS instance.
        - storage (int): The allocated storage for the RDS instance.
        - username (str): Username for database access.
        - password (str): Password for database access.
        - port (int): Port number for the RDS instance.
        - vpc_id (str): ID of the VPC where the RDS instance will be launched.
        - id (str): The ID of the RDS instance.
        - subnet_group_name (str): Name of the subnet group for the RDS instance.
        - allowed_ports (list): List of allowed ports for security group configuration.
        - **kwargs: Additional keyword arguments passed to the Stack.

        Returns:
        - None
        """
        super().__init__(scope, construct_id, **kwargs)

        db_engine = self.get_db_engine(engine)

        db_credentials = self.get_db_credentials(username, password)

        vpc = self.get_db_vpc(name, vpc_id)

        subnet_group = self.get_subnet_group(name, subnet_group_name)

        security_group = self.get_security_group(vpc, name, allowed_ports)

        instance_type = ec2.InstanceType(f"{instance_type}")

        db_instance = rds.DatabaseInstance(
            self,
            f"DBInstance-{name}",
            engine=db_engine,
            credentials=db_credentials,
            vpc=vpc,
            allocated_storage=storage,
            multi_az=multi_az,
            subnet_group=subnet_group,
            security_groups=[security_group],
            port=port,
            instance_identifier=f"{name}",
            instance_type=instance_type,
            ca_certificate=rds.CaCertificate.RDS_CA_RDS2048_G1,
        )

    def get_db_engine(self, engine: str) -> rds.IInstanceEngine:
        """
        Get the RDS database engine based on the specified engine type.

        Args:
        - engine (str): The engine type to be matched.

        Returns:
        - rds.IInstanceEngine: An RDS instance engine corresponding to the specified engine type.
        """
        match engine:
            case "postgres":
                return rds.DatabaseInstanceEngine.POSTGRES
            case "mysql":
                return rds.DatabaseInstanceEngine.MYSQL
            case _:
                return rds.DatabaseInstanceEngine.MYSQL

    def get_db_credentials(self, username: str, password: str) -> rds.Credentials:
        """
        Generate RDS credentials using the provided username and password.

        Args:
        - username (str): The username for the database credentials.
        - password (str): The password for the database credentials.

        Returns:
        - rds.Credentials: RDS credentials generated from the provided username and password.
        """
        return rds.Credentials.from_password(
            os.environ[f"{username}"], sv.unsafe_plain_text(os.environ[f"{password}"])
        )

    def get_db_vpc(self, name: str, vpc_id: str) -> ec2.IVpc:
        """
        Retrieve the VPC using the provided VPC ID.

        Args:
        - name (str): The name identifier for the VPC.
        - vpc_id (str): The ID of the VPC to retrieve.

        Returns:
        - ec2.IVpc: The retrieved VPC.
        """
        return ec2.Vpc.from_lookup(
            self, f"vpc-bd-{name}", is_default=False, vpc_id=vpc_id
        )

    def get_subnet_group(self, name: str, subnet_group_name: str):
        """
        Retrieve the subnet group based on the subnet group name.

        Args:
        - name (str): The name identifier for the subnet group.
        - subnet_group_name (str): The name of the subnet group to retrieve.

        Returns:
        - rds.SubnetGroup: The retrieved subnet group.
        """
        return rds.SubnetGroup.from_subnet_group_name(
            self, f"MySubnetGroup-{name}", subnet_group_name
        )

    def get_security_group(
        self, vpc: ec2.IVpc, name: str, allowed_ports: list
    ) -> ec2.SecurityGroup:
        """
        Retrieve or create a security group for the database instance.

        Args:
        - vpc (ec2.IVpc): The VPC for which the security group is created.
        - name (str): The name identifier for the security group.
        - allowed_ports (list): List of allowed ports and their corresponding IPs.

        Returns:
        - ec2.SecurityGroup: The retrieved or created security group for the database instance.
        """
        sg = ec2.SecurityGroup(
            self,
            f"SecurityGroup-db-{name}",
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Security group for {name}",
            security_group_name=f"db-{name}",
        )

        # Adding ingress rules to the security group based on allowed ports and IPs
        for i in allowed_ports:
            key = next(iter(i))

            port = i[key][0]["port"]
            ip = i[key][0]["ip"]
            description = i[key][0]["ip"]

            if ip == "any":
                sg.add_ingress_rule(
                    ec2.Peer.any_ipv4(), ec2.Port.tcp(port), description=description
                )
            else:
                sg.add_ingress_rule(
                    ec2.Peer.ipv4(ip), ec2.Port.tcp(port), description=description
                )

        return sg
