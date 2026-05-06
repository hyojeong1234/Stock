import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import matplotlib.pyplot as plt

st.title("📊 My Stock Portfolio")

# 기존 그대로 유지
stocks = {
    "Samsung": "005930",
    "SK hynix": "000660",
    "Hanwha Aerospace": "012450",
    "Naver": "035420",
    "kakao": "035720",
    "LOT": "083310",
    "Ace Tech": "088800"
}

buy_prices = {
    "Samsung": 50800,
    "SK hynix": 570000,
    "Hanwha Aerospace": 150000,
    "Naver": 190000,
    "kakao": 50000,
    "LOT": 15000,
    "Ace Tech": 2485
}

shares = {
    "Samsung": 5,
    "SK hynix": 1,
    "Hanwha Aerospace": 3,
    "Naver": 3,
    "kakao": 10,
    "LOT": 20,
    "Ace Tech": 100
}

def get_price(code):
    url = f"https://finance.naver.com/item/main.nhn?code={code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    price = soup.select_one("p.no_today span.blind")
    return int(price.text.replace(",", "")) if price else None

result = []

for name, code in stocks.items():
    price = get_price(code)
    result.append({"종목": name, "현재가": price})
    time.sleep(0.5)

df = pd.DataFrame(result).dropna()

df['매수가'] = df['종목'].map(buy_prices)
df['보유수량'] = df['종목'].map(shares)
df['평가금액'] = df['현재가'] * df['보유수량']
df['투자금액'] = df['매수가'] * df['보유수량']
df['수익금'] = df['평가금액'] - df['투자금액']
df['수익률(%)'] = (df['수익금'] / df['투자금액']) * 100

df = df.sort_values(by="수익률(%)", ascending=False)

# 👉 여기부터가 핵심
st.dataframe(df)

colors = ['blue' if x > 0 else 'red' for x in df['수익률(%)']]

fig, ax = plt.subplots()
ax.bar(df['종목'], df['수익률(%)'], color=colors)

st.pyplot(fig)
