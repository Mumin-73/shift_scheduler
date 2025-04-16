# 고정근로 자동 배정 프로그램

본 프로젝트는 시간표 이미지를 분석하여 각 인원의 가용 시간표를 자동으로 생성하고, 제약 조건에 맞춰 고정 근로를 자동 배정하는 Python 기반의 근로 스케줄링 시스템입니다. `.cmd` 실행 파일을 통해 누구나 쉽게 사용할 수 있도록 설계되었습니다.

---

## 📁 폴더 및 파일 구조

```
project_shift_scheduler/
├── images/                # 시간표 이미지(.jpg)
├── input/                 # 변환된 가용 시간표(.xlsx)
├── output/                # 배정 결과물 및 통계(.xlsx)
├── image2excel.py         # 이미지 → 가용 시간표 변환 스크립트
├── shift_scheduler_v1.py  # 고정 근로 자동 배정 스크립트
├── shift_scheduler_v2.py  # 가용 시간 병합 시각화 스크립트
├── run_converter.cmd      # 변환기 실행용 명령어 파일
├── run_scheduler_v1.cmd   # 고정 배정 실행용 명령어 파일
├── run_scheduler_v2.cmd   # 병합 시각화 실행용 명령어 파일
├── requirements.txt       # 설치 필요 패키지 목록
└── README.md              # 사용 설명서
```

---

## 🖱️ CMD 실행 가이드

아래 `.cmd` 파일을 더블 클릭하면 해당 기능이 자동 실행됩니다:

| 파일명 | 기능 설명 |
|--------|------------|
| `run_converter.cmd`      | `images/` 폴더의 이미지 → `input/` 폴더에 가용시간표 엑셀 생성 |
| `run_scheduler_v1.cmd`   | `input/` 기반 자동 근로 배정 → `output/`에 결과 저장 |
| `run_scheduler_v2.cmd`   | 모든 인원의 가용시간 병합표 엑셀 출력 |

> 📝 설치된 Python 환경에서 실행됩니다. `requirements.txt` 기반 패키지 설치 필요.

---

## 🚀 설치 및 사용법 (개발자용)

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 이미지 → 엑셀 변환 수동 실행
```bash
python image2excel.py
```

### 3. 고정 근로 자동 배정 실행
```bash
python shift_scheduler_v1.py
```

### 4. 가용 시간 병합표 시각화
```bash
python shift_scheduler_v2.py
```

---

## 📌 배정 조건 요약

- 근무 가능 시간은 `8:30 ~ 17:30`, 30분 단위
- 연속 7시간(점심 포함) 근무 금지
- 8:30 타임은 최소 1시간 연속 가능해야 배정
- 시간당 최대 2명까지 배정 가능
- 가용 시간이 넓은 사람 우선, 연속성 우선 배정

---

## 📤 출력 결과물

| 파일명 | 설명 |
|--------|------|
| `최종_시간표.xlsx`      | 시간대별 최종 근무자 배정 결과 |
| `총_근무시간.xlsx`      | 인원별 누적 근무 시간 정리표 |
| `가용_시간표.xlsx`      | 병합된 전체 인원의 가용 시간표 |

---

## 📷 전체 작업 흐름

```
[이미지(.jpg)]
     ↓ run_converter.cmd
[가용시간표 엑셀(.xlsx)]
     ↓ run_scheduler_v1.cmd
[자동 배정 시간표 / 근무시간 요약]
     ↓ (선택) run_scheduler_v2.cmd
[가용 시간 병합표 출력]
```

---

## 🧩 패키지 목록 (`requirements.txt`)
```
opencv-python
pandas
openpyxl
```

---

## 🙌 기여 및 라이선스

- 이 프로젝트는 HR팀 및 근로자들의 업무 스케줄 관리를 자동화하기 위해 개발되었습니다.
- 자유롭게 수정 및 확장 가능하며, MIT 라이선스로 제공됩니다.

