# Streamlit 멀티페이지 앱 배포 실습

## 파일 구조

```
streamlit-multipage-app/
├── app.py                          # 진입점 (st.navigation)
├── requirements.txt                # 패키지 목록
├── .streamlit/
│   ├── secrets.toml                # API 키 (gitignore 제외)
│   └── secrets.example.toml        # API 키 템플릿
├── data/
│   └── california_housing.csv      # 주택 데이터
├── model/
│   └── iris_model.joblib           # 학습된 ML 모델
└── pages/
    ├── data_analysis.py            # 데이터 분석 (@st.fragment)
    ├── visualization.py            # 시각화 (@st.fragment)
    ├── ml_prediction.py            # 붓꽃 예측 (@st.fragment)
    └── gemini_chatbot.py           # Gemini 챗봇 + YouTube 도구
```

## 실행 방법

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. API 키 설정
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
# secrets.toml에 실제 API 키 입력

# 3. 앱 실행
streamlit run app.py
```

## 페이지 구성

| 그룹 | 페이지 | 설명 |
|------|--------|------|
| 데이터 | 📊 데이터 분석 | 캘리포니아 주택 데이터 필터링 및 통계 |
| 데이터 | 📈 시각화 | 분포, 관계, 연식별 차트 |
| AI | 🌸 ML 예측 | 붓꽃 품종 예측 (RandomForest) |
| AI | 💬 Gemini 챗봇 | Gemini 챗봇 + YouTube 검색 도구 |

## 배포 (Streamlit Community Cloud)

1. 이 repo를 본인 GitHub에 push
2. [share.streamlit.io](https://share.streamlit.io) 접속 → 앱 생성
3. **Settings > Secrets**에 API 키 입력:
   ```toml
   GEMINI_API_KEY = "실제_키"
   GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
   YOUTUBE_API_KEY = "실제_키"
   ```
