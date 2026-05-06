import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ------------------------
# 1. 폰트 설정 (한글 깨짐 해결)
# ------------------------
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# ------------------------
# 2. 종목 정보 (수정 가능)
# ------------------------
stocks = {
    "Samsung": "005930",
    "SK hynix": "000660",
    "Hanwha Aerospace": "012450",
    "Naver": "035420",
    "kakao": "035720",
    "LOT": "083310",
    "Ace Tech": "088800"
}

# 내가 산 가격
buy_prices = {
    "Samsung": 50800,
    "SK hynix": 570000,
    "Hanwha Aerospace": 150000,
    "Naver": 190000,
    "kakao": 50000,
    "LOT": 15000,
    "Ace Tech": 2485
}

# 보유 수량
shares = {
    "Samsung": 5,
    "SK hynix": 1,
    "Hanwha Aerospace": 3,
    "Naver": 3,
    "kakao": 10,
    "LOT": 20,
    "Ace Tech": 100
}

# ------------------------
# 3. 현재가 크롤링 함수
# ------------------------
def get_price(code):
    url = f"https://finance.naver.com/item/main.nhn?code={code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    price = soup.select_one("p.no_today span.blind")
    
    if price:
        return int(price.text.replace(",", ""))
    else:
        return None

# ------------------------
# 4. 데이터 수집
# ------------------------
result = []

for name, code in stocks.items():
    price = get_price(code)
    
    result.append({
        "종목": name,
        "현재가": price
    })
    
    time.sleep(1)

df = pd.DataFrame(result)

# ------------------------
# 5. 포트폴리오 계산
# ------------------------
df['매수가'] = df['종목'].map(buy_prices)
df['보유수량'] = df['종목'].map(shares)

df['평가금액'] = df['현재가'] * df['보유수량']
df['투자금액'] = df['매수가'] * df['보유수량']

df['수익금'] = df['평가금액'] - df['투자금액']
df['수익률(%)'] = (df['수익금'] / df['투자금액']) * 100

# 정렬
df = df.sort_values(by="수익률(%)", ascending=False)

print(df)

# ------------------------
# 6. 그래프 (수익/손실 색상)
# ------------------------
colors = ['blue' if x > 0 else 'red' for x in df['수익률(%)']]

plt.figure(figsize=(10,5))
plt.bar(df['종목'], df['수익률(%)'], color=colors)

plt.title("rate of return")
plt.xlabel("Stock")
plt.ylabel("rate (%)")

plt.xticks(rotation=45)
plt.show()

# ------------------------
# 7. 총 자산 요약
# ------------------------
total_invest = df['투자금액'].sum()
total_value = df['평가금액'].sum()
total_return = total_value - total_invest
total_rate = (total_return / total_invest) * 100

print("\n📊 총 투자금:", total_invest)
print("📊 현재 자산:", total_value)
print("📊 총 수익:", total_return)
print(f"📊 총 수익률: {total_rate:.2f}%")
