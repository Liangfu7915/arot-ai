import streamlit as st
import google.generativeai as genai
import random
import time

# --- 1. 塔羅牌資料庫 (完整 78 張) ---
TAROT_DECK = [
    "0. 愚者 (The Fool)", "I. 魔術師 (The Magician)", "II. 女祭司 (The High Priestess)",
    "III. 皇后 (The Empress)", "IV. 皇帝 (The Emperor)", "V. 教皇 (The Hierophant)",
    "VI. 戀人 (The Lovers)", "VII. 戰車 (The Chariot)", "VIII. 力量 (Strength)",
    "IX. 隱士 (The Hermit)", "X. 命運之輪 (Wheel of Fortune)", "XI. 正義 (Justice)",
    "XII. 吊人 (The Hanged Man)", "XIII. 死神 (Death)", "XIV. 節制 (Temperance)",
    "XV. 惡魔 (The Devil)", "XVI. 高塔 (The Tower)", "XVII. 星星 (The Star)",
    "XVIII. 月亮 (The Moon)", "XIX. 太陽 (The Sun)", "XX. 審判 (Judgement)",
    "XXI. 世界 (The World)",
    "權杖王牌 (Ace of Wands)", "權杖二 (Two of Wands)", "權杖三 (Three of Wands)", "權杖四 (Four of Wands)", "權杖五 (Five of Wands)", "權杖六 (Six of Wands)", "權杖七 (Seven of Wands)", "權杖八 (Eight of Wands)", "權杖九 (Nine of Wands)", "權杖十 (Ten of Wands)", "權杖侍者 (Page of Wands)", "權杖騎士 (Knight of Wands)", "權杖皇后 (Queen of Wands)", "權杖國王 (King of Wands)",
    "聖杯王牌 (Ace of Cups)", "聖杯二 (Two of Cups)", "聖杯三 (Three of Cups)", "聖杯四 (Four of Cups)", "聖杯五 (Five of Cups)", "聖杯六 (Six of Cups)", "聖杯七 (Seven of Cups)", "聖杯八 (Eight of Cups)", "聖杯九 (Nine of Cups)", "聖杯十 (Ten of Cups)", "聖杯侍者 (Page of Cups)", "聖杯騎士 (Knight of Cups)", "聖杯皇后 (Queen of Cups)", "聖杯國王 (King of Cups)",
    "寶劍王牌 (Ace of Swords)", "寶劍二 (Two of Swords)", "寶劍三 (Three of Swords)", "寶劍四 (Four of Swords)", "寶劍五 (Five of Swords)", "寶劍六 (Six of Swords)", "寶劍七 (Seven of Swords)", "寶劍八 (Eight of Swords)", "寶劍九 (Nine of Swords)", "寶劍十 (Ten of Swords)", "寶劍侍者 (Page of Swords)", "寶劍騎士 (Knight of Swords)", "寶劍皇后 (Queen of Swords)", "寶劍國王 (King of Swords)",
    "錢幣王牌 (Ace of Pentacles)", "錢幣二 (Two of Pentacles)", "錢幣三 (Three of Pentacles)", "錢幣四 (Four of Pentacles)", "錢幣五 (Five of Pentacles)", "錢幣六 (Six of Pentacles)", "錢幣七 (Seven of Pentacles)", "錢幣八 (Eight of Pentacles)", "錢幣九 (Nine of Pentacles)", "錢幣十 (Ten of Pentacles)", "錢幣侍者 (Page of Pentacles)", "錢幣騎士 (Knight of Pentacles)", "錢幣皇后 (Queen of Pentacles)", "錢幣國王 (King of Pentacles)"
]

# --- 2. 頁面設定 ---
st.set_page_config(
    page_title="Waite - 全能塔羅導師",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. CSS 樣式 ---
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #ffffff; }
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown { color: #ffffff !important; }
    [data-testid="stSidebar"] { background-color: #1e1e1e; }
    .stChatInputContainer { padding-bottom: 20px; }
    textarea[data-testid="stChatInputTextArea"] { background-color: #333333 !important; color: #ffffff !important; border: 1px solid #555555 !important; }
    textarea[data-testid="stChatInputTextArea"]::placeholder { color: #aaaaaa !important; }
    .stTextInput input { background-color: #333333 !important; color: #ffffff !important; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #333333 !important; color: white !important; }
    .stNumberInput input { background-color: #333333 !important; color: white !important; }
    .chat-message { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; }
    .chat-message.user { background-color: #2b313e; }
    .chat-message.bot { background-color: #1f242d; border: 1px solid #4a4e69; }
    .stButton button {
        background-color: #333333;
        color: #d4af37 !important;
        border: 1px solid #d4af37;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #d4af37;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 初始化 Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "致候，我是 Waite。我已連結至黃金黎明與榮格心理學的深層知識庫。除了基礎解牌，我現在能分析**元素尊貴 (Elemental Dignities)** 與 **色彩象徵**。請問今日你想探索內在世界的哪一個角落？"
        }
    ]

# --- 5. 側邊欄功能 ---
with st.sidebar:
    st.title("🔮 Waite's Sanctum")
    st.markdown("---")
    api_key = st.text_input("🔑 請在此貼上 API Key", type="password", help="請從 Google AI Studio 取得 Key")
    st.markdown("[👉 點此取得免費 API Key](https://aistudio.google.com/app/apikey)")

    st.markdown("---")
    st.markdown("### ⚙️ 模型設定")
    available_models = []
    if api_key:
        try:
            genai.configure(api_key=api_key)
            all_models = genai.list_models()
            for m in all_models:
                if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                    available_models.append(m.name)
            available_models.sort(key=lambda x: '1.5' in x, reverse=True)
        except Exception:
            available_models = ["models/gemini-1.5-flash"]
    if not available_models:
        available_models = ["請先輸入 API Key"]
    selected_model = st.selectbox("目前可用模型", available_models)

    st.markdown("---")
    # 🔥 線上抽牌系統
    st.markdown("### 🃏 線上抽牌 (Digital Deck)")
    st.info("請等待 Waite 推薦張數後，再來此設定。")
    draw_count = st.number_input("設定抽牌張數", min_value=1, max_value=13, value=3)

    if st.button("✨ 進行神聖抽牌"):
        if not api_key:
            st.error("請先輸入 API Key。")
        else:
            drawn_cards = random.sample(TAROT_DECK, draw_count)
            result_text = []
            for i, card in enumerate(drawn_cards):
                is_upright = random.choice([True, False])
                position = "正位 (Upright)" if is_upright else "逆位 (Reversed)"
                icon = "🏆" if "聖杯" in card else "⚔️" if "寶劍" in card else "🪄" if "權杖" in card else "🪙" if "錢幣" in card else "🃏"
                result_text.append(f"{i+1}. {icon} {card} - 【{position}】")

            final_draw_string = f"（使用者已執行抽牌儀式，共 {draw_count} 張）\n抽牌結果如下：\n" + "\n".join(result_text) + "\n\n請依照剛剛推薦的牌陣，並運用「元素尊貴」與「榮格原型」為我深度解讀。"
            st.session_state.messages.append({"role": "user", "content": final_draw_string})
            st.rerun()

    st.markdown("---")
    if st.button("🔄 重置對話"):
        st.session_state.messages = [{"role": "assistant", "content": "致候，我是 Waite。我已準備好運用深層神秘學知識為你解惑。請問今日有何困惑？"}]
        st.rerun()

# --- 6. 系統提示詞 (知識庫大幅增強版) ---
SYSTEM_PROMPT = """
<System_Instructions>
* Research Protocol: Search internet if necessary to ensure accuracy.
* Output Language: Traditional Chinese (Taiwan).

You are Waite, an AI mentor based on RWS Tarot, Golden Dawn teachings, and Jungian psychology.

<Interaction_Protocol>
1. **Question Refinement:** If the question is vague ("Will I be rich?"), guide them to "How can I align with abundance?".
2. **Spread Recommendation:** Always recommend a spread + card count BEFORE drawing.
3. **Deep Interpretation:** Use the Enhanced Knowledge Base below.

<Enhanced_Knowledge_Base>

### **1. Elemental Dignities (The Golden Dawn System)**
* **Rule:** Cards affect their neighbors based on elements.
* **Friendly (Strengthening):**
    * Fire (Wands) + Air (Swords) = Active/Masculine Energy (Fast, Dynamic).
    * Water (Cups) + Earth (Pentacles) = Passive/Feminine Energy (Stable, Nurturing).
* **Enemies (Weakening):**
    * Fire (Wands) + Water (Cups) = Steam/Conflict (Will vs. Emotion).
    * Air (Swords) + Earth (Pentacles) = Dust/Stagnation (Mind vs. Matter).
* **Application:** If a positive card is flanked by "Enemy" elements, its power is blocked or delayed.

### **2. Color Symbolism (RWS Specific)**
* **Yellow:** Intellect, Air, Consciousness, Willpower (e.g., Magician's background).
* **Blue:** Subconscious, Water, Memory, Truth (e.g., High Priestess's robes).
* **Red:** Passion, Fire, Action, Desire (e.g., Emperor's robes).
* **White:** Purity, Spirit, Kether (Crown), New Beginnings (e.g., Death's horse).
* **Grey:** Neutrality, Wisdom, Balance (e.g., Hermit's cloak).

### **3. Jungian Archetypes & Court Cards**
* **Major Arcana:** The Hero's Journey (Individuation).
    * *The Fool:* The Inner Child / Potential.
    * *The Shadow:* The Devil, The Moon (Repressed self).
    * *The Anima/Animus:* The High Priestess, The Emperor.
* **Court Cards (Personality Types):**
    * **Page:** The Learner / Sensation function (Child archetype).
    * **Knight:** The Doer / Intuition function (Adolescent/Quest archetype).
    * **Queen:** The Nurturer / Feeling function (Mother archetype).
    * **King:** The Master / Thinking function (Father archetype).

### **4. Advanced Spreads Definition**
* **Celtic Cross (10 Cards):** 1.Present, 2.Cross(Challenge), 3.Crown(Best Outcome), 4.Root(Subconscious), 5.Past, 6.Future, 7.Self, 8.Environment, 9.Hopes/Fears, 10.Outcome.
* **Horseshoe (7 Cards):** 1.Past, 2.Present, 3.Hidden Influences, 4.Obstacles, 5.Environment, 6.Action, 7.Outcome.
* **Astrological (12 Cards):** Each card corresponds to the 12 Zodiac Houses.

<Output_Format>
* When interpreting, explicitly mention **"From the perspective of Elemental Dignities..."** or **"In Jungian terms..."** to show depth.
* Use Markdown for clarity.
"""

# --- 7. 主介面：快捷引導按鈕 ---
st.title("Waite: The Archetypal Mentor")
st.caption("基於 RWS 系統、榮格心理學、黃金黎明元素法則的 AI 導師")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🤔 教我如何提問"):
        prompt = "Waite，我不確定該怎麼問問題，請教我如何設計一個好的塔羅問題？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
with col2:
    if st.button("🃏 推薦適合牌陣"):
        prompt = "我有一個問題，但我不知道該用什麼牌陣，請根據我的狀況推薦給我，並告訴我每個位置代表什麼。"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
with col3:
    if st.button("💘 愛情運勢引導"):
        prompt = "我想算愛情，請推薦適合的牌陣並告訴我需要抽幾張牌。"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# --- 8. 對話顯示與處理 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("在此輸入你的問題..."):
    if not api_key:
        st.warning("⚠️ 請先在左側側邊欄輸入 API Key。")
        st.stop()
    if selected_model == "請先輸入 API Key":
        st.warning("⚠️ 請先輸入 API Key。")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=selected_model, system_instruction=SYSTEM_PROMPT)

            chat_history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=chat_history)

            last_msg = st.session_state.messages[-1]
            response = chat.send_message(last_msg["content"], stream=True)

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"發生錯誤: {str(e)}")

# --- 9. 處理按鈕觸發後的自動回應 ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and not prompt:
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=selected_model, system_instruction=SYSTEM_PROMPT)

            chat_history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=chat_history)
            response = chat.send_message(st.session_state.messages[-1]["content"], stream=True)

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"發生錯誤: {str(e)}")
