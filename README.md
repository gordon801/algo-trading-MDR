# Momentum-based Daily-Rebalancing Trading
This project was done as a proof-of-concept for an algorithmic trading strategy. The strategy employed is a Momentum-based Daily-Rebalancing (MDR) strategy which is backtested against a buy-and-hold of the ASX 200 (benchmark). Primary metrics for comparison include annualised return, Sharpe ratio, and maximum drawdown. Analysis was done over the time period 2015-06-03 to 2021-07-18.

## Strategy
A Momentum-based strategy involves selling the worst-performing stocks within your portfolio and purchasing the best-performing stocks in the stock universe (outside your portfolio). A Daily-Rebalancing strategy implements this once a day.

## Components
The project consists of:
* Input folder (01 - Input): Stock weightings in the ASX 200 as of 2015-06-03 in .csv form.
* backtest_getdata.py: Parses the ASX 200 weightings csv file and outputs daily returns until the latest date for all chosen stocks into returns folder.
* Returns folder (02 - Returns): Daily returns of the chosen ASX 200 stocks in .csv form.
* backtest.py: Defines and produces the backtesting results.

## Assumptions
* No transaction costs.
* Stocks are purchased or sold at their daily closing prices.
* Our stock universe is arbitrarily chosen as the ~top 30 stocks (with >0.7% weighting) in the ASX 200.
* Our portfolio size is of 10 stocks, which each make up 10% of the portfolio's weighting.

## Results
A MDR portfolio significantly outperforms the ASX 200, and a MDR portfolio with a high level of rebalanced stocks (60-80%) appears to perform the best. 
