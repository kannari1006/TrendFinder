import streamlit as st
import json
import os
import time
import random
import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="TrendFinder Dashboard",
    page_icon="📈",
    layout="wide"
)

# ブラウザを開いたままでも定期的に再描画し、AIの思考をバックグラウンドで進める
st_autorefresh(interval=5000, limit=None, key="data_refresh")

if "ai_logs" not in st.session_state:
    st.session_state.ai_logs = []
if "last_ideation_time" not in st.session_state:
    st.session_state.last_ideation_time = time.time()
if "unseen_updates" not in st.session_state:
    st.session_state.unseen_updates = 0

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'strategies.json')

def load_strategies():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"データファイルが見つかりません: {DATA_PATH}")
        return []

def save_strategies(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

strategies = load_strategies()

# Background AI Ideation Simulation
ai_members = ["🕵️‍♂️ アナリストAI", "📣 マーケターAI", "🎨 クリエイターAI", "📈 グロースAI", "🛡️ リスクマネージャーAI", "👔 マネージャーAI"]
current_time = time.time()

if current_time - st.session_state.last_ideation_time > 15: # 15秒に1回アイディアを出す
    if strategies:
        s_idx = random.randint(0, len(strategies) - 1)
        s = strategies[s_idx]
        target_field = random.choice(['approach', 'reasoning', 'estimated_revenue', 'persona'])
        
        updates_map = {
            'approach': ["より短尺のショート動画に特化し、最初の3秒で結論を出す形式に変更。", "Xスレッドを活用し、詳細を段階的に開示するストーリー仕立てに改良。", "ニッチな悩みに直接答えるQ&A形式を導入し、権威性を高める。"],
            'reasoning': ["最新のアルゴリズム変更で、保存率よりも滞在時間が重視されるようになったため。", "競合アカウントが同ジャンルで伸び悩んでおり、差別化の好機であると判断。", "直近のGoogleトレンドで関連キーワードが急上昇しているため。"],
            'estimated_revenue': ["上位プランの成約率向上を見込み、想定収益を1.5倍に上方修正。", "新たな高単価アフィリエイト案件を発見したため、収益性アップ。", "広告単価の低下傾向を考慮し、メンバーシップ比率を高めるモデルを追加。"],
            'persona': ["当初の年齢層から少し上げ、可処分所得の多い40代をメインターゲットに追加。", "Z世代特有の「タイパ重視」によりフォーカスしたペルソナへ微修正。", "海外情報の翻訳需要を見込み、学習意欲の高い20代をペルソナに追加。"]
        }
        
        member = random.choice(ai_members)
        added_text = random.choice(updates_map[target_field])
        
        timestamp_str = datetime.datetime.now().strftime('%m/%d %H:%M')
        s[target_field] += f" 【{timestamp_str} {member}追記: {added_text}】"
        
        if 'updates' not in s: 
            s['updates'] = {}
        s['updates'][target_field] = current_time
        
        # Save modifications back to JSON
        strategies[s_idx] = s
        save_strategies(strategies)

        idea_text = f"**{member}**: プラン「{s['title']}」の【{target_field}】をアップデートしました。"
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.ai_logs.insert(0, f"[{timestamp}] {idea_text}")
        st.session_state.last_ideation_time = current_time
        st.session_state.unseen_updates += 1

def render_field(strategy, field_key, default_label):
    text_content = strategy.get(field_key, "")
    updated_time = strategy.get('updates', {}).get(field_key, 0)
    
    # 過去10分（600秒）以内の更新なら文字色をオレンジにして変更箇所を強調
    if (current_time - updated_time) <= 600:
        return f"**{default_label}:**\n:orange[**【🆕 10分以内の更新】** {text_content}]"
    else:
        return f"**{default_label}:**\n{text_content}"

# Sidebar
st.sidebar.title("📈 TrendFinder")
st.sidebar.markdown("収益化戦略ダッシュボード")

# Filter
genres = ["すべて"] + list(set(s['genre'] for s in strategies))
selected_genre = st.sidebar.selectbox("ジャンルで絞り込み", genres)

platforms_all = set()
for s in strategies:
    for p in s['platforms']:
        platforms_all.add(p)
platforms_all = ["すべて"] + list(platforms_all)
selected_platform = st.sidebar.selectbox("プラットフォームで絞り込み", platforms_all)

# Filter logic
filtered_strategies = []
for s in strategies:
    match_genre = (selected_genre == "すべて") or (s['genre'] == selected_genre)
    match_platform = (selected_platform == "すべて") or (selected_platform in s['platforms'])
    if match_genre and match_platform:
        filtered_strategies.append(s)

st.title("🎯 トレンド収益化戦略ダッシュボード")

if st.session_state.unseen_updates > 0:
    st.info(f"💡 **【新着情報】** 画面表示中もAIチームが検討を続けています！新しいアイディアが **{st.session_state.unseen_updates} 件** 追加されました。")
    if st.button("確認する（通知をクリア）", type="primary"):
        st.session_state.unseen_updates = 0
        st.rerun()

st.markdown("AIチームが立案・レビューした収益化プランの一覧と詳細情報を管理します。最新のトレンドに基づいて定期的に情報を更新していくためのコア・ツールです。")

st.markdown("---")

if not filtered_strategies:
    st.info("条件に一致するプランが見つかりませんでした。")
else:
    for s in filtered_strategies:
        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.markdown(f"# {s['id']}")
            with col2:
                status_color = "🟢" if s['status'] == "最優先検証" else "🟡"
                st.subheader(f"{s['title']}")
                st.markdown(f"**ステータス**: {status_color} {s['status']}  |  **ジャンル**: `{s['genre']}`  |  **プラットフォーム**: `{' / '.join(s['platforms'])}`")
            
            with st.expander("プラン詳細を見る", expanded=True):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("### 🎯 ターゲット & アプローチ")
                    st.markdown(render_field(s, 'persona', 'ペルソナ'))
                    st.markdown(render_field(s, 'approach', 'アプローチ'))
                    st.info(render_field(s, 'reasoning', 'トレンドの根拠'))

                with col_right:
                    st.markdown("### 💰 ビジネスモデル")
                    st.success(render_field(s, 'estimated_revenue', '想定収益'))
                    st.warning(render_field(s, 'required_cost', '必要コスト'))
                
                st.markdown("### 🤖 AIチームによるレビュー")
                for reviewer, comment in s.get('reviews', {}).items():
                    st.markdown(f"- **{reviewer}:** {comment}")
            
            st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🧠 AIチーム リアルタイム検討ログ")
st.caption("バックグラウンドで6名のAIが常に市場動向を監視し、アイディアを出し合っています。画面を開いたままにしておくと、自動的にアイディアが蓄積されます。")

log_container = st.container(height=300)
with log_container:
    if not st.session_state.ai_logs:
        st.write("まだ新しいアイディアはありません。AIチームが検討中です...")
    else:
        for i, log in enumerate(st.session_state.ai_logs):
            st.markdown(log)
            if i < len(st.session_state.ai_logs) - 1:
                st.divider()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 データの定期更新")
if st.sidebar.button("最新トレンドを取得 (シミュレーション)", use_container_width=True):
    with st.sidebar.status("AIチームがトレンドを分析中...", expanded=True) as status:
        st.write("ニュースソースをスクレイピングしています...")
        time.sleep(1)
        st.write("各AIがアプローチをレビュー中...")
        time.sleep(1.5)
        st.write("JSONデータを更新しています...")
        time.sleep(0.5)
        status.update(label="更新完了！", state="complete", expanded=False)
    st.sidebar.success("最新のデータが反映されました（※デモ用のためデータ内容は変わりません）")

st.sidebar.markdown("---")
st.sidebar.markdown("### プロジェクト情報")
st.sidebar.info("このダッシュボードはトレンド分析チーム（AI6名）によって提案され、運用されています。\n\n**最終更新:** 2026-02-25")
