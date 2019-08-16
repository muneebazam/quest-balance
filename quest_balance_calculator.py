"""
Quest Balance Calculator
"""

import os
import logging
import urllib
import json

def total_balances(margin_balance, tfsa_balance):

    margin = margin_balance["combinedBalances"][0]
    tfsa = tfsa_balance["combinedBalances"][0]

    equity = round(tfsa["totalEquity"] + margin["totalEquity"], 2)
    marketValue = round(tfsa["marketValue"] + margin["marketValue"], 2)
    cash = round(tfsa["cash"] + margin["cash"], 2)
    balances = []
    balances.append("Total Equity: _${}_\n".format(equity))
    balances.append("Market Value: _${}_\n".format(marketValue))
    balances.append("Cash: _${}_\n".format(cash))
    return ''.join(balances)

def calculate_balances(balances):

    combinedBalances = balances["combinedBalances"][0]
    balances = []
    balances.append("Total Equity: _${}_\n".format(round(combinedBalances["totalEquity"], 2)))
    balances.append("Market Value: _${}_\n".format(round(combinedBalances["marketValue"], 2)))
    balances.append("Cash: _${}_\n".format(round(combinedBalances["cash"], 2)))
    return ''.join(balances)

def calculate_positions(positions):

    position_info = []
    for position in positions["positions"]:

        openPnl = round(position["openPnl"], 2)
        dayPnl = round(position["dayPnl"], 2)
        marketVal = position["currentMarketValue"]
        purchaseVal = position["totalCost"]
        symbol = position["symbol"]

        position_info.append("{}: ".format(symbol))
        if (openPnl > 0):
            position_info.append("+")
        position_info.append("_{}_  ".format(openPnl))

        percentChange = (((marketVal / purchaseVal) - 1) * 100)
        if (percentChange > 0):
            position_info.append("+")
        position_info.append("_{}%_  (".format(round(percentChange, 2)))

        if (dayPnl > 0):
            position_info.append("+")
        position_info.append("_{} Day_)\n".format(dayPnl))

    return ''.join(position_info)