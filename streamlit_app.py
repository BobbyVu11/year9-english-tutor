"""
Year 9 English Extension Tutor — Streamlit wrapper
====================================================
This file lets the tutor run on Streamlit Community Cloud (free hosting)
or locally via:  streamlit run streamlit_app.py

The entire app lives in index.html — this wrapper just loads that file
and renders it so it's accessible from any device with a browser.
"""

import pathlib
import streamlit as st
import streamlit.components.v1 as components

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Year 9 English Tutor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Hide Streamlit chrome and remove outer page scroll ─────────────────────
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        /* Remove all padding so iframe fills the page */
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            max-width: 100% !important;
        }
        /* Hide Streamlit's own page scrollbar — the iframe handles scrolling */
        html, body { overflow: hidden; }
        [data-testid="stAppViewContainer"] { overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Year 9 English Tutor")
    st.markdown("**Victorian Curriculum · Year 9 → 10**")
    st.divider()
    st.markdown(
        """
**Sections**

✍️ **Writing** — Prompts + instant feedback
📖 **Reading** — Unseen passages + MCQ
🔤 **Vocabulary** — Flashcards + gap fill
🎭 **Metalanguage** — Technique ID quiz
📊 **Progress** — Activity tracker
        """
    )
    st.divider()
    st.markdown(
        """
**Tips**
- Dark/light toggle is in the top-right of the app
- Progress saves automatically in your browser
- Try to do at least one section per day
        """
    )
    st.divider()
    st.caption("© 2024 · Built for Victorian Curriculum Year 9")

# ── Load and render index.html ───────────────────────────────────────────────
html_file = pathlib.Path(__file__).parent / "index.html"

if not html_file.exists():
    st.error(
        "**index.html not found.**  "
        "Make sure `index.html` is in the same folder as `streamlit_app.py`."
    )
    st.stop()

html_content = html_file.read_text(encoding="utf-8")

# height=100vh equivalent via JS — iframe fills the screen, inner app scrolls
components.html(html_content, height=800, scrolling=True)
