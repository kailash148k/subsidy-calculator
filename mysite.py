import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
from fpdf import FPDF

# --- 1. FIRM DETAILS ---
FIRM_NAME = "M/s Swastik Trading Company"
PROPRIETOR = "Mr. Gaurav Jain (Chartered Accountant)"
LOCATION = "Udaipur, Rajasthan"

# --- 2. ODOP DATA ---
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
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool")
st.caption(f"Powered by {FIRM_NAME} | {PROPRIETOR}")

# --- 3. SIDEBAR & FINANCIALS ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    
    st.markdown("---")
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    is_odop_confirmed = st.checkbox(f"Confirm ODOP: {odop_item}?", value=False)
    
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    loc = st.radio("Location", ["Urban", "Rural"])
    is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural")
    min_cont_pct = 0.05 if is_special_cat else 0.10

    st.markdown("### D. Financials")
    pm_cost = st.number_input("Plant & Machinery", value=1500000)
    lb_cost = st.number_input("Land & Building", value=300000)
    wc_req = st.number_input("Working Capital", value=100000)
    total_project_cost = pm_cost + lb_cost + wc_req

    own_cont_amt = st.number_input("Own Contribution", value=float(total_project_cost * min_cont_pct))
    req_loan = float(total_project_cost - own_cont_amt)
    
    loan_tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    start_date = st.date_input("Start Date", date(2026, 1, 1))

# --- 4. ENGINE ---
results = []
v_rate, p_sub, r_rate = 0, 0, 0

# RIPS
r_rate = 8 if (is_special_cat or is_odop_confirmed) else 6
r_sub = req_loan * (r_rate/100) * loan_tenure
results.append({"Scheme": "RIPS 2024", "Cap. Sub": 0, "Int %": f"{r_rate}%", "Int. Sub": r_sub, "Total": r_sub})

# ODOP Standalone
if is_odop_confirmed:
    o_sub = req_loan * 0.08 * 5
    results.append({"Scheme": "ODOP Standalone", "Cap. Sub": 0, "Int %": "8%", "Int. Sub": o_sub, "Total": o_sub})

# VYUPY
v_rate = 9 if (is_special_cat or is_odop_confirmed) else 8
v_sub = req_loan * (v_rate/100) * 5
v_grant = min(req_loan * 0.25, 500000) if lb_cost <= (total_project_cost * 0.25) else 0
results.append({"Scheme": "VYUPY", "Cap. Sub": v_grant, "Int %": f"{v_rate}%", "Int. Sub": v_sub, "Total": v_grant + v_sub})

# PMEGP
if is_new_project == "New Unit":
    p_rate_pct = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
    p_sub = (total_project_cost - lb_cost) * (p_rate_pct/100)
    results.append({"Scheme": "PMEGP", "Cap. Sub": p_sub, "Int %": "0%", "Int. Sub": 0, "Total": p_sub})

# --- 5. DISPLAY & PDF ---
df_res = pd.DataFrame(results).sort_values(by="Total", ascending=False)
st.table(df_res.style.format({"Cap. Sub": "₹{:,.0f}", "Int. Sub": "₹{:,.0f}", "Total": "₹{:,.0f}"}))

st.markdown("---")
selected_scheme = st.radio("Generate Branded Report for:", ["None", "PMEGP", "VYUPY", "RIPS 2024", "ODOP Standalone"], horizontal=True)

if selected_scheme != "None":
    # Generate Schedule
    sched = []
    curr_bal = req_loan
    monthly_p = curr_bal / (loan_tenure * 12)
    cap_c = p_sub if selected_scheme == "PMEGP" else (v_grant if selected_scheme == "VYUPY" else 0)
    i_rate = v_rate if "VYUPY" in selected_scheme else (r_rate if "RIPS" in selected_scheme else (8 if "ODOP" in selected_scheme else 0))

    for m in range(1, (loan_tenure * 12) + 1):
        curr_dt = start_date + pd.DateOffset(months=m-1)
        if m == 1: curr_bal -= cap_c
        interest = (curr_bal * 0.10) / 12
        credit = (curr_bal * (i_rate/100)) if (i_rate > 0 and curr_dt.month == 4) else 0
        curr_bal -= monthly_p
        sched.append({"Month": curr_dt.strftime('%b-%Y'), "Principal": monthly_p, "Interest": interest, "Subsidy": credit + (cap_c if m == 1 else 0), "Balance": max(0, curr_bal)})
    
    df_sched = pd.DataFrame(sched)
    st.dataframe(df_sched.style.format({"Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}", "Subsidy": "₹{:,.0f}", "Balance": "₹{:,.0f}"}))

    # PDF Export with Firm Branding
    def generate_pdf(df, s_name):
        pdf = FPDF()
        pdf.add_page()
        # HEADER
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, FIRM_NAME, ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(200, 5, f"{PROPRIETOR} | {LOCATION}", ln=True, align='C')
        pdf.ln(10)
        # TITLE
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"SUBSIDY REPAYMENT REPORT: {s_name}", ln=True, align='L')
        pdf.set_font("Arial", size=8)
        pdf.ln(5)
        # TABLE
        for col in ["Month", "Principal", "Interest", "Subsidy", "Balance"]: pdf.cell(38, 10, col, 1)
        pdf.ln()
        for _, r in df.iterrows():
            pdf.cell(38, 8, r['Month'], 1)
            pdf.cell(38, 8, f"{r['Principal']:,.0f}", 1)
            pdf.cell(38, 8, f"{r['Interest']:,.0f}", 1)
            pdf.cell(38, 8, f"{r['Subsidy']:,.0f}", 1)
            pdf.cell(38, 8, f"{r['Balance']:,.0f}", 1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')

    st.download_button(f"📥 Download {selected_scheme} PDF Report", generate_pdf(df_sched, selected_scheme), f"{selected_scheme}_Report.pdf", "application/pdf")
