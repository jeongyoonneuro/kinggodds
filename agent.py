import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_football_results():
    """worldcup26.ir API에서 데이터를 가져옵니다."""
    url = "https://worldcup26.ir/get/games"
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"❌ API 호출 중 오류 발생: {e}")
        return []

def extract_match_info(raw_data, team1_name, team2_name=None):
    """
    worldcup26.ir API의 실제 JSON 구조에 맞춰 조별리그 3차전 점수를 추출합니다.
    """
    # 1. API 구조에 맞게 'games' 리스트 가져오기
    data_list = raw_data.get("games", [])
    
    for match in data_list:
        # 2. 날짜 대신 'matchday: 3' (조별리그 3차전) 인 경기만 타겟팅
        if str(match.get("matchday")) != "3":
            continue
            
        home_team = match.get("home_team_name_en", "")
        away_team = match.get("away_team_name_en", "")
        
        # 3. 팀 이름(team1)이 홈 또는 어웨이에 있는지 확인
        if team1_name.lower() in home_team.lower() or team1_name.lower() in away_team.lower():
            
            # team2 이름이 조건에 있다면, 상대팀이 맞는지 확인
            if team2_name:
                if team2_name.lower() not in home_team.lower() and team2_name.lower() not in away_team.lower():
                    continue
            
            # 4. 경기 종료 여부 확인 (API 구조: 'finished' 필드가 'TRUE' 문자열임)
            is_finished = str(match.get("finished", "")).upper() == "TRUE"
            if not is_finished:
                return {"status": "pending"}
            
            # 5. 점수 추출 (정수형으로 변환)
            try:
                h_score = int(match.get("home_score", 0))
                a_score = int(match.get("away_score", 0))
            except ValueError:
                return {"status": "pending"}
                
            # team1이 홈인지 어웨이인지에 따라 점수 매핑 반환
            if team1_name.lower() in home_team.lower():
                return {"status": "finished", "team1_score": h_score, "team2_score": a_score}
            else:
                return {"status": "finished", "team1_score": a_score, "team2_score": h_score}
                
    return {"status": "pending"}  

def evaluate_scenarios(match_data):
    scenarios = {}
    total_achieved = 0

    # 코드 중복을 줄이고 점수까지 깔끔하게 저장하는 헬퍼 함수
    def add_scenario(group, status, desc, reason, t1_score="", t2_score=""):
        scenarios[group] = {
            "status": status,
            "description": desc,
            "reason": reason,
            "t1_score": t1_score,
            "t2_score": t2_score
        }

    # 1. D조 (이미지상 '꽝')
    d_match = extract_match_info(match_data, "Australia", "Paraguay")
    t1_s, t2_s = d_match.get("team1_score", ""), d_match.get("team2_score", "")
    if d_match["status"] == "pending":
        add_scenario("D조", "pending", "호주 승리 또는 파라과이 2점차 이상 승리", "호주 vs 파라과이 대기 중")
    else:
        if t1_s > t2_s:
            add_scenario("D조", "success", "호주 승리 또는 파라과이 2점차 이상 승리", f"호주 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        elif (t2_s - t1_s) >= 2:
            add_scenario("D조", "success", "호주 승리 또는 파라과이 2점차 이상 승리", f"파라과이 대승 ({t2_s}:{t1_s})", t1_s, t2_s)
            total_achieved += 1
        else:
            add_scenario("D조", "fail", "호주 승리 또는 파라과이 2점차 이상 승리", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 2. E조 (이미지상 '꽝')
    ecu_match = extract_match_info(match_data, "Ecuador", "Germany")
    cur_match = extract_match_info(match_data, "Cura", "Ivory Coast")
    if ecu_match["status"] == "pending" or cur_match["status"] == "pending":
        add_scenario("E조", "pending", "에콰도르, 퀴라소 승리 X", "경기 대기 중")
    else:
        t1_s, t2_s = ecu_match["team1_score"], cur_match["team1_score"]
        ecu_win = ecu_match["team1_score"] > ecu_match["team2_score"]
        cur_win = cur_match["team1_score"] > cur_match["team2_score"]
        if not ecu_win and not cur_win:
            add_scenario("E조", "success", "에콰도르, 퀴라소 승리 X", "조건 충족", t1_s, t2_s)
            total_achieved += 1
        else:
            failed = []
            if ecu_win: failed.append(f"에콰도르 승({ecu_match['team1_score']}:{ecu_match['team2_score']})")
            if cur_win: failed.append(f"퀴라소 승({cur_match['team1_score']}:{cur_match['team2_score']})")
            add_scenario("E조", "fail", "에콰도르, 퀴라소 승리 X", f"조건 미달성 [{', '.join(failed)}]", t1_s, t2_s)

    # 3. F조 (이미지상 '꽝')
    f_match = extract_match_info(match_data, "Japan", "Sweden")
    t1_s, t2_s = f_match.get("team1_score", ""), f_match.get("team2_score", "")
    if f_match["status"] == "pending":
        add_scenario("F조", "pending", "일본, 스웨덴에 2골차 이상 승리", "일본 vs 스웨덴 대기 중")
    else:
        if (t1_s - t2_s) >= 2:
            add_scenario("F조", "success", "일본, 스웨덴에 2골차 이상 승리", f"일본 대승 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        else:
            add_scenario("F조", "fail", "일본, 스웨덴에 2골차 이상 승리", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 4. G조: 이집트 vs 이란 -> 이집트 승리 (무승부 안됨)
    g_match = extract_match_info(match_data, "Egypt", "Iran")
    t1_s, t2_s = g_match.get("team1_score", ""), g_match.get("team2_score", "")
    if g_match["status"] == "pending":
        add_scenario("G조", "pending", "이집트 승리 (무승부 안됨)", "이집트 vs 이란 대기 중")
    else:
        if t1_s > t2_s: # 이집트 승리
            add_scenario("G조", "success", "이집트 승리 (무승부 안됨)", f"이집트 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        else:
            add_scenario("G조", "fail", "이집트 승리 (무승부 안됨)", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 5. H조: 스페인 vs 우루과이 -> 스페인 승리 (무승부 안됨)
    h_match = extract_match_info(match_data, "Spain", "Uruguay")
    t1_s, t2_s = h_match.get("team1_score", ""), h_match.get("team2_score", "")
    if h_match["status"] == "pending":
         add_scenario("H조", "pending", "스페인 승리 (무승부 안됨)", "스페인 vs 우루과이 대기 중")
    else:
         if t1_s > t2_s: # 스페인 승리
             add_scenario("H조", "success", "스페인 승리 (무승부 안됨)", f"스페인 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
             total_achieved += 1
         else:
             add_scenario("H조", "fail", "스페인 승리 (무승부 안됨)", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 6. I조: 세네갈 vs 이라크 -> 무승부 OR 세네갈 1점차 승 OR 이라크 4점차 이하 승
    i_match = extract_match_info(match_data, "Senegal", "Iraq")
    t1_s, t2_s = i_match.get("team1_score", ""), i_match.get("team2_score", "")
    if i_match["status"] == "pending":
        add_scenario("I조", "pending", "무승부, 세네갈 1점차 승, 이라크 4점차 이하 승", "세네갈 vs 이라크 대기 중")
    else:
        if t1_s == t2_s: # 무승부
            add_scenario("I조", "success", "무승부, 세네갈 1점차 승, 이라크 4점차 이하 승", f"무승부 충족 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        elif (t1_s - t2_s) == 1: # 세네갈 1점차 승리
            add_scenario("I조", "success", "무승부, 세네갈 1점차 승, 이라크 4점차 이하 승", f"세네갈 1점차 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        elif 0 < (t2_s - t1_s) <= 4: # 이라크 1~4점차 승리
            add_scenario("I조", "success", "무승부, 세네갈 1점차 승, 이라크 4점차 이하 승", f"이라크 4점차 이하 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        else:
            add_scenario("I조", "fail", "무승부, 세네갈 1점차 승, 이라크 4점차 이하 승", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 7. J조: 오스트리아 vs 알제리 -> 오스트리아 승리 OR 알제리 2점차 이상 승리
    j_match = extract_match_info(match_data, "Austria", "Algeria")
    t1_s, t2_s = j_match.get("team1_score", ""), j_match.get("team2_score", "")
    if j_match["status"] == "pending":
        add_scenario("J조", "pending", "오스트리아 승리 또는 알제리 2점차 이상 승", "오스트리아 vs 알제리 대기 중")
    else:
        if t1_s > t2_s: # 오스트리아 승리
            add_scenario("J조", "success", "오스트리아 승리 또는 알제리 2점차 이상 승", f"오스트리아 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        elif (t2_s - t1_s) >= 2: # 알제리 2점차 이상 승리
            add_scenario("J조", "success", "오스트리아 승리 또는 알제리 2점차 이상 승", f"알제리 2점차 이상 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
            total_achieved += 1
        else:
            add_scenario("J조", "fail", "오스트리아 승리 또는 알제리 2점차 이상 승", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 8. K조: 콩고 vs 우즈베키스탄 -> 무승부 OR 우즈베키스탄 승리 (6점차 이하)
    k_match = extract_match_info(match_data, "Congo", "Uzbekistan")
    t1_s, t2_s = k_match.get("team1_score", ""), k_match.get("team2_score", "")
    if k_match["status"] == "pending":
         add_scenario("K조", "pending", "무승부 또는 우즈벡 6점차 이하 승리", "콩고 vs 우즈벡 대기 중")
    else:
         if t1_s == t2_s: # 무승부
             add_scenario("K조", "success", "무승부 또는 우즈벡 6점차 이하 승리", f"무승부 충족 ({t1_s}:{t2_s})", t1_s, t2_s)
             total_achieved += 1
         elif 0 < (t2_s - t1_s) <= 6: # 우즈베키스탄 1~6점차 승리
             add_scenario("K조", "success", "무승부 또는 우즈벡 6점차 이하 승리", f"우즈벡 6점차 이하 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
             total_achieved += 1
         else:
             add_scenario("K조", "fail", "무승부 또는 우즈벡 6점차 이하 승리", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    # 9. L조: 가나 vs 크로아티아 -> 가나 승리 (무승부 안됨)
    l_match = extract_match_info(match_data, "Ghana", "Croatia")
    t1_s, t2_s = l_match.get("team1_score", ""), l_match.get("team2_score", "")
    if l_match["status"] == "pending":
         add_scenario("L조", "pending", "가나 승리 (무승부 안됨)", "가나 vs 크로아티아 대기 중")
    else:
         if t1_s > t2_s:
             add_scenario("L조", "success", "가나 승리 (무승부 안됨)", f"가나 승리 ({t1_s}:{t2_s})", t1_s, t2_s)
             total_achieved += 1
         else:
             add_scenario("L조", "fail", "가나 승리 (무승부 안됨)", f"조건 미달성 ({t1_s}:{t2_s})", t1_s, t2_s)

    return {
        "total_achieved": total_achieved,
        "scenarios": scenarios,
        "ai_comment": f"각 조별 상대팀 매치업 및 디테일 로직 업데이트 완료. 현재 총 {total_achieved}개의 조건이 달성되었습니다!"
                  }

def main():
    print("⚽ [1/3] API 경기 결과 수집 중...")
    match_data = get_football_results()
    print(match_data)

    print("⚡ [2/3] 파이썬 로직 기반 경우의 수 계산 중 (0.01초)...")
    scenario_results = evaluate_scenarios(match_data)

    print("💾 [3/3] 결과를 data/results.json에 저장 중...")
    os.makedirs("data", exist_ok=True)
    with open("data/results.json", "w", encoding="utf-8") as f:
        json.dump(scenario_results, f, ensure_ascii=False, indent=4)

    print(f"✅ 즉각 업데이트 완료! (현재 달성: {scenario_results['total_achieved']}개)")

if __name__ == "__main__":
    main()
