import streamlit as st
from auth.users import users, hash_password

def login_page():
    st.title("🔐 Login to Geo Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users:
            hashed_input = hash_password(password)

            if users[username]["password"] == hashed_input:
                st.session_state["authenticated"] = True
                st.session_state["user"] = username
                st.session_state["role"] = users[username]["role"]

                st.success("Login successful ✅")
                st.rerun()

        st.error("Invalid username or password ❌")
