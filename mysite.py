import streamlit as st
import pandas as pd
from datetime import datetime, date
from fpdf import FPDF
import io

# --- 1. FULL RAJASTHAN ODOP DATA ---
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

# --- 2. ELIGIBILITY & FINANCIALS (LOCKED) ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    has_other_subsidy = st.checkbox("Already availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("State", ["Rajasthan", "Other"])
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    
    st.markdown("### D. Financials")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    loc = st.radio("Location", ["Urban", "Rural"])
    is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural")
    min_cont_pct = 0.05 if is_special_cat else 0.10

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**Project Cost (Assets)**")
        pm_cost = st.number_input("Plant & Machinery", value=1500000)
        furn_cost = st.number_input("Furniture & Fixtures", value=20000)
        lb_cost = st.number_input("Land & Building (Shed)", value=300000)
        wc_req = st.number_input("Working Capital Req.", value=100000)
        other_cost = st.number_input("Other Expenses", value=0)
        total_project_cost = pm_cost + furn_cost + lb_cost + wc_req + other_cost
        st.info(f"Total Project Cost: ₹{total_project_cost:,.0f}")

    with col_right:
        st.markdown("**Means of Finance (Funding)**")
        min_amt_req = total_project_cost * min_cont_pct
        own_cont_amt = st.number_input(f"Own Contribution (Min {int(min_cont_pct*100)}%)", value=float(min_amt_req))
        if own_cont_amt < min_amt_req:
            st.error(f"Minimum contribution required: ₹{min_amt_req:,.0f}")
        req_term_loan = st.number_input("Term Loan Required", value=float(pm_cost + furn_cost + lb_cost + other_cost - own_cont_amt))
        req_wc_loan = st.number_input("Working Capital Loan", value=float(wc_req))
        total_funding = own_cont_amt + req_term_loan + req_wc_loan
        st.info(f"Total Funding: ₹{total_funding:,.0f}")

    loan_tenure = st.slider("Total Loan Tenure (Years)", 1, 7, 7)
    start_date = st.date_input("Loan Start Date", date(2026, 1, 1))

# --- 3. SCHEME ENGINE ---
results = []
if total_project_cost == total_funding and own_cont_amt >= min_amt_req:
    # VYUPY Logic
    if state == "Rajasthan":
        eligible_wc = min(req_wc_loan, total_project_cost * 0.30)
        vyupy_loan = min(req_term_loan + eligible_wc, 20000000)
        v_rate = 8 if vyupy_loan <= 10000000 else 7
        if is_special_cat: v_rate += 1
        vyupy_int_sub = vyupy_loan * (v_rate / 100) * 5
        vyupy_grant = min(vyupy_loan * 0.25, 500000)
        if lb_cost <= (total_project_cost * 0.25):
            results.append({"Scheme": "VYUPY", "Capital %": "25% Grant", "Capital Subsidy": vyupy_grant, "Interest %": f"{v_rate}%", "Tenure": "5 Years", "Interest Subsidy": vyupy_int_sub, "Total Benefit": vyupy_grant + vyupy_int_sub})

    # PMEGP Logic
    if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
        p_rate = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
        pmegp_cost = total_project_cost - lb_cost
        max_limit = 5000000 if sector == "Manufacturing" else 2000000
        pmegp_sub = min(pmegp_cost, max_limit) * (p_rate / 100)
        results.append({"Scheme": "PMEGP", "Capital %": f"{p_rate}%", "Capital Subsidy": pmegp_sub, "Interest %": "0%", "Tenure": "Upfront", "Interest Subsidy": 0, "Total Benefit": pmegp_sub})

# --- 4. DISPLAY ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df_results = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    st.table(df_results.style.format({"Capital Subsidy": "₹{:,.0f}", "Interest Subsidy": "₹{:,.0f}", "Total Benefit": "₹{:,.0f}"}))

    st.markdown("---")
    st.subheader("📋 Project Financing Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Project Cost", f"₹{total_project_cost:,.0f}")
    c2.metric(f"Own Contribution ({int((own_cont_amt/total_project_cost)*100)}%)", f"₹{own_cont_amt:,.0f}")
    c3.metric("Bank Loan Required", f"₹{(req_term_loan + req_wc_loan):,.0f}")

# --- 5. REPAYMENT & PDF EXPORT ---
st.markdown("---")
st.subheader("📅 Repayment Schedule Generator")
col_x, col_y = st.columns(2)
with col_x: use_pmegp = st.checkbox("Include PMEGP Capex Credit (Month 1)", value=True)
with col_y: use_vyupy = st.checkbox("Include VYUPY Interest Subvention (Every April)", value=True)

def get_repayment_df(loan, tenure, start_dt, p_cap, v_sub_rate, v_active):
    sched = []
    curr_bal = loan
    monthly_principal = loan / (tenure * 12)
    for m in range(1, (tenure * 12) + 1):
        curr_dt = start_dt + pd.DateOffset(months=m-1)
        if m == 1: curr_bal -= p_cap 
        interest = (curr_bal * 0.10) / 12 
        credit = (curr_bal * v_sub_rate) if (v_active and curr_dt.month == 4) else 0
        curr_bal -= monthly_principal
        sched.append({"Month": curr_dt.strftime('%b-%Y'), "Principal": monthly_principal, "Interest": interest, "Subsidy Credit": credit + (p_cap if m == 1 else 0), "Balance": max(0, curr_bal)})
    return pd.DataFrame(sched)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "PMEGP/MSME Repayment Schedule", ln=True, align='C')
    pdf.set_font("Arial", 'B', 9)
    cols = ["Month", "Principal", "Interest", "Credit", "Balance"]
    for c in cols: pdf.cell(38, 10, c, 1)
    pdf.ln()
    pdf.set_font("Arial", size=8)
    for _, row in df.iterrows():
        pdf.cell(38, 8, row['Month'], 1)
        pdf.cell(38, 8, f"{row['Principal']:,.0f}", 1)
        pdf.cell(38, 8, f"{row['Interest']:,.0f}", 1)
        pdf.cell(38, 8, f"{row['Subsidy Credit']:,.0f}", 1)
        pdf.cell(38, 8, f"{row['Balance']:,.0f}", 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

if results:
    p_credit = pmegp_sub if use_pmegp else 0
    v_credit_rate = (v_rate / 100) if use_vyupy else 0
    repay_df = get_repayment_df(req_term_loan + req_wc_loan, loan_tenure, start_date, p_credit, v_credit_rate, use_vyupy)
    st.dataframe(repay_df.style.format({"Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}", "Subsidy Credit": "₹{:,.0f}", "Balance": "₹{:,.0f}"}))
    st.download_button("📥 Download Repayment PDF", create_pdf(repay_df), "Repayment_Schedule.pdf", "application/pdf")
