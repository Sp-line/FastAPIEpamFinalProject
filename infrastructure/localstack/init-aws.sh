#!/bin/bash
set -e

echo "Deploying local CloudFormation stack..."
awslocal cloudformation deploy \
  --template-file /etc/localstack/init/ready.d/local-template.yaml \
  --stack-name epam-local-stack

echo "Verifying SES identity..."
awslocal ses verify-email-identity --email-address sender@local.epam.com

echo "Initialization complete!"
