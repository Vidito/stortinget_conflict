import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from storting_processor import StortingDataProcessor
import numpy as np
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Stortinget Intelligence Dashboard",
    layout="wide",
    page_icon="⚖️",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR BETTER STYLING ---
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #f0f8ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- DATA LOADING LOGIC ---
@st.cache_data(ttl=3600)
def load_data():
    """Helper to check if CSVs exist and load them with caching."""
    files = {
        "rebels": "processed_rebels.csv",
        "controversy": "processed_controversy.csv",
        "alliances": "processed_alliances.csv",
    }

    if all(os.path.exists(f) for f in files.values()):
        return (
            pd.read_csv(files["rebels"]),
            pd.read_csv(files["controversy"]),
            pd.read_csv(files["alliances"]),
        )
    return None, None, None


def calculate_insights(df_rebels, df_controversy, df_alliances):
    """Calculate additional insights from the data."""
    insights = {}

    # Most rebellious party
    if len(df_rebels) > 0:
        party_rebels = df_rebels["Party"].value_counts()
        insights["most_rebel_party"] = (
            party_rebels.index[0] if len(party_rebels) > 0 else "N/A"
        )
        insights["most_rebel_count"] = (
            party_rebels.iloc[0] if len(party_rebels) > 0 else 0
        )

        # Most rebellious individual
        individual_rebels = df_rebels["Name"].value_counts()
        insights["most_rebel_person"] = (
            individual_rebels.index[0] if len(individual_rebels) > 0 else "N/A"
        )
        insights["most_rebel_person_count"] = (
            individual_rebels.iloc[0] if len(individual_rebels) > 0 else 0
        )

    # Strongest and weakest alliances
    if len(df_alliances) > 0:
        strongest = df_alliances.nlargest(1, "Agreement_Rate").iloc[0]
        insights["strongest_alliance"] = (
            f"{strongest['Party_A']} ↔ {strongest['Party_B']}"
        )
        insights["strongest_rate"] = strongest["Agreement_Rate"]

        weakest = df_alliances.nsmallest(1, "Agreement_Rate").iloc[0]
        insights["weakest_alliance"] = f"{weakest['Party_A']} ↔ {weakest['Party_B']}"
        insights["weakest_rate"] = weakest["Agreement_Rate"]

    # Average controversy
    insights["avg_controversy"] = (
        df_controversy["Score"].mean() if len(df_controversy) > 0 else 0
    )

    # Most controversial topic
    if len(df_controversy) > 0:
        topic_controversy = (
            df_controversy.groupby("Topic")["Score"].mean().sort_values(ascending=False)
        )
        insights["most_controversial_topic"] = (
            topic_controversy.index[0] if len(topic_controversy) > 0 else "N/A"
        )
        insights["topic_avg_score"] = (
            topic_controversy.iloc[0] if len(topic_controversy) > 0 else 0
        )

    return insights


# --- SIDEBAR & REFRESH LOGIC ---
with st.sidebar:
    st.title("⚙️ Control Panel")

    st.markdown("### Data Configuration")
    session = st.selectbox("Parliamentary Session", ["2024-2025", "2025-2026"])
    case_limit = st.slider("Cases to Analyze", 10, 100, 50, step=10)

    st.markdown("---")

    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        with st.status("Fetching from Stortinget API...", expanded=True) as status:
            st.write("🔌 Connecting to API...")
            processor = StortingDataProcessor(session_id=session)

            st.write(f"📊 Analyzing {case_limit} cases...")
            processor.run_analysis(limit=case_limit)

            st.write("💾 Generating datasets...")
            processor.export_to_csv()

            status.update(label="✅ Data Updated!", state="complete", expanded=False)
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### About")
    st.info(
        "This dashboard analyzes voting patterns, party alliances, and individual dissent in the Norwegian Parliament."
    )

    # Check when data was last updated
    if os.path.exists("processed_alliances.csv"):
        mod_time = os.path.getmtime("processed_alliances.csv")
        last_update = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
        st.caption(f"Last updated: {last_update}")


# --- LOAD DATA ---
df_rebels, df_controversy, df_alliances = load_data()

# --- MAIN APP HEADER ---
st.markdown(
    '<h1 class="main-header">⚖️ Stortinget Intelligence Dashboard</h1>',
    unsafe_allow_html=True,
)
st.markdown("**Exploring Political Dynamics in the Norwegian Parliament**")

if df_rebels is None:
    st.warning(
        "⚠️ **No data available.** Click 'Refresh Data' in the sidebar to begin analysis."
    )
    st.stop()

# Calculate insights
insights = calculate_insights(df_rebels, df_controversy, df_alliances)

# --- KEY METRICS OVERVIEW ---
st.markdown("## 📊 Session Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Votes Analyzed",
        len(df_controversy),
        help="Number of individual votes processed",
    )
with col2:
    st.metric(
        "Rebel Incidents",
        len(df_rebels),
        help="Times representatives voted against party line",
    )
with col3:
    st.metric(
        "Avg Controversy",
        f"{insights['avg_controversy']:.2f}",
        help="Average controversy score (0-1)",
    )
with col4:
    st.metric(
        "Party Pairs Analyzed",
        len(df_alliances),
        help="Unique party-to-party relationships",
    )

st.markdown("---")

# --- TABS FOR BETTER ORGANIZATION ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🤝 Alliance Network",
        "🔥 Controversy Analysis",
        "🎯 The Rebels",
        "📈 Deep Insights",
        "🔍 Topic Explorer",
    ]
)

# ============================================================================
# TAB 1: ALLIANCE NETWORK
# ============================================================================
with tab1:
    st.markdown("### Party Alliance Matrix")
    st.markdown(
        "How often do parties vote together? Higher percentages indicate stronger alignment."
    )

    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Create symmetric heatmap
        heatmap_df = df_alliances.pivot(
            index="Party_A", columns="Party_B", values="Agreement_Rate"
        )
        heatmap_df = heatmap_df.combine_first(heatmap_df.T).fillna(100.0)

        fig_heat = px.imshow(
            heatmap_df,
            text_auto=".0f",
            color_continuous_scale="RdYlGn",
            labels=dict(color="Agreement %"),
            range_color=[0, 100],
            aspect="auto",
        )
        fig_heat.update_layout(
            height=500, xaxis_title="Party", yaxis_title="Party", font=dict(size=11)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_right:
        st.markdown("#### 🏆 Key Alliances")

        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Strongest Alliance**")
        st.markdown(f"**{insights['strongest_alliance']}**")
        st.metric("Agreement Rate", f"{insights['strongest_rate']:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Weakest Alliance**")
        st.markdown(f"**{insights['weakest_alliance']}**")
        st.metric("Agreement Rate", f"{insights['weakest_rate']:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📊 Alliance Distribution")

        # Distribution of agreement rates
        fig_dist = px.histogram(
            df_alliances,
            x="Agreement_Rate",
            nbins=20,
            color_discrete_sequence=["#667eea"],
        )
        fig_dist.update_layout(
            xaxis_title="Agreement Rate (%)",
            yaxis_title="Number of Party Pairs",
            showlegend=False,
            height=250,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

# ============================================================================
# TAB 2: CONTROVERSY ANALYSIS
# ============================================================================
with tab2:
    st.markdown("### High-Stakes Votes")
    st.markdown(
        "Votes with the smallest margins indicate the deepest parliamentary divisions."
    )

    df_controversy_sorted = df_controversy.sort_values("Score", ascending=False)

    col_chart, col_detail = st.columns([3, 2])

    with col_chart:
        # Top controversial votes
        top_n = st.slider(
            "Show top N controversial votes", 5, 20, 10, key="controversy_slider"
        )

        fig_controversy = px.bar(
            df_controversy_sorted.head(top_n),
            x="Score",
            y="Topic",
            orientation="h",
            color="Score",
            color_continuous_scale="Reds",
            hover_data=["Case_ID", "For", "Against", "Title"],
            labels={"Score": "Controversy Score", "Topic": ""},
        )
        fig_controversy.update_layout(
            height=400, yaxis={"categoryorder": "total ascending"}, showlegend=False
        )
        st.plotly_chart(fig_controversy, use_container_width=True)

        # Scatter plot of all votes
        st.markdown("#### Vote Distribution: For vs Against")
        fig_scatter = px.scatter(
            df_controversy,
            x="For",
            y="Against",
            size="Score",
            color="Score",
            hover_data=["Topic", "Title"],
            color_continuous_scale="Reds",
            labels={"For": "Votes For", "Against": "Votes Against"},
        )
        # Add diagonal line for 50/50 split
        max_val = max(df_controversy["For"].max(), df_controversy["Against"].max())
        fig_scatter.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode="lines",
                line=dict(dash="dash", color="gray"),
                name="50/50 Split",
                showlegend=True,
            )
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_detail:
        st.markdown("#### 🎯 Most Controversial Vote")
        if len(df_controversy_sorted) > 0:
            top_case = df_controversy_sorted.iloc[0]

            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.metric("Controversy Score", f"{top_case['Score']:.3f}")
            st.markdown(f"**Topic:** {top_case['Topic']}")
            st.caption(f"Case ID: {top_case['Case_ID']}")
            st.markdown(f"*{top_case['Title']}*")
            st.markdown("</div>", unsafe_allow_html=True)

            # Vote breakdown pie chart
            fig_pie = go.Figure(
                data=[
                    go.Pie(
                        labels=["For", "Against"],
                        values=[top_case["For"], top_case["Against"]],
                        hole=0.4,
                        marker_colors=["#10b981", "#ef4444"],
                    )
                ]
            )
            fig_pie.update_layout(
                height=250, showlegend=True, margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🔥 Most Divisive Topic")
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(f"**{insights['most_controversial_topic']}**")
        st.metric("Average Score", f"{insights['topic_avg_score']:.3f}")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 3: THE REBELS
# ============================================================================
with tab3:
    st.markdown("### Representatives Who Broke Ranks")
    st.markdown("These individuals voted against their party's majority position.")

    col_filter, col_metrics = st.columns([3, 2])

    with col_filter:
        # Filters
        selected_parties = st.multiselect(
            "Filter by Party", options=sorted(df_rebels["Party"].unique()), default=None
        )

        selected_topics = st.multiselect(
            "Filter by Topic", options=sorted(df_rebels["Topic"].unique()), default=None
        )

    # Apply filters
    display_rebels = df_rebels.copy()
    if selected_parties:
        display_rebels = display_rebels[display_rebels["Party"].isin(selected_parties)]
    if selected_topics:
        display_rebels = display_rebels[display_rebels["Topic"].isin(selected_topics)]

    with col_metrics:
        st.markdown("#### 🎖️ Top Rebel")
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(f"**{insights['most_rebel_person']}**")
        st.metric("Rebel Votes", insights["most_rebel_person_count"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("#### 🏴 Most Rebellious Party")
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(f"**{insights['most_rebel_party']}**")
        st.metric("Total Rebels", insights["most_rebel_count"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### Rebels by Party")
        party_rebel_counts = display_rebels["Party"].value_counts().reset_index()
        party_rebel_counts.columns = ["Party", "Count"]

        fig_party_rebels = px.bar(
            party_rebel_counts,
            x="Count",
            y="Party",
            orientation="h",
            color="Count",
            color_continuous_scale="Oranges",
        )
        fig_party_rebels.update_layout(
            yaxis={"categoryorder": "total ascending"}, showlegend=False, height=300
        )
        st.plotly_chart(fig_party_rebels, use_container_width=True)

    with col_chart2:
        st.markdown("#### Rebels by Topic")
        topic_rebel_counts = (
            display_rebels["Topic"].value_counts().head(10).reset_index()
        )
        topic_rebel_counts.columns = ["Topic", "Count"]

        fig_topic_rebels = px.bar(
            topic_rebel_counts,
            x="Count",
            y="Topic",
            orientation="h",
            color="Count",
            color_continuous_scale="Purples",
        )
        fig_topic_rebels.update_layout(
            yaxis={"categoryorder": "total ascending"}, showlegend=False, height=300
        )
        st.plotly_chart(fig_topic_rebels, use_container_width=True)

    # Detailed table
    st.markdown("#### 📋 Detailed Rebel Record")
    st.dataframe(
        display_rebels[
            ["Name", "Party", "Vote", "Split", "Topic", "Case_ID"]
        ].sort_values("Party"),
        use_container_width=True,
        hide_index=True,
        height=400,
    )

# ============================================================================
# TAB 4: DEEP INSIGHTS
# ============================================================================
with tab4:
    st.markdown("### Advanced Analytics")

    # Rebellion rate by party
    st.markdown("#### 📊 Party Discipline Analysis")
    col_disc1, col_disc2 = st.columns(2)

    with col_disc1:
        # Calculate rebellion rate (this is simplified - would need total votes per party for accuracy)
        party_stats = (
            df_rebels.groupby("Party")
            .agg({"Name": "count", "Case_ID": "nunique"})
            .reset_index()
        )
        party_stats.columns = ["Party", "Rebel_Count", "Cases_Involved"]
        party_stats = party_stats.sort_values("Rebel_Count", ascending=False)

        fig_discipline = px.bar(
            party_stats,
            x="Party",
            y="Rebel_Count",
            color="Rebel_Count",
            color_continuous_scale="Reds",
            labels={"Rebel_Count": "Number of Rebel Votes"},
        )
        fig_discipline.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_discipline, use_container_width=True)

        st.info(
            "💡 **Insight:** Lower rebel counts suggest stronger party discipline or higher party agreement with votes."
        )

    with col_disc2:
        # Most independent representatives
        st.markdown("##### Top 10 Most Independent Representatives")
        individual_stats = (
            df_rebels.groupby("Name")
            .agg({"Party": "first", "Case_ID": "count"})
            .reset_index()
        )
        individual_stats.columns = ["Name", "Party", "Rebel_Votes"]
        individual_stats = individual_stats.sort_values(
            "Rebel_Votes", ascending=False
        ).head(10)

        fig_independents = px.bar(
            individual_stats, y="Name", x="Rebel_Votes", color="Party", orientation="h"
        )
        fig_independents.update_layout(
            height=350, yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig_independents, use_container_width=True)

    st.markdown("---")

    # Alliance clusters
    st.markdown("#### 🕸️ Party Relationship Network")

    # Create network-style visualization
    col_net1, col_net2 = st.columns([3, 2])

    with col_net1:
        # Group alliances into categories
        df_alliances_copy = df_alliances.copy()
        df_alliances_copy["Category"] = pd.cut(
            df_alliances_copy["Agreement_Rate"],
            bins=[0, 30, 60, 100],
            labels=["Adversaries (<30%)", "Neutral (30-60%)", "Allies (>60%)"],
        )

        fig_network = px.scatter(
            df_alliances_copy,
            x="Party_A",
            y="Party_B",
            size="Agreement_Rate",
            color="Category",
            hover_data=["Agreement_Rate"],
            color_discrete_map={
                "Adversaries (<30%)": "#ef4444",
                "Neutral (30-60%)": "#f59e0b",
                "Allies (>60%)": "#10b981",
            },
        )
        fig_network.update_layout(height=400, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_network, use_container_width=True)

    with col_net2:
        st.markdown("##### Relationship Distribution")
        category_counts = df_alliances_copy["Category"].value_counts()

        fig_cat = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            color=category_counts.index,
            color_discrete_map={
                "Adversaries (<30%)": "#ef4444",
                "Neutral (30-60%)": "#f59e0b",
                "Allies (>60%)": "#10b981",
            },
        )
        fig_cat.update_layout(height=300)
        st.plotly_chart(fig_cat, use_container_width=True)

        st.info(
            "💡 **Insight:** Party relationships form distinct clusters, revealing political blocs and opposition dynamics."
        )

# ============================================================================
# TAB 5: TOPIC EXPLORER
# ============================================================================
with tab5:
    st.markdown("### Explore by Topic")

    # Topic statistics
    topic_stats = (
        df_controversy.groupby("Topic")
        .agg({"Score": ["mean", "count", "max"], "For": "sum", "Against": "sum"})
        .reset_index()
    )
    topic_stats.columns = [
        "Topic",
        "Avg_Controversy",
        "Vote_Count",
        "Max_Controversy",
        "Total_For",
        "Total_Against",
    ]
    topic_stats = topic_stats.sort_values("Avg_Controversy", ascending=False)

    # Select a topic
    selected_topic = st.selectbox(
        "Select a topic to explore", options=topic_stats["Topic"].tolist()
    )

    if selected_topic:
        topic_data = df_controversy[df_controversy["Topic"] == selected_topic]
        topic_rebels = df_rebels[df_rebels["Topic"] == selected_topic]

        # Metrics for selected topic
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Votes", len(topic_data))
        with col_m2:
            st.metric("Avg Controversy", f"{topic_data['Score'].mean():.3f}")
        with col_m3:
            st.metric("Total Rebels", len(topic_rebels))
        with col_m4:
            total_votes = topic_data["For"].sum() + topic_data["Against"].sum()
            st.metric("Total Participation", total_votes)

        # Visualizations for topic
        col_v1, col_v2 = st.columns(2)

        with col_v1:
            st.markdown("##### Controversy Distribution")
            # Create bins manually for better control
            hist_data = pd.cut(topic_data["Score"], bins=15)
            hist_counts = hist_data.value_counts().sort_index()

            # Create bar chart instead of histogram for better control
            bin_labels = [
                f"{interval.left:.2f}-{interval.right:.2f}"
                for interval in hist_counts.index
            ]

            fig_topic_cont = go.Figure(
                data=[
                    go.Bar(
                        x=bin_labels,
                        y=hist_counts.values,
                        marker_color="#8b5cf6",
                        marker_line_color="white",
                        marker_line_width=1,
                    )
                ]
            )
            fig_topic_cont.update_layout(
                xaxis_title="Controversy Score Range",
                yaxis_title="Number of Votes",
                showlegend=False,
                height=300,
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig_topic_cont, use_container_width=True)

        with col_v2:
            st.markdown("##### Parties with Rebels on This Topic")
            if len(topic_rebels) > 0:
                party_rebels_topic = topic_rebels["Party"].value_counts().reset_index()
                party_rebels_topic.columns = ["Party", "Count"]

                fig_party_topic = px.bar(
                    party_rebels_topic,
                    x="Party",
                    y="Count",
                    color="Count",
                    color_continuous_scale="Reds",
                )
                fig_party_topic.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_party_topic, use_container_width=True)
            else:
                st.info("No rebels found for this topic.")

        # Detailed cases for this topic
        st.markdown("##### Cases for This Topic")
        st.dataframe(
            topic_data[["Title", "Case_ID", "Score", "For", "Against"]].sort_values(
                "Score", ascending=False
            ),
            use_container_width=True,
            hide_index=True,
            height=300,
        )

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>Stortinget Intelligence Dashboard</strong> | Data from data.stortinget.no</p>
    <p>Session: {session} | Analyzing parliamentary voting patterns and political dynamics</p>
</div>
""".format(
        session=session
    ),
    unsafe_allow_html=True,
)
