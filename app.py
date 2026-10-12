import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
import json
import random
from database import init_db, get_members, save_result, get_history, reset_round, clear_history
from gacha import draw_all

st.set_page_config(page_title="YAMATO 神々の情熱 トイレ掃除ガチャ", page_icon="🎰", layout="wide")
init_db()

BASE_URL = "https://raw.githubusercontent.com/akkun-yamato/toilet-gacha-oki/main"
NORMAL_IMG = f"{BASE_URL}/yamato-god2-normal.png"
PEKA_IMG = f"{BASE_URL}/yamato-god2-peka.png"

# メンバーごとの色（参考画像のテイスト）
NAME_COLORS = {
    "あっくん": "#4ecdc4", "かんぬし": "#45b7d1", "しゃっちょ": "#ff6b6b",
    "はっしー": "#feca57", "しゅんちゃん": "#ff9ff3", "けんちゃん": "#5f27cd",
    "こうちゃん大": "#00d2d3", "こうちゃん小": "#a0e157", "しんや": "#ff6348",
    "まさゆき": "#1dd1a1", "なおきち": "#ffa502", "まーくん": "#eccc68",
    "やまぴー": "#ff7f50", "りょうちん": "#7bed9f", "けんたくん": "#70a1ff",
    "いっちー": "#f368e0", "かずえちゃん": "#ff6b9d", "しげちゃん": "#48dbfb",
    "ねえさん": "#ee5a6f", "のぶこちゃん": "#c56cf0", "とももん": "#ff9f43",
    "のりぴー": "#feca57", "ちーかわ": "#ff6b9d",
}

def get_color(name):
    return NAME_COLORS.get(name, "#333333")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #ffe4f1, #fff0f5, #e6e0ff, #fff8e7); }
h1 { color: #d6336c; text-align: center; font-size: 28px; text-shadow: 2px 2px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 0 0 10px rgba(214,51,108,0.3); }
.date-display { text-align: center; color: #333; font-size: 16px; margin-bottom: 15px; font-weight: bold; }
.stButton > button {
    background: linear-gradient(135deg, #ff6b9d, #d6336c);
    color: #fff; font-weight: bold; font-size: 18px;
    border: 3px solid #ffd700; border-radius: 50px; padding: 10px 30px;
    box-shadow: 0 0 20px rgba(255,107,157,0.5);
}
.stCheckbox label { font-size: 16px !important; font-weight: bold !important; color: #333 !important; }
div[data-testid="stExpander"] summary { color: #333 !important; font-weight: bold !important; }
.winner-card {
    background: linear-gradient(135deg, #fff8dc, #ffd700);
    border: 3px solid #ff1493; border-radius: 12px;
    padding: 12px; text-align: center; margin: 8px;
    box-shadow: 0 0 20px rgba(255,20,147,0.6);
}
.winner-card h3 { color: #8b0000; margin: 0; font-size: 18px; }
.winner-card .name { color: #d6336c; font-size: 24px; font-weight: bold; margin-top: 8px; text-shadow: 1px 1px 3px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎰 YAMATO 神々の情熱 トイレ掃除ガチャ 🎰</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'>📅 {date.today().strftime('%Y年%m月%d日')}</div>", unsafe_allow_html=True)

if "absent" not in st.session_state: st.session_state.absent = []
if "results" not in st.session_state: st.session_state.results = None
if "show_gacha" not in st.session_state: st.session_state.show_gacha = False

with st.expander("👥 本日の不在者チェック"):
    absent = []
    men = get_members("M")
    women = get_members("F")
    st.markdown("**男性**")
    cols = st.columns(4)
    for i, name in enumerate(men):
        if cols[i % 4].checkbox(name, key=f"abs_m_{name}"):
            absent.append(name)
    st.markdown("**女子**")
    cols = st.columns(4)
    for i, name in enumerate(women):
        if cols[i % 4].checkbox(name, key=f"abs_w_{name}"):
            absent.append(name)
    st.session_state.absent = absent
    if absent:
        st.info(f"本日の不在者: {len(absent)}名")

if st.button("🕹️ レバーON！ 🎰", use_container_width=True):
    st.session_state.results = draw_all(st.session_state.absent)
    st.session_state.show_gacha = True
    st.rerun()

if st.session_state.show_gacha and st.session_state.results:
    r = st.session_state.results
    men_winner = r.get("Men", "")
    guest_winner = r.get("Guest", "")
    women_winner = r.get("Women", "")

    all_men = get_members("M")
    all_women = get_members("F")

    def build_reel_items(pool, winner):
        items = []
        for _ in range(20):
            items.extend(random.sample(pool, len(pool)))
        if winner in pool:
            others = [n for n in pool if n != winner]
            above = random.choice(others) if others else winner
            below = random.choice(others) if others else winner
            items = [above, winner, below] + items
        else:
            items = [pool[0], pool[0], pool[0]] + items
        return items

    men_items = build_reel_items(all_men, men_winner)
    guest_items = build_reel_items(all_men, guest_winner)
    women_items = build_reel_items(all_women, women_winner)

    def to_list(names):
        return [{"name": n, "color": get_color(n)} for n in names]

    men_js = json.dumps(to_list(men_items), ensure_ascii=False)
    guest_js = json.dumps(to_list(guest_items), ensure_ascii=False)
    women_js = json.dumps(to_list(women_items), ensure_ascii=False)

    gacha_html = f"""
    <div class="cabinet-wrap" style="position:relative; width:400px; height:680px; margin:0 auto;">
        <img id="cabinet" src="{NORMAL_IMG}" style="position:absolute; top:0; left:0; width:400px; height:600px; z-index:1;"/>
        
        <div class="reel-container" style="position:absolute; top:215px; left:108px; width:185px; height:90px; z-index:3; display:flex; gap:2px; justify-content:center;">
            <div class="reel-window" id="rw-men">
                <div class="reel-inner" id="ri-men"></div>
            </div>
            <div class="reel-window" id="rw-guest">
                <div class="reel-inner" id="ri-guest"></div>
            </div>
            <div class="reel-window" id="rw-women">
                <div class="reel-inner" id="ri-women"></div>
            </div>
        </div>
        
        <div id="jackpot" style="position:absolute; top:625px; left:0; right:0; text-align:center; font-size:26px; font-weight:bold; z-index:5; opacity:0; animation:rainbow 1s linear infinite;">
            🎉 当選確定！ 🎉
        </div>
    </div>
    
    <style>
    .reel-window {{
        width:60px; height:90px; overflow:hidden; position:relative;
        background: linear-gradient(180deg, #fafafa 0%, #ffffff 50%, #fafafa 100%);
        border-radius:3px;
    }}
    .reel-window.win {{
        box-shadow: 0 0 20px #ff1493, inset 0 0 10px rgba(255,20,147,0.3);
        animation: winFlash 0.5s linear infinite;
    }}
    @keyframes winFlash {{
        0%, 100% {{ box-shadow: 0 0 20px #ff1493, inset 0 0 10px rgba(255,20,147,0.3); }}
        50% {{ box-shadow: 0 0 35px #ffd700, inset 0 0 15px rgba(255,215,0,0.5); }}
    }}
    .reel-inner {{
        position:absolute; top:0; left:0; width:100%;
    }}
    .reel-item {{
        width:60px; height:30px; display:flex; align-items:center; justify-content:center;
        box-sizing:border-box; padding:2px;
    }}
    .reel-item .name-tag {{
        display:inline-block; padding:3px 5px; border-radius:10px;
        background:#fff; font-weight:bold; font-size:10px;
        text-align:center; line-height:1.1; white-space:nowrap;
        text-shadow: 0 0 2px #fff, 1px 1px 1px rgba(0,0,0,0.1);
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        max-width:54px; overflow:hidden; text-overflow:ellipsis;
        border: 1px solid rgba(0,0,0,0.1);
    }}
    @keyframes rainbow {{
        0% {{ color:#ff0000; text-shadow: 0 0 15px #ff0000; }}
        16% {{ color:#ff8c00; text-shadow: 0 0 15px #ff8c00; }}
        33% {{ color:#ffd700; text-shadow: 0 0 15px #ffd700; }}
        50% {{ color:#00ff00; text-shadow: 0 0 15px #00ff00; }}
        66% {{ color:#00bfff; text-shadow: 0 0 15px #00bfff; }}
        83% {{ color:#8a2be2; text-shadow: 0 0 15px #8a2be2; }}
        100% {{ color:#ff1493; text-shadow: 0 0 15px #ff1493; }}
    }}
    </style>
    
    <script>
    const menList = {men_js};
    const guestList = {guest_js};
    const womenList = {women_js};
    const ITEM_H = 30;
    
    function buildReel(elId, list) {{
        const el = document.getElementById(elId);
        el.innerHTML = list.map(it => {{
            return `<div class="reel-item"><span class="name-tag" style="color:${{it.color}};">${{it.name}}</span></div>`;
        }}).join('');
    }}
    
    function spin(innerId, windowId, list, delay) {{
        const inner = document.getElementById(innerId);
        const win = document.getElementById(windowId);
        const stopPos = 0;
        const startPos = -(list.length - 10) * ITEM_H;
        inner.style.transition = 'none';
        inner.style.top = startPos + 'px';
        setTimeout(() => {{
            inner.style.transition = 'top 1.5s cubic-bezier(0.25, 0.1, 0.25, 1)';
            inner.style.top = stopPos + 'px';
            setTimeout(() => {{
                win.classList.add('win');
            }}, 1500);
        }}, delay + 50);
    }}
    
    buildReel('ri-men', menList);
    buildReel('ri-guest', guestList);
    buildReel('ri-women', womenList);
    
    setTimeout(() => {{
        spin('ri-men', 'rw-men', menList, 0);
        spin('ri-guest', 'rw-guest', guestList, 300);
        spin('ri-women', 'rw-women', womenList, 600);
        
        setTimeout(() => {{
            document.getElementById('cabinet').src = '{PEKA_IMG}';
            document.getElementById('jackpot').style.opacity = '1';
        }}, 2800);
    }}, 500);
    </script>
    """
    components.html(gacha_html, height=720)

    st.markdown("### 🏆 本日の当選者")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='winner-card'><h3>🚹 男性トイレ</h3><div class='name'>{men_winner or '該当者なし'}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='winner-card'><h3>🚻 ゲストトイレ</h3><div class='name'>{guest_winner or '該当者なし'}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='winner-card'><h3>🚺 女子トイレ</h3><div class='name'>{women_winner or '該当者なし'}</div></div>", unsafe_allow_html=True)

    cc1, cc2 = st.columns(2)
    with cc1:
        if st.button("🔄 引き直す"):
            st.session_state.results = draw_all(st.session_state.absent)
            st.rerun()
    with cc2:
        if st.button("✅ この結果で確定！"):
            save_result(st.session_state.results)
            st.success("保存しました！お疲れさまでした🎉")
            st.session_state.results = None
            st.session_state.show_gacha = False
            time.sleep(2)
            st.rerun()

with st.expander("📋 直近7日の履歴"):
    hist = get_history(7)
    if hist:
        from collections import defaultdict
        by_date = defaultdict(dict)
        for d, role, name in hist:
            by_date[d][role] = name
        for d in sorted(by_date.keys(), reverse=True):
            row = by_date[d]
            st.markdown(f"**{d}** 🚹{row.get('Men','-')} / 🚻{row.get('Guest','-')} / 🚺{row.get('Women','-')}")
    else:
        st.info("履歴なし")

with st.expander("⚙️ 管理メニュー"):
    st.markdown("**🔄 全周リセット**")
    cf1 = st.checkbox("リセット実行を確認", key="cf_reset")
    if st.button("全周リセット") and cf1:
        reset_round()
        st.success("リセット完了！")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown("**🗑️ 履歴全削除**")
    cf2 = st.checkbox("履歴削除を確認", key="cf_hist")
    if st.button("履歴クリア") and cf2:
        clear_history()
        st.success("履歴クリア完了！")
        time.sleep(1)
        st.rerun()
