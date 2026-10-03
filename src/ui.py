from __future__ import annotations

import streamlit as st

from src.database.repository import Repository

CATEGORIES = ["Memory", "Attention", "Reasoning", "Language", "Movement"]


def configure_page(title: str) -> None:
    st.set_page_config(page_title=f"{title} | Healthy Aging AI", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown("""
    <style>
    :root { --ink:#1d2925; --muted:#596963; --accent:#276653; --line:#dce2df; --surface:#f6f7f5; }
    .stApp { background:#fff; color:var(--ink); }
    html, body, [class*="css"] { font-size:18px; }
    h1 { font-size:clamp(2rem, 4vw, 3.25rem) !important; letter-spacing:-.035em; line-height:1.08 !important; }
    h2, h3 { letter-spacing:-.015em; }
    [data-testid="stSidebar"] { background:var(--surface); border-right:1px solid var(--line); }
    [data-testid="stMetric"] { border-top:2px solid var(--line); padding:1rem 0; }
    .page-header { padding:2.25rem 0 1.5rem; max-width:820px; border-bottom:1px solid var(--line); margin-bottom:1.5rem; }
    .section-label { color:var(--accent); font-weight:700; font-size:.82rem; text-transform:uppercase; letter-spacing:.08em; }
    .page-summary { color:var(--muted); font-size:1.1rem; line-height:1.55; max-width:720px; }
    .recommendation { border:1px solid var(--line); border-left:5px solid var(--accent); padding:1.25rem 1.4rem; margin:1rem 0 1.75rem; }
    .recommendation strong { color:var(--ink); }
    .disclaimer { border-top:1px solid var(--line); margin-top:2rem; padding:1rem 0; color:var(--muted); font-size:.84rem; }
    .stButton > button { min-height:50px; border-radius:6px; font-weight:650; padding:.6rem 1.1rem; }
    .stButton > button[kind="primary"] { background:var(--accent); border-color:var(--accent); }
    div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea { min-height:50px; border-radius:6px !important; }
    @media (max-width:700px) { .page-header{padding-top:1.25rem;} h1{font-size:2.15rem !important;} }
    </style>""", unsafe_allow_html=True)
    st.sidebar.markdown("### Healthy Aging AI")
    st.sidebar.caption("Adaptive training prototype")


@st.cache_resource
def get_repo() -> Repository:
    return Repository()


def selected_user(required: bool = True):
    repo = get_repo()
    users = repo.list_users()
    if not users:
        if required:
            st.warning("Create a profile on the Home page to continue.")
            st.page_link("app.py", label="Home")
            st.stop()
        return None
    options = {user.user_id: user.display_name for user in users}
    current = st.session_state.get("user_id", users[0].user_id)
    user_ids = list(options)
    selected = st.sidebar.selectbox("Active profile", user_ids, format_func=options.get,
                                    index=user_ids.index(current) if current in options else 0)
    st.session_state.user_id = selected
    return repo.get_user(selected)


def page_intro(label: str, title: str, text: str) -> None:
    st.markdown(f'<div class="page-header"><div class="section-label">{label}</div><h1>{title}</h1><p class="page-summary">{text}</p></div>',
                unsafe_allow_html=True)


def recommendation_summary(result) -> None:
    st.markdown(
        f'<div class="recommendation"><strong>{result.category} · {result.difficulty.value.title()} · {result.duration} minutes</strong><br>'
        f'{result.explanation}<br><small>Learning priority: {result.personalization_priority:.0%} · '
        f'Estimated completion probability: {result.completion_probability:.0%} · '
        f'Final recommendation score: {result.final_score:.0%}</small></div>',
        unsafe_allow_html=True,
    )


def disclaimer() -> None:
    st.markdown('<div class="disclaimer">General wellness support only. This application does not provide medical advice, diagnosis, or treatment. Movement is optional; stop if you feel pain, dizziness, or instability.</div>',
                unsafe_allow_html=True)
