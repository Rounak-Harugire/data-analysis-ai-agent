import streamlit as st
import hashlib

# -----------------------
# Simple SHA256 Hashing
# -----------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Demo Credentials
DEMO_USERNAME = "admin"
DEMO_PASSWORD_HASH = hash_password("1234")


def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.sidebar.title("Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if (
            username == DEMO_USERNAME
            and hash_password(password) == DEMO_PASSWORD_HASH
        ):
            st.session_state.authenticated = True
            st.sidebar.success("Login successful")
            return True
        else:
            st.sidebar.error("Invalid credentials")

    return False