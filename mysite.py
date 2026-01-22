import streamlit as st
import pandas as pd

# --- 1. RAJASTHAN ODOP DATA ---
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
st.title("⚖️ Rajasthan MSME Subsidy Comparison Tool (20jan26-final)")

# --- 2. LOCKED INPUT SECTION ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    # Presentation and input boxes are locked/finalized
    is_new_project = st.radio("Project Status", ["New Unit", "Existing Unit"])
    applicant_type = st.radio("Applicant Category", ["Individual Entrepreneur", "Non-Individual"])
    has_other_subsidy = st.checkbox("Already availed other Govt. Subsidies?")
    
    st.markdown("---")
    state = st.selectbox("State", ["Rajasthan", "Other"])
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    odop_item = rajasthan_odop[district]
    
    sector = st.selectbox("Sector", ["Manufacturing", "Service", "Food Processing"])
    
    st.markdown("### D. Financials")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    loc = st.radio("Location", ["Urban", "Rural"])
    
    # Official Contribution Logic
    is_special = (gender == "Female" or social_cat != "General" or loc == "Rural")
    min_cont_pct = 0.05 if is_special else 0.10

    # Side-by-side Layout
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**Project Cost (Assets)**")
        pm_cost = st.number_input("Plant & Machinery", value=3200000)
        furn_cost = st.number_input("Furniture & Fixtures", value=200000)
        lb_cost = st.number_input("Workshed / Building", value=0)
        wc_req = st.number_input("Working Capital Req.", value=190000)
        total_project_cost = pm_cost + furn_cost + lb_cost + wc_req
        st.info(f"Total Project Cost: ₹{total_project_cost:,.0f}")

    with col_right:
        st.markdown("**Means of Finance (Funding)**")
        min_amt_req = total_project_cost * min_cont_pct
        own_cont_amt = st.number_input(f"Own Contribution (Min {int(min_cont_pct*100)}%)", value=float(min_amt_req))
        
        if own_cont_amt < min_amt_req:
            st.error(f"⚠️ Minimum contribution required: ₹{min_amt_req:,.0f}")
        
        req_term_loan = st.number_input("Term Loan Required", value=float(pm_cost + furn_cost + lb_cost - own_cont_amt))
        req_wc_loan = st.number_input("Working Capital Loan", value=float(wc_req))
        total_funding = own_cont_amt + req_term_loan + req_wc_loan
        st.info(f"Total Funding: ₹{total_funding:,.0f}")

# --- 3. SCHEME ENGINE ---
results = []
if total_project_cost == total_funding and own_cont_amt >= min_amt_req:
    # --- PMEGP Logic ---
    if is_new_project == "New Unit" and applicant_type == "Individual Entrepreneur" and not has_other_subsidy:
        p_rate = (35 if loc == "Rural" else 25) if is_special else (25 if loc == "Rural" else 15)
        # Land excluded from subsidy
        pmegp_eligible = total_project_cost - lb_cost
        max_limit = 5000000 if sector == "Manufacturing" else 2000000
        pmegp_sub = min(pmegp_eligible, max_limit) * (p_rate / 100)
        results.append({"Scheme": "PMEGP", "Benefit": f"{p_rate}% Capital Grant", "Capital Subsidy": pmegp_sub, "Total Benefit": pmegp_sub})

    # --- Rajasthan VYUPY Logic ---
    if state == "Rajasthan":
        vyupy_loan = min(req_term_loan + req_wc_loan, 20000000)
        v_rate = 8 if vyupy_loan <= 10000000 else 7
        if is_special: v_rate += 1
        vyupy_int_sub = vyupy_loan * (v_rate / 100) * 5 # 5 Year subvention
        vyupy_grant = min(vyupy_loan * 0.25, 500000)
        results.append({"Scheme": "VYUPY", "Benefit": "Grant + Interest Sub.", "Capital Subsidy": vyupy_grant, "Total Benefit": vyupy_grant + vyupy_int_sub})

# --- 4. PRESENTATION DISPLAY ---
st.subheader("🏁 Comparative Analysis of Subsidies")
if results:
    df = pd.DataFrame(results).sort_values(by="Total Benefit", ascending=False)
    st.table(df.style.format({"Capital Subsidy": "₹{:,.0f}", "Total Benefit": "₹{:,.0f}"}))

    st.markdown("---")
    st.subheader("📋 Project Financing Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Project Cost", f"₹{total_project_cost:,.0f}")
    c2.metric(f"Own Contribution ({int((own_cont_amt/total_project_cost)*100)}%)", f"₹{own_cont_amt:,.0f}")
    c3.metric("Bank Loan Required", f"₹{(req_term_loan + req_wc_loan):,.0f}")
