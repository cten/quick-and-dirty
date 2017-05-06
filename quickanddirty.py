#!/usr/bin/python

import boto3
import time

region='ap-northeast-1'

ec2 = boto3.resource('ec2', region_name=region)
client = boto3.client('ec2', region_name=region)

keyfile = open('challengekey.pem','w')
keypair = client.create_key_pair(KeyName='challengekey')
keyfile.write(str(keypair['KeyMaterial']))
keyfile.close()

user_data = '''
#!/bin/bash
curl -L -o main https://github.com/cten/quick-and-dirty/raw/master/main
chmod 755 main
./main
'''

vpc = ec2.create_vpc(CidrBlock='10.0.0.0/24')
for s in vpc.security_groups.all():
    sg = s	

for r in vpc.route_tables.all():
    route_table = r

subnet = vpc.create_subnet(CidrBlock='10.0.0.0/25')
gateway=ec2.create_internet_gateway()
sg.authorize_ingress(FromPort=22,ToPort=22,CidrIp='0.0.0.0/0',IpProtocol='TCP')
sg.authorize_ingress(FromPort=80,ToPort=80,CidrIp='0.0.0.0/0',IpProtocol='TCP')
sg.authorize_ingress(FromPort=8080,ToPort=8080,CidrIp='0.0.0.0/0',IpProtocol='TCP')

instances = ec2.create_instances(ImageId='ami-0099bd67', KeyName="challengekey", MinCount=1, MaxCount=1, SubnetId=subnet.id ,InstanceType="t2.micro", UserData=user_data)

gateway.attach_to_vpc(VpcId=vpc.id)
route_table.create_route(GatewayId=gateway.id, DestinationCidrBlock='0.0.0.0/0')
eip = client.allocate_address(Domain='vpc')
address = ec2.VpcAddress(eip['AllocationId'])
time.sleep(30)
address.associate(InstanceId=instances[0].id)

print('http://' + eip['PublicIp'] + '/quick-and-dirty')

