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
    
    # User-Specified Strict Rules
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"], help="PMEGP is for New Units only.")
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual (SHG/Trust/Co-op)"], help="PMEGP is for Individuals.")
    has_other_subsidy = st.checkbox("Already availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP: **{odop_item}**")
    
    sector = st.selectbox("C. Business Type", ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Financial Profile")
    capex = st.number_input("Total CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Total Working Capital (WC) Requirement", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion", value=0)
    
    req_term_loan = st.number_input("Required Term Loan", value=1500000)
    req_wc_loan = st.number_input("Required WC Loan", value=300000)
    
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
    edu_8th = st.checkbox("Passed 8th Standard?")

# --- 3. SCHEME ENGINE ---
results = []

# --- VYUPY Compliance Logic ---
if state == "Rajasthan":
    # 1. WC Loan Capping: Strictly 30% of project cost for subsidy eligibility
    eligible_wc_for_subsidy = min(req_wc_loan, total_cost * 0.30)
    
    # 2. Loan Capping: Interest subsidy strictly capped at 2 Crore loan
    vyupy_total_loan_eligible = min(req_term_loan + eligible_wc_for_subsidy, 20000000)
    
    v_int_rate = 8
    if (gender == "Female" or social_cat in ["SC", "ST"]) and vyupy_total_loan_eligible > 10000000:
        v_int_rate = 9

    # 3. Calculation Capping: Strictly calculated for first 5 years only
    vyupy_int_benefit = vyupy_total_loan_eligible * (v_int_rate / 100) * 5
    
    # 4. Project Grant: 25% Capital Grant (up to 5 Lakh)
    vyupy_capex_sub = min(vyupy_total_loan_eligible * 0.25, 500000)
    
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY",
            "Capital %": "25% (Grant)",
            "Capital Subsidy": vyupy_capex_sub,
            "Interest %": f"{v_int_rate}% (5yrs)",
            "Interest Subsidy": vyupy_int_benefit,
            "Total Combined Benefit": vyupy_capex_sub + vyupy_int_benefit
        })

# --- PMEGP Compliance Logic ---
if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
    edu_ok = True
    if sector == "Manufacturing" and total_cost > 1000000 and not edu_8th: edu_ok = False
    if sector == "Service" and total_cost > 500000 and not edu_8th: edu_ok = False

    if edu_ok:
        is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
        p_rate_val = (35 if loc == "Rural" else 25) if is_special else (25 if loc == "Rural" else 15)
        
        max_limit = 5000000 if sector == "Manufacturing" else 2000000
        pmegp_sub = min(total_cost, max_limit) * (p_rate_val / 100)
        
        results.append({
            "Scheme": "PMEGP",
            "Capital %": f"{p_rate_val}%",
            "Capital Subsidy": pmegp_sub,
            "Interest %": "0%",
            "Interest Subsidy": 0,
            "Total Combined Benefit": pmegp_sub
        })

# --- RIPS 2024 / ODOP ---
if state == "Rajasthan":
    is_odop = st.checkbox(f"Is this specifically for {odop_item}?")
    r_rate_val = 8 if (is_odop or gender == "Female" or social_cat != "General") else 6
    rips_int = (req_term_loan + req_wc_loan) * (r_rate_val / 100) * tenure
    
    results.append({
        "Scheme": "RIPS 2024",
        "Capital %": "0%",
        "Capital Subsidy": 0,
        "Interest %": f"{r_rate_val}%",
        "Interest Subsidy": rips_int,
        "Total Combined Benefit": rips_int
    })

# --- 4. DISPLAY TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Combined Benefit", ascending=False)
    df = df[["Scheme", "Capital %", "Capital Subsidy", "Interest %", "Interest Subsidy", "Total Combined Benefit"]]
    
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Combined Benefit": "₹{:,.0f}"
    }))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found. (Note: PMEGP requires New Unit/Individual Entrepreneur status)")
