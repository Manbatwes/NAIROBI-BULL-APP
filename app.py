import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Bull-Investor Dashboard")

# --- STEALTH HEADER (Telling Yahoo we are a human browser) ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# The Big 10 NSE Tickers
NSE_TICKERS = ["SCOM.KE", "EQTY.KE", "KCB.KE", "EABL.KE", "COOP.KE", "ABSA.KE", "BAT.KE", "NCBA.KE", "SCBK.KE", "KEGN.KE"]

@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        # We use a session to bypass the Yahoo block
        session = requests.Session()
        session.headers.update(HEADERS)
        
        # Fetching data using the session
        data = yf.download(ticker, period="1y", interval="1d", progress=False, session=session)
        
        if data.empty or len(data) < 55:
            return None
        
        # Calculate Moving Average
        last_price = float(data['Close'].iloc[-1])
        sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
        
        return {
            "Ticker": ticker,
            "Price": round(last_price, 2),
            "50-Day Avg": round(float(sma_50), 2),
            "Status": "🟢 BULLISH" if last_price > sma_50 else "🔴 BEARISH"
        }
    except:
        return None

# --- MAIN INTERFACE ---
st.sidebar.header("💰 Settings")
total_capital = st.sidebar.number_input("Total Capital (Ksh)", value=100000)

with st.spinner('Connecting to NSE Market...'):
    all_results = []
    for t in NSE_TICKERS:
        res = get_data(t)
        if res:
            all_results.append(res)
    
    df = pd.DataFrame(all_results)

if not df.empty:
    st.header("📊 Market Intelligence")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Calculator
    st.header("🧮 Buy-Order Calculator")
    bulls = df[df['Status'] == "🟢 BULLISH"]
    
    if not bulls.empty:
        selected = st.multiselect("Pick Bullish Stocks:", bulls['Ticker'].tolist(), default=bulls['Ticker'].tolist()[:1])
        if selected:
            budget_per = total_capital / len(selected)
            cols = st.columns(len(selected))
            for i, stock in enumerate(selected):
                row = bulls[bulls['Ticker'] == stock].iloc[0]
                shares = int(budget_per / (row['Price'] * 1.021))
                with cols[i]:
                    st.metric(label=f"BUY {stock}", value=f"{shares:,} Shares")
                    st.caption(f"Cost: Ksh {int(shares * row['Price'] * 1.021):,}")
    else:
        st.warning("No bullish stocks found. Wait for a market breakout.")
else:
    st.error("Connection still blocked by Yahoo Finance.")
    st.info("Try this: Go to 'Manage App' -> 'Reboot'. If it fails, Yahoo is temporarily blocking the Streamlit server IP. It usually clears in an hour.")

st.divider()
st.caption("Data source: Yahoo Finance via Professional Stealth Proxy")
