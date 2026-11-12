import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="학생용 학습 관리",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
def init_session_state():
    defaults = {
        "running": False,
        "start_time": None,
        "elapsed_before_pause": 0.0,
        "current_subject": "수학",
        "subjects": ["수학", "국어", "영어", "과학", "사회", "기타"],
        "records": [],
        "page": "공부 타이머",
        "todos": [],  # {"id": int, "subject": str, "task": str, "done": bool, "created": str}
        "todo_id_counter": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# 현재 경과 시간 계산 (초)
def get_elapsed_seconds():
    if st.session_state.running and st.session_state.start_time is not None:
        return st.session_state.elapsed_before_pause + (time.time() - st.session_state.start_time)
    return st.session_state.elapsed_before_pause

# 시간 포맷 (HH:MM:SS)
def format_time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ==================== 사이드바 메뉴 ====================
with st.sidebar:
    st.title("📚 학습 관리")
    st.caption("메뉴를 선택하세요")
    
    page = st.radio(
        "메뉴",
        options=["공부 타이머", "오늘 할일", "공부 회고"],
        index=["공부 타이머", "오늘 할일", "공부 회고"].index(st.session_state.page),
        label_visibility="collapsed"
    )
    st.session_state.page = page
    
    st.divider()
    
    # 공부 타이머 페이지일 때만 과목 관리 표시
    if page == "공부 타이머":
        st.header("과목 관리")
        
        new_subject = st.text_input("새 과목 추가", placeholder="예: 역사", key="new_subject_timer")
        if st.button("추가", use_container_width=True, key="add_subject_timer"):
            if new_subject and new_subject.strip() and new_subject not in st.session_state.subjects:
                st.session_state.subjects.append(new_subject.strip())
                st.success(f"'{new_subject.strip()}' 추가됨")
                st.rerun()
            elif new_subject in st.session_state.subjects:
                st.warning("이미 존재하는 과목입니다.")
        
        st.subheader("현재 학습 과목")
        selected = st.selectbox(
            "과목 선택",
            options=st.session_state.subjects,
            index=st.session_state.subjects.index(st.session_state.current_subject)
            if st.session_state.current_subject in st.session_state.subjects else 0,
            key="subject_select"
        )
        
        if selected != st.session_state.current_subject:
            if get_elapsed_seconds() > 0:
                duration = get_elapsed_seconds()
                now = datetime.now()
                start_dt = now - timedelta(seconds=duration)
                st.session_state.records.append({
                    "subject": st.session_state.current_subject,
