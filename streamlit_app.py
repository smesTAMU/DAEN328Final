import os
from dotenv import load_dotenv
import pandas as pd
import datetime
import pydeck as pdk
import plotly.express as px
import re
import streamlit as st
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Connect using env vars
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

st.set_page_config(page_title="Full Inspection App", layout="wide")
st.title("Food Inspection Dashboard")

tab1, tab2, tab3 = st.tabs(["Raw Data Filter", "Inspection Dashboard", "Inspection Map Viewer"])

@st.cache_data
def load_filtered_data():
    query = """
        SELECT 
            i.inspection_id, i.inspection_date, i.inspection_type, i.risk, i.results, i.violations,
            f.dba_name
        FROM inspections AS i
        JOIN facilities AS f
        ON i.license_number = f.license_number;
    """
    df = pd.read_sql(query, engine)
    recent_date = datetime.date.today() - datetime.timedelta(days=730)
    df = df[df["inspection_date"] >= pd.to_datetime(recent_date)]
    return df.head(3000)

@st.cache_data
def load_map_data():
    query = """
        SELECT
            f.latitude,
            f.longitude,
            i.results,
            i.inspection_date,
            f.facility_type,
            f.dba_name,
            i.risk
        FROM facilities AS f
        JOIN inspections AS i
        ON i.license_number = f.license_number
        WHERE
            i.results IN ('Pass', 'Fail');
    """
    df = pd.read_sql(query, engine)
    df = df.dropna(subset=["latitude", "longitude"])
    recent_date = datetime.date.today() - datetime.timedelta(days=730)
    df = df[df["inspection_date"] >= pd.to_datetime(recent_date)]
    df["inspection_date"] = pd.to_datetime(df["inspection_date"]).dt.strftime("%Y-%m-%d")
    return df

# === Raw Data Filter Tab ===
with tab1:
    df = load_filtered_data()

    st.markdown("### Raw Data Viewer with Filters")

    with st.sidebar:
        st.markdown("### Filter Inspections")
        with st.expander("Filter by Result", expanded=True):
            result_options = sorted(df["results"].dropna().unique())
            result_filter = st.multiselect("Choose result(s):", options=result_options, default=result_options, key="raw_result_filter")
        with st.expander("Filter by Risk", expanded=True):
            risk_options = sorted(df["risk"].dropna().unique())
            risk_filter = st.multiselect("Choose risk level(s):", options=risk_options, default=risk_options, key="raw_risk_filter")

    filtered_df = df[df["results"].isin(result_filter) & df["risk"].isin(risk_filter)]
    st.subheader("Filtered Results From the Past 3 Years")
    st.dataframe(filtered_df, use_container_width=True)

# === Dashboard Tab ===
with tab2:
    df = load_filtered_data()

    st.markdown("### Inspection Summary Charts")
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df["results"].value_counts())
        st.caption("Distribution of inspection results (Pass, Fail, etc.) to evaluate performance.")
    with col2:
        st.bar_chart(df["risk"].value_counts())
        st.caption("Frequency of risk levels to help prioritize high-risk inspections.")

    with st.container():
        st.markdown("#### Top 10 Violation Entries")
        violation_counts = df["violations"].value_counts().head(10).reset_index()
        violation_counts.columns = ["violation", "count"]
        violation_counts["label"] = violation_counts["violation"].apply(
            lambda x: x.split(":")[0][:25] + "..." if len(x) > 30 else x.split(":")[0]
        )
        fig = px.pie(
            violation_counts,
            names="label",
            values="count",
            hover_data=["violation"],
            hole=0.4
        )
        fig.update_traces(textinfo='percent')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("This pie chart shows which violations are most common, by percentage.")

    st.markdown("### Violations by Business (DBA)")
    selected_dba = st.selectbox("Choose a Business (DBA):", sorted(df["dba_name"].dropna().unique()))
    dba_df = df[df["dba_name"] == selected_dba]
    st.dataframe(dba_df[["inspection_date", "inspection_type", "risk", "results", "violations"]], use_container_width=True)

    if dba_df["violations"].notna().any():
        dba_violation_counts = dba_df["violations"].value_counts().head(10).reset_index()
        dba_violation_counts.columns = ["Violation", "Count"]
        st.bar_chart(dba_violation_counts.set_index("Violation"))
        st.caption("This visualization provides a breakdown of the most frequent violations by the selected business, helping identify recurring compliance issues.")
        
    with st.container():
        st.markdown("#### Violation Type vs. Result Outcome")

        outcome_df = df[["violations", "results"]].dropna()

        # Extract violation number
        outcome_df["violation_number"] = outcome_df["violations"].apply(
            lambda x: int(re.match(r"^(\d+)", x.strip()).group(1)) if re.match(r"^(\d+)", x.strip()) else None
        )

        # Extract violation text
        outcome_df["violation_text"] = outcome_df["violations"].apply(
            lambda x: x.split('.', 1)[1].strip() if '.' in x else x.strip()
        )

        # Drop rows without violation number
        outcome_df = outcome_df.dropna(subset=["violation_number"])

        # Group by violation text and result
        grouped = outcome_df.groupby(["violation_text", "results"]).size().reset_index(name="Count")

        # Optional: Focus on top 20 violation types
        top_violations = grouped["violation_text"].value_counts().nlargest(20).index
        grouped = grouped[grouped["violation_text"].isin(top_violations)]

        # Optional: Truncate long text for nicer appearance (optional)
        grouped["violation_text"] = grouped["violation_text"].apply(lambda x: (x[:60] + '...') if len(x) > 60 else x)

        # Now create a horizontal bar chart
        fig = px.bar(
            grouped,
            y="violation_text",
            x="Count",
            color="results",
            title="Top Violation Types vs. Result Outcome",
            orientation="h",  # <-- horizontal bars
        )

        fig.update_layout(
            yaxis_title="Violation Type",
            xaxis_title="Count",
            yaxis={'categoryorder':'total ascending'},  # Sort from top to bottom
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption("This horizontal stacked bar chart shows the most common violation types and their inspection outcomes.")

        st.markdown("#### Violation Number Legend")
        full_violations = outcome_df.dropna(subset=["violation_number"]).drop_duplicates(subset=["violation_number"])
        legend_df = full_violations[["violation_number", "violations"]].sort_values("violation_number")
        legend_df["Description"] = legend_df["violations"].apply(lambda x: " ".join(re.findall(r"\b[A-Z\s]{2,}\b", x.strip())))
        st.dataframe(legend_df[["violation_number", "Description"]], use_container_width=True)

# === Map Viewer Tab ===
with tab3:
    df_map = load_map_data()
    st.subheader("Map of inspections over the last 3 years")

    base_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position='[longitude, latitude]',
        get_radius=80,
        get_fill_color='[0, 128, 255, 160]',
        pickable=True,
        auto_highlight=True,
    )
    tooltip = {
        "html": "<b>DBA:</b> {dba_name} <br/>"
                "<b>Facility Type:</b> {facility_type} <br/>"
                "<b>Result:</b> {results} <br/>"
                "<b>Date:</b> {inspection_date}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    view_state = pdk.ViewState(
        latitude=df_map["latitude"].mean(),
        longitude=df_map["longitude"].mean(),
        zoom=11,
        pitch=0,
    )
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[base_layer],
        tooltip=tooltip,
    ))
    st.caption("This map shows the geographic spread of inspections. Hover for details.")

    st.markdown("#### Violation Hotspots by Risk Level")
    if "risk" in df_map.columns:
        df_map["weight"] = df_map["risk"].apply(lambda r: {"High": 3, "Medium": 2, "Low": 1}.get(r, 1))
        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=df_map,
            get_position='[longitude, latitude]',
            get_weight='weight',
            radiusPixels=60,
        )
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v9",
            initial_view_state=view_state,
            layers=[heatmap_layer],
        ))
        st.caption("This heatmap reveals areas with the most serious violations.")
