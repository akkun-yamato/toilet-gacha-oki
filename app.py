import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
import json
from database import init_db, get_members, save_result, get_history, reset_round, clear_history
from gacha import draw_all

st.set_page_config(page_title="沖ドキ風 トイレ掃除ガチャ", page_icon="🌺", layout="wide")
init_db()

# ===== カスタムCSS =====
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1a0033 0%, #4a0080 50%, #ff1493 100%);
    color: white;
}
h1 {
    text-align: center;
    color: #ffeb3b;
    text-shadow: 3px 3px 0 #ff1493, 6px 6px 10px rgba(0,0,0,0.5);
    font-size: 3em !important;
    letter-spacing: 3px;
}
.date-display {
    text-align: center;
    color: #ffeb3b;
    font-size: 1.3em;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
}
.stButton>button {
    background: linear-gradient(180deg, #ff1493 0%, #c71585 50%, #8b008b 100%);
    color: #ffeb3b;
    border: 3px solid #ffeb3b;
    border-radius: 50px;
    font-size: 1.5em;
    font-weight: bold;
    padding: 15px 40px;
    box-shadow: 0 6px 20px rgba(255,20,147,0.6), inset 0 2px 10px rgba(255,255,255,0.3);
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    letter-spacing: 2px;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 30px rgba(255,235,59,0.8);
}
.winner-card {
    background: linear-gradient(135deg, #fff 0%, #ffe4ec 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 10px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    color: #333;
    min-height: 140px;
}
.role-men { border-top: 8px solid #4a90e2; }
.role-guest { border-top: 8px solid #feca57; }
.role-women { border-top: 8px solid #ff6b9d; }
.stCheckbox label { font-size: 18px !important; font-weight: bold !important; color: white !important; }
[data-testid="stExpander"] { background: rgba(0,0,0,0.3); border-radius: 10px; }
[data-testid="stExpander"] summary { color: #ffeb3b !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌺 沖ドキ風 トイレ掃除ガチャ 🌺</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'>📅 {date.today().strftime('%Y年%m月%d日')}</div>", unsafe_allow_html=True)

# セッション
if "absent" not in st.session_state: st.session_state.absent = []
if "results" not in st.session_state: st.session_state.results = None
if "show_slot" not in st.session_state: st.session_state.show_slot = False

# 不在者チェック
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

# レバーON ボタン
if st.button("🕹️ レバーON！ 🎰", use_container_width=True):
    st.session_state.results = draw_all(st.session_state.absent)
    st.session_state.show_slot = True
    st.rerun()

# スロット演出
if st.session_state.show_slot and st.session_state.results:
    results = st.session_state.results
    men_winner = results.get("Men", "該当者なし")
    guest_winner = results.get("Guest", "該当者なし")
    women_winner = results.get("Women", "該当者なし")

    # リール用の名前リスト（不在者除外）
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
        background: linear-gradient(180deg, #1a0033 0%, #4a0080 100%);
        font-family: 'Arial Black', sans-serif;
    }}
    .machine {{
        max-width: 600px;
        margin: 0 auto;
        background: linear-gradient(180deg, #ff69b4 0%, #ff1493 50%, #c71585 100%);
        border: 5px solid #ffeb3b;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 10px 40px rgba(255,20,147,0.6), inset 0 0 20px rgba(0,0,0,0.3);
    }}
    .hibiscus-row {{
        display: flex;
        justify-content: space-around;
        margin-bottom: 10px;
    }}
    .hibiscus {{
        font-size: 40px;
        filter: grayscale(100%);
        transition: filter 0.1s;
    }}
    .hibiscus.lit {{
        filter: none;
        animation: flash 0.3s infinite alternate;
        text-shadow: 0 0 20px #ffeb3b, 0 0 40px #ff1493;
    }}
    @keyframes flash {{
        0% {{ transform: scale(1); }}
        100% {{ transform: scale(1.2); }}
    }}
    .reels {{
        display: flex;
        justify-content: center;
        gap: 8px;
        background: #000;
        padding: 10px;
        border-radius: 10px;
        border: 3px solid #333;
    }}
    .reel {{
        width: 32%;
        height: 180px;
        overflow: hidden;
        background: linear-gradient(180deg, #fff 0%, #f0f0f0 100%);
        border-radius: 5px;
        position: relative;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
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
        font-size: 22px;
        font-weight: bold;
        color: #333;
        border-bottom: 2px solid #ddd;
    }}
    .reel-item.winner {{
        color: #ff1493;
        background: linear-gradient(90deg, #ffeb3b 0%, #fff 50%, #ffeb3b 100%);
    }}
    .reel-mask {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 100%);
        pointer-events: none;
    }}
    .reel-mask-bottom {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: linear-gradient(0deg, rgba(0,0,0,0.5) 0%, transparent 100%);
        pointer-events: none;
    }}
    .center-line {{
        position: absolute;
        top: 60px;
        left: 0;
        right: 0;
        height: 60px;
        border-top: 3px solid #ff1493;
        border-bottom: 3px solid #ff1493;
        pointer-events: none;
        z-index: 5;
    }}
    .controls {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 15px;
        gap: 20px;
    }}
    .lever {{
        width: 50px;
        height: 150px;
        position: relative;
    }}
    .lever-stick {{
        position: absolute;
        bottom: 0;
        left: 50%;
        transform-origin: bottom center;
        width: 10px;
        height: 120px;
        background: linear-gradient(90deg, #888 0%, #ddd 50%, #888 100%);
        margin-left: -5px;
        border-radius: 5px;
        animation: leverDown 0.5s ease-in forwards;
    }}
    .lever-ball {{
        position: absolute;
        top: -15px;
        left: 50%;
        margin-left: -20px;
        width: 40px;
        height: 40px;
        background: radial-gradient(circle at 30% 30%, #ff6b6b 0%, #c00 100%);
        border-radius: 50%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }}
    @keyframes leverDown {{
        0% {{ transform: rotate(0deg); }}
        50% {{ transform: rotate(60deg); }}
        100% {{ transform: rotate(0deg); }}
    }}
    .roles {{
        display: flex;
        justify-content: space-around;
        margin-top: 10px;
        color: #ffeb3b;
        font-weight: bold;
        text-shadow: 1px 1px 2px #000;
        font-size: 16px;
    }}
    .jackpot {{
        text-align: center;
        margin-top: 15px;
        font-size: 28px;
        color: #ffeb3b;
        font-weight: bold;
        text-shadow: 2px 2px 0 #ff1493, 4px 4px 10px #000;
        opacity: 0;
        transition: opacity 0.5s;
    }}
    .jackpot.show {{
        opacity: 1;
        animation: jackpotPulse 0.5s infinite alternate;
    }}
    @keyframes jackpotPulse {{
        0% {{ transform: scale(1); }}
        100% {{ transform: scale(1.15); }}
    }}
    @media (max-width: 600px) {{
        .reel {{ height: 150px; }}
        .reel-item {{ height: 50px; font-size: 16px; }}
        .center-line {{ top: 50px; height: 50px; }}
        .reel-mask, .reel-mask-bottom {{ height: 50px; }}
        .hibiscus {{ font-size: 28px; }}
        .lever {{ width: 35px; height: 100px; }}
        .lever-stick {{ height: 80px; }}
        .lever-ball {{ width: 28px; height: 28px; margin-left: -14px; }}
        .jackpot {{ font-size: 20px; }}
        .roles {{ font-size: 12px; }}
    }}
    </style>
    </head>
    <body>
    <div class="machine">
        <div class="hibiscus-row">
            <span class="hibiscus" id="h1">🌺</span>
            <span class="hibiscus" id="h2">🌺</span>
            <span class="hibiscus" id="h3">🌺</span>
            <span class="hibiscus" id="h4">🌺</span>
            <span class="hibiscus" id="h5">🌺</span>
        </div>
        <div class="reels">
            <div class="reel"><div class="reel-inner" id="reel1"></div><div class="reel-mask"></div><div class="reel-mask-bottom"></div></div>
            <div class="reel"><div class="reel-inner" id="reel2"></div><div class="reel-mask"></div><div class="reel-mask-bottom"></div></div>
            <div class="reel"><div class="reel-inner" id="reel3"></div><div class="reel-mask"></div><div class="reel-mask-bottom"></div></div>
            <div class="center-line"></div>
        </div>
        <div class="roles">
            <span>🚹 男性</span><span>🚻 ゲスト</span><span>🚺 女子</span>
        </div>
        <div class="controls">
            <div class="lever"><div class="lever-stick"><div class="lever-ball"></div></div></div>
        </div>
        <div class="jackpot" id="jackpot">✨ 当選確定！ ✨</div>
    </div>
    <script>
    const menList = {men_list};
    const womenList = {women_list};
    const menWin = {men_win_js};
    const guestWin = {guest_win_js};
    const womenWin = {women_win_js};

    // ハイビスカス点灯（レバー叩いた瞬間）
    const hibiscus = [document.getElementById('h1'), document.getElementById('h2'), document.getElementById('h3'), document.getElementById('h4'), document.getElementById('h5')];
    hibiscus.forEach(h => h.classList.add('lit'));

    // リール生成（長めに繰り返して、最後が当選者）
    function buildReel(list, winner, isMobile) {{
        const itemHeight = isMobile ? 50 : 60;
        const loops = 20;
        let html = '';
        for (let i = 0; i < loops; i++) {{
            for (let name of list) {{
                html += `<div class="reel-item">${{name}}</div>`;
            }}
        }}
        // 最後に当選者を配置（止まる位置）
        html += `<div class="reel-item winner">${{winner}}</div>`;
        html += `<div class="reel-item">${{list[0]}}</div>`;
        return html;
    }}

    const isMobile = window.innerWidth <= 600;
    const itemHeight = isMobile ? 50 : 60;

    const reel1 = document.getElementById('reel1');
    const reel2 = document.getElementById('reel2');
    const reel3 = document.getElementById('reel3');

    reel1.innerHTML = buildReel(menList, menWin, isMobile);
    reel2.innerHTML = buildReel(menList, guestWin, isMobile);
    reel3.innerHTML = buildReel(womenList, womenWin, isMobile);

    // 全リールの最終位置計算
    function getStopPos(reel) {{
        const items = reel.querySelectorAll('.reel-item');
        const winnerItem = reel.querySelector('.reel-item.winner');
        const idx = Array.from(items).indexOf(winnerItem);
        // 当選者を中央（上から1個目の下）に配置
        return -(idx * itemHeight - itemHeight);
    }}

    // スピン開始
    const spinDuration1 = 2000;
    const spinDuration2 = 3500;
    const spinDuration3 = 5000;

    setTimeout(() => {{
        reel1.style.transition = `top ${{spinDuration1 / 1000}}s cubic-bezier(0.33, 0, 0.2, 1)`;
        reel1.style.top = getStopPos(reel1) + 'px';
    }}, 500);

    setTimeout(() => {{
        reel2.style.transition = `top ${{spinDuration2 / 1000}}s cubic-bezier(0.33, 0, 0.2, 1)`;
        reel2.style.top = getStopPos(reel2) + 'px';
    }}, 500);

    setTimeout(() => {{
        reel3.style.transition = `top ${{spinDuration3 / 1000}}s cubic-bezier(0.33, 0, 0.2, 1)`;
        reel3.style.top = getStopPos(reel3) + 'px';
    }}, 500);

    // 全部止まったら JACKPOT 表示
    setTimeout(() => {{
        document.getElementById('jackpot').classList.add('show');
    }}, 500 + spinDuration3 + 300);
    </script>
    </body>
    </html>
    """
    components.html(slot_html, height=500)

    # 結果カード
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

# 履歴
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

# 管理メニュー
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
