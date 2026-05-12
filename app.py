import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import datetime
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import re

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockSense",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

    /* Font application */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes gradientPulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Dark gradient background with fade-in */
    .stApp {
        background: linear-gradient(135deg, #090913 0%, #0a0f1e 50%, #050914 100%);
        animation: fadeIn 0.8s ease-out;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: rgba(14, 17, 23, 0.85) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(30, 58, 95, 0.4);
    }
    section[data-testid="stSidebar"] * {
        color: #e0e8ff !important;
    }

    /* Custom Streamlit Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a5f, #2a4b7c);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
        background: linear-gradient(90deg, #2a4b7c, #3b63a3);
        border: 1px solid rgba(0, 212, 170, 0.5);
    }

    /* Hide default Streamlit header */
    header[data-testid="stHeader"] { background: transparent; }

    /* KPI card container */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.7) 0%, rgba(26, 34, 53, 0.7) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(30, 58, 95, 0.5);
        border-left: 4px solid #00d4aa;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 212, 170, 0.15);
        border-left: 5px solid #00d4aa;
    }
    div[data-testid="metric-container"] label {
        color: #8bb4e6 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #8bb4e6;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(30, 58, 95, 0.5);
        position: relative;
    }
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 2px;
        background: #00d4aa;
    }

    /* Company info card */
    .info-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.7) 0%, rgba(26, 34, 53, 0.7) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(30, 58, 95, 0.5);
        border-radius: 16px;
        padding: 24px;
        margin-top: 12px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid rgba(26, 37, 53, 0.8);
        font-size: 0.9rem;
        transition: background 0.2s ease;
    }
    .info-row:hover {
        background: rgba(255,255,255,0.02);
        padding-left: 8px;
        padding-right: 8px;
        border-radius: 4px;
    }
    .info-row:last-child { border-bottom: none; }
    .info-label { color: #8bb4e6; font-weight: 600; }
    .info-value { color: #f0f4ff; font-weight: 500; }

    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(10,22,40,0.85) 0%, rgba(13,31,60,0.85) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(30, 58, 95, 0.5);
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 32px;
        display: flex;
        align-items: center;
        gap: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, #00d4aa, transparent);
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(270deg, #60a5fa, #818cf8, #00d4aa, #60a5fa);
        background-size: 300% 300%;
        animation: gradientPulse 6s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #8bb4e6;
        margin-top: 8px;
        font-weight: 500;
    }

    /* Positive/Negative delta colors */
    [data-testid="stMetricDelta"] svg { display: none; }
    .positive { color: #22c55e !important; }
    .negative { color: #ef4444 !important; }

    /* Plotly chart background */
    .js-plotly-plot { 
        border-radius: 16px; 
        overflow: hidden; 
        border: 1px solid rgba(30, 58, 95, 0.3);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    /* Sidebar title */
    .sidebar-logo {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(270deg, #60a5fa, #818cf8, #00d4aa);
        background-size: 200% 200%;
        animation: gradientPulse 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 24px;
        text-align: center;
        letter-spacing: 0.5px;
    }
    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(30, 58, 95, 0.5);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📈 StockSense</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    symbol = st.text_input(
        "🔍 Ticker Symbol",
        value="AAPL",
        placeholder="e.g. TSLA, MSFT, GOOG",
        help="Enter a valid stock ticker symbol",
    ).upper().strip()

    with st.expander("📋 My Watchlist", expanded=True):
        col_wl_input, col_wl_btn = st.columns([3, 1])
        with col_wl_input:
            wl_input = st.text_input("Add", placeholder="e.g. NVDA", label_visibility="collapsed", key="wl_input_field").upper().strip()
        with col_wl_btn:
            if st.button("➕", key="wl_add_btn", use_container_width=True):
                if wl_input and wl_input not in st.session_state.watchlist:
                    st.session_state.watchlist = st.session_state.watchlist + [wl_input]
                    st.toast(f"✅ Added {wl_input} to Watchlist!", icon="✨")
                    st.rerun()

        st.markdown("<hr style='margin: 8px 0; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        if not st.session_state.watchlist:
            st.caption("No symbols added yet.")
        else:
            for wl_sym in st.session_state.watchlist:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{wl_sym}**")
                    try:
                        _p = yf.Ticker(wl_sym).history(period="1d")['Close'].iloc[-1]
                        st.caption(f"${_p:.2f}")
                    except:
                        st.caption("N/A")
                with col_b:
                    if st.button("❌", key=f"rm_{wl_sym}"):
                        st.session_state.watchlist = [x for x in st.session_state.watchlist if x != wl_sym]
                        st.rerun()

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    period = st.selectbox(
        "📅 Time Period",
        options=["1d", "5d", "1mo", "3mo", "1y", "5y"],
        index=2,
        format_func=lambda x: {
            "1d": "1 Day",
            "5d": "5 Days",
            "1mo": "1 Month",
            "3mo": "3 Months",
            "1y": "1 Year",
            "5y": "5 Years",
        }[x],
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.caption("Data powered by Yahoo Finance · Free tier")
    st.caption("Refresh page to update quotes")

# ─── Helper: format large numbers ───────────────────────────────────────────
def fmt_num(n):
    if n is None:
        return "N/A"
    try:
        n = float(n)
        if n >= 1e12:
            return f"${n/1e12:.2f}T"
        elif n >= 1e9:
            return f"${n/1e9:.2f}B"
        elif n >= 1e6:
            return f"${n/1e6:.2f}M"
        else:
            return f"{n:,.0f}"
    except Exception:
        return str(n)

def fmt_price(n):
    try:
        return f"${float(n):,.2f}"
    except Exception:
        return "N/A"

# ─── Main Content ────────────────────────────────────────────────────────────

# ─── Data Fetching ───────────────────────────────────────────────────────────
with st.spinner("Fetching data..."):
    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info
        hist   = ticker.history(period=period)
    except Exception as e:
        st.error(f"❌ Failed to fetch data for **{symbol}**: {e}")
        st.stop()

if hist.empty:
    st.error(f"❌ No data found for ticker **{symbol}**. Please check the symbol and try again.")
    st.stop()

# ─── Profile Card / Hero Banner ──────────────────────────────────────────────
company_name = info.get("longName", symbol)
sector = info.get("sector", "Unknown Sector")
industry = info.get("industry", "Unknown Industry")
website = info.get("website", "")

logo_url = ""
if website:
    try:
        req = urllib.request.Request(website, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
        
        match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if match:
            logo_url = match.group(1)
            
        if not logo_url:
            match = re.search(r'<link[^>]*rel=["\'](?:shortcut icon|icon|apple-touch-icon)["\'][^>]*href=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if match:
                icon_url = match.group(1)
                if icon_url.startswith('//'):
                    logo_url = f"https:{icon_url}"
                elif icon_url.startswith('/'):
                    parsed = urllib.parse.urlparse(website)
                    logo_url = f"{parsed.scheme}://{parsed.netloc}{icon_url}"
                elif not icon_url.startswith('http'):
                    logo_url = f"{website.rstrip('/')}/{icon_url}"
                else:
                    logo_url = icon_url
    except Exception:
        pass
    
    if not logo_url:
        domain = urllib.parse.urlparse(website).netloc
        logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

logo_html = f'''<img src="{logo_url}" width="72" height="72" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); object-fit: cover; background: white; padding: 4px;" onerror="this.style.display='none';">''' if logo_url else ""

st.markdown(f"""
<div class="hero-banner" style="display: flex; align-items: center; gap: 24px;">
    {logo_html}
    <div>
        <div class="hero-title" style="font-size: 2.2rem;">{company_name}</div>
        <div class="hero-subtitle">{symbol} · {sector} — {industry}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Derive KPI values ───────────────────────────────────────────────────────
current_price = info.get("currentPrice") or info.get("regularMarketPrice") or (hist["Close"].iloc[-1] if not hist.empty else None)
open_price    = info.get("open") or info.get("regularMarketOpen") or (hist["Open"].iloc[-1] if not hist.empty else None)
day_high      = info.get("dayHigh") or info.get("regularMarketDayHigh") or (hist["High"].iloc[-1] if not hist.empty else None)
day_low       = info.get("dayLow") or info.get("regularMarketDayLow") or (hist["Low"].iloc[-1] if not hist.empty else None)
volume        = info.get("volume") or info.get("regularMarketVolume") or (int(hist["Volume"].iloc[-1]) if not hist.empty else None)

price_change  = None
price_pct     = None
if current_price and open_price:
    try:
        price_change = float(current_price) - float(open_price)
        price_pct    = (price_change / float(open_price)) * 100
    except Exception:
        pass

delta_color = "normal"
delta_str   = None
if price_change is not None:
    sign      = "▲" if price_change >= 0 else "▼"
    delta_str = f"{sign} {abs(price_change):.2f} ({abs(price_pct):.2f}%)"

# ─── KPI Cards ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Market Overview</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Current Price",
        value=fmt_price(current_price),
        delta=delta_str,
        delta_color="normal" if (price_change is None or price_change >= 0) else "inverse",
    )
with col2:
    st.metric(label="📈 Day High",  value=fmt_price(day_high))
with col3:
    st.metric(label="📉 Day Low",   value=fmt_price(day_low))
with col4:
    vol_display = f"{int(volume):,}" if volume else "N/A"
    st.metric(label="🔊 Volume",    value=vol_display)

# ─── Candlestick + Volume Chart ──────────────────────────────────────────────
st.markdown('<div class="section-header">Price Chart</div>', unsafe_allow_html=True)

company_name = info.get("longName", symbol)

# Compute moving averages (only meaningful if enough rows exist)
ma20 = hist["Close"].rolling(window=20).mean()
ma50 = hist["Close"].rolling(window=50).mean()

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.7, 0.3],
)

# ── Row 1: Candlestick ────────────────────────────────────────────────────────
fig.add_trace(
    go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
        name="Price",
        increasing=dict(line=dict(color="#22c55e"), fillcolor="#22c55e"),
        decreasing=dict(line=dict(color="#ef4444"), fillcolor="#ef4444"),
        whiskerwidth=0.6,
    ),
    row=1, col=1,
)

# ── Row 1: 20-day MA overlay ──────────────────────────────────────────────────
fig.add_trace(
    go.Scatter(
        x=hist.index,
        y=ma20,
        name="MA 20",
        line=dict(color="#60a5fa", width=1.6, dash="solid"),
        opacity=0.9,
        hovertemplate="MA20: $%{y:.2f}<extra></extra>",
    ),
    row=1, col=1,
)

# ── Row 1: 50-day MA overlay ──────────────────────────────────────────────────
fig.add_trace(
    go.Scatter(
        x=hist.index,
        y=ma50,
        name="MA 50",
        line=dict(color="#fb923c", width=1.6, dash="solid"),
        opacity=0.9,
        hovertemplate="MA50: $%{y:.2f}<extra></extra>",
    ),
    row=1, col=1,
)

# ── Row 2: Volume bars ────────────────────────────────────────────────────────
vol_colors = [
    "#22c55e" if c >= o else "#ef4444"
    for c, o in zip(hist["Close"], hist["Open"])
]
fig.add_trace(
    go.Bar(
        x=hist.index,
        y=hist["Volume"],
        name="Volume",
        marker_color=vol_colors,
        opacity=0.75,
        hovertemplate="Vol: %{y:,.0f}<extra></extra>",
    ),
    row=2, col=1,
)

fig.update_layout(
    template="plotly_dark",
    title=dict(
        text=f"{symbol} — Price & Volume",
        font=dict(size=16, color="#93c5fd", family="Inter, sans-serif"),
        x=0.01,
        xanchor="left",
    ),
    height=500,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#a0b4cc", size=12),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(15,22,41,0.85)",
        bordercolor="#1e3a5f",
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis_rangeslider_visible=False,
    margin=dict(l=10, r=10, t=50, b=10),
    hovermode="x unified",
    xaxis=dict(
        gridcolor="#1a2535",
        zerolinecolor="#1a2535",
        showgrid=True,
        showticklabels=False,
    ),
    xaxis2=dict(
        gridcolor="#1a2535",
        zerolinecolor="#1a2535",
        showgrid=True,
        showticklabels=True,
    ),
    yaxis=dict(
        gridcolor="#1a2535",
        zerolinecolor="#1a2535",
        showgrid=True,
        tickprefix="$",
        side="right",
    ),
    yaxis2=dict(
        gridcolor="#1a2535",
        zerolinecolor="#1a2535",
        showgrid=True,
        side="right",
    ),
)

st.plotly_chart(fig, use_container_width=True)

# ─── Technical Indicators ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Technical Indicators</div>', unsafe_allow_html=True)

# ── Compute indicators ────────────────────────────────────────────────────────
# RSI (14-period)
_delta = hist["Close"].diff()
_gain  = _delta.clip(lower=0).rolling(14).mean()
_loss  = (-_delta.clip(upper=0)).rolling(14).mean()
_rs    = _gain / _loss
rsi    = 100 - (100 / (1 + _rs))

# MACD
ema12     = hist["Close"].ewm(span=12, adjust=False).mean()
ema26     = hist["Close"].ewm(span=26, adjust=False).mean()
macd      = ema12 - ema26
signal    = macd.ewm(span=9, adjust=False).mean()
histogram = macd - signal

tab_rsi, tab_macd, tab_summary = st.tabs(["📊 RSI", "📉 MACD", "🗂️ Summary"])

# ── RSI Tab ───────────────────────────────────────────────────────────────────
with tab_rsi:
    fig_rsi = go.Figure()

    # Overbought / oversold shaded zone (30–70)
    fig_rsi.add_hrect(
        y0=30, y1=70,
        fillcolor="rgba(96, 165, 250, 0.07)",
        line_width=0,
        annotation_text="Neutral zone  30 – 70",
        annotation_position="top left",
        annotation_font=dict(color="#4d7aa8", size=10),
    )

    # Overbought line at 70
    fig_rsi.add_hline(
        y=70,
        line=dict(color="#ef4444", width=1.2, dash="dash"),
        annotation_text="Overbought 70",
        annotation_position="right",
        annotation_font=dict(color="#ef4444", size=10),
    )

    # Oversold line at 30
    fig_rsi.add_hline(
        y=30,
        line=dict(color="#22c55e", width=1.2, dash="dash"),
        annotation_text="Oversold 30",
        annotation_position="right",
        annotation_font=dict(color="#22c55e", size=10),
    )

    # RSI line — color segments by zone
    fig_rsi.add_trace(
        go.Scatter(
            x=hist.index,
            y=rsi,
            name="RSI (14)",
            line=dict(color="#818cf8", width=2),
            fill="tozeroy",
            fillcolor="rgba(129, 140, 248, 0.06)",
            hovertemplate="RSI: %{y:.2f}<extra></extra>",
        )
    )

    fig_rsi.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"{symbol} — RSI (14-Period)",
            font=dict(size=15, color="#93c5fd", family="Inter, sans-serif"),
            x=0.01, xanchor="left",
        ),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#a0b4cc", size=12),
        margin=dict(l=10, r=80, t=50, b=10),
        hovermode="x unified",
        yaxis=dict(
            range=[0, 100],
            gridcolor="#1a2535",
            zerolinecolor="#1a2535",
            ticksuffix="  ",
            side="right",
        ),
        xaxis=dict(gridcolor="#1a2535", zerolinecolor="#1a2535"),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(15,22,41,0.85)",
            bordercolor="#1e3a5f",
            borderwidth=1,
        ),
    )
    st.plotly_chart(fig_rsi, use_container_width=True)

    # RSI interpretation hint
    last_rsi = rsi.dropna().iloc[-1] if not rsi.dropna().empty else None
    if last_rsi is not None:
        if last_rsi >= 70:
            st.markdown(
                f"⚠️ **RSI = {last_rsi:.1f}** — Stock may be **overbought**. Watch for a potential pullback.",
                unsafe_allow_html=False,
            )
        elif last_rsi <= 30:
            st.markdown(
                f"💡 **RSI = {last_rsi:.1f}** — Stock may be **oversold**. Possible buying opportunity.",
                unsafe_allow_html=False,
            )
        else:
            st.markdown(
                f"✅ **RSI = {last_rsi:.1f}** — Stock is in the **neutral zone** (30–70).",
                unsafe_allow_html=False,
            )

# ── MACD Tab ──────────────────────────────────────────────────────────────────
with tab_macd:
    fig_macd = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.55, 0.45],
    )

    # MACD line
    fig_macd.add_trace(
        go.Scatter(
            x=hist.index, y=macd,
            name="MACD",
            line=dict(color="#60a5fa", width=1.8),
            hovertemplate="MACD: %{y:.4f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # Signal line
    fig_macd.add_trace(
        go.Scatter(
            x=hist.index, y=signal,
            name="Signal (9)",
            line=dict(color="#fb923c", width=1.8, dash="dot"),
            hovertemplate="Signal: %{y:.4f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # Zero line reference
    fig_macd.add_hline(y=0, line=dict(color="#334155", width=1), row=1, col=1)

    # Histogram bars
    hist_colors = [
        "#22c55e" if v >= 0 else "#ef4444"
        for v in histogram
    ]
    fig_macd.add_trace(
        go.Bar(
            x=hist.index, y=histogram,
            name="Histogram",
            marker_color=hist_colors,
            opacity=0.8,
            hovertemplate="Hist: %{y:.4f}<extra></extra>",
        ),
        row=2, col=1,
    )

    fig_macd.add_hline(y=0, line=dict(color="#334155", width=1), row=2, col=1)

    fig_macd.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"{symbol} — MACD (12, 26, 9)",
            font=dict(size=15, color="#93c5fd", family="Inter, sans-serif"),
            x=0.01, xanchor="left",
        ),
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#a0b4cc", size=12),
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(15,22,41,0.85)",
            bordercolor="#1e3a5f", borderwidth=1,
        ),
        xaxis=dict(gridcolor="#1a2535", zerolinecolor="#1a2535", showticklabels=False),
        xaxis2=dict(gridcolor="#1a2535", zerolinecolor="#1a2535", showticklabels=True),
        yaxis=dict(gridcolor="#1a2535", zerolinecolor="#1a2535", side="right", tickformat=".3f"),
        yaxis2=dict(gridcolor="#1a2535", zerolinecolor="#1a2535", side="right", tickformat=".3f"),
    )
    st.plotly_chart(fig_macd, use_container_width=True)

    # MACD interpretation hint
    last_macd   = macd.dropna().iloc[-1]   if not macd.dropna().empty   else None
    last_signal = signal.dropna().iloc[-1] if not signal.dropna().empty else None
    if last_macd is not None and last_signal is not None:
        if last_macd > last_signal:
            st.markdown(f"📈 **MACD ({last_macd:.4f}) > Signal ({last_signal:.4f})** — Bullish crossover signal.", unsafe_allow_html=False)
        else:
            st.markdown(f"📉 **MACD ({last_macd:.4f}) < Signal ({last_signal:.4f})** — Bearish crossover signal.", unsafe_allow_html=False)

# ── Summary Tab ───────────────────────────────────────────────────────────────
with tab_summary:
    summary_df = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
    summary_df["RSI"]       = rsi.round(2)
    summary_df["MACD"]      = macd.round(4)
    summary_df["Signal"]    = signal.round(4)
    summary_df["Histogram"] = histogram.round(4)

    # Format display
    for col in ["Open", "High", "Low", "Close"]:
        summary_df[col] = summary_df[col].map(lambda x: f"${x:.2f}")
    summary_df["Volume"] = summary_df["Volume"].map(lambda x: f"{int(x):,}")

    st.dataframe(
        summary_df.tail(10).iloc[::-1],  # most recent first
        use_container_width=True,
        column_config={
            "Open":      st.column_config.TextColumn("Open"),
            "High":      st.column_config.TextColumn("High"),
            "Low":       st.column_config.TextColumn("Low"),
            "Close":     st.column_config.TextColumn("Close"),
            "Volume":    st.column_config.TextColumn("Volume"),
            "RSI":       st.column_config.NumberColumn("RSI (14)",  format="%.2f"),
            "MACD":      st.column_config.NumberColumn("MACD",      format="%.4f"),
            "Signal":    st.column_config.NumberColumn("Signal (9)",format="%.4f"),
            "Histogram": st.column_config.NumberColumn("Histogram", format="%.4f"),
        },
    )
    st.caption("Showing last 10 trading sessions · Most recent first")

# ─── Stock Comparison ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Stock Comparison</div>', unsafe_allow_html=True)

comp_input = st.text_input(
    "Enter tickers to compare (comma separated)",
    value="AAPL, MSFT, GOOG",
    help="Type any valid stock tickers separated by commas."
)

comp_symbols = [s.strip().upper() for s in comp_input.split(",") if s.strip()]
if len(comp_symbols) > 5:
    st.warning("Only comparing the first 5 tickers to maintain chart readability.")
    comp_symbols = comp_symbols[:5]

if comp_symbols:
    with st.spinner("Fetching comparison data..."):
        comp_data_raw = yf.download(comp_symbols, period=period, progress=False)
        
        try:
            if "Close" in comp_data_raw:
                comp_data = comp_data_raw["Close"]
            else:
                comp_data = pd.DataFrame()
        except Exception:
            comp_data = comp_data_raw.copy()
            
        if isinstance(comp_data, pd.Series):
            comp_data = comp_data.to_frame(comp_symbols[0])
            
        if not comp_data.empty:
            # Drop any columns that are entirely NaN
            comp_data = comp_data.dropna(axis=1, how="all")
            # Fill missing values to allow normalization
            comp_data = comp_data.ffill().bfill()
            
            # Normalize to 100
            norm_data = comp_data / comp_data.iloc[0] * 100

            fig_comp = go.Figure()
            for col in norm_data.columns:
                fig_comp.add_trace(go.Scatter(
                    x=norm_data.index,
                    y=norm_data[col],
                    mode="lines",
                    name=str(col),
                    hovertemplate="%{y:.2f}%<extra></extra>"
                ))
                
            fig_comp.update_layout(
                template="plotly_dark",
                title=dict(
                    text="Normalized Performance (%)",
                    font=dict(size=16, color="#93c5fd", family="Inter, sans-serif"),
                    x=0.01, xanchor="left",
                ),
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color="#a0b4cc", size=12),
                hovermode="x unified",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(15,22,41,0.85)", bordercolor="#1e3a5f", borderwidth=1,
                ),
                xaxis=dict(gridcolor="#1a2535", zerolinecolor="#1a2535"),
                yaxis=dict(gridcolor="#1a2535", zerolinecolor="#1a2535", ticksuffix="%"),
                margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# ─── Company Info ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Company Information</div>', unsafe_allow_html=True)

info_pairs = [
    ("Sector",          info.get("sector", "N/A")),
    ("Industry",        info.get("industry", "N/A")),
    ("Country",         info.get("country", "N/A")),
    ("Market Cap",      fmt_num(info.get("marketCap"))),
    ("52-Week High",    fmt_price(info.get("fiftyTwoWeekHigh"))),
    ("52-Week Low",     fmt_price(info.get("fiftyTwoWeekLow"))),
    ("P/E Ratio",       f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get("trailingPE"), float) else "N/A"),
    ("EPS (TTM)",       fmt_price(info.get("trailingEps"))),
    ("Dividend Yield",  f"{info.get('dividendYield', 0)*100:.2f}%" if info.get("dividendYield") else "N/A"),
    ("Beta",            f"{info.get('beta', 'N/A'):.2f}" if isinstance(info.get("beta"), float) else "N/A"),
    ("Avg Volume",      f"{info.get('averageVolume', 0):,}" if info.get("averageVolume") else "N/A"),
    ("Exchange",        info.get("exchange", "N/A")),
]

html_rows = "".join([
    f'<div class="info-row"><span class="info-label">{k}</span><span class="info-value">{v}</span></div>'
    for k, v in info_pairs
])

st.markdown(f'<div class="info-card">{html_rows}</div>', unsafe_allow_html=True)

# ─── Business Summary ────────────────────────────────────────────────────────
summary = info.get("longBusinessSummary")
if summary:
    with st.expander("📖 Business Summary", expanded=False):
        st.markdown(f"<p style='color:#a0b4cc; font-size:0.9rem; line-height:1.7;'>{summary}</p>", unsafe_allow_html=True)

# ─── News Feed ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Latest News</div>', unsafe_allow_html=True)

try:
    url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        xml_data = response.read()
    root = ET.fromstring(xml_data)
    
    news_items = []
    for item in root.findall('.//item')[:5]:
        title = item.find('title').text if item.find('title') is not None else 'No Title'
        link = item.find('link').text if item.find('link') is not None else '#'
        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else 'Unknown Date'
        source = item.find('source').text if item.find('source') is not None else 'Google News'
        news_items.append({'title': title, 'link': link, 'pubDate': pubDate, 'source': source})

    if news_items:
        for article in news_items:
            with st.expander(f"📰 {article['title']}"):
                st.caption(f"**Source:** {article['source']} | **Published:** {article['pubDate']}")
                st.markdown(f"[Read full article]({article['link']})")
    else:
        st.write("No news available for this ticker.")
except Exception as e:
    st.error("Could not fetch news at this time.")

# ─── Data Export ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Data Export</div>', unsafe_allow_html=True)
csv_data = hist.to_csv().encode('utf-8')
st.download_button(
    label="⬇️ Download CSV",
    data=csv_data,
    file_name=f"{symbol}_data.csv",
    mime='text/csv'
)

st.markdown("<br><p style='text-align:center; color:#2a3f5f; font-size:0.8rem;'>StockSense · Powered by yfinance & Plotly · For informational purposes only</p>", unsafe_allow_html=True)
