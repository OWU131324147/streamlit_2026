import streamlit as st
import pandas as pd

st.title("🎀 推し活支出管理アプリ 🎀")
st.write("推しごとの支出を記録して管理しよう！")

if "oshi_list" not in st.session_state:
    st.session_state.oshi_list = []

if "expenses" not in st.session_state:
    st.session_state.expenses = []

st.header("🌟 推しを追加")

new_oshi = st.text_input("推しの名前を入力")

if st.button("推しを追加"):

    if new_oshi:

        if new_oshi not in st.session_state.oshi_list:
            st.session_state.oshi_list.append(new_oshi)
            st.success(f"「{new_oshi}」を追加しました！")
        else:
            st.warning("その推しは既に登録されています。")

    else:
        st.error("推しの名前を入力してください。")

# 推しが登録されている場合

if st.session_state.oshi_list:

    st.header("💖 推しを選択")

    selected_oshi = st.selectbox(
        "管理する推しを選んでください",
        st.session_state.oshi_list
    )

    st.subheader(f"✨ {selected_oshi} の推し活記録")

    st.header("📝 支出を入力")

    purpose = st.text_input(
        "目的（例：チケット、グッズ、アクスタ、CDなど）"
    )

    amount = st.text_input(
        "金額（円）",
        placeholder="例：5000"
    )

    if st.button("支出を追加"):

        if not purpose:
            st.error("目的を入力してください。")

        elif not amount:
            st.error("金額を入力してください。")

        elif not amount.isdigit():
            st.error("金額は数字で入力してください。")

        else:

            st.session_state.expenses.append(
                {
                    "推し": selected_oshi,
                    "目的": purpose,
                    "金額": int(amount)
                }
            )

            st.success("支出を記録しました！")
            st.rerun()

# データがある場合

if st.session_state.expenses and st.session_state.oshi_list:

    st.divider()

    df = pd.DataFrame(st.session_state.expenses)

    filtered_df = df[df["推し"] == selected_oshi]

    if not filtered_df.empty:

        # 左：履歴　右：集計・グラフ
        left_col, right_col = st.columns([3, 1])

        with left_col:

            st.header(f"📋 {selected_oshi} の支出履歴")

            edited_df = st.data_editor(
                filtered_df,
                use_container_width=True,
                num_rows="dynamic",
                key=f"editor_{selected_oshi}"
            )

            # 編集内容を保存
            other_df = df[df["推し"] != selected_oshi]

            updated_df = pd.concat(
                [other_df, edited_df],
                ignore_index=True
            )

            st.session_state.expenses = updated_df.to_dict("records")

            filtered_df = edited_df

        with right_col:

            # 選択中の推しの合計
            total_spent = filtered_df["金額"].sum()

            st.metric(
                f"💸 {selected_oshi} の合計",
                f"{int(total_spent):,} 円"
            )

            st.divider()

            # 全推しの合計
            all_total = df["金額"].sum()

            st.metric(
                "💰 推し活全体の合計",
                f"{int(all_total):,} 円"
            )

            st.divider()

            # 選択中の推しのグラフ
            purpose_total = (
                filtered_df.groupby("目的")["金額"]
                .sum()
                .reset_index()
                .sort_values("金額", ascending=False)
            )

            st.subheader(f"📈 {selected_oshi}")

            st.bar_chart(
                purpose_total.set_index("目的")
            )

            st.divider()

            # 全推し比較グラフ
            oshi_total = (
                df.groupby("推し")["金額"]
                .sum()
                .reset_index()
                .sort_values("金額", ascending=False)
            )

            st.subheader("📊 全体")

            st.bar_chart(
                oshi_total.set_index("推し")
            )

    else:

        st.info("まだ支出が記録されていません。")

# 全データ削除
if st.session_state.expenses:

    st.divider()

    if st.button("🗑️ 履歴をすべて削除"):
        st.session_state.expenses = []
        st.rerun()
