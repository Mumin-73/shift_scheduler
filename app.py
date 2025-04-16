import streamlit as st
import os
import zipfile
import shutil
from image2excel import generate_availability_from_image
from shift_scheduler_v1 import main as run_scheduler

st.set_page_config(page_title="고정근로 자동 배정기", layout="centered")

st.title("📅 고정근로 자동 배정기")

uploaded_files = st.file_uploader(
    "시간표 이미지 업로드 (.jpg)", type=["jpg"], accept_multiple_files=True
)

# 업로드 전 폴더 초기화
for folder in ["images", "input", "output"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)}개 이미지 업로드 완료")

    for file in uploaded_files:
        filepath = os.path.join("images", file.name)
        with open(filepath, "wb") as f:
            f.write(file.read())

    if st.button("1단계: 가용시간표 생성"):
        created_files = []
        for file in uploaded_files:
            filepath = os.path.join("images", file.name)
            try:
                generate_availability_from_image(filepath)
                created_name = os.path.splitext(file.name)[0] + ".xlsx"
                created_path = os.path.join("input", created_name)
                if os.path.exists(created_path):
                    created_files.append(created_path)
            except Exception as e:
                st.error(f"❌ {file.name} 처리 실패: {e}")

        if created_files:
            st.success(f"📄 총 {len(created_files)}개 엑셀 생성 완료")

            input_zip_path = "input/input_bundle.zip"
            with zipfile.ZipFile(input_zip_path, "w") as zipf:
                for file_path in created_files:
                    zipf.write(file_path, arcname=os.path.basename(file_path))

            with open(input_zip_path, "rb") as f:
                st.download_button("📥 가용시간표 ZIP 다운로드", f, file_name="가용시간표_모음.zip")
        else:
            st.warning("⚠️ 생성된 엑셀 파일이 없습니다. 이미지 분석 실패 가능성 있음")

    if st.button("2단계: 자동 배정 실행"):
        xlsx_files = [f for f in os.listdir("input") if f.endswith(".xlsx")]
        if not xlsx_files:
            st.error("❌ input 폴더에 가용시간표 파일이 없습니다. 1단계를 먼저 실행하세요.")
        else:
            run_scheduler()
            st.success("✅ 자동 배정 완료")

            zip_path = "output/result_bundle.zip"
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for root, _, files in os.walk("output"):
                    for file in files:
                        if file.endswith(".xlsx"):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, arcname=file)

            with open(zip_path, "rb") as f:
                st.download_button("📥 결과 ZIP 다운로드", f, file_name="근무표_결과.zip")
