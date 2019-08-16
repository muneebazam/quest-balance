"""
Quest Balance Controller
"""

# import statements
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

# Lambda entry point
def controller(data, context):
    
    # Configure logger 
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Retrieve refresh token from DynamoDB
    dynamodb = boto3.client('dynamodb')
    entry = dynamodb.get_item(TableName='questBalance', Key={'account_id':{'S':'01'}})['Item']
    api_url = entry['api_url']['S']
    refresh_token = entry['refresh_token']['S']
    tfsa_id = entry['tfsa_id']['N']
    margin_id = entry['margin_id']['N']

    # Retreive access token from login endpoint 
    payload={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.get(QUESTRADE_URL, payload)
    response = json.loads(r.text)
    new_url = response["api_server"]
    new_token = response["refresh_token"]
    access_token = response["access_token"]

    # Construct base URLs for TFSA & Margin accounts 
    MARGIN_URL = "{}v1/accounts/{}/".format(new_url, margin_id)
    TFSA_URL = "{}v1/accounts/{}/".format(new_url, tfsa_id)

    # Store new refresh token in dynamo for future executions 
    dynamodb.update_item(TableName='questBalance', Key={'account_id':{'S':'01'}}, AttributeUpdates={"api_url":{"Action":"PUT","Value":{"S":new_url}}, "refresh_token":{"Action":"PUT","Value":{"S":new_token}}})
    response_text = []

    # Get account balance information for margin account
    balance_query_successful = True
    r = requests.get("{}balances".format(MARGIN_URL), headers={'Authorization': "bearer {}".format(access_token)})
    if (r.status_code != 200):
        logging.warning('unable to retreive account balance information for margin account')
        balance_query_successful = False
    else:
        margin_balances = json.loads(r.text)
        response_text.append("*Margin Account Balances*\n")
        response_text.append(calculate_balances(margin_balances))

    # Get account balance information for TFSA account
    r = requests.get("{}balances".format(TFSA_URL), headers={'Authorization': "bearer {}".format(access_token)})
    if (r.status_code != 200):
        logging.warning('unable to retreive account balance information for TFSA account')
        balance_query_successful = False
    else:
        tfsa_balances = json.loads(r.text)
        response_text.append("\n*TFSA Account Balances*\n")
        response_text.append(calculate_balances(tfsa_balances))

    # If both balance queries successful construct total balance message
    if (balance_query_successful):
        response_text.append("\n*Total Account Balances*\n")
        response_text.append(total_balances(margin_balances, tfsa_balances))

    # Send balance info message on Slack
    payload={
        "token": SLACK_TOKEN, 
        "channel": SLACK_CHANNEL,
        "text": ''.join(response_text)
    }
    r = requests.post(SLACK_URL, params=payload)

    # Get account position information for margin account 
    response_text = []
    response_text.append("*Open Positions*\n")
    r = requests.get("{}positions".format(MARGIN_URL), headers={'Authorization': "bearer {}".format(access_token)})
    if (r.status_code != 200):
        logging.warning('unable to retreive account position information for margin account')
    else:
        margin_positions = json.loads(r.text)
        response_text.append(calculate_positions(margin_positions))

    # Get account position information for TFSA account 
    r = requests.get("{}positions".format(TFSA_URL), headers={'Authorization': "bearer {}".format(access_token)})
    if (r.status_code != 200):
        logging.warning('unable to retreive account position information for TFSA account')
    else:
        tfsa_positions = json.loads(r.text)
        response_text.append(calculate_positions(tfsa_positions))

    # Send position info message on Slack
    payload={
        "token": SLACK_TOKEN, 
        "channel": SLACK_CHANNEL,
        "text": ''.join(response_text)
    }
    r = requests.post(SLACK_URL, params=payload)
    logging.info("Successfully sent dialog payload to slack.")
    return 200