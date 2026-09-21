import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

st.set_page_config(page_title="Spotify Playlist Creator", page_icon="🎵")
st.title("🎵 Spotify Playlist Creator")

CLIENT_ID = st.secrets['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = st.secrets['SPOTIFY_SECRET']
REDIRECT_URI = st.secrets["REDIRECT_URI"]
SCOPE = "playlist-modify-public playlist-modify-private"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    show_dialog=True
)

url_params = st.query_params

if "code" in url_params and "token_info" not in st.session_state:
    code = url_params["code"]
    try:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        st.session_state["token_info"] = token_info
        st.query_params.clear()
    except Exception as e:
        st.error(f"Authentication failed: {e}")

if "token_info" not in st.session_state:
    st.info("Please log in to your Spotify account to create a playlist.")
    auth_url = sp_oauth.get_authorize_url()
    st.link_button("Log In with Spotify", auth_url, type="primary")

else:
    token_info = st.session_state["token_info"]
    
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        st.session_state["token_info"] = token_info

    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    try:
        user_info = sp.current_user()
        st.success(f"Logged in as: **{user_info['display_name']}**")
    except Exception as e:
        st.error("Session expired or invalid. Please log out and try again.")
        if st.button("Clear Session"):
            del st.session_state["token_info"]
            st.rerun()
        st.stop()

    st.divider()
    st.subheader("Create a New Playlist")

    with st.form("playlist_form"):
        playlist_name = st.text_input("Playlist Name", placeholder="My Awesome Streamlit Playlist")
        playlist_desc = st.text_area("Description (Optional)", placeholder="Created using Streamlit and Spotipy!")
        is_public = st.toggle("Make Playlist Public", value=False)
        
        submit_button = st.form_submit_button("Create Playlist")

    if submit_button:
        if not playlist_name.strip():
            st.warning("Please enter a playlist name.")
        else:
            with st.spinner("Creating your playlist..."):
                try:
                    new_playlist = sp.user_playlist_create(
                        user=user_info["id"],
                        name=playlist_name,
                        public=is_public,
                        description=playlist_desc
                    )
                    
                    st.balloons()
                    st.success(f"🎉 Playlist **'{playlist_name}'** successfully created!")
                    st.markdown(f"[🔗 Open your new playlist on Spotify]({new_playlist['external_urls']['spotify']})")
                    
                except Exception as e:
                    st.error(f"Failed to create playlist: {e}")

    st.divider()
    if st.button("Log Out"):
        del st.session_state["token_info"]
        st.rerun()
