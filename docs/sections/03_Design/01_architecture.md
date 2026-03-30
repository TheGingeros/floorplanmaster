# 3.1 Architektura systému

Tato sekce popisuje třívrstvou hybridní architekturu FloorPlanMaster. Je to klíč k pochopení, jak se data proudí mezi jednotlivými komponenty a jak se udržuje konzistence při interakci uživatele. FloorPlanMaster není jen běžné GUI - je to komplexní datový systém, který kombinuje tři odlišné reprezentace půdorysu:
- **Vrstva 1 (Topologie)**: čistý graf propojovacích bodů a stěn - to, co měří a propojuje
- **Vrstva 2 (Sémantika)**: graf místností a jejich vztahů - to, co architekt chápe a používá
- **Vrstva 3 (Synchronizace)**: Blender atributy a Geometry Nodes - to, co vidí na obrazovce

Tato architektura zajišťuje nedestruktivní úpravy půdorysu bez ztráty informací a aktualizaci geometrie v reálném čase. Komunikace vrstev je striktně jednosměrná: grafy v Pythonu vypočítají nová data a skrze pojmenované atributy (Named Attributes) je předají do Blender sítě, kde je Geometry Nodes okamžitě vykreslí.

Systém přímo aplikuje návrhový vzor MVC, kde Python grafy tvoří nezávislý Model, Blender UI a 3D pohled fungují jako View a modální operátory zachytávající kliknutí myší slouží jako Controller. Celý datový tok tak začíná uživatelským vstupem, který změní čistou topologii, což automaticky vyvolá přepočet sémantiky místností a končí instantním překreslením 3D geometrie, aniž by se tyto vrstvy do sebe funkčně zamotaly.

## [Vrstvy architektury](./01_architecture_layers.md)

- Vrstva 1: Topologický skelet (Strukturální graf)
- Vrstva 2: Sémantický graf místností (Duální graf)
- Vrstva 3: Most synchronizace (Pojmenované atributy)

## [Vzor MVC v Blenderu](./01_architecture_mvc.md)
- diagram MVC


## [Organizace modulů](./01_architecture_modules_struct.md)
- reprezentace organizace modulů


## [Tok dat: Základní operace](./01_architecture_data_flow.md)
- 1. Kreslení půdorysu (FP1 - Nástroj Tužka)
- 2. Úprava vlastností místnosti
- 3. Finalizace (FP4 - Převod na trvalou geometrii)

## Principy návrhu

1. **Oddělení zájmů**
   - Logika grafu (vrstvy 1, 2) nezávislá na Blenderu/GN (vrstva 3)
   - Operátory fungují jako tenké řadiče, ne složitá logika
   - Utility jsou bezstavové a opakovaně použitelné

2. **Nedestruktivní úpravy**
   - Identity místností/stěn přetrvávají přes změny parametrů
   - Undo/Redo podporováno přes systém operátorů Blenderu
   - Parametry lze upravovat nekonečně

3. **Zpětná vazba v reálném čase**
   - Náhled během kreslení (modul GPU)
   - Živé aktualizace při změně vlastností (GN drivers)
   - Responzivní UX i se složitými dispozicemi

4. **Modularita**
   - Každá vrstva se dá testovat nezávisle
   - Operace grafu nepotřebují Blenderův kontext
   - Snadné přidávání nových funkcí (okna, dveře, poznámky)

5. **Osvědčené postupy Blenderu**
   - Dodržujte konvence pojmenování Blenderu
   - Používejte modální operátory pro interaktivní nástroje
   - Využívejte Geometry Nodes pro nedestruktivní geometrii
   - Správná podpora undo/redo

## Technická rozhodnutí a zdůvodnění

| Rozhodnutí | Proč | Alternativa | Kompromis |
|----------|-----|-------------|-----------|
| Použití NetworkX pro grafy | Algoritmy planárních grafů, detekce cyklů, prostorová analýza | Vlastní třída grafu | Externí závislost, ale obrovský nárůst výkonu |
| Geometry Nodes pro 3D | Vykreslování v reálném čase, GPU akcelerované, nedestruktivní | Modifikátory Bmesh | GN obtížnější ladění, ale nedestruktivní |
| Most pojmenovaných atributů | Minimální režie synchronizace, nativní Blender | Ukládání v vlastních vlastnostech | Atributy bezproblémově integrují s GN drivers |
| Modální operátory | Hladká, responzivní interakce uživatele | Samostatné nástroje | Vyšší složitost správy stavů |
| Omezení planárního grafu | Validuje topologii půdorysu, umožňuje algoritmy | Povolit neplanární | Vyloučí architektonické nemožnosti |

## Aspekty výkonu

1. **Operace grafu**: Složitost O(n) přijatelná pro typické půdorysy (< 100 místností)
2. **Synchronizace atributů**: Serializuje pouze změněné uzly/hrany, aby se minimalizovaly aktualizace sítě
3. **Geometry Nodes**: Opětovné vyhodnocení GN je automatické; lze optimalizovat pomocí ukládání uzlů do mezipaměti
4. **Vykreslování náhledu**: Používejte lehké GPU čáry pro náhled, ne plnou geometrii
5. **Aktualizace pohledu**: Dávkové aktualizace, aby se zabránilo opětovnému vykreslení na událost

## Zabezpečení a validace

- **Validace topologie**: Zajistěte planární grafy, žádné vlastní průniky
- **Rozsahy parametrů**: Validujte tloušťku stěny, výšku v rozumných mezích
- **V/V souboru**: Validujte serializovaná data před načtením
- **Vstup uživatele**: Dezinfikujte jména místností, ID materiálů
