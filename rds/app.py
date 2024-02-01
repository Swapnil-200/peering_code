#!/usr/bin/env python3
import os
import yaml

import aws_cdk as cdk

from rds.subnet_group_stack import RdsSubnetGroupStack
from rds.rds_instance_stack import RdsInstanceStack


app = cdk.App()

with open("environment.yaml", "r") as envfile:
    yaml_environment = yaml.safe_load(envfile)

for i in range(len(yaml_environment["db"])):
    name = yaml_environment["db"][i]["name"]
    id = yaml_environment["db"][i]["id"]
    subnet_ids = yaml_environment["db"][i]["subnet_ids"]
    account = yaml_environment["db"][i]["account"]
    region = yaml_environment["db"][i]["region"]
    engine = yaml_environment["db"][i]["engine"]
    instance_type = yaml_environment["db"][i]["instance_type"]
    storage = yaml_environment["db"][i]["storage"]
    username = yaml_environment["db"][i]["username"]
    password = yaml_environment["db"][i]["password"]
    vpc_id = yaml_environment["db"][i]["vpc_id"]
    allowed_ports = yaml_environment["db"][i]["allowed_ports"]
    multi_az = yaml_environment["db"][i]["multi_az"]
    port = yaml_environment["db"][i]["port"]

    cdk_env = cdk.Environment(account=account, region=region)

    subnet_group = RdsSubnetGroupStack(
        app,
        f"DatabaseSubnetGroupStack-{name}",
        name=name,
        id=id,
        subnet_ids=subnet_ids,
        env=cdk_env,
    )

    RdsInstanceStack(
        app,
        f"RDSInstanceStack-{name}",
        name=name,
        id=id,
        engine=engine,
        instance_type=instance_type,
        multi_az=multi_az,
        storage=int(storage),
        username=username,
        password=password,
        port=int(port),
        vpc_id=vpc_id,
        allowed_ports=allowed_ports,
        subnet_group_name=subnet_group.subnet_group_name,
        env=cdk_env,
    )


app.synth()
