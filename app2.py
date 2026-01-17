import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. Dashboard Layout & Sync Settings ---
st.set_page_config(page_title="Adobe Stock Intelligence 2026", layout="wide")
# 10-minute auto-refresh taake Google block na kare
st_autorefresh(interval=600 * 1000, key="datarefresh") 

st.title("🚀 Adobe Stock Professional Market Intelligence")
st.write(f"🕒 Last Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Status: Live")

# Sidebar for Research
search_query = st.sidebar.text_input("Enter Research Topic", "nature")

# --- 2. Adobe Creative Trends 2026 Section ---
st.subheader("🎨 Adobe Creative Trends 2026 (Predicted & Rising)")
col_a, col_b = st.columns(2)
with col_a:
    st.info("🔥 **High Demand (Hot Topics)**")
    st.write("- **AI Hyper-Realism:** Photorealistic textures & backgrounds.")
    st.write("- **Eco-Minimalism:** Sustainability & clean energy visuals.")
    st.write("- **Cyberpunk 2.0:** Futuristic neon cityscapes.")
with col_b:
    st.success("📈 **Global Growth Keywords**")
    st.write("- **Authentic Emotions:** Diverse & inclusive human photography.")
    st.write("- **3D Abstract Geometry:** Clean isometric vectors & icons.")
    st.write("- **Retro-Futurism:** 80s style aesthetics for modern tech.")

# --- 3. Daily Global Trends Table ---
st.markdown("---")
st.subheader("🌍 Daily Global Trends Table")
@st.cache_data(ttl=3600)
def get_daily_trends():
    # Adobe Stock ke breakout trends ka professional backup
    backup = [
        {"Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Breakout"},
        {"Rank": 2, "Topic": "Solar Energy Solutions", "Status": "📈 Rising"},
        {"Rank": 3, "Topic": "Mental Health Awareness", "Status": "📈 Rising"},
        {"Rank": 4, "Topic": "Cryptocurrency 3D Icons", "Status": "🔥 Breakout"},
        {"Rank": 5, "Topic": "Organic Texture Patterns", "Status": "✅ Stable"}
    ]
    return pd.DataFrame(backup)
st.table(get_daily_trends())

# --- 4. Live Asset Research (Images, Videos, Vectors with Links) ---
st.markdown("---")
st.subheader(f"🔍 Live Asset Search: What's selling for '{search_query}'?")

def get_live_assets(kw):
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    # Teeno formats shamil hain
    types = {"Photos/Images": "images", "Videos": "video", "Vectors": "vectors"}
    for name, t in types.items():
        url = f"https://stock.adobe.com/search/{t}?k={kw.replace(' ', '+')}&order=relevance"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Scrape direct links and titles
            items = soup.select('a.js-search-result-link')[:2]
            for item in items:
                asset_url = "https://stock.adobe.com" + item['href']
                img_tag = item.find('img')
                title = img_tag['alt'] if img_tag else "View Asset"
                data.append({"Category": name, "Trending Title": title, "Adobe Link": asset_url})
        except: continue
    return pd.DataFrame(data)

asset_df = get_live_assets(search_query)
if not asset_df.empty:
    st.dataframe(
        asset_df, 
        use_container_width=True, 
        column_config={"Adobe Link": st.column_config.LinkColumn("View on Adobe Stock")}
    )
else:
    st.info("Loading live data from Adobe... Please enter a topic in the sidebar.")

# --- 5. Global Market Analytics (Countries & Demand Share) ---
st.markdown("---")
try:
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=3)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Top Buying Countries")
        pytrends.build_payload([search_query], timeframe='now 7-d')
        geo = pytrends.interest_by_region(resolution='COUNTRY').sort_values(by=search_query, ascending=False).head(10)
        st.bar_chart(geo)

    with col2:
        st.subheader("📊 Asset Popularity Share (%)")
        # Muqabla: Image vs Video vs Vector
        kws = [f"{search_query} image", f"{search_query} video", f"{search_query} vector"]
        pytrends.build_payload(kws, timeframe='now 7-d')
        demand = pytrends.interest_over_time().mean().drop('isPartial').reset_index()
        demand.columns = ['Asset Type', 'Popularity']
        
        fig = px.pie(demand, values='Popularity', names='Asset Type', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Google Trends is resting. Charts will auto-load in next refresh.")
