import streamlit as st
import yfinance as yf
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Bull-Investor Dashboard")

# --- SIDEBAR ---
st.sidebar.header("💰 Investment Settings")
total_capital = st.sidebar.number_input("Total Capital (Ksh)", value=100000, min_value=1000)

# The Big 10 NSE Tickers
NSE_TICKERS = ["SCOM.KE", "EQTY.KE", "KCB.KE", "EABL.KE", "COOP.KE", "ABSA.KE", "BAT.KE", "NCBA.KE", "SCBK.KE", "KEGN.KE"]

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Fetching a bit more data to ensure SMA_50 is calculated correctly
        df = stock.history(period="1y")
        if df is None or df.empty or len(df) < 50: 
            return None
        
        last_price = df['Close'].iloc[-1]
        sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        
        # Get dividend info safely
        info = stock.info
        name = info.get('shortName', ticker)
        yld = (info.get('dividendYield', 0) or 0) * 100
        
        return {
            "Ticker": ticker,
            "Name": name,
            "Price": round(last_price, 2),
            "SMA_50": round(sma_50, 2),
            "Yield %": round(yld, 2),
            "Status": "🟢 BULLISH" if last_price > sma_50 else "🔴 BEARISH"
        }
    except Exception as e:
        return None

# --- MAIN ENGINE ---
st.header("📊 Market Intelligence")

with st.spinner('Connecting to Nairobi Securities Exchange...'):
    all_data = []
    for t in NSE_TICKERS:
        res = get_data(t)
        if res:
            all_data.append(res)
    
    # Create DataFrame with guaranteed columns to prevent KeyError
    df_results = pd.DataFrame(all_data, columns=["Ticker", "Name", "Price", "SMA_50", "Yield %", "Status"])

if not df_results.empty:
    # Show the table
    st.dataframe(df_results, use_container_width=True)

    # --- PORTFOLIO CALCULATOR ---
    st.header("🧮 Buy-Order Calculator")
    
    # Filter for Bullish stocks
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
                # Shares calculation (Price + 2.1% brokerage fees)
                shares = int(budget_per / (row['Price'] * 1.021))
                with cols[i]:
                    st.metric(label=f"BUY {s_ticker}", value=f"{shares:,} Shares")
                    st.write(f"**Current Price:** Ksh {row['Price']}")
                    st.caption(f"Total Cost: Ksh {int(shares * row['Price'] * 1.021):,}")
    else:
        st.warning("⚠️ No stocks currently meet 'Bullish' criteria (Price > 50-Day Average). It is safer to hold cash right now.")
else:
    st.error("❌ Could not fetch market data. Please refresh the page or check if the market is open.")

st.divider()
st.info("💡 **Strategy:** Only buy when Status is 🟢 BULLISH. Sell when it turns 🔴 BEARISH.")
