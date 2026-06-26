import streamlit as st
import json
import os

st.set_page_config(page_title="한국 32강 경우의 수 대시보드", page_icon="🇰🇷", layout="wide")

# CSS: 모바일 반응형 및 대시보드 디자인
st.markdown("""
<style>
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 25px;
    }
    .scenario-card {
        position: relative;
        border: 3px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 30px 15px;
        text-align: center;
        min-height: 420px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background-color: rgba(128, 128, 128, 0.03);
        overflow: hidden;
    }
    .flags-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 15px 0 25px 0;
    }
    .flag-box { text-align: center; z-index: 2; }
    .flag-icon {
        width: 120px; height: 80px;
        object-fit: cover; border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        margin-bottom: 12px;
    }
    .team-name { font-size: 32px; font-weight: 900; letter-spacing: -1px; }
    .vs-text { font-size: 30px; font-weight: bold; color: #aaa; padding-top: 25px; }
    .overlay {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        font-size: 400px; font-family: 'Arial', sans-serif; font-weight: 900;
        pointer-events: none; z-index: 10; line-height: 1; user-select: none;
    }
    .overlay-fail { color: rgba(220, 53, 69, 0.5); }
    .overlay-success { color: rgba(40, 167, 69, 0.5); }
    .card-title { font-size: 38px; font-weight: 900; margin-bottom: 10px; z-index: 2; }
    .card-desc { font-size: 24px; font-weight: 700; margin-bottom: 10px; word-break: keep-all; z-index: 2; color: #444; }
    .card-reason { font-size: 26px; font-weight: 900; color: #007bff; z-index: 2; }
    div[data-testid="stMetricValue"] { font-size: 50px; font-weight: 900; }

    @media (max-width: 768px) {
        .dashboard-grid { gap: 8px; }
        .scenario-card { padding: 15px 5px; min-height: 180px; border-width: 2px; border-radius: 10px; }
        .flags-container { gap: 5px; margin: 10px 0 15px 0; }
        .flag-icon { width: 32px; height: 22px; margin-bottom: 4px; border-radius: 3px; }
        .team-name { font-size: 11px; letter-spacing: -0.5px; }
        .vs-text { font-size: 12px; padding-top: 10px; }
        .card-title { font-size: 18px; margin-bottom: 5px; }
        .card-desc { font-size: 10px; margin-bottom: 5px; line-height: 1.2; letter-spacing: -0.5px; }
        .card-reason { font-size: 12px; line-height: 1.2; letter-spacing: -0.5px; }
        .overlay { font-size: 130px; }
        div[data-testid="stMetricValue"] { font-size: 35px; }
    }
</style>
""", unsafe_allow_html=True)

# 한국 시각 기준 경기 일정을 'time' 항목에 추가했습니다.
GROUP_INFO = {
    "D조": {"t1": "호주", "f1": "https://flagcdn.com/w80/au.png", "t2": "파라과이", "f2": "https://flagcdn.com/w80/py.png", "sep": "vs", "time": "6.26(금) 완료"},
    "E조": {"t1": "에콰도르", "f1": "https://flagcdn.com/w80/ec.png", "t2": "퀴라소", "f2": "https://flagcdn.com/w80/cw.png", "sep": "&", "time": "6.26(금) 완료"},
    "F조": {"t1": "일본", "f1": "https://flagcdn.com/w80/jp.png", "t2": "스웨덴", "f2": "https://flagcdn.com/w80/se.png", "sep": "vs", "time": "6.27(토) 오전 10:30"},
    "G조": {"t1": "벨기에", "f1": "https://flagcdn.com/w80/be.png", "t2": "이집트", "f2": "https://flagcdn.com/w80/eg.png", "sep": "+", "time": "6.27(토) 오후 1:30"},
    "H조": {"t1": "스페인", "f1": "https://flagcdn.com/w80/es.png", "t2": "사우디", "f2": "https://flagcdn.com/w80/sa.png", "sep": "+", "time": "6.27(토) 오전 11:30"},
    "I조": {"t1": "세네갈", "f1": "https://flagcdn.com/w80/sn.png", "t2": "이라크", "f2": "https://flagcdn.com/w80/iq.png", "sep": "vs", "time": "6.27(토) 오전 6:30"},
    "J조": {"t1": "오스트리아", "f1": "https://flagcdn.com/w80/at.png", "t2": "알제리", "f2": "https://flagcdn.com/w80/dz.png", "sep": "vs", "time": "6.28(일) 오후 1:30"},
    "K조": {"t1": "콩고민주", "f1": "https://flagcdn.com/w80/cd.png", "t2": "우즈벡", "f2": "https://flagcdn.com/w80/uz.png", "sep": "vs", "time": "6.28(일) 오전 11:00"},
    "L조": {"t1": "가나", "f1": "https://flagcdn.com/w80/gh.png", "t2": "크로아티아", "f2": "https://flagcdn.com/w80/hr.png", "sep": "vs", "time": "6.28(일) 오전 8:30"},
}

def load_data():
    file_path = "data/results.json"
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("🇰🇷 한국 32강 경우의 수 총 정리")
    st.markdown("### 9가지 조별 시나리오 중 **3개**만 맞으면 32강 진출!")
    data = load_data()

    if not data:
        st.warning("아직 수집된 경기 결과가 없습니다. 업데이트를 기다려주세요.")
        return

    # 상단 요약 대시보드
    total_achieved = data.get("total_achieved", 0)
    progress_value = min(total_achieved / 3.0, 1.0)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="현재 달성된 경우의 수", value=f"{total_achieved} 개", delta=f"{3 - total_achieved}개 남음!" if total_achieved < 3 else "진출 확정!", delta_color="normal")
    with col2:
        st.write("진출 달성률")
        st.progress(progress_value)

    st.info(f"**🤖 상태 코멘트:** {data.get('ai_comment', '파이썬 로직 계산 완료.')}")
    st.markdown("---")

    scenarios = data.get("scenarios", {})
    groups = ["D조", "E조", "F조", "G조", "H조", "I조", "J조", "K조", "L조"]

    grid_html = '<div class="dashboard-grid">'

    for group in groups:
        info = scenarios.get(group, {})
        status = info.get("status", "pending")
        desc = info.get("description", "경기 분석 대기 중")
        
        g_info = GROUP_INFO[group]

        # 🚨 [추가된 로직] 대기 중(pending)이면 백엔드 데이터 대신 일정을 덮어씌웁니다.
        if status == "pending":
            reason = f"⏳ {g_info['time']} 예정"
        else:
            reason = info.get("reason", "결과 확인 불가")

        overlay_html = ""
        if status == "success":
            overlay_html = '<div class="overlay overlay-success">O</div>'
        elif status == "fail":
            overlay_html = '<div class="overlay overlay-fail">X</div>'

        card_html = f"""
        <div class="scenario-card">
            {overlay_html}
            <div class="card-title">{group}</div>
            <div class="flags-container">
                <div class="flag-box">
                    <img src="{g_info['f1']}" class="flag-icon">
                    <div class="team-name">{g_info['t1']}</div>
                </div>
                <div class="vs-text">{g_info['sep']}</div>
                <div class="flag-box">
                    <img src="{g_info['f2']}" class="flag-icon">
                    <div class="team-name">{g_info['t2']}</div>
                </div>
            </div>
            <div class="card-desc">{desc}</div>
            <div class="card-reason">{reason}</div>
        </div>
        """
        grid_html += card_html

    grid_html += '</div>'

    if hasattr(st, "html"):
        st.html(grid_html)
    else:
        st.markdown(grid_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
