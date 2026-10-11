"""
แดชบอร์ดสถานประกอบการด้านการท่องเที่ยว
=========================================
ใช้ข้อมูลจากไฟล์ data.csv (สำมะโนธุรกิจ พ.ศ. 2555)
Libraries ที่ใช้: streamlit, pandas, matplotlib, seaborn
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# ============================================================
# ส่วนที่ 1: ตั้งค่าหน้าเว็บ
# ============================================================
st.set_page_config(
    page_title="สถานประกอบการท่องเที่ยว",
    page_icon="🏝️",
    layout="wide",
)

# --- ตั้งค่าฟอนต์ภาษาไทยสำหรับ matplotlib ---
# หาฟอนต์ไทยที่มีในเครื่อง แล้วเลือกตัวแรกที่เจอ
_available = [f.name for f in fm.fontManager.ttflist]
_thai_fonts = ["Leelawadee UI", "Tahoma", "Cordia New", "Segoe UI"]
THAI_FONT = next((f for f in _thai_fonts if f in _available), "sans-serif")
plt.rcParams["font.family"] = THAI_FONT
plt.rcParams["axes.unicode_minus"] = False  # แก้ปัญหาเครื่องหมายลบแสดงผิด

# --- CSS ปรับ UI ให้สะอาดขึ้น ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap');

/* ฟอนต์ทั้งหน้า */
html, body, [class*="css"] {
    font-family: 'Prompt', sans-serif;
}

/* หัวเรื่องหลัก */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 14px;
    padding: 20px 28px;
    margin-bottom: 20px;
    color: #fff;
}
.main-header h2 { margin: 0; font-size: 1.6rem; }
.main-header p  { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }

/* ซ่อนไอคอนลิงก์ที่ Streamlit ใส่ให้ heading */
.main-header a { display: none !important; }

/* หัวข้อย่อยของแต่ละกราฟ */
.chart-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #4a5568;
    margin: 8px 0 10px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ส่วนที่ 2: โหลดข้อมูลจาก data.csv
# ============================================================
@st.cache_data  # cache ไว้ไม่ต้องโหลดใหม่ทุกครั้ง
def load_data():
    """อ่านไฟล์ data.csv แล้ว strip ช่องว่างในคอลัมน์ข้อความ"""
    df = pd.read_csv("data.csv", encoding="utf-8")
    # ลบช่องว่างหัว-ท้ายในคอลัมน์ข้อความทุกตัว
    for col in ["region", "eco_activity", "unit", "source"]:
        df[col] = df[col].str.strip()
    return df

df = load_data()

# --- แยกข้อมูลสำคัญ ---
# แถว "จำนวนสถานประกอบการ" = ยอดรวมทั้งหมดของแต่ละภูมิภาค
df_totals = df[df["eco_activity"] == "จำนวนสถานประกอบการ"]
# ยอดรวมทั้งประเทศ
COUNTRY_TOTAL = df_totals[df_totals["region"] == "รวม"]["value"].values[0]

# --- กิจกรรมเศรษฐกิจ (ไม่รวมแถวรวม) ---
ALL_ACTIVITIES = [a for a in df["eco_activity"].unique() if a != "จำนวนสถานประกอบการ"]
# ภูมิภาค (ไม่รวมแถว "รวม")
ALL_REGIONS = [r for r in df["region"].unique() if r != "รวม"]

# --- กลุ่มกิจกรรมที่เกี่ยวกับการท่องเที่ยว ---
CORE_TOURISM = [
    "ที่พักแรมบริการอาหารและเครื่องดื่ม",      # โรงแรม ร้านอาหาร
    "ศิลปะความบันเทิงและนันทนาการ",             # สถานบันเทิง สวนสนุก
    "กิจกรรมการบริหารและการบริการสนับสนุน",      # ทัวร์ ตัวแทนท่องเที่ยว
]

EXTENDED_TOURISM = CORE_TOURISM + [
    "การขนส่งทางบกสถานที่เก็บสินค้า",           # ขนส่ง
    "การขายปลีก",                                 # ร้านขายของฝาก
    "กิจกรรมบริการอื่นๆ",                         # บริการอื่นๆ
]


# ============================================================
# ส่วนที่ 3: แถบเมนูด้านซ้าย (Sidebar)
# ============================================================
with st.sidebar:
    st.markdown("### 🎛️ ตัวกรองข้อมูล")
    st.divider()

    # --- เลือกกลุ่มกิจกรรม ---
    scope = st.radio(
        "🎯 กลุ่มกิจกรรมเศรษฐกิจ:",
        [
            "ธุรกิจท่องเที่ยวหลัก (3 กิจกรรม)",
            "ท่องเที่ยว + เกี่ยวเนื่อง (6 กิจกรรม)",
            "เลือกเอง",
            "ทั้งหมด",
        ],
    )

    # กำหนดรายการกิจกรรมตามที่เลือก
    if scope == "ธุรกิจท่องเที่ยวหลัก (3 กิจกรรม)":
        selected_activities = CORE_TOURISM
    elif scope == "ท่องเที่ยว + เกี่ยวเนื่อง (6 กิจกรรม)":
        selected_activities = EXTENDED_TOURISM
    elif scope == "ทั้งหมด":
        selected_activities = ALL_ACTIVITIES
    else:
        selected_activities = st.multiselect(
            "เลือกกิจกรรม:", ALL_ACTIVITIES, default=CORE_TOURISM
        )

    st.divider()

    # --- เลือกภูมิภาค ---
    selected_regions = st.multiselect(
        "📍 ภูมิภาค:", ALL_REGIONS, default=ALL_REGIONS
    )

    st.divider()

    # --- สีของกราฟ ---
    palette = st.selectbox(
        "🎨 โทนสีกราฟ:",
        ["Blues_r", "mako", "viridis", "crest", "flare", "Set2"],
    )

    st.divider()
    st.caption("📊 ข้อมูล: สำนักงานสถิติแห่งชาติ (พ.ศ. 2555)")

# --- ตรวจว่าเลือกอย่างน้อย 1 อย่าง ---
if not selected_activities:
    st.warning("⚠️ กรุณาเลือกอย่างน้อย 1 กิจกรรม")
    st.stop()
if not selected_regions:
    st.warning("⚠️ กรุณาเลือกอย่างน้อย 1 ภูมิภาค")
    st.stop()


# ============================================================
# ส่วนที่ 4: กรองข้อมูลและคำนวณตัวเลข
# ============================================================
# กรองเฉพาะกิจกรรมและภูมิภาคที่เลือก
df_filtered = df[
    (df["eco_activity"].isin(selected_activities))
    & (df["region"].isin(selected_regions))
].copy()

# --- สรุปยอดตามภูมิภาค ---
by_region = df_filtered.groupby("region")["value"].sum().reset_index()
by_region = by_region.sort_values("value", ascending=False)

# --- สรุปยอดตามกิจกรรม ---
by_activity = df_filtered.groupby("eco_activity")["value"].sum().reset_index()
by_activity = by_activity.sort_values("value", ascending=False)

# --- ตัวเลขสำคัญ ---
total_est = df_filtered["value"].sum()                    # ยอดรวมที่เลือก
country_act_total = df[                                    # ยอดรวมทั้งประเทศ
    (df["eco_activity"].isin(selected_activities)) & (df["region"] == "รวม")
]["value"].sum()
share_pct = (country_act_total / COUNTRY_TOTAL * 100) if COUNTRY_TOTAL > 0 else 0

# ภูมิภาคอันดับ 1
if not by_region.empty:
    top_region = by_region.iloc[0]
    top_region_name = top_region["region"]
    top_region_val = top_region["value"]
else:
    top_region_name, top_region_val = "-", 0

# กิจกรรมอันดับ 1
if not by_activity.empty:
    top_act = by_activity.iloc[0]
    top_act_name = top_act["eco_activity"]
    top_act_val = top_act["value"]
else:
    top_act_name, top_act_val = "-", 0


# ============================================================
# ส่วนที่ 5: แสดงผล - หัวเรื่อง + ตัวเลขสรุป
# ============================================================
st.markdown("""
<div class="main-header">
    <h2>🏝️ แดชบอร์ดสถานประกอบการด้านการท่องเที่ยว</h2>
    <p>วิเคราะห์จำนวนสถานประกอบการด้านการท่องเที่ยวในประเทศไทย — ข้อมูล พ.ศ. 2555</p>
</div>
""", unsafe_allow_html=True)

# --- KPI cards (4 ตัวเลขสำคัญ) ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("🏨 รวมสถานประกอบการ", f"{total_est:,.0f} แห่ง",
          delta=f"ทั้งประเทศ {country_act_total:,.0f}", delta_color="off")
k2.metric("📍 ภูมิภาคอันดับ 1", top_region_name,
          delta=f"{top_region_val:,.0f} แห่ง")
k3.metric("📊 สัดส่วนต่อธุรกิจทั้งหมด", f"{share_pct:.1f}%",
          delta=f"จาก {COUNTRY_TOTAL:,.0f} แห่ง", delta_color="off")
display_name = (top_act_name[:18] + "…") if len(top_act_name) > 18 else top_act_name
k4.metric("🏆 กิจกรรมอันดับ 1", display_name,
          delta=f"{top_act_val:,.0f} แห่ง")

st.markdown("")  # เว้นบรรทัด


# ============================================================
# ส่วนที่ 6: กราฟและตาราง (แบ่งเป็น 4 แท็บ)
# ============================================================
sns.set_theme(style="whitegrid", font=THAI_FONT)

tab1, tab2, tab3 = st.tabs([
    "📊 ภาพรวม",
    "🗺️ เปรียบเทียบรายภาค",
    "🔥 Heatmap",
])


# --------------------------------------------------
# แท็บ 1: ภาพรวมการกระจายตัว
# --------------------------------------------------
with tab1:
    col_left, col_right = st.columns(2)

    # --- กราฟ 1: แท่งตั้ง - ยอดรวมแต่ละภูมิภาค ---
    with col_left:
        st.markdown('<div class="chart-title">📊 จำนวนสถานประกอบการตามภูมิภาค</div>',
                    unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(7, 4.5))
        sns.barplot(data=by_region, x="region", y="value",
                    palette=palette, hue="region", legend=False, ax=ax1)
        ax1.set_xlabel("ภูมิภาค")
        ax1.set_ylabel("จำนวน (แห่ง)")
        ax1.tick_params(axis="x", rotation=15)
        # แสดงตัวเลขบนหัวแท่ง
        for bar in ax1.patches:
            h = bar.get_height()
            if h > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2, h,
                         f"{h:,.0f}", ha="center", va="bottom",
                         fontsize=8, fontweight="bold")
        ax1.set_ylim(0, by_region["value"].max() * 1.15)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    # --- กราฟ 2: แท่งนอน - จัดอันดับตามกิจกรรม ---
    with col_right:
        st.markdown('<div class="chart-title">🏷️ จัดอันดับตามประเภทกิจกรรม</div>',
                    unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(7, 4.5))
        sns.barplot(data=by_activity, y="eco_activity", x="value",
                    palette=palette, hue="eco_activity", legend=False, ax=ax2)
        ax2.set_xlabel("จำนวน (แห่ง)")
        ax2.set_ylabel("")
        for bar in ax2.patches:
            w = bar.get_width()
            if w > 0:
                ax2.text(w, bar.get_y() + bar.get_height() / 2,
                         f" {w:,.0f}", ha="left", va="center",
                         fontsize=8, fontweight="bold")
        ax2.set_xlim(0, by_activity["value"].max() * 1.22)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    st.divider()

    # --- กราฟ 3: Pointplot - เปรียบเทียบกิจกรรมในแต่ละภูมิภาค ---
    st.markdown('<div class="chart-title">📈 เปรียบเทียบกิจกรรมในแต่ละภูมิภาค</div>',
                unsafe_allow_html=True)
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    sns.pointplot(data=df_filtered, x="region", y="value",
                  hue="eco_activity", palette=palette, markers="o", ax=ax3)
    ax3.set_xlabel("ภูมิภาค")
    ax3.set_ylabel("จำนวน (แห่ง)")
    ax3.legend(title="กิจกรรม", bbox_to_anchor=(1.02, 1), loc="upper left",
               fontsize=7, title_fontsize=8)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)


# --------------------------------------------------
# แท็บ 2: เปรียบเทียบรายภาค
# --------------------------------------------------
with tab2:
    # --- กราฟ 4: Grouped bar - ภูมิภาค x กิจกรรม ---
    st.markdown('<div class="chart-title">📊 เปรียบเทียบกิจกรรมในแต่ละภูมิภาค</div>',
                unsafe_allow_html=True)
    fig4, ax4 = plt.subplots(figsize=(11, 5))
    sns.barplot(data=df_filtered, x="region", y="value",
                hue="eco_activity", palette=palette, ax=ax4)
    ax4.set_xlabel("ภูมิภาค")
    ax4.set_ylabel("จำนวน (แห่ง)")
    ax4.tick_params(axis="x", rotation=10)
    ax4.legend(title="กิจกรรม", bbox_to_anchor=(0.5, -0.18),
               loc="upper center", ncol=2, fontsize=7, title_fontsize=8)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    st.divider()

    # --- สัดส่วนธุรกิจท่องเที่ยวต่อสถานประกอบการรวม ---
    st.markdown('<div class="chart-title">⚖️ สัดส่วนธุรกิจท่องเที่ยวต่อสถานประกอบการรวมในแต่ละภูมิภาค</div>',
                unsafe_allow_html=True)

    # คำนวณสัดส่วนทีละภูมิภาค
    share_list = []
    for region in selected_regions:
        # ยอดรวมทั้งหมดของภูมิภาค (จากแถว "จำนวนสถานประกอบการ")
        total_rows = df_totals[df_totals["region"] == region]["value"]
        region_total = total_rows.values[0] if len(total_rows) > 0 else 0
        # ยอดเฉพาะกิจกรรมที่เลือก
        tourism_val = df_filtered[df_filtered["region"] == region]["value"].sum()
        pct = (tourism_val / region_total * 100) if region_total > 0 else 0
        share_list.append({
            "region": region,
            "ธุรกิจท่องเที่ยว (แห่ง)": tourism_val,
            "รวมทั้งหมด (แห่ง)": region_total,
            "สัดส่วน (%)": round(pct, 2),
        })

    df_shares = pd.DataFrame(share_list).sort_values("สัดส่วน (%)", ascending=False)

    col_chart, col_table = st.columns([1.1, 0.9])

    with col_chart:
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        bars = sns.barplot(data=df_shares, x="region", y="สัดส่วน (%)",
                           palette=palette, hue="region", legend=False, ax=ax5)
        ax5.set_xlabel("ภูมิภาค")
        ax5.set_ylabel("ร้อยละ (%)")
        ax5.tick_params(axis="x", rotation=20)
        for bar in bars.patches:
            h = bar.get_height()
            if h > 0:
                ax5.text(bar.get_x() + bar.get_width() / 2, h,
                         f"{h:.1f}%", ha="center", va="bottom",
                         fontsize=8, fontweight="bold")
        ax5.set_ylim(0, df_shares["สัดส่วน (%)"].max() * 1.2)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

    with col_table:
        st.markdown("**📋 ตารางสัดส่วนรายภูมิภาค**")
        st.dataframe(
            df_shares.style.format({
                "ธุรกิจท่องเที่ยว (แห่ง)": "{:,.0f}",
                "รวมทั้งหมด (แห่ง)": "{:,.0f}",
                "สัดส่วน (%)": "{:.2f}%",
            }).background_gradient(subset=["สัดส่วน (%)"], cmap="Blues"),
            use_container_width=True,
            hide_index=True,
        )


# --------------------------------------------------
# แท็บ 3: Heatmap
# --------------------------------------------------
with tab3:
    st.markdown('<div class="chart-title">🔥 Heatmap ความหนาแน่นสถานประกอบการ (ภูมิภาค × กิจกรรม)</div>',
                unsafe_allow_html=True)

    # สร้างตาราง pivot: แถว = ภูมิภาค, คอลัมน์ = กิจกรรม
    pivot = df_filtered.pivot(
        index="region", columns="eco_activity", values="value"
    ).fillna(0)

    fig6, ax6 = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="YlGnBu",
                linewidths=0.5, linecolor="#e2e8f0",
                cbar_kws={"label": "จำนวน (แห่ง)"}, ax=ax6)
    ax6.set_xlabel("กิจกรรมเศรษฐกิจ")
    ax6.set_ylabel("ภูมิภาค")
    ax6.tick_params(axis="x", rotation=25)
    plt.tight_layout()
    st.pyplot(fig6)
    plt.close(fig6)

    st.info("💡 ช่องสีเข้ม = มีสถานประกอบการจำนวนมาก, ช่องสีอ่อน = มีน้อย")





# ============================================================
# ส่วนที่ 7: Footer
# ============================================================
st.divider()
st.caption("พัฒนาด้วย Streamlit + Seaborn | ข้อมูลสำนักงานสถิติแห่งชาติ")
