"""Gemini 챗봇 페이지 - YouTube 검색 도구 통합

PydanticAI의 tool 기능으로 YouTube 검색을 Gemini 챗봇에 연결합니다.
일반 대화는 스트리밍으로, 동영상 검색 시에는 영상 카드를 함께 표시합니다.
"""

import json
import os

import requests
import streamlit as st
from pydantic_ai import Agent

# =============================================================================
# API 설정
# =============================================================================
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

MODEL_ID = f"google-gla:{st.secrets['GEMINI_MODEL']}"
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

INSTRUCTIONS = """\
당신은 친절한 한국어 AI 어시스턴트입니다.
사용자가 동영상, 영상, 유튜브 검색을 요청하면 youtube_search 도구를 사용하세요.
도구 호출 후에는 검색 결과를 자연스럽게 안내해주세요.
"""


# =============================================================================
# YouTube 검색 함수
# =============================================================================
def _search_youtube(query: str, max_results: int = 3) -> list[dict]:
    """YouTube Data API로 영상을 검색합니다."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    response.raise_for_status()
    return [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
        }
        for item in response.json().get("items", [])
        if "videoId" in item.get("id", {})
    ]


def render_videos(videos: list[dict]):
    """영상 목록을 카드 형태로 표시합니다."""
    for video in videos:
        with st.container(border=True):
            st.markdown(f"**{video['title']}**")
            st.caption(f"채널: {video['channel']}")
            st.video(f"https://www.youtube.com/watch?v={video['video_id']}")


# =============================================================================
# Agent 생성 + YouTube 검색 도구 등록
# =============================================================================
agent = Agent(MODEL_ID, instructions=INSTRUCTIONS)

# 도구 실행 중 검색된 영상을 임시 저장할 리스트
_found_videos: list[dict] = []


@agent.tool_plain
def youtube_search(query: str) -> str:
    """YouTube에서 동영상을 검색합니다. 사용자가 영상, 동영상, 유튜브 관련 검색을 요청할 때 사용합니다.

    Args:
        query: 검색어
    """
    try:
        videos = _search_youtube(query)
        _found_videos.clear()
        _found_videos.extend(videos)
        # 모델에게 텍스트 요약 반환
        summary = [f"- {v['title']} (채널: {v['channel']})" for v in videos]
        return f"검색 결과 {len(videos)}건:\n" + "\n".join(summary)
    except requests.HTTPError as e:
        return f"YouTube 검색 실패: {e}"


# =============================================================================
# Streamlit UI
# =============================================================================
st.title("💬 Gemini 챗봇")
st.caption(f"모델: {MODEL_ID} | YouTube 검색 도구 내장")

# 대화 기록 초기화
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 이전 대화 표시
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        # 영상이 있으면 먼저 표시
        if msg.get("videos"):
            render_videos(msg["videos"])
        if msg.get("content"):
            st.markdown(msg["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요 (예: '파이썬 강의 영상 검색해줘')"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답
    with st.chat_message("assistant"):
        _found_videos.clear()

        for attempt in range(3):
            try:
                # run_sync: 도구 호출이 포함될 수 있으므로 동기 실행
                result = agent.run_sync(
                    prompt, message_history=st.session_state.chat_history
                )
                break
            except RuntimeError:
                pass

        # 영상 검색 결과가 있으면 카드로 표시
        videos = list(_found_videos)
        if videos:
            render_videos(videos)

        # 텍스트 응답 표시
        st.markdown(result.output)

    # 대화 기록 업데이트
    st.session_state.chat_messages.append(
        {"role": "assistant", "content": result.output, "videos": videos}
    )
    st.session_state.chat_history = result.all_messages()
