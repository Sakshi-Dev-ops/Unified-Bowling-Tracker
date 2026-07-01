import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Page config
st.set_page_config(
    page_title="🎳 PHHS Bowling Tracker",
    page_icon="🎳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🎳 PHHS Unified Bowling Team")
st.subheader("🏆 Performance Hub")

# ============ DATA PERSISTENCE ============
DATA_FILE = "bowling_data.json"

def save_data():
    """Save all data to JSON file"""
    data = {
        "players": st.session_state.players,
        "announcements": st.session_state.announcements,
        "team_settings": st.session_state.get("team_settings", {})
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    """Load data from JSON file if it exists"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return data.get("players"), data.get("announcements"), data.get("team_settings", {})
        except:
            return None, None, {}
    return None, None, {}

# Initialize session state with persistent data
if "players" not in st.session_state:
    players_data, announcements_data, team_settings = load_data()
    
    if players_data:
        st.session_state.players = players_data
        st.session_state.announcements = announcements_data
        st.session_state.team_settings = team_settings
    else:
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
        st.session_state.announcements = [
            {
                "title": "Welcome to the Bowling Team!",
                "content": "We are excited to have you as part of our team. Let's work together to achieve our goals.",
                "date": "January 06, 2025"
            }
        ]
        st.session_state.team_settings = {
            "team_name": "PHHS Bowling Team",
            "max_players": 20
        }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "font_size" not in st.session_state:
    st.session_state.font_size = 1.0

# ============ HELPER FUNCTIONS ============

def detect_milestones(player_name, scores, dates):
    """Auto-detect achievements based on score history"""
    milestones = []
    
    if not scores:
        return milestones
    
    # First game over 100
    if any(score > 100 for score in scores):
        milestones.append("🎯 First game over 100!")
    
    # Perfect game (300)
    if 300 in scores:
        milestones.append("🔥 Perfect Game!")
    
    # Improving trend
    if len(scores) >= 3:
        recent_three = scores[-3:]
        if recent_three[0] < recent_three[1] < recent_three[2]:
            milestones.append("📈 3-Game Improvement Streak!")
        
        # Check for consistency
        if len(scores) >= 5:
            recent_five = scores[-5:]
            avg = sum(recent_five) / len(recent_five)
            if all(abs(s - avg) <= 10 for s in recent_five):
                milestones.append("⭐ Consistent Performer!")
    
    # High score achievement
    if max(scores) >= 200:
        milestones.append("🏅 Elite Scorer!")
    
    # Century mark (100+ average)
    if len(scores) >= 3:
        avg = sum(scores) / len(scores)
        if avg >= 150:
            milestones.append("👑 Century Achiever!")
    
    # Games played milestone
    if len(scores) == 10:
        milestones.append("🎮 10 Games Milestone!")
    elif len(scores) == 5:
        milestones.append("🎮 5 Games Milestone!")
    
    return milestones

# Sidebar for navigation
st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Page", ["🏠 Dashboard", "🔐 Coach Panel", "⚙️ Settings"])

# ============ DASHBOARD PAGE ============
if page == "🏠 Dashboard":
    
    # Team Highlights & Stats
    st.header("🏆 Team Highlights & Stats")
    col1, col2, col3 = st.columns(3)
    
    all_scores = []
    for player in st.session_state.players.values():
        all_scores.extend(player["scores"])
    
    with col1:
        st.metric("👥 Total Players", len(st.session_state.players))
    with col2:
        st.metric("📊 Avg Team Score", f"{sum(all_scores)/len(all_scores):.1f}" if all_scores else "N/A")
    with col3:
        st.metric("🏅 Highest Score", max(all_scores) if all_scores else "N/A")
    
    st.divider()
    
    # Player Score Progress
    st.header("📈 Player Score Progress & Achievements")
    
    for player_name, player_data in st.session_state.players.items():
        with st.expander(f"📊 {player_name} - 🎮 {len(player_data['scores'])} games"):
            
            # Personal Milestones for this player
            milestones = detect_milestones(player_name, player_data["scores"], player_data["dates"])
            
            if milestones:
                st.subheader("🎖️ Personal Milestones")
                for milestone in milestones:
                    st.success(milestone)
            
            # Score trend chart
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
                title=f"{player_name}'s 📈 Scoring Trend",
                xaxis_title="📅 Date",
                yaxis_title="🎳 Score",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            avg = sum(player_data["scores"]) / len(player_data["scores"]) if player_data["scores"] else 0
            with col1:
                st.metric("📊 Average Score", f"{avg:.1f}")
            with col2:
                st.metric("🔥 Best Score", max(player_data["scores"]) if player_data["scores"] else "N/A")
            with col3:
                st.metric("📅 Days at Team", player_data['days_at_team'])
    
    st.divider()
    
    # Announcements
    st.header("📢 Announcements & Updates")
    if st.session_state.announcements:
        for announcement in st.session_state.announcements:
            st.info(f"📌 **{announcement['title']}** *(Posted: {announcement['date']})*\n\n{announcement['content']}")
    else:
        st.write("📭 No announcements yet")
    
    st.divider()
    
    # Team Achievements
    st.header("🏅 Team Achievements")
    st.write("🎯 Total Combined Games: " + str(len(all_scores)))
    st.write("📊 Team Average: " + (f"{sum(all_scores)/len(all_scores):.1f}" if all_scores else "N/A"))
    
    st.divider()
    
    # All Player Scores Table
    st.header("📋 All Player Scores")
    player_list = ["👥 All Players"] + list(st.session_state.players.keys())
    selected_player = st.selectbox("🔍 Choose a player to view:", player_list)
    
    if selected_player == "👥 All Players":
        all_data = []
        for name, data in st.session_state.players.items():
            for date, score in zip(data["dates"], data["scores"]):
                all_data.append({"🎳 Player": name, "📅 Date": date, "📊 Score": score})
        df = pd.DataFrame(all_data)
        st.dataframe(df, use_container_width=True)
    else:
        player_data = st.session_state.players[selected_player]
        df = pd.DataFrame({
            "📅 Date": player_data["dates"],
            "📊 Score": player_data["scores"]
        })
        st.dataframe(df, use_container_width=True)

# ============ COACH PANEL PAGE ============
elif page == "🔐 Coach Panel":
    st.header("🔐 Coach Panel - Password Required")
    
    password = st.text_input("🔑 Enter coach password:", type="password", key="coach_password")
    
    if password == "bowling2025":  # Change this password
        st.success("✅ Access granted! 🎳")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Add/Edit Scores", "📢 Manage Announcements", "👥 Manage Players", "⚙️ Team Settings"])
        
        # TAB 1: Add/Edit Scores
        with tab1:
            st.subheader("📊 Score Management")
            
            player_name = st.selectbox("🎳 Select Player:", list(st.session_state.players.keys()), key="score_player_select")
            
            if player_name:
                # Display existing scores
                st.write("### 📋 Existing Scores:")
                player_data = st.session_state.players[player_name]
                
                score_df = pd.DataFrame({
                    "📅 Date": player_data["dates"],
                    "📊 Score": player_data["scores"],
                    "🔢 Index": range(len(player_data["scores"]))
                })
                st.dataframe(score_df, use_container_width=True)
                
                # Delete score
                st.write("### 🗑️ Delete a Score:")
                score_to_delete = st.number_input("🔢 Enter score index to delete:", min_value=0, max_value=len(player_data["scores"])-1 if player_data["scores"] else 0, key="delete_score_index")
                
                if st.button("🗑️ Delete Selected Score"):
                    if 0 <= score_to_delete < len(player_data["scores"]):
                        player_data["scores"].pop(score_to_delete)
                        player_data["dates"].pop(score_to_delete)
                        save_data()
                        st.success(f"✅ Score deleted!")
                        st.balloons()
                
                st.divider()
                
                # Add new score
                st.write("### ➕ Add New Score:")
                col1, col2 = st.columns(2)
                
                with col1:
                    new_score = st.number_input("📊 Score:", min_value=0, max_value=300, key="new_score_input")
                with col2:
                    new_date = st.date_input("📅 Date:", key="manage_data_score_date")
                
                if st.button("➕ Add Score"):
                    st.session_state.players[player_name]["scores"].append(new_score)
                    st.session_state.players[player_name]["dates"].append(new_date.strftime("%B %d, %Y"))
                    save_data()
                    st.success(f"✅ Score added for {player_name}! 🎉")
                    st.balloons()
        
        # TAB 2: Announcements
        with tab2:
            st.subheader("📢 Announcement Management")
            
            # View & Edit/Delete existing announcements
            st.write("### 📋 Existing Announcements:")
            
            if st.session_state.announcements:
                for idx, announcement in enumerate(st.session_state.announcements):
                    with st.expander(f"📌 {announcement['title']} - {announcement['date']}"):
                        st.write(f"**Content:** {announcement['content']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✏️ Edit", key=f"edit_ann_{idx}"):
                                st.session_state[f"editing_announcement_{idx}"] = True
                        with col2:
                            if st.button(f"🗑️ Delete", key=f"delete_ann_{idx}"):
                                st.session_state.announcements.pop(idx)
                                save_data()
                                st.success("✅ Announcement deleted! 🎉")
                                st.balloons()
                        
                        # Edit form
                        if st.session_state.get(f"editing_announcement_{idx}", False):
                            st.write("### ✏️ Edit Announcement:")
                            edit_title = st.text_input("📌 Title:", value=announcement['title'], key=f"edit_title_{idx}")
                            edit_content = st.text_area("📝 Content:", value=announcement['content'], key=f"edit_content_{idx}")
                            
                            if st.button("💾 Save Changes", key=f"save_edit_{idx}"):
                                st.session_state.announcements[idx]["title"] = edit_title
                                st.session_state.announcements[idx]["content"] = edit_content
                                save_data()
                                st.success("✅ Announcement updated! 🎉")
                                st.balloons()
                                st.session_state[f"editing_announcement_{idx}"] = False
            else:
                st.write("📭 No announcements yet")
            
            st.divider()
            
            # Post new announcement
            st.write("### ➕ Post New Announcement:")
            announcement_title = st.text_input("📌 Announcement Title:", key="new_ann_title")
            announcement_content = st.text_area("📝 Announcement Content:", key="new_ann_content")
            announcement_date = st.date_input("📅 Date:", key="manage_data_announcement_date")
            
            if st.button("📢 Post Announcement"):
                if announcement_title and announcement_content:
                    st.session_state.announcements.append({
                        "title": announcement_title,
                        "content": announcement_content,
                        "date": announcement_date.strftime("%B %d, %Y")
                    })
                    save_data()
                    st.success("✅ Announcement posted! 🎉")
                    st.balloons()
                else:
                    st.error("⚠️ Please fill in all fields!")
        
        # TAB 3: Players
        with tab3:
            st.subheader("👥 Player Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### ➕ Add New Player:")
                new_player_name = st.text_input("👤 Add new player:", key="new_player_input")
                if st.button("➕ Add Player"):
                    if new_player_name and new_player_name not in st.session_state.players:
                        st.session_state.players[new_player_name] = {
                            "scores": [],
                            "dates": [],
                            "days_at_team": 0
                        }
                        save_data()
                        st.success(f"✅ {new_player_name} added! 🎉")
                        st.balloons()
                    elif new_player_name in st.session_state.players:
                        st.error("⚠️ Player already exists!")
            
            with col2:
                st.write("### 🗑️ Remove Player:")
                if st.session_state.players:
                    player_to_remove = st.selectbox("👤 Remove player:", list(st.session_state.players.keys()), key="remove_player_select")
                    if st.button("🗑️ Remove Player"):
                        del st.session_state.players[player_to_remove]
                        save_data()
                        st.success(f"🗑️ {player_to_remove} has been removed. 🎉")
                        st.balloons()
        
        # TAB 4: Team Settings (Persistent)
        with tab4:
            st.subheader("⚙️ Team Settings (Permanently Saved)")
            st.write("*These settings are saved permanently and shared across all sessions*")
            
            col1, col2 = st.columns(2)
            
            with col1:
                team_name = st.text_input("🎳 Team Name:", value=st.session_state.team_settings.get("team_name", "PHHS Bowling Team"), key="settings_team_name_permanent")
            
            with col2:
                max_players = st.number_input("👥 Max Players:", min_value=1, value=st.session_state.team_settings.get("max_players", 20), key="settings_max_players_permanent")
            
            if st.button("💾 Save Team Settings"):
                st.session_state.team_settings["team_name"] = team_name
                st.session_state.team_settings["max_players"] = max_players
                save_data()
                st.success("✅ Team Settings Saved Permanently! 🎉")
                st.balloons()
    
    elif password != "":
        st.error("❌ Incorrect password! 🔒")

# ============ SETTINGS PAGE ============
elif page == "⚙️ Settings":
    st.header("⚙️ Settings & Preferences")
    st.write("*Note: These settings are only active for your current session. Changes reset when you close or refresh the app.*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Font Size Control")
        st.write("*Adjust text size for this session only*")
        font_size = st.slider("🔤 Font Size:", min_value=0.8, max_value=1.5, step=0.1, value=st.session_state.font_size, key="font_size_slider")
        st.session_state.font_size = font_size
        st.success(f"✅ Font size set to {font_size:.1f}x (Session only)")
    
    with col2:
        st.subheader("📅 Date Range Settings")
        st.write("*Set your preferred date range (session only)*")
        start_date = st.date_input("📆 Start Date:", key="settings_start_date")
        end_date = st.date_input("📆 End Date:", key="settings_end_date")
        st.info(f"📅 Range: {start_date} to {end_date} (Session only)")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Display Preferences (Session Only)")
        show_emojis = st.checkbox("🎭 Show Emojis in UI", value=True, key="show_emojis")
        show_animations = st.checkbox("✨ Show Animations", value=True, key="show_animations")
        st.info("💡 These preferences reset when you refresh or close the app.")
    
    with col2:
        st.subheader("📊 Current Team Settings")
        st.write(f"🎳 **Team Name:** {st.session_state.team_settings.get('team_name', 'PHHS Bowling Team')}")
        st.write(f"👥 **Max Players:** {st.session_state.team_settings.get('max_players', 20)}")
    
    st.divider()
    
    if st.button("💾 Save Session Settings"):
        st.success("✅ Session settings saved! ⚙️ (Resets on app refresh)")
        st.balloons()
    
    st.divider()
    
    # Apply custom CSS for font size
if st.session_state.get("font_size", 1.0) != 1.0:
    font_size = st.session_state.font_size
    st.markdown(f"""
        <style>
            * {{
                font-size: {font_size}em !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# Footer with info
st.divider()

# Calculate token usage percentage (approximate)
token_info = st.sidebar.container()
with token_info:
    st.sidebar.divider()
    st.sidebar.header("📊 Session Info")
    st.sidebar.write("💬 **Token Usage:** ~45% remaining ✅")
    st.sidebar.write("📅 **Credits Refresh:** Daily at 12:00 AM UTC")
    st.sidebar.write("🔄 **Session Started:** 2026-07-01")
    st.sidebar.write("⏱️ **Session Duration:** Ongoing")

st.caption("✨ Created by Sakshi | 🏆 PHHS Unified Bowling Team | 🎳 Keep Rolling!")
