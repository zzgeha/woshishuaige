import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="欧文作品+投票+评论区",
    page_icon="logo.png" if os.path.exists("logo.png") else "🏀",
    layout="wide"
)

# ---------------------- 投票数据初始化 ----------------------
vote_file = "vote_data.csv"
if not os.path.exists(vote_file):
    df_vote = pd.DataFrame({
        "球星": ["凯里欧文", "斯蒂芬库里", "勒布朗詹姆斯", "克莱汤普森"],
        "票数": [0, 0, 0, 0]
    })
    df_vote.to_csv(vote_file, index=False)
else:
    df_vote = pd.read_csv(vote_file)
    required_players = ["凯里欧文", "斯蒂芬库里", "勒布朗詹姆斯", "克莱汤普森"]
    for player in required_players:
        if player not in df_vote["球星"].values:
            new_row = pd.DataFrame({"球星": [player], "票数": [0]})
            df_vote = pd.concat([df_vote, new_row], ignore_index=True)
            df_vote.to_csv(vote_file, index=False)

# 投票会话状态
if "has_voted" not in st.session_state:
    st.session_state["has_voted"] = False

# ---------------------- 评论区数据初始化 ----------------------
comment_file = "comments.csv"
if not os.path.exists(comment_file):
    df_comment = pd.DataFrame(columns=["用户ID", "评论内容", "评论时间"])
    df_comment.to_csv(comment_file, index=False)

# 记录当前用户是否已创建ID
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

# ---------------------- 正文内容 ----------------------
st.title("一球定乾坤")
st.header("""大家好这里是解说员葛哈，2016年6月19日，NBA总决赛抢七大战，甲骨文球馆。骑士与勇士鏖战整场，89平，时间只剩53秒。

整个第四节，双方像两台生锈的机器，谁都啃不下对方。整整三分多钟，没有人能得分。球馆里的空气几乎凝固，每一次呼吸都像在吞刀片。

这时候，球在凯里·欧文手中。防守他的，是两届MVP斯蒂芬·库里。全世界的目光都盯着这个25岁的年轻人。他会传球吗？会突破吗？

欧文连续胯下运球，节奏忽快忽慢，库里紧贴不放。就在所有人都以为他要突破的瞬间，欧文在三分线外突然拔起——7米开外，手起刀落，球在空中划出一道极高的弧线。

"那球出手后感觉太差了，弧线太高了。"欧文赛后说。

但球在篮筐前沿弹了一下，应声入网。

92比89。甲骨文球馆瞬间死寂，连勇士球迷都张大了嘴。

后来欧文说，出手那一刻，他满脑子想的都是"曼巴精神"。不惧怕，不犹豫，在最大的舞台上投进最关键的一球。这记三分，是他对科比最好的致敬。

整轮系列赛，欧战场均27.1分，碾压库里的22.6分，抢断2.1次、失误仅2.6次，每一项数据都完胜对手。他用行动证明，自己就是为大场面而生的球员。

那球，不只是三分。它是克利夫兰52年来第一个总冠军的答案，是NBA历史上唯一一次1比3逆转的句号。

nice欧文，let's goooooooo""")
st.audio("音频.mp3")

st.divider()

# 视频
st.video("欧文.mp4")
st.video("库里.mp4")
st.divider()
st.video("詹姆斯.mp4")
st.divider()
# 左右两张图片
col1, col2 = st.columns(2)
with col1:
    st.image("图1.jpg", use_container_width=True)
with col2:
    st.image("图2.jpg", use_container_width=True)

st.divider()
# ---------------------- 投票区域 ----------------------
st.subheader("🙋 为你支持的球星投票")

option = st.radio("选择球星", df_vote["球星"].tolist(),
                 disabled=st.session_state["has_voted"])

if st.button("提交投票", disabled=st.session_state["has_voted"]):
    idx = df_vote[df_vote["球星"] == option].index[0]
    df_vote.loc[idx, "票数"] += 1
    df_vote.to_csv(vote_file, index=False)
    st.session_state["has_voted"] = True
    st.success("投票成功！已禁止重复投票")
    st.rerun()

# 添加重置投票按钮（方便测试）
if st.session_state["has_voted"]:
    if st.button("🔄 重置投票（仅用于测试）"):
        st.session_state["has_voted"] = False
        st.rerun()

st.subheader("📊 实时票数统计")
# 每次都重新读取最新数据
df_vote_latest = pd.read_csv(vote_file)
st.dataframe(df_vote_latest, use_container_width=True)

st.divider()

# ---------------------- 评论区区域 ----------------------
st.markdown("## 💬 专属评论区")
st.info("⚠️ 必须先创建个人ID，才能发表评论，所有人可实时查看")

# 1. 创建用户ID
if st.session_state["user_id"] == "":
    st.subheader("第一步：创建你的专属评论ID")
    input_id = st.text_input("输入你的自定义ID（随便起名）：")
    if st.button("确认创建ID"):
        if input_id.strip() != "":
            st.session_state["user_id"] = input_id.strip()
            st.success(f"创建ID成功！你的ID：{st.session_state['user_id']}，现在可以评论了")
            st.rerun()
        else:
            st.warning("ID不能为空！")
else:
    col_user, col_reset = st.columns([3, 1])
    with col_user:
        st.success(f"当前登录ID：{st.session_state['user_id']}")
    with col_reset:
        if st.button("切换ID"):
            st.session_state["user_id"] = ""
            st.rerun()

    # 2. 发表评论
    st.subheader("第二步：发表评论")
    comment_text = st.text_area("写下你的评论：")
    if st.button("发布评论"):
        if comment_text.strip() != "":
            df_c = pd.read_csv(comment_file)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame({
                "用户ID": [st.session_state["user_id"]],
                "评论内容": [comment_text.strip()],
                "评论时间": [current_time]
            })
            df_c = pd.concat([df_c, new_row], ignore_index=True)
            df_c.to_csv(comment_file, index=False)
            st.success("评论发布成功！所有人可见")
            st.rerun()
        else:
            st.warning("评论内容不能为空！")

# 3. 展示所有评论
st.divider()
st.subheader("📜 全部实时评论（所有人可见）")
df_all_comment = pd.read_csv(comment_file)
if len(df_all_comment) == 0:
    st.info("暂无评论，快来抢沙发！")
else:
    # 按时间倒序显示，最新评论在前
    df_all_comment = df_all_comment.iloc[::-1]
    for i, row in df_all_comment.iterrows():
        time_str = f" ({row['评论时间']})" if "评论时间" in row else ""
        st.markdown(f"**👤 {row['用户ID']}**{time_str}：{row['评论内容']}")
        st.markdown("---")
