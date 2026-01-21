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
    
    st.markdown("### D. Financials")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    user_age = st.number_input("Enter Applicant Age", min_value=18, max_value=100, value=25)
    loc = st.radio("Location", ["Urban", "Rural"])
    
    is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural" or user_age <= 40)
    min_cont_pct = 0.05 if is_special_cat else 0.10

    pm_cost = st.number_input("Plant & Machinery / Assets", value=1500000)
    wc_req = st.number_input("Working Capital", value=500000)
    total_project_cost = pm_cost + wc_req
    
    own_cont_amt = st.number_input(f"Own Contribution (Min {int(min_cont_pct*100)}%)", value=float(total_project_cost * min_cont_pct))
    req_loan = total_project_cost - own_cont_amt
    
    bank_roi = st.slider("Bank Interest Rate (%)", 5.0, 15.0, 9.0)
    loan_tenure_yrs = st.slider("Loan Tenure (Years)", 1, 7, 5)

# --- 3. HELPER FUNCTION FOR TOTAL INTEREST SUBSIDY ---
def calc_total_int_sub(principal, roi_sub_pct, tenure_yrs):
    if roi_sub_pct <= 0: return 0
    # Formula for total interest subsidy on a reducing balance with fixed principal
    months = tenure_yrs * 12
    fixed_principal = principal / months
    total_sub = 0
    curr_bal = principal
    for _ in range(months):
        total_sub += curr_bal * (roi_sub_pct / 100 / 12)
        curr_bal -= fixed_principal
    return total_sub

# --- 4. SCHEME ENGINE ---
results = []
if state == "Rajasthan":
    # VYUPY Logic
    if user_age <= 40:
        v_sub_rate = 8 if req_loan <= 10000000 else 7
        if is_special_cat: v_sub_rate += 1
        capex = min(req_loan * 0.25, 500000)
        # Interest sub applies to loan amount remaining after capex sub
        int_sub_amt = calc_total_int_sub(req_loan - capex, v_sub_rate, 5) # VYUPY usually 5 years
        results.append({
            "Scheme": "VYUPY", 
            "Capex Subsidy": capex, 
            "Int. Sub %": f"{v_sub_rate}%", 
            "Interest Subsidy (Amt)": int_sub_amt,
            "Total Benefit": capex + int_sub_amt
        })

    # PMEGP Logic
    if is_new_project == "New Unit" and not has_other_subsidy:
        p_rate = (35 if loc == "Rural" else 25) if is_special_cat else (25 if loc == "Rural" else 15)
        capex = total_project_cost * (p_rate / 100)
        results.append({
            "Scheme": "PMEGP", 
            "Capex Subsidy": capex, 
            "Int. Sub %": "0%", 
            "Interest Subsidy (Amt)": 0,
            "Total Benefit": capex
        })

# --- 5. DISPLAY ---
st.subheader("🏁 Comparative Analysis of Total Benefits")

if results:
    df_schemes = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    # Applying the Rupee formatting
    st.table(df_schemes.style.format({
        "Capex Subsidy": "₹{:,.0f}", 
        "Interest Subsidy (Amt)": "₹{:,.0f}", 
        "Total Benefit": "₹{:,.0f}"
    }))
    
    # Repayment section follows as before...
    st.markdown("---")
    selected_scheme = st.selectbox("Select Scheme for Detailed Repayment Schedule", df_schemes["Scheme"])
    # [Repayment schedule logic remains same as previous version]
else:
    st.warning("No eligible schemes found. Please check eligibility criteria.")
