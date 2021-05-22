import time as t
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import math
import tkinter as tk

from matplotlib import gridspec
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *


root = tk.Tk()
plotFrame = tk.Frame(root, width=300, height=200)
plotFrame.pack(side=tk.TOP, fill=tk.BOTH)
plot3 = tk.Frame(plotFrame, width=300, height=200)
plot3.grid(row=1, column=1)
# plot3.grid(row=1, column=1)

plotRealTime = tk.Frame(plotFrame, width=300, height=200)
# plotRealTime.grid(row=1, column=2)
plotRealTime.grid(row=1, column=2)

inputsFrame = tk.Frame(root, width=300, height=200)
inputsFrame.pack(side=tk.BOTTOM, fill=tk.X)
# inputsFrame.grid(row=2, column=1)
labelyear = tk.Label(inputsFrame, text="Year").grid(row=0)
inputyear = tk.Entry(inputsFrame, width=15)
inputyear.grid(row=0, column=1)
labelmonth = tk.Label(inputsFrame, text="Month").grid(row=1)
inputmonth = tk.Entry(inputsFrame, width=15)
inputmonth.grid(row=1, column=1)
labelday = tk.Label(inputsFrame, text="Day").grid(row=2)
inputday = tk.Entry(inputsFrame, width=15)
inputday.grid(row=2, column=1)


# Dane o spółce w dataframe
tic = "MSFT"  # nazwa spółki w skrócie, może się zmieniać
name = yf.Ticker(tic)
info = name.info
pd.set_option("display.max_rows", None)
df = pd.DataFrame.from_dict(info, orient='index', columns=['value'])
# df.head(123)

# tabela kursów historycznych
hist = name.history(period="max")

# ------------------------------------------------------------------------------
# RSI
# ------------------------------------------------------------------------------
# pobieramy różnicę cen zamknięcia (czy zanotowaliśmy spadek czy wzrost ceny, wynik -/+)
chng = hist["Close"].diff(1)
num = 23  # miesiac 23 robocze

# ----- podział na dwa dataframe w celu rozróżnienia spadków i wzrostów
# suma wzrostów z 23 dni
a = chng.apply(lambda x: 0 if x < 0 else x).rolling(num).sum()
# suma spadków z 23 dni
b = chng.apply(lambda y: 0 if y >= 0 else y).rolling(num).sum()

# wzór na wskaźnik RSI


def rsi(a, b):
    return 100 - (100 / (1 - (a/b)))
# rsi = lambda a, b : 100 - (100 / (1 - (a/b))) # INNY SPOSÓB ZAPISU


RSI = pd.DataFrame()
RSI["rsi"] = rsi(a.iloc[:], b.iloc[:])

# ------------------------------------------------------------------------------
# wykres przefiltrowany od 2008 200 wynikow z volume i średnią m-sesyjną
# ------------------------------------------------------------------------------
m = 200
n = 100
p = 50
year = 2021
month = 1
day = 1


def inputs_value():
    yearValue = inputyear.get()
    monthValue = inputmonth.get()
    dayValue = inputday.get()
    year = int(yearValue)
    month = int(monthValue)
    day = int(dayValue)
    # fig1.clear()
    print(year, month, day)
    return year, month, day


buttonCommit = tk.Button(inputsFrame, height=1, width=10,
                         text="Wyświetl dane", command=lambda: inputs_value())
buttonCommit.grid(row=3, column=1)

# if(buttonCommit):
#     year, month, day = inputs_value()

x = hist.index  # data
y1 = hist["Close"]  # close, cena zamknięcia
y2 = y1.rolling(m).mean()  # średnia 200 wyników
y3 = y1.rolling(n).mean()  # średnia 100 wyników
y4 = y1.rolling(p).mean()  # średnia 50 wyników
vol = hist["Volume"]  # wskaźnik volumen

# filtrowanie po dacie
filt = hist.index >= dt.datetime(year, month, day)

# dane do wykresu przefiltrowane po dacie
x = x[filt]
y1 = y1[filt]  # niebieski wykres, kurs
y2 = y2[filt]  # pomarańczowy wykres - średnia 200 wyników
y3 = y3[filt]  # zielony wykres - średnia 100 wyników
y4 = y4[filt]  # czerwony wykres - średnia 50 wyników
vol = vol[filt]  # słupki, volume
rsi = RSI["rsi"][filt]  # RSI, ostatni wykres

# rozmiary wykresów w siatce
fig1 = plt.figure(figsize=(10, 7))

# podział siatki do wykresu 2:1:1 i opis osi
ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2, colspan=1)
plt.title("Kurs akcji dla danego okresu i średnia m-sesyjna")
plt.ylabel("Cena")
ax2 = plt.subplot2grid((4, 1), (2, 0), rowspan=1, colspan=1, sharex=ax1)
plt.ylabel("Volume")
ax3 = plt.subplot2grid((4, 1), (3, 0), rowspan=1, colspan=1, sharex=ax1)
plt.ylabel("RSI")

# ustawianie wykresów w siatce - grid, jeden pod drugim
# ----- Kurs, średnie x-sesyjne -----
l1, l2, l3, l4 = ax1.plot(x, y1, x, y2, x, y3, x, y4)
ax1.grid(True)
ax1.legend((l1, l2, l3, l4), ("kurs akcji", "średnia 200-sesyjna",
                              "średnia 100-sesyjna", "średnia 50-sesyjna"))

# ----- Volume -----
ax2.bar(x, vol)
ax2.grid(True)

# ----- RSI -----
ax3.plot(x, rsi)
ax3.grid(True)

plt.xlabel("Data")
# widoczność podziałki osi X (dane) ustawiona na niewidoczne
plt.setp(ax1.get_xticklabels(), visible=False)
plt.subplots_adjust(hspace=0)  # ściśnięcie wykresów


# ------------------------------------------------------------------------------
# prezentacja w tabeli wybranych wskaźników
# ------------------------------------------------------------------------------

# słownik key = z df, value - nazwa wskaźnika po angielsku
multiples = {"longName": "Company name", "marketCap": "market capitalisation", "trailingAnnualDividendYield":
             "Dividend yield (12 months)", "payoutRatio": "Payout Ratio", "trailingPE": "P/E", "forwardPE": "forward P/E", "enterpriseToEbitda": "EV/EBITDA", "priceToBook": "P/BV", "sharesPercentSharesOut": "shares short ratio"}
dic = {}  # nowy słownik z nadanymi nazwami po angielsku

# pętla po słowniku wskaźników, odczytuje po kluczu z df wartości wskaźników i wpisuje nazwy i wartości do nowego słownika
for i in range(len(multiples)):
    value = df.loc[list(multiples.keys())[i]].value
    dic[list(multiples.values())[i]] = value
mdf = pd.DataFrame.from_dict(dic, orient='index', columns=['Multiples'])
# mdf
# print(mdf)

# ------------------------------------------------------------------------------
# Wyświetlanie w czasie rzeczywistym co sekundę ostatniego kursu akcji
# ------------------------------------------------------------------------------
# pobierana jest najmniejsza możliwa paczka danych (z ostatniego dnia co minutę) i pobierany jest z niej ostatni kurs


def current_price(tic):
    currentprice = yf.download(tickers=tic, period="1d", interval="1m")
    lastelement = currentprice["Close"].iloc[-1]  # ostatni element dataframe
    return lastelement

# print('\n' in current_price("MSFT"))

# for time in range(10):
#     print(current_price("MSFT"))
#     t.sleep(1)

# ------------------------------------------------------------------------------
# Wykres ceny kursu akcji z ostatniego dnia w czasie rzeczywistym
# ------------------------------------------------------------------------------


fig2, ax = plt.subplots(figsize=(8, 4))

# pobranie ceny kursu z ostatniego dnia co minutę
current_price = yf.download(tickers=tic, period="1d", interval="1m")
# print(current_price)
close_price = current_price["Close"]  # pobranie ceny zamknięcia z tabeli
# index tabeli (1 kolumna), ostatni dzień kursu - data
date = current_price.index

# osie: x- od początku dnia dane z pierwszej minuty do chwili zamknięcia giełdy (+8h z marginesem)
# y - cena kursu + marginesy
ax = plt.axis([date[0], date[0] + dt.timedelta(hours=8),
               min(close_price) - 1, max(close_price) + 1])

line, = plt.plot(date, close_price)
plt.title("Cena kursu akcji w czasie rzeczywistym")

# funkcja do animacji wykresu - kurs w czasie rzeczywistym, aktualizacja co minutę
# wykres ma zakres na osi x cały dzień, linia wyświetla się jednak tylko do chwili obecnej


def animate(i):
    current_price = yf.download(tickers=tic, period="1d", interval="1m")
    close_price = current_price["Close"]
    date = current_price.index  # index dataframe, ostatni dzień kursu
    line.set_data(date, close_price)
    return (line,)


# wywołanie animacji wykresu
myAnimation = animation.FuncAnimation(
    fig2, animate, interval=1000, blit=True, repeat=False)

# ------------------------------------------------------------------------------
# GUI - Prezentacja w tkinter
# ------------------------------------------------------------------------------
root.title("Analiza kursu akcji, statystyki i wskaźniki")
root.geometry("1200x800")
root.resizable(True, True)
# TKINTER FIRST PLOT
scatter1 = FigureCanvasTkAgg(fig1, plot3)
scatter1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
# TKINTER real time
scatter2 = FigureCanvasTkAgg(fig2, plotRealTime)
scatter2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

# SVBar = tk.Scrollbar(root, orient=HORIZONTAL)
# SVBar.pack(side=tk.RIGHT,
#            fill="y")

# SHBar = tk.Scrollbar(root,
#                      orient=tk.HORIZONTAL)
# SHBar.pack(side=tk.BOTTOM,
#            fill="x")

root.mainloop()
