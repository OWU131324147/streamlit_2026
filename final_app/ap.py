import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# --- 設定 ---
st.set_page_config(
    page_title="タイムマネジメント・トラッカー",
    page_icon="🕒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- スタイル設定 (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ffffff;
        border: 1px solid #ced4da;
    }
    .stButton>button:hover {
        border: 1px solid #007bff;
        color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- セッションステート（メモリ）の初期化 ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year
if 'view_month' not in st.session_state:
    st.session_state.view_month = datetime.now().month
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# --- タイトル ---
st.title("🗓️ タイムマネジメント・トラッカー")
st.caption("1か月ごとのカレンダーから日付を選んで、開始時刻と行動内容を手動で記録・時間経過ごとにテキストで確認しましょう！")

# --- メイン画面：1か月カレンダー＆月切り替えセクション ---
with st.container(border=True):
    col_m_left, col_m_title, col_m_right = st.columns([1, 2, 1])
    with col_m_left:
        if st.button("◀ 前月"):
            if st.session_state.view_month == 1:
                st.session_state.view_month = 12
                st.session_state.view_year -= 1
            else:
                st.session_state.view_month -= 1
            st.rerun()
    with col_m_title:
        st.markdown(f"<h3 style='text-align: center; margin: 0;'>📅 {st.session_state.view_year}年 {st.session_state.view_month}月</h3>", unsafe_allow_html=True)
    with col_m_right:
        if st.button("次月 ▶"):
            if st.session_state.view_month == 12:
                st.session_state.view_month = 1
                st.session_state.view_year += 1
            else:
                st.session_state.view_month += 1
            st.rerun()

    st.write("")
    
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(st.session_state.view_year, st.session_state.view_month)
    
    weekdays_header = ["月", "火", "水", "木", "金", "土", "日"]
    header_cols = st.columns(7)
    for idx, day_name in enumerate(weekdays_header):
        with header_cols[idx]:
            st.markdown(f"<p style='text-align: center; font-weight: bold;'>{day_name}</p>", unsafe_allow_html=True)
            
    for week in month_days:
        cols = st.columns(7)
        for idx, d in enumerate(week):
            with cols[idx]:
                is_selected = (d == st.session_state.selected_date)
                label = f"📌 {d.day}" if is_selected else f"{d.day}"
                
                if st.button(label, key=f"cal_date_{d.strftime('%Y%m%d')}", use_container_width=True):
                    st.session_state.selected_date = d
                    st.rerun()

# --- 選択された日付に対する「手動入力」セクション ---
with st.container(border=True):
    st.subheader(f"✍️ 選択中の日付: {st.session_state.selected_date.strftime('%Y年%m月%d日')} の記録追加")
    
    with st.form("manual_input_form", clear_on_submit=True):
        col_t, col_a = st.columns([1, 3])
        with col_t:
            time_str = st.text_input("開始時刻", value="09:00", placeholder="HH:MM")
        with col_a:
            activity_text = st.text_input("行動内容", placeholder="例：プログラミングの勉強、買い物など")
        
        submit_btn = st.form_submit_button("📝 記録を追加する")
        if submit_btn:
            if activity_text.strip():
                try:
                    parsed_t = datetime.strptime(time_str, "%H:%M").time()
                    new_item = {
                        "id": datetime.now().strftime('%Y%m%d%H%M%S') + str(len(st.session_state.logs)),
                        "date": st.session_state.selected_date,
                        "time": parsed_t.strftime("%H:%M"),
                        "activity": activity_text.strip()
                    }
                    st.session_state.logs.append(new_item)
                    st.success("記録を追加しました！")
                    st.rerun()
                except ValueError:
                    st.error("時刻は HH:MM 形式（例: 09:00）で正確に入力してください。")
            else:
                st.error("行動内容を入力してください。")

st.divider()

# --- 選択中の日付のスケジュール・テキスト表示 ---
if st.session_state.logs:
    raw_df = pd.DataFrame(st.session_state.logs)
    raw_df['date'] = pd.to_datetime(raw_df['date']).dt.date
    
    processed_dfs = []
    for d, group in raw_df.groupby('date'):
        group = group.sort_values('time').copy()
        group['start_time'] = group['time']
        
        end_times = []
        for i in range(len(group)):
            if i < len(group) - 1:
                end_times.append(group.iloc[i+1]['time'])
            else:
                end_times.append("24:00")
        group['end_time'] = end_times
        processed_dfs.append(group)
    
    full_processed_df = pd.concat(processed_dfs, ignore_index=True)

    selected_date_mask = (full_processed_df['date'] == st.session_state.selected_date)
    selected_display_df = full_processed_df.loc[selected_date_mask].copy().sort_values(['start_time'])

    st.subheader(f"📌 選択中の日付のスケジュール一覧 ({st.session_state.selected_date.strftime('%Y年%m月%d日')})")
    
    with st.container(border=Thread if 'Thread' in globals() else True): # 安全な記述
        if not selected_display_df.empty:
            for _, row in selected_display_df.iterrows():
                start_t = row['start_time']
                end_t = row['end_time']
                act = row['activity']
                st.markdown(f"🕒 **{start_t} 〜 {end_t}** : {act}")
            
            st.write("")
            
            st.divider()
            st.write("📝 **この日の記録の削除**")
            for _, row in selected_display_df.iterrows():
                cols = st.columns([2, 5, 2])
                with cols[0]:
                    st.write(f"{row['start_time']}〜")
                with cols[1]:
                    st.write(row['activity'])
                with cols[2]:
                    if st.button("❌ 削除", key=f"del_{row['id']}"):
                        st.session_state.logs = [item for item in st.session_state.logs if item['id'] != row['id']]
                        st.rerun()
        else:
            st.info("この日の記録はありません。上のフォームから記録を追加してください。")
else:
    st.info("まだ記録がありません。上部のカレンダーから日付を選んで、時刻と行動内容を登録してみましょう！")

st.divider()
if st.button("すべての記録をリセット"):
    st.session_state.logs = []
    st.success("記録をクリアしました。")
    st.rerun()

st.caption("© 2026 Time Management Tracker App")
