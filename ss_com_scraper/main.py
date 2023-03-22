from website import create_app
from flask import render_template, redirect, url_for, request, flash, Flask, abort
import sqlite3
import requests
from bs4 import BeautifulSoup
import html5lib
import time
import re

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


def Scrapings(URL): # nolasa datus no lietotāja izvēlētās ss.com sadaļas un izprintē tos terminālī
    Slud_list1 = [] # lists kur glabāsies dati iegūtie
    Slud_list2 = [] # lists kurā glabājas iegūtie dati no ss.com


    while True: # mūžīgi atkārto kodu 
        Slud_list2.clear() # notīra datus no lista
        request = requests.get(URL) # savienojās ar mājaslapu kura glabājās URL
        soup = BeautifulSoup(request.content, 'html5lib') # iegūst lapas saturu un parsē to ar html5lib bibliotēkas palīdzību

        sludinajums = soup.find_all('tr', id=re.compile("^tr_")) # ar bibliotēkas re palīdzību beatiful soup atrod visus tr elementus kuriem id sākās ar tr_ 
        slud_ieraksti = soup.find_all('td', {"class": "msg2"}) # atrod visus td elementu ar klasi "msg2"
        for data in soup.find_all('a', {"class": "am"}, limit = 5): # atrod visus elementus td un atlasa limitētu skaitu no tiem
            Slud_list2.append(data.get_text()[:80] ) # piesaista listam katra elementa teksta vērtības pirmos 80 burtus

        if Slud_list1 == Slud_list2: # pārbauda vai ir ielikti jauni sludiājumi salīdzinot iepriekšējos gadījumus
            print("nav jaunu sludinājumu")
            Slud_list2.clear()

        else:
            print("IR JAUNS SLUDINĀJUMS!")
            Slud_list1.clear()
            Slud_list1.extend(Slud_list2)
            print("Jaunākais sludiājums " +URL+ " Ir: ") 
            print(Slud_list1[0]) # izvada jaunākā sludinājuma pirmos 5 aprakstus
            
        time.sleep(100) # nogaidā kādu laiku sekundēs


if __name__ == '__main__':
    app.run(debug=True)
