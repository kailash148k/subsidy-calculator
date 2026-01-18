# --- E. PM Vishwakarma (Expanded) ---
if sector == "Traditional Artisan":
    vishwa_grant = 15000  # Toolkit grant
    training_stipend = 500 * 15  # Approx 15 days training
    # Loan benefit: 5% vs Market 12%
    vishwa_interest_saving = min(cost, 300000) * 0.07 * 5 
    results.append({
        "Scheme": "PM Vishwakarma", 
        "Benefit Type": "Grant + Interest Subvention", 
        "Value": vishwa_grant + training_stipend + vishwa_interest_saving, 
        "Details": "Toolkit + ₹500/day Stipend + 5% Interest Loan"
    })

# --- F. ODOP (One District One Product) ---
is_odop = st.sidebar.checkbox("Is this an ODOP product?")
if is_odop:
    odop_sub = min(cost * 0.25, 2000000) # Assuming 25% capped at 20L
    results.append({
        "Scheme": "ODOP Subsidy", 
        "Benefit Type": "Machinery Grant", 
        "Value": odop_sub, 
        "Details": "25% Subsidy for District-Specific Products"
    })

# --- G. Stand-Up India (SC/ST/Women) ---
if is_special and cost >= 1000000:
    # Logic for 15% margin money assistance
    standup_benefit = cost * 0.15
    results.append({
        "Scheme": "Stand-Up India", 
        "Benefit Type": "Margin Money Support", 
        "Value": standup_benefit, 
        "Details": "15% Composite Loan Subsidy"
    })
