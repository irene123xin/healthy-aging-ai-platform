import pandas as pd
import streamlit as st
from src.ui import configure_page, get_repo, page_intro, selected_user

configure_page("History"); repo=get_repo(); user=selected_user(); attempts=repo.attempts(user.user_id)
page_intro("History","Activity history","Review recorded activities, feedback, and difficulty levels.")
if not attempts: st.info("Your completed activities will appear here.")
else:
    data=[{"Date":a.created_at.strftime("%b %d, %Y"),"Category":a.category,"Activity":a.exercise_type.replace("_"," ").title(),"Level":a.difficulty.title(),"Score":a.normalized_score,"Method":a.scoring_method.replace("_"," ").title(),"Feedback":a.feedback} for a in attempts]
    categories=st.multiselect("Filter categories",sorted({a.category for a in attempts}),default=sorted({a.category for a in attempts}))
    st.dataframe(pd.DataFrame(data).query("Category in @categories"),width="stretch",hide_index=True)
