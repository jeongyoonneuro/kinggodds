import os
import json
import requests
import google.generativeai as genai

# 1. 환경 변수 설정 (GitHub Secrets 또는 로컬 .env에서 가져옴)
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def get_football_results():
    """API-Football에서 최신 경기 결과를 가져오는 함수"""
    # 실제 API 호출 코드 예시 (주석 해제 후 사용)
    # url = "https://v3.football.api-sports.io/fixtures?date=2026-06-26"
    # headers = {
    #     'x-apisports-key': FOOTBALL_API_KEY
    # }
    # response = requests.get(url, headers=headers)
    # return response.json()

    # 당장 로컬 테스트를 위해 가짜(Mock) 데이터 반환
    return {
        "matches": [
            {"home": "호주", "away": "덴마크", "home_score": 2, "away_score": 1, "status": "FT"},
            {"home": "에콰도르", "away": "세네갈", "home_score": 1, "away_score": 1, "status": "FT"}
        ]
    }

def analyze_scenarios_with_gemini(match_data):
    """Gemini API를 사용하여 경우의 수 달성 여부를 분석하는 함수"""
    # 최신 모델 사용
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    너는 축구 데이터 분석 전문가야.
    아래 경기 결과를 바탕으로 한국의 32강 진출을 위한 9가지 조별 시나리오 달성 여부를 판단해줘.

    [현재 경기 결과]
    {json.dumps(match_data, ensure_ascii=False)}

    [한국에 유리한 9가지 시나리오 (이 중 3개 이상 달성 시 진출)]
    1. D조: 호주 승리 또는 파라과이 2점차 이상 승리
    2. E조: 에콰도르, 퀴라소 승리 X
    3. F조: 일본, 스웨덴에 2골차 이상 승리
    4. G조: 벨기에 승리 + 이집트 승리
    5. H조: 스페인 승리 + 사우디 승리
    6. I조: 세네갈 또는 이라크 대승만 아니면 OK (3점차 이상 승리 금지)
    7. J조: 오스트리아 승리
    8. K조: 콩고민주공화국, 우즈벡전 무승부 또는 패배
    9. L조: 가나 승리

    반드시 아래 JSON 형식으로만 응답해. 마크다운(` ```json `) 없이 순수 JSON 텍스트만 출력해야 해.
    {{
        "total_achieved": 1,
        "scenarios": {{
            "D조": {{"status": "success", "description": "호주 승리 또는 파라과이 2점차 이상 승리", "reason": "호주가 2:1로 승리함"}},
            "E조": {{"status": "pending", "description": "에콰도르, 퀴라소 승리 X", "reason": "아직 두 팀의 경기가 완전히 종료되지 않음"}},
            "F조": {{"status": "pending", "description": "일본, 스웨덴에 2골차 이상 승리", "reason": "경기 전"}}
        }},
        "ai_comment": "D조 조건이 성공적으로 달성되었습니다! 남은 8개 중 2개만 더 맞으면 진출합니다."
    }}
    """

    response = model.generate_content(prompt)
    
    # Gemini가 혹시라도 마크다운 텍스트를 붙여서 주면 제거하는 클렌징 작업
    result_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(result_text)

def main():
    print("⚽ [1/3] 경기 결과 수집 중...")
    match_data = get_football_results()

    print("🧠 [2/3] Gemini AI 분석 중...")
    scenario_results = analyze_scenarios_with_gemini(match_data)

    print("💾 [3/3] 결과를 data/results.json에 저장 중...")
    os.makedirs("data", exist_ok=True)
    with open("data/results.json", "w", encoding="utf-8") as f:
        json.dump(scenario_results, f, ensure_ascii=False, indent=4)

    print("✅ 데이터 업데이트 완료!")

if __name__ == "__main__":
    main()
