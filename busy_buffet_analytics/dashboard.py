from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# 1. Page Config & Executive Layout Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hotel Amber 85 - Executive Analytics",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>
    .main { background-color: #F8FAFC; }
    .kpi-card {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06);
        border-top: 4px solid #1E3A8A;
        text-align: center;
    }
    .kpi-value { font-size: 26px; font-weight: bold; color: #1E3A8A; }
    .kpi-label { font-size: 13px; color: #64748B; font-weight: 600; margin-top: 4px; }
    .section-title {
        background: #1E3A8A;
        color: white;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 17px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .card-box {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
    }
    .insight-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px;
        border-radius: 4px;
        font-size: 13.5px;
        color: #1E40AF;
        margin-top: 10px;
    }
    .status-true {
        color: #059669;
        font-weight: bold;
    }
    .status-false {
        color: #DC2626;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 2. Data Processing Engine
# ---------------------------------------------------------
@st.cache_data
def load_data():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "2026 Data Test1 Final - Busy Buffet Dataset.xlsx")
    xls = pd.ExcelFile(file_path)
    sheet_labels = {
        "133": "13/3 (ศุกร์)",
        "143": "14/3 (เสาร์)",
        "153": "15/3 (อาทิตย์)",
        "173": "17/3 (อังคาร)",
        "183": "18/3 (พุธ)",
    }

    all_dfs = []
    for sheet in xls.sheet_names:
        df_sheet = pd.read_excel(xls, sheet)
        df_sheet = df_sheet[
            [
                "service_no.",
                "pax",
                "queue_start",
                "queue_end",
                "table_no.",
                "meal_start",
                "meal_end",
                "Guest_type",
            ]
        ].dropna(how="all")
        df_sheet["sheet_name"] = str(sheet)
        df_sheet["date_label"] = sheet_labels.get(str(sheet), f"Day {sheet}")
        all_dfs.append(df_sheet)

    df = pd.concat(all_dfs, ignore_index=True)

    def parse_time(val):
        if pd.isna(val) or val == "" or str(val).strip() == "":
            return None
        s = str(val).strip()
        try:
            return datetime.strptime(s, "%H:%M:%S").time()
        except Exception:
            try:
                return datetime.strptime(s, "%H:%M").time()
            except Exception:
                return None

    def time_to_min(t):
        if t is None:
            return np.nan
        return t.hour * 60 + t.minute + t.second / 60.0

    for col in ["queue_start", "queue_end", "meal_start", "meal_end"]:
        df[col + "_t"] = df[col].apply(parse_time)
        df[col + "_min"] = df[col + "_t"].apply(time_to_min)

    df["wait_time_min"] = df["queue_end_min"] - df["queue_start_min"]
    df["meal_duration_min"] = df["meal_end_min"] - df["meal_start_min"]
    df["meal_duration_min"] = df["meal_duration_min"].apply(
        lambda x: x + 1440 if x < 0 else (x if pd.notna(x) else np.nan)
    )
    df.loc[df["meal_duration_min"] > 300, "meal_duration_min"] = np.nan

    df["is_walk_away"] = df["queue_start"].notna() & df["meal_start"].isna()
    df["has_queue"] = df["queue_start"].notna()
    df["start_hour"] = df["meal_start_t"].apply(
        lambda t: t.hour if t is not None else np.nan
    )

    return df


df = load_data()

# ---------------------------------------------------------
# 3. Header & Metric Cards
# ---------------------------------------------------------
st.markdown(
    "<h2 style='color: #1E3A8A; font-weight: 800; margin-bottom: 0px;'>HOTEL AMBER 85 - EXECUTIVE ANALYTICS</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color: #64748B; font-size: 14px;'>Atmind Data Analytics Test 2026: Fact-Checking & Proof Analysis</p>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.markdown(
    f"<div class='kpi-card'><div class='kpi-value'>{len(df):,}</div><div class='kpi-label'>กลุ่มลูกค้ารวม</div></div>",
    unsafe_allow_html=True,
)
k2.markdown(
    f"<div class='kpi-card'><div class='kpi-value'>{int(df['pax'].sum()):,}</div><div class='kpi-label'>จำนวนลูกค้ารวม (Pax)</div></div>",
    unsafe_allow_html=True,
)
k3.markdown(
    f"<div class='kpi-card'><div class='kpi-value'>{(df['has_queue'].sum()/len(df)*100):.1f}%</div><div class='kpi-label'>อัตราการรอคิว</div></div>",
    unsafe_allow_html=True,
)
k4.markdown(
    f"<div class='kpi-card'><div class='kpi-value'>{df[df['has_queue'] & (df['Guest_type']=='Walk in')]['wait_time_min'].mean():.1f}m</div><div class='kpi-label'>เวลารอเฉลี่ย (Walk-in)</div></div>",
    unsafe_allow_html=True,
)
k5.markdown(
    f"<div class='kpi-card'><div class='kpi-value' style='color: #DC2626;'>{df['is_walk_away'].sum()}</div><div class='kpi-label'>กลุ่มถอนตัว (Walk-away)</div></div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. TASK 1: Fact Checking 3 Opinions (3 Visuals & Commentary)
# ---------------------------------------------------------
st.markdown(
    "<div class='section-title'>TASK 1: Visual Proofs & Analysis - พิสูจน์ข้อเท็จจริงจากพนักงาน 3 ข้อ</div>",
    unsafe_allow_html=True,
)

v1, v2, v3 = st.columns(3)

# --- VISUAL 1: พิสูจน์ข้อที่ 1 ---
with v1:
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("##### 1. การรอคิวและการถอนตัว (Walk-away)")
    
    q_stats = (
        df[df["has_queue"]]
        .groupby(["Guest_type", "is_walk_away"])
        .agg(
            wait_mean=("wait_time_min", "mean"),
            group_count=("service_no.", "count"),
            pax_count=("pax", "sum"),
        )
        .reset_index()
    )
    q_stats["status_label"] = q_stats["is_walk_away"].map(
        {False: "ได้ทาน (Seated)", True: "ถอนตัว (Walk-away)"}
    )
    q_stats["category"] = q_stats["Guest_type"] + " - " + q_stats["status_label"]
    q_stats["x_label"] = q_stats.apply(
        lambda r: f"{r['category']}<br>({int(r['group_count'])} กลุ่ม / {int(r['pax_count'])} คน)",
        axis=1,
    )

    color_map = {
        "In house - ได้ทาน (Seated)": "#1E3A8A",
        "In house - ถอนตัว (Walk-away)": "#60A5FA",
        "Walk in - ได้ทาน (Seated)": "#D97706",
        "Walk in - ถอนตัว (Walk-away)": "#DC2626",
    }

    fig_v1 = px.bar(
        q_stats,
        x="x_label",
        y="wait_mean",
        color="category",
        text_auto=".1f",
        color_discrete_map=color_map,
    )
    fig_v1.update_layout(
        height=320,
        plot_bgcolor="white",
        margin=dict(l=5, r=5, t=30, b=5),
        showlegend=False,
        xaxis_title="จำนวนลูกค้า (กลุ่ม / คน)",
        yaxis_title="เวลารอเฉลี่ย (นาที)",
    )
    st.plotly_chart(fig_v1, use_container_width=True, key="chart_t1_v1")

    st.markdown(
        """
    <div class='insight-box'>
        <b>ผลการพิสูจน์ข้อ 1: <span class='status-true'>เป็นจริง (True)</span></b><br>
        • <b>Walk-in:</b> ต้องรอนานเฉลี่ยถึง <b>38.6 นาที</b> (สูงสุด 80 นาที) และมีกลุ่มถอนตัว 7 กลุ่ม (เวลาที่ลูกค้าถอนตัวเฉลี่ย 37.1 นาที)<br>
        • <b>In-house:</b> แม้เป็นแขกของโรงแรมแต่รอนานเฉลี่ยถึง <b>27.9 นาที</b> และมีถอนตัวถึง 7 กลุ่มเช่นกัน (เวลาที่ลูกค้าถอนตัวเฉลี่ย 28.3 นาที)<br>
        • <b>สรุป:</b> ทั้งสองกลุ่มไม่พอใจกับการรอคิวนานจนถอนตัวรวม 14 กลุ่ม (16 Pax)
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- VISUAL 2: พิสูจน์ข้อที่ 2 ---
with v2:
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("##### 2. ความยุ่งและคิวสะสมรายวัน (Daily Demand)")
    
    daily_stats = (
        df.groupby(["date_label"])
        .agg(
            total_pax=("pax", "sum"),
            queue_count=("has_queue", "sum"),
            walk_away_count=("is_walk_away", "sum"),
        )
        .reset_index()
    )

    fig_v2 = go.Figure()
    fig_v2.add_trace(
        go.Bar(
            x=daily_stats["date_label"],
            y=daily_stats["total_pax"],
            name="จำนวนลูกค้า (Pax)",
            marker_color="#1E3A8A",
            text=daily_stats["total_pax"],
            textposition="auto",
        )
    )
    fig_v2.add_trace(
        go.Scatter(
            x=daily_stats["date_label"],
            y=daily_stats["queue_count"],
            name="จำนวนกลุ่มที่ต้องรอคิว",
            mode="lines+markers+text",
            line=dict(color="#DC2626", width=3),
            text=daily_stats["queue_count"],
            textposition="top center",
        )
    )
    fig_v2.update_layout(
        height=320,
        plot_bgcolor="white",
        margin=dict(l=5, r=5, t=30, b=5),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
        ),
        xaxis_title="วันที่",
        yaxis_title="จำนวนลูกค้า",
    )
    st.plotly_chart(fig_v2, use_container_width=True, key="chart_t1_v2")

    st.markdown(
        """
    <div class='insight-box'>
        <b>ผลการพิสูจน์ข้อ 2: <span class='status-false'>ไม่เป็นจริง (False)</span></b><br>
        • <b>ไม่ได้ยุ่งทุกวัน:</b> วันธรรมดา 13/3 (ศุกร์), 17/3 (อังคาร), 18/3 (พุธ) <b>ไม่มีคิวเลย (Queue = 0)</b> และไม่มีการถอนตัวเลย<br>
        • <b>แต่คิวจะไปกระจุกตัวกันอยู่ที่วันหยุด:</b> คิวติดขัดหนักเฉพาะวันเสาร์-อาทิตย์ โดยวันที่ 15/3 (อาทิตย์) คิวพุ่งถึง 54 กลุ่ม ถอนตัว 13 กลุ่ม<br>
        • <b>สรุป:</b> ไม่จำเป็นต้องยกเลิกบุฟเฟต์ เพียงแต่ต้องบริหาร Peak Demand ในวันหยุดให้เป็นระบบมากขึ้น
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- VISUAL 3: พิสูจน์ข้อที่ 3 ---
with v3:
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("##### 3. ระยะเวลาการนั่งทานจริง (Meal Duration)")
    
    meal_df = df.dropna(subset=["meal_duration_min"])
    meal_df = meal_df[meal_df["meal_duration_min"] <= 300]

    fig_v3 = px.box(
        meal_df,
        x="Guest_type",
        y="meal_duration_min",
        color="Guest_type",
        color_discrete_map={"In house": "#1E3A8A", "Walk in": "#D97706"},
        points="all",
        labels={
            "Guest_type": "ประเภทลูกค้า",
            "meal_duration_min": "ระยะเวลาทาน (นาที)",
        },
    )
    fig_v3.add_hline(
        y=120,
        line_dash="dash",
        line_color="#DC2626",
        annotation_text="เกณฑ์มาตรฐาน 120 นาที (92.8%)",
    )
    fig_v3.update_layout(
        height=320,
        plot_bgcolor="white",
        margin=dict(l=5, r=5, t=30, b=5),
        showlegend=False,
        yaxis_title="ระยะเวลาทาน (นาที)",
    )
    st.plotly_chart(fig_v3, use_container_width=True, key="chart_t1_v3")

    st.markdown(
        """
    <div class='insight-box'>
        <b>ผลการพิสูจน์ข้อ 3: <span class='status-false'>ไม่เป็นจริง (False)</span></b><br>
        • <b>ไม่ได้นั่งทั้งวัน:</b> Walk-in นั่งทานเฉลี่ย <b>72.8 นาที</b> และ In-house เฉลี่ย 43.9 นาที<br>
        • <b>ลูกค้า 92.8% ทานเสร็จใน 2 ชม.:</b> ลูกค้าเกือบทั้งหมดทานเสร็จตามเวลามาตรฐาน ไม่ได้นั่งแช่นานผิดปกติ<br>
        • <b>สาเหตุจริงของคิว:</b> เกิดจาก Table Allocation ที่ไม่รองรับลูกค้ากลุ่มเล็ก (1-2 Pax) ซึ่งมีสูงถึง 83.7% ไม่ใช่เพราะลูกค้านั่งนาน
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. TASK 2: Visual Evidence Matrix (ดึง Visual จาก Task 1 มาใช้ + กำหนด key ป้องกัน ID ชนกัน)
# ---------------------------------------------------------
st.markdown(
    "<div class='section-title'>TASK 2: Visual Evidence Matrix - หักล้าง 3 แนวทางเดิมด้วยข้อมูล</div>",
    unsafe_allow_html=True,
)

t2_col1, t2_col2, t2_col3 = st.columns(3)

with t2_col1:
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("#### 1. ลดเวลาทานจาก 5 ชั่วโมง")

    # ดึง Visual 3 จาก Task 1 มาใช้วิเคราะห์หักล้าง (ใส่ key="chart_t2_v3")
    st.plotly_chart(fig_v3, use_container_width=True, key="chart_t2_v3")

    st.markdown(
        "**บทวิเคราะห์เพื่อหักล้าง (Disprove):** จาก visuals 3 ของ Task1 จะเห็นว่าลูกค้า **92.8% ทานเสร็จภายใน 120 นาที หรือ 2 ชั่วโมง** อยู่แล้ว การประกาศลดเวลาทานจาก 5 ชั่วโมง จึงไม่ช่วยเพิ่มอัตราการหมุนเวียนโต๊ะได้จริง"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with t2_col2:
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("#### 2. ขึ้นราคา 259 บาททุกวัน")

    # ดึง Visual 2 จาก Task 1 มาใช้วิเคราะห์หักล้าง (ใส่ key="chart_t2_v2")
    st.plotly_chart(fig_v2, use_container_width=True, key="chart_t2_v2")

    st.markdown(
        "**บทวิเคราะห์เพื่อหักล้าง (Disprove):** จาก visuals 2 ของ Task1 จะเห็นว่า Demand ในวันธรรมดาไม่ได้แน่น การปรับขึ้นราคา +62.8% เท่ากันทุกวันจะทำลายฐานลูกค้า Walk-in วันธรรมดาอย่างรุนแรง"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with t2_col3:
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("#### 3. ให้ In-house ข้ามคิว")

    pax_size = df["pax"].value_counts(normalize=True).reset_index()
    pax_size.columns = ["size", "pct"]
    pax_size["pct"] = pax_size["pct"] * 100

    fig_t2_3 = px.pie(
        pax_size,
        names="size",
        values="pct",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.4,
    )
    fig_t2_3.update_layout(
        height=240,
        title="สัดส่วนขนาดกลุ่มลูกค้า (%)",
        margin=dict(l=5, r=5, t=30, b=5),
        showlegend=True,
    )
    st.plotly_chart(fig_t2_3, use_container_width=True, key="chart_t2_pie")
    st.markdown(
        "**บทวิเคราะห์เพื่อหักล้าง (Disprove):** **83.7% ของกลุ่มลูกค้าคือกลุ่มเล็ก 1-2 คน** การเปิดให้ข้ามคิวจะทำให้ Walk-in รอนานเกิน 60 นาที ส่งผลให้ Walk-away พุ่งสูงขึ้นและเกิดรีวิวด้านลบได้"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. TASK 3: Actionable Strategy Dashboard
# ---------------------------------------------------------
st.markdown(
    "<div class='section-title'>TASK 3: Executive Solutions - ข้อเสนอแนวทางแก้ไขที่ตรงจุด</div>",
    unsafe_allow_html=True,
)

s1, s2, = st.columns(2)


with s1:
    st.success(
        "**1. Dynamic Quotas Allocation**\n\nการันตีที่นั่ง 60% สำหรับ In-house และเปิด 40% ให้ Walk-in จองคิวล่วงหน้าผ่านระบบออนไลน์ เพื่อให้มีที่นั่งเพียงพอสำหรับลูกค้า In-house และสามารถจัดการคิวของลูกค้า Walk-in ได้เป็นระบบ"
    )

with s2:
    st.warning(
        "**2. Table Layout Resizing**\n\nปรับแยกโต๊ะรวมขนาดใหญ่ ให้กลายเป็นโต๊ะย่อย 2 ที่นั่ง เพื่อให้รองรับกลุ่มลูกค้าที่มากัน 1-2 คน ซึ่งมีสัดส่วนถึง 83.7%"
    )
