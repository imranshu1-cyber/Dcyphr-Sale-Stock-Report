import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Dcyphr Sale & Stock Report", layout="wide", page_icon="📊")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
*, *::before, *::after { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
.stApp { background: #f4f0ff !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0.8rem !important; padding-bottom: 1rem !important; }

.hero {
    padding: 0.55rem 1.4rem; display: flex; align-items: center; gap: 1rem;
    background: linear-gradient(90deg, #3a0068 0%, #6a1b9a 55%, #9c27b0 100%);
    margin-bottom: 1rem; border-radius: 12px;
    box-shadow: 0 3px 14px rgba(106,27,154,0.3);
}
.hero-badge {
    background: rgba(255,255,255,0.18); border: 1.5px solid rgba(255,255,255,0.35);
    color: #ffffff; font-size:.56rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; padding:4px 11px; border-radius:20px; white-space:nowrap;
}
.hero-title { font-family:'Plus Jakarta Sans',sans-serif !important; font-size:1.05rem; font-weight:800; color:#ffffff; }
.hero-sub-line { font-family:'Plus Jakarta Sans',sans-serif !important; font-size:.8rem; font-weight:600; color:#e8c8ff; }
.hero-sub { color:rgba(255,255,255,0.52); font-size:.65rem; font-weight:400; }

.kpi-card {
    background: linear-gradient(135deg, #6a1b9a 0%, #9c27b0 100%);
    border-radius: 16px; padding: 1.1rem 1.3rem;
    box-shadow: 0 4px 18px rgba(106,27,154,0.35);
}
.kpi-label { font-size:.58rem; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:rgba(255,255,255,0.75); margin-bottom:.4rem; }
.kpi-value { font-family:'Plus Jakarta Sans',sans-serif !important; font-size:1.3rem; font-weight:800; color:#ffffff; line-height:1.1; }
.kpi-sub { font-size:.72rem; color:rgba(255,255,255,0.7); margin-top:.25rem; }
.section-title {
    font-size:.63rem; font-weight:700; letter-spacing:2.5px; text-transform:uppercase;
    color:#6a1b9a; padding:.4rem 0; margin-bottom:.7rem; border-bottom: 2px solid #ddd6fe;
}
p { color:#1a0030 !important; font-size:.9rem !important; }
label { color:#3d0066 !important; font-weight:600 !important; }
[data-testid="stWidgetLabel"] p { color:#6a1b9a !important; font-weight:700 !important; font-size:.85rem !important; }
.stSelectbox > div > div { background:#ffffff !important; border:1.5px solid #c084fc !important; border-radius:10px !important; color:#1a0030 !important; }
[data-baseweb="select"] > div { background:#ffffff !important; border:1.5px solid #c084fc !important; border-radius:10px !important; }
[data-baseweb="popover"] { background:#fff !important; border:1px solid #c084fc !important; }
[data-baseweb="popover"] * { color:#1a0030 !important; background:#fff !important; }
.stMultiSelect > div > div { background:#ffffff !important; border:1.5px solid #c084fc !important; border-radius:10px !important; }
.stButton > button {
    background: linear-gradient(135deg,#6a1b9a,#9c27b0) !important;
    color:#ffffff !important; border:none !important; border-radius:12px !important;
    font-weight:700 !important; padding:.7rem 2rem !important;
    box-shadow:0 4px 14px rgba(106,27,154,0.38) !important;
}
.stButton > button p { color:#ffffff !important; font-weight:700 !important; }
.stDownloadButton > button {
    background:#fff !important; color:#6a1b9a !important;
    border:2px solid #6a1b9a !important; border-radius:10px !important; font-weight:700 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background:#fff !important; border-radius:12px !important; padding:4px !important;
    border:1.5px solid #ddd6fe !important;
}
.stTabs [data-baseweb="tab"] { color:#1a0030 !important; border-radius:8px !important; font-size:.84rem !important; font-weight:600 !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#6a1b9a,#9c27b0) !important; color:#ffffff !important; }
.stTabs [aria-selected="true"] * { color:#ffffff !important; }
div[data-testid="stDataFrame"] * { color:#1a0030 !important; font-size:.84rem !important; }
[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important; border: 2px dashed #c084fc !important;
    border-radius: 14px !important; padding: 16px !important;
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: center !important;
    min-height: 0 !important; max-height: 80px !important;
}
[data-testid="stFileUploaderDropzone"] button {
    visibility: hidden !important; height: 0 !important; padding: 0 !important; margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ══ CONSTANTS ══
MONTHS_ORDER = ['March','April','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',"Jan'26","Feb'26","March'26"]
MONTH_SHORT  = ['Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar26']
CAT_COLORS   = ['#7b1fa2','#e91e63','#ff6f00','#1565c0','#2e7d32','#00838f','#f57f17','#6a1b9a']
BLUE_SEQ     = [[0,'#f3e5f5'],[0.4,'#9c27b0'],[1,'#6a1b9a']]

# ══ HELPERS ══
def fmt_inr(v):
    if pd.isna(v) or v == 0: return "—"
    v = int(round(float(v)))
    s = str(abs(v)); prefix = "-" if v < 0 else ""
    if len(s) <= 3: return prefix + s
    last3 = s[-3:]; rest = s[:-3]; groups = []
    while len(rest) > 2: groups.append(rest[-2:]); rest = rest[:-2]
    if rest: groups.append(rest)
    groups.reverse()
    return prefix + ','.join(groups) + ',' + last3

def pct(v, dec=1):
    if pd.isna(v) or v == 0: return "—"
    return f"{float(v)*100:.{dec}f}%"

def cl(height=380, title="", xangle=0, margin=None):
    m = margin or dict(l=10, r=10, t=55, b=40)
    return dict(
        paper_bgcolor="rgba(255,255,255,1)", plot_bgcolor="rgba(245,240,255,0.5)",
        font=dict(color="#1a0030", family="Inter", size=12),
        margin=m, height=height,
        title=dict(text=f"<b>{title}</b>", font=dict(color="#1a0030", size=14, family="Plus Jakarta Sans")),
        legend=dict(font=dict(color="#1a0030", size=11), bgcolor="rgba(255,255,255,0.97)",
                    bordercolor="#ddd6fe", borderwidth=1.5),
        xaxis=dict(gridcolor="#ede9fe", tickfont=dict(color="#1a0030", size=11),
                   linecolor="#ddd6fe", tickangle=xangle, showgrid=True),
        yaxis=dict(gridcolor="#ede9fe", tickfont=dict(color="#1a0030", size=11),
                   linecolor="#ddd6fe", showgrid=True),
    )

def kpi(col, label, value, sub, icon):
    with col:
        st.markdown(f"""<div class="kpi-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.3rem">
            <div class="kpi-label">{label}</div><span style="font-size:1.1rem">{icon}</span>
          </div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

def sec(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

# ══ PROCESS ══
@st.cache_data(show_spinner=False)
def process(file_bytes):
    df = pd.read_excel(file_bytes, sheet_name='Sale data ', header=0)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={
        'DEVISION DESC.': 'Division',
        'CATEGORY DESC.': 'Category',
        'GENDER.': 'Gender',
        'Brand.': 'Brand',
        'Net Sale (Tax Incl)': 'NetSale',
        'Month Name': 'Month'
    })
    for col in ['Sale Qty', 'NetSale', 'MRP Value', 'Discount Amount']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Distributor'] = df['Distributor'].str.strip()
    df['Store Name']  = df['Store Name'].str.strip()
    df['Gender']      = df['Gender'].str.upper().str.strip()
    df['Category']    = df['Category'].str.upper().str.strip()
    return df

def summary_box(df, title):
    total_sale = df['NetSale'].sum()
    total_qty  = int(df['Sale Qty'].sum())
    total_mrp  = df['MRP Value'].sum()
    avg_disc   = ((df['Discount Amount'].sum() / total_mrp * 100) if total_mrp > 0 else 0)
    top_ch     = df.groupby('Distributor')['NetSale'].sum().idxmax() if len(df) > 0 else "—"
    top_st     = df.groupby('Store Name')['NetSale'].sum().idxmax() if len(df) > 0 else "—"

    st.markdown(f"""<div style="background:linear-gradient(135deg,#3a0068,#6a1b9a);
        border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem;color:#fff">
        <div style="font-size:.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;
            color:rgba(255,255,255,.7);margin-bottom:.5rem">📋 {title}</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem">
            <div><div style="font-size:.6rem;color:rgba(255,255,255,.6);text-transform:uppercase">Total Net Sale</div>
                <div style="font-size:1.1rem;font-weight:800">₹{fmt_inr(int(total_sale))}</div></div>
            <div><div style="font-size:.6rem;color:rgba(255,255,255,.6);text-transform:uppercase">Total Qty Sold</div>
                <div style="font-size:1.1rem;font-weight:800">{total_qty:,} Pcs</div></div>
            <div><div style="font-size:.6rem;color:rgba(255,255,255,.6);text-transform:uppercase">Avg Discount</div>
                <div style="font-size:1.1rem;font-weight:800">{avg_disc:.1f}%</div></div>
            <div><div style="font-size:.6rem;color:rgba(255,255,255,.6);text-transform:uppercase">Top Channel</div>
                <div style="font-size:.85rem;font-weight:700">{top_ch[:30]}</div></div>
            <div><div style="font-size:.6rem;color:rgba(255,255,255,.6);text-transform:uppercase">Top Store</div>
                <div style="font-size:.85rem;font-weight:700">{top_st[:30]}</div></div>
            <div><div style="font-size:.6rem;color:rgba(255,255,255,.6);text-transform:uppercase">Total Channels</div>
                <div style="font-size:1.1rem;font-weight:800">{df['Distributor'].nunique()}</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

# ══ SESSION ══
for k,v in {"ready":False,"data":None,"mode":None}.items():
    if k not in st.session_state: st.session_state[k] = v

# ══ HERO ══
st.markdown("""
<div class="hero">
  <div class="hero-badge">DCYPHR</div>
  <div style="width:1px;height:26px;background:rgba(255,255,255,.22)"></div>
  <div>
    <div style="display:flex;align-items:baseline;gap:.6rem">
      <div class="hero-title">Dcyphr Sale &amp; Stock Report</div>
      <div style="color:rgba(255,255,255,.4)">→</div>
      <div class="hero-sub-line">Channel · Store · Category · Gender Analysis</div>
    </div>
    <div class="hero-sub">Upload Report &nbsp;·&nbsp; Auto Analysis &nbsp;·&nbsp; Excel Export</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══ UPLOAD BUTTONS ══
st.markdown("""<div style="text-align:center;margin-bottom:1rem">
    <div style="font-size:.75rem;font-weight:600;color:#6a1b9a;margin-bottom:.6rem;text-transform:uppercase;letter-spacing:1px">
        Select Report Type to Upload
    </div>
</div>""", unsafe_allow_html=True)

b1, b2 = st.columns(2)
with b1:
    if st.button("📦  Channel Sale & Stock Report", use_container_width=True):
        st.session_state.mode = "channel"
        st.session_state.ready = False
        st.session_state.data = None
with b2:
    if st.button("🏪  Store Sale & Stock Report", use_container_width=True):
        st.session_state.mode = "store"
        st.session_state.ready = False
        st.session_state.data = None

if st.session_state.mode:
    mode_label = "Channel Sale & Stock Report" if st.session_state.mode == "channel" else "Store Sale & Stock Report"
    u1,u2,u3 = st.columns([1,2,1])
    with u2:
        uploaded = st.file_uploader(
            f"📂 Upload {mode_label} · XLSX",
            type=["xlsx","xls"],
            label_visibility="visible",
            key=f"up_{st.session_state.mode}"
        )
        if uploaded:
            if st.button("⚡  Generate Analysis", use_container_width=True):
                with st.spinner("Processing..."):
                    file_bytes = BytesIO(uploaded.read())
                    st.session_state.data  = process(file_bytes)
                    st.session_state.ready = True
                st.success("✅ Done! Analysis Ready.")

if not st.session_state.ready:
    st.markdown("""<div style="text-align:center;padding:4rem 0">
      <div style="font-size:3rem">📊</div>
      <div style="margin-top:1rem;font-size:1rem;color:#607d9b;font-weight:500">
        Select report type above and upload file</div>
      <div style="margin-top:.4rem;font-size:.82rem;color:#90a4c0">
        Channel wise or Store wise analysis will be generated instantly</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df = st.session_state.data
mode = st.session_state.mode

# ══ KPIs ══
total_sale = df['NetSale'].sum()
total_qty  = int(df['Sale Qty'].sum())
total_mrp  = df['MRP Value'].sum()
avg_disc   = (df['Discount Amount'].sum() / total_mrp * 100) if total_mrp > 0 else 0
top_ch     = df.groupby('Distributor')['NetSale'].sum().idxmax()
top_st     = df.groupby('Store Name')['NetSale'].sum().idxmax()

k1,k2,k3,k4,k5,k6 = st.columns(6)
kpi(k1, "Total Net Sale",   f"₹{fmt_inr(int(total_sale))}", f"Mar'25–Mar'26", "💰")
kpi(k2, "Total Qty Sold",   f"{total_qty:,} Pcs",           "All channels", "📦")
kpi(k3, "Avg Discount",     f"{avg_disc:.1f}%",             "On MRP value", "🏷️")
kpi(k4, "Total Channels",   str(df['Distributor'].nunique()), "Active distributors", "🔗")
kpi(k5, "Top Channel",      top_ch.split()[0]+" "+top_ch.split()[1] if len(top_ch.split())>1 else top_ch[:15], f"₹{fmt_inr(int(df.groupby('Distributor')['NetSale'].sum().max()))}", "🏆")
kpi(k6, "Top Store",        top_st[:18],                    f"₹{fmt_inr(int(df.groupby('Store Name')['NetSale'].sum().max()))}", "⭐")
st.markdown("<br>", unsafe_allow_html=True)

# ══ TABS ══
t1,t2,t3,t4,t5 = st.tabs([
    "📈 Overview", "📦 Channel-wise", "🏪 Store-wise",
    "🗂️ Category & Gender", "📋 Export"
])

# ══ TAB 1: OVERVIEW ══
with t1:
    sec("📈 Monthly Net Sale Trend")
    monthly = df.groupby('Month')['NetSale'].sum().reindex(MONTHS_ORDER).fillna(0)
    bi = int(monthly.values.argmax()); wi = int(monthly.values.argmin())
    bcolors = ['#9c27b0' if i not in [bi,wi] else ('#16a34a' if i==bi else '#dc2626') for i in range(len(monthly))]
    fig = go.Figure(go.Bar(
        x=MONTH_SHORT, y=monthly.values,
        marker=dict(color=bcolors, line=dict(width=0)),
        text=[f"₹{fmt_inr(int(v))}" for v in monthly.values],
        textposition='outside', textfont=dict(size=10,color='#1a0030'),
    ))
    fig.update_layout(**cl(360,"Monthly Net Sale Trend — All Channels (Mar'25–Mar'26)",
        margin=dict(l=10,r=10,t=55,b=40)),
        bargap=0.3, yaxis_range=[0, monthly.max()*1.25],
        annotations=[
            dict(x=MONTH_SHORT[bi],y=monthly.values[bi]*1.18,text="🏆 Best",showarrow=False,font=dict(color='#16a34a',size=10)),
            dict(x=MONTH_SHORT[wi],y=monthly.values[wi]*1.18,text="⬇ Low",showarrow=False,font=dict(color='#dc2626',size=10)),
        ])
    st.plotly_chart(fig, use_container_width=True)

    # MoM Growth
    mom = monthly.pct_change()*100
    mp = [float(v) for v in mom.values[1:]]
    fig_mom = go.Figure(go.Bar(
        x=MONTH_SHORT[1:], y=mp,
        marker=dict(color=['#16a34a' if v>=0 else '#dc2626' for v in mp], line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in mp], textposition='outside', textfont=dict(size=10,color='#1a0030')))
    fig_mom.update_layout(**cl(300,"Month-on-Month Growth (%)",margin=dict(l=10,r=10,t=55,b=40)),
        bargap=0.3)
    fig_mom.update_layout(yaxis=dict(gridcolor='#ede9fe',zeroline=True,zerolinecolor='#9c27b0',zerolinewidth=2))
    st.plotly_chart(fig_mom, use_container_width=True)

    ca,cb = st.columns(2)
    with ca:
        sec("🏆 Top Channels by Sale")
        ch_sale = df.groupby('Distributor')['NetSale'].sum().sort_values()
        fig2 = go.Figure(go.Bar(
            x=ch_sale.values, y=[c[:25] for c in ch_sale.index.tolist()], orientation='h',
            marker=dict(color=ch_sale.values, colorscale=BLUE_SEQ, line=dict(width=0)),
            text=[f"₹{fmt_inr(int(v))}" for v in ch_sale.values],
            textposition='outside', textfont=dict(size=10,color='#1a0030')))
        fig2.update_layout(**cl(320,"Channel-wise Total Net Sale",margin=dict(l=10,r=200,t=55,b=40)),
            xaxis_range=[0,ch_sale.max()*1.45])
        st.plotly_chart(fig2, use_container_width=True)

    with cb:
        sec("🗂️ Category Mix")
        cat_s = df.groupby('Category')['NetSale'].sum().sort_values(ascending=False)
        cat_s = cat_s[cat_s>0]
        fig3 = go.Figure(go.Pie(
            labels=cat_s.index.tolist(), values=cat_s.values.tolist(), hole=0.5,
            marker=dict(colors=CAT_COLORS[:len(cat_s)], line=dict(color='#fff',width=2)),
            textinfo='label+percent', textfont=dict(size=11,color='#1a0030'),
            insidetextfont=dict(size=10,color='#fff')))
        fig3.update_layout(**cl(320,"Category-wise Sale",margin=dict(l=10,r=10,t=55,b=10)),
            annotations=[dict(text=f"<b>₹{fmt_inr(int(total_sale))}</b>",x=0.5,y=0.5,
                font=dict(size=11,color='#1a0030'),showarrow=False)])
        st.plotly_chart(fig3, use_container_width=True)

# ══ TAB 2: CHANNEL-WISE ══
with t2:
    sec("📦 Channel-wise Monthly Sale Trend")
    channels = df['Distributor'].dropna().unique().tolist()
    sel_ch = st.multiselect("Select Channels", channels, default=channels, key="ch_sel")

    if sel_ch:
        fig_ch = go.Figure()
        for i,ch in enumerate(sel_ch):
            cd = df[df['Distributor']==ch].groupby('Month')['NetSale'].sum().reindex(MONTHS_ORDER).fillna(0)
            fig_ch.add_trace(go.Bar(x=MONTH_SHORT, y=cd.values, name=ch[:25],
                marker_color=CAT_COLORS[i%len(CAT_COLORS)],
                hovertemplate=f'<b>{ch[:25]}</b><br>%{{x}}: ₹%{{y:,.0f}}<extra></extra>'))
        fig_ch.update_layout(**cl(400,"Channel-wise Monthly Sale",margin=dict(l=10,r=10,t=55,b=40)),
            barmode='group', bargap=0.12)
        st.plotly_chart(fig_ch, use_container_width=True)

    sec("📋 Channel Summary Table")
    ch_tbl = df.groupby('Distributor').agg(
        Total_Sale=('NetSale','sum'),
        Total_Qty=('Sale Qty','sum'),
        MRP_Value=('MRP Value','sum'),
        Discount=('Discount Amount','sum'),
        Stores=('Store Name','nunique')
    ).reset_index()
    ch_tbl['Avg Disc%'] = (ch_tbl['Discount']/ch_tbl['MRP_Value']*100).round(1)
    ch_tbl['Sale Cont%'] = (ch_tbl['Total_Sale']/ch_tbl['Total_Sale'].sum()*100).round(2)
    ch_tbl = ch_tbl.sort_values('Total_Sale',ascending=False)
    ch_tbl['Total_Sale'] = ch_tbl['Total_Sale'].apply(lambda x: f"₹{fmt_inr(int(x))}")
    ch_tbl['MRP_Value']  = ch_tbl['MRP_Value'].apply(lambda x: f"₹{fmt_inr(int(x))}")
    ch_tbl['Total_Qty']  = ch_tbl['Total_Qty'].apply(int)
    ch_tbl.columns = ['Channel','Net Sale','Total Qty','MRP Value','Discount','Stores','Avg Disc%','Sale Cont%']
    ch_tbl = ch_tbl.drop(columns=['Discount'])
    st.dataframe(ch_tbl, use_container_width=True, hide_index=True)

    sec("📅 Channel Month-wise Detail")
    ch_pivot = df.pivot_table(index='Distributor',columns='Month',values='NetSale',aggfunc='sum').reindex(columns=MONTHS_ORDER).fillna(0)
    ch_pivot['Total'] = ch_pivot.sum(axis=1)
    ch_pivot = ch_pivot.sort_values('Total',ascending=False)
    ch_pivot.columns = [c if c!='Total' else 'Total Sale' for c in ch_pivot.columns]
    ch_pivot = ch_pivot.map(lambda x: f"₹{fmt_inr(int(x))}" if x!=0 else "—")
    st.dataframe(ch_pivot, use_container_width=True)

# ══ TAB 3: STORE-WISE ══
with t3:
    sec("🔍 Store Deep Dive")
    stores = sorted(df['Store Name'].dropna().unique().tolist())
    sel_store = st.selectbox("Select Store", stores, key="st_dd")
    if sel_store:
        ss = df[df['Store Name']==sel_store]
        ts = ss['NetSale'].sum(); tq = int(ss['Sale Qty'].sum())
        rank = int(df.groupby('Store Name')['NetSale'].sum().rank(ascending=False)[sel_store])
        cont = ts/total_sale if total_sale>0 else 0

        m1,m2,m3,m4 = st.columns(4)
        kpi(m1,"Net Sale",    f"₹{fmt_inr(int(ts))}", "Mar'25–Mar'26","💰")
        kpi(m2,"Qty Sold",    f"{tq:,} Pcs",          "Total pieces","📦")
        kpi(m3,"Contribution",pct(cont,2),             "Of total sale","📊")
        kpi(m4,"Store Rank",  f"#{rank}",              f"Out of {df['Store Name'].nunique()} stores","🏅")
        st.markdown("<br>", unsafe_allow_html=True)

        da,db = st.columns([3,2])
        with da:
            mm = ss.groupby('Month')['NetSale'].sum().reindex(MONTHS_ORDER).fillna(0)
            fig_dm = go.Figure(go.Bar(x=MONTH_SHORT,y=mm.values,
                marker=dict(color=mm.values,colorscale=BLUE_SEQ,line=dict(width=0)),
                text=[f"₹{fmt_inr(int(v))}" if v>0 else "" for v in mm.values],
                textposition='outside',textfont=dict(size=10,color='#1a0030')))
            fig_dm.update_layout(**cl(280,f"{sel_store} — Monthly Sale",margin=dict(l=10,r=10,t=50,b=40)),bargap=0.3)
            st.plotly_chart(fig_dm, use_container_width=True)

        with db:
            cd = ss.groupby('Category')['NetSale'].sum()
            cd = cd[cd>0]
            if len(cd)>0:
                fig_dp = go.Figure(go.Pie(labels=cd.index.tolist(),values=cd.values.tolist(),hole=0.48,
                    marker=dict(colors=CAT_COLORS[:len(cd)],line=dict(color='#fff',width=2)),
                    textinfo='label+percent',textfont=dict(size=11,color='#1a0030'),
                    insidetextfont=dict(size=10,color='#fff')))
                fig_dp.update_layout(**cl(280,"Category Mix",margin=dict(l=10,r=10,t=50,b=10)))
                st.plotly_chart(fig_dp, use_container_width=True)

    st.markdown("---")
    sec("🏪 Top 10 Stores by Net Sale")
    top10_st = df.groupby('Store Name')['NetSale'].sum().nlargest(10).sort_values()
    fig_st = go.Figure(go.Bar(
        x=top10_st.values, y=[s[:30] for s in top10_st.index.tolist()], orientation='h',
        marker=dict(color=top10_st.values, colorscale=BLUE_SEQ, line=dict(width=0)),
        text=[f"₹{fmt_inr(int(v))}" for v in top10_st.values],
        textposition='outside', textfont=dict(size=10,color='#1a0030')))
    fig_st.update_layout(**cl(420,"Top 10 Stores by Net Sale",margin=dict(l=10,r=180,t=55,b=40)),
        xaxis_range=[0,top10_st.max()*1.45])
    st.plotly_chart(fig_st, use_container_width=True)

    sec("📋 Store Summary Table")
    st_tbl = df.groupby(['Distributor','Store Name']).agg(
        Total_Sale=('NetSale','sum'),
        Total_Qty=('Sale Qty','sum'),
        MRP_Value=('MRP Value','sum'),
        Discount=('Discount Amount','sum'),
    ).reset_index()
    st_tbl['Avg Disc%']  = (st_tbl['Discount']/st_tbl['MRP_Value']*100).round(1)
    st_tbl['Sale Cont%'] = (st_tbl['Total_Sale']/st_tbl['Total_Sale'].sum()*100).round(2)
    st_tbl = st_tbl.sort_values('Total_Sale',ascending=False)
    st_tbl['Total_Sale'] = st_tbl['Total_Sale'].apply(lambda x: f"₹{fmt_inr(int(x))}")
    st_tbl['MRP_Value']  = st_tbl['MRP_Value'].apply(lambda x: f"₹{fmt_inr(int(x))}")
    st_tbl['Total_Qty']  = st_tbl['Total_Qty'].apply(int)
    st_tbl = st_tbl.drop(columns=['Discount'])
    st_tbl.columns = ['Channel','Store','Net Sale','Total Qty','MRP Value','Avg Disc%','Sale Cont%']
    st.dataframe(st_tbl, use_container_width=True, hide_index=True)

# ══ TAB 4: CATEGORY & GENDER ══
with t4:
    ca4,cb4 = st.columns(2)
    with ca4:
        sec("🗂️ Category Monthly Trend")
        cats = df['Category'].dropna().unique()
        fig_cat = go.Figure()
        for i,cat in enumerate(cats):
            cd = df[df['Category']==cat].groupby('Month')['NetSale'].sum().reindex(MONTHS_ORDER).fillna(0)
            fig_cat.add_trace(go.Scatter(x=MONTH_SHORT,y=cd.values,name=cat,
                mode='lines+markers',line=dict(color=CAT_COLORS[i%len(CAT_COLORS)],width=2.5),marker=dict(size=7)))
        fig_cat.update_layout(**cl(340,"Category Monthly Trend",margin=dict(l=10,r=10,t=55,b=40)))
        st.plotly_chart(fig_cat, use_container_width=True)

    with cb4:
        sec("👤 Gender Distribution")
        gdr = df.groupby('Gender')['NetSale'].sum().sort_values(ascending=False)
        gdr = gdr[gdr>0]
        fig_gdr = go.Figure(go.Pie(
            labels=gdr.index.tolist(),values=gdr.values.tolist(),hole=0.5,
            marker=dict(colors=['#7b1fa2','#e91e63','#1565c0'],line=dict(color='#fff',width=2)),
            textinfo='label+percent',textfont=dict(size=12,color='#1a0030'),
            insidetextfont=dict(size=10,color='#fff')))
        fig_gdr.update_layout(**cl(340,"Gender-wise Sale",margin=dict(l=10,r=10,t=55,b=10)))
        st.plotly_chart(fig_gdr, use_container_width=True)

    sec("🔍 Category × Gender × Channel Summary")
    cg_tbl = df.groupby(['Category','Gender','Distributor'])['NetSale'].sum().reset_index()
    cg_tbl = cg_tbl[cg_tbl['NetSale']>0].sort_values('NetSale',ascending=False)
    cg_tbl['NetSale'] = cg_tbl['NetSale'].apply(lambda x: f"₹{fmt_inr(int(x))}")
    cg_tbl.columns = ['Category','Gender','Channel','Net Sale']
    st.dataframe(cg_tbl, use_container_width=True, hide_index=True)

    sec("📅 Category Month-wise Table")
    cat_pivot = df.pivot_table(index='Category',columns='Month',values='NetSale',aggfunc='sum').reindex(columns=MONTHS_ORDER).fillna(0)
    cat_pivot['Total'] = cat_pivot.sum(axis=1)
    cat_pivot = cat_pivot.sort_values('Total',ascending=False)
    cat_pivot = cat_pivot.map(lambda x: f"₹{fmt_inr(int(x))}" if x!=0 else "—")
    st.dataframe(cat_pivot, use_container_width=True)

# ══ TAB 5: EXPORT ══
with t5:
    sec("📥 Export Data")

    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    def build_excel():
        wb = Workbook()

        def style_cell(ws, row, col, val, bg="FFFFFF", fg="1a0030", bold=False, sz=9):
            cell = ws.cell(row=row, column=col, value=val)
            cell.font = Font(bold=bold, size=sz, color=fg.replace('#',''), name="Calibri")
            cell.fill = PatternFill("solid", fgColor=bg.replace('#',''))
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(
                left=Side(style='thin',color="e5e7eb"), right=Side(style='thin',color="e5e7eb"),
                top=Side(style='thin',color="e5e7eb"), bottom=Side(style='thin',color="e5e7eb"))

        # Sheet 1 — Channel Summary
        ws1 = wb.active; ws1.title = "Channel Summary"
        ws1.sheet_view.showGridLines = False
        headers = ['Channel','Net Sale (₹)','Total Qty','MRP Value (₹)','Avg Disc%','Sale Cont%','Stores']
        for ci,h in enumerate(headers,1):
            style_cell(ws1,1,ci,h,"1e3a5f","FFFFFF",bold=True,sz=10)
        ch_data = df.groupby('Distributor').agg(
            NetSale=('NetSale','sum'), Qty=('Sale Qty','sum'),
            MRP=('MRP Value','sum'), Disc=('Discount Amount','sum'),
            Stores=('Store Name','nunique')).reset_index().sort_values('NetSale',ascending=False)
        for ri,row in enumerate(ch_data.itertuples(),2):
            disc_pct = round(row.Disc/row.MRP*100,1) if row.MRP>0 else 0
            cont_pct = round(row.NetSale/total_sale*100,2) if total_sale>0 else 0
            vals = [row.Distributor, int(row.NetSale), int(row.Qty), int(row.MRP), f"{disc_pct}%", f"{cont_pct}%", row.Stores]
            bg = "f5f3ff" if ri%2==0 else "FFFFFF"
            for ci,v in enumerate(vals,1): style_cell(ws1,ri,ci,v,bg)
        for ci,w in enumerate([30,15,12,15,10,10,8],1):
            ws1.column_dimensions[get_column_letter(ci)].width = w

        # Sheet 2 — Store Summary
        ws2 = wb.create_sheet("Store Summary")
        ws2.sheet_view.showGridLines = False
        headers2 = ['Channel','Store','Net Sale (₹)','Total Qty','Avg Disc%','Sale Cont%']
        for ci,h in enumerate(headers2,1):
            style_cell(ws2,1,ci,h,"1e3a5f","FFFFFF",bold=True,sz=10)
        st_data = df.groupby(['Distributor','Store Name']).agg(
            NetSale=('NetSale','sum'), Qty=('Sale Qty','sum'),
            MRP=('MRP Value','sum'), Disc=('Discount Amount','sum')).reset_index().sort_values('NetSale',ascending=False)
        for ri,row in enumerate(st_data.itertuples(),2):
            disc_pct = round(row.Disc/row.MRP*100,1) if row.MRP>0 else 0
            cont_pct = round(row.NetSale/total_sale*100,2) if total_sale>0 else 0
            vals = [row.Distributor, row._2, int(row.NetSale), int(row.Qty), f"{disc_pct}%", f"{cont_pct}%"]
            bg = "f5f3ff" if ri%2==0 else "FFFFFF"
            for ci,v in enumerate(vals,1): style_cell(ws2,ri,ci,v,bg)
        for ci,w in enumerate([28,28,15,12,10,10],1):
            ws2.column_dimensions[get_column_letter(ci)].width = w

        # Sheet 3 — Monthly Pivot
        ws3 = wb.create_sheet("Monthly Channel")
        ws3.sheet_view.showGridLines = False
        style_cell(ws3,1,1,"Channel","1e3a5f","FFFFFF",bold=True,sz=10)
        for ci,m in enumerate(MONTHS_ORDER,2):
            style_cell(ws3,1,ci,m,"1e3a5f","FFFFFF",bold=True,sz=9)
        style_cell(ws3,1,len(MONTHS_ORDER)+2,"Total","1e3a5f","FFFFFF",bold=True,sz=10)
        ch_pivot2 = df.pivot_table(index='Distributor',columns='Month',values='NetSale',aggfunc='sum').reindex(columns=MONTHS_ORDER).fillna(0)
        ch_pivot2['Total'] = ch_pivot2.sum(axis=1)
        for ri,(ch,row) in enumerate(ch_pivot2.iterrows(),2):
            style_cell(ws3,ri,1,ch,"f5f3ff" if ri%2==0 else "FFFFFF")
            for ci,v in enumerate(row.values,2):
                style_cell(ws3,ri,ci,int(v) if v>0 else "","f5f3ff" if ri%2==0 else "FFFFFF")
        ws3.column_dimensions['A'].width = 30
        for ci in range(2,len(MONTHS_ORDER)+3):
            ws3.column_dimensions[get_column_letter(ci)].width = 12

        out = BytesIO(); wb.save(out); out.seek(0)
        return out

    excel = build_excel()
    st.download_button(
        "📥  Download Excel Report",
        data=excel,
        file_name="Dcyphr_Sale_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=False
    )

    st.markdown("<br>", unsafe_allow_html=True)
    sec("📊 Raw Data Preview")
    preview = df[['Distributor','Store Name','Month','Category','Gender','Sale Qty','NetSale','Discount Amount']].copy()
    preview['NetSale'] = preview['NetSale'].apply(lambda x: round(x,2))
    preview['Discount Amount'] = preview['Discount Amount'].apply(lambda x: round(x,2))
    preview.columns = ['Channel','Store','Month','Category','Gender','Sale Qty','Net Sale','Discount']
    st.dataframe(preview, use_container_width=True, hide_index=True)
