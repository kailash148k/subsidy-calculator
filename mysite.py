import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# --- 1. RAJASTHAN ODOP DATA ---
rajasthan_odop = {
    "Ajmer": "Granite and Marble Products", "Alwar": "Automobiles Parts", "Balotra": "Textile Products",
    "Banswara": "Marble Products", "Baran": "Garlic Products", "Barmer": "Kasheedakari",
    "Beawar": "Quartz and Feldspar Powder", "Bharatpur": "Agro Based Product", "Bhilwara": "Textile Products",
    "Bikaner": "Bikaneri Namkeen", "Bundi": "Sand Stone", "Chittorgarh": "Granite and Marble Products",
    "Churu": "Wood Products", "Dausa": "Stone Products", "Deedwana-Kuchaman": "Marble and Granite Products",
    "Deeg": "Stone Based Products", "Dholpur": "Stone Based Products", "Dungarpur": "Marble Product",
    "Hanumangarh": "Agro Based Product", "Jaipur": "Gems & Jewellery", "Jaisalmer": "Yellow Stone Products",
    "Jalore": "Granite Products", "Jhalawar": "Kota Stone Products", "Jhunjhunu": "Wooden Handicraft Products",
    "Jodhpur": "Wooden Furniture Products", "Karauli": "Sandstone Products", "Khairthal-Tijara": "Automobiles Parts",
    "Kota": "Kota Doria", "Kotputli-Behror": "Automobiles Parts", "Nagaur": "Pan Methi and Spices Processing",
    "Pali": "Textile Products", "Phalodi": "Sonamukhi Products", "Pratapgarh": "Thewa Jewellery",
    "Rajsamand": "Granite and Marble Products", "Salumber": "Quartz", "Sawai Madhopur": "Marble Products",
    "Sikar": "Wooden Furniture Products", "Sirohi": "Marble Products", "Sri Ganganagar": "Mustard Oil",
    "Tonk": "Slate Stone Products", "Udaipur": "Marble and Granite Products"
}

st.set_page_config(page_title="Rajasthan MSME Subsidy Pro", layout="wide")
st.title("⚖️ Rajasthan MSME Subsidy Master Engine")

# --- 2. LOCKED INPUT SECTION ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    
    st.markdown("---")
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    
    st.markdown("### D. Financials")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    loc = st.radio("Location", ["Urban", "Rural"])
    is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
    min_cont_pct = 0.05 if is_special else 0.10

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Project Cost**")
        pm_cost = st.number_input("Plant & Machinery", value=1500000)
        lb_cost = st.number_input("Building (Shed)", value=300000)
        wc_req = st.number_input("Working Capital", value=100000)
        total_project_cost = pm_cost + lb_cost + wc_req + 20000 # Incl Furniture
        st.info(f"Total: ₹{total_project_cost:,.0f}")

    with col_r:
        st.markdown("**Funding**")
        min_amt = total_project_cost * min_cont_pct
        own_cont = st.number_input(f"Own Capital (Min {int(min_cont_pct*100)}%)", value=float(min_amt))
        req_loan = total_project_cost - own_cont
        st.info(f"Total Loan: ₹{req_loan:,.0f}")

    start_date = st.date_input("Project Start Date", date(2026, 1, 1))
    loan_tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)

# --- 3. SCHEME SELECTION & ANALYSIS ---
st.subheader("🏁 Scheme Selection & Comparative Analysis")

# Calculate Potentials
p_rate = (35 if loc == "Rural" else 25) if is_special else (25 if loc == "Rural" else 15)
pmegp_cap = (total_project_cost - lb_cost) * (p_rate / 100)
int_sub_rate = 0.08 if is_special else 0.06

# Selection Checkboxes
sel_pmegp = st.checkbox(f"PMEGP ({p_rate}% Capital Subsidy)", value=True)
sel_vyupy = st.checkbox(f"Rajasthan VYUPY ({int(int_sub_rate*100)}% Interest Subvention)", value=True)

results = []
if sel_pmegp:
    results.append({"Scheme": "PMEGP", "Type": "Capital Grant", "Benefit": pmegp_cap, "Recurrence": "One-time (Month 1)"})
if sel_vyupy:
    results.append({"Scheme": "VYUPY", "Type": "Interest Subvention", "Benefit": req_loan * int_sub_rate * loan_tenure, "Recurrence": "Annual (April)"})

if results:
    st.table(pd.DataFrame(results).style.format({"Benefit": "₹{:,.0f}"}))

# --- 4. REPAYMENT SCHEDULE WITH SUBSIDY LOGIC ---
st.markdown("---")
st.subheader("📅 Repayment Schedule with Subsidy Credits")

def get_repayment_schedule(loan, rate, tenure_yrs, start_dt, cap_sub, int_sub_pct):
    schedule = []
    curr_bal = loan
    monthly_principal = loan / (tenure_yrs * 12)
    
    for m in range(1, (tenure_yrs * 12) + 1):
        curr_dt = start_dt + pd.DateOffset(months=m-1)
        
        # Feather 1: Capex Subsidy Credit in Month 1
        if m == 1:
            curr_bal -= cap_sub
            
        # Feather 2: Interest Subsidy Credit every April
        interest_charge = (curr_bal * rate) / 12
        int_credit = 0
        if curr_dt.month == 4 and sel_vyupy:
            int_credit = (curr_bal * int_sub_pct) # Annual credit logic
        
        curr_bal -= monthly_principal
        schedule.append({
            "Month": curr_dt.strftime('%b-%Y'),
            "Principal": monthly_principal,
            "Gross Interest": interest_charge,
            "Govt Credit": int_credit + (cap_sub if m == 1 else 0),
            "Net Balance": max(0, curr_bal)
        })
    return pd.DataFrame(schedule)

if st.button("🚀 Generate Detailed Schedule"):
    df_repay = get_repayment_schedule(req_loan, 0.10, loan_tenure, start_date, 
                                      pmegp_cap if sel_pmegp else 0, int_sub_rate)
    st.dataframe(df_repay.style.format({"Principal": "₹{:,.0f}", "Gross Interest": "₹{:,.0f}", 
                                       "Govt Credit": "₹{:,.0f}", "Net Balance": "₹{:,.0f}"}))
    
    st.download_button("📥 Export Schedule to Excel", df_repay.to_csv().encode('utf-8'), "Repayment.csv")
