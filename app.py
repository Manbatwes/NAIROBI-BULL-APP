import streamlit as st
import yfinance as yf
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Bull-Investor Dashboard")

# --- SIDEBAR ---
st.sidebar.header("💰 Investment Settings")
total_capital = st.sidebar.number_input("Total Capital (Ksh)", value=100000, min_value=1000)

# The Big 10 NSE Tickers (Most Liquid)
NSE_TICKERS = ["SCOM.KE", "EQTY.KE", "KCB.KE", "EABL.KE", "COOP.KE", "ABSA.KE", "BAT.KE", "NCBA.KE", "SCBK.KE", "KEGN.KE"]

# This "Cache" prevents Yahoo Finance from blocking your app
@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        # Use a longer period to ensure we get enough data for the 50-Day Average
        df = yf.download(ticker, period="2y", progress=False)
        
        if df.empty or len(df) < 55:
            return None
        
        # Calculate the 50-Day Moving Average
        # min_periods=1 ensures it works even if there are small gaps in data
        df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        
        last_price = float(df['Close'].iloc[-1])
        sma_50 = float(df['SMA_50'].iloc[-1])
        
        # Determine Status
        status = "🟢 BULLISH" if last_price > sma_50 else "🔴 BEARISH"
        
        return {
            "Ticker": ticker,
            "Price": round(last_price, 2),
            "50-Day Avg": round(sma_50, 2),
            "Status": status
        }
    except Exception as e:
        return None

# --- MAIN ENGINE ---
st.header("📊 Market Intelligence")

with st.spinner('Scanning Nairobi Securities Exchange...'):
    all_data = []
    for t in NSE_TICKERS:
        res = get_data(t)
        if res:
            all_data.append(res)
    
    df_results = pd.DataFrame(all_data)

if not df_results.empty:
    # Display results
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    # --- PORTFOLIO CALCULATOR ---
    st.header("🧮 Buy-Order Calculator")
    bullish_stocks = df_results[df_results['Status'] == "🟢 BULLISH"]

    if not bullish_stocks.empty:
        selected = st.multiselect(
            "Select 'Bullish' stocks to buy:", 
            bullish_stocks['Ticker'].tolist(), 
            default=bullish_stocks['Ticker'].tolist()[:1]
        )
        
        if selected:
            budget_per = total_capital / len(selected)
            cols = st.columns(len(selected))
            
            for i, s_ticker in enumerate(selected):
                row = bullish_stocks[bullish_stocks['Ticker'] == s_ticker].iloc[0]
                # Price + 2.1% brokerage fees
                shares = int(budget_per / (row['Price'] * 1.021))
                with cols[i]:
                    st.metric(label=f"BUY {s_ticker}", value=f"{shares:,} Shares")
                    st.write(f"**Price:** Ksh {row['Price']}")
                    st.caption(f"Cost: Ksh {int(shares * row['Price'] * 1.021):,}")
    else:
        st.warning("⚠️ No stocks are currently in a Bullish trend (Price > 50-Day Average). The safest place for your money right now is a Money Market Fund.")
else:
    st.error("❌ Data connection failed.")
    st.write("This can happen if the market provider is busy. Please click 'Manage App' -> 'Reboot' in 5 minutes.")

st.divider()
st.info("💡 **Professional Advice:** In the NSE, wait for the Bullish green signal. If a stock turns Red, sell to protect your capital.")
