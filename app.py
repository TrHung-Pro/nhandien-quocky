import streamlit as st
import numpy as np
import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Nhận diện Quốc kỳ",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌍"
)

st.markdown("""
<style>
    html, body, [class*="css"] { color: #e2e8f0 !important; }
    .stApp { background-color: #050505 !important; }
    
    .main-header {
        background: linear-gradient(135deg, #171717 0%, #0a0a0a 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #262626;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.5);
    }
    .main-header h1 {
        color: #ffffff !important;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 0 10px rgba(255, 234, 0, 0.2);
    }
    .main-header p {
        color: #a1a1aa !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 1px solid #262626 !important;
    }
    
    [data-testid="stFileUploader"] {
        background-color: #121212;
        border: 2px dashed #404040;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #FFEA00; 
        background-color: #1a1a00; 
    }

    .stButton > button {
        background: transparent !important;
        color: #FFEA00 !important;
        border-radius: 8px;
        border: 1px solid #FFEA00 !important;
        padding: 0.6rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(255, 234, 0, 0.1);
        width: 100%;
    }
    .stButton > button:hover {
        background: #FFEA00 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(255, 234, 0, 0.4);
        transform: translateY(-2px);
    }

    .stDownloadButton > button {
        background: #171717 !important;
        color: #e2e8f0 !important;
        border: 1px solid #404040 !important;
        font-weight: 600;
        width: 100%;
        margin-top: 1rem;
    }
    .stDownloadButton > button:hover {
        background: #262626 !important;
        border-color: #e2e8f0 !important;
    }

    [data-testid="stNotification"] {
        background-color: #171717 !important;
        color: #e2e8f0 !important;
        border: 1px solid #262626 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

ROBOFLOW_API_KEY = "g5Gd6wERKi3CZAGGsBBT" 
ROBOFLOW_PROJECT = "flags-ekzlq-ji22t"
ROBOFLOW_VERSION = "1" 
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_PROJECT}/{ROBOFLOW_VERSION}"

def get_roboflow_predictions(image, api_confidence):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    params = {
        "api_key": ROBOFLOW_API_KEY,
        "confidence": api_confidence,
        "overlap": 30 
    }
    
    try:
        response = requests.post(ROBOFLOW_URL, params=params, data=img_str, 
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
        data = response.json()
        if "predictions" in data:
            return data["predictions"]
        else:
            st.error(f"⚠️ Lỗi API: {data.get('message', 'Không xác định')}")
            return []
    except Exception as e:
        st.error(f"⚠️ Lỗi kết nối API: {e}")
        return []

st.markdown("""
    <div class="main-header">
        <h1>🔍 Hệ Thống Nhận Diện Quốc Kỳ</h1>
        <p>Ứng dụng công nghệ Trí tuệ Nhân tạo Đám mây (Cloud AI)</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ Bảng Điều Khiển")
    api_confidence = st.slider(
        "Độ chính xác (%)", 
        min_value=10, max_value=100, 
        value=25, step=5,
        help="Lọc bỏ các kết quả có độ chính xác thấp hơn mức đã chọn."
    )
    st.markdown("---")
    st.markdown("**Hướng dẫn:**\n1. Kéo thả ảnh vào khu vực tải lên.\n2. Chọn vào nút Phân tích.\n3. Rê chuột vào các khung vàng để xem tên cờ.\n4. Tải ảnh kết quả về máy (nếu cần).")

uploaded_file = st.file_uploader("Kéo thả hoặc chọn tệp ảnh (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📸 Ảnh gốc")
        st.image(image, use_container_width=True)
        
    with col2:
        st.markdown("#### 🎯 Kết quả (Tương tác)")
        
        if st.button("🚀 Bắt đầu Phân tích"):
            with st.spinner("🧠 Đang phân tích hình ảnh..."):
                
                predictions = get_roboflow_predictions(image, api_confidence)

                with col1:
                    with st.expander("👁️ Xem/Ẩn dữ liệu gốc AI trả về"):
                        st.json(predictions)
                        
                drawn_image = image.copy()
                draw = ImageDraw.Draw(drawn_image)
                try: font = ImageFont.truetype("arial.ttf", size=24)
                except: font = ImageFont.load_default()

                img_w, img_h = image.size
                buffered_orig = io.BytesIO()
                image.save(buffered_orig, format="JPEG")
                img_b64 = base64.b64encode(buffered_orig.getvalue()).decode("utf-8")
                
                boxes_html = ""
                has_flags = False
                
                for p in predictions:
                    has_flags = True
                    w, h = p['width'], p['height']
                    x_center, y_center = p['x'], p['y']

                    x1 = int(x_center - w / 2)
                    y1 = int(y_center - h / 2)
                    x2 = int(x_center + w / 2)
                    y2 = int(y_center + h / 2)
                    
                    country_name = str(p['class']).title() 
                    confidence_pct = int(p['confidence'] * 100)
                    label = f"{country_name} ({confidence_pct}%)"

                    draw.rectangle([(x1, y1), (x2, y2)], outline="#FFEA00", width=5)
                    bbox = font.getbbox(label)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    draw.rectangle([(x1, max(0, y1 - th - 12)), (x1 + tw + 12, y1)], fill="#000000")
                    draw.text((x1 + 6, max(0, y1 - th - 10)), label, font=font, fill="#FFEA00")

                    left_pct = (x_center - w / 2) / img_w * 100
                    top_pct = (y_center - h / 2) / img_h * 100
                    width_pct = w / img_w * 100
                    height_pct = h / img_h * 100

                    box_html = f"""
                    <div class="hover-box" style="left: {left_pct}%; top: {top_pct}%; width: {width_pct}%; height: {height_pct}%;">
                        <div class="hover-label">{label}</div>
                    </div>
                    """
                    boxes_html += box_html
                
                if has_flags:
                    interactive_html = f"""
                    <style>
                        .img-container {{
                            position: relative;
                            width: 100%;
                            display: inline-block;
                        }}
                        .hover-box {{
                            position: absolute;
                            border: 3px solid #FFEA00;
                            box-sizing: border-box;
                            cursor: crosshair;
                            transition: background-color 0.2s ease, box-shadow 0.2s;
                        }}
                        .hover-box:hover {{
                            background-color: rgba(255, 234, 0, 0.25);
                            box-shadow: 0 0 15px rgba(255, 234, 0, 0.5);
                            z-index: 10;
                        }}
                        .hover-label {{
                            visibility: hidden;
                            background-color: rgba(0, 0, 0, 0.9);
                            color: #FFEA00;
                            text-align: center;
                            padding: 8px 14px;
                            border-radius: 6px;
                            border: 1px solid #FFEA00;
                            position: absolute;
                            z-index: 100;
                            bottom: calc(100% + 5px);
                            left: 50%;
                            transform: translateX(-50%);
                            white-space: nowrap;
                            font-family: Arial, sans-serif;
                            font-size: 16px;
                            font-weight: bold;
                            opacity: 0;
                            transition: opacity 0.2s ease, transform 0.2s ease;
                            pointer-events: none;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.8);
                        }}
                        .hover-box:hover .hover-label {{
                            visibility: visible;
                            opacity: 1;
                            transform: translateX(-50%) translateY(-5px);
                        }}
                    </style>
                    <div class="img-container">
                        <img src="data:image/jpeg;base64,{img_b64}" style="width: 100%; height: auto; display: block; border-radius: 8px;">
                        {boxes_html}
                    </div>
                    """
                    
                    st.markdown(interactive_html, unsafe_allow_html=True)
                    
                    st.success("✅ Hoàn tất! Điều chỉnh thanh 'Độ chính xác' bên trái nếu thấy kết quả không vừa ý.")
                    
                    buffered = io.BytesIO()
                    drawn_image.save(buffered, format="JPEG")
                    st.download_button(
                        label="📥 Tải ảnh kết quả tĩnh về máy",
                        data=buffered.getvalue(),
                        file_name="ket_qua_nhan_dien.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.warning("⚠️ Không tìm thấy quốc kỳ nào đạt chuẩn. Thử giảm thanh 'Độ chính xác' bên trái xuống.")
        else:
            st.info("👈 Chọn vào 'Bắt đầu Phân tích' để tiến hành nhận diện.")