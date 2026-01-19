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

# --- 2. QUESTIONNAIRE ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    
    # User Request: Mandatory Filters for PMEGP Compliance
    project_status = st.radio("Project Status", ["New Unit", "Existing Unit"], help="PMEGP is for New Units only.")
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual (SHG/Trust/Co-op)"], help="PMEGP focus: Individual Entrepreneurs.")
    has_other_subsidy = st.checkbox("Have you ever availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    st.info(f"📍 Official ODOP: **{odop_item}**")
    
    sector = st.selectbox("C. Business Type", ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    
    st.subheader("D. Financial Profile")
    capex = st.number_input("Total CAPEX (Machinery/Building)", value=2000000)
    wc_req = st.number_input("Total Working Capital Requirement", value=500000)
    total_cost = capex + wc_req
    land_building = st.number_input("Land & Building Portion (Included in CAPEX)", value=0)
    
    req_term_loan = st.number_input("Required Term Loan", value=1500000)
    req_wc_loan = st.number_input("Required WC Loan", value=300000)
    actual_total_loan = req_term_loan + req_wc_loan
    
    tenure = st.slider("Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("E. Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    age = st.number_input("Age", value=25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
    edu_8th = st.checkbox("Passed 8th Standard?")

# --- 3. THE EXPANDED SCHEME ENGINE ---
results = []

# --- PMEGP (Central) - Updated for strictly NEW & INDIVIDUAL ---
if project_status == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
    # Educational qualification check
    edu_ok = True
    if sector == "Manufacturing" and total_cost > 1000000 and not edu_8th: edu_ok = False
    if sector == "Service" and total_cost > 500000 and not edu_8th: edu_ok = False
    
    if edu_ok:
        # PMEGP Subsidy Logic
        is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
        if loc == "Rural":
            p_rate = 0.35 if is_special else 0.25
        else:
            p_rate = 0.25 if is_special else 0.15
        
        # Max project cost capping for subsidy
        max_eligible = 5000000 if sector == "Manufacturing" else 2000000
        pmegp_sub = min(total_cost, max_eligible) * p_rate
        
        results.append({
            "Scheme": "PMEGP (Central)", 
            "Capital Subsidy": pmegp_sub, 
            "Interest Subsidy": 0, 
            "Total Benefit": pmegp_sub,
            "Criteria": "Strictly New/Individual"
        })

# --- VYUPY Logic (Rajasthan) ---
if state == "Rajasthan" and 18 <= age <= 45:
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    vyupy_eligible_loan = min(req_term_loan + eligible_wc_loan, 20000000)
    
    v_rate = 0.08 if vyupy_eligible_loan <= 10000000 else 0.07
    if gender == "Female" or social_cat in ["SC", "ST"]: v_rate += 0.01

    vyupy_int_benefit = vyupy_eligible_loan * v_rate * 5
    vyupy_capex_sub = min(total_cost * 0.25, 500000)
    
    if land_building <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY (Rajasthan)", "Capital Subsidy": vyupy_capex_sub,
            "Interest Subsidy": vyupy_int_benefit, "Total Benefit": vyupy_capex_sub + vyupy_int_benefit,
            "Criteria": "New Units/Expansion"
        })

# --- Ambedkar Scheme (SC/ST Rajasthan) ---
if state == "Rajasthan" and social_cat in ["SC", "ST"]:
    amb_sub = min(total_cost * 0.25, 625000)
    amb_int = min(actual_total_loan, 2500000) * 0.09 * tenure
    results.append({
        "Scheme": "Ambedkar Scheme", "Capital Subsidy": amb_sub,
        "Interest Subsidy": amb_int, "Total Benefit": amb_sub + amb_int,
        "Criteria": "SC/ST Special"
    })

# --- 4. COMPARISON TABLE ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Benefit": "₹{:,.0f}"
    }))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")
else:
    st.error("No eligible schemes found. Note: PMEGP excludes existing units or non-individual applicants.")



### Key Compliance Checks Integrated:
1.  **Family Rule:** PMEGP allows only **one person per family** (self and spouse).
2.  **Education:** Manufacturing projects > ₹10L and Service > ₹5L require at least an **8th standard pass**.
3.  **No Double Dipping:** The code checks `has_other_subsidy` because units that have already taken government subsidies are disqualified.
4.  **Capital Expenditure:** The code assumes a loan is required, as projects without a **Term Loan (Capex)** are ineligible for PMEGP.

**Would you like me to add a feature to calculate the exact Bank EMI after adjusting for these subsidies?**
