import xml.etree.ElementTree as ET
# zbytečně složité, dá se to dělat přímo do parsovaného xml ale zajímavé pro iterace v seznamu tupplů s vnořeným (nested) slovníkem

def SetValue(InsertKey, InsertValue):
    for i in AttrbList:
        for k in i:
            if InsertKey in k:
                k[InsertKey] = InsertValue
                res = [k[InsertKey] for k in i if InsertKey in k]
                print(res)

# parse xml file
tree = ET.parse(r"C:\Users\libor\OneDrive\Dokumenty\python\Superfaktura API\Vstup1.xml")
root = tree.getroot()
AttrbList = []
for child in root.iter():
    dct = (child.tag, child.attrib)
    # Kvartal = child.find("c_okec").text
    AttrbList.append(dct)
print(AttrbList)

#
SetValue("dan23", str(125))
print(AttrbList)
