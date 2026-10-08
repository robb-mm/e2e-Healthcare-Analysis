import streamlit as st
import plotly.express as px
import pandas as pd

st.title("Healthcare Analysis")
st.write(f"Welcome, {st.user.user_name}!")

conn = st.connection("snowflake")

df = conn.query("""
    SELECT  DISTINCT HOSPITAL_NAME, NO_COMPLETED_SURVEYS
    FROM    SNOWPARK_DEMO_DB.PUBLIC.FACT_PATIENT_SURVEY ps
    JOIN    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL h
    ON      ps.hospital_key = h.hospital_key
    WHERE   NO_COMPLETED_SURVEYS IS NOT NULL
    ORDER BY NO_COMPLETED_SURVEYS
""")

# selected_regions = st.multiselect(
#     "Filter by region",
#     options=df["REGION"].unique(),
#     default=df["REGION"].unique(),
# )

# filtered = df[df["REGION"].isin(selected_regions)]
# total = filtered["REVENUE"].sum()
# st.metric("Total Revenue", f"${total:,.0f}")

st.markdown("##### 1. Number of Surveys Completed by Hospitals (Top 10)")
fig = px.bar(
    df.iloc[-10:],#.sort_values("NO_COMPLETED_SURVEYS", ascending=True),
    x="NO_COMPLETED_SURVEYS",
    y="HOSPITAL_NAME",
    orientation="h",
    # title="#### Number of Surveys Completed by Hospitals (Top 10)",
    labels={"NO_COMPLETED_SURVEYS":"Number of Surveys Completed", "HOSPITAL_NAME":"Hospital Name"},
    hover_data={"HOSPITAL_NAME":False}
)
st.plotly_chart(fig, width='stretch')

st.markdown("##### 2. Survey Response rate based on Measure id")

df = conn.query("""
    SELECT  h.PROVIDER_ID,
            h.HOSPITAL_NAME as HOSPITAL,
            m.MEASURE_CODE,
            ps.SURVEY_RESPONSE_RATE_PERCENT as SURVEY_RATE
    FROM    SNOWPARK_DEMO_DB.PUBLIC.FACT_PATIENT_SURVEY ps
    JOIN    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL h
    ON      ps.hospital_key = h.hospital_key
    JOIN    SNOWPARK_DEMO_DB.PUBLIC.DIM_MEASURE m
    ON      ps.measure_key = m.measure_key
    ORDER BY 1, 2, 3 DESC;
""")

# --- Streamlit UI ---
hospital = st.selectbox("Select Hospital", df["HOSPITAL"].unique())
subset = df[df['HOSPITAL']==hospital]

fig = px.bar(
    subset,#.sort_values("MEASURE_CODE"),
    x="SURVEY_RATE",
    y="MEASURE_CODE",
    orientation="h",
    # title="Max Survey Response Rate Per County (Top 3)",
    labels={"SURVEY_RATE":"Survey Response Rate", "MEASURE_CODE":"Measure Id"},
    # hover_data={"MEASURE_CODE":False}
)
st.plotly_chart(fig, width='stretch')

df = conn.query("""
    SELECT  COUNTY, MAX(SURVEY_RESPONSE_RATE_PERCENT) AS MAX_SURVEY_RATE
    FROM    SNOWPARK_DEMO_DB.PUBLIC.FACT_PATIENT_SURVEY ps
    JOIN    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL h
    ON      ps.hospital_key = h.hospital_key
    WHERE   SURVEY_RESPONSE_RATE_PERCENT IS NOT NULL
    GROUP BY COUNTY
    ORDER BY 2 DESC
    LIMIT 3;
""")

st.markdown("##### 3. Top 3 Counties which have the highest survey rate")
fig = px.bar(
    df.sort_values("MAX_SURVEY_RATE"),
    x="MAX_SURVEY_RATE",
    y="COUNTY",
    orientation="h",
    # title="Max Survey Response Rate Per County (Top 3)",
    labels={"MAX_SURVEY_RATE":"Max Survey Response Rate", "COUNTY":"County"},
    hover_data={"COUNTY":False}
)
st.plotly_chart(fig, width='stretch')

st.markdown("##### 4. Top 10 hospitals based on Survey Response Rate")
df = conn.query("""
    SELECT  PROVIDER_ID, HOSPITAL_NAME, MAX(SURVEY_RESPONSE_RATE_PERCENT) as SURVEY_RATE
    FROM    SNOWPARK_DEMO_DB.PUBLIC.FACT_PATIENT_SURVEY ps
    JOIN    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL h
    ON      ps.hospital_key = h.hospital_key
    WHERE   SURVEY_RESPONSE_RATE_PERCENT IS NOT NULL
    GROUP BY PROVIDER_ID, HOSPITAL_NAME
    ORDER BY 3 DESC
    LIMIT 10;
""")

fig = px.bar(
    df.sort_values("SURVEY_RATE"),
    x="SURVEY_RATE",
    y="HOSPITAL_NAME",
    orientation="h",
    # title="Max Survey Response Rate Per County (Top 3)",
    labels={"SURVEY_RATE":"Survey Response Rate", "HOSPITAL_NAME":"Hospital"},
    hover_data={"HOSPITAL_NAME":False}
)
st.plotly_chart(fig, width='stretch')

# st.title("🏥 Hospital Ratings Drill‑Down Report")
df = conn.query("""
    SELECT  County, CITY, Hospital_Name AS HOSPITAL, ROUND(AVG(PATIENT_SURVEY_STAR_RATING), 2) AS RATING
    FROM    SNOWPARK_DEMO_DB.PUBLIC.FACT_PATIENT_SURVEY ps
    JOIN    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL h
    ON      ps.hospital_key = h.hospital_key
    GROUP BY COUNTY, CITY, HOSPITAL
""")

st.markdown("##### 5. County and city wise hospital rating through drill down report")
# # --- Pre-aggregate means for County and City ---
# county_mean = df.groupby("COUNTY", as_index=False)["RATING"].mean()
# city_mean   = df.groupby(["COUNTY","CITY"], as_index=False)["RATING"].mean()

# # Add placeholders for hierarchy consistency
# county_mean = county_mean.assign(CITY=None, HOSPITAL=None)
# city_mean   = city_mean.assign(HOSPITAL=None)

# # Combine into one dataframe
# df_mean = pd.concat([county_mean, city_mean, df])

# --- Streamlit UI ---
# county = st.selectbox("Select County", df["COUNTY"].unique())
# cities = df[df["COUNTY"] == county]["CITY"].unique()
# city   = st.selectbox("Select City", cities)

# # subset = df_mean[(df_mean["COUNTY"] == county) & 
# #                  ((df_mean["CITY"].isna()) | (df_mean["CITY"] == city))]
# subset = df[(df["COUNTY"] == county) & (df["CITY"] == city)]

# fig = px.sunburst(subset,
#                   path=['COUNTY','CITY','HOSPITAL'],
#                   values='RATING',
#                   color='RATING',
#                   color_continuous_scale='RdYlGn',
#                   title=f"{city} Hospitals in {county}",
#                   custom_data=['HOSPITAL', 'RATING'])
# fig.update_traces(hovertemplate="%{customdata[0]}<br>Rating: %{customdata[1]}")
# st.plotly_chart(fig, width='stretch')

# # --- Compute aggregates separately ---
# county_mean = df.groupby("COUNTY", as_index=False)["RATING"].mean()
# county_mean["CITY"] = None
# county_mean["HOSPITAL"] = None
# county_mean["LEVEL"] = "County"

# city_mean = df.groupby(["COUNTY","CITY"], as_index=False)["RATING"].mean()
# city_mean["HOSPITAL"] = "All Hospitals"

# # --- Combine hospital + city mean + county mean ---
# df = pd.concat([df, city_mean, county_mean], ignore_index=True)

# # --- Streamlit UI ---
# county = st.selectbox("Select County", df["COUNTY"].unique())
# cities = df[df["COUNTY"] == county]["CITY"].unique()
# city   = st.selectbox("Select City", cities)

# subset = df[(df["COUNTY"] == county) & ((df["CITY"] == city) | (df["CITY"] == "All Cities"))] #(df["CITY"] == city)] #
# # if subset['CITY'].unique() !='ALL':
# #     subset = subset.drop(subset[subset['HOSPITAL']=='ALL'].index)

# # --- Sunburst chart ---
# fig = px.sunburst(
#     subset,
#     path=['COUNTY','CITY','HOSPITAL'],
#     values='RATING',
#     color='RATING',
#     color_continuous_scale='RdYlGn',
#     title=f"{city} Hospitals in {county}",
#     custom_data=['COUNTY','CITY','HOSPITAL','RATING']
# )

# # --- Tooltip logic ---
# fig.update_traces(
#     hovertemplate=(
#         # "County: %{customdata[0]}<br>"
#         # "City: %{customdata[1]}<br>"
#         # "Hospital: %{customdata[2]}<br>"
#         # "Rating: %{customdata[3]}<extra></extra>"
#         "%{customdata[2]}<br>"
#         "Rating: %{customdata[3]:.2f}<extra></extra>"
#     )
# )

# # Override tooltips for County/City aggregate nodes
# for i, node in enumerate(fig.data[0].customdata):
#     county_val, city_val, hospital_val, rating = node
#     if hospital_val is None:  # County mean
#         fig.data[0].hovertemplate[i] = f"County: {county_val}<br>Mean Rating: {rating}<extra></extra>"
#     elif hospital_val == "All Hospitals":  # City mean
#         fig.data[0].hovertemplate[i] = f"City: {city_val}<br>Mean Rating: {rating}<extra></extra>"
# --- Compute aggregates ---
county_mean = df.groupby("COUNTY", as_index=False)["RATING"].mean().round(2)
county_mean["CITY"] = None
county_mean["HOSPITAL"] = None
county_mean["LEVEL"] = "County"

city_mean = df.groupby(["COUNTY","CITY"], as_index=False)["RATING"].mean().round(2)
city_mean["HOSPITAL"] = None
city_mean["LEVEL"] = "City"

df["LEVEL"] = "Hospital"

# Combine into one dataframe
df_all = pd.concat([county_mean, city_mean, df], ignore_index=True)

# --- Streamlit UI ---
county = st.selectbox("Select County", df["COUNTY"].unique())
cities = df[df["COUNTY"] == county]["CITY"].unique()
city   = st.selectbox("Select City", cities)

subset = df_all[(df_all["COUNTY"] == county) &
                ((df_all["CITY"].isna()) | (df_all["CITY"] == city))]

# --- Show aggregate metrics separately ---
# county_mean = subset["RATING"].mean()
# city_mean   = subset.groupby("CITY")["RATING"].mean().iloc[0]

# --- Sunburst chart ---
fig = px.sunburst(
    subset.drop(subset[subset["HOSPITAL"].isna()].index),
    path=['COUNTY','CITY','HOSPITAL'],
    values='RATING',
    color='RATING',
    color_continuous_scale='RdYlGn',
    title=f"{city} Hospitals in {county}",
    custom_data=['LEVEL','COUNTY','CITY','HOSPITAL','RATING']
)

# --- Tooltip logic ---
fig.update_traces(
    hovertemplate=(
        "%{customdata[0]}: "
        # "%{customdata[1]} "
        # "%{customdata[2]} "
        "%{customdata[3]}<br>"
        "Rating: %{customdata[4]:.2f}<extra></extra>"
    )
)

st.plotly_chart(fig, width='stretch')

st.dataframe(subset[subset['RATING'].notna()].sort_values(['LEVEL','RATING'], ascending=[False,False], ignore_index=True), width='stretch', column_config={'_index':None})

st.markdown("##### 6. Hospitals in the same city")

df = conn.query("""
    WITH CITY_HOSPITALS AS (
        SELECT  CITY, STATE, COUNT(DISTINCT HOSPITAL_NAME)
        FROM    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL
        GROUP BY CITY, STATE
        HAVING COUNT(DISTINCT HOSPITAL_NAME) > 1
    )
    SELECT  h.CITY, h.STATE, h.HOSPITAL_NAME as HOSPITAL
    FROM    SNOWPARK_DEMO_DB.PUBLIC.DIM_HOSPITAL h
    JOIN    CITY_HOSPITALS ch
    ON      h.city = ch.city
    AND     h.state = ch.state
    ORDER BY 1, 2;
""")
# --- Streamlit UI ---
city = st.selectbox("Select City", df["CITY"].unique())

subset = df[df["CITY"] == city]

st.dataframe(df[df["CITY"] == city], width='stretch', column_config={'_index':None})

st.markdown("##### 7. Average Survey Response rate by all the Hospitals")

df = conn.query("""
    SELECT  AVG(SURVEY_RESPONSE_RATE_PERCENT) AS AVG_SURVEY_RESPONSE_RATE
    FROM (
        SELECT DISTINCT
            HOSPITAL_KEY,
            SURVEY_RESPONSE_RATE_PERCENT
        FROM SNOWPARK_DEMO_DB.PUBLIC.FACT_PATIENT_SURVEY
    );
""")

st.markdown(f"{df['AVG_SURVEY_RESPONSE_RATE'][0]:.2f}")
