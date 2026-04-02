import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- APP CONFIG ---
st.set_page_config(page_title="NSE Nairobi Bull-Investor Pro", layout="wide")
st.title("🇰🇪 NSE Nairobi: Professional Portfolio Architect")

# --- SIDEBAR: INVESTOR CONTROLS ---
st.sidebar.header("💰 Capital Management")
total_capital = st.sidebar.number_input("Total Capital to Invest (Ksh)", min_value=1000, value=100000, step=5000)
risk_per_stock = st.sidebar.slider("Max Allocation per Stock (%)", 10, 50, 25)
brokerage_fees = 0.021 # 2.1% standard NSE fees

st.sidebar.divider()
st.sidebar.markdown("""
**Analyst Desk Rule:**
"Never bet the whole shamba on one stock. By limiting allocation to 25%, 
even if one company fails, your portfolio survives to fight another day."
""")

# Key NSE Tickers
NSE_TICKERS = ["SCOM.KE", "EQTY.KE", "KCB.KE", "EABL.KE", "COOP.KE", "ABSA.KE", "BAT.KE", "NCBA.KE", "SCBK.KE", "KEGN.KE"]

@st.cache_data(ttl=3600) # Refresh data every hour
def fetch_nse_data(tickers):
    store = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1y")
            if df.empty: continue
            
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            last_price = df['Close'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            
            # Extract Yield
            info = t.info
            yld = (info.get('dividendYield', 0) or 0) * 100
            
            store.append({
                "Ticker": ticker,
                "Price": round(last_price, 2),
                "SMA_50": round(sma_50, 2),
                "Yield %": round(yld, 2),
                "Status": "BULLISH" if last_price > sma_50 else "BEARISH",
                "Name": info.get('shortName', ticker)
            })
        except:
            continue
    return pd.DataFrame(store)

# --- EXECUTION ---
data_df = fetch_nse_data(NSE_TICKERS)

# 1. Market Overview
st.header("🔭 Market Intelligence")
bulls_only = data_df[data_df['Status'] == "BULLISH"].sort_values(by="Yield %", ascending=False)
st.dataframe(data_df, use_container_width=True)

# 2. Portfolio Calculator
st.header("🧮 Buy-Order Calculator")
if not bulls_only.empty:
    st.write(f"Based on your **Ksh {total_capital:,}** capital, here are your 'Bull' entries:")
    
    selected_stocks = st.multiselect("Select stocks you want to buy now:", bulls_only['Ticker'].tolist(), default=bulls_only['Ticker'].tolist()[:3])
    
    if selected_stocks:
        calc_cols = st.columns(len(selected_stocks))
        budget_per_stock = (total_capital / len(selected_stocks))
        
        total_spent = 0
        
        for i, stock in enumerate(selected_stocks):
            row = bulls_only[bulls_only['Ticker'] == stock].iloc[0]
            price = row['Price']
            
            # Calculation logic: Budget minus fees, then divided by price
            net_budget = budget_per_stock / (1 + brokerage_fees)
            shares_to_buy = int(net_budget // price)
            total_cost = (shares_to_buy * price) * (1 + brokerage_fees)
            total_spent += total_cost
            
            with calc_cols[i]:
                st.metric(label=f"BUY {stock}", value=f"{shares_to_buy:,} Shares")
                st.write(f"**At Price:** Ksh {price}")
                st.write(f"**Est. Cost:** Ksh {total_cost:,.0f}")
                st.caption(f"Yielding {row['Yield %']}%")

        st.divider()
        st.subheader(f"Total Deployment: Ksh {total_spent:,.0f} / Remaining Cash: Ksh {total_capital - total_spent:,.0f}")
    else:
        st.warning("Select stocks above to see the share count calculation.")
else:
    st.error("The market is currently bearish. My professional advice: Sit on cash and wait for a green breakout.")

# --- PROFESSIONAL EXIT STRATEGY ---
st.header("🚪 The Exit Strategy (Sell Signals)")
st.markdown(f"""
| If this happens... | Action to Take |
| :--- | :--- |
| Price drops below **SMA 50** | **SELL IMMEDIATELY.** The bull run for that stock is over. |
| Portfolio gain hits **15%** | **SELL HALF.** Take your initial capital out, let the "house money" run. |
| Dividend is paid | **RE-EVALUATE.** Often the price drops after a dividend. If it stays above the SMA 50, keep holding. |
""")
