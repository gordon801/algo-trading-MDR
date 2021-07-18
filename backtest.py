import yfinance as yf
import datetime as dt
import pandas as pd
import numpy as np
import copy

### Inputs ###
# Import returns data
returns_data = pd.read_csv(r'02 - Returns/Returns_20210718.csv')
returns_data.drop(index=returns_data.index[0], axis=0, inplace=True)  # drop Nans in first row

# Variables
r_f = 0.02  # set rf = 2% (10Y Aus T.Bond yield mostly in the 1-2% band between 2019 to 2021)
n_days = 252  # average number of trading days in a year
dec_pts = 2  # decimal point rounding
port_size = 10  # size of investment portfolio


### Function definitions ###
def perc_conv(decimal):  # convert decimal to percentage with given decimal places
    perc = round(decimal * 100, dec_pts)
    return f'{perc}%'


def CAGR(df):  # CAGR = annualised return
    df1 = df.copy()
    df1["cum_return"] = (1 + df1[df1.columns[0]]).cumprod()
    n = len(df1) / 252
    CAGR = (df1["cum_return"].iloc[-1]) ** (1 / n) - 1
    return CAGR


def volatility(df):  # annualised volatility
    df1 = df.copy()
    vol = df1[df1.columns[0]].std() * np.sqrt(252)
    return vol


def sharpe(df, rf):  # Sharpe ratio
    df1 = df.copy()
    sr = (CAGR(df1) - rf) / volatility(df1)
    return sr


def max_dd(df):  # Maximum drawdown
    df1 = df.copy()
    df1["cum_return"] = (1 + df1[df1.columns[0]]).cumprod()
    df1["cum_roll_max"] = df1["cum_return"].cummax()
    df1["drawdown"] = df1["cum_roll_max"] - df1["cum_return"]
    df1["drawdown_pct"] = df1["drawdown"] / df1["cum_roll_max"]
    max_dd = df1["drawdown_pct"].max()
    return max_dd


def return_stats(df):
    df1 = df.copy()
    df_name = df.columns[0]
    print(f"{df_name} CAGR:", perc_conv(CAGR(df1)))
    print(f"{df_name} Sharpe Ratio:", perc_conv(sharpe(df1, r_f)))
    print(f"{df_name} Max Drawdown:", perc_conv(max_dd(df1)))

### Data setup ###
# stock universe = asx200 constituents as of 2015 (5 years ago) to eliminate survivorship bias
stock_univ = list(i for i in returns_data.columns if i not in ['Date', '^AXJO'])

# initial portfolio = top X stock weights (stock_univ is ordered)
portfolio = stock_univ[0:port_size]

# return statistics will be compared to our benchmark of ASX200
df_AXJO = pd.DataFrame(returns_data['^AXJO'])

### Backtesting strategy ###
# Backtesting our momentum-based daily-rebalanced trading strategy
# MDR_N = rebalanced every day, sell worst performing x stocks in portfolio and buy best performing x stocks outside portfolio
# Assume equal weights in all stocks in portfolio
def back_test_mdr(df, x):
    # bt_df = df.copy()
    daily_ret = []
    curr_portfolio = portfolio
    for i in range(0, len(df)):
        # looks at a row i (i.e. returns for a day) and stores the mean
        daily_ret.append(df[curr_portfolio].iloc[i, :].mean())
        worst_performers = df[curr_portfolio].iloc[i, :].sort_values(ascending=True)[:x].index
        curr_portfolio = [i for i in curr_portfolio if i not in worst_performers]
        best_performers = df[[i for i in stock_univ if i not in curr_portfolio]].iloc[i, :].sort_values(ascending=False)[:x].index
        curr_portfolio.extend(best_performers)
    daily_ret_df = pd.DataFrame(np.array(daily_ret), columns=[f"MDR_{x}"], index=returns_data.index)
    return daily_ret_df


### Backtesting results ###
return_stats(df_AXJO)

BT_MDR1 = back_test_mdr(returns_data, 2)
return_stats(BT_MDR1)

BT_MDR2 = back_test_mdr(returns_data, 4)
return_stats(BT_MDR2)

BT_MDR3 = back_test_mdr(returns_data, 6)
return_stats(BT_MDR3)

BT_MDR4 = back_test_mdr(returns_data, 8)
return_stats(BT_MDR4)

BT_MDR5 = back_test_mdr(returns_data, 10)
return_stats(BT_MDR5)