import streamlit as st
import urllib.parse
import urllib.request
import json
import requests
from io import BytesIO
from PIL import Image

# Set page configurations
st.set_page_config(
    page_title="AI 文字生成圖片",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom premium styling via CSS injection
st.markdown("""
    <style>
        /* Dark Theme Background and Gradients */
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* Main Title styling */
        .main-title {
            text-align: center;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
            background: linear-gradient(135deg, #a8edea, #fed6e3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            font-size: 16px;
            margin-bottom: 30px;
        }

        /* Style Card styling */
        .style-card {
            border: 2px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 15px 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        
        .style-card:hover {
            border-color: rgba(255, 255, 255, 0.4);
            background: rgba(255, 255, 255, 0.08);
        }

        .style-card.active {
            border-color: #a8edea;
            background: rgba(168, 237, 234, 0.15);
            box-shadow: 0 0 15px rgba(168, 237, 234, 0.2);
        }

        .style-icon {
            font-size: 28px;
            display: block;
            margin-bottom: 5px;
        }

        .style-name {
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Footer credits */
        .footer-credit {
            text-align: center;
            margin-top: 50px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.3);
        }
        .footer-credit a {
            color: rgba(255, 255, 255, 0.5);
            text-decoration: none;
        }
        .footer-credit a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to translate Chinese prompt to English
def translate_to_english(text):
    if not any('\u4e00' <= char <= '\u9fff' for char in text):
        return text
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=zh-TW|en"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            translated = data['responseData']['translatedText']
            if translated:
                return translated
    except Exception as e:
        st.warning(f"翻譯連線失敗，將直接使用原輸入提示詞。({e})")
    return text

# Main Title and Subtitle
st.markdown('<div class="main-title">AI 文字生成圖片</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">輸入你的想像，讓 AI 為你繪製</div>', unsafe_allow_html=True)

# 1. API Token and Input
api_key = st.text_input(
    "Hugging Face API 金鑰",
    type="password",
    placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    help="請輸入您的 Hugging Face 讀取權限金鑰 (Read Token)"
)

# 2. Prompt Input
user_prompt = st.text_input(
    "描述你想生成的圖片",
    placeholder="例如：一隻貓咪在火星上散步...",
    help="支援繁體中文或英文描述，中文會自動翻譯為英文發送給模型"
)

# Define Styles
STYLES = {
    "comic": {
        "name": "漫畫",
        "icon": "🎭",
        "prefix": "comic style, cartoon, cel-shaded, bold outlines, vibrant colors, "
    },
    "realistic": {
        "name": "寫實",
        "icon": "📷",
        "prefix": "photorealistic, highly detailed, 8K, natural lighting, "
    },
    "cyberpunk": {
        "name": "賽博龐克",
        "icon": "💡",
        "prefix": "cyberpunk style, neon lights, dark atmosphere, futuristic city, "
    },
    "sketch": {
        "name": "素描",
        "icon": "✏️",
        "prefix": "pencil sketch, black and white, hand-drawn, rough lines, "
    }
}

# 3. Style Selection Layout
st.write("選擇風格")
style_cols = st.columns(4)

# Initialize selected style in session state
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = "comic"

# Render cards as columns with interactive buttons
for i, (style_key, style_data) in enumerate(STYLES.items()):
    with style_cols[i]:
        is_active = st.session_state.selected_style == style_key
        active_class = "active" if is_active else ""
        
        # Display custom styled card HTML
        st.markdown(f"""
            <div class="style-card {active_class}">
                <div class="style-icon">{style_data['icon']}</div>
                <div class="style-name">{style_data['name']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Small invisible spacing, then a button to trigger selection state update
        if st.button(f"選擇 {style_data['name']}", key=f"btn_{style_key}", use_container_width=True):
            st.session_state.selected_style = style_key
            st.rerun()

# 4. Generate Action
st.write("")
generate_btn = st.button("生成圖片", type="primary", use_container_width=True)

# Display Preview of Prompt (only if prompt is entered)
selected_prefix = STYLES[st.session_state.selected_style]["prefix"]
if user_prompt:
    st.info(f"🎨 預計風格提示詞前綴：`{selected_prefix}`")

# Run generation
if generate_btn:
    if not api_key:
        st.error("請輸入 Hugging Face API 金鑰")
    elif not user_prompt:
        st.error("請輸入圖片描述")
    else:
        # Show loading spinner
        with st.spinner("正在生成中，請稍候..."):
            # 1. Automatic Translation to English
            translated_desc = translate_to_english(user_prompt)
            full_prompt = selected_prefix + translated_desc
            
            # Show translated preview in subtext
            if translated_desc != user_prompt:
                st.caption(f"📝 英文翻譯提示詞：*{full_prompt}*")
            else:
                st.caption(f"📝 最終提示詞：*{full_prompt}*")
            
            # 2. Query FLUX.1-schnell model
            API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": full_prompt}
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                
                # Check response
                if response.status_code == 200:
                    img_data = response.content
                    image = Image.open(BytesIO(img_data))
                    
                    # Display the generated image
                    st.success("✨ 生成成功！")
                    st.image(image, caption=full_prompt, use_container_width=True)
                    
                    # Option to download image
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    st.download_button(
                        label="💾 下載圖片",
                        data=byte_im,
                        file_name="ai_generated_image.png",
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    # Parse error details
                    try:
                        err_json = response.json()
                        error_msg = err_json.get("error", f"HTTP {response.status_code}")
                    except:
                        error_msg = response.text or f"HTTP {response.status_code}"
                    
                    st.error(f"生成失敗：{error_msg}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"連線至 Hugging Face 伺服器失敗：{e}")

# Footer Credit
st.markdown("""
    <div class="footer-credit">
        Powered by <a href="https://huggingface.co/" target="_blank">Hugging Face</a> Inference API
    </div>
""", unsafe_allow_html=True)
