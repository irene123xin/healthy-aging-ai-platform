import plotly.express as px
import streamlit as st
from src.analytics.insights import generate_insights
from src.analytics.metrics import attempts_frame, engagement_metrics
from src.analytics.trends import difficulty_trend, performance_trend
from src.recommendation.engine import RecommendationEngine
from src.ui import configure_page, get_repo, page_intro, selected_user

configure_page("Progress"); repo=get_repo(); user=selected_user(); attempts=repo.attempts(user.user_id); sessions=repo.sessions(user.user_id)
frame=attempts_frame(attempts); recommendation=RecommendationEngine().recommend(user,attempts,repo.latest_checkin(user.user_id),sessions); metrics=engagement_metrics(sessions); insights=generate_insights(frame,recommendation.category)
page_intro("Progress","Performance and participation","Scores, challenge level, and session activity over time.")
cols=st.columns(5)
for col,(label,value) in zip(cols,[("This week",metrics["sessions_this_week"]),("Total sessions",metrics["total_sessions"]),("Avg. minutes",metrics["average_duration"]),("Completion",f'{metrics["completion_rate"]}%'),("Streak",f'{metrics["current_streak"]} days')]): col.metric(label,value)
if frame.empty: st.info("No activity yet. Complete a training session—or generate demo data—to bring this dashboard to life.")
else:
    left,right=st.columns([3,2])
    trend=performance_trend(frame)
    left.plotly_chart(px.line(trend,x="date",y="rolling_score",color="category",markers=True,range_y=[0,100],labels={"rolling_score":"5-activity average","date":"Date","category":"Focus"}),width="stretch")
    diff=difficulty_trend(frame)
    right.plotly_chart(px.line(diff,x="date",y="difficulty_value",color="category",markers=True,range_y=[.8,3.2],labels={"difficulty_value":"Level (1–3)","date":"Date"}),width="stretch")
    a,b,c,d,e=st.columns(5)
    for col,key,label in zip([a,b,c,d,e],["strongest","weakest","focus","improvement","decline"],["Strongest","Developing","Focus next","Improving","Watch"]): col.metric(label,insights[key])
