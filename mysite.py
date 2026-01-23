import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. RAJASTHAN ODOP DATABASE ---
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

# --- PAGE CONFIG ---
st.set_page_config(page_title="CA Kailash Mali - MSME Subsidy Specialist", layout="wide")

# --- CUSTOM CSS FOR WHITE THEME & CLEAN LAYOUT ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTable { background-color: #f8f9fa; border-radius: 10px; }
    div.stButton > button:first-child { background-color: #002e5b; color: white; }
    .header-text { color: #002e5b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- PROFESSIONAL HEADER (WHITE BACKGROUND) ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    # Professional CA Logo (Using a standard high-quality placeholder)
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/0/03/Institute_of_Chartered_Accountants_of_India_logo.svg/1200px-Institute_of_Chartered_Accountants_of_India_logo.svg.png", width=120)

with col_title:
    st.markdown("<h1 class='header-text'>Rajasthan MSME Subsidy Comparison Tool</h1>", unsafe_allow_html=True)
    st.markdown(f"### Developed by **CA KAILASH MALI**")
    st.markdown("📞 **7737306376** | 📧 **CAKAILASHMALI4@GMAIL.COM**")

st.markdown("---")

# --- 2. LAYOUT: ELIGIBILITY & FUNDING ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🔍 Project Eligibility")
    with st.expander("Configure Profile", expanded=True):
        is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"], horizontal=True)
        applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"], horizontal=True)
        district = st.selectbox("District", list(rajasthan_odop.keys()))
        odop_item = rajasthan_odop[district]
        is_odop_confirmed = st.checkbox(f"Project falls under ODOP: {odop_item}?")
        
        sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
        social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
        gender = st.selectbox("Gender", ["Male", "Female"])
        loc = st.radio("Location", ["Urban", "Rural"], horizontal=True)
        
        is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural")
        min_cont_pct = 0.05 if is_special_cat else 0.10

with col2:
    st.markdown("### 💰 Funding Structure")
    with st.expander("Financial Details", expanded=True):
        pm_cost = st.number_input("Plant & Machinery", value=1500000)
        lb_cost = st.number_input("Land & Building (Shed)", value=300000)
        wc_req = st.number_input("Working Capital Required", value=200000)
        total_project_cost = pm_cost + lb_cost + wc_req
        
        own_cont_amt = st.number_input(f"Own Contribution (Min {int(min_cont_pct*100)}%)", value=float(total_project_cost * min_cont_pct))
        req_loan = float(total_project_cost - own_cont_amt)
        
        st.metric("Total Project Cost", f"₹{total_project_cost:,.0f}")
        st.metric("Required Loan Amount", f"₹{req_loan:,.0f}")
        
        loan_tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
        start_date = st.date_input("Start Date", date(2026, 1, 1))

# --- 3. SUBSIDY CALCULATION ENGINE ---
results = []
v_rate, p_sub, r_rate, o_rate, v_grant = 0, 0, 0, 0, 0

# 1. ODOP Standalone
if is_odop_confirmed:
    o_rate = 8
    o_sub = req_loan * (o_rate / 100) * 5
    results.append({"Scheme": "ODOP Standalone", "Cap. Sub": 0, "Int %": "8%", "Int. Sub": o_sub, "Total": o_sub})

# 2. RIPS 2024
r_rate = 8 if (is_special_cat) else 6
r_sub = req_loan * (r_rate / 100) * loan_tenure
results.append({"Scheme": "RIPS 2024", "Cap. Sub": 0, "Int %": f"{r_rate}%", "Int. Sub": r_sub, "Total": r_sub})

# 3. VYUPY
vyupy_loan = min(req_loan, 20000000)
v_rate = 8 if vyupy_loan <= 10000000 else 7
if is_special_cat: v_rate += 1
v_sub = vyupy_loan * (v_rate / 100) * 5
v_grant = min(vyupy_loan * 0.25, 500000) if lb_cost <= (total_project_cost * 0.25) else 0
results.append({"Scheme": "VYUPY", "Cap. Sub": v_grant, "Int %": f"{v_rate}%", "Int. Sub": v_sub, "Total": v_grant + v_sub})

# 4. PMEGP
if is_new_project == "New Unit":
    p_rate_pct = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
    p_sub = (total_project_cost - lb_cost) * (p_rate_pct / 100)
    results.append({"Scheme": "PMEGP", "Cap. Sub": p_sub, "Int %": "0%", "Int. Sub": 0, "Total": p_sub})

# --- 4. OUTPUT DISPLAY ---
st.markdown("---")
st.markdown("### 🏁 Comparative Analysis")
df_res = pd.DataFrame(results).sort_values(by="Total", ascending=False)
st.table(df_res.style.format({"Cap. Sub": "₹{:,.0f}", "Int. Sub": "₹{:,.0f}", "Total": "₹{:,.0f}"}))

# --- 5. REPAYMENT SCHEDULE ---
st.markdown("---")
selected_scheme = st.selectbox("Select Scheme for Detailed Repayment Schedule", ["None"] + [r['Scheme'] for r in results])

if selected_scheme != "None":
    sched = []
    curr_bal = req_loan
    monthly_p = curr_bal / (loan_tenure * 12)
    cap_c = p_sub if selected_scheme == "PMEGP" else (v_grant if selected_scheme == "VYUPY" else 0)
    i_rate = v_rate if "VYUPY" in selected_scheme else (r_rate if "RIPS" in selected_scheme else (8 if "ODOP" in selected_scheme else 0))

    for m in range(1, (loan_tenure * 12) + 1):
        curr_dt = start_date + pd.DateOffset(months=m-1)
        if m == 1: curr_bal = max(0, curr_bal - cap_c)
        if curr_bal <= 0:
            p_p, i_ch, i_cr, curr_bal = 0, 0, 0, 0
        else:
            i_ch = (curr_bal * 0.10) / 12
            i_cr = (curr_bal * (i_rate / 100)) if (i_rate > 0 and curr_dt.month == 4) else 0
            p_p = min(monthly_p, curr_bal)
            curr_bal = max(0, curr_bal - p_p)
        
        sched.append({"Month": curr_dt.strftime('%b-%Y'), "Principal": p_p, "Interest": i_ch, "Subsidy Credit": i_cr + (cap_c if m == 1 else 0), "Balance": curr_bal})

    st.dataframe(pd.DataFrame(sched).style.format({"Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}", "Subsidy Credit": "₹{:,.0f}", "Balance": "₹{:,.0f}"}), use_container_width=True)

# FOOTER
st.markdown("---")
st.caption("Developed by CA Kailash Mali | Advisory Tool for Rajasthan MSME Policies 2026")
