# Funkční požadavky
## 1. Interaktivní tvorba místností a kreslení - Pencil Tool
- doplněk umožní uživateli definovat půdorys klikáním bodů ve 3D prostoru v pohledu shora
- nástroj musí fungovat jako modální operátor - stav, kdy addon přebírá všechny vstupy z myši a klávesnice
- systém musí neustále zachytávat pozici kurzoru, vykreslovat náhled budoucí stěny a čekat na kliknutí, zadání čísla nebo stisk klávesy enter
- potřeba automatického snappingu k osám XYZ - kontrola vzdálenosti kurzoru od existujích bodů nebo os a pokud je dostatečně blízko, zarovná ho k nim
## 2. Generování a úprava parametrických objektů
- objekt stěny nebo otvorů není obyčejná mesh z polygonů, ale dynamický systém řízený vstupními parametry jako je délka, výška, tloušťka, pozice na ose
- addon musí využívat custom properties - bpy.props pro uložení dat do .blend souboru
- každý objekt si pamatuje své parametry, když se hodnota změní na posuvníku, addon musí tuto změnu zachytit pomocí funkce update a přepočítat geometrii
- systém musí umět matematicky a datově svázat otvor s danou stěnou, pokud se stěna posune, všechny závislé otvory na ní musí s ní
- ořez otvorů řešen dynamicky, např. pomocí boolean operací v geometry nodes

## 3. Správa prostoru a metadat
- systém automaticky detekje uzavřené prostory stěn jako místnosti, umožní s nimi pracovat a evidovat jejich data
- algoritická detekve uzavřených křívek, systém prochází graf bodů a zjišťuje, zda tvoří uzavřený tvar, pokud ano, spočítá jeho plochu
- doplněk umožní organizaci místností a podlaží v collections, vytvoří logickou strukturu a poskytne rozhraní k jejich hromadnému přepínání viditelnosti

## 4. Finalizační nástroj
- jakmile je návrh hotový, uživatel potřebuje z tohoto parametrického systému vytvořit obyčejný 3D model pro další zpracování, např. UV mapování nebo export do herního enginu
- systém projde vybrané objekty a postupně trvale aplikovat všechny generátory, následně začistit topologii

# Nefunkční požadavky
## 1. Architektura a technologie

## 2. Výkon a Nedestruktivnost

## 3. Použitelnost a UX

# Volitelné požadavky
## 1. Kontextová nabídka

## 2. Interaktivní 3D manipulátory

## 3. Automatické kótování