import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
import tkinter as tk
import seaborn as sns

from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *

# ------------------------------------------------------------------------------
# GUI - Prezentacja w tkinter
# ------------------------------------------------------------------------------
# kontener tkinter
root = tk.Tk()

# ustawienia kontenera
root.title("Analiza kursu akcji, statystyki i wskaźniki")
root.geometry("1200x800")
root.resizable(True, True)

# miejsce na wykres zagnieżdżony (kurs, volume, RSI)
plotFrame = tk.Frame(root, width=0, height=0)
plotFrame.grid(row=1, column=1)
# miejsce na wykresy ceny kursu w czasie rzeczywistym i analize regresji
plotFrame1 = tk.Frame(plotFrame, width=0, height=0)
plotFrame1.grid(row=1, column=2)

# ------------- WYKRESY --------------
# wykres zagnieżdżony (kurs, volume, RSI)
plot3 = tk.Frame(plotFrame, width=0, height=0)
plot3.grid(row=1, column=1)
# wykres ceny w czasie rzeczywistym
plotRealTime = tk.Frame(plotFrame1, width=0, height=0)
plotRealTime.grid(row=1, column=1)
# wykres analizy regresji
regressionPlot = tk.Frame(plotFrame1, width=0, height=0)
regressionPlot.grid(row=2, column=1)
# -------------------------------------

# miejsce na dane do filtrowania oraz na tabelę ze wskaźnikami
# frameDataInputs = tk.Frame(root, width=0, height=0)
# frameDataInputs.pack(side=tk.BOTTOM, fill=tk.X)

# miejsce na dane do filtrowania
# inputsFrame = tk.Frame(frameDataInputs, width=0, height=0)
# inputsFrame.grid(row=1, column=1)
inputsFrame = tk.Frame(root, width=0, height=0)
inputsFrame.grid(row=2, column=1)

# miejsce na tabelę ze wskaźnikami
# frameData = inputsFrame = tk.Frame(frameDataInputs, width=0, height=0)
# frameData.grid(row=1, column=2)

# -------------- WSKAŹNIKI -------------


# --------------- INPUTY ---------------
# nazwa spółki
labelName = tk.Label(inputsFrame, text="Skrót nazwy spółki").grid(row=0)
inputName = tk.Entry(inputsFrame, width=15)
inputName.grid(row=0, column=1)

# data do wyświetlania na wykresie statystyk
# ROK
labelyear = tk.Label(inputsFrame, text="Rok").grid(row=1)
inputyear = tk.Entry(inputsFrame, width=15)
inputyear.grid(row=1, column=1)
# MIESIĄC
labelmonth = tk.Label(inputsFrame, text="Miesiąc").grid(row=2)
inputmonth = tk.Entry(inputsFrame, width=15)
inputmonth.grid(row=2, column=1)
# DZIEŃ
labelday = tk.Label(inputsFrame, text="Dzień").grid(row=3)
inputday = tk.Entry(inputsFrame, width=15)
inputday.grid(row=3, column=1)

# przycisk do wyświetlania danych po wpisanej dacie
buttonCommitDate = tk.Button(inputsFrame, height=1, width=15,
                             text="Wyświetl dane", command=lambda: inputs_value())
buttonCommitDate.grid(row=4, column=1)
# ------------------------------------------------------------------------------
# tic inicjalny
tic = "MSFT"

# Dane o spółce w dataframe
name = yf.Ticker(tic)
info = name.info
pd.set_option("display.max_rows", None)
df = pd.DataFrame.from_dict(info, orient='index', columns=['value'])

# ------------------------------------------------------------------------------
# Funkcja do rysowania wykresów zagnieżdżoonych (cena, volume, RSI)
# ------------------------------------------------------------------------------


def show_plots(year=2021, month=1, day=1, tic="MSFT"):

    fig1 = plt.figure(figsize=(11, 8))  # rozmiar wykresu
    name = yf.Ticker(tic)  # pobranie danych o spółce tic
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
    # zmienne do statystyk x - sesyjnych
    m = 200
    n = 100
    p = 50

    # osie współrzędnych do wykresu
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

    # rozmiary wykresów w siatce
    plot3 = tk.Frame(plotFrame, width=0, height=0)
    plot3.grid(row=1, column=1)
    # TKINTER canvas
    scatter1 = FigureCanvasTkAgg(fig1, plot3)
    scatter1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


# ------------------------------------------------------------------------------
# Koniec funkcji, wywołanie inicjalne
# ------------------------------------------------------------------------------
show_plots(year=2021, month=1, day=1, tic="MSFT")

# ------------------------------------------------------------------------------
# Wykres ceny kursu akcji z ostatniego dnia w czasie rzeczywistym
# ------------------------------------------------------------------------------


def realTime(tic):

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

    # TKINTER
    plotRealTime = tk.Frame(plotFrame1, width=0, height=0)
    plotRealTime.grid(row=1, column=1)

    scatter2 = FigureCanvasTkAgg(fig2, plotRealTime)
    scatter2.get_tk_widget().grid(row=1, column=1)


# ------------------------------------------------------------------------------
# Koniec funkcji, wywołanie inicjalne
# ------------------------------------------------------------------------------
realTime(tic)

# ------------------------------------------------------------------------------
# Analiza regresji - seaborn
# ------------------------------------------------------------------------------


def regression(tic):
    # pobranie danych historycznych cen zamknięcia dla SPY oraz wybranego tickera (spółki)
    # SPY - index giełdowy
    history = yf.download("SPY " + tic, start="2000-01-01")["Close"]
    # zamiana na %
    spy = history["SPY"].pct_change(periods=1)
    company = history[tic].pct_change(periods=1)

    # wykres regresji
    fig3 = plt.Figure(figsize=(8, 4))
    ax5 = fig3.subplots()
    # sns - wykres z biblioteki seaborn
    sns.regplot(x=spy, y=company, ax=ax5)

    # TKINTER
    regressionPlot = tk.Frame(plotFrame1, width=0, height=0)
    regressionPlot.grid(row=2, column=1)

    scatter3 = FigureCanvasTkAgg(fig3, regressionPlot)
    scatter3.get_tk_widget().grid(row=2, column=2)


# ------------------------------------------------------------------------------
# Koniec funkcji, wywołanie inicjalne
# ------------------------------------------------------------------------------
regression(tic)

# ------------------------------------------------------------------------------
# prezentacja w tabeli wybranych wskaźników
# ------------------------------------------------------------------------------
# słownik key = z df, value - nazwa wskaźnika po angielsku
multiples = {"longName": "Company name", "marketCap": "market capitalisation", "trailingAnnualDividendYield":
             "Dividend yield (12 months)", "payoutRatio": "Payout Ratio", "trailingPE": "P/E", "forwardPE": "forward P/E", "enterpriseToEbitda": "EV/EBITDA", "priceToBook": "P/BV", "sharesPercentSharesOut": "shares short ratio"}

# nowy słownik z nadanymi nazwami po angielsku
dic = {}

# pętla po słowniku wskaźników, odczytuje po kluczu z df wartości wskaźników i wpisuje nazwy i wartości do nowego słownika
for i in range(len(multiples)):
    value = df.loc[list(multiples.keys())[i]].value
    dic[list(multiples.values())[i]] = value
mdf = pd.DataFrame.from_dict(dic, orient='index', columns=['Multiples'])
# mdf
# print(mdf)

# ------------------------------------------------------------------------------
# Funkcja do odswieżania okna GUI z nowymi danymi pobranymi z INPUTÓW
# ------------------------------------------------------------------------------


def inputs_value():
    # zniszczenie nieaktualnych wykresów
    plot3.destroy()
    plotRealTime.destroy()
    regressionPlot.destroy()

    # pobranie danych z inputów
    yearValue = inputyear.get()
    monthValue = inputmonth.get()
    dayValue = inputday.get()
    tic = inputName.get()

    # zmiana na int
    year = int(yearValue)
    month = int(monthValue)
    day = int(dayValue)

    # wywołanie funkcji z nowymi danymi
    realTime(tic)
    regression(tic)
    show_plots(year, month, day, tic)

# ------------------------------------------------------------------------------
# Koniec funkcji
# ------------------------------------------------------------------------------


# wywołanie GUI - musi być na końcu programu
root.mainloop()
