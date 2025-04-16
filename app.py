import streamlit as st
import os
import zipfile
import shutil
from image2excel import generate_availability_from_image
from shift_scheduler_v1 import main as run_scheduler_v1
from shift_scheduler_v2 import main as run_scheduler_v2

st.set_page_config(page_title="고정근로 자동 배정기", layout="centered")
st.title("📅 고정근로 자동 배정기")

# 초기 폴더 준비
def prepare_directories():
    for folder in ["images", "input", "output/output_v1", "output/output_v2"]:
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder)

# 세션 초기화
if "step" not in st.session_state:
    st.session_state.step = 0

# 항상 업로드 창은 보이게
uploaded_files = st.file_uploader("시간표 이미지 업로드 (.jpg)", type=["jpg"], accept_multiple_files=True)

# 파일 업로드 처리
if uploaded_files:
    if "uploaded_files" not in st.session_state:
        prepare_directories()
        for file in uploaded_files:
            filepath = os.path.join("images", file.name)
            with open(filepath, "wb") as f:
                f.write(file.read())
        st.session_state.uploaded_files = uploaded_files
        st.session_state.step = 1
        st.rerun()

# 1단계 버튼
if "uploaded_files" in st.session_state and st.session_state.step >= 1:
    st.success(f"✅ {len(st.session_state.uploaded_files)}개 이미지 업로드 완료")
    if st.button("1단계: 가용시간표 생성"):
        created_files = []
        for file in st.session_state.uploaded_files:
            filepath = os.path.join("images", file.name)
            try:
                df = generate_availability_from_image(filepath)
                name = os.path.splitext(file.name)[0]
                excel_path = os.path.join("input", f"{name}.xlsx")
                df.to_excel(excel_path, index=True)
                created_files.append(excel_path)
            except Exception as e:
                st.error(f"❌ {file.name} 처리 실패: {e}")

        if created_files:
            input_zip_path = "input/input_bundle.zip"
            with zipfile.ZipFile(input_zip_path, "w") as zipf:
                for file_path in created_files:
                    zipf.write(file_path, arcname=os.path.basename(file_path))

            st.session_state.input_zip_path = input_zip_path
            st.session_state.step = 2
            st.rerun()

# 1단계 결과 다운로드 버튼
if "input_zip_path" in st.session_state:
    with open(st.session_state.input_zip_path, "rb") as f:
        st.download_button("📥 가용시간표 ZIP 다운로드", f, file_name="가용시간표_모음.zip")

# 2단계 실행 및 다운로드 버튼
if st.session_state.step >= 2:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("2단계: 자동 배정 실행 (v1)"):
            run_scheduler_v1("output/output_v1")
            result_path = "output/output_v1/result_bundle.zip"
            with zipfile.ZipFile(result_path, "w") as zipf:
                for file in os.listdir("output/output_v1"):
                    if file.endswith(".xlsx"):
                        zipf.write(os.path.join("output/output_v1", file), arcname=file)
            st.session_state.v1_zip_path = result_path
            st.rerun()

        if "v1_zip_path" in st.session_state:
            with open(st.session_state.v1_zip_path, "rb") as f:
                st.download_button("📥 결과 ZIP 다운로드 (v1)", f, file_name="자동배정_결과_v1.zip")

    with col2:
        if st.button("2단계: 자동 배정 실행 (v2)"):
            run_scheduler_v2("output/output_v2")
            result_path = "output/output_v2/result_bundle.zip"
            with zipfile.ZipFile(result_path, "w") as zipf:
                for file in os.listdir("output/output_v2"):
                    if file.endswith(".xlsx"):
                        zipf.write(os.path.join("output/output_v2", file), arcname=file)
            st.session_state.v2_zip_path = result_path
            st.rerun()

        if "v2_zip_path" in st.session_state:
            with open(st.session_state.v2_zip_path, "rb") as f:
                st.download_button("📥 결과 ZIP 다운로드 (v2)", f, file_name="자동배정_결과_v2.zip")
