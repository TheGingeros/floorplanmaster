# 3.3 Specifikace funkcí
Zatímco předchozí kapitoly definovaly jádro celého systému (třívrstvou architekturu a exaktní datové modely), tato sekce popisuje samotné ovládací prvky. Definuje kompletní sadu nástrojů a funkcí, prostřednictvím kterých uživatel s datovým jádrem interaguje. Architektura MVC je zde převedena do praxe: modální operátory, gizma a panely představují Controllers, které přijímají uživatelské vstupy a bezpečně je překládají do příkazů pro manipulaci s grafy.

Následující specifikace rozděluje schopnosti addonu do sedmi logických bloků (FP1 až FP7) podle nadefinovaných funkčních požadavků v kapitole analýzy cílových skupin. Jádremu je nástroj Tužka (FP1), který transformuje složité zadávání souřadnic do intuitivního interaktivního kreslení. Další funkce pak pokrývají celý životní cyklus architektonického návrhu – od parametrických úprav a správy sémantických metadat, přes vizuální pomůcky (automatické kótování a 3D manipulátory), až po nevratnou finalizaci (zapečení) matematického modelu do statické 3D sítě. 

Každá funkce je pro přehlednost rozdělena na kritické požadavky (Must-Have), které tvoří minimální životaschopný produkt (MVP), a rozšiřující schopnosti (Should-Have), které zvyšují efektivitu a uživatelský komfort.

## [FP1: Nástroj Tužka - Interaktivní kreslení půdorysů](./03_features_fp1.md)
- Must-Have - součástí MVP
- Should-Have (Schopnosti)
- Diagram stavového automatu
- Zpracování událostí
- Poznámky k implementaci

## [FP2: Parametrické generování a úprava](./03_features_fp2.md)
- Must-Have
- Should-Have

## [FP3: Správa prostoru a metadat](./03_features_fp3.md)
- Must-Have
- Should-Have

## FP4: Nástroj finalizace
Zatímco všechny předchozí nástroje udržují půdorys v dynamickém, matematicky řízeném stavu, FP4 slouží k jednosměrnému „zapečení“ (Baking) této parametrické struktury do běžné, fixní 3D geometrie. Tento modální operátor je klíčový pro fázi, kdy architekt dokončí návrh a potřebuje model předat k dalšímu zpracování (např. ručnímu modelování detailů, exportu do herního enginu nebo renderovací pipeline).

### Funkční požadavky

1. **Pečení hierarchie budovy**
   - Převod Geometry Nodes stromů všech podlaží na trvalou mesh (síť).
   - Dvě výpočetní metody: Nativní aplikace modifikátoru Geometry Nodes (Blender 3.2+) nebo přímé vygenerování bmesh z pythonovských grafů.

2. **Organizace objektů**
   - **Sloučený režim:** Celá budova (všechna patra) se slije do jednoho objektu.
   - **Režim pater:** Každé podlaží vytvoří vlastní oddělený objekt (ideální pro architekturu).
   - **Režim místností:** Samostatný objekt pro každou místnost (ideální pro interiérový design a herní enginy).
   - **Režim elementů:** Rozdělení na objekty stěn, podlah a stropů.

3. **Přiřazení materiálů**
   - Automatické vygenerování a přiřazení Blender uzlů materiálů (Shader Nodes) na základě metadat z Vrstvy 2 (barva podlahy, typ stěny).

4. **Čištění (Cleanup)**
   - Volitelné odstranění nepotřebných pojmenovaných atributů z finální sítě pro úsporu dat.
   - Volitelné odstranění původních řídících objektů a grafů (Vrstva 1 a 2).

### Stavový automat operátoru

```
START
  ↓
OPTIONS (zobrazit dialogové okno)
  ├─ Rozsah pečení (Aktivní patro / Celá budova)
  ├─ Metoda pečení (GN nebo bmesh)
  ├─ Organizace objektu (sloučeno/patra/místnosti)
  ├─ Přiřazení materiálu (ano/ne)
  ↓
BAKING (provést nevratnou finalizaci sítě)
  ↓
FINISHED (vygenerovat krok vrácení - Undo Step)
```

---

## FP5: Kontextová nabídka

Tento modul poskytuje rychlý, kontextově závislý přístup k nejčastějším operacím (vyvolaný typicky pravým tlačítkem myši). Aby nabídka fungovala správně ve vícepodlažním prostředí, provádí interní Raycast (vržení paprsku) do 3D scény, detekuje, na jaký element uživatel klikl, a ověřuje, zda tento element patří do aktuálně aktivního podlaží. Pokud uživatel klikne na element z neaktivního patra, nabídka mu primárně nabídne přepnutí kontextu.

### Položky nabídky

**Na místnosti (kliknutí pravým tlačítkem na plochu místnosti aktivního patra)**:
- Změnit typ místnosti
- Upravit jméno místnosti
- Upravit materiál podlahy/stropu
- Vytvořit schodiště (generuje logickou vazbu na podlaží nad/pod aktuálním)
- Smazat místnost
- Duplikovat místnost (v rámci patra)
- Exportovat místnost do samostatného objektu

**Na stěně (kliknutí pravým tlačítkem na hranu stěny aktivního patra)**:
- Upravit tloušťku stěny
- Upravit výšku stěny
- Upravit materiál
- Přidat okno / Přidat dveře
- Rozdělit stěnu (vloží nový propojovací bod a rozdělí hranu ve Vrstvě 1)
- Smazat stěnu

**V prázdném prostoru (nebo na elementu neaktivního patra)**:
- Přepnout do tohoto podlaží (pokud bylo kliknuto na jiné patro)
- Přidat nové podlaží
- Spustit nový půdorys / Načíst existující plán
- Zobrazit/skrýt mřížku
- Exportovat projekt do souboru

---

## FP6: Interaktivní 3D manipulátory (Gizma)

Gizma představují vizuální rukojeti přímo ve 3D viewportu, které umožňují intuitivní tahání (drag & drop) za stěny a rohy bez nutnosti zadávat čísla do panelů. Z architektonického hlediska jde o nejrizikovější funkci – moduly manipulátorů musí obsahovat tvrdé geometrické zámky (constraints), aby uživatel taháním myší neporušil striktní 2D planaritu strukturálního grafu aktivního patra.

### Typy manipulátorů a jejich bezpečnostní zámky

1. **Manipulátor tloušťky stěny**
   - Zobrazí se na stěně při výběru.
   - Umožňuje tahání výhradně v rovině kolmé na osu stěny (XY).
   - Upravuje atribut `wall_thickness` v reálném čase, topologie (Vrstva 1) zůstává nezměněna.

2. **Manipulátor výšky stěny**
   - Svislá šipka umístěná na stěně.
   - Umožňuje tahání výhradně nahoru a dolů (osa Z).
   - **Kritické:** Tento manipulátor nemění fyzickou Z-souřadnici uzlů ve Vrstvě 1 (které neexistují). Pouze přepisuje číselný atribut `wall_height`, který následně vytáhnou Geometry Nodes.

3. **Manipulátor pohybu propojovacího bodu (Junction Move)**
   - Zobrazí se na vybraném rohu/spoji.
   - **Kritické:** Pohyb je striktně uzamčen do 2D roviny (XY) aktuálního patra. Pokus o vertikální tahání je ignorován.
   - Během posunu se dynamicky přepočítávají délky a úhly všech připojených stěn.

4. **Manipulátor velikosti místnosti**
   - Čtyři rohové rukojeti na obrysu místnosti (bounding box).
   - Slouží pro plošné zvětšení/zmenšení proporcí místnosti.
   - Interně aplikuje 2D transformační matici na všechny ohraničující uzly ve Vrstvě 1.

### Implementace

- Využívá vestavěné API `bpy.types.Gizmo` a `bpy.types.GizmoGroup`.
- Zpětná volání (callbacks) manipulátorů musí po každém pohybu spouštět proces popsaný v čase synchronizace (aktualizace Python grafů → obnova BMesh sítě → překreslení Geometry Nodes).

---

## FP7: Automatické kótování

Tato funkce zajišťuje dynamické zobrazování architektonických rozměrů, ploch a informací (HUD) přímo do 3D scény. Kótování není součástí fyzické geometrie (stěn), ale je to překryvná informační vrstva. Systém musí reflektovat hierarchii budovy – kóty se nesmí hromadit v nulové výšce, ale musí být prostorově posunuty o hodnotu `elevation` aktuálně aktivního patra.

### Prvky zobrazení

1. **Označení stěn (Délky)**
   - Vypočítaná euklidovská vzdálenost mezi dvěma 2D uzly ve Vrstvě 1.
   - Zobrazeno vždy uprostřed dané stěny s aplikovaným převodem jednotek (metrický/imperiální systém).
   - Viditelnost lze globálně přepínat.

2. **Označení místností**
   - Přesná plocha místnosti (m²) zobrazená v jejím těžišti (centroidu).
   - Uživatelský název místnosti dynamicky umístěný nad plošnou kótou.

3. **Anotace výšky a podlaží**
   - Globální kóta ukazující absolutní výšku aktuálního patra (`elevation`).
   - Lokální kóty pro stěny s nestandardní výškou.

### Implementace

- V závislosti na výkonnostních preferencích se realizuje buď přes čisté **Geometry Nodes primitiva (String to Curves)** zapsané přímo v instanci patra, nebo přes nízkoúrovňový **modul GPU (`gpu` a `blf`)** pro kreslení 2D textu překrývajícího 3D pohled (zajišťuje, že texty jsou vždy čitelné a neprotínají je stěny).
- Systém automaticky reaguje na změnu parametru v reálném čase.
---

## Nefunkční požadavky (NP)

### NP1: Architektura a technologie

- **Integrace NetworkX**: Bezproblémová integrace v prostředí Blender Python
- **Geometry Nodes**: Automatické nastavení stromu uzlů
- **Konvence pojmenování**: Dodržení standardů Blenderu/Pythonu
- **Organizace kódu**: Modulární, testovatelné komponenty
- **Dokumentace**: Docstring, API docs, uživatelský průvodce

### NP2: Nedestruktivnost a výkon

- **Nedestruktivní úpravy**: ID místností zůstávají perzistentní
- **Výkon**: Zpracování 50+ místností bez prodlení
- **Undo/Redo**: Plná podpora s efektivním ukládáním stavu
- **Aktualizace v reálném čase**: < 100ms doba odezvy
- **Paměť**: Efektivní ukládání grafu

### NP3: Použitelnost a UX

- **Intuitivní kreslení**: Kreslení jako tužkou, bez učící křivky
- **Vizuální zpětná vazba**: Náhled v reálném čase, stavové zprávy
- **Zpracování chyb**: Jasné chybové zprávy, návrhy obnovy
- **Přístupnost**: Klávesové zkratky, nápověda tlačítka
- **Konzistence**: Dodržení konvencí UI Blenderu
