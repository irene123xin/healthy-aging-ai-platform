import streamlit as st
from src.ui import configure_page, disclaimer, get_repo, page_intro, selected_user

configure_page("Daily Check-in"); repo=get_repo(); user=selected_user()
page_intro("Daily check-in", "Readiness for today's session", "These inputs adjust session length and recommendation ranking.")
with st.form("checkin"):
    a,b=st.columns(2)
    with a:
        energy=st.select_slider("Energy level", range(1,6), value=3, format_func=lambda x: ["Very low","Low","Steady","Good","High"][x-1])
        mood=st.select_slider("Mood", range(1,6), value=3, format_func=lambda x: ["Low","A little low","Neutral","Good","Very good"][x-1])
        sleep=st.select_slider("Sleep quality", range(1,6), value=3, format_func=lambda x: ["Poor","Restless","Okay","Good","Restful"][x-1])
    with b:
        available=st.select_slider("Time available", [5,10,15,20,30], value=min(user.preferred_session_length,30), format_func=lambda x:f"{x} minutes")
        readiness=st.select_slider("Readiness", range(1,6), value=3, format_func=lambda x: ["Not ready","Unsure","Ready","Motivated","Very motivated"][x-1])
    if st.form_submit_button("Save check-in", type="primary", width="stretch"):
        repo.save_checkin(user.user_id,energy_level=energy,mood=mood,sleep_quality=sleep,available_training_time=available,perceived_readiness=readiness)
        st.success("Check-in saved."); st.page_link("pages/2_Training.py",label="Continue to training")
disclaimer()
