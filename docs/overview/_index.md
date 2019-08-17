---
title : Execution Overview
description : High level overview of the implementation and execution flow.
weight : 1
---

## Implementation 

The service features both a controller file which acts as the entrypoint whenever the Lambda function is invoked as well as a calculator file which receives JSON data from Questrades' API and calculates balances & creates the summary text to be sent via Slack. The entire pipeline is written in Python (v3.6).

## Execution Flow

The following is a high level list of chronoical events that occur when the lambda function is invoked: 

1. Refresh token and API url are fetched from **Dynamo**

2. Access token is obtained from Questrade API

3. Requests sent to Balance/Position endpoints of Questrade API

4. Percentage Changes are calculated and summary message is constructed.

5. Summary message is sent to Slack. 
