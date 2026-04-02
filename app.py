import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Bull-Investor Dashboard")

# --- SENIOR ANALYST DESK ---
st.sidebar.header("🤵 Senior Analyst's Office")
total_capital = st.sidebar.number_input("Total Capital (Ksh)", value=100000)

NSE_TICKERS = ["SCOM.KE", "EQTY.KE", "KCB.KE", "EABL.KE", "COOP.KE", "ABSA.KE", "BAT.KE", "NCBA.KE", "SCBK.KE", "KEGN.KE"]

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty: return None
        
        # Calculate Indicators Manually (No extra libraries needed)
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        info = stock.info
        last_price = df['Close'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        yld = (info.get('dividendYield', 0) or 0) * 100
        
        return {
            "Ticker": ticker,
            "Name": info.get('shortName', ticker),
            "Price": round(last_price, 2),
            "SMA_50": round(sma_50, 2),
            "Yield": round(yld, 2),
            "Status": "🟢 BULLISH" if last_price > sma_50 else "🔴 BEARISH"
        }
    except:
        return None

# --- EXECUTION ---
with st.spinner('Scanning the Nairobi Exchange...'):
    results = []
    for t in NSE_TICKERS:
        res = get_data(t)
        if res: results.append(res)
    
    df_results = pd.DataFrame(results)

# 1. Market Table
st.header("📊 Market Intelligence")
st.table(df_results)

# 2. Portfolio Calculator
st.header("🧮 Buy-Order Calculator")
bullish_stocks = df_results[df_results['Status'] == "🟢 BULLISH"]

if not bullish_stocks.empty:
    selected = st.multiselect("Select your 'Bull' stocks:", bullish_stocks['Ticker'].tolist(), default=bullish_stocks['Ticker'].tolist()[:2])
    
    if selected:
        budget_per = total_capital / len(selected)
        cols = st.columns(len(selected))
        
        for i, s_ticker in enumerate(selected):
            row = bullish_stocks[bullish_stocks['Ticker'] == s_ticker].iloc[0]
            # Shares = Budget / (Price + 2.1% fees)
            shares = int(budget_per / (row['Price'] * 1.021))
            with cols[i]:
                st.metric(label=f"BUY {s_ticker}", value=f"{shares:,} Shares")
                st.caption(f"Est. Cost: Ksh {int(shares * row['Price'] * 1.021):,}")
else:
    st.warning("No stocks are currently in a Bullish trend. Keep your cash in the bank.")

st.divider()
st.info("💡 **Pro-Tip:** Focus on stocks where Price is > SMA_50 and Yield is > 7%.")
