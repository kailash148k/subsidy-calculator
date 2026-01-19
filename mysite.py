import streamlit as st
import pandas as pd

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

# --- 2. ELIGIBILITY FILTERS ---
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
    
    st.subheader("D. Financials")
    total_cost = st.number_input("Total Project Cost", value=2500000)
    land_building = st.number_input("Land & Building Portion", value=0)
    
    req_term_loan = st.number_input("Required Term Loan", value=15000000) # 1.5 Cr
    req_wc_loan = st.number_input("Required Working Capital Loan", value=3000000)
    
    # This is the loan tenure for RIPS/Ambedkar
    loan_tenure = st.slider("Total Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- 3. SCHEME ENGINE ---
results = []

# --- VYUPY Logic (Strictly 5 Years) ---
if state == "Rajasthan":
    # WC capping at 30% of project cost
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    # Total loan capped at 2 Cr for interest benefit
    vyupy_loan_capped = min(req_term_loan + eligible_wc_loan, 20000000)
    
    # Slab-based Rates
    if vyupy_loan_capped <= 10000000:
        v_base_rate = 8 
    else:
        v_base_rate = 7
        
    # Special Category Bonus (+1%)
    if (gender == "Female" or social_cat in ["SC", "ST"] or loc == "Rural"):
        v_base_rate += 1

    # FORMULA: Amount * Rate * 5 Years (Fixed Policy Tenure)
    vyupy_int_benefit = vyupy_loan_capped * (v_base_rate / 100) * 5 
    vyupy_grant = min(vyupy_loan_capped * 0.25, 500000)
    
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY",
            "Benefit Tenure": "5 Years",
            "Capital Subsidy": vyupy_grant,
            "Interest %": f"{v_base_rate}%",
            "Interest Subsidy": vyupy_int_benefit,
            "Total Benefit": vyupy_grant + vyupy_int_benefit
        })

# --- PMEGP Logic (Upfront - No Tenure) ---
if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
    is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
    p_rate = (35 if loc == "Rural" else 25) if is_special else (25 if loc == "Rural" else 15)
    
    max_limit = 5000000 if sector == "Manufacturing" else 2000000
    pmegp_sub = min(total_cost, max_limit) * (p_rate / 100)
    
    results.append({
        "Scheme": "PMEGP",
        "Benefit Tenure": "Upfront",
        "Capital Subsidy": pmegp_sub,
        "Interest %": "0%",
        "Interest Subsidy": 0,
        "Total Benefit": pmegp_sub
    })

# --- RIPS 2024 / ODOP (Full Tenure) ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate = 8 if (is_odop or gender == "Female" or social_cat != "General") else 6
    
    # FORMULA: Amount * Rate * User-selected Loan Tenure
    rips_int = (req_term_loan + req_wc_loan) * (r_rate / 100) * loan_tenure
    
    results.append({
        "Scheme": "RIPS 2024",
        "Benefit Tenure": f"{loan_tenure} Years",
        "Capital Subsidy": 0,
        "Interest %": f"{r_rate}%",
        "Interest Subsidy": rips_int,
        "Total Benefit": rips_int
    })

# --- 4. DISPLAY ---
st.subheader("🏁 Comparative Analysis")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    # Reorder columns to include Benefit Tenure
    df = df[["Scheme", "Benefit Tenure", "Interest %", "Capital Subsidy", "Interest Subsidy", "Total Benefit"]]
    
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Benefit": "₹{:,.0f}"
    }))
    
    st.info("💡 Note: VYUPY interest benefit is capped at 5 years by policy, while RIPS follows your loan tenure.")
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
