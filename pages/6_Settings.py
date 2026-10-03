import streamlit as st
from src.ui import CATEGORIES, configure_page, get_repo, page_intro, selected_user

configure_page("Settings"); repo=get_repo(); user=selected_user(); page_intro("Settings","Profile and accessibility","Update session preferences and accessibility options.")
with st.form("settings"):
    name=st.text_input("Display name",user.display_name); language=st.selectbox("Preferred language",["English","简体中文","繁體中文","Spanish"],index=["English","简体中文","繁體中文","Spanish"].index(user.preferred_language) if user.preferred_language in ["English","简体中文","繁體中文","Spanish"] else 0)
    minutes=st.select_slider("Preferred session length",[5,10,15,20,30],value=user.preferred_session_length)
    types=st.multiselect("Preferred training",CATEGORIES,default=user.preferred_training_types); comfort=st.selectbox("Movement comfort",["Seated","Standing with support","Light walking"],index=["Seated","Standing with support","Light walking"].index(user.activity_comfort_level))
    access=st.multiselect("Accessibility",["Larger text","High contrast","Short instructions","Extra time"],default=user.accessibility_preferences)
    if st.form_submit_button("Save preferences",type="primary",width="stretch"): repo.update_user(user.user_id,display_name=name,preferred_language=language,preferred_session_length=minutes,preferred_training_types=types,activity_comfort_level=comfort,accessibility_preferences=access); st.success("Preferences saved.")
st.divider(); developer=st.toggle("Show developer diagnostics",value=False)
if developer:
    stats=repo.ai_diagnostics(); st.subheader("AI diagnostics")
    cols=st.columns(4); cols[0].metric("Requests",stats["requests"]); cols[1].metric("Success",f'{stats["success_rate"]:.0f}%'); cols[2].metric("Fallback",f'{stats["fallback_rate"]:.0f}%'); cols[3].metric("Avg latency",f'{stats["average_latency_ms"]:.0f} ms')
    st.json({"schema_valid_rate":stats["schema_valid_rate"],"validation_failures":stats["validation_failures"],"api_errors":stats["api_errors"],"estimated_tokens":stats["estimated_tokens"]})
