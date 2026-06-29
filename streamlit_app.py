"""
Year 9 English Extension Tutor — Streamlit wrapper with user auth
=================================================================
Multi-user login so each student has separate progress tracking.

Default accounts (change passwords via Admin Panel after first login):
  admin   / admin123   → can manage users + use the tutor
  student / student123 → student account

Run locally:   streamlit run streamlit_app.py
Deploy to:     Streamlit Community Cloud (connect GitHub repo)

NOTE — Streamlit Cloud filesystem is ephemeral.  Users added through
the Admin Panel are saved to users.json on disk; on a fresh Cloud
deploy those changes are lost.  To make new accounts permanent:
  1. Use "Download users.json" in the Admin Panel
  2. Replace users.json in your GitHub repo and push
"""

import json
import hashlib
import pathlib
import streamlit as st
import streamlit.components.v1 as components

BASE = pathlib.Path(__file__).parent
USERS_FILE = BASE / "users.json"

# ── Helpers ──────────────────────────────────────────────────────────────────

def hash_pw(pw: str) -> str:
    """SHA-256 hash of the password (strip whitespace first)."""
    return hashlib.sha256(pw.strip().encode()).hexdigest()


def load_users() -> dict:
    """Load users.json, creating a default admin account if it doesn't exist."""
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    default = {"users": [{
        "username": "admin",
        "password": hash_pw("admin123"),
        "role": "admin",
        "display_name": "Administrator",
    }]}
    USERS_FILE.write_text(json.dumps(default, indent=2), encoding="utf-8")
    return default


def save_users(data: dict):
    USERS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def find_user(username: str, data: dict) -> dict | None:
    for u in data["users"]:
        if u["username"].lower() == username.strip().lower():
            return u
    return None


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Year 9 English Tutor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome; keep slim top-padding for the welcome bar
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0;
            padding-left: 0;
            padding-right: 0;
        }
        iframe[title="streamlit_app.streamlit_app"] {
            overflow: hidden !important;
        }
        /* Form card background */
        div[data-testid="stForm"] {
            background: #f0f4ff;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #c5d0f5;
        }

        /* Text input fields */
        div[data-testid="stTextInput"] input {
            background-color: #ffffff !important;
            border: 1.5px solid #8fa8f5 !important;
            border-radius: 8px !important;
            padding: 0.45rem 0.75rem !important;
            color: #1a1a2e !important;
            transition: border-color 0.2s;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #4a6cf7 !important;
            box-shadow: 0 0 0 3px rgba(74,108,247,0.15) !important;
        }

        /* Selectbox */
        div[data-testid="stSelectbox"] > div > div {
            background-color: #ffffff !important;
            border: 1.5px solid #8fa8f5 !important;
            border-radius: 8px !important;
        }

        /* Labels */
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label {
            font-weight: 600 !important;
            color: #2d3a8c !important;
            font-size: 0.85rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state init ────────────────────────────────────────────────────────

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.display_name = ""


# ── Login page ─────────────────────────────────────────────────────────────────

def show_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("## 📚 Year 9 English Tutor")
        st.markdown("*Victorian Curriculum · Year 10 Extension*")
        st.divider()

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="e.g. bobby")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("→ Log in", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both a username and password.")
            else:
                data = load_users()
                user = find_user(username, data)
                if user and user["password"] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.username = user["username"]
                    st.session_state.role = user["role"]
                    st.session_state.display_name = user.get("display_name", user["username"])
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        st.caption("Contact the admin if you need an account or forgot your password.")


# ── Admin panel ────────────────────────────────────────────────────────────────

def show_admin():
    # Top bar: welcome + logout
    col_title, col_logout = st.columns([8, 1])
    with col_title:
        st.markdown(f"⚙️ **Admin Panel** — logged in as **{st.session_state.display_name}**")
    with col_logout:
        if st.button("Log out", key="admin_logout"):
            for k in ("logged_in", "username", "role", "display_name"):
                st.session_state[k] = False if k == "logged_in" else ""
            st.rerun()

    tab_users, tab_tutor = st.tabs(["👥 Manage Users", "📚 Open Tutor"])

    # ── Users tab ─────────────────────────────────────────────────────────────
    with tab_users:

        # ── Add user form ──────────────────────────────────────────────────────
        st.subheader("➕ Add new user")
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            new_username = c1.text_input("Username *", placeholder="e.g. bobby")
            new_display = c2.text_input("Display name", placeholder="e.g. Bobby Vu")
            c3, c4, c5 = st.columns(3)
            new_pw = c3.text_input("Password *", type="password")
            new_confirm = c4.text_input("Confirm password *", type="password")
            new_role = c5.selectbox("Role", ["student", "admin"])
            add_btn = st.form_submit_button("Add user", use_container_width=True, type="primary")

        if add_btn:
            if not new_username.strip() or not new_pw:
                st.error("Username and password are required.")
            elif new_pw != new_confirm:
                st.error("Passwords do not match.")
            else:
                data = load_users()
                if find_user(new_username, data):
                    st.error(f"Username '{new_username.strip()}' already exists.")
                else:
                    data["users"].append({
                        "username": new_username.strip(),
                        "password": hash_pw(new_pw),
                        "role": new_role,
                        "display_name": new_display.strip() or new_username.strip(),
                    })
                    save_users(data)
                    st.success(f"✅ User '{new_username.strip()}' created.")
                    st.rerun()

        st.divider()

        # ── Existing users ─────────────────────────────────────────────────────
        st.subheader("👥 Existing users")
        data = load_users()
        for u in data["users"]:
            icon = "🔑" if u["role"] == "admin" else "👤"
            label = f"{icon} **{u.get('display_name', u['username'])}** ({u['username']}) — *{u['role']}*"
            with st.expander(label):
                with st.form(f"edit_{u['username']}", clear_on_submit=True):
                    ep1, ep2 = st.columns(2)
                    ep_new = ep1.text_input("New password", type="password",
                                            key=f"np_{u['username']}")
                    ep_conf = ep2.text_input("Confirm new password", type="password",
                                             key=f"nc_{u['username']}")
                    ep_display = st.text_input("Display name",
                                               value=u.get("display_name", ""),
                                               key=f"dn_{u['username']}")
                    btn_col1, btn_col2 = st.columns(2)
                    save_btn = btn_col1.form_submit_button("💾 Save changes",
                                                           use_container_width=True)
                    del_btn = btn_col2.form_submit_button("🗑 Delete user",
                                                          use_container_width=True,
                                                          type="secondary")

                if save_btn:
                    changed = False
                    data = load_users()
                    for uu in data["users"]:
                        if uu["username"] == u["username"]:
                            if ep_display.strip():
                                uu["display_name"] = ep_display.strip()
                                changed = True
                            if ep_new:
                                if ep_new != ep_conf:
                                    st.error("Passwords do not match.")
                                    break
                                uu["password"] = hash_pw(ep_new)
                                changed = True
                    if changed:
                        save_users(data)
                        st.success("Changes saved.")
                        st.rerun()
                    else:
                        st.info("Nothing to update — enter a new password or display name.")

                if del_btn:
                    if u["username"] == st.session_state.username:
                        st.error("You cannot delete your own account.")
                    else:
                        data = load_users()
                        data["users"] = [
                            uu for uu in data["users"]
                            if uu["username"] != u["username"]
                        ]
                        save_users(data)
                        st.success(f"User '{u['username']}' deleted.")
                        st.rerun()

        st.divider()

        # ── Download users.json ────────────────────────────────────────────────
        st.info(
            "**Streamlit Cloud note:** changes made here are saved to disk but reset "
            "when the Cloud app restarts.  To make accounts permanent, download the "
            "file below, replace `users.json` in your GitHub repo, and push."
        )
        st.download_button(
            label="⬇️ Download users.json",
            data=json.dumps(load_users(), indent=2),
            file_name="users.json",
            mime="application/json",
        )

    # ── Tutor tab (admin can also practise) ──────────────────────────────────
    with tab_tutor:
        _render_tutor(st.session_state.username, st.session_state.display_name)


# ── Student view ──────────────────────────────────────────────────────────────

def show_student():
    # Thin Streamlit bar: name on the left, logout button on the right.
    # Logout must live here (not in the iframe) because Streamlit Cloud's
    # sandbox blocks window.top navigation from inside components.html.
    st.markdown(
        """
        <style>
        .student-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4px 12px 4px 16px;
            background: var(--background-color, #ffffff);
            border-bottom: 1px solid rgba(0,0,0,0.08);
            min-height: 38px;
        }
        .student-bar-name {
            font-size: 13px;
            opacity: 0.65;
            white-space: nowrap;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    col_name, col_logout = st.columns([9, 1])
    with col_name:
        st.markdown(
            f'<p class="student-bar-name">👤 {st.session_state.display_name}</p>',
            unsafe_allow_html=True,
        )
    with col_logout:
        if st.button("⏻", key="student_logout", help="Log out",
                     use_container_width=True):
            for k in ("logged_in", "username", "role", "display_name"):
                st.session_state[k] = False if k == "logged_in" else ""
            st.rerun()

    _render_tutor(st.session_state.username, st.session_state.display_name)


def _render_tutor(username: str, display_name: str = ""):
    """Load index.html, inject username + display name, and render."""
    html_file = BASE / "index.html"
    if not html_file.exists():
        st.error("**index.html not found.** Make sure it is in the same folder as streamlit_app.py.")
        st.stop()

    # Inject user identity so the HTML uses per-user localStorage keys
    # and shows the correct name + logout button in its own header.
    safe_name = display_name.replace("'", "\\'")
    html_content = (
        html_file.read_text(encoding="utf-8")
        .replace("var CURRENT_USER  = 'default';", f"var CURRENT_USER  = '{username}';")
        .replace("var DISPLAY_NAME  = '';",         f"var DISPLAY_NAME  = '{safe_name}';")
    )

    # scrolling=False → single browser scrollbar.
    # height=10000 covers the tallest tab (Metalanguage on mobile).
    components.html(html_content, height=10000, scrolling=False)


# ── Router ─────────────────────────────────────────────────────────────────────

if not st.session_state.logged_in:
    show_login()
elif st.session_state.role == "admin":
    show_admin()
else:
    show_student()
