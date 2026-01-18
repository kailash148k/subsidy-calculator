import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Manufacturing DPR - Sales Engine", layout="wide")
st.title("🏦 Manufacturing P&L and Balance Sheet Engine")

# --- 1. DETAILED DATA INPUT AREA ---
with st.sidebar:
    st.header("🏢 Project Cost & Funding")
    capex_investment = st.number_input("Total CAPEX (Machinery, etc.)", value=4000000)
    working_capital_margin = st.number_input("Working Capital Requirement", value=1000000)
    total_project_cost = capex_investment + working_capital_margin
    
    own_contribution_pct = st.number_input("Own Contribution (%)", value=25.0)
    own_capital_amt = total_project_cost * (own_contribution_pct / 100)
    term_loan_amt = total_project_cost - own_capital_amt

    st.header("📈 Sales & Production Engine")
    unit_type = st.selectbox("Unit of Measurement", ["KG", "Metric Ton (MT)", "Numbers (Nos)", "Units"])
    max_capacity = st.number_input(f"Max Annual Production Capacity ({unit_type})", value=50000)
    
    # 4th Ask: Sales projection Unit x Rate
    sale_price_per_unit = st.number_input(f"Selling Price per {unit_type} (₹)", value=200)
    annual_growth_pct = st.number_input("Annual Sales Growth (%)", value=10.0) / 100
    util_yr1 = st.number_input("Year 1 Capacity Utilization (%)", value=50.0) / 100

    st.header("💳 Term Loan Details")
    term_rate = st.number_input("Term Loan Rate (%)", value=10.5) / 100
    term_tenure_months = st.number_input("Tenure (Months)", value=84)
    moratorium_period = st.number_input("Moratorium (Months)", value=6)
    
    st.header("🏦 Working Capital (CC)")
    cc_limit = st.number_input("CC Limit Amount", value=500000)
    cc_rate = st.number_input("CC Rate (%)", value=11.5) / 100
    cc_utilization = st.number_input("Avg. CC Utilization (%)", value=70.0) / 100

# --- 2. CALCULATION ENGINE (7 YEARS) ---
years = [f"Year {i}" for i in range(1, 8)]
pl_data = []
bs_data = []

# Loan Repayment Logic
repayment_months = term_tenure_months - moratorium_period
annual_principal_repay = term_loan_amt / (repayment_months / 12) if repayment_months > 0 else 0
curr_term_loan = term_loan_amt

for i in range(7):
    # --- P&L: SALES CALCULATION (Module 4) ---
    # Capacity increases by 5% yearly or stays at 95% cap
    util = min(0.95, util_yr1 + (i * 0.05)) 
    current_year_units = max_capacity * util
    
    # Revenue = Units x Price x Growth
    current_price = sale_price_per_unit * (1 + annual_growth_pct)**i
    total_sales_revenue = current_year_units * current_price
    
    # Basic Expenses (To be expanded in next steps)
    rm_cost = total_sales_revenue * 0.55 # Placeholder 55%
    other_exp = 500000 * (1.07**i)
    
    ebitda = total_sales_revenue - rm_cost - other_exp
    depreciation = capex_investment * 0.10
    
    interest_term = curr_term_loan * term_rate
    interest_cc = (cc_limit * cc_utilization) * cc_rate
    total_interest = interest_term + interest_cc
    
    pbt = ebitda - depreciation - total_interest
    tax = max(0, pbt * 0.25)
    pat = pbt - tax
    
    pl_data.append({
        "Particulars": years[i], 
        "Capacity Utilization (%)": util * 100,
        "Production Units": current_year_units,
        "Selling Price": current_price,
        "Gross Sales Revenue": total_sales_revenue, 
        "EBITDA": ebitda, "Interest": total_interest, "PAT": pat
    })

    # --- BALANCE SHEET ---
    stock = (rm_cost / 365) * 30 
    debtors = (total_sales_revenue / 365) * 45 
    curr_assets = stock + debtors + (pat * 0.05)
    net_fixed_assets = max(0, capex_investment - (depreciation * (i+1)))
    
    creditors = (rm_cost / 365) * 30
    cpltd = annual_principal_repay if i >= (moratorium_period/12) else 0
    curr_liab = creditors + cpltd + (cc_limit * cc_utilization)
    
    if i >= (moratorium_period/12):
        curr_term_loan -= annual_principal_repay
        
    bs_data.append({
        "Year": years[i], "Net Fixed Assets": net_fixed_assets,
        "Current Assets": curr_assets, "Total Assets": net_fixed_assets + curr_assets,
        "Net Worth": own_capital_amt + (pat * (i+1)), 
        "Term Loan": max(0, curr_term_loan), "Current Liabilities": curr_liab
    })

# --- 3. TABBED DISPLAY (LOCKED FORMAT) ---
df_pl = pd.DataFrame(pl_data).set_index("Particulars").transpose()
df_bs = pd.DataFrame(bs_data).set_index("Year").transpose()

tab1, tab2, tab3 = st.tabs(["📊 Profit & Loss Account", "⚖️ Balance Sheet", "📈 Ratio Analysis"])

with tab1:
    st.subheader("Sales & Production Detailed P&L")
    st.dataframe(df_pl.style.format("₹{:,.0f}"), use_container_width=True)

with tab2:
    st.dataframe(df_bs.style.format("₹{:,.0f}"), use_container_width=True)

with tab3:
    ratios = pd.DataFrame({
        "Year": years,
        "DSCR": [(df_pl.loc["PAT", y] + depreciation + df_pl.loc["Interest", y]) / 
                 (annual_principal_repay + df_pl.loc["Interest", y]) for y in years]
    }).set_index("Year").transpose()
    st.dataframe(ratios.style.format("{:.2f}"), use_container_width=True)
