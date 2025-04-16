import streamlit as st
import os
from image2excel import generate_availability_from_image
from shift_scheduler_v1 import main as run_scheduler

st.title("고정근로 자동 배정기")

uploaded_file = st.file_uploader("시간표 이미지 업로드 (.jpg)", type=["jpg"])
if uploaded_file:
    os.makedirs("images", exist_ok=True)
    filepath = f"images/{uploaded_file.name}"
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ 이미지 업로드 완료")

    if st.button("1단계: 가용시간표 생성"):
        generate_availability_from_image(filepath)
        st.success("가용 시간표 생성 완료")

    if st.button("2단계: 자동 배정 실행"):
        run_scheduler()
        st.success("총 근무 시간, 최종 시간표 생성 완료")
