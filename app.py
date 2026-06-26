import streamlit as st
import json
import os

st.set_page_config(page_title="한국 32강 경우의 수 대시보드", page_icon="🇰🇷", layout="wide")

# CSS: 폰트와 카드 크기를 기존 대비 2배 수준으로 대폭 상향 & 상황판 숫자 크기 확대
st.markdown("""
<style>
    .scenario-card {
        position: relative;
        border: 3px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 30px 15px;
        text-align: center;
        margin-bottom: 25px;
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
    .flag-box {
        text-align: center;
        z-index: 2;
    }
    .flag-icon {
        width: 120px;
        height: 80px;
        object-fit: cover;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        margin-bottom: 12px;
    }
    .team-name {
        font-size: 32px;
        font-weight: 900;
        letter-spacing: -1px;
    }
    .vs-text {
        font-size: 30px;
        font-weight: bold;
        color: #aaa;
        padding-top: 25px;
    }
    .overlay {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 400px;
        font-family: 'Arial', sans-serif;
        font-weight: 900;
        pointer-events: none;
        z-index: 10;
        line-height: 1;
        user-select: none;
    }
    .overlay-fail { color: rgba(220, 53, 69, 0.5); }
    .overlay-success { color: rgba(40, 167, 69, 0.5); }
    .card-title {
        font-size: 38px;
        font-weight: 900;
        margin-bottom: 10px;
        z-index: 2;
    }
    .card-desc {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
        word-break: keep-all;
        z-index: 2;
        color: #444;
    }
    .card-reason {
        font-size: 26px;
        font-weight: 900;
        color: #007bff;
        z-index: 2;
    }
    div[data-testid="stMetricValue"] {
        font-size: 50px;
        font-weight: 900;
    }
</style>
""", unsafe_allow_html=True)

GROUP_INFO = {
    "D조": {"t1": "호주", "f1": "https://flagcdn.com/w80/au.png", "t2": "파라과이", "f2": "https://flagcdn.com/w80/py.png", "sep": "vs"},
    "E조": {"t1": "에콰도르", "f1": "https://flagcdn.com/w80/ec.png", "t2": "퀴라소", "f2": "https://flagcdn.com/w80/cw.png", "sep": "&"},
    "F조": {"t1": "일본", "f1": "https://flagcdn.com/w80/jp.png", "t2": "스웨덴", "f2": "https://flagcdn.com/w80/se.png", "sep": "vs"},
    "G조": {"t1": "벨기에", "f1": "https://flagcdn.com/w80/be.png", "t2": "이집트", "f2": "https://flagcdn.com/w80/eg.png", "sep": "+"},
    "H조": {"t1": "스페인", "f1": "https://flagcdn.com/w80/es.png", "t2": "사우디", "f2": "https://flagcdn.com/w80/sa.png", "sep": "+"},
    "I조": {"t1": "세네갈", "f1": "https://flagcdn.com/w80/sn.png", "t2": "이라크", "f2": "https://flagcdn.com/w80/iq.png", "sep": "vs"},
    "J조": {"t1": "오스트리아", "f1": "https://flagcdn.com/w80/at.png", "t2": "알제리", "f2": "https://flagcdn.com/w80/dz.png", "sep": "vs"},
    "K조": {"t1": "콩고민주", "f1": "https://flagcdn.com/w80/cd.png", "t2": "우즈벡", "f2": "https://flagcdn.com/w80/uz.png", "sep": "vs"},
    "L조": {"t1": "가나", "f1": "https://flagcdn.com/w80/gh.png", "t2": "크로아티아", "f2": "https://flagcdn.com/w80/hr.png", "sep": "vs"},
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

    for i in range(0, 9, 3):
        cols = st.columns(3)
        for j in range(3):
            group = groups[i + j]
            with cols[j]:
                info = scenarios.get(group, {})
                status = info.get("status", "pending")
                desc = info.get("description", "경기 분석 대기 중")
                reason = info.get("reason", "아직 데이터가 없습니다")
                
                g_info = GROUP_INFO[group]

                overlay_html = ""
                if status == "success":
                    overlay_html = '<div class="overlay overlay-success">O</div>'
                elif status == "fail":
                    overlay_html = '<div class="overlay overlay-fail">X</div>'

                card_html = f"""<div class="scenario-card">{overlay_html}
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
</div>"""
                if hasattr(st, "html"):
                    st.html(card_html)
                else:
                    st.markdown(card_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
