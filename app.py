import streamlit as st

from src.recommendation.engine import RecommendationEngine
from src.ui import (CATEGORIES, configure_page, disclaimer, get_repo, page_intro,
                    recommendation_summary, selected_user)

configure_page("Home")
repo = get_repo()
page_intro("Home", "Today's training plan", "Cognitive exercises and optional movement, adjusted using your recent activity and daily check-in.")
user = selected_user(required=False)

if user is None:
    st.subheader("Create a local profile")
    st.caption("We only ask for information needed to personalize the experience. No medical history is collected.")
    with st.form("onboarding"):
        left, right = st.columns(2)
        with left:
            name = st.text_input("What should we call you?", placeholder="Alex")
            age = st.selectbox("Age range", ["50–59", "60–69", "70–79", "80+"])
            language = st.selectbox("Preferred language", ["English", "简体中文", "繁體中文", "Spanish"])
            minutes = st.select_slider("Preferred session length", [5, 10, 15, 20, 30], value=15)
        with right:
            goals = st.multiselect("Cognitive goals", CATEGORIES[:-1], default=["Memory", "Attention"])
            types = st.multiselect("Favorite activities", CATEGORIES, default=["Memory", "Language"])
            comfort = st.selectbox("Movement comfort", ["Seated", "Standing with support", "Light walking"])
            access = st.multiselect("Accessibility preferences", ["Larger text", "High contrast", "Short instructions", "Extra time"])
        if st.form_submit_button("Create my profile", type="primary", width="stretch"):
            if not name.strip(): st.error("Please enter a display name.")
            else:
                created = repo.create_user(display_name=name.strip(), age_range=age, preferred_language=language,
                    cognitive_goals=goals, preferred_session_length=minutes, preferred_training_types=types,
                    activity_comfort_level=comfort, accessibility_preferences=access)
                st.session_state.user_id = created.user_id; st.success("Profile created."); st.rerun()
else:
    checkin = repo.latest_checkin(user.user_id); attempts = repo.attempts(user.user_id)
    recommendation = RecommendationEngine().recommend(user, attempts, checkin, repo.sessions(user.user_id))
    recommendation_summary(recommendation)
    a,b,c = st.columns(3)
    with a:
        st.subheader("1. Check in"); st.write("Record today's energy, sleep, and available time.")
        st.page_link("pages/1_Daily_Checkin.py", label="Open check-in")
    with b:
        st.subheader("2. Train"); st.write(f"Current recommended focus: {recommendation.category}.")
        st.page_link("pages/2_Training.py", label="Open training")
    with c:
        st.subheader("3. Review"); st.write("Review performance, difficulty, and engagement trends.")
        st.page_link("pages/3_Dashboard.py", label="Open progress")
disclaimer()
