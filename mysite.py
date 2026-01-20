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
    # Breakdown for the Summary Box
    capex_pm = st.number_input("Plant & Machinery", value=1500000)
    capex_furn = st.number_input("Furniture & Fixtures", value=200000)
    capex_lb = st.number_input("Land & Building (Shed)", value=300000)
    wc_req = st.number_input("Working Capital Requirement", value=500000)
    
    total_cost = capex_pm + capex_furn + capex_lb + wc_req
    
    req_term_loan = st.number_input("Required Term Loan", value=15000000) 
    req_wc_loan = st.number_input("Required WC Loan", value=3000000)
    
    loan_tenure = st.slider("Total Loan Tenure (Years)", 1, 7, 7)
    loc = st.radio("Location", ["Urban", "Rural"])
    
    st.subheader("F. Social Profile")
    gender = st.selectbox("Gender", ["Male", "Female"])
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
    edu_8th = st.checkbox("Passed 8th Standard?")

# --- 3. SCHEME ENGINE ---
results = []

# --- VYUPY Logic ---
if state == "Rajasthan":
    eligible_wc_loan = min(req_wc_loan, total_cost * 0.30)
    vyupy_loan_capped = min(req_term_loan + eligible_wc_loan, 20000000)
    
    v_base_rate = 8 if vyupy_loan_capped <= 10000000 else 7
    if (gender == "Female" or social_cat in ["SC", "ST"] or loc == "Rural"):
        v_base_rate += 1

    vyupy_int_benefit = vyupy_loan_capped * (v_base_rate / 100) * 5
    vyupy_grant_amt = min(vyupy_loan_capped * 0.25, 500000)
    
    if capex_lb <= (total_cost * 0.25):
        results.append({
            "Scheme": "VYUPY",
            "Capital %": "25% (Grant)",
            "Capital Subsidy": vyupy_grant_amt,
            "Interest %": f"{v_base_rate}%",
            "Tenure": "5 Years",
            "Interest Subsidy": vyupy_int_benefit,
            "Total Benefit": vyupy_grant_amt + vyupy_int_benefit
        })

# --- PMEGP Logic ---
if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
    is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
    if loc == "Rural":
        p_rate = 35 if is_special else 25
    else:
        p_rate = 25 if is_special else 15
    
    # Land is excluded from project cost in PMEGP
    pmegp_eligible_cost = total_cost - capex_lb
    max_limit = 5000000 if sector == "Manufacturing" else 2000000
    pmegp_sub = min(pmegp_eligible_cost, max_limit) * (p_rate / 100)
    
    results.append({
        "Scheme": "PMEGP",
        "Capital %": f"{p_rate}%",
        "Capital Subsidy": pmegp_sub,
        "Interest %": "0%",
        "Tenure": "Upfront",
        "Interest Subsidy": 0,
        "Total Benefit": pmegp_sub
    })

# --- RIPS 2024 ---
if state == "Rajasthan":
    r_rate = 8 if (gender == "Female" or social_cat != "General") else 6
    rips_int = (req_term_loan + req_wc_loan) * (r_rate / 100) * loan_tenure
    results.append({
        "Scheme": "RIPS 2024",
        "Capital %": "0%",
        "Capital Subsidy": 0,
        "Interest %": f"{r_rate}%",
        "Tenure": f"{loan_tenure} Years",
        "Interest Subsidy": rips_int,
        "Total Benefit": rips_int
    })

# --- 4. DISPLAY RESULTS ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    df = df[["Scheme", "Capital %", "Capital Subsidy", "Interest %", "Interest Subsidy", "Tenure", "Total Benefit"]]
    st.table(df.style.format({
        "Capital Subsidy": "₹{:,.0f}",
        "Interest Subsidy": "₹{:,.0f}",
        "Total Benefit": "₹{:,.0f}"
    }))
    st.success(f"🏆 Best Financial Benefit: {df.iloc[0]['Scheme']}")

    # --- NEW: PROJECT FINANCING SUMMARY BOX ---
    st.markdown("---")
    st.subheader("📋 Project Financing Summary")
    
    # Logic for Own Contribution
    is_special_cat = (gender == "Female" or social_cat != "General" or loc == "Rural")
    own_cont_pct = 0.05 if is_special_cat else 0.10
    own_cont_amt = total_cost * own_cont_pct
    total_loan_required = total_cost - own_cont_amt

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Project Cost", f"₹{total_cost:,.0f}")
        st.caption(f"(Capex: ₹{capex_pm + capex_furn + capex_lb:,.0f} + WC: ₹{wc_req:,.0f})")
    with col2:
        st.metric(f"Own Contribution ({int(own_cont_pct*100)}%)", f"₹{own_cont_amt:,.0f}")
        st.caption("Margin Money required from Beneficiary")
    with col3:
        st.metric("Total to be Matched (Loan)", f"₹{total_loan_required:,.0f}")
        st.caption("Amount to be funded via Bank Loan")

    st.info(f"📍 **Note:** Land cost of ₹{capex_lb:,.0f} has been excluded from the PMEGP subsidy calculation as per policy.")

else:
    st.error("No eligible schemes found for this profile.")
