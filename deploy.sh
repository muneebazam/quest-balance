#!/bin/bash

echo "Creating deployment package..."
mkdir deployment
cp quest_balance_controller.py deployment/
cp quest_balance_calculator.py deployment/
cd deployment

echo "Deploying questBalance lambda functions..."
pip install requests --target .
zip -r package.zip .
aws lambda update-function-code --function-name quest-balance --region us-east-1 --zip-file fileb://package.zip

echo "Done"
