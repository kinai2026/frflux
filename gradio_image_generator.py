
import gradio as gr
import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
import tempfile
import os

def generate_image(api_key, base_url, model, prompt, size, quality="standard", style="vivid"):
    """生成圖像的函數"""
    try:
        if not api_key.strip():
            return None, "請輸入 API Key"

        if not prompt.strip():
            return None, "請輸入提示詞"

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

        # 下載圖像
        img_response = requests.get(image_url)
        img_response.raise_for_status()

        # 保存到臨時文件
        image = Image.open(BytesIO(img_response.content))

        # 創建臨時文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_file.name, 'PNG')
        temp_file.close()

        return temp_file.name, f"圖像生成成功！\n模型: {model}\n尺寸: {size}\n提示詞: {prompt}"

    except Exception as e:
        return None, f"生成圖像時發生錯誤: {str(e)}"

def use_example_prompt(example):
    """使用示例提示詞"""
    return example

# 示例提示詞
example_prompts = [
    "A cute cat wearing a wizard hat",
    "A futuristic cityscape at sunset with flying cars",
    "A magical forest with glowing mushrooms and fairies",
    "A steampunk robot playing chess with a human",
    "An underwater palace with colorful coral and fish",
    "A cyberpunk street scene with neon lights"
]

# 創建 Gradio 界面
with gr.Blocks(
    title="AI 圖像生成器",
    theme=gr.themes.Soft(),
    css="""
    .main-container { max-width: 1200px; margin: 0 auto; }
    .header { text-align: center; margin-bottom: 2rem; }
    .example-row { margin-top: 1rem; }
    """
) as app:

    gr.HTML("""
    <div class="header">
        <h1>🎨 AI 圖像生成器</h1>
        <p>使用 OpenAI API 生成高質量的 AI 圖像</p>
    </div>
    """)

    with gr.Row():
        # 左側：設置和輸入
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ API 設置")

            api_key = gr.Textbox(
                label="API Key",
                type="password",
                placeholder="輸入您的 OpenAI API Key",
                info="您的 API Key 將安全處理"
            )

            base_url = gr.Textbox(
                label="Base URL",
                value="https://api.navy/v1",
                placeholder="API 基礎 URL"
            )

            gr.Markdown("### 🎛️ 圖像設置")

            model = gr.Dropdown(
                label="模型",
                choices=["flux.1-schnell", "dall-e-3", "dall-e-2"],
                value="flux.1-schnell",
                info="選擇圖像生成模型"
            )

            size = gr.Dropdown(
                label="圖像尺寸",
                choices=["1024x1024", "1024x1792", "1792x1024", "512x512", "256x256"],
                value="1024x1024",
                info="選擇生成圖像的尺寸"
            )

            with gr.Row():
                quality = gr.Dropdown(
                    label="品質",
                    choices=["standard", "hd"],
                    value="standard",
                    info="僅適用於 DALL-E 3"
                )

                style = gr.Dropdown(
                    label="風格",
                    choices=["vivid", "natural"],
                    value="vivid",
                    info="僅適用於 DALL-E 3"
                )

        # 右側：提示詞和生成
        with gr.Column(scale=1):
            gr.Markdown("### 📝 提示詞輸入")

            prompt = gr.Textbox(
                label="描述您想要生成的圖像",
                value="A cute cat wearing a wizard hat",
                lines=4,
                placeholder="詳細描述您想要生成的圖像...",
                info="詳細的描述通常能生成更好的圖像"
            )

            gr.Markdown("### 💡 示例提示詞")

            with gr.Row():
                example_dropdown = gr.Dropdown(
                    label="選擇示例",
                    choices=example_prompts,
                    value=None,
                    info="選擇一個示例提示詞"
                )

                use_example_btn = gr.Button("使用示例", size="sm")

            # 生成按鈕
            generate_btn = gr.Button(
                "🎨 生成圖像",
                variant="primary",
                size="lg"
            )

    # 結果顯示區域
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🖼️ 生成的圖像")

            generated_image = gr.Image(
                label="生成結果",
                type="filepath",
                height=400,
                show_download_button=True,
                show_share_button=True
            )

            result_info = gr.Textbox(
                label="生成信息",
                lines=3,
                interactive=False,
                show_copy_button=True
            )

    # 示例展示
    gr.Markdown("### 🌟 示例圖像")
    gr.Examples(
        examples=[
            ["A cute cat wearing a wizard hat", "flux.1-schnell", "1024x1024"],
            ["A futuristic cityscape at sunset", "dall-e-3", "1024x1792"],
            ["A magical forest with glowing mushrooms", "flux.1-schnell", "1024x1024"],
        ],
        inputs=[prompt, model, size],
        label="點擊示例來嘗試"
    )

    # 說明文檔
    with gr.Accordion("📚 使用說明", open=False):
        gr.Markdown("""
        ### 如何使用
        1. **配置 API**: 輸入您的 OpenAI API Key 和 Base URL
        2. **選擇設置**: 選擇模型、尺寸、品質和風格
        3. **輸入提示詞**: 詳細描述您想要生成的圖像
        4. **生成圖像**: 點擊生成按鈕並等待結果
        5. **下載圖像**: 可以直接下載生成的圖像

        ### 提示
        - **詳細描述**: 更詳細的提示詞通常能生成更好的圖像
        - **模型選擇**: 不同模型有不同的特點和風格
        - **尺寸設置**: 根據需要選擇合適的圖像尺寸
        - **品質設置**: HD 品質會消耗更多 token 但生成更高質量的圖像

        ### 支持的模型
        - **flux.1-schnell**: 快速生成，適合快速原型
        - **dall-e-3**: 最新的 DALL-E 模型，支持高品質生成
        - **dall-e-2**: 經典的 DALL-E 模型，穩定可靠
        """)

    # 事件綁定
    use_example_btn.click(
        fn=use_example_prompt,
        inputs=[example_dropdown],
        outputs=[prompt]
    )

    generate_btn.click(
        fn=generate_image,
        inputs=[api_key, base_url, model, prompt, size, quality, style],
        outputs=[generated_image, result_info]
    )

# 啟動應用
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )
