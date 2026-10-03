import streamlit as st
from src.ai.client import LLMClient
from src.ai.evaluator import score_exercise
from src.ai.schemas import Difficulty, ExerciseSchema
from src.recommendation.engine import RecommendationEngine
from src.ui import (CATEGORIES, configure_page, disclaimer, get_repo, page_intro,
                    recommendation_summary, selected_user)

configure_page("Training"); repo=get_repo(); user=selected_user(); attempts=repo.attempts(user.user_id); checkin=repo.latest_checkin(user.user_id)
recommendation=RecommendationEngine().recommend(user,attempts,checkin,repo.sessions(user.user_id))
page_intro("Training", "Training activity", "Complete one activity or select a different category and difficulty.")
recommendation_summary(recommendation)
a,b=st.columns([2,1]); category=a.selectbox("Training category",CATEGORIES,index=CATEGORIES.index(recommendation.category)); difficulty=b.selectbox("Difficulty",list(Difficulty),index=list(Difficulty).index(recommendation.difficulty),format_func=lambda x:x.value.title())
key=f"{category}:{difficulty.value}"
if st.button("Create a new activity",type="primary",width="stretch") or st.session_state.get("exercise_key") != key:
    exercise=LLMClient(repo).generate_exercise(user.__dict__,category,difficulty,user.user_id)
    st.session_state.exercise=exercise.model_dump(mode="json"); st.session_state.exercise_key=key; st.session_state.pop("last_result",None)
exercise=ExerciseSchema.model_validate(st.session_state.exercise)
st.subheader(exercise.instruction)
if exercise.content.get("items"): st.info("  ·  ".join(exercise.content["items"]))
if exercise.content.get("sequence"): st.info("  →  ".join(map(str,exercise.content["sequence"])))
if exercise.content.get("movement"): st.info(f"{exercise.content['movement'].title()} · {exercise.content['repetitions']} repetitions")
with st.expander("Need a hint?"): st.write(exercise.hint)
label="What is your answer?" if category!="Movement" else "Choose what felt right"
if category=="Movement": response=st.radio(label,["completed","skipped"],format_func=str.title,horizontal=True)
else: response=st.text_area(label,height=120,placeholder="Type your response here…")
if st.button("Submit activity",width="stretch",disabled=not bool(response.strip())):
    session=repo.start_session(user.user_id); result=score_exercise(exercise,response)
    repo.save_attempt(session_id=session.session_id,user_id=user.user_id,category=category,exercise_type=exercise.exercise_type,difficulty=difficulty.value,prompt_content=exercise.model_dump(mode="json"),response=response,raw_score=result.raw_score,normalized_score=result.normalized_score,scoring_method=result.scoring_method,evaluator_version=result.evaluator_version,feedback=result.feedback)
    repo.complete_session(session.session_id,"skipped" if response=="skipped" else "completed"); st.session_state.last_result=(result.normalized_score,result.feedback)
if "last_result" in st.session_state:
    score,feedback=st.session_state.last_result; st.success(f"Score: {score:.0f}/100 — {feedback}")
disclaimer()
