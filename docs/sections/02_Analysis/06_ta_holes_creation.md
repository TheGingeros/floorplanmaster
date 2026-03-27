# Tvorba otvorů pro okna a dveře
- v parametrickém modelování je kritické, aby otvory pro okna a dveře byly plně dynamické
-pokud dojde k posunu stěny, okno se musí posunout s ní a otvor se musí automaticky regenerovat bez nutnosti manuálního zásahu
- lze rešit pomocí tří metod:
## Boolean operace spravované přes Python API
- tento přístup využívá standardní modifikátorový stack Blenderu, kde Python skript dynamicky vytváří a konfiguruje objekty typu `cutter` a přiřazuje je ke stěně
- každý modifikátor v Blenderu představuje separátní výpočetní krok v rámci objektu
- při použití `Exact` solveru se využívají homogenní celočíselné souřadnice k zajištění absolutní přesnosti, což eliminuje numerické chyby u coplanárních ploch, ale je to náročné na paměť
- hlavní nevýhodou při správě přes API je, že každá Booleovská operace mezi dvěma objekty musí brát v úvahu jejich světové transformační matice
- pokud souřadnice po transformaci nejsou binárně identické (např. kvůli zaokrouhlovací chybě floatů), `Exact` solver může selhat při detekci společných ploch, což vede k artefaktům
-režie na správu stacku s desítkami modifikátorů je extrémní
-Blender musí při každé změně reevaluovat celý řetězec, což v Pythonu nelze efektivně paralelizovat
## Mesh Boolean v Geometry Nodes
- tato metoda nahrazuje objektový stack jedním uzlovým stromem, kde operace probíhají nad proudy geometrických dat
- na rozdíl od modifikátorů, které pracují v párech (Object A - Object B), uzel Mesh Boolean v Geometry Nodes dokáže zpracovat celé kolekce instancí oken jako jeden sloučený vstup - to dramaticky snižuje počet reevaluací
- uzel Mesh Boolean považuje vše zapojené do vstupu Mesh 1 za jediné těleso
- pokud se tedy dvě stěny uvnitř tohoto vstupu překrývají nebo dotýkají, solver se snaží vyřešit i tyto vnitřní průsečíky, což může způsobit mizení částí geometrie nebo vznik dutých výsledků
## [Metody bez Booleovských operací (Procedurální dekompozice)](./06_ta_non_boolean_methods.md)
## Srovnání metod

| Parametr | API Modifikátory | GN Mesh Boolean | Curve Trimming |
| :--- | :--- | :--- | :--- |
| **Výpočetní složitost** | $O(n \times m)$ | $O(m \times \log m)$ | $O(n)$ |
| **Numerická stabilita** | Nízká (float drift mezi objekty) | Střední (závislá na Gapu) | Absolutní (čistá topologie) |
| **Topologický výstup** | Často n-gony s artefakty | n-gony, vyžaduje Merge by Distance | Perfektní quads/tris |
| **Flexibilita** | Vysoká (libovolné tvary) | Vysoká | Omezená na vertikální otvory |

- hint: doporučuje se kombinace curve trimming pro základní stěnové otvory a GN mesh boolean pro atypické otvory, které nelze vyjádřit 2d profilem
## Problém coplanárních ploch a integrity sítě
- coplární plocha = plochy oken a stěn ležící v přesně stejné rovině
- architektonické modely jsou náchylné k chybám Boolean operací díky nim
- často vede k selhání Exact solveru nebo k vytvoření dutých stěn
- osvědčeným řešením v parametrickém workflow je zavedení nepatrného přesahu u cutterů

[Zdroje](../../files/00_sources.md#tvorba-otvorů-pro-okna-a-dveře---nedestruktivní-workflow)