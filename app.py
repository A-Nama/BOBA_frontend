import streamlit as st
import requests

# Backend API URL
API_BASE_URL = "https://backendboba.onrender.com"

# Session state initialization
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.page = "login"
    st.session_state.selected_user = None

# -------- LOGIN PAGE --------
def login_page():
    st.image("logo.png", width=150)
    st.markdown("""
        <style>
            .stButton>button {background-color: #4C2A1E; color: white; width: 100%; border-radius: 10px;}
            .stTextInput>div>div>input {border-radius: 10px;}
            .title {text-align: center; font-size: 32px; font-weight: bold;}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='title'>Welcome back!</h1>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.user = response.json()
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

# -------- SIGNUP PAGE --------
def signup_page():
    st.image("logo.png", width=150)
    st.markdown("<h1 class='title'>Create your profile</h1>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    bio = st.text_area("Bio")
    topics = st.text_input("Talk to me about (comma-separated)")
    
    if st.button("Sign Up"):
        response = requests.post(f"{API_BASE_URL}/signup", json={
            "username": username,
            "email": email,
            "password": password,
            "bio": bio,
            "topics": topics.split(",")
        })
        if response.status_code == 201:
            st.success("Account created! Please log in.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Signup failed. Try again.")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# -------- HOME PAGE --------
def home_page():
    st.image("logo.png", width=150)
    st.markdown("<h1 class='title'>Let's Chat!</h1>", unsafe_allow_html=True)
    st.write("Tap on a boba pearl to view profile & chat!")

    if not st.session_state.user:
        st.error("User not logged in. Redirecting to login...")
        st.session_state.page = "login"
        st.rerun()

    user_id = st.session_state.user.get('user_id')  # FIX: Use correct key
    if not user_id:
        st.error("User ID missing from session. Please log in again.")
        st.session_state.page = "login"
        st.rerun()

    # Fetch matches from backend
    response = requests.get(f"{API_BASE_URL}/matches/{user_id}")
    if response.status_code == 200:
        matches = response.json().get("matches", [])
    else:
        st.error("Failed to load matches.")
        matches = []

    cols = st.columns(5)
    for i, match in enumerate(matches):
        if cols[i % 5].button(match["username"]):
            st.session_state.selected_user = match
            st.session_state.page = "profile_view"
            st.rerun()

# -------- PROFILE VIEW PAGE --------
def profile_view_page():
    st.image("logo.png", width=150)

    user = st.session_state.selected_user
    if not user:
        st.error("No user selected. Returning to home page...")
        st.session_state.page = "home"
        st.rerun()

    st.markdown(f"""
        <h1 class='title'>@{user['username']}</h1>
        <p style='text-align: center;'>{user['bio']}</p>
    """, unsafe_allow_html=True)

    st.write("Talk to me about:")
    for topic in user["interests"].split(","):
        st.button(topic.strip())

    if st.button("Chat"):
        st.session_state.page = "chat"
        st.rerun()

# -------- CHAT PAGE --------
def chat_page():
    st.image("logo.png", width=150)

    user = st.session_state.selected_user
    if not user:
        st.error("No user selected. Returning to home page...")
        st.session_state.page = "home"
        st.rerun()

    st.markdown(f"<h1 class='title'>Chat with {user['username']}</h1>", unsafe_allow_html=True)

    sender_id = st.session_state.user.get("user_id")
    receiver_id = user.get("_id")

    if not sender_id or not receiver_id:
        st.error("Missing user ID. Please log in again.")
        st.session_state.page = "login"
        st.rerun()

    # Fetch chat messages
    response = requests.get(f"{API_BASE_URL}/chat/{sender_id}/{receiver_id}")
    if response.status_code == 200:
        messages = response.json()
    else:
        messages = []

    for msg in messages:
        st.write(f"{msg['sender']}: {msg['text']}")

    new_msg = st.text_input("Type here...")
    if st.button("Send"):
        requests.post(f"{API_BASE_URL}/chat/send", json={
            "sender": sender_id,
            "receiver": receiver_id,
            "text": new_msg
        })
        st.rerun()

# -------- MAIN FUNCTION --------
def main():
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
    elif st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "profile_view":
        profile_view_page()
    elif st.session_state.page == "chat":
        chat_page()

if __name__ == "__main__":
    main()
