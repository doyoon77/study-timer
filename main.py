import streamlit as st
import time
from datetime import datetime, timedelta, date
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
        "todos": [],
        "todo_id_counter": 0,
        "reflections": [],  # 공부 회고 목록
        "reflection_id_counter": 0,
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
                    "duration_sec": duration,
                    "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": now.strftime("%Y-%m-%d %H:%M:%S"),
                })
                st.session_state.elapsed_before_pause = 0.0
                st.session_state.start_time = None
                st.session_state.running = False
            st.session_state.current_subject = selected
            st.rerun()


# ==================== 페이지별 내용 ====================

# ---------- 1. 공부 타이머 ----------
if page == "공부 타이머":
    st.title("⏱️ 공부 타이머")
    st.caption("과목별로 공부 시간을 기록하고 관리하세요.")

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

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ 시작", use_container_width=True, type="primary", disabled=st.session_state.running):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.rerun()

    with col2:
        if st.button("⏸️ 일시정지", use_container_width=True, disabled=not st.session_state.running):
            st.session_state.elapsed_before_pause = get_elapsed_seconds()
            st.session_state.running = False
            st.session_state.start_time = None
            st.rerun()

    with col3:
        if st.button("🔄 초기화", use_container_width=True):
            st.session_state.running = False
            st.session_state.start_time = None
            st.session_state.elapsed_before_pause = 0.0
            st.rerun()

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
            st.session_state.running = False
            st.session_state.start_time = None
            st.session_state.elapsed_before_pause = 0.0
            st.success(f"{st.session_state.current_subject} - {format_time(duration)} 저장 완료!")
            st.rerun()

    if st.session_state.running:
        time.sleep(1)
        st.rerun()

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
        
        csv = pd.DataFrame(st.session_state.records).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 전체 기록 CSV 다운로드",
            data=csv,
            file_name=f"study_records_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        if st.button("🗑️ 모든 기록 삭제", type="secondary"):
            st.session_state.records = []
            st.rerun()
    else:
        st.info("아직 저장된 학습 기록이 없습니다. 타이머를 사용하고 '현재 세션 저장'을 눌러주세요.")


# ---------- 2. 오늘 할일 ----------
elif page == "오늘 할일":
    st.title("✅ 오늘 할일")
    st.caption("과목과 할 일을 입력하고 추가하세요. 여러 개 추가할 수 있습니다.")

    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            todo_subject = st.selectbox(
                "과목",
                options=st.session_state.subjects,
                key="todo_subject"
            )
        
        with col2:
            todo_task = st.text_input(
                "할 일",
                placeholder="예: 수학 문제집 20쪽까지 풀기",
                key="todo_task"
            )
        
        if st.button("➕ 추가", use_container_width=True, type="primary"):
            if todo_task and todo_task.strip():
                st.session_state.todo_id_counter += 1
                st.session_state.todos.append({
                    "id": st.session_state.todo_id_counter,
                    "subject": todo_subject,
                    "task": todo_task.strip(),
                    "done": False,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.success("할 일이 추가되었습니다!")
                st.rerun()
            else:
                st.warning("할 일 내용을 입력해주세요.")

    st.divider()
    st.subheader("📋 할 일 목록")

    if not st.session_state.todos:
        st.info("아직 등록된 할 일이 없습니다. 위에서 추가해보세요!")
    else:
        total = len(st.session_state.todos)
        done_count = sum(1 for t in st.session_state.todos if t["done"])
        st.caption(f"전체 {total}개 중 {done_count}개 완료")

        for todo in st.session_state.todos:
            col_check, col_content, col_delete = st.columns([0.5, 5, 1])
            
            with col_check:
                new_done = st.checkbox(
                    "완료",
                    value=todo["done"],
                    key=f"done_{todo['id']}",
                    label_visibility="collapsed"
                )
                if new_done != todo["done"]:
                    todo["done"] = new_done
                    st.rerun()
            
            with col_content:
                if todo["done"]:
                    st.markdown(
                        f"<span style='color: gray; text-decoration: line-through;'>"
                        f"<b>[{todo['subject']}]</b> {todo['task']}</span> "
                        f"<small style='color:#999'>({todo['created']})</small>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<b>[{todo['subject']}]</b> {todo['task']} "
                        f"<small style='color:#999'>({todo['created']})</small>",
                        unsafe_allow_html=True
                    )
            
            with col_delete:
                if st.button("🗑️", key=f"del_{todo['id']}", help="삭제"):
                    st.session_state.todos = [
                        t for t in st.session_state.todos if t["id"] != todo["id"]
                    ]
                    st.rerun()

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🧹 완료된 할 일만 삭제", use_container_width=True):
                st.session_state.todos = [
                    t for t in st.session_state.todos if not t["done"]
                ]
                st.rerun()
        with col_b:
            if st.button("🗑️ 전체 삭제", use_container_width=True, type="secondary"):
                st.session_state.todos = []
                st.rerun()


# ---------- 3. 공부 회고 ----------
elif page == "공부 회고":
    st.title("📝 공부 회고")
    st.caption("오늘 공부를 돌아보고, 내일 더 잘하기 위한 기록을 남기세요.")

    # ----- 새 회고 작성 -----
    st.subheader("✏️ 오늘의 회고 작성")

    col_date, col_subj = st.columns(2)
    with col_date:
        reflection_date = st.date_input("날짜", value=date.today(), key="ref_date")
    with col_subj:
        reflection_subject = st.selectbox(
            "주요 과목",
            options=st.session_state.subjects,
            key="ref_subject"
        )

    st.markdown("**자기 평가**")
    col_focus, col_understand = st.columns(2)
    with col_focus:
        focus_score = st.slider("집중도", 1, 5, 3, help="1=거의 집중 못함, 5=매우 집중함")
    with col_understand:
        understand_score = st.slider("이해도", 1, 5, 3, help="1=거의 이해 못함, 5=잘 이해함")

    studied_content = st.text_area(
        "오늘 공부한 내용",
        placeholder="예: 이차방정식 근의 공식, 국어 시 해석 연습...",
        height=80,
        key="ref_content"
    )

    good_points = st.text_area(
        "잘한 점 / 뿌듯했던 점",
        placeholder="예: 막혔던 문제를 끝까지 풀어냈다. 계획한 분량을 다 끝냈다.",
        height=70,
        key="ref_good"
    )

    hard_points = st.text_area(
        "아쉬웠던 점 / 어려웠던 점",
        placeholder="예: 중간에 집중력이 떨어져서 휴대폰을 봤다. 개념이 아직 헷갈린다.",
        height=70,
        key="ref_hard"
    )

    tomorrow_goal = st.text_area(
        "내일의 목표",
        placeholder="예: 수학 오답노트 정리 + 영어 단어 30개 암기",
        height=70,
        key="ref_goal"
    )

    if st.button("💾 회고 저장", use_container_width=True, type="primary"):
        if not studied_content.strip() and not good_points.strip() and not hard_points.strip():
            st.warning("내용을 조금이라도 작성해주세요.")
        else:
            st.session_state.reflection_id_counter += 1
            st.session_state.reflections.append({
                "id": st.session_state.reflection_id_counter,
                "date": reflection_date.strftime("%Y-%m-%d"),
                "subject": reflection_subject,
                "focus": focus_score,
                "understand": understand_score,
                "content": studied_content.strip(),
                "good": good_points.strip(),
                "hard": hard_points.strip(),
                "goal": tomorrow_goal.strip(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            st.success("회고가 저장되었습니다!")
            st.rerun()

    st.divider()

    # ----- 과거 회고 목록 -----
    st.subheader("📚 지난 회고 보기")

    if not st.session_state.reflections:
        st.info("아직 저장된 회고가 없습니다. 위에서 첫 회고를 작성해보세요!")
    else:
        # 최신순 정렬
        sorted_refs = sorted(
            st.session_state.reflections,
            key=lambda x: x["date"],
            reverse=True
        )

        # 간단한 통계
        avg_focus = sum(r["focus"] for r in st.session_state.reflections) / len(st.session_state.reflections)
        avg_understand = sum(r["understand"] for r in st.session_state.reflections) / len(st.session_state.reflections)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("총 회고 수", f"{len(st.session_state.reflections)}회")
        with col_s2:
            st.metric("평균 집중도", f"{avg_focus:.1f} / 5")
        with col_s3:
            st.metric("평균 이해도", f"{avg_understand:.1f} / 5")

        st.markdown("---")

        for ref in sorted_refs:
            with st.expander(
                f"📅 {ref['date']}  |  {ref['subject']}  |  집중 {ref['focus']}점 · 이해 {ref['understand']}점",
                expanded=False
            ):
                if ref["content"]:
                    st.markdown(f"**공부한 내용**\n\n{ref['content']}")
                if ref["good"]:
                    st.markdown(f"**잘한 점**\n\n{ref['good']}")
                if ref["hard"]:
                    st.markdown(f"**아쉬웠던 점**\n\n{ref['hard']}")
                if ref["goal"]:
                    st.markdown(f"**다음날 목표**\n\n{ref['goal']}")
                
                st.caption(f"작성 시각: {ref['created_at']}")
                
                if st.button("🗑️ 이 회고 삭제", key=f"del_ref_{ref['id']}"):
                    st.session_state.reflections = [
                        r for r in st.session_state.reflections if r["id"] != ref["id"]
                    ]
                    st.rerun()

        st.divider()
        if st.button("🗑️ 모든 회고 삭제", type="secondary"):
            st.session_state.reflections = []
            st.rerun()


# 푸터
st.markdown("---")
st.caption("학생용 학습 관리 앱 · Streamlit Cloud")
