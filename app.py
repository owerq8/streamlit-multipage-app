"""멀티페이지 Streamlit 앱 - 메인 진입
"""

import streamlit as st

# 페이지 정의 (딕셔너리로 그룹화)
pg = st.navigation({
    "데이터": [
        st.Page("pages/data_analysis.py", title="데이터 분석", icon="📊", default=True),
        st.Page("pages/visualization.py", title="시각화", icon="📈"),
    ],
    "AI": [
        st.Page("pages/ml_prediction.py", title="ML 예측", icon="🌸"),
        st.Page("pages/gemini_chatbot.py", title="Gemini 챗봇", icon="💬"),
    ],
})

pg.run()
