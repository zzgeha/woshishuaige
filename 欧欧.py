import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="欧欧欧欧文",
    page_icon="🏀",
    layout="wide"
)

# ---------------------- 烟花特效 ----------------------
fireworks_html = """
<style>
#fireworks-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    
    height: 100%;
    z-index: 9999;
    pointer-events: none;
}
</style>

<canvas id="fireworks-canvas"></canvas>

<script>
(function() {
    const canvas = document.getElementById('fireworks-canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const fireworks = [];

    class Particle {
        constructor(x, y, color) {
            this.x = x;
            this.y = y;
            this.color = color;
            const angle = Math.random() * Math.PI * 2;
            const velocity = Math.random() * 4 + 2;
            this.vx = Math.cos(angle) * velocity;
            this.vy = Math.sin(angle) * velocity;
            this.alpha = 1;
            this.decay = Math.random() * 0.015 + 0.01;
            this.gravity = 0.1;
        }

        update() {
            this.vx *= 0.98;
            this.vy *= 0.98;
            this.vy += this.gravity;
            this.x += this.vx;
            this.y += this.vy;
            this.alpha -= this.decay;
        }

        draw() {
            ctx.save();
            ctx.globalAlpha = this.alpha;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    class Firework {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = canvas.height;
            this.targetY = Math.random() * (canvas.height * 0.5) + 50;
            this.speed = Math.random() * 3 + 8;
            this.angle = -Math.PI / 2 + (Math.random() - 0.5) * 0.3;
            this.vx = Math.cos(this.angle) * this.speed;
            this.vy = Math.sin(this.angle) * this.speed;
            this.exploded = false;
            this.colors = [
                '#ff0040', '#ff4000', '#ff8000', '#ffbf00',
                '#ffff00', '#80ff00', '#00ff00', '#00ff80',
                '#00ffff', '#0080ff', '#0000ff', '#8000ff',
                '#ff00ff', '#ff0080', '#ffffff', '#ffd700'
            ];
            this.color = this.colors[Math.floor(Math.random() * this.colors.length)];
        }

        update() {
            if (!this.exploded) {
                this.x += this.vx;
                this.y += this.vy;
                this.vy += 0.1;

                if (this.y <= this.targetY || this.vy >= 0) {
                    this.explode();
                }
            }
        }

        explode() {
            this.exploded = true;
            const particleCount = Math.floor(Math.random() * 50) + 80;
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle(this.x, this.y, this.color));
            }
        }

        draw() {
            if (!this.exploded) {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, 4, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    function animate() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        for (let i = fireworks.length - 1; i >= 0; i--) {
            fireworks[i].update();
            fireworks[i].draw();
            if (fireworks[i].exploded) {
                fireworks.splice(i, 1);
            }
        }

        for (let i = particles.length - 1; i >= 0; i--) {
            particles[i].update();
            particles[i].draw();
            if (particles[i].alpha <= 0) {
                particles.splice(i, 1);
            }
        }

        requestAnimationFrame(animate);
    }

    let fireworkCount = 0;
    const maxFireworks = 15;

    function launchFireworks() {
        if (fireworkCount < maxFireworks) {
            fireworks.push(new Firework());
            fireworkCount++;

            setTimeout(launchFireworks, Math.random() * 400 + 200);
        }
    }

    animate();
    launchFireworks();

    setTimeout(() => {
        canvas.style.transition = 'opacity 1s';
        canvas.style.opacity = '0';
        setTimeout(() => {
            canvas.remove();
        }, 1000);
    }, 5000);
})();
</script>
"""

components.html(fireworks_html, height=0)

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

if "show_confirm" not in st.session_state:
    st.session_state["show_confirm"] = False

if "voted_player" not in st.session_state:
    st.session_state["voted_player"] = ""

# ---------------------- 评论区数据初始化 ----------------------
comment_file = "comments.csv"
if not os.path.exists(comment_file):
    df_comment = pd.DataFrame(columns=["用户ID", "评论内容", "评论时间"])
    df_comment.to_csv(comment_file, index=False)

# 记录当前用户是否已创建ID
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

# 记录不同用户的投票状态（用于区分不同用户）
if "user_votes" not in st.session_state:
    st.session_state["user_votes"] = {}

# ---------------------- 正文内容 ----------------------
st.title("一球定乾坤")

# ---------------------- 用户ID输入区域（放在最上面）----------------------
st.divider()
st.markdown("## 👤 用户身份验证")
st.info("⚠️ 请先输入您的用户名，才能进行投票和评论")

if st.session_state["user_id"] == "":
    input_id = st.text_input("请输入您的用户名：", key="login_user_id")
    if st.button("确认登录"):
        if input_id.strip() != "":
            st.session_state["user_id"] = input_id.strip()
            # 检查该用户是否已经投过票
            if st.session_state["user_id"] not in st.session_state["user_votes"]:
                st.session_state["user_votes"][st.session_state["user_id"]] = False
            st.success(f"欢迎，{st.session_state['user_id']}！现在可以投票和评论了")
            st.rerun()
        else:
            st.warning("用户名不能为空！")
else:
    col_user, col_logout = st.columns([3, 1])
    with col_user:
        st.success(f"当前登录用户：**{st.session_state['user_id']}**")
    with col_logout:
        if st.button("退出登录"):
            st.session_state["user_id"] = ""
            st.rerun()

st.divider()

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

# 检查用户是否已登录
if st.session_state["user_id"] == "":
    st.warning("⚠️ 请先在上方输入用户名并登录，才能进行投票！")
    option = st.radio("选择球星", df_vote["球星"].tolist(), disabled=True)
    st.button("提交投票", disabled=True)
else:
    # 检查当前用户是否已投票（geha用户除外）
    is_tester = st.session_state["user_id"] == "geha"
    has_user_voted = st.session_state["user_votes"].get(st.session_state["user_id"], False)
    
    if has_user_voted and not is_tester:
        st.info("✅ 您已经投过票了，不能重复投票！")
        if st.session_state.get("voted_player"):
            st.success(f"您投票给了：**{st.session_state['voted_player']}**")
    
    option = st.radio("选择球星", df_vote["球星"].tolist(),
                      disabled=has_user_voted and not is_tester)
    
    if st.button("提交投票", disabled=has_user_voted and not is_tester):
        if option != "凯里欧文" and not st.session_state.get("confirmed_not_kyrie", False):
            st.session_state["show_confirm"] = True
            st.session_state["temp_selected_player"] = option
        else:
            idx = df_vote[df_vote["球星"] == option].index[0]
            df_vote.loc[idx, "票数"] += 1
            df_vote.to_csv(vote_file, index=False)
            st.session_state["has_voted"] = True
            st.session_state["voted_player"] = option
            st.session_state["user_votes"][st.session_state["user_id"]] = True
            st.session_state["show_confirm"] = False
            st.session_state["confirmed_not_kyrie"] = False
            st.rerun()

    # 显示确认对话框
    if st.session_state.get("show_confirm", False):
        st.warning("⚠️ 真的选择不投德鲁大叔吗？")
        st.info('💡 提示：您可以点击"❌ 不，我要投欧文"按钮重新选择凯里·欧文')
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✅ 是的，坚持选择"):
                option = st.session_state.get("temp_selected_player", option)
                idx = df_vote[df_vote["球星"] == option].index[0]
                df_vote.loc[idx, "票数"] += 1
                df_vote.to_csv(vote_file, index=False)
                st.session_state["has_voted"] = True
                st.session_state["voted_player"] = option
                st.session_state["user_votes"][st.session_state["user_id"]] = True
                st.session_state["show_confirm"] = False
                st.session_state["confirmed_not_kyrie"] = True
                st.rerun()
        with col_no:
            if st.button("❌ 不，我要投欧文"):
                st.session_state["show_confirm"] = False
                st.session_state["temp_selected_player"] = ""
                st.rerun()

    # 显示投票成功消息
    if st.session_state["has_voted"] and st.session_state.get("voted_player"):
        if st.session_state.get("voted_player") == "凯里欧文":
            st.balloons()
            st.success("投票成功！已禁止重复投票")
            st.markdown("""
            <div style='text-align: center; font-size: 32px; color: #FFD700; font-weight: bold; margin: 20px 0; animation: glow 2s ease-in-out infinite;'>
                ✨ 好人一生平安 ✨
            </div>
            <style>
            @keyframes glow {
                0%, 100% { text-shadow: 0 0 10px #FFD700, 0 0 20px #FFD700, 0 0 30px #FFD700; }
                50% { text-shadow: 0 0 20px #FFA500, 0 0 30px #FFA500, 0 0 40px #FFA500; }
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.success("投票成功！已禁止重复投票")

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

# 检查用户是否已登录
if st.session_state["user_id"] == "":
    st.warning("⚠️ 请先在上方输入用户名并登录，才能发表评论！")
else:
    # 2. 发表评论
    st.subheader("发表评论")
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
