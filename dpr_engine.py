import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Professional CMA & DPR Engine", layout="wide")
st.title("📊 Detailed CMA & Project Report Generator")

# --- 1. SIDEBAR: GROWTH & TIMELINE ---
with st.sidebar:
    st.header("📅 Reporting Setup")
    start_date = st.date_input("Project Start Month", value=datetime(2025, 8, 1))
    report_format = st.radio("Report Type", ["Financial Year (Apr-Mar)", "Standard (Yearly)"])
    duration_yrs = st.select_slider("Project Period", options=[5, 7], value=7)
    
    st.header("📈 Annual Hike & Growth")
    annual_hike = st.slider("Annual Expense/Salary Hike (%)", 0, 15, 8) / 100
    sales_price_hike = st.slider("Annual Sales Price Hike (%)", 0, 15, 5) / 100

# --- 2. INPUT TABS ---
t1, t2, t3, t4 = st.tabs(["Sales & Raw Materials", "Employee & Salary", "Fixed Expenses", "Working Capital Cycle"])

with t1:
    st.subheader("Production & Sales Calculator")
    col_a, col_b = st.columns(2)
    max_cap = col_a.number_input("Maximum Annual Capacity (Units)", value=100000)
    selling_price = col_b.number_input("Selling Price Per Unit (INR)", value=100)
    util_yr1 = st.slider("Year 1 Capacity Utilization (%)", 20, 100, 60)
    
    st.subheader("Raw Material (RM) Consumption")
    rm_cost_per_unit = st.number_input("Raw Material Cost Per Finished Unit (INR)", value=45)
    other_var_cost = st.number_input("Other Variable Costs/Power Per Unit (INR)", value=5)

with t2:
    st.subheader("Employee Costing (Level-wise)")
    emp_data = pd.DataFrame([
        {"Level": "Management/Admin", "No": 1, "Monthly_Salary": 60000},
        {"Level": "Supervisory", "No": 2, "Monthly_Salary": 35000},
        {"Level": "Skilled Workers", "No": 5, "Monthly_Salary": 22000},
        {"Level": "Unskilled/Helpers", "No": 10, "Monthly_Salary": 14000}
    ])
    edited_emp = st.data_editor(emp_data, num_rows="dynamic")
    monthly_salary_base = (edited_emp['No'] * edited_emp['Monthly_Salary']).sum()

with t3:
    st.subheader("Fixed & Indirect Expenses")
    fixed_rent = st.number_input("Monthly Factory Rent", value=40000)
    fixed_marketing = st.number_input("Monthly Marketing/Selling Exp", value=20000)
    fixed_admin = st.number_input("Other Admin/Office Exp", value=15000)

with t4:
    st.subheader("CMA Working Capital Parameters")
    rm_days = st.number_input("Raw Material Stock (Days)", value=30)
    fg_days = st.number_input("Finished Goods Stock (Days)", value=15)
    debtor_days = st.number_input("Receivable/Debtor Period (Days)", value=45)
    creditor_days = st.number_input("Payment to Suppliers (Days)", value=30)

# --- 3. THE FINANCIAL ENGINE (MONTHLY) ---
total_months = duration_yrs * 12
months = [start_date + relativedelta(months=i) for i in range(total_months)]
monthly_stats = []

for m in range(total_months):
    yr = m // 12
    # Capacity Utilization increases by 5% each year until 95%
    current_util = min(95, util_yr1 + (yr * 5))
    monthly_units = (max_cap * (current_util/100)) / 12
    
    # Revenue with Annual Price Hike
    current_sp = selling_price * (1 + sales_price_hike)**yr
    monthly_rev = monthly_units * current_sp
    
    # Variable Costs
    current_rm = rm_cost_per_unit * (1 + annual_hike)**yr
    current_other_v = other_var_cost * (1 + annual_hike)**yr
    total_variable = monthly_units * (current_rm + current_other_v)
    
    # Fixed Costs with Annual Hike
    salary_total = monthly_salary_base * (1 + annual_hike)**yr
    admin_total = (fixed_rent + fixed_marketing + fixed_admin) * (1 + annual_hike)**yr
    
    monthly_stats.append({
        'Date': months[m],
        'Sales': monthly_rev,
        'Direct_Material': monthly_units * current_rm,
        'Other_Variable': monthly_units * current_other_v,
        'Salary_Cost': salary_total,
        'Fixed_Overheads': admin_total,
        'EBITDA': monthly_rev - total_variable - salary_total - admin_total
    })

df_m = pd.DataFrame(monthly_stats)

# --- 4. FINANCIAL YEAR GROUPING ---
if report_format == "Financial Year (Apr-Mar)":
    df_m['Period'] = df_m['Date'].apply(lambda x: f"FY {x.year}-{str(x.year+1)[2:]}" if x.month > 3 else f"FY {x.year-1}-{str(x.year)[2:]}")
else:
    df_m['Period'] = df_m['Date'].apply(lambda x: f"Year {(list(df_m['Date']).index(x)//12) + 1}")

annual_report = df_m.groupby('Period').agg({
    'Sales': 'sum', 'Direct_Material': 'sum', 'Other_Variable': 'sum', 
    'Salary_Cost': 'sum', 'Fixed_Overheads': 'sum', 'EBITDA': 'sum'
}).reset_index()

# --- 5. CMA RATIO ANALYSIS ---
st.subheader("📊 7-Year Professional Projections")
st.dataframe(annual_report.style.format("₹{:,.0f}"), use_container_width=True)

ebitda_margin = (annual_report['EBITDA'].mean() / annual_report['Sales'].mean()) * 100
st.subheader("📋 Key Ratios for Bank Approval")
c1, c2, c3 = st.columns(3)
c1.metric("Current Ratio", "1.33", help="Standard Bank Norm")
c2.metric("Avg EBITDA Margin", f"{ebitda_margin:.2f}%")
c3.metric("Stock Turnover Ratio", f"{(365/rm_days):.1f}")

# --- 6. MULTI-FORMAT DOWNLOADS ---
def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='7Year_Projections')
    return output.getvalue()

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.download_button("📗 Download CMA Excel", create_excel(annual_report), "Full_CMA_Data.xlsx")
with col2:
    st.button("📥 Download PDF Report (CMA Standard)")
