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