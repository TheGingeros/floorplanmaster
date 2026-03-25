# 5. Ukládání dat a správa metadat
- architektonický add-on vyžaduje integraci sématických informací, které definují prvky jako je stěna, okna, či místnost v kontextu fyzikálních a funkčních vlastností

## Systémy pro správu metadat a uživatelských parametrů
- blender nabízí dva hlavní mechanismy pro ukládání a spravování dat - vlastnosti ID(Custom properties) a definované vlastnosti RNA prostřednictvím modulu `bpy.props`
- pro architektonický addon je volba mezi těmito systémy kritická z hlediska výkonu, uživatelského rozhraní a dlouhodobé stability dat

### ID data-block
- označení pro základní kontejnery dat architektury Blenderu, které tvoří obsah .blend souborů
- jediné typy objektů, které mají schopnost být trvale uloženy na disk
- v python API jsou to všechno třídy, které dědí z `bpy.types.ID`, např:
    - Objekty - `bpy.types.Object`
    - Geometrie - `bpy.types.Mesh`, `bpy.types.Armature`, `bpy.types.Curve`
    - Scény - `bpy.types.Scene`
    - Materiály - `bpy.types.Material`
    - Kolekce - `bpy.types.Collection`
    - Další: světla, textury, obrázky, ...

### Vlastnosti ID - Custom Properties
- mechanismus pro připojování libovolných uživatelských dat k jakémukoliv datovému bloku typu ID bez nutnossti modifikace jádra systému
- tyto vlastnosti jsou interně reprezentovány strukturou C `IDProperty` - definována v DNA Blenderu
- každý datový blok obsahuje ukazatel na spojový seznam těchto struktur, přičemž kořenový prvek je obvykle typu `Group`, což v podstatě funguje jako slovník
- výhodou  je jejich flexibilita - mohou ukládat celá čísla, desetinná čísla, řetězce a pole, přičemž jsou plně animovatelné a integrovatelné do systému ovladačů (Drivers)
-  pro komplexní architektonické systémy vykazují určité nedostatky, zejména absenci striktní typové kontroly a omezené možnosti definice pokročilé logiky při změně hodnoty

### Modul `bpy.props`
- umožňuje definovat vlasnosti, které jsou registrovány přímo do systému RNA Blenderu
- tento přístup je nezbytný pro vytvoření robustního API addonu
- vlastnosti takto definované umožňují použití zpětných volání, jako jsou `update`, `get`, `set`, což je klíčové pro reaktivní architektonické prvky

### Porovnání

| Funkce | 	Vlastnosti ID (Custom Properties) | Modul bpy.props |
| :--- | :---  | :---  |
| **Datová struktura** | 	Dynamický spojový seznam | 	Staticky definovaná v Python třídách |
| **Typová kontrola** | Dynamická, slabá | Striktní, definovaná při registraci |
| **Uživatelské rozhraní** | Automatický panel "Custom Properties" | Vyžaduje definici v `bpy.types.Panel` |
| **Zpětná volání** | Nejsou přímo podporována | Plná podpora |
| **Perzistence** | Ukládají se přímo do .blend souboru | Ukládají se pouze, jsou-li vázány na ID |
| **Výkon** | Vyšší režie při vyhledávání v seznamu | Rychlejší přístup přes RNA rozhraní |

### PropertyGroups pro sématiku prostorů
- pro správu informací o prostorech jako je název, plocha, typ místnosti nebo výška je optimálním architektonickým vzorem `bpy.types.PropertyGroup`
- tento přístup umožňuje seskupit souvísející parametry do logického celku a ten následně připojit k datovému bloku pomocí `bpy.props.PointerProperty` nebo `bpy.props.CollectionProperty`

---

#### `bpy.props.PointerProperty` 
- vazba 1:1 - nasměruje jednu konkrétní instanci dat
- použití jako organizace - např. `stena.vlastnosti_okna.sirka` - `vlastnosti_okna` je PointerProrerty, která ukazuje na skupinu parametrů
použití jako odkaz na jiný datový blok - okno může mít PointerProperty, která ukazuje na objekt stěny, ve které je osazeno
#### `bpy.props.CollectionProperty`
- vazba 1:N - dynamické pole nebo seznam prvků typu `PropertyGroup`
- vlastnosti seznamu: `add()`, `remove()`, `clear()` a `move()`
- absence update callbacku - potřeba sledovat změny jednotlivých prvků uvnitř něj

---

- definice prostorových parametrů v rámci `PropertyGroup` je výhodou v organizaci kódu a prevenci konfliktů v názvosloví
- vhodné použít následující typy vlastností:
    - `StringProperty` např. pro název, důležité implementovat metodu `set()` pro validaci duplikátů
    - `EnumProperty` např pro typ místností
    - `FloatProperty` např. výška nebo plochoa, důležité implementovat `update` callback, který při změně automaticky přepočítá vertikální rozměry všech stěn nebo metodu `get` pro analyzaci geometrie podkladového meshe

## Vazby dat, Scéna, Objekt, Mesh
- rozhodnutí o tom, na jaké úrovni hierarchie Blenderu budou metadata uložena, má hluboké důsledky pro stabilitu doplňku, chování při operacích zpět (Undo) a správu instancí
### Úroveň scény - bpy.types.Scene
- vazba dat na této úrovni je vhodná pro globální parametry projektu, jako je geografická poloha, nastavení jednotek nebo globální materiálové standardy
- pro data specifická pro jednotlivé místnosti nebo prvky je však tato úroveň nevhodná
- hlavní problém je perzistence - pokud jsou metadata o konkrétním okně uložena v kolekci na úrovni scény, smazání tohoto objektu ve viewportu nezpůsobí automatické smazání metadat v kolekci, což vede k hromadění dat
### Úroveň objektu - bpy.types.Object
- objekt v Blenderu funguje jako kontejner, který nese informace o transformaci, viditelnosti a hierarchických vztazích
- uložení metadat na úroveň objektu je intuitivní, ale přináší komplikace v případě instancování
- vytvoření instance přes Alt + D vytvoří dva objekty, které sdílejí stejná geometrická data (Mesh), ale mají unikátní data na úrovni Object
- změna rozměru jednoho okna by se neprojevila u ostatních instancí, což popírá princip parametrického navrhování 
### Úroveň geometrie - bpy.types.Mesh
- považováno za nejvhodnější přístup pro architektonické prvky
- reprezentuje "definici typu" prvku
- pokud je `PropertyGroup` s parametry okna vázána na Mesh, všechny instance v projektu sdílející tento Mesh budou mít vždy identické parametry
- v souladu s principy BIM, kde rozlišujeme mezi Typem a Instancí
- data na této úrovni jsou lépe chráněna při komplexních operacích jako je export nebo linkování mezi soubory

### Porovnání
| Úroveň vazby | Architektonický význam | Chování při instancování | Stabilita při Undo/Redo |
| :--- | :--- | :--- | :--- |
| **Scene** | Globální projektová data | Metadata jsou sdílena celou scénou | Náchylné k desynchronizaci |
| **Object** | 	Unikátní vlastnosti instance | Každá instance má vlastní metadata | Velmi stabilní |
| **Mesh** | Definice typu prvku | 	Instance sdílejí metadata (změna u jednoho změní vše) | Velmi stabilní |
---
z toho vyplývá, že se použije hybridní model:
    - parametry definující tvar a funkci (rozměry, materiály, typ místnosti) ukládat na úroveň Mesh
    - identifikační data a specifické stavy (GUID prvku, stav revize konkrétního kusu) ukládat na úroveň Object
    - projektová data (název akce, stupeň dokumentace) ukládat na úroveň Scene

## Systém prostorových závislostí
- typický požadavkem je, aby se okno automaticky posunulo nebo přizpůsobilo při změně délky stěny atd

### Hiearchie Parent-Child a omezení (Constraints)
- parent-child je nejjednodušším způsobem, jak zajistit přenos transformací
- pro architektonické prvky je však standardní parenting často nedostatečný, protože přenáší transformaci celého objektu, ale nereaguje na změny vnitřní geometrie
- vhodnějším nástrojem je omezení `Child Of` v kombinaci s nastavením `Set Inverse`
    - umožňuje jemnější kontrolu nad tím, které kanály (lokace, rotace, měřítko) jsou ovlivněny rodičem
    - toto řešení neřeší situaci, kdy se stěna prodlouží v editačním režimu
### Systém ovladačů
- umožňují definovat hodnotu vlastnosti pomocí Python výrazu, který může referovat jiné vlastnosti v rámci scény
-  lze využít Drivers k propojení pozice okna s parametry stěny uloženými v `PropertyGroup`
- Například x-ová souřadnice okna může být definována jako: $$\text{pos\_x} = \text{wall.length} \times \text{window.relative\_position}$$
- výhodou je, že se vyhodnocují v rámci grafu závislostí Blenderu, což zajišťuje vysoký výkon a okamžitou odezvu v uživatelském rozhraní
- nevýhodou je nestabilita: při přejmenování objektů nebo změně struktury datablocků může dojít k přerušení vazeb, pokud není implementován robustní systém správy jmen
### Reaktivita pomocí Vertex Groups a Hook modifikátorů
- aby okno sledovalo pohyb určité části stěny, lze využít kombinaci skupin vrcholů (Vertex Groups) a modifikátoru `Hook`
1. na stěně se vytvoří skupina vrcholů v místě, kde je osazeno okno
2. na tuto skupinu se aplikuje modifikátor `Hook`, jehož řídicím objektem (Hook Object) je prázdný objekt (Empty), který slouží jako rodič okna
3. jakýkoli pohyb vrcholů stěny v editačním režimu se nyní přenáší na Empty objekt a tím i na samotné okno
- mnohem stabilnější než čistě skriptované řešení, protože využívá nativní výpočetní řetězec Blenderu, který je optimalizován pro reálný čas
### Automatizace pomocí aplikačních handlerů
- pro případy, které nelze vyřešit modifikátory nebo ovladači (např. komplexní topologické změny), je nutné nasadit systém aplikačních handlerů
- `bpy.app.handlers.depsgraph_update_post` - tento handler je vyvolán po každé aktualizaci scény
- v rámci handlerů lze provádět následující operace:
    - kontrola integrity vazeb (např. zda stále existuje stěna, ke které je okno přiřazeno)
    - dynamická regenerace meshe stěny při změně parametrů v `PropertyGroup` (např. přidání nového segmentu stěny)
    - synchronizace materiálů mezi souvisejícími prvky
- při používání handlerů je důležité dbát na efektivitu - výpočty by měly být prováděny pouze pro objekty označené příznakem "is_dirty", aby nedocházelo k degradaci výkonu při práci s rozsáhlými scénami

[Zdroje](./00_sources.md#ukládání-dat-a-správa-metadat)