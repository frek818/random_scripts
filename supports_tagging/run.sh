#!/usr/bin/env bash

[ -d ./terraform-provider-aws ] && cd terraform-provider-aws

set -e


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Get repo if you're not already inside the repo directory
if ! [[ ${PWD} =~ "terraform-provider-aws" ]]; then
  git clone --depth 1 https://github.com/hashicorp/terraform-provider-aws.git
  cd terraform-provider-aws
fi

ag '"tags":\s+tftags' -l internal/service \
	| grep ".go" \
	| grep -v -P "(data_source|kinesis\/migrate\.go|networkmanager\/core_network\.go|rds\/instance_migrate\.go|opsworks\/layers\.go)" \
	| python3 ${SCRIPT_DIR}/aws_provider_resources_support_tags.py
