"""
Quest Balance Controller
"""

import os
import logging
import urllib
import json
import boto3
import requests
from quest_balance_calculator import calculate_balances
from quest_balance_calculator import calculate_positions
from quest_balance_calculator import total_balances

# Grab the environment variables.
SLACK_TOKEN  = os.environ["SLACK_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
DYNAMO_TABLE = os.environ["DYNAMO_TABLE"]

# Define the URL of the targeted Slack API resource.
SLACK_URL = "https://slack.com/api/chat.postMessage"
QUESTRADE_URL = "https://login.questrade.com/oauth2/token"

def controller(data, context):
    
    # Configure logger 
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Retrieve entries from DynamoDB
    dynamodb = boto3.client('dynamodb')
    entry = dynamodb.get_item(TableName='questBalance', Key={'account_id':{'S':'01'}})['Item']
    api_url = entry['api_url']['S']
    refresh_token = entry['refresh_token']['S']
    tfsa_id = entry['tfsa_id']['N']
    margin_id = entry['margin_id']['N']

    payload={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.get(QUESTRADE_URL, payload)
    response = json.loads(r.text)
    new_url = response["api_server"]
    new_token = response["refresh_token"]
    access_token = response["access_token"]

    MARGIN_URL = "{}v1/accounts/{}/".format(new_url, margin_id)
    TFSA_URL = "{}v1/accounts/{}/".format(new_url, tfsa_id)

    dynamodb.update_item(TableName='questBalance', Key={'account_id':{'S':'01'}}, AttributeUpdates={"api_url":{"Action":"PUT","Value":{"S":new_url}}, "refresh_token":{"Action":"PUT","Value":{"S":new_token}}})

    r = requests.get("{}balances".format(MARGIN_URL), headers={'Authorization': "bearer {}".format(access_token)})
    margin_balances = json.loads(r.text)

    r = requests.get("{}balances".format(TFSA_URL), headers={'Authorization': "bearer {}".format(access_token)})
    tfsa_balances = json.loads(r.text)

    r = requests.get("{}positions".format(MARGIN_URL), headers={'Authorization': "bearer {}".format(access_token)})
    margin_positions = json.loads(r.text)

    r = requests.get("{}positions".format(TFSA_URL), headers={'Authorization': "bearer {}".format(access_token)})
    tfsa_positions = json.loads(r.text)

    # calculate balances
    response_text = []
    response_text.append("*Margin Account Balances*\n")
    response_text.append(calculate_balances(margin_balances))
    response_text.append("\n*TFSA Account Balances*\n")
    response_text.append(calculate_balances(tfsa_balances))
    response_text.append("\n*Total Account Balances*\n")
    response_text.append(total_balances(margin_balances, tfsa_balances))
    
    payload={
        "token": SLACK_TOKEN, 
        "channel": SLACK_CHANNEL,
        "text": ''.join(response_text)
    }
    r = requests.post(SLACK_URL, params=payload)

    response_text = []
    response_text.append("*Open Positions*\n")
    response_text.append(calculate_positions(margin_positions))
    response_text.append(calculate_positions(tfsa_positions))

    payload={
        "token": SLACK_TOKEN, 
        "channel": SLACK_CHANNEL,
        "text": ''.join(response_text)
    }

    r = requests.post(SLACK_URL, params=payload)
    logging.info("Successfully sent dialog payload to slack.")

    return 200