import streamlit as st
import json
import os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="한국 32강 경우의 수 대시보드",
    page_icon="🇰🇷",
    layout="centered"
)

def load_data():
    """업데이트된 JSON 데이터 불러오기"""
    file_path = "data/results.json"
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("🇰🇷 한국 32강 경우의 수 총 정리")
    st.markdown("#### 9가지 조별 시나리오 중 **3개**만 맞으면 32강 진출!")

    data = load_data()

    if not data:
        st.warning("아직 수집된 경기 결과가 없습니다. 업데이트를 기다려주세요.")
        return

    # 2. 요약 대시보드 영역
    total_achieved = data.get("total_achieved", 0)
    
    # 진행률 시각화 (3개 달성 시 100%)
    progress_value = min(total_achieved / 3.0, 1.0)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="현재 달성된 경우의 수", value=f"{total_achieved} 개", delta=f"{3 - total_achieved}개 남음!" if total_achieved < 3 else "진출 확정!", delta_color="normal")
    with col2:
        st.write("진출 달성률")
        st.progress(progress_value)

    st.info(f"**🤖 AI 코멘트:** {data.get('ai_comment', '')}")

    st.markdown("---")
    st.subheader("📊 각 조별 시나리오 현황")

    # 3. 조별 현황 리스트 (상태에 따라 아이콘 변경)
    status_mapping = {
        "success": ("✅", "달성 성공", "success"),
        "fail": ("❌", "달성 실패", "error"),
        "pending": ("⏳", "대기 중", "secondary")
    }

    scenarios = data.get("scenarios", {})

    # 전체 조 리스트 (알파벳 순서 보장)
    groups = ["D조", "E조", "F조", "G조", "H조", "I조", "J조", "K조", "L조"]

    for group in groups:
        if group in scenarios:
            info = scenarios[group]
            status = info.get("status", "pending")
            icon, status_text, _ = status_mapping.get(status, status_mapping["pending"])

            # Streamlit Expander를 활용한 카드 UI
            with st.expander(f"{icon} **{group}** | {status_text}"):
                st.write(f"**목표 조건:** {info.get('description', '')}")
                st.write(f"**현재 상황:** {info.get('reason', '')}")
        else:
            # 아직 JSON에 데이터가 없을 경우 기본값 노출
            with st.expander(f"⏳ **{group}** | 대기 중"):
                st.write("경기 대기 중이거나 아직 분석되지 않았습니다.")

if __name__ == "__main__":
    main()
