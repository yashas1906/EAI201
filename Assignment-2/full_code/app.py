import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import xgboost as xgb
import plotly.graph_objects as go
from sklearn.decomposition import PCA  
from mpl_toolkits.mplot3d import Axes3D  

st.set_page_config(layout="wide")
st.title('FIFA World Cup 2026 Prediction & Analytics')

@st.cache_data
def load_data():
    df = pd.read_csv('fifa_overall_dataset.csv')
    df['Win Rate'] = df.apply(lambda row: row['Wins'] / row['Matches Played'] if row['Matches Played'] > 0 else 0, axis=1)
    df['TopQuartile'] = (pd.qcut(df['Win Rate'], 4, labels=False) == 3).astype(int)
    return df

df = load_data()


log = []

# === Select features for clustering and modeling ===
overall_agg_features = [col for col in df.columns if not (
    col.endswith('_2010') or col.endswith('_2014') or col.endswith('_2018') or col.endswith('_2022') or col in ['Team', 'Win Rate', 'ID']
)]
numeric_overall_agg_features = [col for col in overall_agg_features if np.issubdtype(df[col].dtype, np.number)]

# === Yearly features ===
yearly_feats = [col for col in df.columns if (
    '_2010' in col or '_2014' in col or '_2018' in col or '_2022' in col
) and np.issubdtype(df[col].dtype, np.number)]

numeric_yearly_features = yearly_feats  # Alias for consistency

# === Prepare data for clustering ===
X_overall = df[numeric_overall_agg_features].fillna(0)
scaler_overall = StandardScaler()
X_overall_scaled = scaler_overall.fit_transform(X_overall)

X_yearly = df[yearly_feats].fillna(0)
scaler_yearly = StandardScaler()
X_yearly_scaled = scaler_yearly.fit_transform(X_yearly)

# === K-Means clustering (overall features) ===
optimal_k = 4
kmeans_overall = KMeans(n_clusters=optimal_k, random_state=42)
df['Cluster'] = kmeans_overall.fit_predict(X_overall_scaled)
log.append(f"✅ K-Means clustering completed with {optimal_k} clusters")

# === K-Means clustering (yearly features) ===
kmeans_yearly = KMeans(n_clusters=optimal_k, random_state=42)
df['Yearly_Cluster'] = kmeans_yearly.fit_predict(X_yearly_scaled)
log.append(f"✅ Yearly K-Means clustering completed")

# === Find best clusters by Win Rate ===
best_overall_cluster = df.groupby('Cluster')['Win Rate'].mean().idxmax()
best_yearly_cluster = df.groupby('Yearly_Cluster')['Win Rate'].mean().idxmax()
log.append(f"📊 Best overall cluster: {best_overall_cluster} (Avg Win Rate: {df[df['Cluster']==best_overall_cluster]['Win Rate'].mean():.3f})")
log.append(f"📊 Best yearly cluster: {best_yearly_cluster} (Avg Win Rate: {df[df['Yearly_Cluster']==best_yearly_cluster]['Win Rate'].mean():.3f})")

# === Consensus teams: Both best clusters ===
df['Combo_Flag'] = ((df['Cluster'] == best_overall_cluster) & (df['Yearly_Cluster'] == best_yearly_cluster)).astype(int)
consensus_df = df[df['Combo_Flag'] == 1].copy()
consensus_qualifiers = consensus_df['Team'].tolist()
log.append(f"🎯 {len(consensus_qualifiers)} consensus teams identified")

# === Model Training on Consensus Teams ===
overall_features = [col for col in consensus_df.columns if np.issubdtype(consensus_df[col].dtype, np.number)
                    and '2010' not in col and '2014' not in col and '2018' not in col and '2022' not in col
                    and col not in ['Cluster', 'Yearly_Cluster', 'Combo_Flag', 'Win Rate', 'TopQuartile']]
X_overall_model = consensus_df[overall_features].fillna(0)
y_reg = consensus_df['Win Rate'].fillna(0)

yearly_features = [col for col in consensus_df.columns if (
    '_2010' in col or '_2014' in col or '_2018' in col or '_2022' in col) and np.issubdtype(consensus_df[col].dtype, np.number)]
X_yearly_model = consensus_df[yearly_features].fillna(0)

# ---- Random Forest (overall) ----
rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg.fit(X_overall_model, y_reg)
consensus_df['RF_Overall_Reg'] = rf_reg.predict(X_overall_model)
log.append("✅ Random Forest (Overall) trained")

# ---- Random Forest (yearly) ----
rf_reg_yearly = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg_yearly.fit(X_yearly_model, y_reg)
consensus_df['RF_Yearly_Reg'] = rf_reg_yearly.predict(X_yearly_model)
log.append("✅ Random Forest (Yearly) trained")

# ---- XGBoost (overall) ----
xgb_reg = xgb.XGBRegressor(n_estimators=100, random_state=42)
xgb_reg.fit(X_overall_model, y_reg)
consensus_df['XGB_Overall_Reg'] = xgb_reg.predict(X_overall_model)
log.append("✅ XGBoost (Overall) trained")

# ---- XGBoost (yearly) ----
xgb_reg_yearly = xgb.XGBRegressor(n_estimators=100, random_state=42)
xgb_reg_yearly.fit(X_yearly_model, y_reg)
consensus_df['XGB_Yearly_Reg'] = xgb_reg_yearly.predict(X_yearly_model)
log.append("✅ XGBoost (Yearly) trained")

# ---- Combine predictions ----
consensus_df['RF_Score'] = 0.5 * consensus_df['RF_Overall_Reg'] + 0.5 * consensus_df['RF_Yearly_Reg']
consensus_df['XGB_Score'] = 0.5 * consensus_df['XGB_Overall_Reg'] + 0.5 * consensus_df['XGB_Yearly_Reg']
consensus_df['Final_Score'] = 0.6 * consensus_df['RF_Score'] + 0.4 * consensus_df['XGB_Score']

# ---- Merge scores back to main df ----
df = df.merge(consensus_df[['Team', 'RF_Score', 'XGB_Score', 'Final_Score']], on='Team', how='left')
df['RF_Score'] = df['RF_Score'].fillna(0)
df['XGB_Score'] = df['XGB_Score'].fillna(0)
df['Final_Score'] = df['Final_Score'].fillna(0)

# === ADDITIONAL: Train models on ALL TEAMS for Tab 2 visualization ===
# This ensures rf_reg_overall and xgb_reg_overall can predict for all teams
y_all = df['Win Rate'].fillna(0)

# Train RF on all teams (overall features)
X_all_overall = df[numeric_overall_agg_features].fillna(0)
Xo_train, Xo_test, yo_train, yo_test = train_test_split(X_all_overall, y_all, test_size=0.2, random_state=42)
rf_reg_overall = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf_reg_overall.fit(Xo_train, yo_train)

# Train RF on all teams (yearly features)
X_all_yearly = df[yearly_feats].fillna(0)
Xy_train, Xy_test, yy_train, yy_test = train_test_split(X_all_yearly, y_all, test_size=0.2, random_state=42)
rf_reg_yearly_full = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf_reg_yearly_full.fit(Xy_train, yy_train)

# Train XGBoost on all teams (overall features)
xgb_reg_overall = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
xgb_reg_overall.fit(Xo_train, yo_train)

# Train XGBoost on all teams (yearly features)
xgb_reg_yearly_full = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
xgb_reg_yearly_full.fit(Xy_train, yy_train)

# Generate predictions for ALL teams
df['predicted_win_rate'] = rf_reg_overall.predict(X_all_overall)
df['predicted_win_rate_yearly'] = rf_reg_yearly_full.predict(X_all_yearly)
df['xgb_pred_win_rate'] = xgb_reg_overall.predict(X_all_overall)
df['xgb_pred_win_rate_yearly'] = xgb_reg_yearly_full.predict(X_all_yearly)
df['grouped_score'] = (df['predicted_win_rate'] + df['predicted_win_rate_yearly']) / 2
df['xgb_grouped_score'] = (df['xgb_pred_win_rate'] + df['xgb_pred_win_rate_yearly']) / 2

log.append("✅ Full dataset models trained for visualization")

# ---- Final Rankings ----
top16 = df.nlargest(16, 'Final_Score')
top10 = top16.head(10)[['Team', 'RF_Score', 'XGB_Score', 'Final_Score']]
quarters = top16['Team'].head(8).tolist()
winner_team = top16.iloc[0]['Team']
winner_score = top16.iloc[0]['Final_Score']
runner_up = top16.iloc[1]['Team']
third_place = top16.iloc[2]['Team']

log.append(f"🏆 Winner Prediction: {winner_team} (Final Score: {winner_score:.4f})")


# === APP CONTENT SETUP ===
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Qualifiers & Winner", "📊 Model Insights", "🔍 Team Explorer", "📈 EDA"])

with tab1:
    # === TOP 10 TABLE ===
    st.header("🏅 Top 10 Predicted Qualifiers")
    st.dataframe(top10.style.format({
        'RF_Score': '{:.4f}',
        'XGB_Score': '{:.4f}',
        'Final_Score': '{:.4f}'
    }), use_container_width=True)
    
    st.markdown("---")
    
    # === TOURNAMENT BRACKET (TOP 10 - SCORE-BASED) ===
    st.header("⚽ Tournament Bracket (Top 10 Teams)")
    st.info("**Winner determined by higher Final_Score in each matchup**")
    
    # Get top 10 teams
    top10_teams = df.nlargest(10, 'Final_Score')
    
    # Quarter Finals (Top 8 from top 10)
    st.subheader("🥊 Quarter Finals (Top 8)")
    qf_matchups = [
        (0, 7),  # 1st vs 8th
        (3, 4),  # 4th vs 5th
        (2, 5),  # 3rd vs 6th
        (1, 6)   # 2nd vs 7th
    ]
    
    qf_winners = []
    cols = st.columns(4)
    
    for idx, (i, j) in enumerate(qf_matchups):
        team1 = top10_teams.iloc[i]
        team2 = top10_teams.iloc[j]
        
        # Winner is team with higher Final_Score
        if team1['Final_Score'] > team2['Final_Score']:
            winner = team1
            loser = team2
        else:
            winner = team2
            loser = team1
        
        qf_winners.append(winner['Team'])
        
        with cols[idx]:
            st.markdown(f"""
            **QF {idx + 1}**
            - 🟢 {team1['Team']} ({team1['Final_Score']:.4f})
            - 🔴 {team2['Team']} ({team2['Final_Score']:.4f})
            - **Winner:** {winner['Team']} 🏆
            """)
    
    st.markdown("---")
    
    # Semi Finals
    st.subheader("🥊 Semi Finals")
    sf_matchups = [
        (0, 1),  # QF1 winner vs QF2 winner
        (2, 3)   # QF3 winner vs QF4 winner
    ]
    
    sf_winners = []
    sf_losers = []
    cols = st.columns(2)
    
    for idx, (i, j) in enumerate(sf_matchups):
        team1_name = qf_winners[i]
        team2_name = qf_winners[j]
        team1_data = df[df['Team'] == team1_name].iloc[0]
        team2_data = df[df['Team'] == team2_name].iloc[0]
        
        # Winner is team with higher Final_Score
        if team1_data['Final_Score'] > team2_data['Final_Score']:
            winner_name = team1_name
            loser_name = team2_name
        else:
            winner_name = team2_name
            loser_name = team1_name
        
        sf_winners.append(winner_name)
        sf_losers.append(loser_name)
        
        with cols[idx]:
            st.markdown(f"""
            **Semi Final {idx + 1}**
            - 🟢 {team1_name} ({team1_data['Final_Score']:.4f})
            - 🔴 {team2_name} ({team2_data['Final_Score']:.4f})
            - **Winner:** {winner_name} 🏆
            - *Loser to 3rd Place Playoff*
            """)
    
    st.markdown("---")
    
    # Third Place Playoff
    st.subheader("🥉 Third Place Playoff")
    team1_data = df[df['Team'] == sf_losers[0]].iloc[0]
    team2_data = df[df['Team'] == sf_losers[1]].iloc[0]
    
    if team1_data['Final_Score'] > team2_data['Final_Score']:
        third_winner = sf_losers[0]
        fourth_place = sf_losers[1]
    else:
        third_winner = sf_losers[1]
        fourth_place = sf_losers[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        - 🟢 {sf_losers[0]} ({team1_data['Final_Score']:.4f})
        - 🔴 {sf_losers[1]} ({team2_data['Final_Score']:.4f})
        """)
    with col2:
        st.success(f"🥉 **Third Place:** {third_winner}")
        st.info(f"4th Place: {fourth_place}")
    
    st.markdown("---")
    
    # Final
    st.subheader("🏆 FINAL")
    team1_data = df[df['Team'] == sf_winners[0]].iloc[0]
    team2_data = df[df['Team'] == sf_winners[1]].iloc[0]
    
    if team1_data['Final_Score'] > team2_data['Final_Score']:
        final_winner = sf_winners[0]
        final_loser = sf_winners[1]
    else:
        final_winner = sf_winners[1]
        final_loser = sf_winners[0]
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        ### Championship Match
        - 🟢 {sf_winners[0]} ({team1_data['Final_Score']:.4f})
        - 🔴 {sf_winners[1]} ({team2_data['Final_Score']:.4f})
        """)
        
        st.success(f"# 🏆 CHAMPION: {final_winner}")
        st.info(f"🥈 Runner-up: {final_loser}")
    
    st.markdown("---")
    
    # === FINAL STANDINGS ===
    st.header("🏅 Final Top 10 Standings")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 🥇 Champion")
        winner_row = df[df['Team'] == final_winner].iloc[0]
        st.metric("Team", final_winner)
        st.metric("Final Score", f"{winner_row['Final_Score']:.4f}")
        st.metric("Win Rate", f"{winner_row['Win Rate']:.3f}")
    
    with col2:
        st.markdown("### 🥈 Runner-Up")
        runner_row = df[df['Team'] == final_loser].iloc[0]
        st.metric("Team", final_loser)
        st.metric("Final Score", f"{runner_row['Final_Score']:.4f}")
    
    with col3:
        st.markdown("### 🥉 Third Place")
        third_row = df[df['Team'] == third_winner].iloc[0]
        st.metric("Team", third_winner)
        st.metric("Final Score", f"{third_row['Final_Score']:.4f}")
    
    with col4:
        st.markdown("### 4️⃣ Fourth Place")
        fourth_row = df[df['Team'] == fourth_place].iloc[0]
        st.metric("Team", fourth_place)
        st.metric("Final Score", f"{fourth_row['Final_Score']:.4f}")
    
    # Remaining teams 5-10
    st.subheader("📋 Positions 5-10 (Eliminated in Quarter Finals)")
    
    # Get QF losers (teams that didn't advance to SF)
    qf_losers = [team for team in top10_teams['Team'].head(8) if team not in qf_winners]
    
    cols = st.columns(4)
    for idx, team in enumerate(qf_losers):
        team_data = df[df['Team'] == team].iloc[0]
        with cols[idx % 4]:
            st.info(f"**{idx + 5}. {team}**\nScore: {team_data['Final_Score']:.4f}")
    
    st.markdown("---")
    
    # === MODELING PROCESS VISUALIZATION ===
    st.header("🔬 Step-by-Step Modeling Process")
    
    # Step 1: Clustering
    st.subheader("Step 1️⃣: K-Means Clustering")
    st.markdown("**Input:** All teams from dataset")
    st.markdown("**Process:** Group teams into 4 clusters based on performance features")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"""
        **Best Overall Cluster:** {best_overall_cluster}  
        **Best Yearly Cluster:** {best_yearly_cluster}  
        **Consensus Teams Found:** {len(consensus_qualifiers)}
        """)
    
    with col2:
        st.success(f"""
        **✅ Teams After Clustering:**  
        {', '.join(consensus_qualifiers[:10])}{'...' if len(consensus_qualifiers) > 10 else ''}
        """)
    
    st.markdown("↓")
    
    # Step 2: Random Forest
    st.subheader("Step 2️⃣: Random Forest Prediction")
    st.markdown("**Input:** Consensus teams from clustering")
    st.markdown("**Process:** Train RF models on Overall + Yearly features → Predict scores")
    
    # Get top teams after RF
    rf_top_teams = df[df['Combo_Flag'] == 1].nlargest(10, 'RF_Score')['Team'].tolist()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"""
        **Overall RF Score:** ✓  
        **Yearly RF Score:** ✓  
        **Combined RF Score:** ✓
        """)
    
    with col2:
        st.success(f"""
        **✅ Top 10 Teams After RF:**  
        {', '.join(rf_top_teams)}
        """)
    
    st.markdown("↓")
    
    # Step 3: XGBoost
    st.subheader("Step 3️⃣: XGBoost Prediction")
    st.markdown("**Input:** Same consensus teams")
    st.markdown("**Process:** Train XGBoost models on Overall + Yearly features → Refine predictions")
    
    # Get top teams after XGBoost
    xgb_top_teams = df[df['Combo_Flag'] == 1].nlargest(10, 'XGB_Score')['Team'].tolist()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"""
        **Overall XGB Score:** ✓  
        **Yearly XGB Score:** ✓  
        **Combined XGB Score:** ✓
        """)
    
    with col2:
        st.success(f"""
        **✅ Top 10 Teams After XGBoost:**  
        {', '.join(xgb_top_teams)}
        """)
    
    st.markdown("↓")
    
    # Step 4: Final Ranking
    st.subheader("Step 4️⃣: Final Score Calculation")
    st.markdown("**Process:** Combine RF (60%) + XGBoost (40%) → Final Rankings")
    
    final_top_teams = df.nlargest(10, 'Final_Score')['Team'].tolist()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("""
        **Formula:**  
        Final Score = (0.6 × RF) + (0.4 × XGB)
        """)
    
    with col2:
        st.success(f"""
        **🏆 Final Top 10 Teams:**  
        {', '.join(final_top_teams)}
        """)
    
    st.markdown("---")
    
    # Summary Box
    st.subheader("📊 Process Summary")
    summary_cols = st.columns(4)
    
    with summary_cols[0]:
        st.metric("Total Teams Analyzed", len(df))
    
    with summary_cols[1]:
        st.metric("Teams After Clustering", len(consensus_qualifiers))
    
    with summary_cols[2]:
        st.metric("Models Trained", "6")
        st.caption("2 RF + 2 XGB + 2 Cluster")
    
    with summary_cols[3]:
        st.metric("Final Predictions", "10")
        st.caption("Top 10 Tournament Teams")
    
    st.markdown("---")
    
    # Tournament Format Info
    st.subheader("⚽ Tournament Format")
    st.info("""
    **Bracket Simulation Rules:**
    - **Quarter Finals:** 1 vs 8, 4 vs 5, 3 vs 6, 2 vs 7
    - **Semi Finals:** QF winners compete
    - **Third Place:** SF losers compete for bronze
    - **Final:** SF winners compete for championship
    - **Winner Selection:** Team with higher Final_Score wins each matchup
    """)

with tab2:
    st.header("📊 K-Means, Random Forest & XGBoost Model Insights")
    
    # === DATA PREPARATION FOR TAB 2 ===
    X_cluster = df[numeric_overall_agg_features].fillna(0)
    scaler_tab2 = StandardScaler()
    X_scaled_tab2 = scaler_tab2.fit_transform(X_cluster)
    
    X_yearly_cluster = df[yearly_feats].fillna(0)
    scaler_yearly_tab2 = StandardScaler()
    X_yearly_scaled_tab2 = scaler_yearly_tab2.fit_transform(X_yearly_cluster)
    
    # ============================================================
    # K-MEANS CLUSTERING SECTION
    # ============================================================
    
    # === ELBOW METHOD ===
    st.subheader("🔍 Elbow Method for Optimal K")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Overall Features**")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        wcss_overall = []
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X_scaled_tab2)
            wcss_overall.append(kmeans.inertia_)
        ax1.plot(range(1, 11), wcss_overall, marker='o', color='#667eea')
        ax1.set_xlabel('Number of Clusters K')
        ax1.set_ylabel('WCSS (Inertia)')
        ax1.set_title('Elbow Method (Overall Features)')
        ax1.grid(alpha=0.3)
        st.pyplot(fig1)
        plt.close(fig1)
    
    with col2:
        st.markdown("**Yearly Features**")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        wcss_yearly = []
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X_yearly_scaled_tab2)
            wcss_yearly.append(kmeans.inertia_)
        ax2.plot(range(1, 11), wcss_yearly, marker='o', color='#764ba2')
        ax2.set_xlabel('Number of Clusters K')
        ax2.set_ylabel('WCSS (Inertia)')
        ax2.set_title('Elbow Method (Yearly Features)')
        ax2.grid(alpha=0.3)
        st.pyplot(fig2)
        plt.close(fig2)
    
    st.markdown("---")
    
    # === CLUSTER DISTRIBUTION ===
    st.subheader("🎯 K-Means Cluster Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Overall Features Clusters**")
        fig_pca1, ax_pca1 = plt.subplots(figsize=(6, 5))
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled_tab2)
        scatter = ax_pca1.scatter(X_pca[:, 0], X_pca[:, 1], c=df['Cluster'], cmap='tab10', s=100, alpha=0.7)
        for i, name in enumerate(df['Team']):
            ax_pca1.text(X_pca[i, 0], X_pca[i, 1], name, fontsize=7, alpha=0.8)
        ax_pca1.set_xlabel('PCA Component 1')
        ax_pca1.set_ylabel('PCA Component 2')
        ax_pca1.set_title('K-Means Clusters (Overall)')
        plt.colorbar(scatter, ax=ax_pca1)
        st.pyplot(fig_pca1)
        plt.close(fig_pca1)
    
    with col2:
        st.markdown("**Yearly Features Clusters**")
        fig_pca2, ax_pca2 = plt.subplots(figsize=(6, 5))
        pca_yearly = PCA(n_components=2)
        X_pca_yearly = pca_yearly.fit_transform(X_yearly_scaled_tab2)
        scatter2 = ax_pca2.scatter(X_pca_yearly[:, 0], X_pca_yearly[:, 1], c=df['Yearly_Cluster'], cmap='tab10', s=100, alpha=0.7)
        for i, name in enumerate(df['Team']):
            ax_pca2.text(X_pca_yearly[i, 0], X_pca_yearly[i, 1], name, fontsize=7, alpha=0.8)
        ax_pca2.set_xlabel('PCA Component 1')
        ax_pca2.set_ylabel('PCA Component 2')
        ax_pca2.set_title('K-Means Clusters (Yearly)')
        plt.colorbar(scatter2, ax=ax_pca2)
        st.pyplot(fig_pca2)
        plt.close(fig_pca2)
    
    st.markdown("---")
    
    # === CLUSTER METRICS ===
    st.subheader("📈 Cluster Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Overall Cluster Metrics**")
        cluster_metrics = df.groupby('Cluster')[['Win Rate', 'Points', 'Goal Difference']].mean()
        st.dataframe(cluster_metrics.style.highlight_max(axis=0, color='lightgreen'))
        
        best_cluster_id = cluster_metrics['Win Rate'].idxmax()
        qualifiers = df[df['Cluster'] == best_cluster_id]['Team'].tolist()
        st.success(f"**Best Cluster: {best_cluster_id}** (Highest Win Rate)")
        st.info(f"**Teams:** {', '.join(qualifiers)}")
    
    with col2:
        st.markdown("**Yearly Cluster Metrics**")
        cluster_metrics_yearly = df.groupby('Yearly_Cluster')[['Win Rate', 'Points', 'Goal Difference']].mean()
        st.dataframe(cluster_metrics_yearly.style.highlight_max(axis=0, color='lightgreen'))
        
        best_cluster_id_yearly = cluster_metrics_yearly['Win Rate'].idxmax()
        qualifiers_yearly = df[df['Yearly_Cluster'] == best_cluster_id_yearly]['Team'].tolist()
        st.success(f"**Best Cluster: {best_cluster_id_yearly}** (Highest Win Rate)")
        st.info(f"**Teams:** {', '.join(qualifiers_yearly)}")
    
    st.markdown("---")
    
    
    # RANDOM FOREST SECTION

    
    st.subheader("🌲 Random Forest: Top Teams by Predicted Win Rate")
    
    top_teams = df.sort_values('predicted_win_rate', ascending=False).head(10)
    
    fig_rf, ax_rf = plt.subplots(figsize=(10, 5))
    bars = ax_rf.bar(top_teams['Team'], top_teams['predicted_win_rate'], color='lime')
    ax_rf.set_xlabel('Team')
    ax_rf.set_ylabel('Predicted Win Rate')
    ax_rf.set_title('Top Teams by Random Forest Prediction')
    ax_rf.set_ylim(0, 1)
    plt.xticks(rotation=30, ha='right')
    for bar in bars:
        height = bar.get_height()
        ax_rf.annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    st.pyplot(fig_rf)
    plt.close(fig_rf)
    
    st.dataframe(top_teams[['Team', 'predicted_win_rate']], use_container_width=True)
    
    st.markdown("---")
    
    # === PREDICTED VS ACTUAL (UPDATED WITH ALL 4 METRICS) ===
    st.subheader("🎯 Random Forest: Predicted vs Actual Win Rate")
    
    fig_pred, ax_pred = plt.subplots(figsize=(8, 6))
    ax_pred.scatter(df['Win Rate'], df['predicted_win_rate'], alpha=0.6, color='darkgreen')
    ax_pred.plot([0, 1], [0, 1], 'r--', lw=2, label='Perfect Prediction')
    ax_pred.set_xlabel('Actual Win Rate')
    ax_pred.set_ylabel('Predicted Win Rate')
    ax_pred.set_title('Random Forest: Predicted vs Actual')
    ax_pred.legend()
    ax_pred.grid(alpha=0.3)
    st.pyplot(fig_pred)
    plt.close(fig_pred)
    
    # Calculate all 4 metrics
    mae = np.mean(np.abs(df['Win Rate'] - df['predicted_win_rate']))
    mse = np.mean((df['Win Rate'] - df['predicted_win_rate'])**2)
    rmse = np.sqrt(mse)
    r2 = 1 - (np.sum((df['Win Rate'] - df['predicted_win_rate'])**2) / np.sum((df['Win Rate'] - df['Win Rate'].mean())**2))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MAE", f"{mae:.4f}")
    with col2:
        st.metric("MSE", f"{mse:.4f}")
    with col3:
        st.metric("RMSE", f"{rmse:.4f}")
    with col4:
        st.metric("R² Score", f"{r2:.4f}")
    
    st.markdown("---")
    
    # === OVERALL VS YEARLY RF COMPARISON (UPDATED WITH ALL 4 METRICS) ===
    st.subheader("⚖️ Overall vs Yearly RF Model Comparison")
    
    # Calculate metrics for Overall model
    mae_overall = np.mean(np.abs(df['Win Rate'] - df['predicted_win_rate']))
    mse_overall = np.mean((df['Win Rate'] - df['predicted_win_rate'])**2)
    rmse_overall = np.sqrt(mse_overall)
    r2_overall = 1 - (np.sum((df['Win Rate'] - df['predicted_win_rate'])**2) / np.sum((df['Win Rate'] - df['Win Rate'].mean())**2))
    
    # Calculate metrics for Yearly model
    mae_yearly = np.mean(np.abs(df['Win Rate'] - df['predicted_win_rate_yearly']))
    mse_yearly = np.mean((df['Win Rate'] - df['predicted_win_rate_yearly'])**2)
    rmse_yearly = np.sqrt(mse_yearly)
    r2_yearly = 1 - (np.sum((df['Win Rate'] - df['predicted_win_rate_yearly'])**2) / np.sum((df['Win Rate'] - df['Win Rate'].mean())**2))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Overall Features Model**")
        st.metric("MAE", f"{mae_overall:.4f}")
        st.metric("MSE", f"{mse_overall:.4f}")
        st.metric("RMSE", f"{rmse_overall:.4f}")
        st.metric("R² Score", f"{r2_overall:.4f}")
        
    with col2:
        st.markdown("**Yearly Features Model**")
        st.metric("MAE", f"{mae_yearly:.4f}")
        st.metric("MSE", f"{mse_yearly:.4f}")
        st.metric("RMSE", f"{rmse_yearly:.4f}")
        st.metric("R² Score", f"{r2_yearly:.4f}")
    
    fig_comp, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.scatter(df['Win Rate'], df['predicted_win_rate'], alpha=0.6, color='blue')
    ax1.plot([0, 1], [0, 1], 'r--', lw=2)
    ax1.set_xlabel('Actual Win Rate')
    ax1.set_ylabel('Predicted Win Rate')
    ax1.set_title('Overall Features RF Model')
    ax1.grid(alpha=0.3)
    
    ax2.scatter(df['Win Rate'], df['predicted_win_rate_yearly'], alpha=0.6, color='purple')
    ax2.plot([0, 1], [0, 1], 'r--', lw=2)
    ax2.set_xlabel('Actual Win Rate')
    ax2.set_ylabel('Predicted Win Rate')
    ax2.set_title('Yearly Features RF Model')
    ax2.grid(alpha=0.3)
    
    st.pyplot(fig_comp)
    plt.close(fig_comp)
    
    st.markdown("---")
    
    # === PREDICTION DISTRIBUTION ===
    st.subheader("📊 Random Forest: Prediction Distribution")
    
    fig_dist, ax_dist = plt.subplots(figsize=(10, 5))
    ax_dist.hist(df['predicted_win_rate'], bins=20, color='seagreen', alpha=0.7, edgecolor='black')
    ax_dist.set_xlabel('Predicted Win Rate')
    ax_dist.set_ylabel('Frequency')
    ax_dist.set_title('Distribution of Random Forest Predictions')
    ax_dist.axvline(df['predicted_win_rate'].mean(), color='red', linestyle='--', 
                    linewidth=2, label=f"Mean: {df['predicted_win_rate'].mean():.3f}")
    ax_dist.legend()
    st.pyplot(fig_dist)
    plt.close(fig_dist)
    
    st.markdown("---")
    
  
    # XGBOOST SECTION
    
    
    st.subheader("🔥 XGBoost: Top Teams by Predicted Win Rate")
    top_teams_xgb = df.sort_values('xgb_pred_win_rate', ascending=False).head(10)
    
    fig_xgb, ax_xgb = plt.subplots(figsize=(10, 5))
    bars = ax_xgb.bar(top_teams_xgb['Team'], top_teams_xgb['xgb_pred_win_rate'], color='orange')
    ax_xgb.set_xlabel('Team')
    ax_xgb.set_ylabel('Predicted Win Rate')
    ax_xgb.set_title('Top Teams by XGBoost Prediction')
    ax_xgb.set_ylim(0, 1)
    plt.xticks(rotation=30, ha='right')
    for bar in bars:
        height = bar.get_height()
        ax_xgb.annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    st.pyplot(fig_xgb)
    plt.close(fig_xgb)
    st.dataframe(top_teams_xgb[['Team', 'xgb_pred_win_rate']], use_container_width=True)
    
    st.markdown("---")
    

    # === RANDOM FOREST VS XGBOOST COMPARISON (UPDATED WITH ALL 4 METRICS) ===
    st.subheader("🏆 Random Forest vs XGBoost Model Comparison")
    
    # Calculate RF metrics
    mae_rf = np.mean(np.abs(df['Win Rate'] - df['predicted_win_rate']))
    mse_rf = np.mean((df['Win Rate'] - df['predicted_win_rate'])**2)
    rmse_rf = np.sqrt(mse_rf)
    r2_rf = 1 - (np.sum((df['Win Rate'] - df['predicted_win_rate'])**2) / np.sum((df['Win Rate'] - df['Win Rate'].mean())**2))
    
    # Calculate XGBoost metrics
    mae_xgb = np.mean(np.abs(df['Win Rate'] - df['xgb_pred_win_rate']))
    mse_xgb = np.mean((df['Win Rate'] - df['xgb_pred_win_rate'])**2)
    rmse_xgb = np.sqrt(mse_xgb)
    r2_xgb = 1 - (np.sum((df['Win Rate'] - df['xgb_pred_win_rate'])**2) / np.sum((df['Win Rate'] - df['Win Rate'].mean())**2))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌲 Random Forest Metrics**")
        st.metric("MAE", f"{mae_rf:.4f}")
        st.metric("MSE", f"{mse_rf:.4f}")
        st.metric("RMSE", f"{rmse_rf:.4f}")
        st.metric("R² Score", f"{r2_rf:.4f}")
        
    with col2:
        st.markdown("**🔥 XGBoost Metrics**")
        st.metric("MAE", f"{mae_xgb:.4f}")
        st.metric("MSE", f"{mse_xgb:.4f}")
        st.metric("RMSE", f"{rmse_xgb:.4f}")
        st.metric("R² Score", f"{r2_xgb:.4f}")
    
    fig_compare, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.scatter(df['Win Rate'], df['predicted_win_rate'], color='lime', label='RF', alpha=0.6)
    ax1.plot([0, 1], [0, 1], 'r--', lw=2)
    ax1.set_title("Random Forest")
    ax1.set_xlabel("Actual Win Rate")
    ax1.set_ylabel("Predicted Win Rate")
    ax1.grid(alpha=0.3)
    ax1.legend()
    
    ax2.scatter(df['Win Rate'], df['xgb_pred_win_rate'], color='orange', label='XGB', alpha=0.6)
    ax2.plot([0, 1], [0, 1], 'r--', lw=2)
    ax2.set_title("XGBoost")
    ax2.set_xlabel("Actual Win Rate")
    ax2.set_ylabel("Predicted Win Rate")
    ax2.grid(alpha=0.3)
    ax2.legend()
    
    st.pyplot(fig_compare)
    plt.close(fig_compare)


    

with tab3:
    st.header("🔍 Explore Any Team")
    
    # Team selection
    team_select = st.selectbox("Choose a Team:", ['Select a team...'] + df['Team'].sort_values().tolist())
    
    # Only show results after team is selected
    if team_select != 'Select a team...':
        team_row = df[df['Team'] == team_select].iloc[0]
        
        # Display key metrics
        st.subheader(f"📊 {team_select} - Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Win Rate", f"{team_row['Win Rate']:.3f}")
        with col2:
            st.metric("RF Score", f"{team_row['RF_Score']:.3f}")
        with col3:
            st.metric("XGB Score", f"{team_row['XGB_Score']:.3f}")
        with col4:
            st.metric("Final Score", f"{team_row['Final_Score']:.3f}")
        
        st.markdown("---")
        
        # === SCORE COMPARISON CHART ===
        st.subheader("📈 Score Comparison")
        
        scores_data = {
            'Metric': ['Win Rate', 'RF Score', 'XGB Score', 'Final Score'],
            'Value': [
                team_row['Win Rate'],
                team_row['RF_Score'],
                team_row['XGB_Score'],
                team_row['Final_Score']
            ]
        }
        scores_df = pd.DataFrame(scores_data)
        
        fig_scores, ax_scores = plt.subplots(figsize=(10, 5))
        bars = ax_scores.bar(scores_df['Metric'], scores_df['Value'], 
                             color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444'])
        ax_scores.set_ylabel('Score')
        ax_scores.set_title(f'{team_select} - Performance Scores')
        ax_scores.set_ylim(0, max(scores_df['Value']) * 1.2)
        ax_scores.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax_scores.annotate(f'{height:.3f}',
                              xy=(bar.get_x() + bar.get_width() / 2, height),
                              xytext=(0, 3),
                              textcoords="offset points",
                              ha='center', va='bottom',
                              fontsize=10, fontweight='bold')
        
        st.pyplot(fig_scores)
        plt.close(fig_scores)
        
        st.markdown("---")
        
        # === TOP FEATURES FOR THIS TEAM (SPECIFIC COLUMNS) ===
        st.subheader("🎯 Key Match Statistics")
        
        # Specific features to display
        key_features = ['Matches Played', 'Wins', 'Losses', 'Draws', 'Goal Difference']
        
        # Check which features exist in the dataframe
        available_features = [feat for feat in key_features if feat in df.columns]
        
        if available_features:
            feature_data = {}
            for feat in available_features:
                if pd.notna(team_row[feat]):
                    feature_data[feat] = team_row[feat]
            
            if feature_data:
                fig_feats, ax_feats = plt.subplots(figsize=(10, 5))
                feature_series = pd.Series(feature_data)
                bars = feature_series.plot(kind="barh", color='slateblue', ax=ax_feats)
                ax_feats.set_xlabel('Value')
                ax_feats.set_title(f'{team_select} - Match Statistics')
                ax_feats.grid(axis='x', alpha=0.3)
                
                # Add value labels
                for i, (feat, val) in enumerate(feature_data.items()):
                    ax_feats.text(val, i, f' {val:.0f}', va='center', fontsize=10, fontweight='bold')
                
                st.pyplot(fig_feats)
                plt.close(fig_feats)
            else:
                st.warning("No match statistics data available for this team.")
        else:
            st.warning("Match statistics columns not found in dataset.")
        
        st.markdown("---")
        
        # === TEAM RANKING ===
        st.subheader("🏆 Team Ranking")
        
        team_rank = df.sort_values('Final_Score', ascending=False).reset_index(drop=True)
        team_position = team_rank[team_rank['Team'] == team_select].index[0] + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Rank", f"#{team_position} / {len(df)}")
        with col2:
            cluster_id = team_row['Cluster']
            st.metric("Cluster", f"{cluster_id}")
        with col3:
            yearly_cluster_id = team_row['Yearly_Cluster']
            st.metric("Yearly Cluster", f"{yearly_cluster_id}")
        
        st.markdown("---")
        
        # === DETAILED STATS TABLE ===
        st.subheader("📋 Detailed Statistics")
        
        detail_cols = ['Team', 'Win Rate', 'Points', 'Goal Difference', 'Matches Played', 
                       'Wins', 'Draws', 'Losses', 'RF_Score', 'XGB_Score', 'Final_Score']
        available_cols = [col for col in detail_cols if col in df.columns]
        
        st.dataframe(
            team_row[available_cols].to_frame().T.style.highlight_max(axis=0, color='lightgreen'),
            use_container_width=True
        )
    else:
        st.info("👆 Please select a team from the dropdown to view detailed statistics.")


with tab4:
    st.header("Exploratory Data Analysis (EDA)")
    st.subheader("Summary Insights")
    
    summary_msg = f"""
- Highest Win Rate: {df['Team'][df['Win Rate'].idxmax()]} ({df['Win Rate'].max():.2f})
- Most Matches Played: {df['Team'][df['Matches Played'].idxmax()]} ({df['Matches Played'].max():.0f})
- Most Goals For: {df['Team'][df['Goals For'].idxmax()]} ({df['Goals For'].max():.0f})
- Typical Win Rate Range: {df['Win Rate'].min():.2f}–{df['Win Rate'].max():.2f}
- Dataset size: {len(df)} teams/rows
"""
    st.info(summary_msg)

    # Dataset info
    st.subheader("Dataset Info")
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)

    # Dataset statistics
    st.subheader("Dataset Summary Statistics")
    st.dataframe(df.describe())
    
    # Win Rate Table
    st.subheader("Win Rate Table")
    st.markdown("**The Win Rate is calculated as:**")
    st.code("Wins / Matches Played (if Matches Played > 0, else 0)")
    st.dataframe(df[['Team', 'Wins', 'Matches Played', 'Win Rate']])

    # Distribution of Win Rate
    st.subheader("Distribution of Win Rate Across Teams")
    fig, ax = plt.subplots(figsize=(4, 2))
    sns.histplot(df['Win Rate'], bins=20, kde=True, ax=ax)
    ax.set_title("Distribution of Win Rate Across Teams")
    ax.set_xlabel("Win Rate")
    st.pyplot(fig)
    plt.close(fig)

    # Correlation: Overall Aggregate Features
    overall_agg_features = [col for col in df.columns if not (
        col.endswith('_2010') or col.endswith('_2014') or
        col.endswith('_2018') or col.endswith('_2022') or col in ['Team', 'Win Rate', 'ID'])]
    numeric_overall_agg_features = [col for col in overall_agg_features if np.issubdtype(df[col].dtype, np.number)]
    
    st.subheader("Correlation Matrix: Overall Aggregate Features")
    fig_corr_overall, ax_corr_overall = plt.subplots(figsize=(15, 9))
    sns.heatmap(df[numeric_overall_agg_features + ['Win Rate']].corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax_corr_overall)
    ax_corr_overall.set_title('Correlation Matrix (Overall Aggregate Features)')
    st.pyplot(fig_corr_overall)
    plt.close(fig_corr_overall)

    # Win Rate Quartiles
    df['Win Rate Quartile'] = pd.qcut(df['Win Rate'], 4, labels=False)
    st.subheader("Win Rate Quartile Distribution")
    st.dataframe(df['Win Rate Quartile'].value_counts().sort_index())
    st.write("Win Rate Quartile Sample:", df[['Team', 'Win Rate', 'Win Rate Quartile']].head())
    
    yearly_stats_features = [col for col in df.columns if (
        col.endswith('_2010') or col.endswith('_2014') or
        col.endswith('_2018') or col.endswith('_2022'))]
    exclude_ids = ["ID_2010", "ID_2014", "ID_2018", "ID_2022"]
    numeric_yearly_features = [
        col for col in yearly_stats_features
        if np.issubdtype(df[col].dtype, np.number)
        and col not in exclude_ids
        and col.lower() != "id"
    ]
    
    # Group by Win Rate Quartile
    yearly_group_means = df.groupby('Win Rate Quartile')[numeric_yearly_features].mean()
    st.write("Yearly Group Means by Win Rate Quartile:")
    st.dataframe(yearly_group_means)

    st.subheader("Top 5 Teams by Win Rate")
    top_winrate = df.sort_values(by='Win Rate', ascending=False)[['Team', 'Win Rate']].head(5)
    st.dataframe(top_winrate)
    
    if 'Goals For' in df.columns:
        st.subheader("Top 5 Teams by Goals For")
        top_goals = df.sort_values(by='Goals For', ascending=False)[['Team', 'Goals For']].head(5)
        st.dataframe(top_goals)
        
    st.subheader("Top 5 Teams by Matches Played")
    top_matches = df.sort_values(by='Matches Played', ascending=False)[['Team', 'Matches Played']].head(5)
    st.dataframe(top_matches)

    st.subheader("Pairplot of Key Features (Win Rate, Goals For, Goals Against, Matches Played, Points)")
    pairplot_features = ["Win Rate", "Goals For", "Goals Against", "Matches Played", "Points"]
    existing_features = [col for col in pairplot_features if col in df.columns]
    pairplot = sns.pairplot(df[existing_features], height=1.8)
    st.pyplot(pairplot.figure)
    plt.close(pairplot.figure)
    
    st.markdown("---")
  
    # INTERACTIVE SECTION 1: FEATURE DISTRIBUTION
  
    st.subheader("📊 Feature Distribution Analysis")
    
    year_suffixes = ['2010', '2014', '2018', '2022']
    num_cols = [
        col for col in df.select_dtypes(include='number').columns
        if not any(year in col for year in year_suffixes)
    ]

    select_feat = st.selectbox(
        "Select a numeric feature to see its distribution",
        ['Select a feature...'] + num_cols
    )
    
    if select_feat != 'Select a feature...':
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(df[select_feat], bins=20, kde=True, ax=ax, color='#3b82f6')
        ax.set_xlabel(select_feat)
        ax.set_title(f"Distribution of {select_feat}")
        ax.grid(alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
        
        # Add statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean", f"{df[select_feat].mean():.2f}")
        with col2:
            st.metric("Median", f"{df[select_feat].median():.2f}")
        with col3:
            st.metric("Std Dev", f"{df[select_feat].std():.2f}")
        with col4:
            st.metric("Max", f"{df[select_feat].max():.2f}")
    else:
        st.info("👆 Please select a feature from the dropdown to view its distribution.")
    
    st.markdown("---")
    

    # INTERACTIVE SECTION 2: YEAR-OVER-YEAR TRENDS
 
    st.subheader("📈 Year-over-Year Trends for Key Stats")
    
    year_suffixes = ['2010', '2014', '2018', '2022']
    numeric_yearly_features_trend = []
    for col in df.columns:
        for year in year_suffixes:
            if col.endswith('_' + year) and np.issubdtype(df[col].dtype, np.number):
                base_feat = col.replace('_' + year, '')
                if not base_feat.lower().startswith('id'):
                    numeric_yearly_features_trend.append(base_feat)

    numeric_yearly_features_trend = sorted(list(set(numeric_yearly_features_trend)))

    selected_feature = st.selectbox(
        "Select Numeric Yearly Feature for Year-over-Year Trend",
        ['Select a feature...'] + numeric_yearly_features_trend
    )
    
    if selected_feature != 'Select a feature...':
        averages = []
        years_present = []
        for year in year_suffixes:
            yearly_col = f"{selected_feature}_{year}"
            if yearly_col in df.columns:
                averages.append(df[yearly_col].mean())
                years_present.append(int(year))
                
        if averages:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(years_present, averages, marker='o', linewidth=2, markersize=8, color='#10b981')
            ax.set_title(f"{selected_feature} Average Over Years")
            ax.set_xlabel("Year")
            ax.set_ylabel(f"{selected_feature} (Average)")
            ax.grid(alpha=0.3)
            
            # Add value labels on points
            for year, avg in zip(years_present, averages):
                ax.text(year, avg, f'{avg:.2f}', ha='center', va='bottom', fontweight='bold')
            
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("No numeric yearly columns found for the selected feature.")
    else:
        st.info("👆 Please select a feature from the dropdown to view year-over-year trends.")
    
    st.markdown("---")


    # INTERACTIVE DATASET SEARCH & FILTER
   
    st.subheader("🔍 Interactive Dataset Search & Filter")
    team_list = np.sort(df['Team'].unique())
    selected_teams = st.multiselect("Teams", team_list, default=list(team_list[:10]))
    
    if 'Win Rate Quartile' in df.columns:
        quartile_list = sorted(df['Win Rate Quartile'].unique())
        selected_quartiles = st.multiselect("Win Rate Quartile", quartile_list, default=quartile_list)
    else:
        selected_quartiles = None
        
    year_columns = [c for c in df.columns if any(yr in c for yr in ['2010','2014','2018','2022'])]
    if year_columns:
        selected_year_col = st.selectbox("Yearly Feature", options=year_columns)
    else:
        selected_year_col = None
        
    # Create a copy for filtering to avoid modifying original df
    filtered_df = df.copy()
    
    for col in ['Win Rate', 'Goals For', 'Matches Played']:
        if col in filtered_df.columns:
            min_val = float(filtered_df[col].min())
            max_val = float(filtered_df[col].max())
            slider = st.slider(f"Range for {col}", min_val, max_val, (min_val, max_val))
            filtered_df = filtered_df[(filtered_df[col] >= slider[0]) & (filtered_df[col] <= slider[1])]
            
    search_txt = st.text_input("Search Team Name")
    if search_txt:
        filtered_df = filtered_df[filtered_df['Team'].str.contains(search_txt, case=False, na=False)]
        
    filtered_df = filtered_df[filtered_df['Team'].isin(selected_teams)]
    if selected_quartiles is not None:
        filtered_df = filtered_df[filtered_df['Win Rate Quartile'].isin(selected_quartiles)]
        
    if selected_year_col:
        st.dataframe(filtered_df[['Team', selected_year_col]], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")
    
    st.subheader("📋 Full Dataset Preview")
    st.dataframe(df, use_container_width=True)
