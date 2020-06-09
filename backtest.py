import yfinance as yf
import datetime as dt
import pandas as pd
import numpy as np
import copy


def CAGR(df):
    # CAGR = annualised return
    df1 = df.copy()
    df1["cum_return"] = (1 + df1["daily_ret"]).cumprod()
    n = len(df1) / 252
    CAGR = (df1["cum_return"][-1]) ** (1 / n) - 1
    return CAGR


def volatility(df):
    # annualised volatility
    df1 = df.copy()
    vol = df1["daily_ret"].std() * np.sqrt(252)
    return vol


def sharpe(df, rf):
    # Sharpe ratio
    df1 = df.copy()
    sr = (CAGR(df1) - rf) / volatility(df1)
    return sr


def max_dd(df):
    # Maximum drawdown & Calmar Ratio
    df1 = df.copy()
    df1["cum_return"] = (1 + df["daily_ret"]).cumprod()
    df1["cum_roll_max"] = df1["cum_return"].cummax()
    df1["drawdown"] = df1["cum_roll_max"] - df1["cum_return"]
    df1["drawdown_pct"] = df1["drawdown"] / df1["cum_roll_max"]
    max_dd = df1["drawdown_pct"].max()
    return max_dd


# asx200 constituents as of 2015 (5 years ago) to eliminate survivorship bias
tickers = ["CBA.AX", "WBC.AX", "BHP.AX", "ANZ.AX", "NAB.AX", "TLS.AX", "WES.AX", "CSL.AX", "WOW.AX", "WPL.AX",\
           "MQG.AX", "RIO.AX", "SCG.AX", "TCL.AX", "QBE.AX", "AMP.AX", "BXB.AX", "SUN.AX"]

# start time = today - 10 years, end time =  today
start = dt.datetime.today() - dt.timedelta(1825)
end = dt.datetime.today()

# ticker ohlc monthly prices
ohlc_daily = {}
for i in tickers:
    ohlc_daily[i] = yf.download(i, start, end)

# check for nan values
# for i in ohlc_daily:
# print(ohlc_daily[i].isnull().values.any())

# in case of nan values, need to backfill
# ohlc_daily.fillna(method = "bfill", inplace = True)

# redefine tickers variables as keys - needed if you drop the tickers that
# aren't suitable (can use try function when adding info to tickers)
# tickers = ohlc_daily.keys()

ohlc_XJO = yf.download("^AXJO", start, end)
ohlc_XJO["daily_ret"] = ohlc_XJO["Adj Close"].pct_change()
print("ASX200 CAGR:", CAGR(ohlc_XJO))
print("ASX200 Sharpe Ratio:", sharpe(ohlc_XJO, 0.02))
print("ASX200 Max Drawdown:", max_dd(ohlc_XJO))

ohlc_dict = copy.deepcopy(ohlc_daily)
stock_returns = pd.DataFrame()
for ticker in tickers:
    # print("Calculating daily return for", ticker)
    ohlc_dict[ticker]["daily_ret"] = ohlc_dict[ticker]["Adj Close"].pct_change()
    stock_returns[ticker] = ohlc_dict[ticker]["daily_ret"]

# rebalanced every day, sell worst x buy best y
# i = 1
# y = 2
# x = 10
# df = stock_returns
portfolio = ["CBA.AX", "WBC.AX", "BHP.AX", "ANZ.AX", "NAB.AX", "TLS.AX",\
             "WES.AX", "CSL.AX", "WOW.AX", "WPL.AX"]


# backtesting using a momentum-based daily-rebalanced trading strategy
def back_test_mdr(df, x, y):
    # bt_df = df.copy()
    portfolio = ["CBA.AX", "WBC.AX", "BHP.AX", "ANZ.AX", "NAB.AX", "TLS.AX",\
             "WES.AX", "CSL.AX", "WOW.AX", "WPL.AX"]
    daily_ret = [0]
    for i in range(1, len(df)):
        if len(portfolio) > 0:
            # looks at a row i (i.e. returns for a day) and stores the mean
            daily_ret.append(df[portfolio].iloc[i, :].mean())
            worst_performers = df[portfolio].iloc[i, :].sort_values(ascending=True)[:y].index
            portfolio = [i for i in portfolio if i not in worst_performers]
        best_performers = df[[i for i in tickers if i not in portfolio]].iloc[i, :].sort_values(ascending=True)[x - y:]\
            .index
        portfolio.extend(best_performers)
    daily_ret_df = pd.DataFrame(np.array(daily_ret), columns=["daily_ret"], index=stock_returns.index)
    return daily_ret_df


BT_MDR1 = back_test_mdr(stock_returns, 10, 2)
print("BT_MDR1 CAGR:", CAGR(BT_MDR1))
print("BT_MDR1 Sharpe Ratio:", sharpe(BT_MDR1, 0.02))
print("BT_MDR1 Max Drawdown:", max_dd(BT_MDR1))

BT_MDR2 = back_test_mdr(stock_returns, 8, 2)
print("BT_MDR2 CAGR:", CAGR(BT_MDR2))
print("BT_MDR2 Sharpe Ratio:", sharpe(BT_MDR2, 0.02))
print("BT_MDR2 Max Drawdown:", max_dd(BT_MDR2))

BT_MDR3 = back_test_mdr(stock_returns, 5, 2)
print("BT_MDR3 CAGR:", CAGR(BT_MDR3))
print("BT_MDR3 Sharpe Ratio:", sharpe(BT_MDR3, 0.02))
print("BT_MDR3 Max Drawdown:", max_dd(BT_MDR3))