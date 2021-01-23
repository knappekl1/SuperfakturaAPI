
from datetime import datetime
import PySimpleGUI as sg

def NoData():
    layout1 = [[sg.Text("Parametry nezadány")]]
    window1 = sg.Window("Error msg").Layout(layout1)
    window1.Read()

DatumDnes = ((str(datetime.now())).split(' ')[0]).split('-')[2] + '.' + ((str(datetime.now())).split(' ')[0]).split('-')[1] + '.' + ((str(datetime.now())).split(' ')[0]).split('-')[0]
    

layout = [
    [sg.Text("Načíst údaje ze Superfaktura")],
    [sg.Text("DPH za období", auto_size_text=True)],
    [sg.InputText(key= "ctvrtleti", size=(10,1)), sg.Text("čtvrtetí", size=(10,1))],
    [sg.InputText(key= "rok", size=(10,1)), sg.Text("Rok", size=(10,1))],
    [sg.In(DatumDnes, key="DatumZpracovani", size=(10,1)),sg.Text("Datum zpracování ve formátu DD.MM.YYYY", size=(32,1))],
    [sg.CButton("Run")]#close button
    ]

window = sg.Window('Přiznání k DPH').Layout(layout)
Button, Values = window.Read() # tohle musí být aby se okno objevilo

if Button == None or len(Values.get("rok")) == 0 or len(Values.get("ctvrtleti")) == 0:
    NoData()
    exit(0)
else:
    Rok = Values.get("rok")
    Quarter = Values.get("ctvrtleti")
    DatumDnes = Values.get("DatumZpracovani")

MesicAktual = int(DatumDnes[3:5])

QuarterMonths = int(Quarter) * 3

if (QuarterMonths - 3) <= MesicAktual <= QuarterMonths:
    KodKvartalu = 8
else:
    KodKvartalu = 10

print(KodKvartalu)
