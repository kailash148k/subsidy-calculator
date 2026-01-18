import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Professional CMA & Balance Sheet", layout="wide")
st.title("🏦 Full Manufacturing P&L and Balance Sheet Engine")

# --- 1. DETAILED DATA INPUT AREA ---
with st.sidebar:
    st.header("🏢 Project Cost Bifurcation")
    capex_investment = st.number_input("Total CAPEX (Machinery, Building, etc.)", value=4000000)
    working_capital_margin = st.number_input("Working Capital Requirement", value=1000000)
    total_project_cost = capex_investment + working_capital_margin
    st.info(f"Total Project Cost: ₹{total_project_cost:,.0f}")
    
    own_contribution_pct = st.number_input("Own Contribution (%)", value=25.0)
    own_capital_amt = total_project_cost * (own_contribution_pct / 100)
    
    st.header("💳 Term Loan Details")
    term_loan_amt = st.number_input("Term Loan Amount", value=3000000)
    term_rate = st.number_input("Term Loan Interest Rate (%)", value=10.5) / 100
    term_tenure_months = st.number_input("Tenure in Months (Total)", value=84)
    moratorium_period = st.number_input("Moratorium Period (Months)", value=6)
    
    st.header("🏦 Working Capital (CC) Details")
    cc_limit = st.number_input("CC Limit Amount", value=500000)
    cc_rate = st.number_input("CC Interest Rate (%)", value=11.5) / 100
    cc_utilization = st.number_input("Avg. CC Utilization (%)", value=70.0) / 100

    st.header("⚙️ Operations")
    max_annual_sales = st.number_input("Max Annual Sales Revenue (100% Capacity)", value=8000000)
    rm_cost_pct = st.number_input("Raw Material Cost (%)", value=55.0) / 100
    util_y1 = st.number_input("Year 1 Utilization (%)", value=60.0) / 100

# --- 2. CALCULATION ENGINE (7 YEARS) ---
years = [f"Year {i}" for i in range(1, 8)]
pl_data = []
bs_data = []

# Loan Repayment Calculation
repayment_months = term_tenure_months - moratorium_period
annual_principal_repay = term_loan_amt / (repayment_months / 12) if repayment_months > 0 else 0
curr_term_loan = term_loan_amt

for i in range(7):
    # --- P&L ACCOUNT ---
    util = min(0.95, util_y1 + (i * 0.05))
    sales = max_annual_sales * util * (1.08**i) # 8% Growth
    cogs = sales * rm_cost_pct
    fixed_overhead = 600000 * (1.07**i) # Salary/Rent/Admin
    
    ebitda = sales - cogs - fixed_overhead
    depreciation = capex_investment * 0.10 # 10% SLM
    
    # Interest Bifurcation
    interest_term = curr_term_loan * term_rate
    interest_cc = (cc_limit * cc_utilization) * cc_rate
    total_interest = interest_term + interest_cc
    
    pbt = ebitda - depreciation - total_interest
    tax = max(0, pbt * 0.25)
    pat = pbt - tax
    
    pl_data.append({
        "Particulars": years[i], "Gross Sales": sales, "Direct Expenses (RM)": cogs,
        "Operating Expenses": fixed_overhead, "EBITDA": ebitda, 
        "Interest (Term+CC)": total_interest, "Depreciation": depreciation, 
        "PBT": pbt, "Tax": tax, "PAT": pat
    })

    # --- BALANCE SHEET ---
    # Assets
    stock = (cogs / 365) * 30 
    debtors = (sales / 365) * 45 
    cash_bal = pat * 0.05
    curr_assets = stock + debtors + cash_bal
    net_fixed_assets = max(0, capex_investment - (depreciation * (i+1)))
    
    # Liabilities
    creditors = (cogs / 365) * 30
    # Current Portion of Long Term Debt (CPLTD) for Ratio calculation
    cpltd = annual_principal_repay if i >= (moratorium_period/12) else 0
    curr_liab = creditors + cpltd + (cc_limit * cc_utilization)
    
    if i >= (moratorium_period/12):
        curr_term_loan -= annual_principal_repay
        
    bs_data.append({
        "Year": years[i], "Net Fixed Assets": net_fixed_assets,
        "Current Assets": curr_assets, "Total Assets": net_fixed_assets + curr_assets,
        "Net Worth": own_capital_amt + (pat * (i+1)), 
        "Term Loan (Long Term)": max(0, curr_term_loan),
        "Current Liabilities": curr_liab, 
        "Total Liabilities": (own_capital_amt + (pat * (i+1))) + max(0, curr_term_loan) + curr_liab
    })

# --- 3. TABBED DISPLAY (LOCKED FORMAT) ---
df_pl = pd.DataFrame(pl_data).set_index("Particulars").transpose()
df_bs = pd.DataFrame(bs_data).set_index("Year").transpose()

tab1, tab2, tab3 = st.tabs(["📊 Profit & Loss Account", "⚖️ Balance Sheet", "📈 Ratio Analysis"])

with tab1:
    st.dataframe(df_pl.style.format("₹{:,.0f}"), use_container_width=True)

with tab2:
    st.dataframe(df_bs.style.format("₹{:,.0f}"), use_container_width=True)

with tab3:
    ratios = pd.DataFrame({
        "Year": years,
        "Current Ratio": [df_bs.loc["Current Assets", y] / df_bs.loc["Current Liabilities", y] for y in years],
        "DSCR": [(df_pl.loc["PAT", y] + df_pl.loc["Depreciation", y] + df_pl.loc["Interest (Term+CC)", y]) / 
                 (annual_principal_repay + df_pl.loc["Interest (Term+CC)", y]) for y in years]
    }).set_index("Year").transpose()
    st.dataframe(ratios.style.format("{:.2f}"), use_container_width=True)

# Excel Export
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_pl.to_excel(writer, sheet_name='P&L_Account')
    df_bs.to_excel(writer, sheet_name='Balance_Sheet')
st.download_button("📗 Download CMA Excel", output.getvalue(), "CMA_Detailed_Report.xlsx")
