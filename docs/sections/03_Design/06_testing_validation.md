# 3.6 Testování a validace návrhu

Předchozí kapitoly 3.1–3.5 definovaly MVP scope, architekturu, datový model, funkce a uživatelské rozhraní. Před zahájením implementace je nezbytné provést důkladnou kontrolu celého návrhu — ověřit, že architektura, datové toky a funkce společně spolehlivě pokrývají zadání z MVP scope (kapitola 3.1) a neobsahují logické trhliny. Tato kapitola plní roli „lékařské prohlídky" návrhu prostřednictvím kontrolních seznamů, teoretických průchodů scénáři a analýzy okrajových případů.

## Pokrytí funkčních požadavků

Následující kontrolní seznam ověřuje, že každý must-have prvek MVP (kapitola 3.1) je plně pokryt návrhem funkce (kapitola 3.4), datovým modelem (kapitola 3.3) a architekturou (kapitola 3.2).

| Požadavek | Must-have prvek | Navrhující sekce | Datový model | Vrstva |
| :--- | :--- | :--- | :--- | :--- |
| FP1 | Modální operátor pro kreslení bodů | FP1 — stavový automat | Junction, Wall (L1) | Controller → L1 → L2 → L3 |
| FP1 | Snap na existující junction | FP1 — snapping | Junction.position (L1) | Controller |
| FP1 | Zápis do L1 až po potvrzení | FP1 — interakce s modelem | — | Controller → L1 |
| FP2 | Dynamická parametrická stěna | FP2 — parametry stěny | Wall.thickness/height (L1) | L1 → L3 → GN |
| FP2 | Vložení pravoúhlé místnosti | FP2 — vložení místnosti | Junction × 4, Wall × 4 (L1) | Controller → L1 → L2 → L3 |
| FP2 | Vazba otvoru na stěnu | FP2 — vazba otvorů | Wall.openings (L1) | L1 → L3 → GN |
| FP3 | Automatická detekce místností | FP3 — detekce cyklů | Room (L2) z cyklu (L1) | L1 → L2 |
| FP3 | Zobrazení plochy místnosti | FP3 — prostorová data | Room.area (L2) | L2 → L3 → GN |
| FP4 | Aplikace GN modifikátoru | FP4 — stavový automat | L3 → statická mesh | View |
| FP5 | Kontextová nabídka s akcemi | FP5 — raycast + akce | L3 raycast → L1/L2 | Controller |
| FP6 | Gizmo pro tloušťku/výšku/posun | FP6 — typy manipulátorů | Wall.thickness/height, Junction.position | Controller → L1 → L3 |
| FP7 | GPU overlay kóty | FP7 — datový pipeline | L1 délky, L2 area + centroid | View (BLF) |

Každý must-have prvek je pokryt jednou návrhovou sekcí, má definovaný datový model a průchoditelný tok dat napříč vrstvami.

## Pokrytí nefunkčních požadavků

| Požadavek | Jak je pokryt návrhem |
| :--- | :--- |
| NP1 — Architektura a technologie | Geometry Nodes jako výpočetní jádro (L3 → GN); Python jako manažer (L1, L2); oddělení vizuální a aplikační logiky (třívrstvá architektura, kapitola 3.2); NetworkX jako deklarovaná wheel závislost |
| NP2 — Výkon a nedestruktivnost | Jednosměrný tok dat bez cyklických přepočtů; změna atributu nevyvolá detekci cyklů (pouze L3 fáze 2); dvoufázová synchronizace minimalizuje overhead; Undo přes Blender snapshot |
| NP3 — Použitelnost a UX | N-panel se standardními UILayout komponentami; klávesové zkratky z Blender/AutoCAD konvencí; GPU overlay s barevnou sémantikou nativních nástrojů; validační chyby hlášeny pop-overem |

## Průchod scénáři použití (walkthroughs)

Teoretický průchod každým scénářem z analýzy (kapitola 2.4) ověřuje, že navržená architektura a funkce společně pokrývají celý uživatelský workflow.

**UC 1.1 — Hmotová studie na základě stavebního programu**

1. Uživatel otevře N-panel → sekce Nástroje → „Vložit místnost" (kapitola 3.5)
2. Zadá plochu 30 m² a poměr stran → addon dopočítá šířku a hloubku (FP2 — vložení místnosti)
3. Po potvrzení: `L1.add_junction()` × 4 + `L1.add_wall()` × 4 → detekce cyklů → L2 Room s `area = 30.0` → L3 sync → GN reevaluace (tok dat, kapitola 3.2)
4. Uživatel zapne kótování klávesou T → FP7 draw_handler čte `room_area` z L2 a zobrazí štítek v centroidu (FP7)

Pokrytí: FP2 (must-have), FP3 (must-have), FP7 (must-have). Celý workflow průchozí.

**UC 1.2 — Zkoušení prostorových variant a posun stěn**

1. Uživatel vybere stěnu ve viewportu → N-panel zobrazí parametry (kapitola 3.5, Auto-manipulate on select)
2. Aktivuje gizmo pohybu junctionu → táhne v rovině XY (FP6 — manipulátor pohybu)
3. Posun junctionu → L1 aktualizace souřadnic → detekce cyklů → L2 přepočet area/perimeter obou sousedních místností → L3 sync fáze 1 + 2 → GN reevaluace
4. Kóty se automaticky aktualizují (FP7 čte aktuální data z L1/L2)

Pokrytí: FP5 (must-have — výběr prvku), FP6 (must-have), FP3 (must-have), FP7 (must-have). Celý workflow průchozí.

**UC 2.1 — Obkreslení 2D půdorysu**

1. Uživatel aktivuje Pencil Tool klávesou D → stav ČEKÁNÍ (FP1 — stavový automat)
2. Klikne na roh místnosti → snap na mřížku / junction → stav KRESLENÍ (FP1 — snapping)
3. Klikne na další roh → `L1.add_junction()` + `L1.add_wall()` → koncový bod = nový počáteční (FP1 — interakce s modelem)
4. Opakuje dokud neuzavře cyklus → snap na existující junction → L1 detekce cyklu → L2 Room → L3 sync → GN generuje 3D stěny
5. Pokračuje kreslením dalších místností sdílejících junctions

Pokrytí: FP1 (must-have), FP3 (must-have). Celý workflow průchozí.

**UC 2.2 — Vložení otvorů**

1. Uživatel klikne RMB na stěnu → kontextová nabídka (FP5) → „Přidat otvor — okno"
2. Zadá rozměry otvoru (1500 × 1250 mm) a výšku parapetu → validace vůči délce stěny
3. Otvor uložen jako reference v `Wall.openings` (L1) → L3 serializace pozičních atributů → GN Mesh Boolean vyřízne díru (FP2 — otvory)
4. Pozdější změna rozměru: RMB → „Upravit otvor" → nová hodnota → update cyklus L1 → L3 → GN

Pokrytí: FP2 (must-have — vazba otvorů), FP5 (must-have). Celý workflow průchozí. Poznámka: GN Mesh Boolean pro vizuální výřez je should-have; v MVP se otvor ukládá datově, ale vizuální výřez může být odložen.

**UC 3.1 — Rychlý blockout**

1. Pencil Tool → série navazujících stěn se snap na junction (FP1)
2. Automatická detekce místností při uzavření cyklů (FP3)
3. Žádné metriky nepotřebné — uživatel pracuje vizuálně

Pokrytí: FP1 (must-have), FP3 (must-have). Workflow průchozí.

**UC 3.2 — Iterace na základě playtestingu a finalizace**

1. Uživatel vybere junction na kraji chodby → gizmo pohybu → rozšíření chodby (FP6)
2. L1 → L2 přepočet sousedních místností → L3 sync → GN reevaluace
3. Spuštění finalizačního nástroje → dialog s volbami (FP4 — možnosti finalizace)
4. Aplikace GN modifikátoru → konverze UV atributů → konsolidace materiálů → statická mesh připravená na FBX export

Pokrytí: FP6 (must-have), FP4 (must-have). Celý workflow průchozí.

## Analýza okrajových případů (edge cases)

Návrh musí spolehlivě reagovat i na nestandardní vstupy a situace. Následující analýza ověřuje, že architektura a datový model tyto případy pokrývají.

**Topologické edge cases (Vrstva 1)**

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Stěna s nulovým rozpětím (start = end junction) | Odmítnuta validací L1 — prostý graf neumožňuje smyčkové hrany | Validační pravidla (kapitola 3.3) |
| Duplicitní stěna mezi dvěma junctions | Odmítnuta validací L1 — prostý graf povoluje max jednu hranu mezi dvěma uzly | Validační pravidla (kapitola 3.3) |
| Smazání stěny sdílené dvěma místnostmi | L1 odebere hranu → dva cykly se sloučí v jeden → L2 node fusion (ID zachovaného uzlu přetrvá) | Tok dat — odebrání hrany (kapitola 3.2) |
| Smazání posledního junctionu izolované stěny | L1 odebere stěnu i osiřelé junctions → L2 žádná změna (nebyl cyklus) | FP1 — vrácení |
| Posun junctionu tak, že stěny se protnou | Planaritní kontrola L1 detekuje neplatný stav → operace odmítnuta nebo junction vrácen na poslední platnou pozici | Principy návrhu — planarita (kapitola 3.2) |

**Sémantické edge cases (Vrstva 2)**

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Místnost s plochou pod minimem (< 1 m²) | Cyklus detekován, ale Room nevytvořen kvůli validaci minimální plochy | Validační pravidla (kapitola 3.3) |
| Místnost s extrémním poměrem stran | Validace aspect ratio (0.1–10.0) → Room nevytvořen | Validační pravidla (kapitola 3.3) |
| Všechny stěny místnosti smazány najednou | Každé odebrání hrany spouští detekci cyklů → postupný zánik místností → L2 konzistentní | Tok dat (kapitola 3.2) |
| Změna geometrie bez změny topologie (posun junctionu) | ID místnosti a metadata přetrvávají; přepočítá se pouze area, perimeter, centroid | Model místnosti (kapitola 3.3) |

**UI edge cases**

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Dvojitý stisk ESC v Pencil Tool | Stav KRESLENÍ → ČEKÁNÍ (první ESC); ČEKÁNÍ → NEAKTIVNÍ (druhý ESC) — stavový automat neumožňuje přeskočení | FP1 — stavový automat |
| RMB na prázdný prostor (žádný element) | Kontextová nabídka zobrazí globální akce (mřížka, kótování) | FP5 — kontext: prázdný prostor |
| Gizmo výšky — tah pod nulu | Minimální výška vynucena validačním pravidlem (≥ 1.0 m); gizmo nepřekročí limit | FP6 + validace (kapitola 3.3) |
| Vložení otvoru širšího než stěna | Validace šířky otvoru vůči délce stěny → operace odmítnuta se srozumitelnou chybovou zprávou | FP2 — vazba otvorů + NP3 (UX) |

**Persistence edge cases**

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Načtení .blend souboru bez room metadata Custom Property | Rekonstrukce L1 a L2 z named attributes na mesh → místnosti existují, ale bez uživatelských názvů | FP3 — perzistence dat |
| Undo po přidání stěny | Blender Undo obnoví snapshot mesh → rekonstrukce L1 + L2 ze stavu před přidáním | FP3 — perzistence dat |
| Undo po finalizaci (s volbou „zachovat originál") | Blender Undo odstraní finalizovanou kopii → parametrický originál nedotčen | FP4 — interakce s modelem |

## Kontrolní matice: scénáře × požadavky

Ověření, že každý scénář použití z analýzy (kapitola 2.4) je pokryt alespoň jedním must-have FP a že žádný must-have FP není nepokryt scénářem.

| | UC 1.1 | UC 1.2 | UC 2.1 | UC 2.2 | UC 3.1 | UC 3.2 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FP1 | | | ✅ | | ✅ | |
| FP2 | ✅ | | | ✅ | | ✅ |
| FP3 | ✅ | ✅ | ✅ | | ✅ | |
| FP4 | | | | | | ✅ |
| FP5 | | ✅ | | ✅ | | |
| FP6 | | ✅ | | | | ✅ |
| FP7 | ✅ | ✅ | | | | |

Závěr: Každý must-have FP je pokryt minimálně jedním scénářem. Každý scénář je průchozí navrhovanou architekturou bez identifikovaných logických trhlin.
