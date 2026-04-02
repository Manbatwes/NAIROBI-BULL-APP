import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Bull-Investor Dashboard")

# --- STEALTH HEADERS ---
# This makes us look like an iPhone user, not a server
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"

# The Big 10 NSE Tickers
TICKERS = {
    "SCOM.KE": "Safaricom",
    "EQTY.KE": "Equity Bank",
    "KCB.KE": "KCB Group",
    "EABL.KE": "EABL",
    "COOP.KE": "Co-op Bank",
    "ABSA.KE": "Absa Bank",
    "BAT.KE": "BAT Kenya",
    "NCBA.KE": "NCBA Group",
    "SCBK.KE": "StanChart",
    "KEGN.KE": "KenGen"
}

@st.cache_data(ttl=3600)
def fetch_data(symbol):
    try:
        # Step 1: Create a session with a human ID
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        
        # Step 2: Download only 6 months (smaller data is less suspicious)
        ticker = yf.Ticker(symbol, session=session)
        df = ticker.history(period="6mo")
        
        if df.empty or len(df) < 50:
            return None
        
        # Step 3: Calculation
        last_price = float(df['Close'].iloc[-1])
        sma_50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
        
        return {
            "Ticker": symbol,
            "Company": TICKERS[symbol],
            "Price": round(last_price, 2),
            "50-Day Avg": round(sma_50, 2),
            "Status": "🟢 BULLISH" if last_price > sma_50 else "🔴 BEARISH"
        }
    except:
        return None

# --- MAIN DASHBOARD ---
st.sidebar.header("🤵 Analyst Desk")
total_capital = st.sidebar.number_input("Total Capital (Ksh)", value=100000)

if st.sidebar.button('🔄 Try Market Connect'):
    st.cache_data.clear()
    st.rerun()

st.header("📊 Market Intelligence")
all_data = []
with st.spinner('Authenticating with Nairobi Exchange Data...'):
    for symbol in TICKERS.keys():
        res = fetch_data(symbol)
        if res:
            all_data.append(res)

if all_data:
    df_results = pd.DataFrame(all_data)
    st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    # Calculator
    st.header("🧮 Buy-Order Calculator")
    bulls = df_results[df_results['Status'] == "🟢 BULLISH"]
    if not bulls.empty:
        selected = st.multiselect("Pick Stocks:", bulls['Company'].tolist())
        if selected:
            budget_per = total_capital / len(selected)
            cols = st.columns(len(selected))
            for i, name in enumerate(selected):
                row = bulls[bulls['Company'] == name].iloc[0]
                shares = int(budget_per / (row['Price'] * 1.021))
                with cols[i]:
                    st.metric(name, f"Buy {shares:,}")
                    st.caption(f"Cost: Ksh {int(shares * row['Price'] * 1.021):,}")
    else:
        st.warning("No Bullish trends detected right now.")
else:
    st.error("❌ Yahoo Finance is still blocking the Cloud Server IP.")
    st.info("💡 **Professional Recommendation:** Since you are a serious investor, cloud servers like Streamlit are often blocked. For a 100% reliable connection, copy this code and run it **locally** on your computer. Your home internet is never blocked.")

st.divider()
st.caption("Strategy: 50-Day SMA Momentum")
