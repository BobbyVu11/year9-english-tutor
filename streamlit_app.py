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
    st.session_state.flash = ""   # one-shot success/info message


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

def _logout():
    """Clear session — called via st.button() so no page navigation needed."""
    for k in ("logged_in", "username", "role", "display_name"):
        st.session_state[k] = False if k == "logged_in" else ""


def _show_bar(icon: str, name: str, btn_key: str) -> bool:
    """
    Renders the identity bar as a true single row: '👤 Bobby Vu  ⏻'
    Uses st.columns() so the Streamlit button is inline with the name.
    The .sbar-row marker class lets CSS target only this row's button.
    """
    st.markdown(
        """
        <style>
        /* Make both columns shrink to content width so button sits next to name */
        div[data-testid="stHorizontalBlock"]:has(.sbar-row) {
            align-items: center !important;
            border-bottom: 1px solid rgba(0,0,0,0.08);
            padding: 3px 14px !important;
            gap: 4px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.sbar-row)
            > div[data-testid="stColumn"] {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
        }
        /* Name text */
        div[data-testid="stHorizontalBlock"]:has(.sbar-row) p {
            font-size: 13px !important;
            opacity: 0.65;
            margin: 0 !important;
            white-space: nowrap;
            line-height: 30px;
        }
        /* Strip button box — bare red icon, properly centred */
        div[data-testid="stHorizontalBlock"]:has(.sbar-row) button {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            color: #c0392b !important;
            font-size: 16px !important;
            height: 28px !important;
            width: 28px !important;
            min-height: unset !important;
            padding: 0 !important;
            border-radius: 50% !important;
            opacity: 0.7;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: opacity 0.15s, background 0.15s !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.sbar-row) button:hover {
            background: rgba(192,57,43,0.1) !important;
            opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    col_name, col_btn = st.columns([1, 1])
    col_name.markdown(f'<span class="sbar-row">{icon} {name}</span>', unsafe_allow_html=True)
    return col_btn.button("⏻", key=btn_key, help="Log out")


def show_admin():
    if _show_bar("⚙️", st.session_state.display_name, "admin_logout"):
        _logout()
        st.rerun()

    # Show one-shot flash message (set before st.rerun() so it survives)
    if st.session_state.get("flash"):
        st.success(st.session_state.flash)
        st.session_state.flash = ""

    tab_users, tab_progress, tab_tutor = st.tabs(["👥 Manage Users", "📊 Student Progress", "📚 Open Tutor"])

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
                    st.session_state.flash = f"✅ User '{new_username.strip()}' created successfully."
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
                        st.session_state.flash = f"✅ Changes saved for '{u['username']}'."
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
                        st.session_state.flash = f"🗑 User '{u['username']}' deleted."
                        st.rerun()

                # ── Teacher note (students only) ──────────────────────────
                if u["role"] == "student":
                    st.markdown("**📝 Teacher feedback note**")
                    st.caption("This message will appear as a banner when the student next logs in.")
                    with st.form(f"note_{u['username']}", clear_on_submit=False):
                        current_note = u.get("note", "")
                        new_note = st.text_area("Note for student", value=current_note,
                                                placeholder="e.g. Great work on reading this week! Focus on metalanguage next.",
                                                key=f"note_ta_{u['username']}", height=80)
                        nc1, nc2 = st.columns(2)
                        save_note_btn = nc1.form_submit_button("💾 Save note", use_container_width=True)
                        clear_note_btn = nc2.form_submit_button("🗑 Clear note", use_container_width=True)

                    if save_note_btn:
                        data = load_users()
                        for uu in data["users"]:
                            if uu["username"] == u["username"]:
                                uu["note"] = new_note.strip()
                        save_users(data)
                        st.session_state.flash = f"📝 Note saved for '{u['username']}'."
                        st.rerun()

                    if clear_note_btn:
                        data = load_users()
                        for uu in data["users"]:
                            if uu["username"] == u["username"]:
                                uu["note"] = ""
                        save_users(data)
                        st.session_state.flash = f"🗑 Note cleared for '{u['username']}'."
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

    # ── Student Progress tab ──────────────────────────────────────────────────
    with tab_progress:
        data = load_users()
        students = [u for u in data["users"] if u["role"] == "student"]
        if not students:
            st.info("No student accounts yet.")
        else:
            # Build a JSON list of student usernames to inject into the component
            students_json = json.dumps([
                {"username": u["username"], "display_name": u.get("display_name", u["username"])}
                for u in students
            ])
            progress_html = f"""
<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
          font-size: 14px; color: #1a1a1a; background: #f5f5f0; margin: 0; padding: 12px; }}
  h3 {{ margin: 0 0 4px; font-size: 15px; color: #1f4e79; }}
  .student-block {{ background: #fff; border-radius: 10px; border: 1px solid #ddd;
                    padding: 14px; margin-bottom: 14px; }}
  .student-name {{ font-weight: 700; font-size: 15px; margin-bottom: 10px; color: #1f4e79; }}
  .grade-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }}
  .grade-chip {{ padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
  .chip-A {{ background:#d5f5e3; color:#196f3d; }}
  .chip-B {{ background:#d6e4f0; color:#1f4e79; }}
  .chip-C {{ background:#fef9e7; color:#7d6608; }}
  .chip-D {{ background:#fadbd8; color:#922b21; }}
  .chip-E {{ background:#f4ecf7; color:#6c3483; }}
  .no-data {{ color: #888; font-size: 13px; font-style: italic; }}
  canvas {{ max-height: 160px; }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; margin-top:8px; }}
  th {{ background:#f0f4ff; padding:5px 8px; text-align:left; color:#2d3a8c; }}
  td {{ padding:5px 8px; border-bottom:1px solid #eee; }}
</style>
</head><body>
<script>
var STUDENTS = {students_json};
var TYPE_COLORS = {{
  "Writing":"#4a6cf7","Reading":"#10b981",
  "Metalanguage":"#8b5cf6","Vocabulary":"#f59e0b"
}};
var LEVEL_NUM = {{"A":5,"B":4,"C":3,"D":2,"E":1}};

function loadData(username) {{
  try {{ return JSON.parse(localStorage.getItem("y9levels_" + username) || "[]"); }}
  catch(e) {{ return []; }}
}}

function latestByType(records) {{
  var latest = {{}};
  records.forEach(function(r) {{
    if (!latest[r.type] || r.ts > latest[r.type].ts) latest[r.type] = r;
  }});
  return latest;
}}

function renderStudent(s) {{
  var records = loadData(s.username);
  var div = document.createElement("div");
  div.className = "student-block";

  var nameDiv = document.createElement("div");
  nameDiv.className = "student-name";
  nameDiv.textContent = "👤 " + s.display_name + " (" + s.username + ")";
  div.appendChild(nameDiv);

  if (records.length === 0) {{
    var nd = document.createElement("div");
    nd.className = "no-data";
    nd.textContent = "No practice sessions recorded yet.";
    div.appendChild(nd);
    return div;
  }}

  // Latest grade chips
  var latest = latestByType(records);
  var row = document.createElement("div");
  row.className = "grade-row";
  ["Writing","Reading","Vocabulary","Metalanguage"].forEach(function(t) {{
    if (latest[t]) {{
      var chip = document.createElement("span");
      chip.className = "grade-chip chip-" + latest[t].level;
      chip.textContent = t + ": " + latest[t].level + " (" + latest[t].pct + "%)";
      row.appendChild(chip);
    }}
  }});
  div.appendChild(row);

  // Mini chart — last 12 sessions across all types
  var recent = records.slice(-12);
  var canvasWrap = document.createElement("div");
  var canvas = document.createElement("canvas");
  canvas.id = "chart_" + s.username;
  canvasWrap.appendChild(canvas);
  div.appendChild(canvasWrap);
  setTimeout(function() {{
    new Chart(canvas, {{
      type: "bar",
      data: {{
        labels: recent.map(function(r) {{ return r.date + " " + r.type.slice(0,1); }}),
        datasets: [{{
          data: recent.map(function(r) {{ return LEVEL_NUM[r.level]; }}),
          backgroundColor: recent.map(function(r) {{ return TYPE_COLORS[r.type] + "cc"; }}),
          borderRadius: 4
        }}]
      }},
      options: {{
        plugins: {{ legend: {{ display: false }}, tooltip: {{
          callbacks: {{ label: function(c) {{
            var r = recent[c.dataIndex];
            return r.type + ": " + r.level + " (" + r.pct + "%) — " + r.score + "/" + r.total;
          }}}}
        }}}},
        scales: {{
          y: {{ min:0, max:5, ticks: {{ stepSize:1,
            callback: function(v) {{ return ["","E","D","C","B","A"][v] || ""; }} }} }},
          x: {{ ticks: {{ font: {{ size: 10 }} }} }}
        }}
      }}
    }});
  }}, 50);

  // Session history table
  var h3 = document.createElement("h3");
  h3.textContent = "Session history (" + records.length + " total)";
  h3.style.marginTop = "12px";
  div.appendChild(h3);
  var table = document.createElement("table");
  table.innerHTML = "<tr><th>Date</th><th>Skill</th><th>Score</th><th>Grade</th></tr>";
  records.slice().reverse().slice(0, 20).forEach(function(r) {{
    var tr = document.createElement("tr");
    tr.innerHTML = "<td>" + r.date + "</td><td>" + r.type + "</td>" +
                   "<td>" + r.score + "/" + r.total + " (" + r.pct + "%)</td>" +
                   "<td><span class='grade-chip chip-" + r.level + "'>" + r.level + "</span></td>";
    table.appendChild(tr);
  }});
  div.appendChild(table);

  return div;
}}

window.addEventListener("load", function() {{
  var container = document.getElementById("container");
  if (STUDENTS.length === 0) {{
    container.innerHTML = "<p style='color:#888'>No student accounts.</p>";
    return;
  }}
  STUDENTS.forEach(function(s) {{
    container.appendChild(renderStudent(s));
  }});
}});
</script>
<div id="container"></div>
</body></html>
"""
            components.html(progress_html, height=600, scrolling=True)

    # ── Tutor tab (admin can also practise) ──────────────────────────────────
    with tab_tutor:
        _render_tutor(st.session_state.username, st.session_state.display_name)


# ── Student view ──────────────────────────────────────────────────────────────

def show_student():
    if _show_bar("👤", st.session_state.display_name, "student_logout"):
        _logout()
        st.rerun()

    _render_tutor(st.session_state.username, st.session_state.display_name)


def _render_tutor(username: str, display_name: str = ""):
    """Load index.html, inject username, display name, and teacher note, then render."""
    html_file = BASE / "index.html"
    if not html_file.exists():
        st.error("**index.html not found.** Make sure it is in the same folder as streamlit_app.py.")
        st.stop()

    # Load teacher note for this user from users.json
    data = load_users()
    user_rec = find_user(username, data) or {}
    note = user_rec.get("note", "").replace("'", "\\'").replace("\n", " ")

    safe_name = display_name.replace("'", "\\'")
    html_content = (
        html_file.read_text(encoding="utf-8")
        .replace("var CURRENT_USER  = 'default';", f"var CURRENT_USER  = '{username}';")
        .replace("var DISPLAY_NAME  = '';",         f"var DISPLAY_NAME  = '{safe_name}';")
        .replace("var TEACHER_NOTE  = '';",         f"var TEACHER_NOTE  = '{note}';")
    )

    components.html(html_content, height=10000, scrolling=False)


# ── Router ─────────────────────────────────────────────────────────────────────

if not st.session_state.logged_in:
    show_login()
elif st.session_state.role == "admin":
    show_admin()
else:
    show_student()
