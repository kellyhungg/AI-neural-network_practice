# -*- coding: utf-8 -*-
"""RNN, LSTM, GRU: 蘋果公司美股股價預測.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aGG2rbrpl1uzqM3QwEV0Fhf2Typ1yaP8
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

import matplotlib.pyplot as plt

"""## 資料集準備"""

# Google股價資料可以從美國Yahoo金融網站下載：https://finance.yahoo.com/quote/GOOG/
# 訓練資料集2017/01/01-2021/12/31
# 測試資料集2022/01/01-2022/4/30

# 載入Google股價的訓練資料集
df_train = pd.read_csv("GOOG_Stock_Price_Train.csv",index_col="Date",parse_dates=True)
df_train.head()

X_train_set = df_train.iloc[:,4:5].values  # Adj Close欄位
X_train_len = len(X_train_set)
print("筆數: ", X_train_len)

# 產生特徵資料和標籤資料
def create_dataset(ds, look_back=1):
  X_data, Y_data = [],[]
  for i in range(len(ds)-look_back):
    X_data.append(ds[i:(i+look_back), 0])
    Y_data.append(ds[i+look_back, 0])
  
  return np.array(X_data), np.array(Y_data)

# 設定回看天數
look_back = 60

X_train, Y_train = create_dataset(X_train_set, look_back)
print("回看天數:", look_back)
print("X_train.shape: ", X_train.shape)
print("Y_train.shape: ", Y_train.shape)
print(X_train[0])
print(X_train[1])
print(Y_train[0])

np.random.seed(10)  # 指定亂數種子

# 特徵標準化 - 正規化
sc = MinMaxScaler() 
X_train_set = sc.fit_transform(X_train_set)

# 分割成特徵資料和標籤資料
X_train, Y_train = create_dataset(X_train_set, look_back)
# 轉換成(樣本數, 時步, 特徵)張量
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
print("X_train.shape: ", X_train.shape)
print("Y_train.shape: ", Y_train.shape)

"""## 打造LSTM模型預測google股價"""

# 定義模型
model = Sequential()
model.add(LSTM(50, return_sequences=True,input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(50))
model.add(Dropout(0.2))
model.add(Dense(1))
model.summary()   # 顯示模型摘要資訊

# 編譯模型
model.compile(loss="mse", optimizer="adam")
# 訓練模型
model.fit(X_train, Y_train, epochs=100, batch_size=32)

# 使用模型預測股價 - 2017年1~3月預測 4月份股價
df_test = pd.read_csv("GOOG_Stock_Price_Test.csv")
X_test_set = df_test.iloc[:,4:5].values
X_test_set = sc.transform(X_test_set) # 特徵標準化
# 產生特徵資料和標籤資料
X_test, Y_test = create_dataset(X_test_set, look_back)
# 轉換成(樣本數, 時步, 特徵)張量
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

X_test_pred = model.predict(X_test)
# 將（被標準化過的）預測值與實際值轉換回真實股價數值
X_test_pred_price = sc.inverse_transform(X_test_pred)
Y_test_price = sc.inverse_transform(Y_test.reshape(-1, 1))

# 繪出股價圖表
plt.plot(Y_test_price, color="red", label="Real Stock Price")
plt.plot(X_test_pred_price, color="blue", label="Predicted Stock Price")
plt.title("2017 Google Stock Price Prediction")
plt.xlabel("Time")
plt.ylabel("Google Time Price")
plt.legend()
plt.show()

# 儲存Keras模型
model.save("LSTM_StockPrice.h5")

"""---

## 作業：實作案例 蘋果公司美股股價預測 (美股代號: AAPL)
#### 蒐集過去五年的股價資料建立並訓練模型
#### 以今年初到四月底的股價為預測資料
#### 回看60筆數據（一季1~3月)，來預測後續(4月份)價格走勢
##### 訓練資料2017/01/01-2021/12/31
##### 測試資料2022/01/01-2022/4/30
"""

from sklearn.metrics import r2_score

r2_score(Y_test, X_test_pred) #一模一樣會是會是1, 負相關會是負的



