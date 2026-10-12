import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
import json
from database import init_db, get_members, save_result, get_history, reset_round, clear_history
from gacha import draw_all

st.set_page_config(page_title="沖ドキ風 トイレ掃除ガチャ", page_icon="🌺", layout="wide")
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
    text-shadow: 2px 2px 0 #ff1493, 4px 4px 10px rgba(0,0,0,0.8);
    font-size: 2.5em !important;
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

st.markdown("<h1>🌺 沖ドキ風 トイレ掃除ガチャ 🌺</h1>", unsafe_allow_html=True)
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

    men_list = json.dumps(all_men, ensure_ascii=False)
    women_list = json.dumps(all_women, ensure_ascii=False)
    men_win_js = json.dumps(men_winner, ensure_ascii=False)
    guest_win_js = json.dumps(guest_winner, ensure_ascii=False)
    women_win_js = json.dumps(women_winner, ensure_ascii=False)

    slot_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    padding: 10px;
    background: radial-gradient(ellipse at center, #2a0845 0%, #000 100%);
    font-family: 'Arial Black', 'Impact', sans-serif;
    overflow: hidden;
}}
.cabinet {{
    max-width: 480px;
    margin: 0 auto;
    position: relative;
    background: linear-gradient(180deg, #4a0e4e 0%, #2a0845 50%, #1a0033 100%);
    border-radius: 15px 15px 25px 25px;
    padding: 10px;
    box-shadow: 0 0 60px rgba(255,20,147,0.6), inset 0 0 30px rgba(0,0,0,0.5);
    border: 3px solid #ffd700;
}}
.top-vent {{
    display: flex;
    justify-content: space-between;
    height: 20px;
    background: repeating-linear-gradient(90deg, #333 0 3px, #111 3px 6px);
    border-radius: 10px 10px 0 0;
    margin-bottom: 5px;
}}
.bonus-plate {{
    background: linear-gradient(180deg, #ffd700 0%, #ff8c00 50%, #8b4513 100%);
    border: 3px solid #ffd700;
    border-radius: 10px;
    padding: 5px;
    text-align: center;
    margin: 0 auto 8px;
    width: 60%;
    box-shadow: 0 0 20px #ffd700, inset 0 0 10px rgba(255,255,255,0.5);
}}
.bonus-plate .text {{
    color: #8b0000;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 3px;
    text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff;
    font-style: italic;
}}
.hibiscus-panel {{
    background: linear-gradient(180deg, #1a0033 0%, #2a0845 100%);
    border: 3px solid #ffd700;
    border-radius: 10px;
    padding: 10px 5px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.8), 0 0 15px rgba(255,215,0,0.3);
    position: relative;
}}
.hibiscus-panel::before {{
    content: 'OKI-DOKI';
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #ffd700;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    text-shadow: 0 0 5px #ff1493;
}}
.hibiscus-panel::after {{
    content: 'OKI-DOKI';
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #ffd700;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    text-shadow: 0 0 5px #ff1493;
}}
.flower {{
    width: 42px;
    height: 42px;
    position: relative;
    filter: brightness(0.3) saturate(0.5);
    transition: all 0.2s;
}}
.flower.lit {{
    filter: brightness(1.3) saturate(1.5) drop-shadow(0 0 15px #ff1493);
    animation: flowerPulse 0.3s infinite alternate;
}}
@keyframes flowerPulse {{
    0% {{ transform: scale(1) rotate(0deg); }}
    100% {{ transform: scale(1.15) rotate(5deg); }}
}}
.petal {{
    position: absolute;
    width: 20px;
    height: 20px;
    background: radial-gradient(circle at 30% 30%, #ff6b6b 0%, #c70000 70%, #8b0000 100%);
    border-radius: 50% 10% 50% 10%;
    left: 50%;
    top: 50%;
    transform-origin: 0 0;
}}
.petal:nth-child(1) {{ transform: rotate(0deg) translate(-50%, -100%); }}
.petal:nth-child(2) {{ transform: rotate(72deg) translate(-50%, -100%); }}
.petal:nth-child(3) {{ transform: rotate(144deg) translate(-50%, -100%); }}
.petal:nth-child(4) {{ transform: rotate(216deg) translate(-50%, -100%); }}
.petal:nth-child(5) {{ transform: rotate(288deg) translate(-50%, -100%); }}
.flower-center {{
    position: absolute;
    width: 10px;
    height: 10px;
    background: radial-gradient(circle, #ffeb3b 0%, #ff8c00 100%);
    border-radius: 50%;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 2;
    box-shadow: 0 0 8px #ffd700;
}}
.reel-frame {{
    background: linear-gradient(180deg, #ffd700 0%, #ff8c00 50%, #8b4513 100%);
    padding: 6px;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(255,215,0,0.5), inset 0 0 10px rgba(0,0,0,0.5);
    margin-bottom: 8px;
}}
.reels {{
    display: flex;
    gap: 4px;
    background: #000;
    padding: 4px;
    border-radius: 6px;
    position: relative;
}}
.reel {{
    flex: 1;
    height: 180px;
    overflow: hidden;
    background: linear-gradient(180deg, #fff 0%, #f0f0f0 50%, #fff 100%);
    border-radius: 4px;
    position: relative;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
}}
.reel-inner {{
    position: absolute;
    width: 100%;
    top: 0;
    left: 0;
}}
.reel-item {{
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 900;
    color: #333;
    border-bottom: 1px dashed #ccc;
    background: linear-gradient(90deg, transparent 0%, rgba(255,215,0,0.1) 50%, transparent 100%);
}}
.reel-item.winner {{
    color: #c71585;
    background: linear-gradient(90deg, #ffd700 0%, #fff 50%, #ffd700 100%);
    text-shadow: 1px 1px 0 #fff;
}}
.center-line {{
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    height: 60px;
    border-top: 2px solid #ff1493;
    border-bottom: 2px solid #ff1493;
    pointer-events: none;
    z-index: 5;
    box-shadow: 0 0 10px #ff1493;
}}
.reel-glass {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.3) 100%);
    pointer-events: none;
    z-index: 4;
}}
.roles {{
    display: flex;
    justify-content: space-around;
    margin: 5px 0 8px;
    color: #ffd700;
    font-weight: 900;
    text-shadow: 1px 1px 2px #000;
    font-size: 13px;
    letter-spacing: 1px;
}}
.score-panel {{
    background: #000;
    border: 2px solid #ffd700;
    border-radius: 5px;
    padding: 5px;
    display: flex;
    justify-content: space-around;
    margin-bottom: 8px;
}}
.score-box {{
    text-align: center;
}}
.score-box .label {{
    color: #ffd700;
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 1px;
}}
.score-box .num {{
    color: #ff0000;
    font-size: 24px;
    font-family: 'Courier New', monospace;
    font-weight: 900;
    text-shadow: 0 0 8px #ff0000;
    background: #220000;
    padding: 2px 8px;
    border-radius: 3px;
    min-width: 30px;
    display: inline-block;
}}
.controls {{
    background: linear-gradient(180deg, #8b4513 0%, #654321 100%);
    border-radius: 8px;
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);
    border: 2px solid #ffd700;
    margin-bottom: 8px;
}}
.stop-buttons {{
    display: flex;
    gap: 15px;
}}
.stop-btn {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ff6b6b 0%, #c00 60%, #600 100%);
    border: 2px solid #333;
    box-shadow: 0 3px 6px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.4);
}}
.lever {{
    width: 40px;
    height: 110px;
    position: relative;
}}
.lever-stick {{
    position: absolute;
    bottom: 0;
    left: 50%;
    transform-origin: bottom center;
    width: 8px;
    height: 90px;
    background: linear-gradient(90deg, #666 0%, #ddd 50%, #666 100%);
    margin-left: -4px;
    border-radius: 4px;
    animation: leverDown 0.6s ease-in-out forwards;
}}
.lever-ball {{
    position: absolute;
    top: -12px;
    left: 50%;
    margin-left: -16px;
    width: 32px;
    height: 32px;
    background: radial-gradient(circle at 30% 30%, #ff8080 0%, #c00 70%, #600 100%);
    border-radius: 50%;
    box-shadow: 0 2px 5px rgba(0,0,0,0.6), inset 0 2px 4px rgba(255,255,255,0.4);
}}
@keyframes leverDown {{
    0% {{ transform: rotate(0deg); }}
    40% {{ transform: rotate(55deg); }}
    100% {{ transform: rotate(0deg); }}
}}
.gold-logo {{
    text-align: center;
    background: linear-gradient(180deg, #ffd700 0%, #ff8c00 100%);
    border: 3px solid #ffd700;
    border-radius: 10px;
    padding: 8px;
    box-shadow: 0 0 20px #ffd700, inset 0 0 10px rgba(255,255,255,0.4);
}}
.gold-logo .text {{
    color: #8b0000;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 3px;
    text-shadow: 1px 1px 0 #fff;
    font-style: italic;
}}
.jackpot {{
    text-align: center;
    margin-top: 10px;
    font-size: 24px;
    color: #ffd700;
    font-weight: 900;
    text-shadow: 2px 2px 0 #ff1493, 4px 4px 10px #000;
    opacity: 0;
    letter-spacing: 2px;
}}
.jackpot.show {{
    opacity: 1;
    animation: jackpotPulse 0.4s infinite alternate;
}}
@keyframes jackpotPulse {{
    0% {{ transform: scale(1); color: #ffd700; }}
    100% {{ transform: scale(1.2); color: #fff; }}
}}
@media (max-width: 600px) {{
    .cabinet {{ max-width: 95%; }}
    .reel {{ height: 150px; }}
    .reel-item {{ height: 50px; font-size: 14px; }}
    .center-line {{ top: 50px; height: 50px; }}
    .flower {{ width: 32px; height: 32px; }}
    .petal {{ width: 15px; height: 15px; }}
    .flower-center {{ width: 8px; height: 8px; }}
    .bonus-plate .text {{ font-size: 18px; }}
    .gold-logo .text {{ font-size: 16px; }}
    .jackpot {{ font-size: 18px; }}
    .lever {{ width: 32px; height: 90px; }}
    .lever-stick {{ height: 70px; }}
    .lever-ball {{ width: 26px; height: 26px; margin-left: -13px; }}
    .stop-btn {{ width: 28px; height: 28px; }}
    .stop-buttons {{ gap: 10px; }}
}}
</style>
</head>
<body>
<div class="cabinet">
    <div class="top-vent"></div>
    <div class="bonus-plate"><div class="text">BIG BONUS</div></div>
    <div class="hibiscus-panel">
        <div class="flower" id="f1"><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="flower-center"></div></div>
        <div class="flower" id="f2"><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="flower-center"></div></div>
        <div class="flower" id="f3"><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="flower-center"></div></div>
        <div class="flower" id="f4"><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="flower-center"></div></div>
        <div class="flower" id="f5"><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="petal"></div><div class="flower-center"></div></div>
    </div>
    <div class="reel-frame">
        <div class="reels">
            <div class="reel"><div class="reel-inner" id="reel1"></div><div class="reel-glass"></div></div>
            <div class="reel"><div class="reel-inner" id="reel2"></div><div class="reel-glass"></div></div>
            <div class="reel"><div class="reel-inner" id="reel3"></div><div class="reel-glass"></div></div>
            <div class="center-line"></div>
        </div>
    </div>
    <div class="roles"><span>🚹 男性</span><span>🚻 ゲスト</span><span>🚺 女子</span></div>
    <div class="score-panel">
        <div class="score-box"><div class="label">LEFT</div><div class="num" id="s1">0</div></div>
        <div class="score-box"><div class="label">CENTER</div><div class="num" id="s2">0</div></div>
        <div class="score-box"><div class="label">RIGHT</div><div class="num" id="s3">0</div></div>
    </div>
    <div class="controls">
        <div class="stop-buttons">
            <div class="stop-btn"></div>
            <div class="stop-btn"></div>
            <div class="stop-btn"></div>
        </div>
        <div class="lever"><div class="lever-stick"><div class="lever-ball"></div></div></div>
    </div>
    <div class="gold-logo"><div class="text">OKI-DOKI GOLD</div></div>
    <div class="jackpot" id="jackpot">✨ 当選確定！ ✨</div>
</div>
<script>
const menList = {men_list};
const womenList = {women_list};
const menWin = {men_win_js};
const guestWin = {guest_win_js};
const womenWin = {women_win_js};

const flowers = ['f1','f2','f3','f4','f5'].map(id => document.getElementById(id));
flowers.forEach(f => f.classList.add('lit'));

const isMobile = window.innerWidth <= 600;
const itemHeight = isMobile ? 50 : 60;

function buildReel(list, winner) {{
    const loops = 25;
    let html = '';
    for (let i = 0; i < loops; i++) {{
        for (let name of list) {{
            html += `<div class="reel-item">${{name}}</div>`;
        }}
    }}
    html += `<div class="reel-item">${{list[0]}}</div>`;
    html += `<div class="reel-item winner">${{winner}}</div>`;
    html += `<div class="reel-item">${{list[0] || '---'}}</div>`;
    return html;
}}

const reel1 = document.getElementById('reel1');
const reel2 = document.getElementById('reel2');
const reel3 = document.getElementById('reel3');

reel1.innerHTML = buildReel(menList, menWin);
reel2.innerHTML = buildReel(menList, guestWin);
reel3.innerHTML = buildReel(womenList, womenWin);

function getStopPos(reel) {{
    const items = reel.querySelectorAll('.reel-item');
    const winnerItem = reel.querySelector('.reel-item.winner');
    const idx = Array.from(items).indexOf(winnerItem);
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

// 数字パネルのランダム点滅→確定
const s1 = document.getElementById('s1'), s2 = document.getElementById('s2'), s3 = document.getElementById('s3');
const scoreTimer = setInterval(() => {{
    s1.textContent = Math.floor(Math.random()*10);
    s2.textContent = Math.floor(Math.random()*10);
    s3.textContent = Math.floor(Math.random()*10);
}}, 80);

setTimeout(() => {{ s1.textContent = Math.floor(Math.random()*10); }}, 500 + d1);
setTimeout(() => {{ s2.textContent = Math.floor(Math.random()*10); }}, 500 + d2);
setTimeout(() => {{
    clearInterval(scoreTimer);
    s3.textContent = Math.floor(Math.random()*10);
    document.getElementById('jackpot').classList.add('show');
}}, 500 + d3 + 300);
</script>
</body>
</html>
"""
    components.html(slot_html, height=720)

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
