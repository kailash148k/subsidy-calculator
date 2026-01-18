import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="MSME Professional DPR Engine", layout="wide")

# --- HEADER & FIRM DETAILS (Module 1) ---
st.title("🏭 Manufacturing Project Report & CMA Engine")
with st.expander("📝 Step 1: Basic Firm Details", expanded=True):
    c1, c2 = st.columns(2)
    firm_name = c1.text_input("Firm Name", "Kailash Manufacturing")
    gst_no = c2.text_input("GST Number")
    udyam_no = c1.text_input("Udyam Number")
    address = c2.text_area("Address")
    mobile = c1.text_input("Mobile No")

# --- CAPEX & PROJECT COST (Modules 10 & 11) ---
with st.expander("🏗️ Step 2: CAPEX, Project Cost & Funding"):
    st.subheader("Asset Investment (CAPEX)")
    col1, col2, col3 = st.columns(3)
    val_land = col1.number_input("Land & Building", value=2000000)
    val_machinery = col2.number_input("Plant & Machinery", value=2500000)
    val_comp = col3.number_input("Computers/Printers", value=100000)
    val_furniture = col1.number_input("Furniture & Fixtures", value=200000)
    val_car = col2.number_input("Vehicles/Car", value=800000)
    val_other = col3.number_input("Other Fixed Assets", value=0)

    total_capex = val_land + val_machinery + val_comp + val_furniture + val_car + val_other
    st.divider()
    
    st.subheader("Means of Finance")
    # CHANGED: Slider replaced with numeric input box as requested
    own_cont_pct = st.number_input("Own Contribution (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
    
    own_capital = (total_capex * own_cont_pct) / 100
    term_loan_req = total_capex - own_capital
    st.info(f"Total Project Cost: ₹{total_capex:,.0f} | Own Capital: ₹{own_capital:,.0f} | Term Loan: ₹{term_loan_req:,.0f}")

# --- LOAN & WORKING CAPITAL (Modules 2, 3 & 13) ---
with st.expander("💰 Step 3: Loan & Working Capital Details"):
    c1, c2, c3 = st.columns(3)
    loan_tenure = c1.number_input("Term Loan Tenure (Months)", value=84)
    loan_rate = c2.number_input("Term Loan Rate (%)", value=10.5) / 100
    moratorium = c3.number_input("Moratorium Period (Months)", value=6)
    
    cc_limit = c1.number_input("CC Limit (Working Capital)", value=1000000)
    cc_rate = c2.number_input("CC Interest Rate (%)", value=11.0) / 100
    cc_util_val = c3.number_input("Avg. CC Utilization (%)", min_value=0, max_value=100, value=70)

# --- MANUFACTURING & SALES (Modules 4, 5, 12) ---
with st.expander("⚙️ Step 4: Sales, Manufacturing & Stock"):
    c1, c2, c3 = st.columns(3)
    unit_name = c1.selectbox("Unit Type", ["KG", "MT", "Nos", "Units"])
    max_cap = c2.number_input(f"Max Annual Capacity ({unit_name})", value=10000)
    sell_price = c3.number_input("Selling Price per Unit (₹)", value=1000)
    growth_val = c1.number_input("Annual Sales Growth (%)", value=10.0) / 100
    util_yr1_val = c2.number_input("Year 1 Capacity Utilization (%)", value=60.0) / 100
    
    st.subheader("Direct Manufacturing Expenses (Per Unit)")
    rm_cost = c1.number_input("Raw Material Cost per Unit", value=500)
    other_var_mfg = c2.number_input("Other Variable Mfg Cost", value=50)
    
    st.subheader("Working Capital Cycle (Days)")
    stock_days = c1.number_input("Stock Days (Raw Material)", value=30)
    debtor_days = c2.number_input("Debtor Days", value=45)
    creditor_days = c3.number_input("Creditor Days", value=30)

# --- OVERHEADS & TAX (Modules 6, 7, 8, 9, 14) ---
with st.expander("🏢 Step 5: Overheads & Taxation"):
    constitution = st.selectbox("Business Type (For Tax)", ["Proprietor", "Partnership", "Company"])
    c1, c2 = st.columns(2)
    salary_fix = c1.number_input("Monthly Fixed Salary (Indirect)", value=100000)
    salary_var = c2.number_input("Monthly Manufacturing Wages (Direct)", value=50000)
    rent_exp = c1.number_input("Monthly Rental Exp", value=40000)
    admin_exp = c2.number_input("Monthly Admin/Office Exp", value=15000)
    annual_hike_val = st.number_input("Annual Salary/Exp Hike (%)", value=7.0) / 100

# --- CALCULATION BUTTON ---
if st.button("🚀 Generate Full 7-Year DPR & CMA"):
    start_date = datetime(2025, 4, 1) 
    years = [f"FY {start_date.year + i}-{str(start_date.year + i + 1)[2:]}" for i in range(7)]
    
    m_rate = loan_rate / 12
    repay_months = loan_tenure - moratorium
    emi = term_loan_req * m_rate * ((1 + m_rate)**repay_months) / (((1 + m_rate)**repay_months) - 1)
    
    results = []
    curr_loan = term_loan_req
    
    for y in range(7):
        util = min(0.95, util_yr1_val + (y * 0.05))
        annual_units = max_cap * util
        revenue = annual_units * sell_price * (1 + growth_val)**y
        rm_total = annual_units * rm_cost * (1 + annual_hike_val)**y
        mfg_var = annual_units * other_var_mfg * (1 + annual_hike_val)**y
        salaries = (salary_fix + salary_var) * 12 * (1 + annual_hike_val)**y
        rent_admin = (rent_exp + admin_exp) * 12 * (1 + annual_hike_val)**y
        
        ebitda = revenue - rm_total - mfg_var - salaries - rent_admin
        depr = (val_machinery * 0.15) + (val_comp * 0.40) + (val_land * 0.05) + (val_furniture * 0.10) + (val_car * 0.15)
        
        int_term = curr_loan * loan_rate
        int_cc = (cc_limit * (cc_util_val/100)) * cc_rate
        pbt = ebitda - depr - int_term - int_cc
        
        tax_rate = 0.25 if constitution == "Company" else 0.30
        tax = max(0, pbt * tax_rate)
        pat = pbt - tax
        
        prin_repay = (emi * 12) - int_term if y > 0 else 0
        # Split Principal for Current Ratio (Module 13)
        curr_liability_prin = emi * 12 if y < 6 else curr_loan
        curr_loan -= prin_repay
        
        results.append({
            "Year": years[y], "Sales": revenue, "Direct_Cost": rm_total + mfg_var, 
            "EBITDA": ebitda, "Depreciation": depr, "Interest": int_term + int_cc,
            "PBT": pbt, "Tax": tax, "PAT": pat, "Repayment": prin_repay, "Loan_Bal": max(0, curr_loan)
        })

    df = pd.DataFrame(results)

    # --- RATIO & FLOW CALCULATIONS (Modules 15 & 16) ---
    st.subheader(f"📊 7-Year CMA for {firm_name}")
    st.dataframe(df.style.format(precision=0, thousands=","), use_container_width=True)

    t1, t2 = st.tabs(["Flow Statements", "Ratio Analysis"])
    with t1:
        df['Cash_Inflow'] = df['PAT'] + df['Depreciation']
        st.write("**Projected Cash Flow**")
        st.dataframe(df[['Year', 'Cash_Inflow', 'Repayment', 'Tax']].style.format(precision=0, thousands=","))
    with t2:
        df['DSCR'] = (df['PAT'] + df['Depreciation'] + df['Interest']) / (df['Repayment'] + df['Interest'])
        st.write("**Key Ratios**")
        st.dataframe(df[['Year', 'DSCR']].style.format(precision=2))

    # --- EXCEL EXPORT ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='CMA_Data', index=False)
        workbook = writer.book
        worksheet = writer.sheets['CMA_Data']
        header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        worksheet.write('A1', f"Detailed Project Report: {firm_name}", header_format)
        
    st.download_button("📗 Download CMA Excel", output.getvalue(), f"DPR_{firm_name}.xlsx")
