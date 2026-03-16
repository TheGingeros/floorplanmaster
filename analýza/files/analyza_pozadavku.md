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

## 5. Kontextová nabídka - pet palette
- po kliknutí na určitý objekt/prvek se přímo na daném místě na obrazovce objeví malá plovoucí nabídka s akcemi
- addon musí zachytávat události myši, provést raycast a zjistit, na jakou část objektu uživatel kliknul
- pomocí modulu gpu nebo blf nakreslit a ovládat vlastní UI vrstu překrývající 3D viewport

## 6. Interaktivní 3D manipulátory
- místo zadávání úpravy do panelu může uživatel chytit barevnouo šipku přímo u zdi a táhnout s ní hahoru
- využití rozhraní bpy.types.Gizmo a GizmoGroup 

# Nefunkční požadavky
## 1. Architektura a technologie
- geometry nodes jako výpočetní jádro addonu
- logika tvarování geometrie bude díky geometry nodes stromům
- python bude sloužit jako manažer, které tyto stromy bude připojovat a měnit jejich vstupy
- oddělení vizuální logiky a aplikační logiky
- zero dependency - addon nesmí k běhu potřebovat doinstalování externích knihoven - pro běžného uživatele složité
- vše se musí zvládnout pomocí bpy a standardní knihovny Python

## 2. Výkon a Nedestruktivnost
- systém musí reagovat plynule, netrhat se a uživatel nesmí ztratit možnost úpravy ani pro komplexních úpravách a generace
- minimalizace výpočetní náročnosti při operacích
- důraz na optimalizaci při přepočtu parametrů
- respoektování [DepsGraph](definice.md#depsgraph---dependency-graph) - systém závislostí v Blenderu, aby nedocházelo ke zbytečným cyklickým přepočtům celé scény

## 3. Použitelnost a UX
- vzhled addonu by měl působit jako nativní součást blenderu
- striktní použití zabudovaných UI komponent - UILayout.row atd
- logické seskupování nástrojů do záložek, přidávání Tooltips
- důraz na ošetření chyb - srozumitelný feedback při špatných operací, například přidání okna do stěny, která je menší než zadaná velikost okna

## 4. Automatické kótování
- vizualizace rozměrů, která neustále ukazují velikost, aniž by se musela překreslovat
- generování dynamických textů přes modul blf přímo do viewportu přes draw_handler
- tyto kóty se musí aktulizovat nejen při změně délky stěny ale musí se správně orientovat podle pohledu kamery
