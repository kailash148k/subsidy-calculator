import streamlit as st
import pandas as pd

# --- 1. DATA & CONFIG ---
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

# --- 2. SIDEBAR INPUTS ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    has_other_subsidy = st.checkbox("Already availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("State", ["Rajasthan", "Other"])
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    
    st.markdown("### D. Financials")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    user_age = st.number_input("Enter Applicant Age", min_value=18, max_value=100, value=25)
    loc = st.radio("Location", ["Urban", "Rural"])
    
    is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural" or user_age <= 40)
    min_cont_pct = 0.05 if is_special_cat else 0.10

    st.markdown("**Project Costs**")
    pm_cost = st.number_input("Plant & Machinery / Assets", value=1500000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_project_cost = pm_cost + wc_req
    
    min_amt_req = total_project_cost * min_cont_pct
    own_cont_amt = st.number_input(f"Own Contribution (Min {int(min_cont_pct*100)}%)", value=float(min_amt_req))
    req_loan = total_project_cost - own_cont_amt
    
    st.info(f"Total Loan Required: ₹{req_loan:,.0f}")
    
    bank_roi = st.slider("Bank Interest Rate (%)", 5.0, 15.0, 9.0)
    loan_tenure_yrs = st.slider("Loan Tenure (Years)", 1, 7, 5)

# --- 3. SCHEME ENGINE ---
results = []
if state == "Rajasthan":
    # VYUPY Logic
    if user_age <= 40:
        v_sub_rate = 8 if req_loan <= 10000000 else 7
        if is_special_cat: v_sub_rate += 1
        results.append({"Scheme": "VYUPY", "Capex Sub": min(req_loan * 0.25, 500000), "Int Sub %": v_sub_rate})

    # PMEGP Logic
    if is_new_project == "New Unit" and not has_other_subsidy:
        p_rate = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
        results.append({"Scheme": "PMEGP", "Capex Sub": total_project_cost * (p_rate / 100), "Int Sub %": 0})

# --- 4. DISPLAY & REPAYMENT ---
st.subheader("🏁 Comparative Analysis & Repayment Schedule")

if results:
    df_schemes = pd.DataFrame(results)
    st.table(df_schemes.style.format({"Capex Sub": "₹{:,.0f}", "Int Sub %": "{:.1f}%"}))
    
    selected_scheme = st.selectbox("Select Scheme for Detailed Schedule", df_schemes["Scheme"])
    scheme_info = df_schemes[df_schemes["Scheme"] == selected_scheme].iloc[0]
    
    # --- REPAYMENT CALCULATOR ---
    # Rule 2: Capex subsidy received Day 1 (Reduces Principal)
    effective_principal = req_loan - scheme_info["Capex Sub"]
    months = loan_tenure_yrs * 12
    
    # Rule 1: Fixed Principal + Monthly Interest on Outstanding
    fixed_principal = effective_principal / months
    
    schedule = []
    current_balance = effective_principal
    
    for m in range(1, months + 1):
        interest_charge = current_balance * (bank_roi / 100 / 12)
        
        # Rule 2: Interest subsidy received annually
        annual_int_sub = 0
        if scheme_info["Int Sub %"] > 0 and m % 12 == 0:
            # Calculated on the average outstanding balance for that year
            avg_bal_year = (current_balance + (current_balance + (fixed_principal * 11))) / 2
            annual_int_sub = avg_bal_year * (scheme_info["Int Sub %"] / 100)
        
        gross_payment = fixed_principal + interest_charge
        # Rule 3: Net effect (amortizing the annual subsidy monthly for display)
        monthly_sub_effect = (scheme_info["Int Sub %"] / 100 / 12) * current_balance
        net_payment = gross_payment - monthly_sub_effect
        
        schedule.append({
            "Month": m,
            "Opening Bal": current_balance,
            "Principal": fixed_principal,
            "Interest": interest_charge,
            "Gross PMT": gross_payment,
            "Net PMT (Subsidized)": net_payment,
            "Annual Rebate": annual_int_sub,
            "Closing Bal": max(0, current_balance - fixed_principal)
        })
        current_balance -= fixed_principal

    st.dataframe(pd.DataFrame(schedule).style.format({
        "Opening Bal": "₹{:,.0f}", "Principal": "₹{:,.0f}", "Interest": "₹{:,.0f}",
        "Gross PMT": "₹{:,.0f}", "Net PMT (Subsidized)": "₹{:,.0f}", 
        "Annual Rebate": "₹{:,.0f}", "Closing Bal": "₹{:,.0f}"
    }))
else:
    st.warning("Check eligibility inputs to see results.")
