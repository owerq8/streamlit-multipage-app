"""ML 예측 페이지 - 붓꽃 품종 예측

@st.fragment를 사용하여 슬라이더 변경 시
전체 페이지가 아닌 예측 영역만 다시 실행됩니다.
"""

from pathlib import Path

import joblib
import numpy as np
import streamlit as st

SPECIES = ["Setosa", "Versicolor", "Virginica"]
SPECIES_INFO = {
    "Setosa": "작고 둥근 꽃잎이 특징입니다.",
    "Versicolor": "중간 크기의 꽃잎을 가집니다.",
    "Virginica": "크고 긴 꽃잎이 특징입니다.",
}


@st.cache_resource
def load_model():
    """학습된 모델을 캐싱하여 로드합니다. 앱이 리렌더링되어도 모델은 한 번만 로드됩니다."""
    model_path = Path(__file__).parents[1] / "model" / "iris_model.joblib"
    return joblib.load(model_path)


model = load_model()

st.title("🌸 붓꽃 품종 예측")


# ──────────────────────────────────────────────
# @st.fragment: 이 함수 안의 위젯이 변경되면
# 전체 페이지가 아닌 이 함수만 다시 실행됩니다.
# → 다른 페이지 요소(제목, 설명 등)는 그대로 유지!
# ──────────────────────────────────────────────
@st.fragment
def prediction_section():
    """슬라이더 입력 + 예측 결과를 하나의 fragment로 묶습니다."""

    col1, col2 = st.columns(2)
    with col1:
        sepal_length = st.slider("꽃받침 길이 (cm)", 4.0, 8.0, 5.0, key="sl")
        sepal_width = st.slider("꽃받침 너비 (cm)", 2.0, 4.5, 3.0, key="sw")
    with col2:
        petal_length = st.slider("꽃잎 길이 (cm)", 1.0, 7.0, 4.0, key="pl")
        petal_width = st.slider("꽃잎 너비 (cm)", 0.1, 2.5, 1.0, key="pw")

    # 예측 수행
    input_data = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    st.divider()

    # 품종별 예측 확률
    st.subheader("품종별 예측 확률")
    for name, prob in zip(SPECIES, probabilities):
        st.progress(prob, text=f"{name}: {prob:.1%}")

    # 최종 예측 결과
    predicted_name = SPECIES[prediction]
    st.success(f"**예측 결과: {predicted_name}** ({probabilities[prediction]:.1%})")
    st.info(SPECIES_INFO[predicted_name])


# fragment 실행
prediction_section()
