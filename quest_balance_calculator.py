"""
Quest Balance Calculator
"""

# Calculates total balance from margin and TFSA accounts 
def total_balances(margin_balance, tfsa_balance):

    # Extract combined balance data (USD & CAD) 
    margin = margin_balance["combinedBalances"][0]
    tfsa = tfsa_balance["combinedBalances"][0]

    # Extract and round dollar figures to nearest tenth 
    equity = round(tfsa["totalEquity"] + margin["totalEquity"], 2)
    marketValue = round(tfsa["marketValue"] + margin["marketValue"], 2)
    cash = round(tfsa["cash"] + margin["cash"], 2)

    # Construct balance message
    balances = []
    balances.append("Total Equity: _${}_\n".format(equity))
    balances.append("Market Value: _${}_\n".format(marketValue))
    balances.append("Cash: _${}_\n".format(cash))
    return ''.join(balances)

# Calculates balance information for specific account
def calculate_balances(balances):

    combinedBalances = balances["combinedBalances"][0]
    balances = []
    balances.append("Total Equity: _${}_\n".format(round(combinedBalances["totalEquity"], 2)))
    balances.append("Market Value: _${}_\n".format(round(combinedBalances["marketValue"], 2)))
    balances.append("Cash: _${}_\n".format(round(combinedBalances["cash"], 2)))
    return ''.join(balances)

# Calculates position information for specific account
def calculate_positions(positions):

    # loop through each open position in portfolio
    position_info = []
    for position in positions["positions"]:

        # round P&L values to nearest tenth
        openPnl = round(position["openPnl"], 2)
        dayPnl = round(position["dayPnl"], 2)

        # Add Open P&L value to message
        symbol = position["symbol"]
        position_info.append("{}: ".format(symbol))
        if (openPnl > 0):
            position_info.append("+")
        position_info.append("_{}_  ".format(openPnl))

        # Calculate % gain(loss) from Purchase/Market values
        marketVal = position["currentMarketValue"]
        purchaseVal = position["totalCost"]
        percentChange = (((marketVal / purchaseVal) - 1) * 100)
        if (percentChange > 0):
            position_info.append("+")
        position_info.append("_{}%_  (".format(round(percentChange, 2)))

        # Add Day P&L value to the message 
        if (dayPnl > 0):
            position_info.append("+")
        position_info.append("_{} Day_)\n".format(dayPnl))

    return ''.join(position_info)