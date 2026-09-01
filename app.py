import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import re

# Page config
st.set_page_config(
    page_title=" PHHS Bowling Tracker",
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

def remove_emojis(text):
    """Remove emojis from text"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

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

if "zoom_level" not in st.session_state:
    st.session_state.zoom_level = 100  # Google-style: 100 = 100%

if "show_emojis" not in st.session_state:
    st.session_state.show_emojis = True

if "show_animations" not in st.session_state:
    st.session_state.show_animations = True

# ============ HELPER FUNCTIONS ============

def detect_milestones(player_name, scores, dates):
    """Auto-detect achievements based on score history"""
    milestones = []
    
    if not scores:
        return milestones
    
    # First game over 100
    if any(score > 100 for score in scores):
        milestone_text = "First game over 100!"
        milestones.append(("🎯", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    
    # Perfect game (300)
    if 300 in scores:
        milestone_text = "Perfect Game!"
        milestones.append(("🔥", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    
    # Improving trend
    if len(scores) >= 3:
        recent_three = scores[-3:]
        if recent_three[0] < recent_three[1] < recent_three[2]:
            milestone_text = "3-Game Improvement Streak!"
            milestones.append(("📈", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
        
        # Check for consistency
        if len(scores) >= 5:
            recent_five = scores[-5:]
            avg = sum(recent_five) / len(recent_five)
            if all(abs(s - avg) <= 10 for s in recent_five):
                milestone_text = "Consistent Performer!"
                milestones.append(("⭐", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    
    # High score achievement
    if max(scores) >= 200:
        milestone_text = "Elite Scorer!"
        milestones.append(("🏅", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    
    # Century mark (100+ average)
    if len(scores) >= 3:
        avg = sum(scores) / len(scores)
        if avg >= 150:
            milestone_text = "Century Achiever!"
            milestones.append(("👑", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    
    # Games played milestone
    if len(scores) == 10:
        milestone_text = "10 Games Milestone!"
        milestones.append(("🎮", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    elif len(scores) == 5:
        milestone_text = "5 Games Milestone!"
        milestones.append(("🎮", milestone_text) if st.session_state.show_emojis else ("", milestone_text))
    
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
        label = "Total Players" if not st.session_state.show_emojis else "👥 Total Players"
        st.metric(label, len(st.session_state.players))
    with col2:
        label = "Avg Team Score" if not st.session_state.show_emojis else "📊 Avg Team Score"
        st.metric(label, f"{sum(all_scores)/len(all_scores):.1f}" if all_scores else "N/A")
    with col3:
        label = "Highest Score" if not st.session_state.show_emojis else "🏅 Highest Score"
        st.metric(label, max(all_scores) if all_scores else "N/A")
    
    st.divider()
    
    # Player Score Progress
    st.header("Player Score Progress & Achievements")
    
    for player_name, player_data in st.session_state.players.items():
        expander_label = f"{player_name} - {len(player_data['scores'])} games"
        if st.session_state.show_emojis:
            expander_label = f"📊 {expander_label} 🎮"
        
        with st.expander(expander_label):
            
            # Personal Milestones for this player
            milestones = detect_milestones(player_name, player_data["scores"], player_data["dates"])
            
            if milestones:
                st.subheader("Personal Milestones")
                for emoji, milestone_text in milestones:
                    display_text = f"{emoji} {milestone_text}".strip()
                    st.success(display_text)
            
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
            chart_title = f"{player_name}'s Scoring Trend" if not st.session_state.show_emojis else f"{player_name}'s 📈 Scoring Trend"
            fig.update_layout(
                title=chart_title,
                xaxis_title="Date" if not st.session_state.show_emojis else "📅 Date",
                yaxis_title="Score" if not st.session_state.show_emojis else "🎳 Score",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            avg = sum(player_data["scores"]) / len(player_data["scores"]) if player_data["scores"] else 0
            with col1:
                label = "Average Score" if not st.session_state.show_emojis else "📊 Average Score"
                st.metric(label, f"{avg:.1f}")
            with col2:
                label = "Best Score" if not st.session_state.show_emojis else "🔥 Best Score"
                st.metric(label, max(player_data["scores"]) if player_data["scores"] else "N/A")
            with col3:
                label = "Days at Team" if not st.session_state.show_emojis else "📅 Days at Team"
                st.metric(label, player_data['days_at_team'])
    
    st.divider()
    
    # Announcements
    st.header("Announcements & Updates")
    if st.session_state.announcements:
        for announcement in st.session_state.announcements:
            ann_header = f"{announcement['title']} (Posted: {announcement['date']})"
            if st.session_state.show_emojis:
                ann_header = f"📌 **{announcement['title']}** *(Posted: {announcement['date']})*"
            st.info(f"{ann_header}\n\n{announcement['content']}")
    else:
        st.write("No announcements yet")
    
    st.divider()
    
    # Team Achievements
    st.header("Team Achievements")
    st.write("Total Combined Games: " + str(len(all_scores)))
    if st.session_state.show_emojis:
        st.write("🎯 Total Combined Games: " + str(len(all_scores)))
    st.write("Team Average: " + (f"{sum(all_scores)/len(all_scores):.1f}" if all_scores else "N/A"))
    if st.session_state.show_emojis:
        st.write("📊 Team Average: " + (f"{sum(all_scores)/len(all_scores):.1f}" if all_scores else "N/A"))
    
    st.divider()
    
    # All Player Scores Table
    st.header("All Player Scores")
    player_list = ["All Players"] + list(st.session_state.players.keys())
    if st.session_state.show_emojis:
        player_list = ["👥 All Players"] + list(st.session_state.players.keys())
    
    selected_player = st.selectbox("Choose a player to view:", player_list)
    
    if selected_player == "👥 All Players" or selected_player == "All Players":
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

# ============ COACH PANEL PAGE ============
elif page == "🔐 Coach Panel":
    st.header("Coach Panel - Password Required")
    
    password = st.text_input("Enter coach password:", type="password", key="coach_password")
    
    if password == "bowling2025":  # Change this password
        st.success("Access granted!")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Add/Edit Scores", "Manage Announcements", "Manage Players", "Team Settings"])
        
        # TAB 1: Add/Edit Scores
        with tab1:
            st.subheader("Score Management")
            
            player_name = st.selectbox("Select Player:", list(st.session_state.players.keys()), key="score_player_select")
            
            if player_name:
                # Display existing scores
                st.write("### Existing Scores:")
                player_data = st.session_state.players[player_name]
                
                score_df = pd.DataFrame({
                    "Date": player_data["dates"],
                    "Score": player_data["scores"],
                    "Index": range(len(player_data["scores"]))
                })
                st.dataframe(score_df, use_container_width=True)
                
                # Delete score
                st.write("### Delete a Score:")
                score_to_delete = st.number_input("Enter score index to delete:", min_value=0, max_value=len(player_data["scores"])-1 if player_data["scores"] else 0, key="delete_score_index")
                
                if st.button("Delete Selected Score"):
                    if 0 <= score_to_delete < len(player_data["scores"]):
                        player_data["scores"].pop(score_to_delete)
                        player_data["dates"].pop(score_to_delete)
                        save_data()
                        st.success(f"Score deleted!")
                        st.balloons()
                
                st.divider()
                
                # Add new score
                st.write("### Add New Score:")
                col1, col2 = st.columns(2)
                
                with col1:
                    new_score = st.number_input("Score:", min_value=0, max_value=300, key="new_score_input")
                with col2:
                    new_date = st.date_input("Date:", key="manage_data_score_date")
                
                if st.button("Add Score"):
                    st.session_state.players[player_name]["scores"].append(new_score)
                    st.session_state.players[player_name]["dates"].append(new_date.strftime("%B %d, %Y"))
                    save_data()
                    st.success(f"Score added for {player_name}!")
                    st.balloons()
        
        # TAB 2: Announcements
        with tab2:
            st.subheader("Announcement Management")
            
            # View & Edit/Delete existing announcements
            st.write("### Existing Announcements:")
            
            if st.session_state.announcements:
                for idx, announcement in enumerate(st.session_state.announcements):
                    with st.expander(f"{announcement['title']} - {announcement['date']}"):
                        st.write(f"**Content:** {announcement['content']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Edit", key=f"edit_ann_{idx}"):
                                st.session_state[f"editing_announcement_{idx}"] = True
                        with col2:
                            if st.button(f"Delete", key=f"delete_ann_{idx}"):
                                st.session_state.announcements.pop(idx)
                                save_data()
                                st.success("Announcement deleted!")
                                st.balloons()
                        
                        # Edit form
                        if st.session_state.get(f"editing_announcement_{idx}", False):
                            st.write("### Edit Announcement:")
                            edit_title = st.text_input("Title:", value=announcement['title'], key=f"edit_title_{idx}")
                            edit_content = st.text_area("Content:", value=announcement['content'], key=f"edit_content_{idx}")
                            
                            if st.button("Save Changes", key=f"save_edit_{idx}"):
                                st.session_state.announcements[idx]["title"] = edit_title
                                st.session_state.announcements[idx]["content"] = edit_content
                                save_data()
                                st.success("Announcement updated!")
                                st.balloons()
                                st.session_state[f"editing_announcement_{idx}"] = False
            else:
                st.write("No announcements yet")
            
            st.divider()
            
            # Post new announcement
            st.write("### Post New Announcement:")
            announcement_title = st.text_input("Announcement Title:", key="new_ann_title")
            announcement_content = st.text_area("Announcement Content:", key="new_ann_content")
            announcement_date = st.date_input("Date:", key="manage_data_announcement_date")
            
            if st.button("Post Announcement"):
                if announcement_title and announcement_content:
                    st.session_state.announcements.append({
                        "title": announcement_title,
                        "content": announcement_content,
                        "date": announcement_date.strftime("%B %d, %Y")
                    })
                    save_data()
                    st.success("Announcement posted!")
                    st.balloons()
                else:
                    st.error("Please fill in all fields!")
        
        # TAB 3: Players
        with tab3:
            st.subheader("Player Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Add New Player:")
                new_player_name = st.text_input("Add new player:", key="new_player_input")
                if st.button("Add Player"):
                    if new_player_name and new_player_name not in st.session_state.players:
                        st.session_state.players[new_player_name] = {
                            "scores": [],
                            "dates": [],
                            "days_at_team": 0
                        }
                        save_data()
                        st.success(f"{new_player_name} added!")
                        st.balloons()
                    elif new_player_name in st.session_state.players:
                        st.error("Player already exists!")
            
            with col2:
                st.write("### Remove Player:")
                if st.session_state.players:
                    player_to_remove = st.selectbox("Remove player:", list(st.session_state.players.keys()), key="remove_player_select")
                    if st.button("Remove Player"):
                        del st.session_state.players[player_to_remove]
                        save_data()
                        st.success(f"{player_to_remove} has been removed.")
                        st.balloons()
        
        # TAB 4: Team Settings (Persistent)
        with tab4:
            st.subheader("Team Settings (Permanently Saved)")
            st.write("*These settings are saved permanently and shared across all sessions*")
            
            col1, col2 = st.columns(2)
            
            with col1:
                team_name = st.text_input("Team Name:", value=st.session_state.team_settings.get("team_name", "PHHS Bowling Team"), key="settings_team_name_permanent")
            
            with col2:
                max_players = st.number_input("Max Players:", min_value=1, value=st.session_state.team_settings.get("max_players", 20), key="settings_max_players_permanent")
            
            if st.button("Save Team Settings"):
                st.session_state.team_settings["team_name"] = team_name
                st.session_state.team_settings["max_players"] = max_players
                save_data()
                st.success("Team Settings Saved Permanently!")
                st.balloons()
    
    elif password != "":
        st.error("Incorrect password!")

# ============ SETTINGS PAGE ============
elif page == "⚙️ Settings":
    st.header("Settings & Preferences")
    
    col_session, col_info = st.columns([2, 1])
    
    with col_session:
        st.write("**Session-Only Settings** *(Reset when you close/refresh the app)*")
    with col_info:
        st.info("Each device has its own settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Zoom Level (Like Google)")
        st.write("*Adjust page zoom for this session only*")
        
        # Google-style zoom: 75%, 90%, 100%, 110%, 125%, 150%
        zoom_options = [75, 90, 100, 110, 125, 150]
        zoom_value = st.select_slider(
            "Zoom Level:",
            options=zoom_options,
            value=st.session_state.zoom_level,
            key="zoom_slider"
        )
        st.session_state.zoom_level = zoom_value
        st.success(f"Zoom set to {zoom_value}% (Session only)")
    
    with col2:
        st.subheader("Date Range Settings")
        st.write("*Set your preferred date range (session only)*")
        start_date = st.date_input("Start Date:", key="settings_start_date")
        end_date = st.date_input("End Date:", key="settings_end_date")
        st.info(f"Range: {start_date} to {end_date} (Session only)")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Display Preferences (Session Only)")
        show_emojis = st.checkbox("Show Emojis in UI", value=st.session_state.show_emojis, key="show_emojis_checkbox")
        show_animations = st.checkbox("Show Animations", value=st.session_state.show_animations, key="show_animations_checkbox")
        
        # Update session state when checkboxes change
        if show_emojis != st.session_state.show_emojis:
            st.session_state.show_emojis = show_emojis
            st.success(f"Emojis {'enabled' if show_emojis else 'disabled'}!")
            st.rerun()
        
        if show_animations != st.session_state.show_animations:
            st.session_state.show_animations = show_animations
            st.success(f"Animations {'enabled' if show_animations else 'disabled'}!")
        
        st.info("Independent settings per browser/device session.")
    
    with col2:
        st.subheader("Current Team Settings")
        team_name = st.session_state.team_settings.get('team_name', 'PHHS Bowling Team')
        max_players = st.session_state.team_settings.get('max_players', 20)
        
        if st.session_state.show_emojis:
            st.write(f"🎳 **Team Name:** {team_name}")
            st.write(f"👥 **Max Players:** {max_players}")
        else:
            st.write(f"**Team Name:** {team_name}")
            st.write(f"**Max Players:** {max_players}")
    
    st.divider()
    
    if st.button("Save Session Settings"):
        st.success("Session settings saved! (Resets on app refresh)")
        st.balloons()
    
    st.divider()

# ============ APPLY ZOOM & DISPLAY PREFERENCES ============
# Apply zoom level as percentage using CSS
zoom_percentage = st.session_state.zoom_level / 100
st.markdown(f"""
    <style>
        * {{
            zoom: {zoom_percentage};
        }}
    </style>
""", unsafe_allow_html=True)

# Apply animation toggle via CSS
if not st.session_state.get("show_animations", True):
    st.markdown("""
        <style>
            * {
                animation: none !important;
                transition: none !important;
            }
            .stSpinner, .stProgress {
                display: none !important;
            }
            .balloon {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Footer with info
st.divider()

# Calculate token usage percentage (approximate)
token_info = st.sidebar.container()
with token_info:
    st.sidebar.divider()
    st.sidebar.header("Session Info")
    st.sidebar.write("Session Started: 2026-07-01")
    st.sidebar.write("Session Duration: Ongoing")

st.caption("Created by Sakshi.M | PHHS Unified Bowling Team")
