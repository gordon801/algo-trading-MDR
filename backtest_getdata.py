import yfinance as yf
import datetime as dt
import pandas as pd

### Inputs ###
# Import data of ASX200 weightings (2015-06-03)
wts_2015 = pd.read_csv(r'01 - Input/20150603-asx200.csv')

# Set time and date for stocks data
start = dt.date(2015, 6, 3)  # same date as the ASX weightings
end = dt.date.today()

# weighting threshold for stocks
wt_threshold = 0.7  # pick stocks w/ >= 0.7% weighting in ASX200 (~top 30 stocks)

### Data Extraction ###
# Pull OHLC (open, high, low, closing figures) data for stocks meeting chosen weight threshold
sig_wts_2015 = wts_2015[wts_2015["Weighting (%)"] >= wt_threshold]

tickers = sig_wts_2015['Code'].tolist()
for i in range(len(tickers)):
    tickers[i] += '.AX'  # All ASX stock tickers on Yahoo finance end in .AX

tickers_olhc = {}
for ticker in tickers:
    tickers_olhc[ticker] = yf.download(ticker, start, end)

# Create dataframe of daily returns for tickers and XJO (ASX200)
tickers_returns = pd.DataFrame()
for ticker in tickers:
    tickers_olhc[ticker]["daily_ret"] = tickers_olhc[ticker]["Adj Close"].pct_change()
    tickers_returns[ticker] = tickers_olhc[ticker]["daily_ret"]

ohlc_XJO = yf.download("^AXJO", start, end)
ohlc_XJO["^AXJO"] = ohlc_XJO["Adj Close"].pct_change()
tickers_returns = tickers_returns.join(ohlc_XJO["^AXJO"])

# Export returns to csv
end_dt = str(end).replace("-","")
tickers_returns.to_csv(f'02 - Returns/Returns_{end_dt}.csv')