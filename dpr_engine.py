import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Professional CMA - Balanced Funding", layout="wide")
st.title("🏦 Full Manufacturing P&L and Balance Sheet Engine")

# --- 1. DATA INPUT AREA (REORDERED) ---
with st.sidebar:
    st.header("🏢 Project Cost & Funding")
    capex_inv = st.number_input("Total CAPEX (Machinery/Building)", value=4000000)
    wc_margin = st.number_input("Working Capital Margin", value=1000000)
    total_project_cost = capex_inv + wc_margin
    
    own_contribution_pct = st.number_input("Own Contribution (%)", value=25.0)
    own_capital_amt = total_project_cost * (own_contribution_pct / 100)
    
    st.header("💳 Term Loan Details")
    term_loan_amt = st.number_input("Term Loan Amount", value=3000000)
    term_rate = st.number_input("Term Loan Rate (%)", value=10.5) / 100
    term_tenure = st.number_input("Tenure (Months)", value=84)
    moratorium = st.number_input("Moratorium (Months)", value=6)
    
    st.header("🏦 Working Capital (CC)")
    cc_limit = st.number_input("CC Limit Amount", value=500000)
    cc_rate = st.number_input("CC Rate (%)", value=11.5) / 100
    cc_utilization = st.number_input("Avg. CC Utilization (%)", value=70.0) / 100

    # --- FUNDING VALIDATION LOGIC ---
    total_funding = own_capital_amt + term_loan_amt + cc_limit
    difference = total_project_cost - total_funding
    
    if abs(difference) > 1: # Allowance for minor rounding
        st.error(f"❌ Funding Mismatch! Total Project Cost (₹{total_project_cost:,.0f}) must equal Total Funding (₹{total_funding:,.0f}). Difference: ₹{difference:,.0f}")
        st.stop() # Prevents P&L generation if unbalanced
    else:
        st.success("✅ Funding Balanced")

    st.header("📈 Sales & Production Engine")
    max_capacity = st.number_input("Max Annual Capacity (Units)", value=50000)
    sale_price = st.number_input("Selling Price per Unit (₹)", value=200)
    growth_pct = st.number_input("Annual Sales Growth (%)", value=10.0) / 100
    util_yr1 = st.number_input("Year 1 Utilization (%)", value=50.0) / 100

# --- 2. CALCULATION ENGINE (7 YEARS) ---
years = [f"Year {i}" for i in range(1, 8)]
pl_data = []
bs_data = []

repay_months = term_tenure - moratorium
annual_prin_repay = term_loan_amt / (repay_months / 12) if repay_months > 0 else 0
curr_term_loan = term_loan_amt

for i in range(7):
    # P&L Logic
    util = min(0.95, (util_yr1) + (i * 0.05)) 
    current_units = max_capacity * util
    current_price = sale_price * (1 + growth_pct)**i
    revenue = current_units * current_price
    
    rm_cost = revenue * 0.55
    ebitda = revenue - rm_cost - (500000 * (1.07**i))
    depr = capex_inv * 0.10
    interest = (curr_term_loan * term_rate) + (cc_limit * cc_utilization * cc_rate)
    pbt = ebitda - depr - interest
    pat = pbt - (max(0, pbt * 0.25))
    
    pl_data.append({
        "Particulars": years[i], "Units": current_units, "Price": current_price,
        "Sales": revenue, "EBITDA": ebitda, "Interest": interest, "PAT": pat
    })

    # Balance Sheet Logic (Module 13 Bifurcation)
    stock = (rm_cost / 365) * 30
    debtors = (revenue / 365) * 45
    curr_assets = stock + debtors + (pat * 0.05)
    
    cpltd = annual_prin_repay if i >= (moratorium/12) else 0
    curr_liab = ((rm_cost / 365) * 30) + cpltd + (cc_limit * cc_utilization)
    
    if i >= (moratorium/12):
        curr_term_loan -= annual_prin_repay
        
    bs_data.append({
        "Year": years[i], "Fixed Assets": max(0, capex_inv - (depr*(i+1))),
        "Current Assets": curr_assets, "Total Assets": max(0, capex_inv - (depr*(i+1))) + curr_assets,
        "Net Worth": own_capital_amt + (pat * (i+1)), 
        "Long Term Loan": max(0, curr_term_loan), "Current Liabilities": curr_liab
    })

# --- 3. LOCKED FORMAT DISPLAY ---
df_pl = pd.DataFrame(pl_data).set_index("Particulars").transpose()
df_bs = pd.DataFrame(bs_data).set_index("Year").transpose()

t1, t2, t3 = st.tabs(["📊 Profit & Loss", "⚖️ Balance Sheet", "📈 Ratios"])
with t1: st.dataframe(df_pl.style.format("₹{:,.0f}"), use_container_width=True)
with t2: st.dataframe(df_bs.style.format("₹{:,.0f}"), use_container_width=True)
with t3:
    ratios = pd.DataFrame({
        "Year": years,
        "Current Ratio": [df_bs.loc["Current Assets", y] / df_bs.loc["Current Liabilities", y] for y in years],
        "DSCR": [(df_pl.loc["PAT", y] + depr + df_pl.loc["Interest", y]) / (annual_prin_repay + df_pl.loc["Interest", y]) for y in years]
    }).set_index("Year").transpose()
    st.dataframe(ratios.style.format("{:.2f}"), use_container_width=True)
