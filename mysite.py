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

# --- BRANDED PAGE CONFIG & HEADER (EMOJI REMOVED) ---
st.set_page_config(page_title="CA Kailash Mali - MSME Subsidy", layout="wide")
st.title("Rajasthan MSME Subsidy Comparison Tool")
st.subheader("by CA KAILASH MALI")
st.markdown(f"**📞 7737306376** | **📧 CAKAILASHMALI4@GMAIL.COM**")
st.markdown("---")

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
    is_odop_confirmed = st.checkbox(f"Confirm: Project is for {odop_item}?", value=False)
    
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
        req_term_loan = st.number_input("Term Loan Required", value=float(pm_cost + furn_cost + lb_cost + other_cost - own_cont_amt))
        req_wc_loan = st.number_input("Working Capital Loan", value=float(wc_req))
        total_funding = own_cont_amt + req_term_loan + req_wc_loan
        st.info(f"Total Funding: ₹{total_funding:,.0f}")

    loan_tenure = st.slider("Total Loan Tenure (Years)", 1, 7, 7)
    start_date = st.date_input("Loan Start Date", date(2026, 1, 1))

# --- 3. SCHEME ENGINE ---
results = []
v_rate, p_sub, r_rate, o_rate, v_grant = 0, 0, 0, 0, 0

if total_project_cost == total_funding:
    # 1. ODOP Standalone
    if is_odop_confirmed:
        o_rate = 8
        o_sub = (req_term_loan + req_wc_loan) * (o_rate / 100) * 5
        results.append({"Scheme": "ODOP Standalone", "Cap. Sub": 0, "Int %": "8%", "Int. Sub": o_sub, "Total": o_sub})

    # 2. RIPS 2024
    r_rate = 8 if (is_special_cat) else 6
    r_sub = (req_term_loan + req_wc_loan) * (r_rate / 100) * loan_tenure
    results.append({"Scheme": "RIPS 2024", "Cap. Sub": 0, "Int %": f"{r_rate}%", "Int. Sub": r_sub, "Total": r_sub})

    # 3. VYUPY
    if state == "Rajasthan":
        vyupy_loan = min(req_term_loan + min(req_wc_loan, total_project_cost * 0.30), 20000000)
        v_rate = 8 if vyupy_loan <= 10000000 else 7
        if is_special_cat: v_rate += 1
        v_sub = vyupy_loan * (v_rate / 100) * 5
        v_grant = min(vyupy_loan * 0.25, 500000) if lb_cost <= (total_project_cost * 0.25) else 0
        results.append({"Scheme": "VYUPY", "Cap. Sub": v_grant, "Int %": f"{v_rate}%", "Int. Sub": v_sub, "Total": v_grant + v_sub})

    # 4. PMEGP
    if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
        p_rate_pct = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
        p_sub = min(total_project_cost - lb_cost, 5000000 if sector == "Manufacturing" else 2000000) * (p_rate_pct / 100)
        results.append({"Scheme": "PMEGP", "Cap. Sub": p_sub, "Int %": "0%", "Int. Sub": 0, "Total": p_sub})

# --- 4. DISPLAY & SELECTION ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df_res = pd.DataFrame(results).sort_values(by="Total", ascending=False)
    st.table(df_res.style.format({"Cap. Sub": "₹{:,.0f}", "Int. Sub": "₹{:,.0f}", "Total": "₹{:,.0f}"}))

    st.markdown("---")
    st.subheader("📅 Repayment Schedule Configuration")
    selected_scheme = st.radio(
        "Select **ONLY ONE** scheme for detailed Repayment Analysis:",
        ["None", "PMEGP (Capex Credit)", "VYUPY (Capex + Interest Credit)", "RIPS 2024 (Interest Credit)", "ODOP Standalone (8% Interest Credit)"],
        horizontal=True
    )

# --- 5. REPAYMENT SCHEDULE (CA-LOGIC: ZERO-BALANCE GUARD) ---
if results and selected_scheme != "None":
    sched = []
    curr_bal = req_term_loan + req_wc_loan
    monthly_p_baseline = curr_bal / (loan_tenure * 12)
    
    cap_credit = p_sub if selected_scheme == "PMEGP (Capex Credit)" else (v_grant if selected_scheme == "VYUPY (Capex + Interest Credit)" else 0)
    int_rate = v_rate if "VYUPY" in selected_scheme else (r_rate if "RIPS" in selected_scheme else (8 if "ODOP" in selected_scheme else 0))

    for m in range(1, (loan_tenure * 12) + 1):
        curr_dt = start_date + pd.DateOffset(months=m-1)
        
        if m == 1: 
            curr_bal = max(0, curr_bal - cap_credit)

        if curr_bal <= 0:
            p_pay, i_chg, i_cred, curr_bal = 0, 0, 0, 0
        else:
            i_chg = (curr_bal * 0.10) / 12  # Base 10% Interest
            i_cred = (curr_bal * (int_rate / 100)) if (int_rate > 0 and curr_dt.month == 4) else 0
            p_pay = min(monthly_p_baseline, curr_bal)
            curr_bal = max(0, curr_bal - p_pay)

        sched.append({
            "Month": curr_dt.strftime('%b-%Y'), 
            "Principal": p_pay, 
            "Interest": i_chg, 
            "Subsidy Credit": i_cred + (cap_credit if m == 1 and cap_credit > 0 else 0), 
            "Balance": curr_bal
        })
    
    df_sched = pd.DataFrame(sched)
    st.dataframe(df_sched.style.format({"Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}", "Subsidy Credit": "₹{:,.0f}", "Balance": "₹{:,.0f}"}))
