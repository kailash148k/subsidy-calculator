import streamlit as st
import pandas as pd
import numpy as np

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
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool (v.20jan26-finalk)")

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
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    
    st.markdown("### D. Financials")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    user_age = st.number_input("Enter Applicant Age", min_value=18, max_value=100, value=25)
    loc = st.radio("Location", ["Urban", "Rural"])
    
    is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural" or user_age <= 40)
    min_cont_pct = 0.05 if is_special_cat else 0.10

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**Project Cost**")
        pm_cost = st.number_input("Plant & Machinery", value=1500000)
        furn_cost = st.number_input("Furniture & Fixtures", value=20000)
        lb_cost = st.number_input("Land & Building", value=300000)
        wc_req = st.number_input("Working Capital Req.", value=100000)
        total_project_cost = pm_cost + furn_cost + lb_cost + wc_req
        st.info(f"Total: ₹{total_project_cost:,.0f}")

    with col_right:
        st.markdown("**Funding**")
        min_amt_req = total_project_cost * min_cont_pct
        own_cont_amt = st.number_input(f"Own Cont. (Min {int(min_cont_pct*100)}%)", value=float(min_amt_req))
        req_term_loan = st.number_input("Term Loan Required", value=float(total_project_cost - own_cont_amt))
        total_funding = own_cont_amt + req_term_loan

    bank_roi = st.slider("Bank Interest Rate (%)", 5.0, 15.0, 9.0)
    loan_tenure_yrs = st.slider("Loan Tenure (Years)", 1, 7, 5)

# --- 3. SCHEME ENGINE ---
results = []
selected_scheme_data = None

if total_project_cost == total_funding and own_cont_amt >= min_amt_req:
    # VYUPY Logic
    if state == "Rajasthan" and user_age <= 40:
        v_sub_rate = 8 if req_term_loan <= 10000000 else 7
        if is_special_cat: v_sub_rate += 1
        vyupy_grant = min(req_term_loan * 0.25, 500000)
        results.append({"Scheme": "VYUPY", "Capex Sub": vyupy_grant, "Int Sub %": v_sub_rate})

    # PMEGP Logic
    if is_new_project == "New Unit" and not has_other_subsidy:
        p_rate = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
        pmegp_sub = min(total_project_cost, 5000000) * (p_rate / 100)
        results.append({"Scheme": "PMEGP", "Capex Sub": pmegp_sub, "Int Sub %": 0})

# --- 4. REPAYMENT SCHEDULE (THE NEW LOGIC) ---
st.subheader("🏁 Comparative Analysis & Repayment Schedule")

if results:
    df_schemes = pd.DataFrame(results)
    st.table(df_schemes)
    
    selected_scheme = st.selectbox("Select Scheme for Repayment Schedule", df_schemes["Scheme"])
    scheme_info = df_schemes[df_schemes["Scheme"] == selected_scheme].iloc[0]
    
    # Rule 2: Capex subsidy received Day 1
    effective_principal = req_term_loan - scheme_info["Capex Sub"]
    months = loan_tenure_yrs * 12
    
    # Rule 1: Fixed Principal + Monthly Interest
    fixed_principal_payment = effective_principal / months
    
    schedule = []
    current_balance = effective_principal
    
    for m in range(1, months + 1):
        interest_charge = current_balance * (bank_roi / 100 / 12)
        
        # Rule 2 & 3: Interest subsidy received annually (every 12th month)
        interest_subsidy_credit = 0
        if scheme_info["Int Sub %"] > 0 and m % 12 == 0:
            # Simplified annual calculation: Interest subsidy on avg outstanding for the year
            interest_subsidy_credit = (current_balance + (current_balance + (fixed_principal_payment * 11))) / 2 * (scheme_info["Int Sub %"] / 100)
        
        total_payment = fixed_principal_payment + interest_charge
        net_payment = total_payment - (interest_subsidy_credit / 12 if interest_subsidy_credit > 0 else 0)
        
        schedule.append({
            "Month": m,
            "Opening Balance": current_balance,
            "Principal": fixed_principal_payment,
            "Interest": interest_charge,
            "Gross Payment": total_payment,
            "Annual Int. Subsidy Credit": interest_subsidy_credit,
            "Net Monthly Effect": net_payment,
            "Closing Balance": max(0, current_balance - fixed_principal_payment)
        })
        current_balance -= fixed_principal_payment

    sched_df = pd.DataFrame(schedule)
    
    # Display Schedule
    st.write(f"### 📅 Repayment Schedule for {selected_scheme}")
    st.info(f"Note: Capex Subsidy of ₹{scheme_info['Capex Sub']:,.0f} applied on Day 1. Interest Subsidy of {scheme_info['Int Sub %']}% applied annually.")
    
    st.dataframe(sched_df.style.format({
        "Opening Balance": "₹{:,.0f}", "Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}", 
        "Gross Payment": "₹{:,.0f}", "Annual Int. Subsidy Credit": "₹{:,.0f}", 
        "Net Monthly Effect": "₹{:,.0f}", "Closing Balance": "₹{:,.0f}"
    }))

    # Visualizing Net Effect
    st.line_chart(sched_df.set_index("Month")[["Gross Payment", "Net Monthly Effect"]])
else:
    st.warning("No schemes eligible based on current profile.")
