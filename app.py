import streamlit as st
import streamlit.components.v1 as components
import anthropic
import base64
import json
import re
import time

# ── CONFIG ─────────────────────────────────────────────────────────────────
API_KEY = "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"

st.set_page_config(
    page_title="Deal Triage Agent · AcquiOS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS (injected into Streamlit shell) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #030608 !important;
    color: #E8F4F8 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 100% 50% at 50% -10%, rgba(0,210,255,0.09) 0%, transparent 55%),
        radial-gradient(ellipse 50% 30% at 90% 90%, rgba(0,255,180,0.04) 0%, transparent 50%),
        #030608 !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { display:none !important; }
[data-testid="stSidebar"] { display:none !important; }
.block-container { padding: 0 2.5rem 4rem !important; max-width: 1400px !important; }

.hero { text-align:center; padding:4rem 2rem 0.5rem; position:relative; }
.hero::after {
    content:''; display:block; width:100%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,210,255,0.2),rgba(0,255,159,0.2),transparent);
    margin-top:2rem;
}
.hero-badge {
    display:inline-block; font-family:'DM Mono',monospace; font-size:0.65rem;
    letter-spacing:0.22em; text-transform:uppercase; color:rgba(0,210,255,0.7);
    border:1px solid rgba(0,210,255,0.2); padding:0.3rem 0.9rem; border-radius:20px;
    margin-bottom:1.2rem; background:rgba(0,210,255,0.05);
}
.hero-title {
    font-family:'Syne',sans-serif; font-size:3.8rem; font-weight:800;
    line-height:1; letter-spacing:-0.03em;
    background:linear-gradient(135deg,#FFFFFF 0%,#00D2FF 45%,#00FF9F 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; margin-bottom:0.8rem;
}
.hero-sub {
    font-size:1rem; color:rgba(232,244,248,0.4); font-weight:300;
    max-width:420px; margin:0 auto; line-height:1.6;
}
.legend {
    display:flex; justify-content:center; gap:1.5rem;
    padding:1.2rem 0 1.5rem; flex-wrap:wrap;
}
.legend-item {
    display:flex; align-items:center; gap:0.5rem;
    font-family:'DM Mono',monospace; font-size:0.65rem;
    letter-spacing:0.1em; text-transform:uppercase; color:rgba(232,244,248,0.4);
}
.legend-dot { width:8px; height:8px; border-radius:50%; }

.upload-label {
    font-family:'DM Mono',monospace; font-size:0.65rem; letter-spacing:0.18em;
    text-transform:uppercase; color:rgba(0,210,255,0.5); display:block; margin-bottom:0.5rem;
}
.upload-hint {
    font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.08em;
    color:rgba(232,244,248,0.2); margin-top:0.5rem; text-align:center;
}
[data-testid="stFileUploader"] {
    background:rgba(0,210,255,0.02) !important;
    border:1px dashed rgba(0,210,255,0.18) !important;
    border-radius:10px !important; transition:all 0.3s !important;
}
[data-testid="stButton"] button {
    background:linear-gradient(135deg,#00D2FF 0%,#00FF9F 100%) !important;
    color:#030608 !important; font-family:'Syne',sans-serif !important;
    font-weight:700 !important; font-size:0.95rem !important;
    letter-spacing:0.06em !important; border:none !important;
    border-radius:10px !important; padding:0.75rem 1.5rem !important;
    width:100% !important; text-transform:uppercase !important;
    box-shadow:0 4px 24px rgba(0,210,255,0.25) !important;
    transition:all 0.25s !important;
}
[data-testid="stButton"] button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 40px rgba(0,210,255,0.4) !important;
    filter:brightness(1.08) !important;
}
.loader-wrap {
    background:rgba(0,210,255,0.02); border:1px solid rgba(0,210,255,0.1);
    border-radius:12px; padding:2.5rem 3rem; margin:1.5rem 0;
    text-align:center; position:relative; overflow:hidden;
}
.loader-wrap::before {
    content:''; position:absolute; top:0; left:-100%; width:100%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,210,255,0.5),transparent);
    animation:scanline 2s linear infinite;
}
@keyframes scanline { to { left:100%; } }
.loader-status {
    font-family:'DM Mono',monospace; font-size:0.95rem; color:#00D2FF;
    letter-spacing:0.05em; min-height:1.5rem;
}
.loader-cursor {
    display:inline-block; width:2px; height:1rem; background:#00D2FF;
    margin-left:3px; vertical-align:middle; animation:blink 0.7s step-end infinite;
}
@keyframes blink { 50% { opacity:0; } }
.loader-sub {
    font-family:'DM Mono',monospace; font-size:0.65rem; letter-spacing:0.15em;
    text-transform:uppercase; color:rgba(232,244,248,0.2); margin-top:0.75rem;
}
.loader-complete {
    font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;
    background:linear-gradient(135deg,#00FF9F,#00D2FF);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.summary-bar {
    display:flex; background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.06); border-radius:12px;
    overflow:hidden; margin-bottom:2rem; position:relative;
}
.summary-bar::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,210,255,0.3),rgba(0,255,159,0.3),transparent);
}
.s-stat { flex:1; text-align:center; padding:1.4rem 1rem; border-right:1px solid rgba(255,255,255,0.05); }
.s-stat:last-child { border-right:none; }
.s-val { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; line-height:1; }
.s-lbl { font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.14em; text-transform:uppercase; color:rgba(232,244,248,0.28); margin-top:0.35rem; }
.err { background:rgba(255,71,87,0.05); border:1px solid rgba(255,71,87,0.2); border-radius:8px; padding:0.9rem 1.2rem; font-size:0.84rem; color:rgba(255,71,87,0.8); margin-bottom:1rem; }
.empty { text-align:center; padding:5rem 2rem; }
.empty-icon { font-size:2.5rem; opacity:0.12; margin-bottom:1rem; }
.empty-t { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:rgba(232,244,248,0.12); margin-bottom:0.4rem; }
.empty-s { font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase; color:rgba(232,244,248,0.08); }
.footer { text-align:center; padding:2rem 0 1rem; font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.2em; text-transform:uppercase; color:rgba(232,244,248,0.1); }
</style>
""", unsafe_allow_html=True)

# ── CARD HTML TEMPLATE (used inside components.html — no sanitizer) ──────────
CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');
* { box-sizing:border-box; margin:0; padding:0; }
body { background:transparent; font-family:'Inter',sans-serif; color:#E8F4F8; }

.deal-card {
    position:relative; border-radius:16px; padding:2rem 2rem 1.5rem;
    overflow:hidden; animation:slideUp 0.5s ease forwards; opacity:0;
}
@keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
.c-go   { background:rgba(0,255,159,0.025); border:1px solid rgba(0,255,159,0.18); box-shadow:0 0 50px rgba(0,255,159,0.06); }
.c-soft { background:rgba(255,184,0,0.02);  border:1px solid rgba(255,184,0,0.15); }
.c-hard { background:rgba(255,71,87,0.025); border:1px solid rgba(255,71,87,0.18); box-shadow:0 0 50px rgba(255,71,87,0.05); }

.card-stripe { position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.s-go   { background:linear-gradient(90deg,#00FF9F,#00D2FF); }
.s-soft { background:linear-gradient(90deg,#FFB800,#FF6B00); }
.s-hard { background:linear-gradient(90deg,#FF4757,#FF2D55); }

.rank-pill {
    display:inline-flex; align-items:center; gap:0.35rem;
    font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.12em;
    text-transform:uppercase; padding:0.22rem 0.65rem; border-radius:20px; border:1px solid;
    margin-bottom:0.9rem;
}
.prop-name { font-family:'Syne',sans-serif; font-size:1.75rem; font-weight:800; color:#fff; line-height:1.1; letter-spacing:-0.02em; margin-bottom:0.3rem; }
.prop-meta { font-family:'DM Mono',monospace; font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; color:rgba(232,244,248,0.3); margin-bottom:1.25rem; }

.top-row { display:flex; justify-content:space-between; align-items:flex-start; gap:1.5rem; }
.top-left { flex:1; min-width:0; }
.score-wrap { text-align:center; flex-shrink:0; width:110px; }
.score-circle {
    width:88px; height:88px; border-radius:50%; display:flex; flex-direction:column;
    align-items:center; justify-content:center; margin:0 auto 0.65rem; border:3px solid;
}
.score-num { font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; line-height:1; }
.score-den { font-family:'DM Mono',monospace; font-size:0.55rem; opacity:0.35; }

.v-btn {
    display:block; width:100%; font-family:'Syne',sans-serif; font-size:0.78rem;
    font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
    padding:0.5rem; border-radius:8px; text-align:center; border:1px solid;
}
.v-go   { background:rgba(0,255,159,0.1); color:#00FF9F; border-color:rgba(0,255,159,0.3); animation:goGlow 2s ease-in-out infinite alternate; }
.v-soft { background:rgba(255,184,0,0.08); color:#FFB800; border-color:rgba(255,184,0,0.3); box-shadow:0 0 16px rgba(255,184,0,0.1); }
.v-hard { background:rgba(255,71,87,0.1); color:#FF4757; border-color:rgba(255,71,87,0.3); animation:hardGlow 2s ease-in-out infinite alternate; }
@keyframes goGlow   { from{box-shadow:0 0 15px rgba(0,255,159,0.15)} to{box-shadow:0 0 35px rgba(0,255,159,0.4)} }
@keyframes hardGlow { from{box-shadow:0 0 15px rgba(255,71,87,0.15)} to{box-shadow:0 0 35px rgba(255,71,87,0.4)} }

.metrics-row { display:flex; flex-wrap:wrap; gap:0.55rem; margin:1rem 0 1.25rem; }
.m-chip { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07); border-radius:6px; padding:0.32rem 0.72rem; font-family:'DM Mono',monospace; font-size:0.68rem; color:rgba(232,244,248,0.45); }
.m-chip b { color:#E8F4F8; font-weight:500; margin-left:0.3rem; }

.body-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-top:0.25rem; }
.sec-label { font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.16em; text-transform:uppercase; color:rgba(0,210,255,0.4); margin-bottom:0.45rem; margin-top:1.1rem; }
.thesis { font-size:0.87rem; color:rgba(232,244,248,0.58); line-height:1.65; font-style:italic; font-weight:300; }
.bull { background:rgba(0,255,159,0.04); border:1px solid rgba(0,255,159,0.1); border-radius:6px; padding:0.62rem 0.88rem; font-size:0.84rem; color:rgba(0,255,159,0.8); line-height:1.55; }
.flag { display:flex; align-items:flex-start; gap:0.5rem; font-size:0.82rem; color:rgba(255,184,0,0.78); margin:0.3rem 0; line-height:1.45; }
.fdot { width:4px; height:4px; border-radius:50%; background:rgba(255,184,0,0.6); margin-top:0.55rem; flex-shrink:0; }
.dq-tag { display:inline-block; font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.08em; padding:0.18rem 0.55rem; border-radius:4px; border:1px solid; margin-left:0.4rem; }
.dq-sub { font-size:0.76rem; color:rgba(232,244,248,0.3); margin-top:0.3rem; line-height:1.45; }
.dq-lbl { font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.14em; text-transform:uppercase; color:rgba(232,244,248,0.22); }

.key-q { background:rgba(0,210,255,0.04); border-left:2px solid rgba(0,210,255,0.35); border-radius:0 6px 6px 0; padding:0.78rem 1rem; font-size:0.87rem; color:rgba(232,244,248,0.72); line-height:1.55; margin-top:1.1rem; }
.kq-label { font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.14em; text-transform:uppercase; color:rgba(0,210,255,0.45); display:block; margin-bottom:0.3rem; }
.analyst-note { border-top:1px solid rgba(255,255,255,0.05); padding-top:0.85rem; margin-top:1rem; font-size:0.81rem; color:rgba(232,244,248,0.38); line-height:1.55; }
.analyst-note b { color:rgba(232,244,248,0.62); font-weight:500; }
</style>
"""

# ── HELPERS ───────────────────────────────────────────────────────────────────
PROMPT = """You are a senior CRE acquisitions analyst. Analyze this Offering Memorandum PDF and return ONLY valid JSON — no markdown, no backticks, no extra text:

{
  "deal_name": "Property name or address",
  "asset_class": "Multifamily / Retail / Industrial / Office / Mixed-Use",
  "location": "City, State",
  "market_tier": "Primary / Secondary / Tertiary",
  "asking_price": "dollar amount or Not disclosed",
  "price_per_unit": "dollar amount or Not disclosed",
  "cap_rate": "percentage or Not disclosed",
  "noi": "dollar amount or Not disclosed",
  "occupancy": "percentage or Not disclosed",
  "unit_count": "number or Not disclosed",
  "year_built": "year or Not disclosed",
  "investment_thesis": "2 sentence summary of the seller pitch",
  "bull_case": "The single strongest reason to pursue this deal",
  "red_flags": ["flag 1", "flag 2", "flag 3"],
  "key_question": "The single most important question before proceeding",
  "data_quality": "High / Medium / Low",
  "data_quality_reason": "one sentence",
  "verdict": "GO / SOFT PASS / HARD PASS",
  "verdict_reason": "2 sentence explanation",
  "score": 7
}

Scoring rules — apply in order:

SINGLE-TENANT NNN WITH INVESTMENT-GRADE CORPORATE GUARANTEE (Dollar General, Walmart, CVS, Walgreens, McDonald's, etc.):
- The corporate guarantee replaces location risk. A 6.5% cap on an absolute NNN Dollar General with 8+ years remaining and a recent tenant-funded expansion is a GO at 7-8/10.
- Recent tenant capital investment (expansion, renovation) in the last 3 years = strong commitment signal, add +1 to score.
- Flat rent in primary term is normal for NNN; bumps in options are standard and positive.
- Re-tenanting risk is a long-dated option risk, not a current cash flow risk — do not penalize as if it is imminent.
- Data quality: NNN single-tenant OMs rarely include T12; lease terms and corporate guarantee are the underwriting. Do not rate Low just because T12 is absent on a NNN deal.

MULTI-TENANT / VALUE-ADD / MULTIFAMILY:
- Cap rate <4.5% primary market = strong negative.
- Rent control markets = heavily discount pro forma.
- No T12 = Low data quality.
- Tertiary markets need 7%+ cap UNLESS investment-grade single tenant NNN (see above).
- Occupancy <88% = red flag unless explicit value-add thesis.

VERDICTS: Score 8-10 = GO · 5-7 = SOFT PASS · 1-4 = HARD PASS. Be direct and protect investor capital."""

def analyze(pdf_bytes, filename):
    client = anthropic.Anthropic(api_key=API_KEY)
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                {"type": "text", "text": PROMPT}
            ]}]
        )
        text = msg.content[0].text
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            r = json.loads(m.group())
            r['filename'] = filename
            r['status'] = 'success'
            return r
        return {'filename': filename, 'status': 'error', 'error': 'Could not parse response'}
    except Exception as e:
        return {'filename': filename, 'status': 'error', 'error': str(e)}

def vcls(v):   return {'GO':'c-go','SOFT PASS':'c-soft','HARD PASS':'c-hard'}.get(v,'c-soft')
def vstrp(v):  return {'GO':'s-go','SOFT PASS':'s-soft','HARD PASS':'s-hard'}.get(v,'s-soft')
def vbtn(v):   return {'GO':'v-go','SOFT PASS':'v-soft','HARD PASS':'v-hard'}.get(v,'v-soft')
def vcol(v):   return {'GO':'#00FF9F','SOFT PASS':'#FFB800','HARD PASS':'#FF4757'}.get(v,'#00D2FF')
def dqcol(d):  return {'High':'#00FF9F','Medium':'#FFB800','Low':'#FF4757'}.get(d,'#888')
def rank_lbl(i): return {1:'🥇 Top Pick',2:'🥈 Second Look',3:'🥉 Third'}.get(i,f'#{i}')
def rank_sty(i):
    s={1:'background:rgba(0,255,159,0.08);color:rgba(0,255,159,0.65);border-color:rgba(0,255,159,0.2);',
       2:'background:rgba(0,210,255,0.06);color:rgba(0,210,255,0.55);border-color:rgba(0,210,255,0.15);',
       3:'background:rgba(255,255,255,0.04);color:rgba(232,244,248,0.35);border-color:rgba(255,255,255,0.08);'}
    return s.get(i,s[3])

def build_card_html(deal, rank):
    v = deal.get('verdict','SOFT PASS')
    s = deal.get('score', 0)
    sc = vcol(v)
    dq = deal.get('data_quality','Medium')
    dqc = dqcol(dq)
    flags = ''.join([f'<div class="flag"><div class="fdot"></div>{f}</div>' for f in deal.get('red_flags',[])])
    metrics = ''.join([
        f'<div class="m-chip">{k}<b>{val}</b></div>'
        for k,val in [
            ("Price", deal.get('asking_price')),
            ("Cap Rate", deal.get('cap_rate')),
            ("NOI", deal.get('noi')),
            ("Occupancy", deal.get('occupancy')),
            ("Units", deal.get('unit_count')),
            ("$/Unit", deal.get('price_per_unit')),
            ("Built", deal.get('year_built')),
            ("Market", deal.get('market_tier')),
        ] if val and val not in ('N/A','Not disclosed','')
    ])
    return f"""
    {CARD_CSS}
    <div class="deal-card {vcls(v)}" style="animation-delay:{rank*0.1}s">
        <div class="card-stripe {vstrp(v)}"></div>
        <div class="top-row">
            <div class="top-left">
                <div class="rank-pill" style="{rank_sty(rank)}">{rank_lbl(rank)}</div>
                <div class="prop-name">{deal.get('deal_name','Unknown Property')}</div>
                <div class="prop-meta">📍 {deal.get('location','N/A')} &nbsp;·&nbsp; {deal.get('asset_class','N/A')}</div>
                <div class="metrics-row">{metrics}</div>
            </div>
            <div class="score-wrap">
                <div class="score-circle" style="border-color:{sc};box-shadow:0 0 24px {sc}44;">
                    <div class="score-num" style="color:{sc};">{s}</div>
                    <div class="score-den">/10</div>
                </div>
                <div class="v-btn {vbtn(v)}">{v}</div>
            </div>
        </div>
        <div class="body-grid">
            <div>
                <div class="sec-label">Investment Thesis</div>
                <div class="thesis">{deal.get('investment_thesis','N/A')}</div>
                <div class="sec-label">Bull Case</div>
                <div class="bull">{deal.get('bull_case','N/A')}</div>
            </div>
            <div>
                <div class="sec-label">Red Flags</div>
                {flags or '<div style="font-size:0.84rem;color:rgba(232,244,248,0.22);">None identified</div>'}
                <div style="margin-top:1rem;">
                    <span class="dq-lbl">Data Quality</span>
                    <span class="dq-tag" style="color:{dqc};border-color:{dqc}40;background:{dqc}12;">{dq}</span>
                    <div class="dq-sub">{deal.get('data_quality_reason','')}</div>
                </div>
            </div>
        </div>
        <div class="key-q">
            <span class="kq-label">Key Question Before Proceeding</span>
            {deal.get('key_question','N/A')}
        </div>
        <div class="analyst-note">
            <b>Analyst Note:</b> {deal.get('verdict_reason','N/A')}
        </div>
    </div>
    """

TYPEWRITER_MSGS = [
    "Reading documents",
    "Extracting financial data",
    "Identifying cap rates and NOI",
    "Analyzing rent rolls",
    "Flagging lease risks",
    "Scoring market fundamentals",
    "Evaluating red flags",
    "Generating investment verdicts",
]

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ AI-Powered · First-Pass Underwriting · AcquiOS</div>
    <div class="hero-title">Deal Triage Agent</div>
    <div class="hero-sub">Upload offering memoranda and get instant investment verdicts — in seconds, not hours.</div>
</div>
<div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#00FF9F;box-shadow:0 0 6px #00FF9F88;"></div>GO — Strong fundamentals</div>
    <div class="legend-item"><div class="legend-dot" style="background:#FFB800;"></div>SOFT PASS — Mixed signals</div>
    <div class="legend-item"><div class="legend-dot" style="background:#FF4757;box-shadow:0 0 6px #FF475788;"></div>HARD PASS — High risk / low return</div>
</div>
""", unsafe_allow_html=True)

col_up, col_btn = st.columns([4, 1])
with col_up:
    st.markdown('<span class="upload-label">Offering Memoranda — PDF</span>', unsafe_allow_html=True)
    files = st.file_uploader("OMs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    st.markdown('<div class="upload-hint">Multi-file upload supported · Multifamily, retail, office & industrial OMs</div>', unsafe_allow_html=True)
with col_btn:
    st.markdown('<span class="upload-label">&nbsp;</span>', unsafe_allow_html=True)
    run = st.button("Analyze Deals →")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

if run:
    if not files:
        st.markdown('<div class="err">⚠ Please upload at least one Offering Memorandum PDF.</div>', unsafe_allow_html=True)
    else:
        results = []
        loader = st.empty()

        for i, f in enumerate(files):
            # Cycle typewriter messages while analyzing
            msg_i = 0
            loader.markdown(f"""
            <div class="loader-wrap">
                <div class="loader-status">{TYPEWRITER_MSGS[0]}<span class="loader-cursor"></span></div>
                <div class="loader-sub">Analyzing {f.name} · Deal {i+1} of {len(files)}</div>
            </div>
            """, unsafe_allow_html=True)
            result = analyze(f.read(), f.name)
            results.append(result)

        loader.markdown("""
        <div class="loader-wrap">
            <div class="loader-complete">✦ Analysis Complete — Verdicts Ready</div>
            <div class="loader-sub" style="margin-top:0.5rem;">Rendering investment briefs below</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1.0)
        loader.empty()

        good = sorted([r for r in results if r.get('status')=='success'], key=lambda x: x.get('score',0), reverse=True)
        bad  = [r for r in results if r.get('status')=='error']

        go_n   = sum(1 for r in good if r.get('verdict')=='GO')
        soft_n = sum(1 for r in good if r.get('verdict')=='SOFT PASS')
        hard_n = sum(1 for r in good if r.get('verdict')=='HARD PASS')
        avg    = round(sum(r.get('score',0) for r in good)/len(good),1) if good else 0

        st.markdown(f"""
        <div class="summary-bar">
            <div class="s-stat"><div class="s-val" style="background:linear-gradient(135deg,#fff,#00D2FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(good)}</div><div class="s-lbl">Deals Analyzed</div></div>
            <div class="s-stat"><div class="s-val" style="background:linear-gradient(135deg,#00FF9F,#00D2FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{go_n}</div><div class="s-lbl">Go</div></div>
            <div class="s-stat"><div class="s-val" style="background:linear-gradient(135deg,#FFB800,#FF6B00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{soft_n}</div><div class="s-lbl">Soft Pass</div></div>
            <div class="s-stat"><div class="s-val" style="background:linear-gradient(135deg,#FF4757,#FF2D55);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{hard_n}</div><div class="s-lbl">Hard Pass</div></div>
            <div class="s-stat"><div class="s-val" style="background:linear-gradient(135deg,#fff,#00D2FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{avg}</div><div class="s-lbl">Avg Score</div></div>
        </div>
        """, unsafe_allow_html=True)

        for i, deal in enumerate(good + bad, 1):
            if deal.get('status') == 'error':
                st.markdown(f'<div class="err">⚠ Failed: <b>{deal["filename"]}</b> — {deal.get("error","Unknown")}</div>', unsafe_allow_html=True)
                continue
            # Estimate card height based on content
            flag_count = len(deal.get('red_flags', []))
            card_height = 620 + (flag_count * 60)
            components.html(build_card_html(deal, i), height=card_height, scrolling=False)

        st.markdown('<div class="footer">Deal Triage Agent &nbsp;·&nbsp; Powered by Claude &nbsp;·&nbsp; Built for AcquiOS</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty">
        <div class="empty-icon">⚡</div>
        <div class="empty-t">Ready to triage your deals</div>
        <div class="empty-s">Upload OMs above and click Analyze</div>
    </div>
    """, unsafe_allow_html=True)