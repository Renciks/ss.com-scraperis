from website import create_app
from flask import render_template, redirect, url_for, request, flash, Flask, abort
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import re
from win10toast_click import ToastNotifier
import webbrowser

tosteris = ToastNotifier() #toastnotifier izsūta windows notifikāciju.
app = create_app() #flask instance
conn = sqlite3.connect('sadalas.db', check_same_thread= False) # Savieno datubāzi
c = conn.cursor() # savienojas ar kursoru
@app.route('/', methods=['GET','POST']) # Nolasa tabulas "Sadala" vērtības un padot uz home.html dropdown izvēlni
def home():
    sadala1 = ("""SELECT * FROM Sadala""")
    c.execute(sadala1)
    data = c.fetchall()
    return render_template("home.html", data = data)


@app.route("/home.html", methods=["GET","POST"]) # Saņemo POST un atjauno datubāzi ar jaunu linku
def linka_ievads():
    if request.method == "POST":
        Generetais_links = request.form["gen_link"]
        c.execute('DELETE FROM aktivi_linki;',)
        sql = '''INSERT INTO aktivi_linki VALUES(?)'''
        c.execute(sql, (Generetais_links,))
        conn.commit()
        return linkaizvads()
    
@app.route("/apraksts.html")
def apraksts():
    return render_template("apraksts.html")

    
def linkaizvads(): #nolasa lietotāja izveidoto linku no datubāzes
    url = ("""SELECT * FROM aktivi_linki""")
    c.execute(url)
    url_links = c.fetchall()

    URL = url_links[0][0] # pārvērš no datu bāzes iegūto linku no korta uz stringu
    Scrapings(URL) # izsauc funkciju Scraping ar padoto vērtību URL

@app.route("/aiziet.html", methods=["POST"]) # aizsūta uz sludinājumu
def doties_uz():
    try: # ja viss labi aizsūta uz linku
        linkz = "https://www.ss.com" + Slud_links[0]
        webbrowser.open(linkz)
    except: # ja links nedarbojās parāda kļūdu
        tosteris.show_toast("Kļūme",
                                "neizdevās atrast sludinājumus, pārbaudi interneta savienojumu un mēģini vēlreiz",
                                duration=6,
                                threaded=True)
    return redirect("/")



Slud_links = []
def Scrapings(URL): # nolasa datus no lietotāja izvēlētās ss.com sadaļas un izprintē tos terminālī
    Slud_list1 = ["0"] # lists kur glabāsies dati iegūtie
    Slud_list2 = [] # lists kurā glabājas iegūtie dati no ss.com

    first_run = True
    while True: # mūžīgi atkārto kodu 
        Slud_list2.clear() # notīra datus no lista
        Slud_links.clear()
        request = requests.get(URL) # savienojās ar mājaslapu kura glabājās URL
        soup = BeautifulSoup(request.content, 'html5lib') # iegūst lapas saturu un parsē to ar html5lib bibliotēkas palīdzību

        sludinajums = soup.find_all('tr', id=re.compile("^tr_")) # ar bibliotēkas re palīdzību beatiful soup atrod visus tr elementus kuriem id sākās ar tr_ 
        slud_ieraksti = soup.find_all('td', {"class": "msg2"}) # atrod visus td elementu ar klasi "msg2"

        for data in soup.find_all('a', {"class": "am"}, limit = 1): # atrod visus elementus td un atlasa limitētu skaitu no tiem
            Slud_list2.append(data.get_text()[:50] ) # piesaista listam katra elementa teksta vērtības pirmos 80 burtus
            Slud_links.append(data['href'])

        if Slud_list1 == Slud_list2: # pārbauda vai ir ielikti jauni sludiājumi salīdzinot iepriekšējos gadījumus
            print("nav jaunu sludinājumu")
            Slud_list2.clear()

        elif first_run == False: # pārbauda vai programma tiek palaista pirmo reizi
            printSlud = Slud_list2[0] +" | sludinājums: "+ "https://www.ss.com" + Slud_links[0] # izsūta notifikāciju par jauno sludinājumu
            Slud_list1.clear()
            tosteris.show_toast("Jauns sludinājums!", # izsūta paziņojumu par jauno sludinājumu
                                printSlud,
                                duration=6,
                                threaded=True)
                                # callback_on_click = aiziet_uz_linku(Slud_links)) #<<< uzspiežot uz sludinājuma vajadzētu aizsūtīt uz sludinājuma adresi bet bibliotēka ir novecojusi :(
            Slud_list1.extend(Slud_list2)
        else: # ja programma tiek palaista pirmo reizi parāda paziņojumu par to.
            tosteris.show_toast("Programma darbojas!", " ", duration=1, threaded=True)
            first_run = False
            
        time.sleep(30) # nogaidā kādu laiku sekundēs

if __name__ == '__main__':
    app.run(debug=True)
