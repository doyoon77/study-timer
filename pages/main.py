import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="학생용 학습 타이머",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
def init_session_state():
    defaults = {
        "running": False,
        "start_time": None,
        "elapsed_before_pause": 0.0,  # 일시정지 전까지 누적된 시간 (초)
        "current_subject": "수학",
        "subjects": ["수학", "국어", "영어", "과학", "사회", "기타"],
        "records": [],  # {"subject": str, "duration_sec": float, "start": str, "end": str}
        "last_update": time.time(),
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

# 사이드바 - 과목 관리
with st.sidebar:
    st.header("📚 과목 관리")
    
    # 새 과목 추가
    new_subject = st.text_input("새 과목 추가", placeholder="예: 역사")
    if st.button("추가", use_container_width=True):
        if new_subject and new_subject.strip() and new_subject not in st.session_state.subjects:
            st.session_state.subjects.append(new_subject.strip())
            st.success(f"'{new_subject.strip()}' 추가됨")
            st.rerun()
        elif new_subject in st.session_state.subjects:
            st.warning("이미 존재하는 과목입니다.")
    
    st.divider()
    
    # 현재 과목 선택
    st.subheader("현재 학습 과목")
    selected = st.selectbox(
        "과목 선택",
        options=st.session_state.subjects,
        index=st.session_state.subjects.index(st.session_state.current_subject)
        if st.session_state.current_subject in st.session_state.subjects else 0,
        key="subject_select"
    )
    
    # 과목이 바뀌면 현재 타이머를 자동으로 기록하고 리셋할지 여부
    if selected != st.session_state.current_subject:
        if get_elapsed_seconds() > 0:
            # 과목 변경 시 기존 시간 자동 저장
            duration = get_elapsed_seconds()
            now = datetime.now()
            start_dt = now - timedelta(seconds=duration)
            st.session_state.records.append({
                "subject": st.session_state.current_subject,
                "duration_sec": duration,
                "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "end": now.strftime("%Y-%m-%d %H:%M:%S"),
            })
            st.session_state.elapsed_before_pause = 0.0
            st.session_state.start_time = None
            st.session_state.running = False
        st.session_state.current_subject = selected
        st.rerun()

# 메인 화면
st.title("⏱️ 학생용 학습 타이머")
st.caption("과목별로 공부 시간을 기록하고 관리하세요.")

# 현재 타이머 표시
elapsed = get_elapsed_seconds()
st.markdown(
    f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.2rem; opacity: 0.9;">현재 과목: {st.session_state.current_subject}</h2>
        <h1 style="margin: 10px 0; font-size: 4rem; font-family: monospace; letter-spacing: 4px;">
            {format_time(elapsed)}
        </h1>
        <p style="margin: 0; opacity: 0.8;">
            {"🟢 진행 중" if st.session_state.running else "⏸️ 일시정지 / 대기"}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 버튼 영역
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ 시작", use_container_width=True, type="primary", disabled=st.session_state.running):
        st.session_state.running = True
        st.session_state.start_time = time.time()
        st.rerun()

with col2:
    if st.button("⏸️ 일시정지", use_container_width=True, disabled=not st.session_state.running):
        # 현재까지 경과 시간 저장
        st.session_state.elapsed_before_pause = get_elapsed_seconds()
        st.session_state.running = False
        st.session_state.start_time = None
        st.rerun()

with col3:
    if st.button("🔄 초기화", use_container_width=True):
        # 초기화 전에 시간이 있으면 기록할지 확인은 생략하고 바로 리셋 (사용자가 원할 때 저장 버튼 사용)
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.elapsed_before_pause = 0.0
        st.rerun()

# 저장 버튼 (현재 세션 기록)
st.divider()
if st.button("💾 현재 세션 저장", use_container_width=True, type="secondary"):
    duration = get_elapsed_seconds()
    if duration < 1:
        st.warning("기록할 시간이 너무 짧습니다 (1초 이상).")
    else:
        now = datetime.now()
        start_dt = now - timedelta(seconds=duration)
        st.session_state.records.append({
            "subject": st.session_state.current_subject,
            "duration_sec": duration,
            "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "end": now.strftime("%Y-%m-%d %H:%M:%S"),
        })
        # 저장 후 타이머 리셋
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.elapsed_before_pause = 0.0
        st.success(f"{st.session_state.current_subject} - {format_time(duration)} 저장 완료!")
        st.rerun()

# 실시간 업데이트를 위한 자동 새로고침 (진행 중일 때만)
if st.session_state.running:
    time.sleep(1)
    st.rerun()

# ===== 기록 및 통계 =====
st.header("📊 학습 기록")

if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    df["duration"] = df["duration_sec"].apply(format_time)
    df = df[["subject", "duration", "start", "end"]].rename(columns={
        "subject": "과목",
        "duration": "학습 시간",
        "start": "시작",
        "end": "종료"
    })
    
    # 과목별 합계
    summary = (
        pd.DataFrame(st.session_state.records)
        .groupby("subject")["duration_sec"]
        .sum()
        .reset_index()
    )
    summary["총 시간"] = summary["duration_sec"].apply(format_time)
    summary = summary[["subject", "총 시간"]].rename(columns={"subject": "과목"})
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("과목별 총 학습 시간")
        st.dataframe(summary, use_container_width=True, hide_index=True)
    
    with col_b:
        st.subheader("최근 세션")
        st.dataframe(df.tail(10).iloc[::-1], use_container_width=True, hide_index=True)
    
    # 전체 기록 다운로드
    csv = pd.DataFrame(st.session_state.records).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 전체 기록 CSV 다운로드",
        data=csv,
        file_name=f"study_records_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # 기록 삭제
    if st.button("🗑️ 모든 기록 삭제", type="secondary"):
        st.session_state.records = []
        st.rerun()
else:
    st.info("아직 저장된 학습 기록이 없습니다. 타이머를 사용하고 '현재 세션 저장'을 눌러주세요.")

# 푸터
st.markdown("---")
st.caption("Streamlit Cloud용 학생 학습 타이머 · 과목별 시간 관리")
