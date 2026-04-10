"""시각화 페이지 - 캘리포니아 주택 데이터 차트

@st.fragment를 사용하여 차트 옵션 변경 시 해당 차트 영역만 리렌더링합니다.
데이터 분석 페이지에서 설정한 필터가 Session State를 통해 공유됩니다.
"""

from pathlib import Path
import platform

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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

# 한글 폰트 설정
sns.set_style("darkgrid")
if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":
    plt.rc("font", family="AppleGothic")
else:
    plt.rc("font", family="NanumGothic")
plt.rc("axes", unicode_minus=False)

# =============================================================================
# 필터링 (데이터 분석 페이지의 Session State 활용)
# =============================================================================
income_min = st.session_state.get("income_min", float(df["MedInc"].min()))
income_max = st.session_state.get("income_max", float(df["MedInc"].max()))
filtered_df = df[
    (df["MedInc"] >= income_min) & (df["MedInc"] <= income_max)
].copy()

st.title("📈 데이터 시각화")
st.caption(
    f"소득 필터: {income_min:.1f} ~ {income_max:.1f} | "
    f"데이터: {len(filtered_df):,}건"
)

tab1, tab2, tab3 = st.tabs(["📊 분포", "📈 관계", "📉 연식별 분석"])


# ──────────────────────────────────────────────
# Tab 1: 분포 차트 (정적이므로 fragment 불필요)
# ──────────────────────────────────────────────
with tab1:
    st.subheader("변수 분포 분석")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**주택 가격 분포**")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        sns.histplot(data=filtered_df, x="MedHouseVal", kde=True, ax=ax1)
        ax1.set_xlabel("주택 가격 (10만 달러)")
        ax1.set_ylabel("빈도")
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    with col2:
        st.write("**소득 분포**")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        sns.histplot(data=filtered_df, x="MedInc", kde=True, color="green", ax=ax2)
        ax2.set_xlabel("소득 (만 달러)")
        ax2.set_ylabel("빈도")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # 박스플롯
    st.write("**주요 변수 박스플롯**")
    fig3, axes = plt.subplots(1, 4, figsize=(16, 4))
    variables = ["MedInc", "HouseAge", "AveRooms", "MedHouseVal"]
    titles = ["소득", "주택 연식", "평균 방 수", "주택 가격"]
    colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]

    for ax, var, title, color in zip(axes, variables, titles, colors):
        sns.boxplot(data=filtered_df, y=var, ax=ax, color=color)
        ax.set_title(title)
        ax.set_ylabel("")

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)


# ──────────────────────────────────────────────
# Tab 2: 관계 차트
# @st.fragment: X/Y축 변수 선택 시 이 영역만 리렌더링
# ──────────────────────────────────────────────
with tab2:
    st.subheader("변수 간 관계 분석")

    @st.fragment
    def scatter_section():
        """산점도 변수 선택 + 차트를 fragment로 묶습니다."""
        col1, col2 = st.columns(2)
        with col1:
            x_var = st.selectbox(
                "X축 변수",
                options=["MedInc", "HouseAge", "AveRooms", "Population"],
                index=0,
                key="viz_x_var",
            )
        with col2:
            y_var = st.selectbox(
                "Y축 변수",
                options=["MedHouseVal", "MedInc", "HouseAge", "AveRooms"],
                index=0,
                key="viz_y_var",
            )

        st.write(f"**{x_var} vs {y_var}**")
        sample_size = min(1000, len(filtered_df))
        sample_df = filtered_df.sample(sample_size, random_state=42)

        fig, ax = plt.subplots(figsize=(10, 4))
        scatter = ax.scatter(
            sample_df[x_var],
            sample_df[y_var],
            c=sample_df["MedHouseVal"],
            cmap="viridis",
            alpha=0.6,
            s=20,
        )
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        plt.colorbar(scatter, label="주택 가격")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    scatter_section()


# ──────────────────────────────────────────────
# Tab 3: 연식별 분석 (정적)
# ──────────────────────────────────────────────
with tab3:
    st.subheader("주택 연식별 분석")

    age_price = filtered_df.groupby("HouseAge")["MedHouseVal"].mean().reset_index()

    st.write("**주택 연식별 평균 가격**")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(
        age_price["HouseAge"],
        age_price["MedHouseVal"],
        marker="o",
        linewidth=2,
        markersize=4,
    )
    ax.fill_between(age_price["HouseAge"], age_price["MedHouseVal"], alpha=0.3)
    ax.set_xlabel("주택 연식 (년)")
    ax.set_ylabel("평균 주택 가격 (10만 달러)")
    ax.set_title("주택 연식에 따른 평균 가격 변화")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # 연식 구간별 통계
    st.write("**연식 구간별 통계**")
    bins = [0, 10, 20, 30, 40, 52]
    labels = ["신축(~10년)", "준신축(10~20년)", "중간(20~30년)", "노후(30~40년)", "고령(40년+)"]
    temp_df = filtered_df.copy()
    temp_df["AgeGroup"] = pd.cut(temp_df["HouseAge"], bins=bins, labels=labels)

    age_stats = (
        temp_df.groupby("AgeGroup", observed=False)
        .agg({"MedHouseVal": ["mean", "std", "count"], "MedInc": "mean"})
        .round(2)
    )
    age_stats.columns = ["평균가격", "가격표준편차", "데이터수", "평균소득"]
    st.dataframe(age_stats)

st.divider()
st.info("💡 **Tip**: 데이터 분석 페이지에서 소득 필터를 변경하면 여기서도 반영됩니다.")
