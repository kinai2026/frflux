
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
import base64

# 頁面配置
st.set_page_config(
    page_title="AI 圖像生成器",
    page_icon="🎨",
    layout="wide"
)

# 標題
st.title("🎨 AI 圖像生成器")
st.markdown("使用 OpenAI API 生成高質量的 AI 圖像")

# 側邊欄配置
with st.sidebar:
    st.header("⚙️ 設置")

    # API 設置
    st.subheader("API 配置")
    api_key = st.text_input(
        "API Key", 
        type="password",
        help="輸入您的 OpenAI API Key"
    )

    base_url = st.text_input(
        "Base URL", 
        value="https://api.navy/v1",
        help="API 基礎 URL"
    )

    # 圖像設置
    st.subheader("圖像設置")
    model = st.selectbox(
        "模型",
        ["flux.1-schnell", "dall-e-3", "dall-e-2"],
        help="選擇圖像生成模型"
    )

    size = st.selectbox(
        "圖像尺寸",
        ["1024x1024", "1024x1792", "1792x1024", "512x512", "256x256"],
        help="選擇生成圖像的尺寸"
    )

    # 高級設置
    st.subheader("高級設置")
    quality = st.selectbox(
        "品質",
        ["standard", "hd"],
        help="圖像品質（僅適用於 DALL-E 3）"
    )

    style = st.selectbox(
        "風格",
        ["vivid", "natural"],
        help="圖像風格（僅適用於 DALL-E 3）"
    )

# 主內容區域
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 提示詞輸入")

    # 提示詞輸入
    prompt = st.text_area(
        "描述您想要生成的圖像",
        value="A cute cat wearing a wizard hat",
        height=120,
        help="詳細描述您想要生成的圖像"
    )

    # 示例提示詞
    st.subheader("💡 示例提示詞")
    example_prompts = [
        "A futuristic cityscape at sunset with flying cars",
        "A magical forest with glowing mushrooms and fairies",
        "A steampunk robot playing chess with a human",
        "An underwater palace with colorful coral and fish",
        "A cyberpunk street scene with neon lights"
    ]

    selected_example = st.selectbox(
        "選擇示例提示詞",
        ["自定義"] + example_prompts
    )

    if selected_example != "自定義":
        if st.button("使用選中的示例"):
            prompt = selected_example
            st.rerun()

    # 生成按鈕
    generate_button = st.button(
        "🎨 生成圖像",
        type="primary",
        use_container_width=True
    )

with col2:
    st.header("🖼️ 生成的圖像")

    # 初始化 session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    # 圖像生成邏輯
    if generate_button:
        if not api_key:
            st.error("請輸入 API Key")
            st.stop()

        if not prompt.strip():
            st.error("請輸入提示詞")
            st.stop()

        try:
            with st.spinner("正在生成圖像，請稍候..."):
                # 設置 OpenAI 客戶端
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )

                # 準備請求參數
                generation_params = {
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size
                }

                # 僅對 DALL-E 3 添加額外參數
                if model == "dall-e-3":
                    generation_params["quality"] = quality
                    generation_params["style"] = style

                # 生成圖像
                response = client.images.generate(**generation_params)

                # 獲取圖像 URL
                image_url = response.data[0].url
                st.session_state.image_url = image_url

                # 下載並顯示圖像
                img_response = requests.get(image_url)
                img_response.raise_for_status()

                image = Image.open(BytesIO(img_response.content))
                st.session_state.generated_image = image

                st.success("圖像生成成功！")

        except Exception as e:
            st.error(f"生成圖像時發生錯誤: {str(e)}")

    # 顯示生成的圖像
    if st.session_state.generated_image is not None:
        st.image(
            st.session_state.generated_image,
            caption="生成的圖像",
            use_column_width=True
        )

        # 下載按鈕
        col_download1, col_download2 = st.columns(2)

        with col_download1:
            # 轉換圖像為字節
            img_buffer = BytesIO()
            st.session_state.generated_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            st.download_button(
                label="📥 下載 PNG",
                data=img_bytes,
                file_name="generated_image.png",
                mime="image/png",
                use_container_width=True
            )

        with col_download2:
            # JPEG 格式下載
            img_buffer_jpg = BytesIO()
            # 轉換為 RGB（JPEG 不支持透明度）
            rgb_image = st.session_state.generated_image.convert('RGB')
            rgb_image.save(img_buffer_jpg, format='JPEG', quality=95)
            img_bytes_jpg = img_buffer_jpg.getvalue()

            st.download_button(
                label="📥 下載 JPEG",
                data=img_bytes_jpg,
                file_name="generated_image.jpg",
                mime="image/jpeg",
                use_container_width=True
            )

        # 顯示圖像信息
        st.subheader("📊 圖像信息")
        st.write(f"**尺寸**: {st.session_state.generated_image.size[0]} x {st.session_state.generated_image.size[1]}")
        st.write(f"**模型**: {model}")
        st.write(f"**提示詞**: {prompt}")

        # 顯示原始 URL（可選）
        if st.checkbox("顯示原始圖像 URL"):
            st.code(st.session_state.image_url)

    else:
        st.info("點擊「生成圖像」按鈕開始創建您的 AI 圖像")

# 底部說明
st.markdown("---")
st.markdown("""
### 🔧 使用說明
1. 在左側邊欄配置您的 API Key 和設置
2. 在左側輸入描述圖像的提示詞
3. 點擊「生成圖像」按鈕
4. 等待圖像生成完成
5. 可以下載生成的圖像

### 💡 提示
- 詳細的提示詞通常能生成更好的圖像
- 不同的模型有不同的特點和風格
- 可以嘗試不同的尺寸和設置來獲得最佳效果
""")
