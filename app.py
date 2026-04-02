import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Bull-Investor Dashboard")

# --- PROFESSIONAL GUIDANCE ---
st.sidebar.header("🤵 Analyst Desk")
total_capital = st.sidebar.number_input("Total Capital (Ksh)", value=100000)

if st.sidebar.button('🔄 Force Market Refresh'):
    st.cache_data.clear()
    st.rerun()

# We try two different suffixes for Nairobi to bypass blocks
TICKERS = {
    "Safaricom": ["SCOM.NR", "SCOM.KE"],
    "Equity Bank": ["EQTY.NR", "EQTY.KE"],
    "KCB Group": ["KCB.NR", "KCB.KE"],
    "EABL": ["EABL.NR", "EABL.KE"],
    "Co-op Bank": ["COOP.NR", "COOP.KE"],
    "Absa Bank": ["ABSA.NR", "ABSA.KE"],
    "BAT Kenya": ["BAT.NR", "BAT.KE"],
    "NCBA Group": ["NCBA.NR", "NCBA.KE"],
    "StanChart": ["SCBK.NR", "SCBK.KE"],
    "KenGen": ["KEGN.NR", "KEGN.KE"]
}

@st.cache_data(ttl=600) # Cache for 10 minutes
def fetch_stock_data(name, variants):
    for ticker in variants:
        try:
            # We fetch a very small amount of data first to see if it's blocked
            data = yf.download(ticker, period="1y", interval="1d", progress=False, timeout=10)
            if not data.empty and len(data) > 50:
                last_price = float(data['Close'].iloc[-1])
                sma_50 = float(data['Close'].rolling(window=50).mean().iloc[-1])
                return {
                    "Company": name,
                    "Ticker": ticker,
                    "Price": round(last_price, 2),
                    "50-Day Avg": round(sma_50, 2),
                    "Status": "🟢 BULLISH" if last_price > sma_50 else "🔴 BEARISH"
                }
        except:
            continue
    return None

# --- MAIN ENGINE ---
st.header("📊 Market Intelligence")

with st.spinner('Probing the Exchange for live prices...'):
    results = []
    # Fetching one by one with a tiny delay to look "Human"
    for name, variants in TICKERS.items():
        res = fetch_stock_data(name, variants)
        if res:
            results.append(res)
        time.sleep(0.5) # The "Human" pause

if results:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # CALCULATOR
    st.header("🧮 Buy-Order Calculator")
    bulls = df[df['Status'] == "🟢 BULLISH"]
    
    if not bulls.empty:
        selected = st.multiselect("Select your Bullish entries:", bulls['Company'].tolist(), default=bulls['Company'].tolist()[:1])
        if selected:
            budget_per = total_capital / len(selected)
            cols = st.columns(len(selected))
            for i, comp_name in enumerate(selected):
                row = bulls[bulls['Company'] == comp_name].iloc[0]
                # Price + 2.1% fees
                shares = int(budget_per / (row['Price'] * 1.021))
                with cols[i]:
                    st.metric(label=f"BUY {comp_name}", value=f"{shares:,} Shares")
                    st.caption(f"Ksh {int(shares * row['Price'] * 1.021):,}")
    else:
        st.warning("Strategy Note: The market is currently in a 'Wait and See' mode. No Bullish breakouts detected.")
else:
    st.error("⚠️ Yahoo Finance is heavily throttling the connection.")
    st.info("Because the Nairobi Exchange is a smaller market, Yahoo's data feed can be unstable on cloud servers. If you see this, wait 10 minutes and click 'Force Market Refresh' in the sidebar.")

st.divider()
st.caption("Strategic Analysis: 50-Day Moving Average Crossover Strategy")
