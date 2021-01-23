import xml.etree.ElementTree as ET


def SetValueKH(TargetTag, InsertKey, InsertValue):
    for child in root.iter(TargetTag):
        if InsertKey in child.attrib:
            child.set(InsertKey,InsertValue)
        # print(child.tag, child.attrib)

# parse xml file
tree = ET.parse(r"C:\Users\libor\OneDrive\Dokumenty\python\Superfaktura API\KontrolniHlaseniTest.xml")
root = tree.getroot()
#print(root.tag, root.attrib)
'''
for child in root.iter():
    # child.attrib.clear()
    print(child.tag, child.attrib)


# odstranit elementy- iterace do struktury xml nodů
for child in root.findall("DPHKH1"):
    for i in child.findall('VetaA4'):
        child.remove(i)

# Vyrobit nový node pod DPHKH1

Node1 = root.find("DPHKH1")
ET.SubElement(Node1, "VetaA4", attrib={'zakl_dane1': '100', 'dan1': '10'})
'''


a = ET.Element("VetaA4", attrib={'zakl_dane1': '100', 'dan1': '10'}) # vytvoří element
root[0].insert(2,a) # vsune na dané místo dle [index] a pozice (2)

ET.dump(root)


'''

#Přímý přístup do nodů (jako do seznamu/DF, index je 0(řádek), 0(slopuec))
(root[1][0].tag) = "VetaX"
(root[1][0].attrib) = {"DanP":"444", "DZPUC":"6666"}



'''




'''
# odstranit elementy- iterace do struktury xml nodů
for child in root.findall("DPHKH1"):
    for i in child.findall('VetaA4'):
        child.remove(i)

ET.dump(root)
'''





'''
# Set nodes to be updated only
NodeUpate = ["VetaD", "VetaP","VetaC"]
ItemsUpdate = {"rok":str(2019), 'ctvrt':str(4),'obrat23': str(0), 'pln23': str(0), 'pln5': str(0) }

for InsTag in NodeUpate:
    for InsKey, InsValue in ItemsUpdate.items():
        SetValueKH(InsTag, InsKey, InsValue)


for child in root.iter():
    print(child.tag, child.attrib)



# SetValue("dan23","7878")




# Old part
tree.write(r"C:\\Users\\libor\\OneDrive\\Dokumenty\\python\\Superfaktura API\test.xml")
for child in root.iter():
    print(child.tag, child.attrib)
    if "dan23" in child.attrib:
        child.set("dan23","666")
        Kvartal = child.get("dan23")
    print(child.tag, child.attrib)
 '''