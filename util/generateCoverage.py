import os
import json
import pprint
import math
import re

services = None
cfn_spec = None

tf_resources = []
cfn_types = []
cfn_occurances = []
tf_occurances = []
cfn_exceptions = {
    'AWS::CloudFormation::CustomResource': 'N/A',
    'AWS::CloudFormation::Macro': 'N/A',
    'AWS::CloudFormation::Stack': 'N/A',
    'AWS::CloudFormation::WaitCondition': 'N/A',
    'AWS::CloudFormation::WaitConditionHandle': 'N/A',
    'AWS::EC2::SecurityGroupEgress': 'N/A',
    'AWS::EC2::SecurityGroupIngress': 'N/A',
    'AWS::EC2::TrunkInterfaceAssociation': 'N/A',
    'AWS::ElastiCache::SecurityGroupIngress': 'N/A',
    'AWS::Redshift::ClusterSecurityGroupIngress': 'N/A',
    'AWS::Route53::RecordSetGroup': 'N/A',
    'AWS::SDB::Domain': 'N/A'
}

with open("util/cfnspec.json", "r") as f:
    cfn_spec = json.loads(f.read())['ResourceTypes']

with open("util/tf_resources.txt", "r") as f:
    lines = f.read().splitlines()
    for line in lines:
        tf_resources.append(line)

for cfntype, _ in cfn_spec.items():
    cfn_types.append(cfntype)

cfn_types.append("AWS::Lambda::LayerVersionPermission")
cfn_types.append("AWS::EC2::VPCEndpointService")
cfn_types.append("AWS::Lambda::LayerVersion")
cfn_types = set(cfn_types)

with open("js/mappings.js", "r") as f:
    text = f.read()
    lines = text.splitlines()
    cfn_occurances += re.compile('(AWS\:\:[a-zA-Z0-9]+\:\:[a-zA-Z0-9]+)').findall(text)
    tf_occurances += re.compile('terraformType\'\:\ \'(aws(?:\_[a-zA-Z0-9]+)+)\'').findall(text)

total_services = 0
total_operations = 0
total_unique_occurances = 0
with open("RESOURCE_COVERAGE.md", "w") as f:
    f.write("## CloudFormation Resource Coverage\n\n")
    f.write("**%s/%s (%s%%)** Resources Covered\n" % (
        len(set(cfn_occurances)),
        len(cfn_types) + len(cfn_exceptions),
        int(math.floor((len(set(cfn_occurances)) + len(cfn_exceptions)) * 100 / len(cfn_types)))
    ))

    f.write("\n| Type | Coverage |\n")
    f.write("| --- | --- |\n")

    for cfntype in sorted(cfn_types):
        coverage = ""
        if cfn_occurances.count(cfntype) > 0:
            coverage = ":thumbsup:"
        if cfntype in cfn_exceptions:
            coverage = cfn_exceptions[cfntype]
        f.write("| *%s* | %s |\n" % (cfntype, coverage))

    f.write("\n## Terraform Coverage\n\n")
    f.write("**%s/%s (%s%%)** Resources Covered\n" % (
        len(set(tf_occurances)),
        len(tf_resources),
        int(math.floor(len(set(tf_occurances)) * 100 / len(tf_resources)))
    ))
    
    f.write("\n| Type | Coverage |\n")
    f.write("| --- | --- |\n")

    for tf_resource in sorted(tf_resources):
        coverage = ""
        if tf_occurances.count(tf_resource) > 0:
            coverage = ":thumbsup:"
        f.write("| *%s* | %s |\n" % (tf_resource, coverage))