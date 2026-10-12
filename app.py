import streamlit as st
import streamlit.components.v1 as components
from datetime import date
import time
import json
from database import init_db, get_members, save_result, get_history, reset_round, clear_history
from gacha import draw_all

st.set_page_config(page_title="YAMATO 神々の情熱 トイレ掃除ガチャ", page_icon="🎰", layout="wide")
init_db()

# 画像URLベース
BASE_URL = "https://raw.githubusercontent.com/akkun-yamato/toilet-gacha-oki/main"
NORMAL_IMG = f"{BASE_URL}/yamato-god2-normal.png"
PEKA_IMG = f"{BASE_URL}/yamato-god2-peka.png"
FRAME_NORMAL = f"{BASE_URL}/reel-frame-normal.png"
FRAME_WIN = f"{BASE_URL}/reel-frame-photo.png"

# 名前⇔画像マッピング
NAME_TO_IMG = {
    "あっくん": "akkun.png",
    "かんぬし": "kannushi.png",
    "しゃっちょ": "shaccho.png",
    "はっしー": "hasshii.png",
    "しゅんちゃん": "shun-chan.png",
    "けんちゃん": "ken-chan.png",
    "こうちゃん大": "kou-chan-dai.png",
    "こうちゃん小": "kou-chan-sho.png",
    "しんや": "shinya.png",
    "まさゆき": "masayuki.png",
    "なおきち": "naokichi.png",
    "まーくん": "maakun.png",
    "やまぴー": "yamapii.png",
    "りょうちん": "ryouchin.png",
    "けんたくん": "kenta-kun.png",
    "いっちー": "icchii.png",
    "かずえちゃん": "kazue-chan.png",
    "しげちゃん": "shige-chan.png",
    "ねえさん": "neesan.png",
    "のぶこちゃん": "nobuko-chan.png",
    "とももん": "tomomon.png",
    "のりぴー": "noripii.png",
    "ちーかわ": "chiikawa.png",
}

def img_url(name):
    fn = NAME_TO_IMG.get(name, "")
    return f"{BASE_URL}/{fn}" if fn else ""

# CSS
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #1a0033, #4a0080, #1a0033); }
h1 { color: #ffd700; text-align: center; text-shadow: 0 0 15px #ff8c00; font-size: 36px; }
.date-display { text-align: center; color: #fff; font-size: 20px; margin-bottom: 20px; }
.stButton > button {
    background: linear-gradient(135deg, #ff0000, #8b0000);
    color: #ffd700; font-weight: bold; font-size: 20px;
    border: 3px solid #ffd700; border-radius: 50px; padding: 15px 40px;
    box-shadow: 0 0 20px rgba(255,215,0,0.6);
}
.stCheckbox label { font-size: 18px !important; font-weight: bold !important; color: #fff !important; }
.winner-card {
    background: linear-gradient(135deg, #fff8dc, #ffd700);
    border: 4px solid #ff1493; border-radius: 15px;
    padding: 20px; text-align: center; margin: 10px;
    box-shadow: 0 0 25px rgba(255,20,147,0.7);
}
.winner-card h3 { color: #8b0000; margin: 0; font-size: 22px; }
.winner-card .name { color: #ff1493; font-size: 30px; font-weight: bold; margin-top: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎰 YAMATO 神々の情熱 トイレ掃除ガチャ 🎰</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'>📅 {date.today().strftime('%Y年%m月%d日')}</div>", unsafe_allow_html=True)

if "absent" not in st.session_state: st.session_state.absent = []
if "results" not in st.session_state: st.session_state.results = None
if "show_gacha" not in st.session_state: st.session_state.show_gacha = False

# 不在者チェック
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

# レバーON
if st.button("🕹️ レバーON！ 🎰", use_container_width=True):
    st.session_state.results = draw_all(st.session_state.absent)
    st.session_state.show_gacha = True
    st.rerun()

# ガチャ演出
if st.session_state.show_gacha and st.session_state.results:
    r = st.session_state.results
    men_winner = r.get("Men", "")
    guest_winner = r.get("Guest", "")
    women_winner = r.get("Women", "")

    all_men = get_members("M")
    all_women = get_members("F")

    def build_reel_items(pool, winner):
        import random
        items = []
        for _ in range(20):
            items.extend(random.sample(pool, len(pool)))
        # 停止位置: 中央段に winner が来るように
        # 上段/中段/下段の3つを表示、中央が winner
        # winner の index を決めて、その前後にダミー
        if winner in pool:
            others = [n for n in pool if n != winner]
            import random as rnd
            above = rnd.choice(others) if others else winner
            below = rnd.choice(others) if others else winner
            items.extend([above, winner, below])
        else:
            items.extend([pool[0], pool[0], pool[0]])
        return items

    men_items = build_reel_items(all_men, men_winner)
    guest_items = build_reel_items(all_men, guest_winner)
    women_items = build_reel_items(all_women, women_winner)

    def to_img_list(names):
        return [{"name": n, "url": img_url(n)} for n in names]

    men_js = json.dumps(to_img_list(men_items), ensure_ascii=False)
    guest_js = json.dumps(to_img_list(guest_items), ensure_ascii=False)
    women_js = json.dumps(to_img_list(women_items), ensure_ascii=False)

    gacha_html = f"""
    <div style="position:relative; width:600px; height:900px; margin:0 auto;">
        <!-- 筐体画像 -->
        <img id="cabinet" src="{NORMAL_IMG}" style="position:absolute; top:0; left:0; width:600px; height:900px; z-index:1;"/>
        
        <!-- リール3本（筐体の窓位置に重ねる） -->
        <div class="reel-container" style="position:absolute; top:333px; left:120px; width:360px; height:150px; z-index:3; display:flex; gap:5px; justify-content:center;">
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
        
        <!-- 当選確定テキスト -->
        <div id="jackpot" style="position:absolute; top:800px; left:0; right:0; text-align:center; font-size:40px; font-weight:bold; z-index:5; opacity:0; animation:rainbow 1s linear infinite;">
            🎉 当選確定！ 🎉
        </div>
    </div>
    
    <style>
    .reel-window {{
        width:110px; height:150px; overflow:hidden; position:relative;
        background:#fff; border:3px solid #ffd700; border-radius:5px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }}
    .reel-window.win {{
        border-color: #ff1493;
        box-shadow: 0 0 30px #ff1493, inset 0 0 15px rgba(255,20,147,0.3);
        animation: winFlash 0.5s linear infinite;
    }}
    @keyframes winFlash {{
        0%, 100% {{ box-shadow: 0 0 30px #ff1493, inset 0 0 15px rgba(255,20,147,0.3); }}
        50% {{ box-shadow: 0 0 50px #ffd700, inset 0 0 20px rgba(255,215,0,0.5); }}
    }}
    .reel-inner {{
        position:absolute; top:0; left:0; width:100%;
        transition: top 2s cubic-bezier(0.25, 0.1, 0.25, 1);
    }}
    .reel-item {{
        width:110px; height:50px; display:flex; align-items:center; justify-content:center;
        background:#fff;
    }}
    .reel-item img {{
        max-width:100px; max-height:48px; object-fit:contain;
    }}
    .reel-item .fallback {{
        font-weight:bold; color:#8b0000; font-size:14px;
    }}
    @keyframes rainbow {{
        0% {{ color:#ff0000; text-shadow: 0 0 20px #ff0000; }}
        16% {{ color:#ff8c00; text-shadow: 0 0 20px #ff8c00; }}
        33% {{ color:#ffd700; text-shadow: 0 0 20px #ffd700; }}
        50% {{ color:#00ff00; text-shadow: 0 0 20px #00ff00; }}
        66% {{ color:#00bfff; text-shadow: 0 0 20px #00bfff; }}
        83% {{ color:#8a2be2; text-shadow: 0 0 20px #8a2be2; }}
        100% {{ color:#ff1493; text-shadow: 0 0 20px #ff1493; }}
    }}
    @media (max-width: 650px) {{
        div[style*="width:600px"] {{ transform: scale(0.6); transform-origin: top center; }}
    }}
    </style>
    
    <script>
    const menList = {men_js};
    const guestList = {guest_js};
    const womenList = {women_js};
    const ITEM_H = 50;
    
    function buildReel(elId, list) {{
        const el = document.getElementById(elId);
        el.innerHTML = list.map(it => {{
            if (it.url) {{
                return `<div class="reel-item"><img src="${{it.url}}" onerror="this.style.display='none'; this.parentNode.innerHTML='<div class=fallback>${{it.name}}</div>';"/></div>`;
            }} else {{
                return `<div class="reel-item"><div class="fallback">${{it.name}}</div></div>`;
            }}
        }}).join('');
    }}
    
    function spin(innerId, windowId, list, delay) {{
        const inner = document.getElementById(innerId);
        const win = document.getElementById(windowId);
        // 最後から3つ目を中央段に（index: list.length - 2）
        const targetIdx = list.length - 2;
        // 中央に来るように: top = -(targetIdx * ITEM_H - ITEM_H)
        const stopPos = -(targetIdx * ITEM_H - ITEM_H);
        
        setTimeout(() => {{
            inner.style.transition = 'top 2.5s cubic-bezier(0.25, 0.1, 0.25, 1)';
            inner.style.top = stopPos + 'px';
            setTimeout(() => {{
                win.classList.add('win');
            }}, 2500);
        }}, delay);
    }}
    
    buildReel('ri-men', menList);
    buildReel('ri-guest', guestList);
    buildReel('ri-women', womenList);
    
    setTimeout(() => {{
        spin('ri-men', 'rw-men', menList, 0);
        spin('ri-guest', 'rw-guest', guestList, 500);
        spin('ri-women', 'rw-women', womenList, 1000);
        
        // 全停止後にPEKA画像に切替＆当選確定表示
        setTimeout(() => {{
            document.getElementById('cabinet').src = '{PEKA_IMG}';
            document.getElementById('jackpot').style.opacity = '1';
        }}, 4000);
    }}, 500);
    </script>
    """
    components.html(gacha_html, height=950)

    # 当選カード
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

# 履歴
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

# 管理メニュー
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
