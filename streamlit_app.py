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

# ── Hide Streamlit chrome for a cleaner look ───────────────────────────────
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* Hide the iframe's own scrollbar — we use page scroll only */
        iframe[title="streamlit_app.streamlit_app"] {
            overflow: hidden !important;
        }
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

# scrolling=False removes the inner iframe scrollbar.
# height=2200 is tall enough for the longest tab (metalanguage + tech table).
# The browser's own page scrollbar is then the only one visible.
components.html(html_content, height=2200, scrolling=False)
