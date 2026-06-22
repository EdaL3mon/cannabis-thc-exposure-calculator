import streamlit as st
import pandas as pd
from datetime import datetime


DEFAULT_BIOAVAILABILITY = {
    "Oral oil": 0.06,
    "Capsule/tablet": 0.06,
    "Dried flower": 0.25,
    "Vape": 0.25,
    "Oromucosal spray": 0.12,
}


st.set_page_config(
    page_title="Cannabis THC Exposure Calculator",
    layout="wide"
)


def calculate_thc_mg_per_dose(route, inputs):
    """
    Calculates nominal THC in mg per dose based on route-specific product information.
    """

    if route == "Oral oil":
        thc_mg_per_dose = inputs["thc_mg_per_ml"] * inputs["ml_per_dose"]
        formula = "THC mg/mL × mL per dose"

    elif route == "Capsule/tablet":
        thc_mg_per_dose = inputs["thc_mg_per_unit"] * inputs["units_per_dose"]
        formula = "THC mg per unit × units per dose"

    elif route == "Dried flower":
        thc_mg_per_dose = inputs["thc_percent"] * inputs["grams_per_dose"] * 10
        formula = "THC % × grams per dose × 10"

    elif route == "Vape":
        thc_mg_per_dose = inputs["thc_mg_per_ml"] * inputs["ml_per_dose"]
        formula = "THC mg/mL × mL per dose"

    elif route == "Oromucosal spray":
        thc_mg_per_dose = inputs["thc_mg_per_spray"] * inputs["sprays_per_dose"]
        formula = "THC mg per spray × sprays per dose"

    else:
        raise ValueError("Unsupported route.")

    return thc_mg_per_dose, formula


def calculate_product_result(
    product_name,
    route,
    formula,
    thc_mg_per_dose,
    regular_doses_per_day,
    prn_doses_per_week,
    default_bioavailability,
    bioavailability_factor,
    custom_bioavailability_used
):
    """
    Calculates product-level nominal and bioavailability-adjusted THC exposure.
    """

    regular_thc_mg_per_day = thc_mg_per_dose * regular_doses_per_day
    prn_thc_mg_per_day = thc_mg_per_dose * prn_doses_per_week / 7
    nominal_thc_mg_per_day = regular_thc_mg_per_day + prn_thc_mg_per_day
    bioadjusted_thc_mg_per_day = nominal_thc_mg_per_day * bioavailability_factor

    return {
        "Product name": product_name,
        "Route": route,
        "Formula": formula,
        "THC per dose, mg": round(thc_mg_per_dose, 4),
        "Regular doses/day": regular_doses_per_day,
        "PRN doses/week": prn_doses_per_week,
        "Regular THC, mg/day": round(regular_thc_mg_per_day, 4),
        "PRN THC, mg/day": round(prn_thc_mg_per_day, 4),
        "Nominal THC, mg/day": round(nominal_thc_mg_per_day, 4),
        "Default bioavailability": default_bioavailability,
        "Bioavailability used": bioavailability_factor,
        "Custom bioavailability used": custom_bioavailability_used,
        "Bioavailability-adjusted THC, mg/day": round(bioadjusted_thc_mg_per_day, 4),
    }


def show_disclaimer():
    """
    Displays the scientific, clinical, and AI-assisted code development disclaimer.
    """

    st.markdown(
        """
        <div style="background-color:#fff3cd; padding:16px; border-radius:8px; border-left:6px solid #ffcc00;">

        <p><u><strong>Scientific and clinical disclaimer</strong></u></p>

        <p><em>This calculator estimates nominal THC exposure in mg/day and route-specific
        bioavailability-adjusted THC exposure in mg/day.</em></p>

        <p><em>It is intended for research, audit, and documentation standardisation only.
        It is not intended to guide cannabis initiation, prescribing, dose adjustment,
        perioperative clearance, anaesthetic dosing, or individual clinical decision-making.</em></p>

        <p><em>The calculated values do not estimate plasma THC concentration, acute intoxication,
        impairment, withdrawal risk, anaesthetic requirement, postoperative risk, or
        individual patient-level clinical effect.</em></p>

        <p><em>Bioavailability-adjusted exposure is an approximation. THC pharmacokinetics vary
        substantially by route, formulation, product composition, inhalation technique,
        oral absorption, first-pass metabolism, timing of last use, and inter-individual
        metabolic variability.</em></p>

        <p><em>Default bioavailability assumptions should be treated as modifiable research
        parameters, not fixed biological constants.</em></p>

        <p><u><strong>Scientific context</strong></u></p>

        <p><em>Medicinal cannabis product availability and prescribing pathways vary across
        products and jurisdictions, complicating standardised exposure documentation
        (Therapeutic Goods Administration, 2026; AIHW, 2024).</em></p>

        <p><em>Cannabis exposure has been associated with perioperative and anaesthetic
        considerations including sedative/anaesthetic requirements, postoperative nausea
        and vomiting, postoperative pain, opioid use, and cardiovascular risk signals in
        observational studies (Imasogie et al., 2021; Suhre et al., 2020; Liu et al., 2019;
        Goel et al., 2020; Ekrami et al., 2024; Baker et al., 2025).</em></p>

        <p><em>Route-specific THC bioavailability estimates are variable and should be interpreted
        cautiously (Hazekamp et al.; Hädener et al.; Huestis et al.).</em></p>

        <p><u><strong>AI-assisted code development statement</strong></u></p>

        <p><em>This calculator was developed with assistance from ChatGPT. The authors reviewed,
        edited, and tested the code and remain responsible for the calculator logic,
        implementation, assumptions, outputs, and interpretation. The tool should be used
        only in accordance with the stated research and documentation purposes.</em></p>

        </div>
        """,
        unsafe_allow_html=True
    )


if "products" not in st.session_state:
    st.session_state.products = []

if "form_counter" not in st.session_state:
    st.session_state.form_counter = 1

if "product_added_message" not in st.session_state:
    st.session_state.product_added_message = False


st.title("Cannabis THC Exposure Calculator")

show_disclaimer()

st.markdown(
    """
    This tool converts cannabis product information into:

    1. **Nominal THC exposure**, expressed as mg/day  
    2. **Bioavailability-adjusted THC exposure**, expressed as estimated mg/day  

    Add one product at a time. After each product is added, a fresh product form will appear.
    """
)


if st.session_state.product_added_message:
    st.success("Product added. A new blank product form has been started.")
    st.session_state.product_added_message = False


st.header("Add cannabis product")

current_form_id = st.session_state.form_counter

route = st.selectbox(
    "Product route",
    [
        "Oral oil",
        "Capsule/tablet",
        "Dried flower",
        "Vape",
        "Oromucosal spray",
    ],
    index=None,
    placeholder="Select the route",
    key=f"route_{current_form_id}"
)

if route is None:
    st.info("Select a product route to show the route-specific input fields.")

else:
    with st.form(key=f"product_form_{current_form_id}"):
        product_name = st.text_input(
            "Product name or description",
            value="",
            key=f"product_name_{current_form_id}"
        )

        st.subheader("Product concentration / amount per dose")

        inputs = {}

        if route == "Oral oil":
            inputs["thc_mg_per_ml"] = st.number_input(
                "THC concentration, mg/mL",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"oil_thc_mg_per_ml_{current_form_id}"
            )

            inputs["ml_per_dose"] = st.number_input(
                "mL per dose",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"oil_ml_per_dose_{current_form_id}"
            )

        elif route == "Capsule/tablet":
            inputs["thc_mg_per_unit"] = st.number_input(
                "THC mg per capsule/tablet",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"capsule_thc_mg_per_unit_{current_form_id}"
            )

            inputs["units_per_dose"] = st.number_input(
                "Capsules/tablets per dose",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"capsule_units_per_dose_{current_form_id}"
            )

        elif route == "Dried flower":
            inputs["thc_percent"] = st.number_input(
                "THC percentage of flower",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                key=f"flower_thc_percent_{current_form_id}"
            )

            inputs["grams_per_dose"] = st.number_input(
                "Grams per dose",
                min_value=0.0,
                value=0.0,
                step=0.01,
                key=f"flower_grams_per_dose_{current_form_id}"
            )

        elif route == "Vape":
            inputs["thc_mg_per_ml"] = st.number_input(
                "THC concentration, mg/mL",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"vape_thc_mg_per_ml_{current_form_id}"
            )

            inputs["ml_per_dose"] = st.number_input(
                "mL per dose",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"vape_ml_per_dose_{current_form_id}"
            )

        elif route == "Oromucosal spray":
            inputs["thc_mg_per_spray"] = st.number_input(
                "THC mg per spray",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"spray_thc_mg_per_spray_{current_form_id}"
            )

            inputs["sprays_per_dose"] = st.number_input(
                "Sprays per dose",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"spray_sprays_per_dose_{current_form_id}"
            )

        st.subheader("Frequency")

        regular_doses_per_day = st.number_input(
            "Regular doses per day. If none, enter 0.",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key=f"regular_doses_per_day_{current_form_id}"
        )

        prn_doses_per_week = st.number_input(
            "PRN doses per week. If none, enter 0.",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key=f"prn_doses_per_week_{current_form_id}"
        )

        st.subheader("Bioavailability")

        default_bioavailability = DEFAULT_BIOAVAILABILITY[route]

        use_custom_bioavailability = st.checkbox(
            f"Use custom bioavailability factor? Default for {route} is {default_bioavailability}.",
            key=f"use_custom_bioavailability_{current_form_id}"
        )

        if use_custom_bioavailability:
            bioavailability_factor = st.number_input(
                "Custom bioavailability factor",
                min_value=0.0,
                max_value=1.0,
                value=default_bioavailability,
                step=0.01,
                help="Enter as a decimal. For example, 0.10 means 10%.",
                key=f"custom_bioavailability_{current_form_id}"
            )
        else:
            bioavailability_factor = default_bioavailability

        submitted = st.form_submit_button("Add product")

        if submitted:
            if product_name.strip() == "":
                product_name = f"Product {len(st.session_state.products) + 1}"

            thc_mg_per_dose, formula = calculate_thc_mg_per_dose(route, inputs)

            if thc_mg_per_dose <= 0:
                st.error("Please enter product concentration and dose values greater than 0.")
                st.stop()

            if regular_doses_per_day == 0 and prn_doses_per_week == 0:
                st.error("Please enter at least one regular dose per day or PRN dose per week.")
                st.stop()

            product_result = calculate_product_result(
                product_name=product_name,
                route=route,
                formula=formula,
                thc_mg_per_dose=thc_mg_per_dose,
                regular_doses_per_day=regular_doses_per_day,
                prn_doses_per_week=prn_doses_per_week,
                default_bioavailability=default_bioavailability,
                bioavailability_factor=bioavailability_factor,
                custom_bioavailability_used=use_custom_bioavailability
            )

            st.session_state.products.append(product_result)

            st.session_state.form_counter += 1
            st.session_state.product_added_message = True
            st.rerun()


st.header("Current products")

if len(st.session_state.products) == 0:
    st.info("No products added yet.")

else:
    df = pd.DataFrame(st.session_state.products)

    st.dataframe(df, use_container_width=True)

    total_nominal = df["Nominal THC, mg/day"].sum()
    total_bioadjusted = df["Bioavailability-adjusted THC, mg/day"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Number of products", len(df))
    col2.metric("Total nominal THC", f"{total_nominal:.2f} mg/day")
    col3.metric("Total bioavailability-adjusted THC", f"{total_bioadjusted:.2f} mg/day")

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download results as CSV",
        data=csv_data,
        file_name=f"cannabis_thc_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

    if st.button("Clear all products"):
        st.session_state.products = []
        st.session_state.form_counter += 1
        st.rerun()


st.header("Default bioavailability assumptions")

bioavailability_df = pd.DataFrame(
    [
        {"Route": route_name, "Default bioavailability factor": factor}
        for route_name, factor in DEFAULT_BIOAVAILABILITY.items()
    ]
)

st.table(bioavailability_df)
