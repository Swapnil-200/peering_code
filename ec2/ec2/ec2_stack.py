from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct


class Ec2Stack(Stack):
    """
    A class representing a stack for creating EC2 instances and associated resources.

    Attributes:
    - scope: Construct: The parent of this construct (scope).
    - construct_id: str: The identifier for the construct.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes a new Ec2Stack instance.

        Args:
        - scope (Construct): The parent of this construct (scope).
        - construct_id (str): The identifier for the construct.
        - **kwargs: Additional keyword arguments for the Stack constructor.
        """
        super().__init__(scope, construct_id, **kwargs)

    def create_ec2(
        self,
        name: str,
        key_name: str,
        device_name: str,
        vpc_id: str,
        allowed_ports: list,
        instance_type: str,
        instance_ami: str,
        user_data: str,
        is_public: bool,
    ) -> None:
        """
        Creates an EC2 instance with associated resources based on provided parameters.

        Args:
        - name (str): The name of the EC2 instance.
        - key_name (str): The key pair name for SSH access.
        - device_name (str): The device name for block device.
        - vpc_id (str): The ID of the VPC where the instance will be launched.
        - allowed_ports (list): List of dictionaries containing allowed ports and IPs.
        - instance_type (str): The EC2 instance type.
        - instance_ami (str): The AMI ID for the EC2 instance.
        - user_data (str): The user data script for the EC2 instance.
        - is_public (bool): Flag to indicate whether the EC2 instance is public.

        Returns:
        - None
        """
        # Role creation for EC2 instance
        role = iam.Role(
            self,
            f"InstanceRole-application-{name}",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="EC2 role for SSM for Quick-Setup",
            role_name=f"{name}-AmazonSSMRole",
        )
        # Adding managed policies to the role
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMPatchAssociation")
        )

        # VPC lookup
        vpc = ec2.Vpc.from_lookup(
            self, f"VPC-application-{name}", is_default=False, vpc_id=vpc_id
        )

        # Security Group creation for the EC2 instance
        sg = ec2.SecurityGroup(
            self,
            f"SecurityGroup-application-{name}",
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Security group for {name}",
            security_group_name=f"application-{name}",
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

        # Block device configuration for the EC2 instance
        block_device = ec2.BlockDevice(
            device_name=device_name,
            volume=ec2.BlockDeviceVolume.ebs(
                200,
                delete_on_termination=False,
                iops=3000,
                volume_type=ec2.EbsDeviceVolumeType.GP3,
            ),
        )

        # Subnet selection based on public/private settings
        vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        if is_public:
            vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)

        # EC2 instance creation
        ec2_instance = ec2.Instance(
            self,
            f"Instance-application-{name}",
            instance_name=f"application-{name}",
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ec2.MachineImage().lookup(name=instance_ami),
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_group=sg,
            key_name=key_name,
            role=role,
            block_devices=[block_device],
            user_data=ec2.UserData.custom(user_data),
        )
