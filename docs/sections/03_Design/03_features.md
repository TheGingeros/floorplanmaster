# 3.3 Specifikace funkcí

Tento dokument obsahuje podrobné specifikace všech sedmi hlavních funkcí (FP1-FP7) - co dělají, jak fungují, jaké jsou jejich požadavky a implementační poznámky. Každá funkce je rozdělena na must-have a should-have prvky.

Architekturu a data modely máte. Teď přichází otázka: "Jaké jsou vlastně funkce, které s ním budeme dělat?" To je v tomto dokumentu.

**FP1: Nástroj Tužka** je srdce addonu - modální operátor, kde klikáte body v 3D pohledu a vytváříte stěny. Musíte pochopit stavový automat, jak se kreslí náhled, jak funguje přichycování a jak se stěny přidávají do grafu.

**FP2-FP3: Správa** - Jak editujete parametry stěn (tloušťka, výška), jak spravujete místnosti (přejmenování, typ), jak procházíte graf (sousedství, cesty, izolované místnosti).

**FP4: Finalizace** - Jakmile máte hotový půdorys v parametrickém formě, musíte ho "upéct" na trvalou geometrii. Dvě metody: Geometry Nodes nebo BMesh. Tři režimy organizace: sloučeno, odděleno, rozděleno.

**FP5-FP7: Rozšíření** - Kontextové nabídky, 3D manipulátory (gizmo), automatické kótování (délky, plochy, výšky).

V tomto dokumentu se dozvíte:
- Detailní specifikaci všech sedmi funkcí (FP1-FP7)
- Stavový automat pro Tužku (musíte to pochopit!)
- Must-have vs should-have prvky (co je kritické, co je bonus)
- Nefunkční požadavky (výkon, nedestruktivnost, integrace)
- Tabulky event zpracování a parametrů
- Implementační poznámky a gotchas

Když chcete vědět "Co přesně by měl addon dělat?", odpověď je tady.

## FP1: Nástroj Tužka - Interaktivní kreslení půdorysů

### Přehled funkce

Modální operátor, který umožňuje architektům intuitivně kreslit půdorysy klikáním bodů v top-view a vytváří stěny a propojovací body interaktivně s viditelnou zpětnou vazbou v reálném čase.

### Funkční požadavky

#### Must-Have (Jádro FP1)

1. **Modální operátor se stavovým automatem**
   - Operátor vstupí do modálního stavu po aktivaci
   - Následuje přechody stavů: START → DRAWING → CONFIRMING → RECORDING → finished/cancelled
   - Reaguje na pohyb myši, kliknutí a vstup z klávesnice

2. **Umístění bodů**
   - Kliknutí umístí propojovací bod v 3D prostoru
   - Souřadnice jsou zachyceny v souřadnicích světa
   - Validace: Žádné duplicitní propojovací body v toleranci

3. **Vytváření stěn**
   - Po prvním bodu: Zobrazit náhledovou linii sledující myš
   - Kliknutí na druhý bod: Vytvoří stěnu mezi propojovacími body
   - Stěna je přidána do strukturálního grafu vrstvy 1
   - Automatická detekce cyklů aktualizuje vrstvu 2

4. **Základní přichycování** (Should-Have zvýšeno na Must-Have)
   - **Přichycování osy**: Přichytit k osám X, Y v případě, že je kurzor v 10 pixelech
   - **Přichycování bodu**: Přichytit na existující propojovací body v rámci 15 pixelů
   - Vizuální indikátor (kruh) když je přichycování aktivní
   - Uživatel může přichycování přepnout klávesou modifikátoru (Shift)

5. **Vykreslování náhledu**
   - Zobrazit ducha/náhledovou stěnu před potvrzením
   - Náhled v reálném čase při pohybu myši
   - Barva náhledu odlišná od potvrzených stěn
   - Používá modul `gpu` pro výkon

6. **Potvrzení a zrušení**
   - Stiskněte **Enter/LMB**: Potvrdit bod
   - Stiskněte **Esc/RMB**: Zrušit aktuální akci
   - Stiskněte **Z** pak Enter: Vrátit poslední bod
   - Přechody stavů se zpracovávají bez chyb

7. **Vizuální zpětná vazba**
   - Zobrazování souřadnic v reálném čase (HUD overlay)
   - Zobrazení délky stěny během kreslení
   - Zobrazení úhlu (stupně)
   - Stavové zprávy v levém horním rohu pohledu

### Should-Have (Schopnosti)

1. **Vstup tloušťky stěny**
   - Po druhém bodu: Umožnit uživateli zadržet hodnotu tloušťky
   - Stiskněte Enter pro potvrzení, ESC pro výchozí
   - Zobrazena hodnota v aktuálním systému jednotek

2. **Vstup výšky stěny**
   - Podobně jako tloušťka, umožnit přizpůsobení výšky
   - Výchozí 3.0m, uživatel může přepsat

3. **Nepřetržité kreslení**
   - Po potvrzení stěny je připraven automaticky pro další stěnu
   - Předchozí koncový bod se stane novým počátečním bodem
   - Uživatel může stisknout ESC pro ukončení režimu kreslení

4. **Přichycování úhlu**
   - Možnost přichycovat k 45°, 90°, 135°, atd.
   - Přepnout klávesou **A**
   - Vizuální indikátor úhlu při přichycování

5. **Přichycování mřížky**
   - Volitelná mřížka (0.1m, 0.5m, 1.0m)
   - Přepnout klávesou **G**
   - Kurzor přichytit na nejbližší bod mřížky

6. **Vrácení během kreslení**
   - Stiskněte **Z** pro vrácení poslední bodu v aktuální relaci kreslení
   - Opakovat s **Y**
   - Omezeno na aktuální relaci (do Esc/Enter)

### Diagram stavového automatu

```
        ┌─────────────┐
        │   START     │
        └──────┬──────┘
               │
         (Uživatel klikne)
               │
               ▼
        ┌─────────────┐
        │   DRAWING   │◄────┐
        │             │     │
        │ (show prev) │     │ (pohyb myši)
        └──────┬──────┘     │
               │            │
        (klik/Enter)    ┌────┘
               │        │
               ▼        │
        ┌─────────────┐ │
        │ CONFIRMING  ├─┘
        │             │
        │ (add wall)  │
        └──────┬──────┘
               │
        (Opakovat nebo Esc)
               │
               ▼
        ┌─────────────┐
        │  FINISHED   │
        │ (cleanup)   │
        └─────────────┘
```

### Zpracování událostí

| Událost | Stav | Akce | Příští stav |
|---------|------|--------|-----------|
| LMB Kliknutí | START | Přidat propojovací bod | DRAWING |
| Pohyb myši | DRAWING | Aktualizovat náhled | DRAWING |
| LMB Kliknutí | DRAWING | Přidat stěnu, detekovat cykly | CONFIRMING |
| Zadejte číslo | CONFIRMING | Nastavit tloušťku stěny | CONFIRMING |
| Enter | CONFIRMING | Potvrdit stěnu | DRAWING |
| Esc (1x) | DRAWING | Odebrat poslední bod | START |
| Esc (2x) | START | Ukončit operátor | FINISHED |
| Z | Libovolný | Vrátit bod | Předchozí |
| Y | Libovolný | Znovu vytvořit bod | Příští |
| Scroll | Libovolný | Zoom (PASS_THROUGH) | Aktuální |
| Střední myš | Libovolný | Pan (PASS_THROUGH) | Aktuální |

### Poznámky k implementaci

- **Modální handler**: Zaregistrovat s `context.window_manager.modal_handler_add(self)`
- **Návratové hodnoty**:
  - `RUNNING_MODAL`: Pokračovat v zpracování vstupů
  - `PASS_THROUGH`: Umožnit interakci pohledu (zoom, pan)
  - `FINISHED`: Operace úspěšná, vytvořit krok vrácení
  - `CANCELLED`: Přerušit operaci
- **Vykreslování GPU**: Použít `gpu.types.GPUBatch` a shadery pro náhled
- **Výkon**: Ukládat geometrické výpočty do mezipaměti, aktualizovat pouze na významný pohyb

---

## FP2: Parametrické generování a úprava

### Přehled funkce

Umožnit uživatelům upravovat parametry stěn a místností (tloušťka, výška, materiály, barvy) nedestruktivně s aktualizacemi geometrie v reálném čase.

### Funkční požadavky

1. **Úprava parametrů stěny**
   - Tloušťka: 0.05m - 1.0m
   - Výška: 1.0m - 10.0m
   - Materiál/Barva: Výběr uživatelem
   - Posun: Pro asymetrické stěny
   - Upravovat přes panel vlastností nebo 3D manipulátory

2. **Úprava parametrů místnosti**
   - Jméno, typ, materiál podlahy/stropu
   - Barva podlahy/stěny/stropu
   - Upravovat přes panel vlastností nebo modální operátor

3. **Nedestruktivní aktualizace**
   - Upravit parametry → Pouze atributy se změní
   - ID místností zůstávají nezměněna
   - Plná podpora vrácení/opakování

4. **Zpětná vazba v reálném čase**
   - Geometry Nodes drivers čtou atributy
   - Pohled se aktualizuje okamžitě
   - Není potřeba ruční obnovení

### Přístup k implementaci

- Ukládat parametry ve vrstvě 1 (stěny) a vrstvě 2 (místnosti)
- Aktualizovat pojmenované atributy při změně parametru
- Geometry Nodes GN driver spustí aktualizaci

---

## FP3: Správa prostoru a metadat

### Přehled funkce

Poskytovat pokročilé analýzy prostoru a možnosti organizace místností.

### Funkční požadavky

1. **Správa místností**
   - Vytváření, přejmenování, mazání místností
   - Přiřazování typu místnosti (obytná, komerční, atd.)
   - Sledování hierarchie místností (zóny, podlaží)

2. **Analýza konektivity**
   - Dotazování sousedních místností
   - Hledání evakuačních cest (algoritmus Dijkstry)
   - Identifikace izolovaných prostorů
   - Generování diagramů cirkulace

3. **Ukládání metadat**
   - Vlastní vlastnosti na místnost (obsazenost, požární třída)
   - Metadata stěny (nosná kapacita, akustický rating)
   - Anotace propojovacího bodu

4. **Export/Import**
   - Uložit půdorys do formátu JSON
   - Načíst z JSON (zachuje ID)
   - Kompatibilní s jinými nástroji

### Technické detaily

- Procházení grafu Room Graph pro konektivitu
- NetworkX algoritmy nejkratší cesty
- Serializace grafů do JSON

---

## FP4: Nástroj finalizace

### Přehled funkce

Modální operátor pro finalizaci půdorysů - převod parametrických dat na trvalou 3D geometrii.

### Funkční požadavky

1. **Pečení**
   - Možnost 1: Pečení Geometry Nodes do sítě (Blender 3.2+)
   - Možnost 2: Přímé generování geometrie bmesh

2. **Organizace objektů**
   - Volba: Vytvoření samostatného objektu na místnost
   - Volba: Vytvoření objektu stěny, podlahy, stropu
   - Volba: Jednolitý sloučený objekt

3. **Přiřazení materiálů**
   - Přiřazení materiálů stěnám, podlahám, stropům
   - Vytvoření uzlů materiálu Blenderu na základě parametrů

4. **Čištění**
   - Odebrání pojmenovaných atributů (volitelné)
   - Odebrání Geometry Nodes (volitelné)
   - Zachování grafů vrstvy 1/2 (volitelné)

### Stavový automat

```
START
  ↓
OPTIONS (zobrazit dialog)
  ├─ Metoda pečení (GN nebo bmesh)
  ├─ Organizace objektu (sloučeno/odděleno)
  ├─ Přiřazení materiálu (ano/ne)
  ↓
BAKING (provést finalizaci)
  ↓
FINISHED (vygenerovat krok vrácení)
```

---

## FP5: Kontextová nabídka

### Přehled funkce

Nabídka kliknutí pravým tlačítkem pro rychlé operace s místnostmi/stěnami.

### Položky nabídky

**Na místnosti (kliknutí pravým tlačítkem na plochu místnosti)**:
- Změnit typ místnosti
- Upravit jméno místnosti
- Upravit materiál podlahy/stropu
- Smazat místnost
- Duplikovat místnost
- Exportovat místnost do samostatného objektu

**Na stěně (kliknutí pravým tlačítkem na hranu stěny)**:
- Upravit tloušťku stěny
- Upravit výšku stěny
- Upravit materiál
- Přidat okno
- Přidat dveře
- Smazat stěnu
- Rozdělit stěnu (přidat propojovací bod)

**V prázdném prostoru**:
- Spustit nový půdorys
- Načíst existující plán
- Zobrazit/skrýt mřížku
- Exportovat do souboru

---

## FP6: Interaktivní 3D manipulátory (Gizma)

### Přehled funkce

Operátory gizma pro přímou manipulaci stěn a místností v 3D.

### Typy manipulátorů

1. **Manipulátor tloušťky stěny**
   - Objevit se na stěně, když je vybrána
   - Táhnout kolmo na osu stěny
   - Aktualizovat tloušťku v reálném čase

2. **Manipulátor výšky stěny**
   - Svislá šipka na stěně
   - Táhnout nahoru/dolů pro změnu výšky

3. **Manipulátor pohybu propojovacího bodu**
   - Objevit se na propojovacím bodu, když je vybrán
   - Táhnout v rovině XY
   - Aktualizovat všechny připojené stěny

4. **Manipulátor velikosti místnosti**
   - Čtyři rohové rukojeti na obvodu místnosti
   - Táhnout pro změnu velikosti místnosti
   - Upravit připojené stěny

### Implementace

- Použít `bpy.types.Gizmo` a `bpy.types.GizmoGroup`
- Vlastní shadery pro vizuální reprezentaci
- Zpětná volání pro aktualizaci grafu a atributů

---

## FP7: Automatické kótování

### Přehled funkce

Automatické zobrazování rozměrů, ploch a měření.

### Prvky zobrazení

1. **Označení stěn**
   - Délka stěny zobrazena na středu stěny
   - Aplikován převod jednotek
   - Přepínatelná viditelnost

2. **Označení místností**
   - Plocha místnosti zobrazena ve středu místnosti
   - Jméno místnosti nad plochou
   - Přepínatelná viditelnost

3. **Anotace výšky**
   - Výška stěny označena
   - Anotace úrovně

4. **Označení obvodu**
   - Volitelné: Zobrazit obvod místnosti
   - Volitelné: Zobrazit poměr stran

### Implementace

- Použít Geometry Nodes primitiv textu nebo
- Objekty textu Blenderu pozicované dynamicky
- Aktualizace při změně parametru

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
