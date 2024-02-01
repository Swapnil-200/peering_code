#!/usr/bin/env python3
import os
import yaml

import aws_cdk as cdk

from ec2.ec2_stack import Ec2Stack

app = cdk.App()

with open('environment.yaml', 'r') as envfile:
    yaml_environment = yaml.safe_load(envfile)


for i in range(len(yaml_environment['ec2'])):

    name = yaml_environment['ec2'][i]['name']
    env_name = yaml_environment['ec2'][i]['env_name']
    region = yaml_environment['ec2'][i]['region']
    account = yaml_environment['ec2'][i]['account']
    instance_type = yaml_environment['ec2'][i]['type']
    instance_ami = yaml_environment['ec2'][i]['ami']
    device_name = yaml_environment['ec2'][i]['device_name']
    key_name = yaml_environment['ec2'][i]['key_name']
    vpc_id = yaml_environment['ec2'][i]['vpc_id']
    is_public = yaml_environment['ec2'][i]['is_public']
    script = yaml_environment['ec2'][i]['script']
    allowed_ports = yaml_environment['ec2'][i]['allowed_ports']
    
    with open(f"./scripts/{script}") as f:
        user_data = f.read()
    
    cdk_env = cdk.Environment(account=account, region=region)

    ec2 = Ec2Stack(app, f"ec2-{name}-{env_name}-{region}",env=cdk_env)
    ec2.create_ec2(name=name, key_name=key_name, device_name=device_name,
                   vpc_id=vpc_id, allowed_ports=allowed_ports,
                   instance_type=instance_type, instance_ami=instance_ami, user_data=user_data, is_public=is_public)

app.synth()
