import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="PHHS Bowling Tracker",
    page_icon="🎳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🎳 PHHS Unified Bowling Team")
st.subheader("Performance Hub")

# Initialize session state
if "players" not in st.session_state:
    st.session_state.players = {
        "Taylor": {
            "scores": [155, 162, 148, 171, 159],
            "dates": ["October 01, 2025", "October 08, 2025", "October 15, 2025", "October 22, 2025", "October 29, 2025"],
            "days_at_team": 15
        },
        "Tom": {
            "scores": [148, 151, 160, 155, 158],
            "dates": ["October 01, 2025", "October 08, 2025", "October 15, 2025", "October 22, 2025", "October 29, 2025"],
            "days_at_team": 15
        }
    }

if "announcements" not in st.session_state:
    st.session_state.announcements = [
        {
            "title": "Welcome to the Bowling Team!",
            "content": "We are excited to have you as part of our team. Let's work together to achieve our goals.",
            "date": "January 06, 2025"
        }
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for navigation
st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Manage Data", "Settings"])

# ============ DASHBOARD PAGE ============
if page == "Dashboard":
    
    # Team Highlights & Stats
    st.header("🏆 Team Highlights")
    col1, col2, col3, col4 = st.columns(4)
    
    all_scores = []
    for player in st.session_state.players.values():
        all_scores.extend(player["scores"])
    
    with col1:
        st.metric("Total Players", len(st.session_state.players))
    with col2:
        st.metric("Avg Team Score", f"{sum(all_scores)/len(all_scores):.1f}")
    with col3:
        st.metric("Highest Score", max(all_scores))
    with col4:
        st.metric("Lowest Score", min(all_scores))
    
    st.divider()
    
    # Player Score Progress
    st.header("📈 Player Score Progress")
    
    for player_name, player_data in st.session_state.players.items():
        with st.expander(f"📊 {player_name} - {len(player_data['scores'])} games"):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=player_data["dates"],
                y=player_data["scores"],
                mode='lines+markers',
                name=player_name,
                line=dict(color='#00D9FF', width=3),
                marker=dict(size=10)
            ))
            fig.update_layout(
                title=f"{player_name}'s Scoring Trend",
                xaxis_title="Date",
                yaxis_title="Score",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            avg = sum(player_data["scores"]) / len(player_data["scores"])
            st.write(f"**Average Score:** {avg:.1f}")
            st.write(f"**Days at Team:** {player_data['days_at_team']}")
    
    st.divider()
    
    # Announcements (moved below player progress)
    st.header("📢 Announcements")
    for announcement in st.session_state.announcements:
        st.info(f"**{announcement['title']}** *(Posted: {announcement['date']})*\n\n{announcement['content']}")
    
    st.divider()
    
    # Personal Milestones
    st.header("🎖️ Personal Milestones")
    if len(st.session_state.players) == 0:
        st.write("No players added yet")
    else:
        for player_name, player_data in st.session_state.players.items():
            avg_score = sum(player_data["scores"]) / len(player_data["scores"])
            highest = max(player_data["scores"])
            st.write(f"**{player_name}**")
            st.write(f"- Average Score: {avg_score:.1f}")
            st.write(f"- Personal Best: {highest}")
            st.write("")
    
    st.divider()
    
    # All Player Scores Table
    st.header("📋 All Player Scores")
    player_list = ["All Players"] + list(st.session_state.players.keys())
    selected_player = st.selectbox("Choose a player to view:", player_list)
    
    if selected_player == "All Players":
        all_data = []
        for name, data in st.session_state.players.items():
            for date, score in zip(data["dates"], data["scores"]):
                all_data.append({"Player": name, "Date": date, "Score": score})
        df = pd.DataFrame(all_data)
        st.dataframe(df, use_container_width=True)
    else:
        player_data = st.session_state.players[selected_player]
        df = pd.DataFrame({
            "Date": player_data["dates"],
            "Score": player_data["scores"]
        })
        st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Season Summary
    st.header("📅 Season Summary")
    st.write(f"**Total Games Played:** {len(all_scores)}")
    st.write(f"**Season Average:** {sum(all_scores)/len(all_scores):.1f}")
    st.write(f"**Best Performance:** {max(all_scores)}")

# ============ MANAGE DATA PAGE ============
elif page == "Manage Data":
    st.header("🔐 Coach Panel - Password Required")
    
    password = st.text_input("Enter coach password:", type="password")
    
    if password == "bowling2025":  # Change this password
        st.success("✅ Access granted!")
        
        tab1, tab2, tab3 = st.tabs(["Add/Edit Scores", "Announcements", "Players"])
        
        # TAB 1: Add/Edit Scores
        with tab1:
            st.subheader("📊 Add or Edit Scores")
            
            player_name = st.selectbox("Select Player:", list(st.session_state.players.keys()))
            
            if player_name:
                col1, col2 = st.columns(2)
                
                with col1:
                    new_score = st.number_input("Score:", min_value=0, max_value=300)
                with col2:
                    new_date = st.date_input("Date:")
                
                if st.button("➕ Add Score"):
                    st.session_state.players[player_name]["scores"].append(new_score)
                    st.session_state.players[player_name]["dates"].append(new_date.strftime("%B %d, %Y"))
                    st.success(f"✅ Score added for {player_name}!")
                    st.balloons()
        
        # TAB 2: Announcements
        with tab2:
            st.subheader("📢 Manage Announcements")
            
            announcement_title = st.text_input("Announcement Title:")
            announcement_content = st.text_area("Announcement Content:")
            announcement_date = st.date_input("Date:")
            
            if st.button("➕ Post Announcement"):
                st.session_state.announcements.append({
                    "title": announcement_title,
                    "content": announcement_content,
                    "date": announcement_date.strftime("%B %d, %Y")
                })
                st.success("✅ Announcement posted!")
                st.balloons()
        
        # TAB 3: Players
        with tab3:
            st.subheader("👥 Manage Players")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_player_name = st.text_input("Add new player:")
                if st.button("➕ Add Player"):
                    if new_player_name not in st.session_state.players:
                        st.session_state.players[new_player_name] = {
                            "scores": [],
                            "dates": [],
                            "days_at_team": 0
                        }
                        st.success(f"✅ {new_player_name} added!")
                        st.balloons()
            
            with col2:
                player_to_remove = st.selectbox("Remove player:", list(st.session_state.players.keys()))
                if st.button("🗑️ Remove Player"):
                    del st.session_state.players[player_to_remove]
                    st.success(f"🗑️ {player_to_remove} has been removed.")
                    st.balloons()
    
    elif password != "":
        st.error("❌ Incorrect password!")

# ============ SETTINGS PAGE ============
elif page == "Settings":
    st.header("⚙️ Settings")
    st.write("General app settings coming soon!")

# Footer
st.divider()
st.caption("Created by Sakshi | PHHS Unified Bowling Team")
