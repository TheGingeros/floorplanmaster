# Reprezentace geometrie a topologie
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

### Porovnání bmesh a Geometry nodes pro generování 3D stěn

| Charakteristika | BMesh | Geometry Nodes |
| :--- | :--- | :--- |
| **Základní jednotka** | Entita (Vertex, Edge, Face) | Doména a Atributy |
| **Způsob práce** | Iterativní / Imperativní | Paralelní / Deklarativní |
| **Výkon** | Omezený interpretací Pythonu  | Vysoce optimalizované C++  |
| **Topologická flexibilita** | Absolutní (přímá změna struktury) | Omezená na definované uzly |
| **Vizuální odezva** | Po spuštění skriptu | Real-time v 3D viewportu  |

### Výkonnostní analýza a stabilita
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

## Datová reprezentace logické struktury sítě místností
- pro parametrické modelování není mesh dostatečnou reprezentací
- systém musí vědět, že prostor A je například obývací pokoj a sousedí s prostorem B, který je kuchyní
- existují hlavní dva přístupy k uložení této logiky - **topologické sítě(half-edge)** a **abstraktní grafy**

### Topologické sítě - half edge struktury
- v blenderu implementována jako BMesh
- ideální pro reprezentaci lokálních vztahů
- umožňuje rychle zjistit, která stěna je spojena s kterou nebo které plochy (místnosti) sdílejí konkrétní hranu (stěnu)
-  ideální pro čistě geometrické úkoly, jako je automatické generování soklových lišt nebo výpočet plochy podlah
- nevýhodou je však globální navigace - vyhledání cesty mezi dvěma vzdálenými místnostmi v rámci BMesh vyžaduje náročné procházení sítě

### Abstraktní grafy - grafová reprezentace
- pro reprezentaci logické struktury jako je budova jsou nejvhodnější **strukturní grafy:**
    - **Uzly/Vrcholy** reprezentují funkční prostory(místnosti) nebo wall-junctions (body setkání stěn)
    - **Hrany** reprezentují fyzické stěny nebo komunikační propojení(dveře, otvory)

### Datový model
- využití knihoven jako NetworkX v prostředí Blenderu umožňuje provádět prostorové analýzy, které jsou čistě geometrickými nástroji nedosažitelné
    - například použít algoritmus pro hledání nejkratší cesty (Dijkstra) pro ověření evakuačních tras nebo automaticky generovat sémantické popisky místností na základě jejich konektivity
- nejefektivnější systém za využití hybridního modelu
- tento model umožňuje například změnit typ oken v celé jižní straně budovy pouhou změnou jednoho parametru v grafu, což se okamžitě projeví v geometry nodes díky dynamickému čtění atributů
#### 1. **Abstraktní vrstva(NetworkX):** 
- uchovává logické vazby, metadata o místnostech (plocha, určení) a hierarchii podlaží nezávisle na konkrétních souřadnicích
- **Node-Relation Graph (NRG):** 
    - v tomto grafu reprezentují uzly funkční prostory (místnosti) a hrany definují jejich sousednost nebo fyzické propojení (dveře, otvory)
- **Strukturální grafy:** 
    - alternativním přístupem je graf, kde uzly jsou stěnové spoje (wall-junctions) a hrany jsou jednotlivé segmenty stěn
    - vhodnější pro generování vektorových půdorysů
- **Hierarchická dekompozice:** 
    - model využívá vztahy inkluze, které organizují data do stromové struktury: Budova → Podlaží → Místnost → Funkční zóna
#### 2. **Geometrická vrstva (Geometry Nodes + Attributes):**
- přijímá data z grafu a realizuje je v 3D prostoru
- informace z grafu jsou do geometrie přenášeny skrze pojmenované atributy uložené na vrcholech nebo plochách
- **Boundary Representation (B-Rep):** 
    - definuje tělesa pomocí jejich hranic (vrcholy, hrany, plochy)
    - na rozdíl od pouhého seznamu trojúhelníků uchovává B-Rep explicitní informace o tom, jak se plochy setkávají v hranách
- **CW-komplexy vs. Standardní B-Rep:** 
    - v klasickém modelování jsou sousední stěny často dvěma separátními objekty s duplicitními plochami