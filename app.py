import streamlit as st
import fastf1
import fastf1.plotting
import fastf1.utils
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ─────────────────────────────────────────────────────────────────
# SAYFA YAPILANDIRMASI
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Telemetry Analysis Tool",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS: Koyu tema fine-tuning ve sekme stilleri
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0d0d0d; }
    .block-container { padding-top: 1rem; }
    div[data-testid="stTabs"] button {
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 1.2rem;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 3px solid #ff1801 !important;
        color: #ff1801 !important;
    }
    .f1-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .f1-table th { background: #1a1a1a; color: #ff1801; padding: 10px 14px;
                   text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #333; }
    .f1-table td { padding: 9px 14px; border-bottom: 1px solid #222; color: #e0e0e0; }
    .f1-table tr:hover td { background: rgba(255,24,1,0.06); }
    .pill { display:inline-block; border-radius:4px; padding:2px 10px;
            font-weight:700; font-size:0.78rem; letter-spacing:.04em; }
    .metric-card { background:#111; border:1px solid #222; border-radius:10px;
                   padding:14px 18px; margin:6px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# FastF1 ÖNBELLEK
# ─────────────────────────────────────────────────────────────────
if not os.path.exists("cache"):
    os.makedirs("cache")
fastf1.Cache.enable_cache("cache")

# ─────────────────────────────────────────────────────────────────
# BAŞLIK
# ─────────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([1, 6, 1])
with h1:
    st.markdown("<h1 style='text-align:right;font-size:2.8rem;margin:0'>🏎️</h1>", unsafe_allow_html=True)
with h2:
    st.markdown("""
    <h1 style='text-align:center;color:#ff1801;font-family:Inter,sans-serif;
        font-weight:900;letter-spacing:0.04em;margin:0;font-size:2rem;'>
        F1 TELEMETRY ANALYSIS TOOL
    </h1>
    <p style='text-align:center;color:#666;margin:0;font-size:0.85rem;'>
        Professional Race Data Intelligence Platform
    </p>
    """, unsafe_allow_html=True)
with h3:
    st.markdown("<h1 style='text-align:left;font-size:2.8rem;margin:0'>🏁</h1>", unsafe_allow_html=True)

st.markdown("<hr style='border:0;border-top:1px solid #2a2a2a;margin:12px 0 16px'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# SOL KENAR ÇUBUĞU (SIDEBAR)
# ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🕹️ Kontrol Paneli")

current_year = pd.Timestamp.now().year
years = list(range(2020, current_year + 1))[::-1]
sessions = {
    '1. Antrenman': 'FP1', '2. Antrenman': 'FP2', '3. Antrenman': 'FP3',
    'Sıralama (Quali)': 'Q', 'Sprint': 'S', 'Yarış (Race)': 'R'
}

selected_year = st.sidebar.selectbox("🗓️ Sezon (Yıl)", years)
selected_gp   = st.sidebar.text_input("🏟️ Grand Prix (Pist / Ülke)", value="Bahrain")
selected_session_name = st.sidebar.selectbox("📡 Seans", list(sessions.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("#### 👤 Pilot Karşılaştırma")
driver1 = st.sidebar.text_input("1. Pilot (örn: VER)", value="VER").upper()
driver2 = st.sidebar.text_input("2. Pilot (örn: NOR)", value="NOR").upper()

load_button = st.sidebar.button("🚀 Telemetriyi Yükle", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size:0.75rem;color:#555;line-height:1.6'>
<b>İpucu:</b> Yıl + GP adı + Seans seçin.<br>
Pilot kısaltmaları büyük harf olmalı.<br>
İlk yükleme 1-2 dakika sürebilir.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_session_data(year, gp, session_identifier):
    """FastF1 üzerinden seans verisini çek ve önbellekte sakla."""
    try:
        session = fastf1.get_session(year, gp, session_identifier)
        session.load()
        return session
    except Exception as e:
        return str(e)


# F1 takımlarının güvenilir renk paleti (FastF1 yanlış renk dönerse fallback)
F1_TEAM_COLORS = {
    'red bull': '#3671C6', 'redbull': '#3671C6', 'red bull racing': '#3671C6',
    'ferrari': '#E8002D', 'scuderia ferrari': '#E8002D',
    'mercedes': '#27F4D2', 'mercedes amg': '#27F4D2',
    'mclaren': '#FF8000', 'mclaren f1': '#FF8000',
    'aston martin': '#229971', 'aston martin f1': '#229971',
    'alpine': '#FF87BC', 'bwt alpine': '#FF87BC',
    'williams': '#64C4FF', 'williams racing': '#64C4FF',
    'haas': '#B6BABD', 'haas f1': '#B6BABD', 'haas f1 team': '#B6BABD',
    'racing bulls': '#6692FF', 'rb': '#6692FF', 'alphatauri': '#6692FF',
    'kick sauber': '#52E252', 'sauber': '#52E252', 'alfa romeo': '#C92D4B',
}

# Yedek kontrast renk paleti: hiçbir yöntem işe yaramazsa bu renkler kullanılır
FALLBACK_PALETTE = ['#FF3333', '#3399FF', '#33FF99', '#FF9900', '#CC33FF', '#FFFF00']


def hex_to_rgb(h):
    """#RRGGBB → (R, G, B) tuple."""
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def color_similarity(h1, h2):
    """İki renk arasındaki Öklid mesafesi (0-441 arası). 80 altı çok benzer."""
    try:
        r1, g1, b1 = hex_to_rgb(h1)
        r2, g2, b2 = hex_to_rgb(h2)
        return ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) ** 0.5
    except:
        return 0


def driver_color(abbr, team_name=''):
    """Pilot rengini en güvenilir kaynaktan al.
    Öncelik: 1) F1_TEAM_COLORS tablosu  2) FastF1 driver_color  3) beyaz
    """
    # Önce takım adına göre tablomuzdan ara
    if team_name:
        key = team_name.lower().strip()
        for k, v in F1_TEAM_COLORS.items():
            if k in key or key in k:
                return v
    # FastF1'e sor
    try:
        fastf1.plotting.setup_mpl(misc_mpl_mods=False)
        return fastf1.plotting.driver_color(abbr)
    except:
        return '#ffffff'


def safe_tolist(series):
    """Pandas/FastF1 serisini temiz Python listesine çevir."""
    return [float(v) if not isinstance(v, bool) else v for v in series.tolist()]


# Lastik renk paleti
TYRE_COLORS = {
    "SOFT":   "#e8002d",
    "MEDIUM": "#ffd700",
    "HARD":   "#f0f0f0",
    "INTER":  "#39b54a",
    "WET":    "#0067ff",
}
TYRE_LABELS = {
    "SOFT": "S", "MEDIUM": "M", "HARD": "H", "INTER": "I", "WET": "W"
}

# ─────────────────────────────────────────────────────────────────
# ANA UYGULAMA — veri yüklendikten sonra çalışır
# ─────────────────────────────────────────────────────────────────

if load_button:
    with st.spinner(f"⏳ {selected_year} {selected_gp} — {selected_session_name} yükleniyor..."):
        sess_id = sessions[selected_session_name]
        session = load_session_data(selected_year, selected_gp, sess_id)

    if isinstance(session, str):
        st.error(f"❌ Veri çekilemedi. GP adını veya yılı kontrol edin.\n\n`{session}`")
        st.stop()

    st.success(f"✅ {selected_year} {selected_gp} — {selected_session_name} verisi yüklendi!")

    # ── Ortak telemetri verilerini hazırla ──────────────────────
    try:
        laps_d1 = session.laps.pick_driver(driver1)
        laps_d2 = session.laps.pick_driver(driver2)
        fastest_d1 = laps_d1.pick_fastest()
        fastest_d2 = laps_d2.pick_fastest()
        tel_d1 = fastest_d1.get_telemetry().add_distance()
        tel_d2 = fastest_d2.get_telemetry().add_distance()

        # Takım adlarını results'tan çek (renk için en güvenilir kaynak)
        results_data = session.results
        def get_team(abbr):
            try:
                row = results_data[results_data['Abbreviation'] == abbr].iloc[0]
                return row.get('TeamName', '')
            except:
                return ''

        team1 = get_team(driver1)
        team2 = get_team(driver2)

        # Önce results'taki TeamColor'u dene (6 haneli hex, # olmadan saklanır)
        def color_from_results(abbr):
            try:
                row = results_data[results_data['Abbreviation'] == abbr].iloc[0]
                tc = str(row.get('TeamColor', '')).strip()
                if tc and tc not in ('', 'nan') and len(tc) >= 3:
                    return f'#{tc}' if not tc.startswith('#') else tc
            except:
                pass
            return None

        c1 = color_from_results(driver1) or driver_color(driver1, team1)
        c2 = color_from_results(driver2) or driver_color(driver2, team2)

        # Eğer iki renk birbirine çok benziyorsa (mesafe < 80) fallback renkler ata
        if color_similarity(c1, c2) < 80:
            # Takım rengini tablomuzdan almayı tekrar dene
            t1_color = driver_color(driver1, team1)
            t2_color = driver_color(driver2, team2)
            if color_similarity(t1_color, t2_color) >= 80:
                c1, c2 = t1_color, t2_color
            else:
                # Son çare: sabit kontrast renk çifti
                c1 = FALLBACK_PALETTE[0]
                c2 = FALLBACK_PALETTE[1]

    except Exception as e:
        st.error(f"❌ Pilot verileri işlenemedi: `{e}`\nPilot kısaltmalarını doğru yazdığınızdan emin olun.")
        st.stop()

    # ── 5 ANA SEKME ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Yarış Merkezi",
        "📊 Detaylı Telemetri",
        "🛣️ Yarış Çizgisi & G-Kuvveti",
        "🔥 Isı Haritaları",
        "🔧 Strateji & Lastik"
    ])

    # ═══════════════════════════════════════════════════════════════
    # SEKME 1 — YARIŞ MERKEZİ
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.subheader(f"🏆 {selected_year} {selected_gp} — {selected_session_name} Sonuçları")

        try:
            results = session.results.copy()
            if results is not None and not results.empty:

                # ── Pozisyon sütununu akıllıca belirle ──────────────
                # FastF1, yeni yarışlarda Ergast verisini henüz alamaz.
                # Öncelik sırası: Position → ClassifiedPosition → GridPosition → tur bazlı hız sırası
                def resolve_position(r):
                    for col in ['Position', 'ClassifiedPosition', 'GridPosition']:
                        val = r.get(col)
                        if val is not None and pd.notna(val) and str(val).strip() not in ('', 'nan'):
                            try:
                                return int(float(val))
                            except:
                                pass
                    return None

                results['_pos'] = results.apply(resolve_position, axis=1)

                # Eğer hâlâ hiç pozisyon yoksa, tur verilerinden en hızlı sıralamayı infer et
                if results['_pos'].isna().all():
                    try:
                        # Her pilotun en iyi turunu al, hıza göre sırala
                        best_laps = (
                            session.laps
                            .pick_quicklaps()
                            .groupby('Driver')['LapTime']
                            .min()
                            .reset_index()
                            .sort_values('LapTime')
                            .reset_index(drop=True)
                        )
                        best_laps['_inferred_pos'] = best_laps.index + 1
                        pos_map = dict(zip(best_laps['Driver'], best_laps['_inferred_pos']))
                        results['_pos'] = results['Abbreviation'].map(pos_map)
                        data_note = "⚠️ Resmi sıralama henüz mevcut değil — en hızlı laplara göre sıralandı."
                    except:
                        data_note = "⚠️ Resmi sıralama henüz mevcut değil."
                else:
                    data_note = None

                results = results.sort_values('_pos', na_position='last')

                # ── Süre sütununu belirle ───────────────────────────
                # Her satır için en uygun zaman verisini seç
                def resolve_time(r):
                    for tcol in ['Time', 'Q3', 'Q2', 'Q1']:
                        val = r.get(tcol)
                        if val is not None and pd.notna(val):
                            try:
                                s = str(val).split('days ')[-1]
                                return s[:11].lstrip('0:') or '0.000'
                            except:
                                pass
                    # Tur verisinden en hızlı lap süresini al
                    try:
                        drv_laps = session.laps.pick_driver(r['Abbreviation']).pick_quicklaps()
                        if not drv_laps.empty:
                            best = drv_laps['LapTime'].min()
                            total_s = best.total_seconds()
                            mins = int(total_s // 60)
                            secs = total_s % 60
                            return f"{mins}:{secs:06.3f}"
                    except:
                        pass
                    return '—'

                # ── Seans Sonuç Tablosu ──────────────────────────
                st.markdown("#### 📋 Seans Sıralaması")
                if data_note:
                    st.info(data_note)

                rows_html = ""
                for enum_idx, (_, row) in enumerate(results.iterrows()):
                    pos_val = row.get('_pos')
                    pos_disp = int(pos_val) if pd.notna(pos_val) else enum_idx + 1
                    abbr = row.get('Abbreviation', '')
                    full_name = f"{row.get('FirstName','')} {row.get('LastName','')}".strip()
                    team = row.get('TeamName', '')

                    # Takım rengini önce results'tan, yoksa plotting'den al
                    tc = '#444'
                    raw_tc = row.get('TeamColor', '')
                    if raw_tc and str(raw_tc) not in ('', 'nan'):
                        tc = f"#{raw_tc}" if not str(raw_tc).startswith('#') else str(raw_tc)
                    else:
                        try:
                            tc = fastf1.plotting.team_color(team)
                        except:
                            pass

                    t_col = resolve_time(row)

                    pts = row.get('Points')
                    pts_str = f"<b>{int(float(pts))}</b> pt" if pts and pd.notna(pts) and float(pts) > 0 else ''

                    # P1 P2 P3 için özel renk
                    pos_style = 'color:#ff1801'
                    if pos_disp == 1: pos_style = 'color:#ffd700'
                    elif pos_disp == 2: pos_style = 'color:#c0c0c0'
                    elif pos_disp == 3: pos_style = 'color:#cd7f32'

                    rows_html += f"""
                    <tr>
                        <td style='text-align:center;font-weight:900;font-size:1.05rem;{pos_style}'>{pos_disp}</td>
                        <td><span class='pill' style='background:{tc}25;border:1px solid {tc};color:{tc}'>{abbr}</span></td>
                        <td style='font-weight:600'>{full_name}</td>
                        <td style='color:#888;font-size:0.85rem'>{team}</td>
                        <td style='font-family:monospace;color:#ddd'>{t_col}</td>
                        <td style='color:#ffd700'>{pts_str}</td>
                    </tr>"""

                st.markdown(f"""
                <table class='f1-table'>
                    <thead><tr>
                        <th>P</th><th>Kod</th><th>Pilot</th><th>Takım</th><th>En İyi Süre</th><th>Puan</th>
                    </tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """, unsafe_allow_html=True)
            else:
                st.info("Bu seans için sonuç verisi bulunamadı.")
        except Exception as e:
            st.warning(f"Sonuç tablosu yüklenemedi: `{e}`")
            import traceback; st.code(traceback.format_exc(), language='text')

        # ── Pilot Özet Metrikleri ────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Seçili Pilotlar — Hızlı Özet")
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
            <div class='metric-card' style='border-left:4px solid {c1}'>
                <div style='color:{c1};font-weight:700;font-size:1.1rem'>{driver1}</div>
                <div>En Hızlı Tur: <b style='font-family:monospace'>{fastest_d1['LapTime']}</b></div>
                <div style='color:#666;font-size:0.8rem'>Tur #{int(fastest_d1['LapNumber']) if pd.notna(fastest_d1['LapNumber']) else '—'}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='metric-card' style='border-left:4px solid {c2}'>
                <div style='color:{c2};font-weight:700;font-size:1.1rem'>{driver2}</div>
                <div>En Hızlı Tur: <b style='font-family:monospace'>{fastest_d2['LapTime']}</b></div>
                <div style='color:#666;font-size:0.8rem'>Tur #{int(fastest_d2['LapNumber']) if pd.notna(fastest_d2['LapNumber']) else '—'}</div>
            </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SEKME 2 — DETAYLI TELEMETRİ + DELTA TIME
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.subheader(f"📊 {driver1} vs {driver2} — Viraj Viraj Karşılaştırma")

        # ── Delta Time Hesaplama ──────────────────────────────────
        # fastf1.utils.delta_time: Her mesafe noktasında Pilot1'in Pilot2'ye göre
        # kaç saniye önde/geride olduğunu hesaplar.
        # Pozitif değer → Pilot1 geride (yavaş), Negatif değer → Pilot1 önde (hızlı)
        try:
            delta_time, ref_car, comp_car = fastf1.utils.delta_time(fastest_d1, fastest_d2)
            # ref_car: Pilot1 telemetrisi (mesafe referanslı)
            # delta_time: Saniye cinsinden zaman farkı dizisi
            has_delta = True
        except Exception as delta_err:
            has_delta = False
            delta_warn = str(delta_err)

        # 4 grafik: Delta, Hız, Gaz, Fren
        rows_count = 4 if has_delta else 3
        subplot_titles_list = []
        if has_delta:
            subplot_titles_list.append(f'⏱ Zaman Farkı (Delta): {driver1} - {driver2}  (sn)')
        subplot_titles_list += ['🚀 Hız (km/h)', '⛽ Gaz Pedalı (%)', '🛑 Fren']

        fig_tel = make_subplots(
            rows=rows_count, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.18, 0.34, 0.24, 0.24] if has_delta else [0.4, 0.3, 0.3],
            subplot_titles=subplot_titles_list
        )

        row_offset = 1
        if has_delta:
            # Delta zaman çizgisi — Y=0 referans çizgisi ile birlikte
            delta_y = delta_time.tolist() if hasattr(delta_time, 'tolist') else list(delta_time)
            ref_x   = ref_car['Distance'].tolist()
            fig_tel.add_hline(y=0, line_color="#555", line_dash="dot", row=1, col=1)
            fig_tel.add_trace(go.Scatter(
                x=ref_x, y=delta_y,
                name="Δ Zaman",
                line=dict(color="#00e5ff", width=1.5),
                fill='tozeroy',
                fillcolor="rgba(0,229,255,0.08)"
            ), row=1, col=1)
            # Pozitif alan = Pilot2 hızlı; Negatif = Pilot1 hızlı
            row_offset = 2

        # Hız
        fig_tel.add_trace(go.Scatter(
            x=tel_d1['Distance'].tolist(), y=tel_d1['Speed'].tolist(),
            name=driver1, line=dict(color=c1, width=1.8)
        ), row=row_offset, col=1)
        fig_tel.add_trace(go.Scatter(
            x=tel_d2['Distance'].tolist(), y=tel_d2['Speed'].tolist(),
            name=driver2, line=dict(color=c2, width=1.8)
        ), row=row_offset, col=1)

        # Gaz
        fig_tel.add_trace(go.Scatter(
            x=tel_d1['Distance'].tolist(), y=tel_d1['Throttle'].tolist(),
            name=f"{driver1} Gaz", line=dict(color=c1, width=1.2), showlegend=False
        ), row=row_offset+1, col=1)
        fig_tel.add_trace(go.Scatter(
            x=tel_d2['Distance'].tolist(), y=tel_d2['Throttle'].tolist(),
            name=f"{driver2} Gaz", line=dict(color=c2, width=1.2), showlegend=False
        ), row=row_offset+1, col=1)

        # Fren
        fig_tel.add_trace(go.Scatter(
            x=tel_d1['Distance'].tolist(), y=tel_d1['Brake'].tolist(),
            name=f"{driver1} Fren", line=dict(color=c1, width=1.2), showlegend=False
        ), row=row_offset+2, col=1)
        fig_tel.add_trace(go.Scatter(
            x=tel_d2['Distance'].tolist(), y=tel_d2['Brake'].tolist(),
            name=f"{driver2} Fren", line=dict(color=c2, width=1.2), showlegend=False
        ), row=row_offset+2, col=1)

        fig_tel.update_layout(
            height=700,
            template="plotly_dark",
            paper_bgcolor="#0d0d0d",
            plot_bgcolor="#0d0d0d",
            hovermode="x unified",
            legend=dict(orientation='h', y=1.04),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        fig_tel.update_xaxes(title_text="Pist Mesafesi (metre)", row=rows_count, col=1)

        if not has_delta:
            st.warning(f"⚠️ Delta Time hesaplanamadı: `{delta_warn}`")

        st.plotly_chart(fig_tel, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════
    # SEKME 3 — YARIŞ ÇİZGİSİ & G-KUVVETİ
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        col_line, col_g = st.columns(2)

        # ── Sol: 2D Yarış Çizgisi ───────────────────────────────
        with col_line:
            st.markdown("#### 🛣️ Kuşbakışı Yarış Çizgisi (Racing Line)")
            try:
                fig_line = go.Figure()

                # ── Pist Haritası Arka Planı ────────────────────────
                # Pistʼin tam sınırlarını göstermek için, seansın TÜM turlarındaki
                # X,Y konum verilerini tek bir referans turun telometrisinden elde ediyoruz.
                # Bu sayede pist şeridinin tam görünümü kalın gri çizgi olarak arka plana çizilir.
                try:
                    # Orta sahadaki bir turu referans al (pitten çıkan/giren değil)
                    ref_lap = session.laps.pick_quicklaps().iloc[len(session.laps.pick_quicklaps())//2]
                    tel_ref = ref_lap.get_telemetry()
                    if 'X' in tel_ref.columns and tel_ref['X'].notna().any():
                        # Kalın, düşük opaklıklı gri çizgi = pist zemini
                        fig_line.add_trace(go.Scatter(
                            x=tel_ref['X'].tolist(),
                            y=tel_ref['Y'].tolist(),
                            mode='lines',
                            name='Pist',
                            line=dict(color='rgba(120,120,120,0.35)', width=16),
                            hoverinfo='skip',
                            showlegend=True
                        ))
                        # İnce beyaz merkez çizgisi
                        fig_line.add_trace(go.Scatter(
                            x=tel_ref['X'].tolist(),
                            y=tel_ref['Y'].tolist(),
                            mode='lines',
                            name='Merkez Çizgisi',
                            line=dict(color='rgba(255,255,255,0.12)', width=1, dash='dot'),
                            hoverinfo='skip',
                            showlegend=False
                        ))
                except Exception:
                    pass  # Pist arka planı alınamazsa sessizce geç

                # ── Pilot Yarış Çizgileri ───────────────────────────
                fig_line.add_trace(go.Scatter(
                    x=tel_d1['X'].tolist(), y=tel_d1['Y'].tolist(),
                    mode='lines', name=driver1,
                    line=dict(color=c1, width=2.5)
                ))
                fig_line.add_trace(go.Scatter(
                    x=tel_d2['X'].tolist(), y=tel_d2['Y'].tolist(),
                    mode='lines', name=driver2,
                    line=dict(color=c2, width=2.5)
                ))

                fig_line.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0d0d0d",
                    plot_bgcolor="#0d0d0d",
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False,
                               scaleanchor="y", scaleratio=1),
                    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation='h', y=1.05, bgcolor='rgba(0,0,0,0)')
                )
                st.plotly_chart(fig_line, use_container_width=True)
            except Exception as e:
                st.warning(f"Yarış çizgisi çizilemedi: `{e}`")

        # ── Sağ: G-Kuvveti / Kavrama Dairesi ────────────────────
        with col_g:
            st.markdown("#### ⭕ Kavrama Dairesi (G-Force / Friction Circle)")
            try:
                # G-Kuvveti hesaplama:
                # Aracın hız değişiminden ivme hesaplanır.
                # Lateral G = dV_lateral / dt ≈ (V * dYaw) / 9.81   →   burada pozisyon türevi kullanıyoruz.
                # Pratik yaklaşım: hız vektörünün yön değişiminden G hesabı.

                def compute_g_forces(tel):
                    """Telemetri datasından Lateral ve Longitudinal G hesapla."""
                    dt = tel['Time'].diff().dt.total_seconds().fillna(0.001)
                    # Boyuna ivme (Longitudinal G): Hızdaki değişim (m/s^2) → G'ye çevir
                    # Hız km/h → m/s: / 3.6
                    v_ms = tel['Speed'] / 3.6
                    long_g = (v_ms.diff() / dt) / 9.81    # m/s² → G

                    # Yanal ivme (Lateral G): X–Y pozisyonundan yön değişimi
                    dx = tel['X'].diff().fillna(0)
                    dy = tel['Y'].diff().fillna(0)
                    # Her adımdaki kurs açısı (radyan)
                    heading = np.arctan2(dy, dx)
                    # Kurs değişimi (angular rate rad/s)
                    d_heading = heading.diff() / dt
                    # Yanal ivme = V * omega (m/s * rad/s) → G
                    lat_g = (v_ms * d_heading) / 9.81

                    # Sonsuz ve aşırı değerleri temizle
                    long_g = long_g.replace([np.inf, -np.inf], np.nan).fillna(0)
                    lat_g  = lat_g.replace([np.inf, -np.inf], np.nan).fillna(0)
                    # ±5G dışını kırp (gerçekçi sınır)
                    long_g = long_g.clip(-5, 5)
                    lat_g  = lat_g.clip(-5, 5)
                    return lat_g, long_g

                lat1, lon1 = compute_g_forces(tel_d1)
                lat2, lon2 = compute_g_forces(tel_d2)

                fig_g = go.Figure()
                # Kavrama dairesi arka plan halkası
                theta = np.linspace(0, 2*np.pi, 200)
                for r in [1, 2, 3]:
                    fig_g.add_trace(go.Scatter(
                        x=(r*np.cos(theta)).tolist(), y=(r*np.sin(theta)).tolist(),
                        mode='lines', line=dict(color='#333', width=1, dash='dot'),
                        showlegend=False, hoverinfo='skip'
                    ))

                fig_g.add_trace(go.Scatter(
                    x=lat1.tolist(), y=lon1.tolist(),
                    mode='markers', name=driver1,
                    marker=dict(color=c1, size=2, opacity=0.6)
                ))
                fig_g.add_trace(go.Scatter(
                    x=lat2.tolist(), y=lon2.tolist(),
                    mode='markers', name=driver2,
                    marker=dict(color=c2, size=2, opacity=0.6)
                ))
                fig_g.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0d0d0d",
                    plot_bgcolor="#0d0d0d",
                    xaxis=dict(title="Yanal G (→ Sağ)", range=[-4, 4],
                               zeroline=True, zerolinecolor="#444"),
                    yaxis=dict(title="Boyuna G (↑ Gaz / ↓ Fren)", range=[-4, 4],
                               scaleanchor="x", scaleratio=1,
                               zeroline=True, zerolinecolor="#444"),
                    legend=dict(orientation='h', y=1.05),
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_g, use_container_width=True)
                st.caption("⬆ Gaz açık · ⬇ Fren · ➡ Sağ dönüş · ⬅ Sol dönüş")
            except Exception as e:
                st.warning(f"G-Force grafiği çizilemedi: `{e}`")

    # ═══════════════════════════════════════════════════════════════
    # SEKME 4 — ISI HARİTALARI (VİTES)
    # ═══════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("🔥 Pist Isı Haritası — Vites Bazlı Renklendirme")

        try:
            # nGear sütunundan vites verisi al; referans olarak Pilot 1'in en hızlı turunu kullan
            if 'nGear' not in tel_d1.columns:
                st.info("Bu seans için vites (nGear) verisi mevcut değil.")
            else:
                fig_heat = go.Figure()

                gear_vals = tel_d1['nGear'].tolist()
                x_vals    = tel_d1['X'].tolist()
                y_vals    = tel_d1['Y'].tolist()

                # Vites bazlı renk skalası: 1-2 vites kırmızı, 7-8 mor/yeşil
                # Plotly'nin Plasma renk skalasını kullanıyoruz (düşük=sarı, yüksek=mor)
                fig_heat.add_trace(go.Scatter(
                    x=x_vals, y=y_vals,
                    mode='markers',
                    marker=dict(
                        color=gear_vals,
                        colorscale='Plasma',
                        colorbar=dict(
                            title="Vites",
                            tickvals=list(range(1, 9)),
                            ticktext=[f"Vites {i}" for i in range(1, 9)]
                        ),
                        size=4,
                        showscale=True
                    ),
                    text=[f"Vites: {g}" for g in gear_vals],
                    hovertemplate="%{text}<extra></extra>",
                    showlegend=False
                ))

                fig_heat.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0d0d0d",
                    plot_bgcolor="#0d0d0d",
                    height=550,
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False,
                               scaleanchor="y", scaleratio=1),
                    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                    margin=dict(l=0, r=0, t=20, b=0),
                    title=dict(text=f"<b>{driver1}</b> — En Hızlı Tur Vites Haritası",
                               font=dict(color="#ccc"), x=0.5)
                )
                st.plotly_chart(fig_heat, use_container_width=True)

                # Vites dağılım pastası
                st.markdown("---")
                st.markdown("#### 📊 Vites Kullanım Dağılımı")
                gc1, gc2 = st.columns(2)
                for col_w, tel_temp, drv, clr in [(gc1, tel_d1, driver1, c1), (gc2, tel_d2, driver2, c2)]:
                    with col_w:
                        if 'nGear' in tel_temp.columns:
                            gear_counts = tel_temp['nGear'].value_counts().sort_index()
                            fig_pie = go.Figure(go.Pie(
                                labels=[f"Vites {g}" for g in gear_counts.index],
                                values=gear_counts.values.tolist(),
                                hole=0.5,
                                marker=dict(colors=[
                                    f"hsl({int(g/8*270)},80%,55%)" for g in gear_counts.index
                                ])
                            ))
                            fig_pie.update_layout(
                                template="plotly_dark",
                                paper_bgcolor="#0d0d0d",
                                title=dict(text=f"<b>{drv}</b>", font=dict(color=clr)),
                                margin=dict(l=0, r=0, t=40, b=0),
                                showlegend=True
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)

        except Exception as e:
            st.warning(f"Isı haritası oluşturulamadı: `{e}`")

    # ═══════════════════════════════════════════════════════════════
    # SEKME 5 — STRATEJİ & LASTİK ANALİZİ
    # ═══════════════════════════════════════════════════════════════
    with tab5:
        st.subheader("🔧 Strateji Analizi & Lastik Aşınması")

        # ── Üst: Gantt — Stint Geçmişi ──────────────────────────
        st.markdown("#### 📅 Stint Geçmişi (Gantt)")

        try:
            fig_gantt = go.Figure()
            y_labels  = []

            for drv_abbr, laps_set, clr_base, idx in [
                (driver1, laps_d1, c1, 0),
                (driver2, laps_d2, c2, 1)
            ]:
                y_labels.append(drv_abbr)

                # Lap verilerini hazırla
                drv_laps = laps_set.copy()
                drv_laps['LapNumber'] = drv_laps['LapNumber'].fillna(0).astype(int)

                # Stint numarası ve lastik cinsine göre grupla
                if 'Stint' in drv_laps.columns and 'Compound' in drv_laps.columns:
                    stints = drv_laps.groupby(['Stint', 'Compound']).agg(
                        StartLap=('LapNumber', 'min'),
                        EndLap=('LapNumber', 'max'),
                        NumLaps=('LapNumber', 'count')
                    ).reset_index()

                    for _, stint_row in stints.iterrows():
                        compound = str(stint_row['Compound']).upper()
                        tyre_clr = TYRE_COLORS.get(compound, "#888")
                        tyre_lbl = TYRE_LABELS.get(compound, compound[0])

                        fig_gantt.add_trace(go.Bar(
                            x=[stint_row['NumLaps']],
                            y=[drv_abbr],
                            base=[stint_row['StartLap']],
                            orientation='h',
                            name=compound,
                            marker=dict(color=tyre_clr, line=dict(color="#0d0d0d", width=2)),
                            text=f"{tyre_lbl} ({stint_row['NumLaps']} tur)",
                            textposition='inside',
                            insidetextfont=dict(color='black' if compound == 'HARD' else 'white',
                                                size=11, family='Inter'),
                            hovertemplate=(
                                f"<b>{drv_abbr}</b><br>"
                                f"Hamur: {compound}<br>"
                                f"Tur {int(stint_row['StartLap'])} → {int(stint_row['EndLap'])}<br>"
                                f"Süre: {int(stint_row['NumLaps'])} tur<extra></extra>"
                            ),
                            showlegend=(idx == 0),
                            legendgroup=compound,
                        ))
                else:
                    st.info(f"{drv_abbr} için stint/hamur verisi yok (bu seans için beklenen bir durum olabilir).")

            fig_gantt.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0d0d0d",
                plot_bgcolor="#0d0d0d",
                barmode='overlay',
                xaxis=dict(title="Tur Numarası"),
                yaxis=dict(title="Pilot", categoryorder='array', categoryarray=[driver1, driver2]),
                height=260,
                legend=dict(
                    title="Lastik Hamuru",
                    orientation='h', y=1.15,
                    font=dict(size=11)
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            st.plotly_chart(fig_gantt, use_container_width=True)

        except Exception as e:
            st.warning(f"Gantt grafiği oluşturulamadı: `{e}`")

        # ── Alt: Lastik Aşınması (Degradation) ──────────────────
        st.markdown("---")
        st.markdown("#### 📉 Lastik Aşınması (Tyre Degradation)")

        deg_c1, deg_c2 = st.columns(2)

        for col_w, laps_set, drv_abbr, clr in [
            (deg_c1, laps_d1, driver1, c1),
            (deg_c2, laps_d2, driver2, c2)
        ]:
            with col_w:
                st.markdown(f"<span style='color:{clr};font-weight:700'>{drv_abbr}</span>", unsafe_allow_html=True)

                # Pitten çıkış/giriş turları hariç; yalnızca güvenilir turlar
                valid = laps_set[
                    (laps_set['PitOutTime'].isnull()) &
                    (laps_set['PitInTime'].isnull()) &
                    (laps_set['IsAccurate'] == True)
                ].copy()

                if not valid.empty:
                    valid['LapTime_s'] = valid['LapTime'].dt.total_seconds()
                    valid = valid.dropna(subset=['LapTime_s'])

                    if len(valid) >= 2:
                        # Fuel correction: Yakıt azaldıkça araç hafifler, tur süreleri kısalır.
                        # Ortalama yakıt payı ~0.065 sn/tur olarak alınır ve çıkarılır.
                        fuel_correction_per_lap = 0.065
                        valid['FuelCorrectedTime'] = (
                            valid['LapTime_s'] +
                            (valid['LapNumber'] - valid['LapNumber'].min()) * fuel_correction_per_lap
                        )

                        # Gerçek lastik düşüşü için doğrusal regresyon
                        z = np.polyfit(valid['LapNumber'], valid['FuelCorrectedTime'], 1)
                        p = np.poly1d(z)
                        deg_per_lap = z[0]  # pozitifse lastik aşınıyor

                        fig_deg = go.Figure()

                        # Noktalar (ham)
                        fig_deg.add_trace(go.Scatter(
                            x=valid['LapNumber'].tolist(),
                            y=valid['LapTime_s'].tolist(),
                            mode='markers', name='Ham Tur Süresi',
                            marker=dict(color=clr, size=7, opacity=0.7)
                        ))
                        # Yakıt düzeltmeli noktalar
                        fig_deg.add_trace(go.Scatter(
                            x=valid['LapNumber'].tolist(),
                            y=valid['FuelCorrectedTime'].tolist(),
                            mode='markers', name='Yakıt Düzeltmeli',
                            marker=dict(color=clr, size=7, symbol='diamond',
                                        line=dict(color='white', width=1))
                        ))
                        # Trend
                        x_range = np.linspace(valid['LapNumber'].min(), valid['LapNumber'].max(), 100)
                        fig_deg.add_trace(go.Scatter(
                            x=x_range.tolist(), y=p(x_range).tolist(),
                            mode='lines', name='Aşınma Trendi',
                            line=dict(color='white', dash='dash', width=1.5)
                        ))

                        fig_deg.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0d0d0d",
                            plot_bgcolor="#0d0d0d",
                            xaxis_title="Tur Numarası",
                            yaxis_title="Tur Süresi (sn)",
                            legend=dict(font=dict(size=10)),
                            margin=dict(l=0, r=0, t=20, b=0)
                        )
                        st.plotly_chart(fig_deg, use_container_width=True)

                        # Aşınma oranı özeti
                        deg_sign = "+" if deg_per_lap > 0 else ""
                        st.metric(
                            label="Tur başına lastik kaybı",
                            value=f"{deg_sign}{deg_per_lap:.3f} sn/tur"
                        )
                    else:
                        st.info("Trend için yeterli tur verisi yok.")
                else:
                    st.info("Kesintisiz stint verisi bulunamadı.")

else:
    # ── Hoş Geldin Ekranı ──────────────────────────────────────
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;'>
        <div style='font-size:5rem;margin-bottom:16px'>🏎️</div>
        <h2 style='color:#ff1801;font-family:Inter,sans-serif;font-weight:900'>
            DASHBOARD HAZIR
        </h2>
        <p style='color:#666;max-width:500px;margin:0 auto;line-height:1.7'>
            Sol panelden <b style='color:#ccc'>Sezon</b>, <b style='color:#ccc'>Grand Prix</b>
            ve <b style='color:#ccc'>Seans</b> seçin.<br>
            Karşılaştırmak istediğiniz iki pilotu girin ve<br>
            <b style='color:#ff1801'>🚀 Telemetriyi Yükle</b> butonuna basın.
        </p>
    </div>
    """, unsafe_allow_html=True)
