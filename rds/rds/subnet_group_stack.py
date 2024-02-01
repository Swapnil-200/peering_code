from aws_cdk import (
    # Duration,
    Stack,
    aws_rds as rds,
)
from constructs import Construct


class RdsSubnetGroupStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name: str,
        id: str,
        subnet_ids: list,
        **kwargs,
    ) -> None:
        """
        Initialize an RDS Subnet Group Stack.

        Args:
        - scope (Construct): The parent Construct instantiating this class.
        - construct_id (str): The ID of this Construct.
        - name (str): The name of the RDS subnet group.
        - id (str): The ID of the RDS subnet group.
        - subnet_ids: Subnet IDs associated with the RDS subnet group.
        - **kwargs: Additional keyword arguments passed to the Stack.

        Returns:
        - None
        """
        super().__init__(scope, construct_id, **kwargs)

        subnet_group = rds.CfnDBSubnetGroup(
            self,
            f"MyDBSubnetGroup-{name}",
            db_subnet_group_description=f"{id}-{name} subnet group",
            subnet_ids=subnet_ids,
            db_subnet_group_name=f"{id}-{name}-subnet-group",
        )

        self.subnet_group_name = subnet_group.db_subnet_group_name
