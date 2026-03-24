# 1. Reprezentace geometrie
- **geometrie** = definuje polohu prvků v prostoru
- **topologie** = definuje vzájemné vztahy a propojení
- v blenderu je základní jednotkou mesh - složena z vrcholů, hran a ploch
- každá mesh nese specifické informace o své roli v celkové struktuře

## Datová struktura BMesh a její význam pro architektonické modelování
- BMesh je interní datová struktura Blenderu, která je na rozdíl od tradičních struktur založených na trojúhelnících podporuje n-gony (polygony s více než 4 vrcholy) 
- využívá systém podobný half-edge datovým strukturám, kde jsou vztahy mezi plochami a hranami uloženy tak, aby umožňovaly rychlou navigaci po povrchu sítě
- z pohledu parametrického modelování nabízí BMesh skrze python API (modul bmesh) nízkoúrovňový přístup k topologii
- možnost dotazovat se, které hrany jsou spojeny s daným vrcholem a tedy provádět akce jako je např. dissolve bez poškození okolní topologie
- tento přístup je nezbytný pro algoritmy, které vyžadují detailní manipulaci s jednotlivými elementy sítě na základě komplexních pravidel

#### Implementace pomocí BMesh
- obvykle se začíná načtením 2D hran
- algoritmus musí identifikovat uzavřené smyčky hran představující obrysy místností nebo osy stěn
- výhodou Pythonu je snadná integrace s externími knihovnami pro výpočetní geometrii nebo grafové algoritmy
- operace tloušťky (offset) se v bmesh často provádí pomocí operátoru `bmesh.ops.bevel`
    - aplikovaný na hrany nebo vlastním algoritmem, který posouvá vrcholy podél normál hran
- API poskytuje funkci `offset_multiplier`, která pomáhá udržovat tloušťku stěny i při ostrých úhlech výpočtem sharpness faktoru vrcholu
- tento proces je v Pythonu relativně pomalý, zejména pokud je třeba neustále validovat integritu sítě a předcházet vzniku non-manifold geometrie
    - struktura sítě (mesh), která by nemohla existovat v reálném fyzickém světě

## Geometry nodes a paradigma polí
- uživatel definuje systém pravidel, která jsou aplikována na celou geometrii současně
- data jsou reprezentována jako pole atributů, která jsou vázána na různé domény - vrcholy, hrany, plochy, instance
- pro architekturu to znamená, že informace jako typu stěny nebo příslušnost k místnosti mohou být uloženy přímo v geometrii jako pojmenované atributy
- tento přístup umožňuje extrémně rychlou vizuální zpětnou vazbu, neboť systém je optimalizován pro multithreading a běží v nativním kódu C++

#### Implementace pomocí Geometry Nodes
- stěny se nejčastěji generují z křivek pomocí uzlu` Curve to Mesh`
- hlavní výzvou je zde Miter Joint problém - standardní vytažení profilu podél křivky vede ke ztenčení stěny v ostrých rozích
- je potřeba implementovat **matematickou korekci měřítka profilu v každém bodě:**
    - koreční faktor f pro bod v rohu s úhlem theta je dán vztahem: f= 1 / sin(theta/2)
    - v geometry nodes se tento výpočet provádí pomocí vektorové matematiky, kde se určuje úhel mezi sousedními segmenty stěny pomocí skalárního součinu a následně se mění měřítko profilu v daném bodě
    - přestože je toto nastavení v uzlech komplexnější na přípravu, jeho použití je rychlé a umožňuje dynamicky měnit tloušťku stěn pouhým posunutím bodu v 2D půdorysu

## Porovnání bmesh a Geometry nodes pro generování 3D stěn

| Charakteristika | BMesh | Geometry Nodes |
| :--- | :--- | :--- |
| **Základní jednotka** | Entita (Vertex, Edge, Face) | Doména a Atributy |
| **Způsob práce** | Iterativní / Imperativní | Paralelní / Deklarativní |
| **Výkon** | Omezený interpretací Pythonu  | Vysoce optimalizované C++  |
| **Topologická flexibilita** | Absolutní (přímá změna struktury) | Omezená na definované uzly |
| **Vizuální odezva** | Po spuštění skriptu | Real-time v 3D viewportu  |

## Výkonnostní analýza a stabilita
- v rozsáhlých scénách se Geometry nodes jeví jako efektivnější a rychlejší
- python script musí při každé změně znovu vybudovat celou BMesh strukturu a promítnout jí
- geometry nodes pracují v rámci modifikátorského stacku a reevaluují pouze nezbytné části

| Operace | bmesh (Python) | Geometry Nodes |
| :--- | :--- | :--- |
| **Vytváření tloušťky** | Přesné, ale výpočetně drahé | Vyžaduje manuální matematickou korekci |
| **Multithreading** | Ne (omezení Pythonu) | Ano (nativní implementace)  |
| **Stabilita topologie** | Riziko vzniku non-manifold chyb  | Stabilnější díky omezenému rozsahu operací |
| **Iterace vývoje** | Pomalá (editace kódu) |Rychlá (přetahování uzlů) |

[Zdroje](./sources.md#reprezentace-geometrie---bmesh-a-geometry-nodes)

# 2. Datová reprezentace logické struktury sítě místností
- pro parametrické modelování není mesh dostatečnou reprezentací
- systém musí vědět, že prostor A je například obývací pokoj a sousedí s prostorem B, který je kuchyní
- existují hlavní dva přístupy k uložení této logiky - **topologické sítě(half-edge)** a **abstraktní grafy**

### Abstraktní grafy - grafová reprezentace
- pro reprezentaci logické struktury jako je budova jsou nejvhodnější **strukturální grafy:**
    - **Uzly/Vrcholy** reprezentují funkční prostory(místnosti) nebo wall-junctions (body setkání stěn) - možnost použít oba jako duální graf
    - **Hrany** reprezentují fyzické stěny nebo komunikační propojení(dveře, otvory)

#### Strukturální graf pro základ kreslení
- pro interaktivní kreslení je strukturální graf nezbytný, protože přímo odpovídá fyzické realitě stěn
- **Reprezentace:**
    - Uzly ($V_s$) jsou body spojení stěn s XY souřadnicemi 
    - Hrany ($E_s$) jsou osy stěn
- **Role:**
    - slouží jako vodicí geometrie pro Geometry Nodes
    - tato vrstva řeší úhly napojení a tloušťku stěn
- **Technické specifikum:**
    - graf je planární. 
    - každá hrana v něm reprezentuje fyzickou stěnu, která odděluje buď dva prostory, nebo prostor od exteriéru
#### Node Relation Graph pro sématiku místností
- **Reprezentace:**
    - Uzly ($V_r$) jsou středy místností
    - Hrany ($E_r$) reprezentují relace sousednosti nebo prostupnosti (dveře)
- **Role:**
    - uchovává nefyzikální metadata
    - umožňuje dotazy typu: Sousedí obývací pokoj s chodbou? nebo Jaká je celková plocha všech ložnic?
#### Hybridní spojení - princip minimálních cyklů
- klíčem k realizaci je, že místnost v NRG je v podstatě minimální uzavřený cyklus ve strukturálním grafu

| Akce v addonu | Změna ve strukturálním grafu | Dopad na NRG Room Graph |
| :--- | :--- | :--- |
| Nakreslení nové stěny | Přidání hrany $E_s$ | Algoritmus hledá, zda vznikl nový cyklus. Pokud ano, v NRG vznikne uzel místnosti |
| Vložení dveří | Atribut na hraně $E_s$ | V NRG se vytvoří hrana $E_r$ propojující sousední uzly místností |
| Smazání stěny | Odstranění hrany $E_s$ | Dvě sousední místnosti v NRG se spojí do jedné (node fusion) pokud je stěna spojovala, jinak odstranění uzlu místnosti |


### Datový model - MultiGraph
- využití knihoven jako NetworkX v prostředí Blenderu umožňuje provádět prostorové analýzy, které jsou čistě geometrickými nástroji nedosažitelné
    - například použít algoritmus pro hledání nejkratší cesty (Dijkstra) pro ověření evakuačních tras nebo automaticky generovat sémantické popisky místností na základě jejich konektivity
- nejefektivnější systém za využití hybridního modelu
- tento model umožňuje například změnit typ oken v celé jižní straně budovy pouhou změnou jednoho parametru v grafu, což se okamžitě projeví v geometry nodes díky dynamickému čtění atributů

#### Vrstva 1. Topologický skelet (Strukturální)
- čistá grafová data o junction bodech a stěnách
- NetworkX zde vypočítává planární embedding a identifikuje "Face" (místnosti) pomocí metod pro hledání cyklů
#### Vrstva 2: Sémantický dual (NRG):
- uzly této vrstvy jsou mapovány na ID cyklů z Vrstvy 1
- změna geometrie ve Vrstvě 1 (např. posun stěny) aktualizuje pouze atribut "Area" v uzlu Vrstvy 2, aniž by se měnila její identita
#### Synchronizační bridge (Named Attributes)
- python addon v každém kroku serializuje data z grafu do Named Attributes meshe v Blenderu (např. `room_id` na Face doméně, `wall_thickness` na Edge doméně)
- Geometry Nodes pak tato data čtou a generují 3D objemy v reálném čase

[Zdroje](./sources.md#datová-reprezentace-logické-struktury-sítě-místností)

# 3. Tvorba otvorů pro okna a dveře - nedestruktivní workflow
- v parametrickém modelování je kritické, aby otvory pro okna a dveře byly plně dynamické
-pokud dojde k posunu stěny, okno se musí posunout s ní a otvor se musí automaticky regenerovat bez nutnosti manuálního zásahu
- lze rešit pomocí tří metod:

### Boolean operace spravované přes Python API
- tento přístup využívá standardní modifikátorový stack Blenderu, kde Python skript dynamicky vytváří a konfiguruje objekty typu `cutter` a přiřazuje je ke stěně
- každý modifikátor v Blenderu představuje separátní výpočetní krok v rámci objektu
- při použití `Exact` solveru se využívají homogenní celočíselné souřadnice k zajištění absolutní přesnosti, což eliminuje numerické chyby u coplanárních ploch, ale je to náročné na paměť
- hlavní nevýhodou při správě přes API je, že každá Booleovská operace mezi dvěma objekty musí brát v úvahu jejich světové transformační matice
- pokud souřadnice po transformaci nejsou binárně identické (např. kvůli zaokrouhlovací chybě floatů), `Exact` solver může selhat při detekci společných ploch, což vede k artefaktům

### Mesh Boolean v Geometry Nodes
- vše v rámci jednoho node-tree, vysoký výkon 
- náročnější na logiku injection dat oken 

### Metody bez Booleovských operací (Procedurální dekompozice)
- 

### Problém coplanárních ploch a integrity sítě
- coplární plocha = plochy oken a stěn ležící v přesně stejné rovině
- architektonické modely jsou náchylné k chybám Boolean operací díky nim
- často vede k selhání Exact solveru nebo k vytvoření dutých stěn
- osvědčeným řešením v parametrickém workflow je zavedení nepatrného přesahu u cutterů