import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import matplotlib.pyplot as plt

st.title("📊 Stock Portfolio")

# 🔄 새로고침 버튼
if st.button("🔄 새로고침"):
    st.cache_data.clear()
    st.rerun()

# 📌 종목 정보
stocks = {
    "Samsung": "005930",
    "SK hynix": "000660",
    "Hanwha Aeros": "012450",
    "Naver": "035420",
    "kakao": "035720",
    "LOT": "083310",
    "Ace Tech": "088800"
}

buy_prices = {
    "Samsung": 50800,
    "SK hynix": 570000,
    "Hanwha Aeros": 150000,
    "Naver": 190000,
    "kakao": 50000,
    "LOT": 15000,
    "Ace Tech": 2485
}

shares = {
    "Samsung": 5,
    "SK hynix": 1,
    "Hanwha Aeros": 3,
    "Naver": 3,
    "kakao": 10,
    "LOT": 20,
    "Ace Tech": 100
}

# 📌 가격 크롤링 함수
@st.cache_data(ttl=300)
def get_price(code):
    try:
        url = f"https://finance.naver.com/item/main.nhn?code={code}"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        price = soup.select_one("p.no_today span.blind")

        if price:
            return int(price.text.replace(",", ""))
        return None

    except Exception:
        return None


# 📌 데이터 수집
with st.spinner("데이터 가져오는 중..."):
    result = []

    for name, code in stocks.items():
        price = get_price(code)

        if price is not None:
            result.append({
                "종목": name,
                "현재가": price
            })

        time.sleep(0.3)

# 📌 데이터프레임 생성
df = pd.DataFrame(result)

# 🚨 빈 데이터 처리
if df.empty:
    st.warning("데이터를 불러오지 못했습니다.")
    st.stop()

# 📌 매핑 데이터 추가
df["매수가"] = df["종목"].map(buy_prices)
df["보유수량"] = df["종목"].map(shares)

# 📌 계산
df["평가금액"] = df["현재가"] * df["보유수량"]
df["투자금액"] = df["매수가"] * df["보유수량"]
df["수익금"] = df["평가금액"] - df["투자금액"]
df["수익률(%)"] = (df["수익금"] / df["투자금액"]) * 100
df["비중(%)"] = df["평가금액"] / df["평가금액"].sum() * 100

df = df.sort_values(by="수익률(%)", ascending=False)

# 🏆 최고 수익 종목
st.subheader("🏆 최고 수익 종목")
st.write(df.iloc[0])

# 📊 테이블 출력 (안정 버전)
st.subheader("📊 포트폴리오")
st.dataframe(df)

# 📉 수익률 그래프
colors = ["blue" if x > 0 else "red" for x in df["수익률(%)"]]

fig, ax = plt.subplots()
ax.bar(df["종목"], df["수익률(%)"], color=colors)
ax.set_title("Return (%)")
st.pyplot(fig)

# 💰 전체 수익
total_invest = df["투자금액"].sum()
total_value = df["평가금액"].sum()

total_rate = ((total_value - total_invest) / total_invest * 100) if total_invest != 0 else 0

st.metric("총 자산", f"{total_value:,}원")
st.metric("수익률", f"{total_rate:.2f}%")

# 🥧 비중 차트
st.subheader("📊 포트폴리오 비중")

fig2, ax2 = plt.subplots()
ax2.pie(df["비중(%)"], labels=df["종목"], autopct="%1.1f%%")
st.pyplot(fig2)
