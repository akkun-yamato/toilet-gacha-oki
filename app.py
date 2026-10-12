import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
import json
from database import init_db, get_members, save_result, get_history, reset_round, clear_history
from gacha import draw_all

st.set_page_config(page_title="YAMATO 神々の情熱 トイレ掃除ガチャ", page_icon="🎰", layout="wide")
init_db()

st.markdown("""
<style>
.stApp {
    background: radial-gradient(ellipse at top, #2a0845 0%, #000 100%);
    color: white;
}
h1 {
    text-align: center;
    color: #ffd700;
    text-shadow: 2px 2px 0 #c71585, 4px 4px 10px rgba(0,0,0,0.8);
    font-size: 2.3em !important;
    letter-spacing: 2px;
}
.date-display {
    text-align: center;
    color: #ffd700;
    font-size: 1.2em;
    margin-bottom: 15px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
}
.stButton>button {
    background: linear-gradient(180deg, #ffd700 0%, #ff8c00 50%, #c71585 100%);
    color: #fff;
    border: 3px solid #ffd700;
    border-radius: 50px;
    font-size: 1.4em;
    font-weight: bold;
    padding: 12px 30px;
    box-shadow: 0 6px 20px rgba(255,215,0,0.5), inset 0 2px 10px rgba(255,255,255,0.3);
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    letter-spacing: 2px;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 30px rgba(255,215,0,0.8);
}
.winner-card {
    background: linear-gradient(135deg, #fff8dc 0%, #ffe4b5 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 10px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.5), inset 0 0 10px rgba(255,215,0,0.3);
    color: #333;
    min-height: 140px;
    border: 3px solid #ffd700;
}
.role-men { border-top: 8px solid #4a90e2; }
.role-guest { border-top: 8px solid #ff8c00; }
.role-women { border-top: 8px solid #ff1493; }
.stCheckbox label { font-size: 18px !important; font-weight: bold !important; color: white !important; }
[data-testid="stExpander"] { background: rgba(0,0,0,0.5); border-radius: 10px; border: 1px solid #ffd700; }
[data-testid="stExpander"] summary { color: #ffd700 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎰 YAMATO 神々の情熱 トイレ掃除ガチャ 🎰</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'>📅 {date.today().strftime('%Y年%m月%d日')}</div>", unsafe_allow_html=True)

if "absent" not in st.session_state: st.session_state.absent = []
if "results" not in st.session_state: st.session_state.results = None
if "show_slot" not in st.session_state: st.session_state.show_slot = False

with st.expander("👥 本日の不在者チェック"):
    absent = []
    men = get_members("M")
    women = get_members("F")
    st.markdown("**🚹 男性**")
    cols = st.columns(4)
    for i, name in enumerate(men):
        if cols[i % 4].checkbox(name, key=f"abs_m_{name}"):
            absent.append(name)
    st.markdown("**🚺 女子**")
    cols = st.columns(4)
    for i, name in enumerate(women):
        if cols[i % 4].checkbox(name, key=f"abs_w_{name}"):
            absent.append(name)
    st.session_state.absent = absent
    if absent:
        st.info(f"本日の不在者: {len(absent)}名")

if st.button("🕹️ レバーON！ 🎰", use_container_width=True):
    st.session_state.results = draw_all(st.session_state.absent)
    st.session_state.show_slot = True
    st.rerun()

if st.session_state.show_slot and st.session_state.results:
    results = st.session_state.results
    men_winner = results.get("Men", "該当者なし")
    guest_winner = results.get("Guest", "該当者なし")
    women_winner = results.get("Women", "該当者なし")

    all_men = [n for n in get_members("M") if n not in st.session_state.absent]
    all_women = [n for n in get_members("F") if n not in st.session_state.absent]
    if not all_men: all_men = ["---"]
    if not all_women: all_women = ["---"]

    men_reel_list = list(all_men)
    guest_reel_list = list(all_men)
    women_reel_list = list(all_women)
    if men_winner not in men_reel_list and men_winner != "該当者なし":
        men_reel_list.append(men_winner)
    if guest_winner not in guest_reel_list and guest_winner != "該当者なし":
        guest_reel_list.append(guest_winner)
    if women_winner not in women_reel_list and women_winner != "該当者なし":
        women_reel_list.append(women_winner)

    men_list = json.dumps(men_reel_list, ensure_ascii=False)
    guest_list = json.dumps(guest_reel_list, ensure_ascii=False)
    women_list = json.dumps(women_reel_list, ensure_ascii=False)
    men_win_js = json.dumps(men_winner, ensure_ascii=False)
    guest_win_js = json.dumps(guest_winner, ensure_ascii=False)
    women_win_js = json.dumps(women_winner, ensure_ascii=False)

    img_normal = "https://raw.githubusercontent.com/akkun-yamato/toilet-gacha-oki/main/yamato-god2-normal.png"
    img_peka = "https://raw.githubusercontent.com/akkun-yamato/toilet-gacha-oki/main/yamato-god2-peka.png"

    slot_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    padding: 0;
    background: radial-gradient(ellipse at center, #2a0845 0%, #000 100%);
    font-family: 'Arial Black', 'Impact', sans-serif;
    overflow: hidden;
}}
.cabinet-wrap {{
    position: relative;
    width: 480px;
    height: 600px;
    margin: 10px auto;
}}
.cabinet-bg {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: url('{img_normal}');
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
    z-index: 1;
}}
.cabinet-peka {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: url('{img_peka}');
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0;
    z-index: 2;
    transition: opacity 0.3s;
}}
.cabinet-peka.show {{
    opacity: 1;
    animation: pekaFlash 0.3s infinite alternate, rainbowHue 2s linear infinite;
}}
@keyframes pekaFlash {{
    0% {{ filter: brightness(1) saturate(1); }}
    100% {{ filter: brightness(1.5) saturate(1.5) drop-shadow(0 0 25px #ffd700); }}
}}
@keyframes rainbowHue {{
    0% {{ filter: hue-rotate(0deg) brightness(1.3) saturate(1.5); }}
    100% {{ filter: hue-rotate(360deg) brightness(1.3) saturate(1.5); }}
}}
.reels {{
    position: absolute;
    top: 232px;
    left: 148px;
    width: 212px;
    height: 108px;
    display: flex;
    gap: 2px;
    z-index: 5;
}}
.reel {{
    flex: 1;
    overflow: hidden;
    background: linear-gradient(180deg, #fff8e1 0%, #fff 50%, #fff8e1 100%);
    position: relative;
    border-radius: 2px;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
}}
.reel-inner {{
    position: absolute;
    width: 100%;
    top: 0;
    left: 0;
}}
.reel-item {{
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 900;
    color: #4a0e4e;
    border-bottom: 1px dashed #ccc;
    background: linear-gradient(180deg, transparent 0%, rgba(255,215,0,0.08) 100%);
    text-shadow: 1px 1px 0 rgba(255,255,255,0.8);
    letter-spacing: 1px;
}}
.reel-item.winner {{
    color: #c71585;
    background: linear-gradient(90deg, #ffd700 0%, #fff 50%, #ffd700 100%);
    text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff, 0 0 8px #ffd700;
    font-weight: 900;
    animation: winnerGlow 0.5s infinite alternate;
}}
@keyframes winnerGlow {{
    0% {{ box-shadow: inset 0 0 10px rgba(255,215,0,0.5); }}
    100% {{ box-shadow: inset 0 0 20px rgba(255,215,0,1), 0 0 15px #ffd700; }}
}}
.reel-glass {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.4) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.3) 100%);
    pointer-events: none;
    z-index: 3;
}}
.center-line {{
    position: absolute;
    top: 268px;
    left: 148px;
    width: 212px;
    height: 36px;
    border-top: 2px solid rgba(255,20,147,0.5);
    border-bottom: 2px solid rgba(255,20,147,0.5);
    pointer-events: none;
    z-index: 6;
}}
.jackpot {{
    position: absolute;
    bottom: -40px;
    left: 0; right: 0;
    text-align: center;
    font-size: 28px;
    font-weight: 900;
    text-shadow: 2px 2px 0 #c71585, 4px 4px 15px #ff1493;
    opacity: 0;
    letter-spacing: 3px;
    z-index: 10;
    color: #ffd700;
}}
.jackpot.show {{
    opacity: 1;
    animation: jackpotPulse 0.4s infinite alternate, rainbowText 2s linear infinite;
}}
@keyframes jackpotPulse {{
    0% {{ transform: scale(1); }}
    100% {{ transform: scale(1.2); }}
}}
@keyframes rainbowText {{
    0% {{ color: #ff0000; }}
    16% {{ color: #ff8c00; }}
    33% {{ color: #ffd700; }}
    50% {{ color: #00ff00; }}
    66% {{ color: #00bfff; }}
    83% {{ color: #ff00ff; }}
    100% {{ color: #ff0000; }}
}}
@media (max-width: 600px) {{
    .cabinet-wrap {{
        width: 320px;
        height: 400px;
    }}
    .reels {{
        top: 155px;
        left: 99px;
        width: 141px;
        height: 72px;
    }}
    .reel-item {{ height: 24px; font-size: 11px; }}
    .center-line {{ top: 179px; left: 99px; width: 141px; height: 24px; }}
    .jackpot {{ font-size: 20px; }}
}}
</style>
</head>
<body>
<div class="cabinet-wrap">
    <div class="cabinet-bg"></div>
    <div class="cabinet-peka" id="peka"></div>
    <div class="reels">
        <div class="reel"><div class="reel-inner" id="reel1"></div><div class="reel-glass"></div></div>
        <div class="reel"><div class="reel-inner" id="reel2"></div><div class="reel-glass"></div></div>
        <div class="reel"><div class="reel-inner" id="reel3"></div><div class="reel-glass"></div></div>
    </div>
    <div class="center-line"></div>
    <div class="jackpot" id="jackpot">✨ 当選確定！ ✨</div>
</div>
<script>
const menList = {men_list};
const guestList = {guest_list};
const womenList = {women_list};
const menWin = {men_win_js};
const guestWin = {guest_win_js};
const womenWin = {women_win_js};

const isMobile = window.innerWidth <= 600;
const itemHeight = isMobile ? 24 : 36;

function buildReel(list, winner) {{
    const loops = 30;
    let html = '';
    for (let i = 0; i < loops; i++) {{
        const shuffled = [...list].sort(() => Math.random() - 0.5);
        for (let name of shuffled) {{
            html += `<div class="reel-item">${{name}}</div>`;
        }}
    }}
    const dummy1 = list.find(n => n !== winner) || list[0];
    const dummy2 = list.find(n => n !== winner && n !== dummy1) || list[0];
    html += `<div class="reel-item">${{dummy1}}</div>`;
    html += `<div class="reel-item winner">${{winner}}</div>`;
    html += `<div class="reel-item">${{dummy2}}</div>`;
    return html;
}}

const reel1 = document.getElementById('reel1');
const reel2 = document.getElementById('reel2');
const reel3 = document.getElementById('reel3');

reel1.innerHTML = buildReel(menList, menWin);
reel2.innerHTML = buildReel(guestList, guestWin);
reel3.innerHTML = buildReel(womenList, womenWin);

function getStopPos(reel) {{
    const winnerItem = reel.querySelector('.reel-item.winner');
    const idx = Array.from(reel.querySelectorAll('.reel-item')).indexOf(winnerItem);
    return -(idx * itemHeight - itemHeight);
}}

const d1 = 2000, d2 = 3500, d3 = 5000;

setTimeout(() => {{
    reel1.style.transition = `top ${{d1/1000}}s cubic-bezier(0.33, 0, 0.2, 1)`;
    reel1.style.top = getStopPos(reel1) + 'px';
}}, 500);
setTimeout(() => {{
    reel2.style.transition = `top ${{d2/1000}}s cubic-bezier(0.33, 0, 0.2, 1)`;
    reel2.style.top = getStopPos(reel2) + 'px';
}}, 500);
setTimeout(() => {{
    reel3.style.transition = `top ${{d3/1000}}s cubic-bezier(0.33, 0, 0.2, 1)`;
    reel3.style.top = getStopPos(reel3) + 'px';
}}, 500);

setTimeout(() => {{
    document.getElementById('peka').classList.add('show');
    document.getElementById('jackpot').classList.add('show');
}}, 500 + d3 + 300);
</script>
</body>
</html>
"""
    components.html(slot_html, height=680)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='winner-card role-men'><h3>🚹 男性トイレ</h3><h2>{men_winner}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='winner-card role-guest'><h3>🚻 ゲストトイレ</h3><h2>{guest_winner}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='winner-card role-women'><h3>🚺 女子トイレ</h3><h2>{women_winner}</h2></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 引き直す", use_container_width=True):
            st.session_state.results = draw_all(st.session_state.absent)
            st.rerun()
    with col_b:
        if st.button("✅ この結果で確定！", use_container_width=True):
            save_result(st.session_state.results)
            st.success("保存しました！お疲れさまでした🎉")
            st.session_state.results = None
            st.session_state.show_slot = False
            time.sleep(2)
            st.rerun()

with st.expander("📋 直近7日の履歴"):
    history = get_history(7)
    if history:
        from collections import defaultdict
        grouped = defaultdict(dict)
        for d, role, name in history:
            grouped[d][role] = name
        for d in sorted(grouped.keys(), reverse=True):
            row = grouped[d]
            st.write(f"**{d}** 🚹{row.get('Men','-')} / 🚻{row.get('Guest','-')} / 🚺{row.get('Women','-')}")
    else:
        st.write("履歴なし")

with st.expander("⚙️ 管理メニュー"):
    st.markdown("**危険な操作⚠️**")
    confirm_r = st.checkbox("全周リセットを実行する（確認）", key="confirm_r")
    if st.button("🔄 全周リセット実行"):
        if confirm_r:
            reset_round()
            st.success("リセット完了！")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("チェックボックスにチェックを入れてください")
    confirm_h = st.checkbox("履歴を全削除する（確認）", key="confirm_h")
    if st.button("🗑️ 履歴を全削除"):
        if confirm_h:
            clear_history()
            st.success("履歴を削除しました！")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("チェックボックスにチェックを入れてください")
