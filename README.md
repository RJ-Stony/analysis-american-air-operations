# 🛫 US Air Operations Analysis

미국 국내선 항공 운항 데이터를 기반으로,  
시간대별, 노선별 운항 패턴을 분석하고 시각화하는 프로젝트입니다.

---

## 📁 프로젝트 구조

```
analysis-american-air-operations-main/
├── data_loading.py                          # ✅ 항공 데이터 로딩 및 기초 처리
├── 4_preprocessing_and_visualization.py     # ✅ 전처리 + 시각화
├── 5_analysis.py                            # ✅ 시간대별·노선별 분석
├── 컬럼 설명.xlsx                            # 📄 데이터셋 컬럼 상세 설명
├── .gitignore
└── README.md
```

---

## 🔍 분석 흐름

1. **데이터 로딩**
   - `data_loading.py`  
     → CSV 또는 XLSX 파일을 로드하여 pandas DataFrame으로 구성  
     → 주요 컬럼: `ORIGIN`, `DEST`, `DEP_TIME`, `ARR_DELAY`, `CANCELLED` 등

2. **전처리 및 시각화**
   - `4_preprocessing_and_visualization.py`  
     → 결측치 처리, 시간 단위 변환, 요약 통계 계산  
     → 운항 수 / 지연 시간 등을 기반으로 다양한 시각화 생성

3. **운항 분석**
   - `5_analysis.py`  
     → 요일/시간대/출도착 공항 기준의 운항 패턴 분석  
     → matplotlib 또는 seaborn 기반의 고급 시각화 포함

---

## 📊 시각화 예시

- 시간대별 항공편 수 히스토그램
- 주요 노선별 운항 횟수 바차트
- 요일별 평균 지연 시간 라인 차트 등

---

## 🛠 사용 기술

- Python 3.12+
- pandas, matplotlib, seaborn
- 엑셀 파일 처리용 `openpyxl` (필요 시)

---

## 📌 참고 사항

- 데이터는 미국 교통부(US DOT) 또는 OpenFlights 등의 공공 항공 데이터셋을 가정
- 각 Python 파일 실행 전, 필요한 CSV/XLSX 파일을 지정 경로에 위치시켜야 함
