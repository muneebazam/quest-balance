# Quest Balance

This repository features a collection of lambda functions which fetch stock position & market data from Questrade's API and calculates percentage gains(losses) to provide a daily summary via Slack. 

<br/>

## Setup

1. Install Python 3 **(Python 2 will not work)**

```
brew install python3
```

2. Clone Repository and Download Dependencies

```
git clone https://github.com/muneebazam/quest-balance.git
pip install -r requirements.txt
```

3. Set Environment Variables

```
export SLACK_TOKEN=<slack_token>
export SLACK_CHANNEL=<slack_channel>
export DYNAMO_TABLE=<dynamo_table_name>
```

<br/>

## Usage

To run the lambda function locally:

```
python quest_balance_controller.py
```

## Deployment

The `deploy.sh` script will package the source files and dependencies and upload the zip to AWS.
