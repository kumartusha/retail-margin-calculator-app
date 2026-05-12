import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inventory Margin Calculator",
    page_icon="🚗",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 780px !important;
}

/* ── Page header ── */
.page-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 2rem;
}
.page-header-icon {
    width: 48px; height: 48px;
    background: #0F172A;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}
.page-header h1 {
    font-size: 22px !important;
    font-weight: 600 !important;
    color: #0F172A !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}
.page-header p {
    font-size: 13px;
    color: #64748B;
    margin: 2px 0 0 !important;
}

/* ── Search box ── */
.search-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748B;
    margin-bottom: 6px;
}

div[data-testid="stTextInput"] input {
    font-family: 'DM Mono', monospace !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    background: #FFFFFF !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 0 16px !important;
    height: 48px !important;
    color: #0F172A !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

/* ── Primary button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    height: 48px !important;
    padding: 0 28px !important;
    transition: opacity 0.15s, transform 0.1s !important;
    letter-spacing: 0.01em !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary button ── */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #3B82F6 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    height: 48px !important;
    padding: 0 28px !important;
    width: 100% !important;
    transition: background 0.15s, transform 0.1s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #2563EB !important;
    transform: translateY(-1px) !important;
}

/* ── Number input ── */
div[data-testid="stNumberInput"] input {
    font-family: 'DM Mono', monospace !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    background: #FFFFFF !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

/* ── Vehicle card ── */
.vehicle-card {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    animation: fadeUp 0.3s ease;
}
.vehicle-card-header {
    background: #0F172A;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.vch-left { display: flex; flex-direction: column; gap: 4px; }
.vch-reg {
    font-family: 'DM Mono', monospace;
    font-size: 22px;
    font-weight: 500;
    color: #FFFFFF;
    letter-spacing: 0.06em;
}
.vch-seller { font-size: 13px; color: #94A3B8; }
.vch-badge {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 20px;
}
.badge-ats    { background: #D1FAE5; color: #065F46; }
.badge-booked { background: #DBEAFE; color: #1E40AF; }

.vehicle-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    border-top: 1.5px solid #E2E8F0;
}
.vg-cell {
    padding: 18px 20px;
    border-right: 1.5px solid #E2E8F0;
    border-bottom: 1.5px solid #E2E8F0;
}
.vg-cell:nth-child(3n) { border-right: none; }
.vg-cell:nth-last-child(-n+3) { border-bottom: none; }
.vg-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 6px;
}
.vg-value {
    font-size: 15px;
    font-weight: 500;
    color: #0F172A;
}
.vg-value.mono { font-family: 'DM Mono', monospace; font-size: 14px; }
.vg-value.blue { color: #2563EB; }
.vg-value.green { color: #059669; }
.vg-value.red   { color: #DC2626; }

/* ── Calc section ── */
.calc-card {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.calc-card-header {
    padding: 16px 24px;
    border-bottom: 1.5px solid #E2E8F0;
    display: flex;
    align-items: center;
    gap: 10px;
    background: #F8FAFC;
}
.calc-card-header .ch-icon { font-size: 18px; }
.calc-card-header .ch-title {
    font-size: 14px;
    font-weight: 600;
    color: #0F172A;
}
.calc-card-body { padding: 20px 24px; }

/* ── Margin result pill ── */
.margin-result {
    margin-top: 1.25rem;
    border-radius: 14px;
    padding: 24px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    animation: fadeUp 0.25s ease;
}
.margin-result.positive {
    background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    border: 1.5px solid #6EE7B7;
}
.margin-result.negative {
    background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%);
    border: 1.5px solid #FCA5A5;
}
.mr-left { display: flex; flex-direction: column; gap: 4px; }
.mr-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.margin-result.positive .mr-label { color: #065F46; }
.margin-result.negative .mr-label { color: #9F1239; }
.mr-note {
    font-size: 12px;
}
.margin-result.positive .mr-note { color: #059669; }
.margin-result.negative .mr-note { color: #DC2626; }
.mr-value {
    font-family: 'DM Mono', monospace;
    font-size: 42px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: -0.02em;
}
.margin-result.positive .mr-value { color: #059669; }
.margin-result.negative .mr-value { color: #DC2626; }

/* ── Alerts ── */
.custom-alert {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 13px;
    margin-top: 10px;
    line-height: 1.5;
}
.alert-warn { background: #FFFBEB; border: 1.5px solid #FCD34D; color: #92400E; }
.alert-info { background: #EFF6FF; border: 1.5px solid #93C5FD; color: #1E40AF; }
.alert-err  { background: #FEF2F2; border: 1.5px solid #FCA5A5; color: #991B1B; }

/* ── Divider ── */
.styled-divider {
    border: none;
    border-top: 1.5px solid #E2E8F0;
    margin: 1.75rem 0;
}

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_inr(value):
    """Format a number as Indian Rupees."""
    try:
        n = int(round(float(str(value).replace(',', '').strip())))
        s = f"{abs(n):,}"
        # Convert to Indian comma format
        parts = s.split(',')
        if len(parts) > 1:
            last = parts[-1]
            rest = ','.join(parts[:-1])
            # rebuild with Indian grouping
            pass
        return f"₹{n:,.0f}"
    except Exception:
        return str(value)


def safe_float(val):
    try:
        return float(str(val).replace(',', '').strip())
    except Exception:
        return 0.0


def margin_color_class(pct: float) -> str:
    return "green" if pct >= 0 else "red"


# ── Google Sheets ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def get_sheet_data():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        try:
            creds_dict = json.loads(st.secrets["google_credentials"])
        except Exception:
            with open('service_account.json', 'r') as f:
                creds_dict = json.load(f)

        credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
        gc = gspread.authorize(credentials)
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        sheet = gc.open_by_key(spreadsheet_id).worksheet("Procurment_Backup")
        all_data = sheet.get_all_values()

        headers = all_data[0]
        seen = {}
        unique_headers = []
        for h in headers:
            if h in seen:
                seen[h] += 1
                unique_headers.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 1
                unique_headers.append(h)

        return pd.DataFrame(all_data[1:], columns=unique_headers)
    except Exception as e:
        return None, str(e)


def resolve_columns(result: pd.DataFrame):
    """Return a dict mapping logical names → actual column names."""
    cols = result.columns
    mapping = {}

    if len(cols) > 34:
        mapping['concat_rank']    = cols[28]
        mapping['final_mmvf']     = cols[34]
        mapping['expected_sp']    = cols[26]
        mapping['margin_pct']     = cols[27]
        mapping['seller_name']    = cols[10]
        mapping['ageing']         = cols[6]
        mapping['auction_status'] = cols[23]

    for col in cols:
        c = str(col)
        if 'Final Auction Won Status' in c:
            mapping['auction_status'] = col
        if 'New Landed Cost' in c:
            mapping['landed_cost'] = col
        if 'Procurement Price' in c:
            mapping['procurement_price'] = col

    return mapping


# ── Session state init ────────────────────────────────────────────────────────
for key in ('vehicle_row', 'col_map', 'calc_done', 'calc_result'):
    if key not in st.session_state:
        st.session_state[key] = None
st.session_state.setdefault('calc_done', False)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">🚗</div>
  <div>
    <h1>Inventory Margin Calculator</h1>
    <p>Search by registration number · Instant margin analysis</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="search-label">Registration number</div>', unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1.2])
with col_input:
    registration_number = st.text_input(
        label="reg",
        label_visibility="collapsed",
        placeholder="e.g. MH02AB1234",
        key="reg_input",
    )
with col_btn:
    search_clicked = st.button("Search →", type="primary", use_container_width=True)

# ── Run search ────────────────────────────────────────────────────────────────
if search_clicked:
    st.session_state.vehicle_row = None
    st.session_state.calc_done = False

    if not registration_number.strip():
        st.markdown("""<div class="custom-alert alert-warn">
            ⚠️ Please enter a registration number before searching.
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Fetching vehicle data…"):
            result = get_sheet_data()

        if result is None or (isinstance(result, tuple)):
            err = result[1] if isinstance(result, tuple) else "Unknown error"
            st.markdown(f"""<div class="custom-alert alert-err">
                ❌ Could not connect to Google Sheets: {err}
            </div>""", unsafe_allow_html=True)
        elif result.empty:
            st.markdown("""<div class="custom-alert alert-err">
                ❌ The sheet returned no data. Please check your credentials.
            </div>""", unsafe_allow_html=True)
        else:
            matched = result[
                result.apply(
                    lambda row: registration_number.strip().upper() in str(row.values).upper(),
                    axis=1,
                )
            ]
            col_map = resolve_columns(matched) if not matched.empty else {}

            # Filter to ATS / BOOKED only
            if col_map.get('auction_status') and not matched.empty:
                matched = matched[
                    matched[col_map['auction_status']].str.upper().isin(['ATS', 'BOOKED'])
                ]

            if matched.empty:
                st.markdown(f"""<div class="custom-alert alert-warn">
                    ⚠️ No ATS/Booked record found for <strong>{registration_number.upper()}</strong>.
                </div>""", unsafe_allow_html=True)
            else:
                st.session_state.vehicle_row = matched.iloc[0]
                st.session_state.col_map = col_map


# ═══════════════════════════════════════════════════════════════════════════════
#  VEHICLE CARD
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.vehicle_row is not None:
    row = st.session_state.vehicle_row
    cm  = st.session_state.col_map

    def get(key, fallback="—"):
        col = cm.get(key)
        if col is None:
            return fallback
        v = row.get(col, fallback)
        return v if str(v).strip() not in ("", "nan", "None") else fallback

    # ── Margin with 2% reduction ──
    raw_margin = get('margin_pct', '0')
    try:
        margin_adj = round(safe_float(str(raw_margin).replace('%', '')) - 2, 2)
        margin_display = f"{'+' if margin_adj >= 0 else ''}{margin_adj}%"
        margin_class = margin_color_class(margin_adj)
    except Exception:
        margin_display = raw_margin
        margin_class = "blue"

    # ── Status badge ──
    status = get('auction_status', 'ATS').upper()
    badge_class = "badge-ats" if status == "ATS" else "badge-booked"

    st.markdown(f"""
    <div class="vehicle-card">
      <div class="vehicle-card-header">
        <div class="vch-left">
          <div class="vch-reg">{registration_number.upper()}</div>
          <div class="vch-seller">{get('seller_name')}</div>
        </div>
        <span class="vch-badge {badge_class}">{status}</span>
      </div>
      <div class="vehicle-grid">
        <div class="vg-cell">
          <div class="vg-label">Rank &amp; Vehicle</div>
          <div class="vg-value mono">{get('concat_rank')}</div>
        </div>
        <div class="vg-cell">
          <div class="vg-label">Final MMVF</div>
          <div class="vg-value blue">{get('final_mmvf')}</div>
        </div>
        <div class="vg-cell">
          <div class="vg-label">Expected Selling Price</div>
          <div class="vg-value">{get('expected_sp')}</div>
        </div>
        <div class="vg-cell">
          <div class="vg-label">Margin %</div>
          <div class="vg-value {margin_class}">{margin_display}</div>
        </div>
        <div class="vg-cell">
          <div class="vg-label">Ageing</div>
          <div class="vg-value">{get('ageing')}</div>
        </div>
        <div class="vg-cell">
          <div class="vg-label">Auction Status</div>
          <div class="vg-value">{status}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    #  MARGIN CALCULATOR
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="calc-card">
      <div class="calc-card-header">
        <span class="ch-icon">🧮</span>
        <span class="ch-title">Calculate expected margin</span>
      </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="calc-card-body">', unsafe_allow_html=True)

    price_col, calc_col = st.columns([3, 1])
    with price_col:
        user_price = st.number_input(
            "Your selling price (₹)",
            min_value=0.0,
            step=1000.0,
            format="%.0f",
            placeholder="e.g. 575000",
            key="user_price",
            label_visibility="visible",
        )
    with calc_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        calc_clicked = st.button("Calculate", type="secondary", use_container_width=True)

    if calc_clicked:
        if user_price <= 0:
            st.markdown("""<div class="custom-alert alert-warn">
                ⚠️ Please enter a valid selling price greater than ₹0.
            </div>""", unsafe_allow_html=True)
            st.session_state.calc_done = False
        else:
            y_val = safe_float(get('landed_cost',       '0'))
            z_val = safe_float(get('procurement_price', '0'))

            margin_for_gst   = user_price - z_val
            gst_amount       = margin_for_gst - (margin_for_gst / 1.18)
            margin_net_gst   = user_price - y_val - gst_amount
            denom            = user_price - gst_amount

            if denom == 0:
                st.markdown("""<div class="custom-alert alert-err">
                    ❌ Cannot calculate — division by zero encountered.
                </div>""", unsafe_allow_html=True)
                st.session_state.calc_done = False
            else:
                expected = round((margin_net_gst / denom) * 100 - 2, 2)
                st.session_state.calc_result = {
                    'price':          user_price,
                    'z_val':          z_val,
                    'y_val':          y_val,
                    'margin_for_gst': margin_for_gst,
                    'gst_amount':     gst_amount,
                    'margin_net_gst': margin_net_gst,
                    'expected':       expected,
                }
                st.session_state.calc_done = True

    st.markdown("</div></div>", unsafe_allow_html=True)  # close calc-card-body + calc-card

    # ── Result display ────────────────────────────────────────────────────────
    if st.session_state.calc_done and st.session_state.calc_result:
        r = st.session_state.calc_result
        exp   = r['expected']
        sign  = "+" if exp >= 0 else ""
        m_cls = margin_color_class(exp)

        pill_cls  = "positive" if exp >= 0 else "negative"
        note_text = "Healthy margin — good to go ✓" if exp >= 0 else "Below target — review pricing ✗"

        st.markdown(f"""
        <div class="margin-result {pill_cls}">
          <div class="mr-left">
            <div class="mr-label" style="font-size: 14px;">Expected margin</div>
            <!-- <div class="mr-note">{note_text}</div> -->
          </div>
          <div class="mr-value">{sign}{exp}%</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer note ───────────────────────────────────────────────────────────────
st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
# st.markdown("""<div class="custom-alert alert-info">
#     💡 Data is fetched securely via Google Sheets service account authentication.
#     Results show only ATS / Booked vehicles. Margin % is displayed net of a 2% adjustment.
# </div>""", unsafe_allow_html=True)