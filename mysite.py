import os
import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# --- 1. FIRM BRANDING ---
FIRM_NAME = "M/s Swastik Trading Company"
PROPRIETOR = "Mr. Gaurav Jain (Chartered Accountant)"

# --- 2. PDF SYSTEM CHECK ---
try:
    from fpdf import FPDF
    PDF_READY = True
except ImportError:
    # Try one last-ditch effort to install on the fly
    os.system("python -m pip install fpdf")
    try:
        from fpdf import FPDF
        PDF_READY = True
    except:
        PDF_READY = False

# --- 3. ODOP DATA ---
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

# --- 4. SIDEBAR ---
with st.sidebar:
    if PDF_READY:
        st.success("✅ PDF Export Active")
    else:
        st.error("⚠️ PDF Library Missing")
    
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
    total_project_cost = pm_cost + lb_cost + 120000 # Adding misc/WC base

    own_cont_amt = st.number_input("Own Contribution", value=float(total_project_cost * min_cont_pct))
    req_loan = float(total_project_cost - own_cont_amt)
    
    loan_tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    start_date = st.date_input("Loan Start Date", date(2026, 1, 1))

# --- 5. CALCULATION ENGINE ---
results = []
v_rate, p_sub, r_rate, v_grant = 8, 0, 6, 0

# Logic
r_rate = 8 if (is_special_cat or is_odop_confirmed) else 6
results.append({"Scheme": "RIPS 2024", "Cap. Sub": 0, "Int %": f"{r_rate}%", "Int. Sub": req_loan * (r_rate/100) * loan_tenure, "Total": req_loan * (r_rate/100) * loan_tenure})

v_rate = 9 if (is_special_cat or is_odop_confirmed) else 8
v_grant = min(req_loan * 0.25, 500000) if lb_cost <= (total_project_cost * 0.25) else 0
results.append({"Scheme": "VYUPY", "Cap. Sub": v_grant, "Int %": f"{v_rate}%", "Int. Sub": req_loan * (v_rate/100) * 5, "Total": v_grant + (req_loan * (v_rate/100) * 5)})

if is_new_project == "New Unit":
    p_pct = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
    p_sub = (total_project_cost - lb_cost) * (p_pct/100)
    results.append({"Scheme": "PMEGP", "Cap. Sub": p_sub, "Int %": "0%", "Int. Sub": 0, "Total": p_sub})

# --- 6. DISPLAY ---
df_res = pd.DataFrame(results).sort_values(by="Total", ascending=False)
st.table(df_res.style.format({"Cap. Sub": "₹{:,.0f}", "Int. Sub": "₹{:,.0f}", "Total": "₹{:,.0f}"}))

st.markdown("---")
selected_scheme = st.radio("Generate Branded Report for:", ["None", "PMEGP", "VYUPY", "RIPS 2024"], horizontal=True)

if results and selected_scheme != "None" and PDF_READY:
    # Simpler Repayment Table for PDF
    sched = []
    curr_bal = req_loan
    monthly_p = curr_bal / (loan_tenure * 12)
    cap_c = p_sub if selected_scheme == "PMEGP" else (v_grant if selected_scheme == "VYUPY" else 0)
    i_rate = v_rate if "VYUPY" in selected_scheme else (r_rate if "RIPS" in selected_scheme else 0)

    for m in range(1, (loan_tenure * 12) + 1):
        curr_dt = start_date + pd.DateOffset(months=m-1)
        if m == 1: curr_bal -= cap_c
        interest = (curr_bal * 0.10) / 12
        credit = (curr_bal * (i_rate/100)) if (i_rate > 0 and curr_dt.month == 4) else 0
        curr_bal -= monthly_p
        sched.append({"Month": curr_dt.strftime('%b-%Y'), "Principal": monthly_p, "Interest": interest, "Subsidy": credit + (cap_c if m == 1 else 0), "Balance": max(0, curr_bal)})
    
    df_sched = pd.DataFrame(sched)
    st.dataframe(df_sched.style.format({"Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}", "Subsidy": "₹{:,.0f}", "Balance": "₹{:,.0f}"}))

    def get_pdf(df, s_name):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, FIRM_NAME, ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(200, 5, f"{PROPRIETOR}", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"Repayment Schedule: {s_name}", ln=True, align='L')
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 8)
        for col in ["Month", "Principal", "Interest", "Subsidy", "Balance"]: pdf.cell(38, 10, col, 1)
        pdf.ln()
        pdf.set_font("Arial", size=8)
        for _, r in df.iterrows():
            pdf.cell(38, 8, r['Month'], 1)
            pdf.cell(38, 8, f"{r['Principal']:,.0f}", 1)
            pdf.cell(38, 8, f"{r['Interest']:,.0f}", 1)
            pdf.cell(38, 8, f"{r['Subsidy']:,.0f}", 1)
            pdf.cell(38, 8, f"{r['Balance']:,.0f}", 1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')

    st.download_button(f"📥 Download {selected_scheme} PDF", get_pdf(df_sched, selected_scheme), f"{selected_scheme}.pdf", "application/pdf")
