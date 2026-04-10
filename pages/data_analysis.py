"""데이터 분석 페이지 - 캘리포니아 주택 데이터

@st.fragment를 사용하여 필터 변경 시 필터+테이블 영역만 리렌더링합니다.
기술 통계 영역도 별도 fragment로 분리하여 탭 전환 시 독립적으로 동작합니다.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# =============================================================================
# 데이터 로드 (캐싱)
# =============================================================================
DATA_PATH = Path(__file__).parents[1] / "data" / "california_housing.csv"


@st.cache_data
def load_data():
    """캘리포니아 주택 데이터를 캐싱하여 로드합니다."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    # 데이터 파일이 없으면 샘플 생성
    np.random.seed(42)
    n = 1000
    return pd.DataFrame(
        {
            "MedInc": np.random.uniform(0.5, 15, n),
            "HouseAge": np.random.randint(1, 52, n),
            "AveRooms": np.random.uniform(1, 10, n),
            "AveBedrms": np.random.uniform(0.5, 5, n),
            "Population": np.random.randint(100, 10000, n),
            "AveOccup": np.random.uniform(1, 10, n),
            "Latitude": np.random.uniform(32, 42, n),
            "Longitude": np.random.uniform(-124, -114, n),
            "MedHouseVal": np.random.uniform(0.5, 5, n),
        }
    )


df = load_data()

st.title("📊 데이터 분석")


# ──────────────────────────────────────────────
# @st.fragment: 필터 + 데이터 테이블 영역
# 소득 범위 슬라이더를 변경하면 이 영역만 다시 실행됩니다.
# ──────────────────────────────────────────────
@st.fragment
def filter_and_table_section():
    """필터링 + 메트릭 + 데이터 테이블을 하나의 fragment로 묶습니다."""

    # 필터: 소득 범위
    income_range = st.slider(
        "💰 소득 범위 (만 달러)",
        min_value=float(df["MedInc"].min()),
        max_value=float(df["MedInc"].max()),
        value=(float(df["MedInc"].min()), float(df["MedInc"].max())),
        key="income_range",
    )

    # 데이터 필터링
    filtered_df = df[
        (df["MedInc"] >= income_range[0]) & (df["MedInc"] <= income_range[1])
    ]

    # Session State에 저장 (시각화 페이지에서 공유)
    st.session_state.income_min = income_range[0]
    st.session_state.income_max = income_range[1]

    # 필터 결과 요약
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 데이터", f"{len(df):,}건")
    with col2:
        st.metric(
            "필터링된 데이터",
            f"{len(filtered_df):,}건",
            delta=f"{len(filtered_df) - len(df):,}건",
        )
    with col3:
        st.metric("필터링 비율", f"{len(filtered_df) / len(df) * 100:.1f}%")

    st.divider()

    # 데이터 테이블
    st.subheader("📋 데이터 테이블")
    all_columns = df.columns.tolist()
    selected_cols = st.multiselect(
        "표시할 컬럼 선택",
        options=all_columns,
        default=all_columns[:5],
        key="analysis_columns",
    )

    if selected_cols:
        st.dataframe(filtered_df[selected_cols].head(100), hide_index=True)
    else:
        st.warning("최소 하나의 컬럼을 선택해주세요.")

    st.divider()

    # 기술 통계
    st.subheader("📈 기술 통계")
    tab1, tab2 = st.tabs(["요약 통계", "상관관계"])

    with tab1:
        st.write("**필터링된 데이터의 기술 통계량**")
        st.dataframe(filtered_df.describe())

    with tab2:
        st.write("**변수 간 상관관계**")
        numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
        corr_matrix = filtered_df[numeric_cols].corr()
        st.dataframe(
            corr_matrix.style.background_gradient(cmap="RdYlBu", vmin=-1, vmax=1)
        )


# fragment 실행
filter_and_table_section()

st.divider()
st.info("💡 **Tip**: 필터 설정은 Session State에 저장되어 시각화 페이지에서도 적용됩니다.")
