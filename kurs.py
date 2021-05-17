import time as t
from matplotlib import gridspec
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

from matplotlib.animation import FuncAnimation
from itertools import count
from matplotlib import animation, rc
from IPython.display import HTML

msft = yf.Ticker("MSFT")
info = msft.info
df = pd.DataFrame.from_dict(info, orient='index', columns=['value'])
df.head(20)

# tabela kursów historycznych
hist = msft.history(period="max")
# print(hist)

# średnia 200-sesyjna
hist = msft.history(period="max")
x = hist.index
y1 = hist["Close"]
y2 = y1.rolling(200).mean()
plt.figure(figsize=(12, 6))
plt.plot(x, y1, y2)
plt.yscale('log')
plt.grid(True)
# plt.show()

# wykres przefiltrowany od 2008 200 wynikow

m = 200
year = 2008

hist = msft.history(period="max")
x = hist.index  # data
y1 = hist["Close"]  # close
y2 = y1.rolling(m).mean()  # średnia 200 wyników

filt = hist.index >= dt.datetime(year, 1, 1)
# hist = hist[filt]
x = x[filt]
y1 = y1[filt]
y2 = y2[filt]

plt.figure(figsize=(12, 6))
plt.plot(x, y1, y2)
plt.yscale('log')
plt.grid(True)
# plt.show()


# wykres przefiltrowany od 2008 200 wynikow z volume i średnią m-sesyjną
m = 200
year = 2021

hist = msft.history(period="max")
x = hist.index  # data
y1 = hist["Close"]  # close
y2 = y1.rolling(m).mean()  # średnia 200 wyników
vol = hist["Volume"]

filt = hist.index >= dt.datetime(year, 1, 1)
# hist = hist[filt]
x = x[filt]
y1 = y1[filt]
y2 = y2[filt]
vol = vol[filt]

fig = plt.figure(figsize=(15, 10))
ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2, colspan=1)
ax2 = plt.subplot2grid((3, 1), (2, 0), rowspan=1, colspan=1, sharex=ax1)

ax1.plot(x, y1, y2)
ax1.grid(True)

ax2.bar(x, vol)
ax2.grid(True)

# fig.tight_layout() #ściśnięcie wykresu
# ax1.axes.xaxis.set_ticklabels([])
plt.setp(ax1.get_xticklabels(), visible=False)
plt.subplots_adjust(hspace=0)  # ściśnięcie wykresów
# plt.show()

# Wyświetlanie w czasie rzeczywistym co sekundę ostatniego kursu akcji

# pobierana jest najmniejsza możliwa paczka danych (z ostatniego dnia co minutę) i pobierany jest z niej ostatni kurs


def current_price(tic):
    currentprice = yf.download(tickers=tic, period="1d", interval="1m")
    lastelement = currentprice["Close"].iloc[-1]  # ostatni element dataframe
    return lastelement

# print('\n' in current_price("MSFT"))


# for time in range(10):
#     print(current_price("MSFT"))
#     t.sleep(1)


fig, ax = plt.subplots()
tic = "MSFT"
current_price = yf.download(tickers=tic, period="1d", interval="1m")
close_price = current_price["Close"]
date = current_price.index  # index dataframe, ostatni dzień kursu
print(current_price)
print(date)

t = np.arange(date[0], date[-1], len(date))

ax = plt.axis([date[0], date[-1], min(close_price) - 1, max(close_price) + 1])

line, = plt.plot(date, close_price)


def animate(i):
    current_price = yf.download(tickers=tic, period="1d", interval="1m")
    close_price = current_price["Close"]
    date = current_price.index  # index dataframe, ostatni dzień kursu
    # t = np.arange(date[0], date[-1], len(date))
    # print("czujka", t)
    # print("czujka", date)
    line.set_data(date, close_price)
    return (line,)


# create animation using the animate() function
myAnimation = animation.FuncAnimation(
    fig, animate, interval=1000, blit=True, repeat=False)

plt.show()

# print("czujka111111", animate(1))
