import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG & THEME ---
st.set_page_config(layout="wide", page_title="Style Finder Prototype")

# --- CUSTOM CSS & LOGOS ---
html_and_css = """
<style>
/* Responsive Logo Container - Sizes reduced by 50% */
.logo-container {
    display: flex; flex-wrap: wrap; justify-content: space-between; 
    align-items: center; margin-bottom: 3rem;
}
.logo-container img { max-width: 9%; height: auto; min-width: 50px; margin-bottom: 10px; }
@media (max-width: 768px) { .logo-container img { max-width: 22.5%; } }

/* Responsive Grid for Thumbnails */
@media (min-width: 768px) and (max-width: 1024px) {
    div[data-testid="column"] { width: 33.33% !important; flex: 1 1 33.33% !important; min-width: 33.33% !important; }
}
@media (max-width: 767px) {
    div[data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
}
</style>

<div class='logo-container'>
    <img src='https://lh3.googleusercontent.com/d/1Qi7BHej4ZiXosgkoQm18gC1owuEi_XeY'>
    <img src='https://lh3.googleusercontent.com/d/1_x5phTRaEIfeCwXPOdvjkFpAeKZU6Z6W'>
    <img src='https://lh3.googleusercontent.com/d/1-a5DsndN4xa1NW9cQqFg2VgNdCBxv6gx'>
    <img src='https://lh3.googleusercontent.com/d/1ROutq2AGNtyHSPg80VRYykZL92MamPdM'>
    <img src='https://lh3.googleusercontent.com/d/1W0c_Mze5syN3bvAOCKUcz2uc7gMxMnz7'>
</div>
"""

# --- LOGIN LOGIC ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        # Checks inputs against Streamlit Secrets
        if (st.session_state["username"] == st.secrets["username"] and 
            st.session_state["password"] == st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Wipe password from memory
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.subheader("Login to Style Finder")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("Incorrect username or password.")
        return False
    return True

# --- MAIN APP ---
def main_app():
    st.markdown(html_and_css, unsafe_allow_html=True)

    # Loads CSV from the local GitHub repository folder
    @st.cache_data
    def load_data():
        csv_file = 'style_finder_data.csv'
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, dtype=str)
            if 'Style_Number' in df.columns:
                df['Style_Number'] = df['Style_Number'].astype(str)
            return df
        else:
            st.error(f"Cannot find CSV at: {csv_file}")
            return pd.DataFrame()

    df = load_data()

    if 'search_results' not in st.session_state:
        st.session_state.search_results = pd.DataFrame()

    def clear_sku():
        st.session_state.sku_key = ""
        st.session_state.search_results = pd.DataFrame()

    def clear_keyword():
        st.session_state.key_key = ""
        st.session_state.search_results = pd.DataFrame()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Search by Style SKU")
        sku_input = st.text_input("Enter SKU (e.g. 1234):", key="sku_key")
        c1, c2 = st.columns([1, 1])
        sku_submit = c1.button("Submit", key="sub_sku", use_container_width=True)
        c2.button("Clear", key="clr_sku", use_container_width=True, on_click=clear_sku)

    with col2:
        st.subheader("Search by Product Keyword")
        key_input = st.text_input("Enter Keyword (e.g. Traffic):", key="key_key")
        c3, c4 = st.columns([1, 1])
        key_submit = c3.button("Submit", key="sub_key", use_container_width=True)
        c4.button("Clear", key="clr_key", use_container_width=True, on_click=clear_keyword)

    if not df.empty:
        if sku_submit and sku_input:
            st.session_state.search_results = df[df['Style_Number'].str.contains(sku_input, case=False, na=False)]
        elif key_submit and key_input:
            st.session_state.search_results = df[df['Product_Name'].str.contains(key_input, case=False, na=False)]

    results = st.session_state.search_results

    if not results.empty:
        st.markdown(f"**Found {len(results)} matches**")
        st.divider()
        
        cols = st.columns(4)
        for index, row in results.reset_index(drop=True).iterrows():
            col = cols[index % 4]
            with col:
                img_id = row.get('Google_Image_ID', '') 
                product_name = row.get('Product_Name', 'Unknown Product')
                style_number = row.get('Style_Number', 'Unknown Style')
                
                if pd.notna(img_id) and img_id:
                    # Dynamically constructs the Google Drive view link using the reliable lh3 structure
                    drive_url = f"https://lh3.googleusercontent.com/d/{img_id}"
                    st.image(drive_url, use_container_width=True)
                    st.markdown(f"**{product_name}**<br>{style_number}", unsafe_allow_html=True)
                else:
                    st.warning("No Google Image ID in CSV.")
    else:
        if (sku_submit and sku_input) or (key_submit and key_input):
            st.info("No matching styles found.")

# The script runs the login check first; if True, it fires the main app
if check_password():
    main_app()
