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
NORMAL_IMG = f"{BASE_URL}/yamato-god2-normal-2x.png"
PEKA_IMG = f"{BASE_URL}/yamato-god2-peka-2x.png"
FONT_URL = f"{BASE_URL}/MPLUSRounded1c-Black.ttf"

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
@media (max-width: 600px) {
    h1 { font-size: 20px; }
    .date-display { font-size: 14px; }
}
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

if not st.session_state.results:
    st.session_state.results = draw_all(st.session_state.absent)
    st.session_state.show_gacha = True

if st.session_state.show_gacha and st.session_state.results:
    r = st.session_state.results
    men_winner = r.get("Men", "")
    guest_winner = r.get("Guest", "")
    women_winner = r.get("Women", "")

    all_men = get_members("M")
    all_women = get_members("F")

    men_js = json.dumps(all_men, ensure_ascii=False)
    guest_js = json.dumps(all_men, ensure_ascii=False)
    women_js = json.dumps(all_women, ensure_ascii=False)

    gacha_html = f"""
<style>
@font-face{{
    font-family:"MR";
    src:url("{FONT_URL}") format("truetype");
    font-weight:900;
    font-display:block;
}}
html,body{{margin:0;padding:0;background:transparent;overflow:hidden;font-family:"MR","Hiragino Maru Gothic ProN",sans-serif;}}
#fit{{position:relative;width:100%;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding-top:10px;}}
#stage-wrap{{position:relative;width:100%;max-width:480px;overflow:visible;}}
#stage{{position:relative;width:480px;height:680px;flex:none;transform-origin:top center;}}
.cab{{position:absolute;top:0;left:0;width:480px;height:600px;z-index:5;pointer-events:none;user-select:none;}}
.cab.peka{{opacity:0;transition:opacity .08s;}}
#stage.win .cab.peka{{animation:peka 0.5s steps(1) infinite;}}
@keyframes peka{{0%{{opacity:1}}50%{{opacity:0}}}}
#stage.win.hold .cab.peka{{animation:none;opacity:1;}}

.reel{{position:absolute;z-index:2;overflow:hidden;background:#efe6cf;border-radius:3px;}}
.strip{{position:absolute;left:0;right:0;top:0;will-change:transform;}}
.cell{{position:relative;box-sizing:border-box;display:block;overflow:hidden;}}
.cell canvas{{display:block;width:100%;height:100%;}}
.backlight{{position:absolute;inset:0;z-index:1;pointer-events:none;mix-blend-mode:screen;
    background:radial-gradient(ellipse 70% 55% at 50% 50%,rgba(255,250,230,.55),rgba(255,240,200,0) 70%);}}
.shade{{position:absolute;inset:0;z-index:3;pointer-events:none;
    background:
      linear-gradient(180deg,rgba(20,5,0,.70) 0%,rgba(20,5,0,.30) 10%,rgba(20,5,0,.06) 24%,rgba(0,0,0,0) 34%,rgba(0,0,0,0) 66%,rgba(20,5,0,.06) 76%,rgba(20,5,0,.30) 90%,rgba(20,5,0,.70) 100%),
      linear-gradient(90deg,rgba(0,0,0,.22) 0%,rgba(0,0,0,0) 14%,rgba(0,0,0,0) 86%,rgba(0,0,0,.22) 100%);}}
.glass{{position:absolute;inset:0;z-index:4;pointer-events:none;
    background:linear-gradient(115deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.28) 38%,rgba(255,255,255,0) 46%,rgba(255,255,255,0) 70%,rgba(255,255,255,.12) 74%,rgba(255,255,255,0) 78%);
    box-shadow:inset 0 0 10px rgba(0,0,0,.55);}}
.blur .strip{{filter:blur(1.4px) brightness(1.02);}}
.line{{position:absolute;left:0;right:0;z-index:3;pointer-events:none;opacity:0;
    box-shadow:inset 0 0 0 2px #ff1493,inset 0 0 12px rgba(255,20,147,.85);transition:opacity .2s;}}
#stage.win .line{{opacity:1;animation:lineflash .5s ease-in-out infinite alternate;}}
@keyframes lineflash{{from{{box-shadow:inset 0 0 0 2px #ff1493,inset 0 0 10px rgba(255,20,147,.6)}}to{{box-shadow:inset 0 0 0 2px #fff,inset 0 0 18px rgba(255,20,147,1)}}}}

.hot{{position:absolute;z-index:6;border-radius:50%;cursor:pointer;background:transparent;border:0;padding:0;
    -webkit-tap-highlight-color:rgba(255,255,255,.3);touch-action:manipulation;}}
.hot:active{{background:rgba(255,255,255,.18);}}
.hot.ready{{animation:ready 0.8s ease-in-out infinite alternate;}}
@keyframes ready{{from{{box-shadow:0 0 0 0 rgba(255,215,0,0)}}to{{box-shadow:0 0 18px 6px rgba(255,215,0,.85)}}}}

#jackpot{{position:absolute;top:620px;left:0;right:0;text-align:center;font-size:26px;font-weight:900;z-index:7;opacity:0;color:#fff;
    animation:rainbow 1s linear infinite;}}
#stage.win #jackpot{{opacity:1;}}
@keyframes rainbow{{
    0%{{color:#ff0000;text-shadow:0 0 15px #ff0000}}
    33%{{color:#ffd700;text-shadow:0 0 15px #ffd700}}
    66%{{color:#00bfff;text-shadow:0 0 15px #00bfff}}
    100%{{color:#ff1493;text-shadow:0 0 15px #ff1493}}
}}
#hint{{position:absolute;top:605px;left:0;right:0;text-align:center;font-size:13px;color:#d6336c;font-weight:bold;z-index:6;}}
#stage.win #hint{{display:none;}}

#winners{{width:95%;max-width:900px;margin-top:30px;opacity:0;transition:opacity 1s;}}
#winners.show{{opacity:1;}}
.winners-title{{color:#d6336c;font-size:22px;font-weight:bold;text-align:left;margin-bottom:10px;}}
.winners-row{{display:flex;gap:12px;justify-content:space-between;flex-wrap:wrap;}}
.winner-card{{flex:1;min-width:240px;background:linear-gradient(135deg, #fff8dc, #ffd700);
    border:3px solid #ff1493;border-radius:12px;padding:14px;text-align:center;
    box-shadow:0 0 20px rgba(255,20,147,0.6);box-sizing:border-box;}}
.winner-card h3{{color:#8b0000;margin:0;font-size:18px;}}
.winner-card .wname{{color:#d6336c;font-size:28px;font-weight:bold;margin-top:10px;text-shadow:1px 1px 3px rgba(0,0,0,0.2);}}

@media (max-width: 600px) {{
    .winners-title{{font-size:18px;}}
    .winner-card{{min-width:100%;}}
}}
</style>

<div id="fit">
  <div id="stage-wrap">
    <div id="stage">
        <div class="reel" id="r0"><div class="strip"></div><div class="backlight"></div><div class="line"></div><div class="shade"></div><div class="glass"></div></div>
        <div class="reel" id="r1"><div class="strip"></div><div class="backlight"></div><div class="line"></div><div class="shade"></div><div class="glass"></div></div>
        <div class="reel" id="r2"><div class="strip"></div><div class="backlight"></div><div class="line"></div><div class="shade"></div><div class="glass"></div></div>
        <img class="cab normal" src="{NORMAL_IMG}" alt="">
        <img class="cab peka" src="{PEKA_IMG}" alt="">
        <button class="hot ready" id="lever" title="レバー"></button>
        <button class="hot" id="b0" title="左ストップ"></button>
        <button class="hot" id="b1" title="中ストップ"></button>
        <button class="hot" id="b2" title="右ストップ"></button>
        <div id="hint">👆 レバーをクリックで回転 → ストップボタンで停止</div>
        <div id="jackpot">🎉 当選確定！ 🎉</div>
    </div>
  </div>
  
  <div id="winners">
    <div class="winners-title">🏆 本日の当選者</div>
    <div class="winners-row">
        <div class="winner-card"><h3>🚹 男性トイレ</h3><div class="wname">{men_winner or '該当者なし'}</div></div>
        <div class="winner-card"><h3>🚻 ゲストトイレ</h3><div class="wname">{guest_winner or '該当者なし'}</div></div>
        <div class="winner-card"><h3>🚺 女子トイレ</h3><div class="wname">{women_winner or '該当者なし'}</div></div>
    </div>
  </div>
</div>

<script>
const HOLES = [
    {{ x:315*0.5, y:443*0.5, w:117*0.5, h:201*0.5 }},
    {{ x:452*0.5, y:443*0.5, w:118*0.5, h:201*0.5 }},
    {{ x:591*0.5, y:443*0.5, w:118*0.5, h:201*0.5 }},
];
const HOT_POS = {{
    lever: {{x:190*0.5, y:820*0.5, r:30*0.5}},
    b0:    {{x:390*0.5, y:822*0.5, r:30*0.5}},
    b1:    {{x:480*0.5, y:822*0.5, r:30*0.5}},
    b2:    {{x:570*0.5, y:822*0.5, r:30*0.5}},
}};
const BLEED = 3;
const ROWS = 3;

const REEL_NAMES = [{men_js}, {guest_js}, {women_js}];
const WINNERS = ["{men_winner}", "{guest_winner}", "{women_winner}"];

function shuffle(a){{for(let i=a.length-1;i>0;i--){{const j=Math.random()*(i+1)|0;[a[i],a[j]]=[a[j],a[i]];}}return a;}}

function makeCell(name, w, h){{
    const S=2, W=Math.round(w*S), H=Math.round(h*S);
    const cv=document.createElement('canvas'); cv.width=W; cv.height=H;
    const x=cv.getContext('2d');
    const bg=x.createLinearGradient(0,0,0,H);
    bg.addColorStop(0,'#f3ead3'); bg.addColorStop(.5,'#fbf6e8'); bg.addColorStop(1,'#f0e6cc');
    x.fillStyle=bg; x.fillRect(0,0,W,H);
    for(let i=0;i<W*H/900;i++){{
        x.fillStyle='rgba(120,90,40,'+(Math.random()*.05)+')';
        x.fillRect(Math.random()*W,Math.random()*H,S,S);
    }}
    x.fillStyle='rgba(180,130,40,.35)';
    x.fillRect(0,0,W,1.2*S); x.fillRect(0,H-1.2*S,W,1.2*S);
    x.save(); x.translate(W/2,H/2); x.scale(1,.62);
    const pg=x.createRadialGradient(0,0,4*S,0,0,W*.48);
    pg.addColorStop(0,'rgba(30,0,25,.18)'); pg.addColorStop(1,'rgba(30,0,25,0)');
    x.fillStyle=pg; x.beginPath(); x.arc(0,0,W*.48,0,7); x.fill(); x.restore();
    let lines=[name]; const len=[...name].length;
    if(len>=5 && name.endsWith('ちゃん')) lines=[name.slice(0,-3),'ちゃん'];
    else if(len>=6) lines=[name.slice(0,Math.ceil(len/2)),name.slice(Math.ceil(len/2))];
    const padX=5*S, padY=4*S, maxW=W-padX*2, maxH=H-padY*2;
    let fs = maxH/lines.length/1.05;
    x.font='900 '+fs+'px MR,sans-serif';
    const mw=Math.max(...lines.map(l=>x.measureText(l).width));
    const ow=fs*0.28; if(mw+ow>maxW) fs*=maxW/(mw+ow);
    x.font='900 '+fs+'px MR,sans-serif';
    x.textAlign='center'; x.textBaseline='middle'; x.lineJoin='round';
    const lh=fs*1.0, y0=H/2-(lines.length-1)*lh/2+fs*.05;
    const ys=lines.map((_,i)=>y0+i*lh);
    const each=f=>lines.forEach((l,i)=>f(l,W/2,ys[i]));
    x.lineWidth=fs*.30; x.strokeStyle='#fff';
    x.shadowColor='rgba(0,0,0,.35)'; x.shadowBlur=3*S; x.shadowOffsetY=1*S;
    each((l,a,b)=>x.strokeText(l,a,b));
    x.shadowColor='transparent';
    for(let d=4;d>=1;d--){{
        x.lineWidth=fs*.17; x.strokeStyle='#000';
        each((l,a,b)=>x.strokeText(l,a+d*.35*S,b+d*.55*S));
        x.fillStyle='rgb('+(110+d*8)+','+(55+d*4)+',0)';
        each((l,a,b)=>x.fillText(l,a+d*.35*S,b+d*.55*S));
    }}
    x.lineWidth=fs*.17; x.strokeStyle='#111';
    each((l,a,b)=>x.strokeText(l,a,b));
    lines.forEach((l,i)=>{{
        const y=ys[i], g=x.createLinearGradient(0,y-fs/2,0,y+fs/2);
        g.addColorStop(0,'#fffbe0'); g.addColorStop(.22,'#ffe866');
        g.addColorStop(.45,'#ffd700'); g.addColorStop(.56,'#ff8c00');
        g.addColorStop(.78,'#ffc21a'); g.addColorStop(1,'#fff0a0');
        x.fillStyle=g; x.fillText(l,W/2,y);
    }});
    return cv;
}}

const stage = document.getElementById('stage');
const stageWrap = document.getElementById('stage-wrap');
let reels=[], playing=false;

for (const [id,h] of Object.entries(HOT_POS)){{
    const el=document.getElementById(id);
    Object.assign(el.style,{{left:(h.x-h.r)+'px',top:(h.y-h.r)+'px',width:(h.r*2)+'px',height:(h.r*2)+'px'}});
}}

// スマホ対応: 画面幅に合わせて拡縮
function fitStage(){{
    const parentWidth = stageWrap.offsetWidth;
    const scale = Math.min(1, parentWidth / 480);
    stage.style.transform = `scale(${{scale}})`;
    stageWrap.style.height = (680 * scale) + 'px';
}}
window.addEventListener('resize', fitStage);
setTimeout(fitStage, 50);

function render(r){{
    const p = ((r.pos % r.N)+r.N)%r.N;
    const y = -(p + r.N) * r.cellH + r.offsetTop;
    r.strip.style.transform = `translateY(${{y}}px)`;
}}

document.fonts.ready.then(() => document.fonts.load('900 40px MR')).then(build);

function build(){{
    reels = HOLES.map((h,i)=>{{
        const el=document.getElementById('r'+i);
        const W=h.w+BLEED*2, H=h.h+BLEED*2;
        Object.assign(el.style,{{left:(h.x-BLEED)+'px',top:(h.y-BLEED)+'px',width:W+'px',height:H+'px'}});
        const cellH = h.h/ROWS;
        const names = REEL_NAMES[i];
        const N = names.length;
        const order = shuffle([...Array(N).keys()]);
        const strip = el.querySelector('.strip');
        for(let k=0;k<3;k++) order.forEach(n=>{{
            const c=document.createElement('div'); c.className='cell'; c.style.height=cellH+'px';
            c.appendChild(makeCell(names[n], W, cellH));
            strip.appendChild(c);
        }});
        const line = el.querySelector('.line');
        Object.assign(line.style,{{top:(BLEED+cellH)+'px',height:cellH+'px'}});
        return {{ el, strip, order, names, N, cellH, offsetTop:BLEED, pos:Math.random()*N, speed:0, state:'stop' }};
    }});
    reels.forEach(render);
    fitStage();
}}

function start(){{
    if (!reels.length) return;
    if (reels.some(r=>r.state!=='stop')) return;
    stage.classList.remove('win','hold');
    document.getElementById('winners').classList.remove('show');
    reels.forEach(r=>{{ r.state='spin'; r.speed=0; r.el.classList.add('blur'); }});
    document.getElementById('lever').classList.remove('ready');
    [0,1,2].forEach(i=>document.getElementById('b'+i).classList.add('ready'));
    if(!playing){{ playing=true; requestAnimationFrame(loop); }}
}}

function stop(i){{
    const r=reels[i]; if(r.state!=='spin') return;
    const winnerName = WINNERS[i];
    const winnerIdx = r.names.indexOf(winnerName);
    if(winnerIdx<0){{
        r.state='stop'; r.el.classList.remove('blur');
        document.getElementById('b'+i).classList.remove('ready');
        checkEnd(); return;
    }}
    const k = r.order.indexOf(winnerIdx);
    let topRow = k-1;
    let base = Math.floor(r.pos);
    let t = base + ((topRow - base) % r.N + r.N) % r.N;
    if (t - r.pos < 3) t += r.N;
    r.target=t; r.state='braking'; r.from=r.pos;
    r.t0=performance.now(); r.dur = 400 + (t-r.pos)*8;
    document.getElementById('b'+i).classList.remove('ready');
}}

function loop(now){{
    let active=false;
    for(const r of reels){{
        if(r.state==='spin'){{
            r.speed=Math.min(r.speed+0.02,0.42);
            r.pos += r.speed;
            active=true;
        }}
        else if(r.state==='braking'){{
            const u=Math.min(1,(now-r.t0)/r.dur), e=1-Math.pow(1-u,3);
            r.pos = r.from + (r.target-r.from)*e;
            if(u>=1){{
                r.pos=r.target; r.state='stop';
                r.el.classList.remove('blur');
                bounce(r); checkEnd();
            }} else active=true;
        }}
        render(r);
    }}
    if(active) requestAnimationFrame(loop); else playing=false;
}}

function bounce(r){{
    r.strip.animate([{{marginTop:'3px'}},{{marginTop:'-1px'}},{{marginTop:'0px'}}],{{duration:160,easing:'ease-out'}});
}}

function checkEnd(){{
    if(reels.every(r=>r.state==='stop')){{
        stage.classList.add('win');
        setTimeout(()=>stage.classList.add('hold'),1800);
        setTimeout(()=>{{
            document.getElementById('winners').classList.add('show');
        }}, 2000);
    }}
}}

// タッチイベントとクリックイベント両対応
function bindButton(el, fn){{
    el.addEventListener('click', fn);
    el.addEventListener('touchend', (e)=>{{ e.preventDefault(); fn(); }});
}}
bindButton(document.getElementById('lever'), start);
[0,1,2].forEach(i => bindButton(document.getElementById('b'+i), () => stop(i)));
</script>
    """
    components.html(gacha_html, height=1000)

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
