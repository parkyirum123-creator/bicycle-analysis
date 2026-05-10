import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="따릉이 데이터 분석 대시보드", layout="wide")
st.title("🚲 서울시 따릉이 이용 패턴 분석")
st.markdown("공공데이터를 활용해 기온과 장소에 따른 따릉이 이용 현황을 살펴봅니다.")

# 2. 데이터베이스 연결 확인
DB_FILE = "bicycle.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

if not os.path.exists(DB_FILE):
    st.error(f"⚠️ '{DB_FILE}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

# 데이터 로드 함수 (캐싱을 통해 속도 향상)
@st.cache_data
def run_query(query):
    with get_connection() as conn:
        return pd.read_sql(query, conn)

# --- 시각화 시작 ---

# 1. 월별 이용패턴
st.header("1. 월별 이용패턴")
sql_1 = """
SELECT 대여일자, SUM(이용건수) as 총이용건수 
FROM 이용정보 
GROUP BY 대여일자 
ORDER BY 대여일자
"""
df_monthly = run_query(sql_1)

col1_1, col1_2 = st.columns([2, 1])
with col1_1:
    fig1 = px.line(df_monthly, x='대여일자', y='총이용건수', markers=True, title="월별 총 이용건수 추이")
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.subheader("🔍 SQL 쿼리")
    st.code(sql_1, language='sql')
    st.subheader("💡 인사이트")
    st.info("""
    - 계절적 요인에 따라 이용량이 크게 변동합니다. 
    - 주로 야외 활동이 적합한 봄(5~6월)과 가을(9~10월)에 이용건수가 급증하는 경향을 보입니다.
    """)


# 2. 기온별 평균 이용량
st.header("2. 기온별 평균 이용량")
sql_2 = """
SELECT 
    (CAST(T.평균기온 / 5 AS INT) * 5) as 기온구간, 
    AVG(I.이용건수) as 평균이용건수
FROM 이용정보 I
JOIN 기온 T ON I.대여일자 = T.년월
GROUP BY 기온구간
ORDER BY 기온구간
"""
df_temp = run_query(sql_2)
df_temp['기온구간'] = df_temp['기온구간'].astype(str) + "도 대"

col2_1, col2_2 = st.columns([2, 1])
with col2_1:
    fig2 = px.bar(df_temp, x='기온구간', y='평균이용건수', color='평균이용건수', 
                 title="기온(5도 단위)별 평균 이용건수", color_continuous_scale='Viridis')
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("🔍 SQL 쿼리")
    st.code(sql_2, language='sql')
    st.subheader("💡 인사이트")
    st.info("""
    - 너무 춥거나 너무 더운 날씨보다 15~25도 사이의 적정 기온에서 이용량이 가장 높습니다.
    - 기온이 5도 미만으로 떨어지면 이용량이 급격히 감소하는 것을 알 수 있습니다.
    """)


# 3. 인기 대여소 TOP 10
st.header("3. 인기 대여소 TOP 10")
sql_3 = """
SELECT S.보관소명, SUM(I.이용건수) as 총이용건수
FROM 이용정보 I
JOIN 대여소 S ON I.대여소번호 = S.대여소번호
GROUP BY S.보관소명
ORDER BY 총이용건수 DESC
LIMIT 10
"""
df_top10 = run_query(sql_3).sort_values(by='총이용건수', ascending=True)

col3_1, col3_2 = st.columns([2, 1])
with col3_1:
    fig3 = px.bar(df_top10, x='총이용건수', y='보관소명', orientation='h', 
                 title="이용건수 상위 10개 대여소", color='총이용건수')
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("🔍 SQL 쿼리")
    st.code(sql_3, language='sql')
    st.subheader("💡 인사이트")
    st.info("""
    - 유동인구가 많은 지하철역 인근이나 한강 공원 근처의 대여소가 상위권을 차지합니다.
    - 이들 지역에는 자전거 및 거치대 추가 배치를 고려해볼 수 있습니다.
    """)

st.caption("Data Source: 서울특별시 공공데이터 - 따릉이 이용정보")