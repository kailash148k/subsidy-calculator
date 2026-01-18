import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="Professional CMA & Balance Sheet", layout="wide")
st.title("🏦 Full Manufacturing P&L and Balance Sheet Engine")

# --- INPUT SECTION (Simplified for clarity) ---
with st.sidebar:
    st.header("🏢 Capital & Loan")
    total_cost = st.number_input("Total Project Cost", value=5000000)
    own_pct = st.number_input("Own Contribution (%)", value=25.0)
    own_cap = total_cost * (own_pct/100)
    loan_amt = total_cost - own_cap
    
    st.header("⚙️ Operations")
    max_sales = st.number_input("Max Annual Sales Revenue", value=8000000)
    rm_cost_pct = st.number_input("Raw Material Cost (%)", value=55.0) / 100
    util_y1 = st.number_input("Year 1 Utilization (%)", value=60.0) / 100

# --- FINANCIAL CALCULATION ---
years = [f"Year {i}" for i in range(1, 8)]
pl_data = []
bs_data = []

curr_loan = loan_amt
for i in range(7):
    # --- PROFIT & LOSS ACCOUNT ---
    util = min(0.95, util_y1 + (i * 0.05))
    sales = max_sales * util * (1.08**i) # 8% growth
    cogs = sales * rm_cost_pct
    salaries = 600000 * (1.07**i)
    ebitda = sales - cogs - salaries
    depr = total_cost * 0.10
    interest = curr_loan * 0.105
    pbt = ebitda - depr - interest
    tax = max(0, pbt * 0.25)
    pat = pbt - tax
    
    pl_data.append({
        "Particulars": years[i], "Gross Sales": sales, "COGS": cogs, 
        "EBITDA": ebitda, "Interest": interest, "Depreciation": depr, "PBT": pbt, "PAT": pat
    })

    # --- BALANCE SHEET (Module 12 & 13) ---
    stock = (cogs / 365) * 30 # 30 Days Stock
    debtors = (sales / 365) * 45 # 45 Days Debtors
    cash = pat * 0.10 # Cash reserve
    curr_assets = stock + debtors + cash
    
    # Liabilities
    creditors = (cogs / 365) * 30
    prin_repay = loan_amt / 7
    curr_liab = creditors + prin_repay # Incl. Current Portion of Loan
    curr_loan -= prin_repay
    
    bs_data.append({
        "Year": years[i], "Net Fixed Assets": total_cost - (depr*(i+1)),
        "Current Assets": curr_assets, "Total Assets": (total_cost - (depr*(i+1))) + curr_assets,
        "Net Worth": own_cap + (pat*(i+1)), "Long Term Loan": max(0, curr_loan),
        "Current Liabilities": curr_liab, "Total Liabilities": (own_cap + (pat*(i+1))) + max(0, curr_loan) + curr_liab
    })

df_pl = pd.DataFrame(pl_data).set_index("Particulars").transpose()
df_bs = pd.DataFrame(bs_data).set_index("Year").transpose()

# --- DISPLAY ---
t1, t2, t3 = st.tabs(["Profit & Loss A/c", "Balance Sheet", "Ratio Sheet"])

with t1:
    st.subheader("📊 Projected Profit & Loss Statement")
    st.dataframe(df_pl.style.format("₹{:,.0f}"), use_container_width=True)

with t2:
    st.subheader("⚖️ Projected Balance Sheet")
    st.dataframe(df_bs.style.format("₹{:,.0f}"), use_container_width=True)

with t3:
    st.subheader("📈 Financial Ratios")
    ratios = pd.DataFrame({
        "Year": years,
        "Current Ratio": [df_bs.loc["Current Assets", y] / df_bs.loc["Current Liabilities", y] for y in years],
        "Debt-Equity": [df_bs.loc["Long Term Loan", y] / df_bs.loc["Net Worth", y] for y in years]
    }).set_index("Year").transpose()
    st.dataframe(ratios.style.format("{:.2f}"), use_container_width=True)

# --- EXCEL DOWNLOAD ---
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_pl.to_excel(writer, sheet_name='P&L_Account')
    df_bs.to_excel(writer, sheet_name='Balance_Sheet')
st.download_button("📗 Download CMA Excel", output.getvalue(), "CMA_Full_Report.xlsx")
