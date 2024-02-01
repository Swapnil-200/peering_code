#!/usr/bin/env python3
import os
import yaml

import aws_cdk as cdk

from vpc.vpc_stack import VpcStack


app = cdk.App()

with open('environment.yaml', 'r') as envfile:
    yaml_environment = yaml.safe_load(envfile)


for i in range(len(yaml_environment['vpc'])):


    env = yaml_environment['vpc'][i]['name']
    region = yaml_environment['vpc'][i]['region']
    account = yaml_environment['vpc'][i]['account']
    cidr = yaml_environment['vpc'][i]['cidr']

    cdk_env = cdk.Environment(account=account, region=region)

    vpc = VpcStack(app, f"network-vpc-{env}-{region}",env=cdk_env)
    vpc.create_vpc_and_subnets(env, region, cidr)

app.synth()
