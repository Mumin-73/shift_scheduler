import streamlit as st
import os
import zipfile
from image2excel import generate_availability_from_image
from shift_scheduler_v1 import main as run_scheduler

st.set_page_config(page_title="고정근로 자동 배정기", layout="centered")
st.title("📅 고정근로 자동 배정기")

uploaded_files = st.file_uploader(
    "시간표 이미지 업로드 (.jpg)", type=["jpg"], accept_multiple_files=True
)

if uploaded_files:
    os.makedirs("images", exist_ok=True)
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    st.success(f"✅ {len(uploaded_files)}개 이미지 업로드 완료")

    for file in uploaded_files:
        filepath = os.path.join("images", file.name)
        with open(filepath, "wb") as f:
            f.write(file.read())

    if st.button("1단계: 가용시간표 생성"):
        for file in uploaded_files:
            filepath = os.path.join("images", file.name)
            generate_availability_from_image(filepath)
        st.success("📄 가용시간표 엑셀 생성 완료 (input 폴더)")

    if st.button("2단계: 자동 배정 실행"):
        run_scheduler()
        st.success("✅ 자동 배정 완료 (output 폴더)")

        # zip 결과물 생성
        zip_path = "output/result_bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk("output"):
                for file in files:
                    if file.endswith(".xlsx"):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, arcname=file)

        with open(zip_path, "rb") as f:
            st.download_button("📥 결과 ZIP 다운로드", f, file_name="근무표_결과.zip")
