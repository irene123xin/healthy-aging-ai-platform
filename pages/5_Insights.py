import streamlit as st
from src.analytics.insights import generate_insights
from src.analytics.metrics import attempts_frame
from src.recommendation.engine import RecommendationEngine
from src.ui import configure_page, get_repo, page_intro, recommendation_summary, selected_user

configure_page("Insights"); repo=get_repo(); user=selected_user(); attempts=repo.attempts(user.user_id); checkin=repo.latest_checkin(user.user_id); rec=RecommendationEngine().recommend(user,attempts,checkin,repo.sessions(user.user_id)); insights=generate_insights(attempts_frame(attempts),rec.category)
page_intro("Insights","Recommendation details","The ranking combines learning priority with an estimated probability of completing the proposed session.")
recommendation_summary(rec)
a,b,c=st.columns(3); a.metric("Strongest",insights["strongest"]); b.metric("Developing",insights["weakest"]); c.metric("Recent change",insights["improvement"])
st.subheader("Completion estimate"); st.progress(rec.completion_probability,text=f"{rec.completion_probability:.0%} estimated completion probability")
st.caption(f"Prediction source: {rec.completion_model.replace('_',' ')}. This is a planning input, not a health assessment.")
