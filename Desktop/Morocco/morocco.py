import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA

# --- Page Config ---
st.set_page_config(page_title="Morocco Zone Dashboard", layout="wide")

# --- Load Data ---
import os
file_path = os.path.join(os.path.dirname(__file__), "Data Morocco.xlsx")
df = pd.read_excel(file_path)
df["DateTime"] = pd.to_datetime(df["DateTime"])

# --- Sidebar Controls ---
st.sidebar.title("Controls")
zone = st.sidebar.selectbox(
    "Select Zone", ["zone1", "zone2", "zone3", "zone4", "zone5"]
)
start_date = st.sidebar.date_input("Start Date", df["DateTime"].min())
end_date = st.sidebar.date_input("End Date", df["DateTime"].max())
pca_mode = st.sidebar.selectbox("Select PCA View", ["2D", "3D", "4D"])

# --- Filter Data ---
df = df[
    (df["DateTime"] >= pd.to_datetime(start_date))
    & (df["DateTime"] <= pd.to_datetime(end_date))
]

# --- Scale Features ---
features = df[["zone1", "zone2", "zone3", "zone4", "zone5"]]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)
df_scaled = pd.DataFrame(X_scaled, columns=features.columns)
df_scaled["DateTime"] = df["DateTime"]

# --- Clustering ---
kmeans = KMeans(n_clusters=3, random_state=42)
df_scaled["Cluster"] = kmeans.fit_predict(df_scaled[features.columns])

# --- Time Features ---
df_scaled["Hour"] = df_scaled["DateTime"].dt.hour
df_scaled["Weekday"] = df_scaled["DateTime"].dt.dayofweek

# --- Anomaly Detection ---
iso_forest = IsolationForest(contamination=0.05, random_state=42)
df_scaled["Anomaly"] = iso_forest.fit_predict(
    df_scaled[features.columns.tolist() + ["Hour", "Weekday"]]
)

# --- PCA ---
pca = PCA(n_components=3)
pca_result = pca.fit_transform(df_scaled[features.columns])
df_scaled["PCA1"] = pca_result[:, 0]
df_scaled["PCA2"] = pca_result[:, 1]
df_scaled["PCA3"] = pca_result[:, 2]

# --- Styled Header ---
st.markdown(
    """
<div style='background-color:#f9fafb; padding:20px; border-radius:12px; border:1px solid #e5e7eb'>
    <h2 style='color:#3b82f6; font-family:sans-serif;'> Morocco Zone Dashboard</h2>
    <p style='color:#374151;'>Visualize zone trends, detect anomalies, and explore clustering insights.</p>
</div>
""",
    unsafe_allow_html=True,
)

# --- Layout: Chart + Metrics ---
col1, col2 = st.columns([3, 1])

with col1:
    fig = px.line(
        df_scaled,
        x="DateTime",
        y=zone,
        color=df_scaled["Cluster"].astype(str),
        title=f"{zone} Over Time by Cluster",
        labels={"color": "Cluster"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    latest = df_scaled[zone].iloc[-1]
    anomaly_count = (df_scaled["Anomaly"] == -1).sum()

    st.markdown(
        f"""
    <div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-bottom:10px'>
        <h4 style='color:#10b981;'>Latest {zone} Value</h4>
        <p style='font-size:24px; font-weight:bold;'>{latest:.2f}</p>
    </div>
    <div style='background-color:#ffffff; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.05);'>
        <h4 style='color:#ef4444;'>Anomalies Detected</h4>
        <p style='font-size:24px; font-weight:bold;'>{anomaly_count}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

# --- PCA Visualization ---
st.markdown("### PCA Projection")

if pca_mode == "2D":
    fig_pca = px.scatter(
        df_scaled,
        x="PCA1",
        y="PCA2",
        color=df_scaled["Anomaly"].map({1: "Normal", -1: "Anomaly"}),
        symbol=df_scaled["Cluster"].astype(str),
        title="2D PCA Projection",
        labels={"color": "Anomaly", "symbol": "Cluster"},
    )
    st.plotly_chart(fig_pca, use_container_width=True)

elif pca_mode == "3D":
    fig_3d = px.scatter_3d(
        df_scaled,
        x="PCA1",
        y="PCA2",
        z="PCA3",
        color=df_scaled["Anomaly"].map({1: "Normal", -1: "Anomaly"}),
        symbol=df_scaled["Cluster"].astype(str),
        title="3D PCA Projection",
        labels={"color": "Anomaly", "symbol": "Cluster"},
    )
    st.plotly_chart(fig_3d, use_container_width=True)

else:  # 4D
    fig_4d = px.scatter_3d(
        df_scaled,
        x="PCA1",
        y="PCA2",
        z="PCA3",
        color="Hour",
        size=df_scaled["Anomaly"].map({1: 5, -1: 10}),
        symbol=df_scaled["Cluster"].astype(str),
        hover_data=["DateTime", "Anomaly", "Cluster"],
        title="4D PCA Projection",
        labels={"color": "Hour", "symbol": "Cluster"},
    )
    st.plotly_chart(fig_4d, use_container_width=True)

# --- Footer ---
st.markdown(
    """
<hr style='margin-top:40px;'>
<p style='text-align:center; color:#6b7280;'>Built by GIFT TANDASI using Streamlit, Plotly, and Scikit-learn</p>
""",
    unsafe_allow_html=True,
)
