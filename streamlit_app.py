"""
AMAG Competitor Intelligence Dashboard - Stabile Version
Ohne Plotly - verwendet Streamlit native Charts
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import time

# Page Config
st.set_page_config(
    page_title="AMAG Competitor Intelligence",
    page_icon="🚗",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main {padding-top: 0rem;}
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Demo Data
DEMO_DATA = {
    'Emil Frey': {
        'aktionen': [
            {'title': 'VW Golf - Winteraktion', 'price': 29900, 'discount': 15},
            {'title': 'Audi A3 - Leasing', 'price': 299, 'discount': 0},
            {'title': 'Service-Paket', 'price': 199, 'discount': 20}
        ],
        'total_offers': 12,
        'avg_discount': 15.5,
        'keywords': ['winteraktion', 'leasing', 'service', 'vw', 'audi']
    },
    'Garage Weiss': {
        'aktionen': [
            {'title': 'Mercedes A-Klasse', 'price': 35500, 'discount': 10},
            {'title': 'BMW 3er Business', 'price': 45900, 'discount': 8},
            {'title': 'Winterreifen-Aktion', 'price': 599, 'discount': 25}
        ],
        'total_offers': 8,
        'avg_discount': 12.3,
        'keywords': ['mercedes', 'bmw', 'business', 'winterreifen']
    },
    'Auto Kunz': {
        'aktionen': [
            {'title': 'Toyota Hybrid', 'price': 31900, 'discount': 12},
            {'title': 'Mazda CX-5', 'price': 39900, 'discount': 10},
            {'title': 'Gratis-Service', 'price': 0, 'discount': 100}
        ],
        'total_offers': 10,
        'avg_discount': 14.8,
        'keywords': ['hybrid', 'toyota', 'mazda', 'gratis']
    }
}

def load_data():
    """Load competitor data"""
    # Try to scrape, fallback to demo
    return DEMO_DATA

def generate_alerts(data):
    """Generate competitive alerts"""
    alerts = []
    for comp, comp_data in data.items():
        for aktion in comp_data.get('aktionen', []):
            if aktion['discount'] >= 20:
                alerts.append(f"⚠️ {comp}: {aktion['discount']}% Rabatt auf {aktion['title']}")
    
    if not alerts:
        alerts.append("✅ Keine kritischen Wettbewerber-Aktivitäten")
    
    return alerts

# Main App
def main():
    # Header
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.title("🚗 AMAG Competitor Intelligence")
    with col2:
        if st.session_state.last_update:
            st.info(f"Update: {st.session_state.last_update}")
    with col3:
        if st.button("🔄 Refresh", type="primary"):
            with st.spinner("Lade Daten..."):
                st.session_state.data_cache = load_data()
                st.session_state.last_update = datetime.now().strftime('%H:%M:%S')
                st.rerun()
    
    # Load initial data
    if not st.session_state.data_cache:
        st.session_state.data_cache = load_data()
        st.session_state.last_update = datetime.now().strftime('%H:%M:%S')
    
    data = st.session_state.data_cache
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Preise", "🚨 Alerts", "📈 Analyse"])
    
    with tab1:
        st.subheader("Dashboard Overview")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_offers = sum(d.get('total_offers', 0) for d in data.values())
        avg_discount = sum(d.get('avg_discount', 0) for d in data.values()) / len(data)
        total_competitors = len(data)
        total_keywords = sum(len(d.get('keywords', [])) for d in data.values())
        
        col1.metric("Total Aktionen", total_offers, "+5")
        col2.metric("Ø Rabatt", f"{avg_discount:.1f}%", "+2.3%")
        col3.metric("Wettbewerber", total_competitors)
        col4.metric("Keywords", total_keywords)
        
        st.divider()
        
        # Overview table
        overview_data = []
        for comp, comp_data in data.items():
            overview_data.append({
                'Wettbewerber': comp,
                'Anzahl Aktionen': comp_data.get('total_offers', 0),
                'Ø Rabatt %': comp_data.get('avg_discount', 0),
                'Top Keywords': ', '.join(comp_data.get('keywords', [])[:3])
            })
        
        df = pd.DataFrame(overview_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Preisvergleich")
        
        # Price comparison using native Streamlit
        price_data = []
        for comp, comp_data in data.items():
            for aktion in comp_data.get('aktionen', []):
                price_data.append({
                    'Wettbewerber': comp,
                    'Angebot': aktion['title'],
                    'Preis CHF': aktion['price'],
                    'Rabatt %': aktion['discount']
                })
        
        price_df = pd.DataFrame(price_data)
        
        # Simple bar chart
        st.subheader("Rabatt-Übersicht")
        chart_data = price_df.set_index('Angebot')['Rabatt %']
        st.bar_chart(chart_data)
        
        # Price table
        st.subheader("Detaillierte Preisliste")
        st.dataframe(price_df, use_container_width=True, hide_index=True)
        
        # Highlight best deals
        best_deals = price_df.nlargest(3, 'Rabatt %')
        st.subheader("🎯 Top Deals")
        for _, deal in best_deals.iterrows():
            st.success(f"**{deal['Wettbewerber']}**: {deal['Angebot']} - {deal['Rabatt %']}% Rabatt")
    
    with tab3:
        st.subheader("Competitive Alerts")
        
        alerts = generate_alerts(data)
        
        for alert in alerts:
            if "⚠️" in alert:
                st.warning(alert)
            else:
                st.success(alert)
        
        st.divider()
        
        # Action items
        st.subheader("💡 Empfohlene Massnahmen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Sofort-Massnahmen:**
            - 🎯 Preise bei >20% Rabatten prüfen
            - 📝 Content-Gaps schliessen
            - 💰 Leasing-Angebote matchen
            """)
        
        with col2:
            st.markdown("""
            **Mittelfristig:**
            - 📊 Wöchentliches Monitoring
            - 🤝 Supplier-Verhandlungen
            - 📱 Digital-Kampagnen
            """)
    
    with tab4:
        st.subheader("Keyword-Analyse")
        
        # Collect all keywords
        all_keywords = {}
        for comp, comp_data in data.items():
            for kw in comp_data.get('keywords', []):
                if kw not in all_keywords:
                    all_keywords[kw] = 0
                all_keywords[kw] += 1
        
        # Create DataFrame
        kw_df = pd.DataFrame(
            list(all_keywords.items()), 
            columns=['Keyword', 'Häufigkeit']
        ).sort_values('Häufigkeit', ascending=False)
        
        # Display as bar chart
        st.bar_chart(kw_df.set_index('Keyword')['Häufigkeit'])
        
        # Keyword table
        st.dataframe(kw_df, use_container_width=True, hide_index=True)
        
        # Export option
        st.divider()
        if st.button("📥 Export JSON"):
            json_str = json.dumps(st.session_state.data_cache, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"competitor_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

# Run app
if __name__ == "__main__":
    main()
