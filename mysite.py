import streamlit as st
import pandas as pd
from datetime import datetime, date

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

# --- 2. ELIGIBILITY & FINANCIALS ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    has_other_subsidy = st.checkbox("Already availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("State", ["Rajasthan", "Other"])
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    
    is_odop_confirmed = st.checkbox(f"Is this for ODOP: {odop_item}?", value=False)
    
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
        own_cont_amt = st.number_input(f"Own Contribution", value=float(min_amt_req))
        req_term_loan = st.number_input("Term Loan Required", value=float(pm_cost + furn_cost + lb_cost + other_cost - own_cont_amt))
        req_wc_loan = st.number_input("Working Capital Loan", value=float(wc_req))
        total_funding = own_cont_amt + req_term_loan + req_wc_loan
        st.info(f"Total Funding: ₹{total_funding:,.0f}")

    loan_tenure = st.slider("Total Loan Tenure (Years)", 1, 7, 7)
    start_date = st.date_input("Loan Start Date", date(2026, 1, 1))

# --- 3. SCHEME ENGINE ---
results = []
v_rate = 0
pmegp_sub = 0
vyupy_grant = 0

if total_project_cost == total_funding and own_cont_amt >= min_amt_req:
    # 1. STANDALONE ODOP BENEFIT
    if state == "Rajasthan" and is_odop_confirmed:
        odop_int_sub = (req_term_loan + req_wc_loan) * (0.08) * 5
        results.append({"Scheme": "ODOP Standalone", "Capital Subsidy": 0, "Interest %": "8%", "Interest Subsidy": odop_int_sub, "Total Benefit": odop_int_sub})

    # 2. RIPS 2024 (RESTORED)
    if state == "Rajasthan":
        r_rate = 8 if (is_odop_confirmed or is_special_cat) else 6
        rips_int = (req_term_loan + req_wc_loan) * (r_rate / 100) * loan_tenure
        results.append({"Scheme": "RIPS 2024", "Capital Subsidy": 0, "Interest %": f"{r_rate}%", "Interest Subsidy": rips_int, "Total Benefit": rips_int})

    # 3. VYUPY Logic
    if state == "Rajasthan":
        vyupy_loan = min(req_term_loan + min(req_wc_loan, total_project_cost * 0.30), 20000000)
        v_rate = 8 if vyupy_loan <= 10000000 else 7
        if is_special_cat: v_rate += 1
        v_int_sub = vyupy_loan * (v_rate / 100) * 5
        # HIDDEN CONDITION LOCKED
        v_grant = min(vyupy_loan * 0.25, 500000) if lb_cost <= (total_project_cost * 0.25) else 0
        results.append({"Scheme": "VYUPY", "Capital Subsidy": v_grant, "Interest %": f"{v_rate}%", "Interest Subsidy": v_int_sub, "Total Benefit": v_grant + v_int_sub})

    # 4. PMEGP Logic
    if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
        p_rate = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
        pmegp_sub = min(total_project_cost - lb_cost, 5000000 if sector == "Manufacturing" else 2000000) * (p_rate / 100)
        results.append({"Scheme": "PMEGP", "Capital Subsidy": pmegp_sub, "Interest %": "0%", "Interest Subsidy": 0, "Total Benefit": pmegp_sub})

# --- 4. DISPLAY ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df_results = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    st.table(df_results.style.format({"Capital Subsidy": "₹{:,.0f}", "Interest Subsidy": "₹{:,.0f}", "Total Benefit": "₹{:,.0f}"}))

# --- 5. REPAYMENT ---
st.markdown("---")
st.subheader("📅 Repayment Schedule")
csv = pd.DataFrame().to_csv(index=False).encode('utf-8') # Placeholder
if results:
    # Repayment Logic as per Baseline
    st.info("Generating schedule based on highest calculated benefit...")
