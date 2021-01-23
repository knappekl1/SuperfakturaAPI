import requests
import json
import pandas as pd
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import PySimpleGUI as sg


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, indent=4, sort_keys=True)
    print(text)

def sfapi(URL):
  # request API
  credentials="SFAPI email=libor.knappek@gmail.com&apikey=e89c1ba085e6097bf3eba2f99cec7dbb&module=MyPythonModule1&company_id=4974"
  Headers={'Authorization': credentials}
  r = requests.get(URL, headers=Headers)
  # print(r.status_code)
  return(r)

def SetValueDP(InsertKey, InsertValue):
    for child in root.iter():
        if InsertKey in child.attrib:
            child.set(InsertKey,InsertValue)

def SetValueKH(TargetTag, InsertKey, InsertValue):
    for child in root.iter(TargetTag):
        if InsertKey in child.attrib:
            child.set(InsertKey,InsertValue)

def NoData():
    layout1 = [[sg.Text("Parametry nezadány")]]
    window1 = sg.Window("Error msg").Layout(layout1)
    window1.Read()

# Date definitions
DatumDnes = ((str(datetime.now())).split(' ')[0]).split('-')[2] + '.' + ((str(datetime.now())).split(' ')[0]).split('-')[1] + '.' + ((str(datetime.now())).split(' ')[0]).split('-')[0] 

layout = [
    [sg.Text("Načíst údaje ze Superfaktura")],
    [sg.Text("DPH za období", auto_size_text=True)],
    [sg.InputText(key= "ctvrtleti", size=(10,1)), sg.Text("čtvrletí", size=(10,1))],
    [sg.InputText(key= "rok", size=(10,1)), sg.Text("Rok", size=(10,1))],
    [sg.In(DatumDnes, key="DatumZpracovani", size=(10,1)),sg.Text("Datum zpracování ve formátu DD.MM.YYYY", size=(35,1))],
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

# Najdi aktuální kvartál z data
MesicAktual = int(DatumDnes[3 : 5])
QuarterMonths = int(Quarter) * 3
if (QuarterMonths - 3) <= MesicAktual <= QuarterMonths:
    KodKvartalu = 8
else:
    KodKvartalu = 10

# Get expense list
# created: X je číslo periody (8: tento kvartál, 10: minulý kvartál)
CisloPeriody = KodKvartalu
ExpenseURL = "https://moje.superfaktura.cz/expenses/index.json/listinfo:1/created:" + str(CisloPeriody)

Items = sfapi(ExpenseURL).json()["items"]
#jprint(Items)

ExpenseList=[]

for i in Items:
  DIC = i["Client"]["ic_dph"]
  ICO = i["Client"]["ico"]
  Name = i["Client"]["name"]
  Amount = i["Expense"]["amount"]
  VATamount = i["Expense"]["paid"]
  Datum = i["Expense"]["taxdate"]
  TaxDate = Datum[8:10] + '.' + Datum[5:7] + '.' + Datum[0:4]
  ExpenseType = i["Expense"]["type"]
  ExpenseID = i["Expense"]["document_number"]
  Result = {"ExpenseID":ExpenseID, "Name": Name, "DIC":DIC, "ICO":ICO, "TaxDate":TaxDate, "ExVAT":Amount, "InVAT":VATamount, "Type":ExpenseType}
  ExpenseList.append(Result)

# get invoice list, používá stejnou periodu jako náklady
InvoiceURL = "https://moje.superfaktura.cz/invoices/index.json/listinfo:1/created:" + str(CisloPeriody)

Items = sfapi(InvoiceURL).json()["items"]
#jprint(Items)

InvoiceList=[]
for i in Items:
  DIC = i["Client"]["ic_dph"]
  ICO = i["Client"]["ico"]
  Name = i["Client"]["name"]
  Amount = i["Summary"]["vat_base_total"]
  VATamount = i["Summary"]["invoice_total"]
  Datum = i["Invoice"]["delivery"]
  TaxDate = Datum[8:10] + '.' + Datum[5:7] + '.' + Datum[0:4]
  InvoiceID = i["Invoice"]["invoice_no_formatted"]
  Result = {"InvoiceID":InvoiceID,"Name": Name, "DIC":DIC, "ICO":ICO, "TaxDate":TaxDate, "ExVAT":Amount, "InVAT":VATamount}
  InvoiceList.append(Result)

# Create Data Frame 
ExpensesDataFrame = pd.DataFrame(ExpenseList)
InvoiceDataFrame = pd.DataFrame(InvoiceList)

# Calculate Totals and rates
# Invoice DF
InvoiceDataFrame["VAT"] = InvoiceDataFrame["InVAT"] - InvoiceDataFrame["ExVAT"]
InvoiceDataFrame["VATrate"] = round(InvoiceDataFrame["VAT"] / InvoiceDataFrame ["ExVAT"],2)
InvoiceSumExVAT = round(InvoiceDataFrame["ExVAT"].sum())
InvoiceSumInVAT = round(InvoiceDataFrame["InVAT"].sum())
InvoiceSumVAT = round(InvoiceDataFrame["VAT"].sum())
# Tržby pod 10 tis nebo od FO nepodnikatel (nemá IČO)
InvoiceSumExVATsmall = round(InvoiceDataFrame.query('ICO == "" or ExVAT < 10000')["ExVAT"].sum())
InvoiceSumVATsmall = round(InvoiceDataFrame.query('ICO == "" or ExVAT < 10000')["VAT"].sum())

# Expense DF, nechápu ale posílají to z API na rozdíl od Invoice jako string (musí se převést přes .astype(float))
ExpensesDataFrame["InVAT"] = ExpensesDataFrame["InVAT"].astype(float)
ExpensesDataFrame["ExVAT"] = ExpensesDataFrame["ExVAT"].astype(float)
ExpensesDataFrame["VAT"] = ExpensesDataFrame["InVAT"] - ExpensesDataFrame["ExVAT"]
ExpensesDataFrame["VATrate"] = round(ExpensesDataFrame["VAT"] / ExpensesDataFrame["ExVAT"],2)
# Suma pro 21% VAT
ExpensesSumExVAT21 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.21')['ExVAT'].sum()) # query vynechává prázdné DIČ = neplátce 
ExpensesSumInVAT21 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.21')['InVAT'].sum())
ExpensesSumVAT21 = round(ExpensesSumInVAT21 - ExpensesSumExVAT21)
# Suma pro 15% VAT
ExpensesSumExVAT15 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.15')['ExVAT'].sum()) # query vynechává prázdné DIČ = neplátce 
ExpensesSumInVAT15 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.15')['InVAT'].sum())
ExpensesSumVAT15 = round(ExpensesSumInVAT15 - ExpensesSumExVAT15)
# Output pro Kontrolní hlášení
# Náklady pod 10 tis Kč
# Pro VAT 21%
ExpensesSumExVATsmall21 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.21 and ExVAT < 10000')['ExVAT'].sum())
ExpensesSumVATsmall21 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.21 and ExVAT < 10000')['VAT'].sum())
# pro VAT 15%
ExpensesSumExVATsmall15 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.15 and ExVAT < 10000')['ExVAT'].sum())
ExpensesSumVATsmall15 = round(ExpensesDataFrame.query('DIC != "" and VATrate == 0.15 and ExVAT < 10000')['VAT'].sum())

# to be saved as excel
with pd.ExcelWriter(r"C:\Users\libor\Dropbox\LK_docs\DPH\WORKING\summaryVAT.xlsx") as writer:
  InvoiceDataFrame.to_excel(writer,sheet_name="Invoices")
  ExpensesDataFrame.to_excel(writer, sheet_name="Expenses")

# Produce xml file for Přiznání k DPH
# parse xml file
tree = ET.parse(r"C:\Users\libor\OneDrive\Dokumenty\python\Superfaktura API\Vstup1.xml")
root = tree.getroot()

# Change values xml
OutputDict = {"rok":Rok, 'ctvrt':Quarter, "d_poddp":DatumDnes, "obrat23":str(InvoiceSumExVAT),"dan23":str(InvoiceSumVAT), "odp_tuz23_nar":str(ExpensesSumVAT21),
"odp_tuz5_nar":str(ExpensesSumVAT15), "pln23":str(ExpensesSumExVAT21), "pln5":str(ExpensesSumExVAT15),"odp_sum_nar":str(ExpensesSumVAT21 + ExpensesSumVAT15),
"dan_zocelk":str(InvoiceSumVAT), "odp_zocelk":str(ExpensesSumVAT21 + ExpensesSumVAT15), "dano_da":str(InvoiceSumVAT - ExpensesSumVAT21 - ExpensesSumVAT15)}

for OutputKey, OutputValue in OutputDict.items():
  SetValueDP(OutputKey, OutputValue)

# Output xml file 
tree.write(r"C:\Users\libor\Dropbox\LK_docs\DPH\WORKING\PriznaniDPH.xml", encoding="UTF-8", xml_declaration=True)

# produce xml file for Kontrolní hlášení
# parse xml file
tree = ET.parse(r"C:\Users\libor\OneDrive\Dokumenty\python\Superfaktura API\KontrolniHlaseni.xml")
root = tree.getroot()

# Set nodes to be updated only
NodeUpate = ["VetaD", "VetaP","VetaC"]
ItemsUpdate = {"rok":Rok, 'ctvrt':Quarter, "d_poddp":DatumDnes, 'obrat23': str(InvoiceSumExVAT), 'pln23': str(ExpensesSumExVAT21), 'pln5': str(ExpensesSumExVAT15) }

for InsTag in NodeUpate:
    for InsKey, InsValue in ItemsUpdate.items():
        SetValueKH(InsTag, InsKey, InsValue)

# Nods for separate update: VetaA5

SetValueKH("VetaA5","zakl_dane1", str(InvoiceSumExVATsmall))
SetValueKH("VetaA5","dan1", str(InvoiceSumVATsmall))

# Nods for separate update: VetaB3
B3UpdateDict = {"zakl_dane1":str(ExpensesSumExVATsmall21), "dan1":str(ExpensesSumVATsmall21),"zakl_dane2":str(ExpensesSumExVATsmall15),"dan2":str(ExpensesSumVATsmall15)}

for InsKey, InsValue in B3UpdateDict.items():
  SetValueKH("VetaB3",InsKey, InsValue)

# Nods to be added/removed
# VetaA4 (tržby nad 10 000)
# Prepare Data
InvoiceDataFrameLarge = InvoiceDataFrame.query('ICO != "" and ExVAT >= 10000')
InvoiceDictLarge = InvoiceDataFrameLarge.to_dict('records')

#Pass Data to xml
a = 1
if len(InvoiceDictLarge) != 0:
  for i in InvoiceDictLarge:
    OutputInvoiceLarge = {'dic_odb': i["ICO"], 'c_evid_dd': i["InvoiceID"], 'dppd': i["TaxDate"], 'zakl_dane1': str(round(i["ExVAT"])),
    'dan1': str(round(i["VAT"])), 'zakl_dane2': '0', 'dan2': '0', 'zakl_dane3': '0', 'dan3': '0', 'kod_rezim_pl': '0', 'zdph_44': 'N'}
    a += 1
    NewElement = ET.Element("VetaA4", attrib=OutputInvoiceLarge)
    root[0].insert(a,NewElement)

# Veta B2 (náklady nad 10000 a plátce DPH)
# Prepare data
ExpensesDataFrameLarge = ExpensesDataFrame.query('DIC != "" and ExVAT >= 10000')
ExpensesDictLarge = ExpensesDataFrameLarge.to_dict('records')

# Pass data to xml
b=1
if len(ExpensesDictLarge) != 0:
  for i in ExpensesDictLarge:
    OutputExpenseLarge = {'dic_dod': re.findall("\d+", i["DIC"])[0], 'c_evid_dd': i["ExpenseID"], 'dppd': i["TaxDate"],
    'zakl_dane1': str(round(i["ExVAT"] if i["VATrate"] == 0.21 else 0)),
    'dan1': str(round(i["VAT"] if i["VATrate"] == 0.21 else 0)),
    'zakl_dane2': str(round(i["ExVAT"] if i["VATrate"] == 0.15 else 0)),
    'dan2': str(round(i["VAT"] if i["VATrate"] == 0.15 else 0)),
    'zakl_dane3': '0', 'dan3': '0', 'pomer': 'N', 'zdph_44': 'N'}
    b += 1
    NewElement = ET.Element("VetaB2", attrib=OutputExpenseLarge)
    root[0].insert(a + 2,NewElement)

# Output xml file
tree.write(r"C:\Users\libor\Dropbox\LK_docs\DPH\WORKING\KontrolniHlaseni.xml", encoding="UTF-8", xml_declaration=True)
