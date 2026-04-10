# 3.6 Testování a validace návrhu

Předchozí kapitoly 3.1–3.5 definovaly MVP scope, architekturu, datový model, funkce a uživatelské rozhraní. Před zahájením implementace je nezbytné provést důkladnou kontrolu celého návrhu — ověřit, že architektura, datové toky a funkce společně spolehlivě pokrývají zadání z MVP scope (kapitola 3.1) a neobsahují logické trhliny. Tato kapitola plní roli kontroly návrhu prostřednictvím kontrolních seznamů, teoretických průchodů scénáři a analýzy okrajových případů.

## Pokrytí must-have požadavků

Následující kontrolní seznam ověřuje, že každý must-have prvek MVP (kapitola 3.1) je plně pokryt návrhem funkce (kapitola 3.4), datovým modelem (kapitola 3.3) a architekturou (kapitola 3.2).

| Požadavek | Must-have prvek | Navrhující sekce | Datový model | Vrstva |
| :--- | :--- | :--- | :--- | :--- |
| FP1 | Modální operátor pro kreslení bodů | FP1 — stavový automat | Junction, Wall (L1) | Controller → L1 → L2 → L3 |
| FP1 | Snap na existující junction | FP1 — snapping | Junction.position (L1) | Controller |
| FP1 | Zápis do L1 až po potvrzení | FP1 — interakce s modelem | — | Controller → L1 |
| FP2 | Dynamická parametrická stěna | FP2 — parametry stěny | Wall.thickness/height (L1) | L1 → L3 → GN |
| FP2 | Vložení pravoúhlé místnosti | FP2 — vložení místnosti | Junction × 4, Wall × 4 (L1) | Controller → L1 → L2 → L3 |
| FP2 | Vazba otvoru na stěnu | FP2 — vazba otvorů | Wall.openings (L1) | L1 → L3 → GN |
| FP2 | GN Mesh Boolean — vizuální výřez otvorů | FP2 — otvory GN Mesh Boolean | Wall.openings, poziční atributy (L3) | L1 → L3 → GN |
| FP3 | Automatická detekce místností | FP3 — detekce cyklů | Room (L2) z cyklu (L1) | L1 → L2 |
| FP3 | Zobrazení plochy místnosti | FP3 — prostorová data | Room.area (L2) | L2 → L3 → GN |
| FP4 | Aplikace GN modifikátoru | FP4 — stavový automat | L3 → statická mesh | View |

Každý must-have prvek je pokryt jednou návrhovou sekcí, má definovaný datový model a průchoditelný tok dat napříč vrstvami.

## Pokrytí should-have požadavků

| Požadavek | Should-have prvek | Navrhující sekce | Datový model | Vrstva |
| :--- | :--- | :--- | :--- | :--- |
| FP5 | Kontextová nabídka s akcemi | FP5 — raycast + akce | L3 raycast → L1/L2 | Controller |
| FP6 | Gizmo pro tloušťku/výšku/posun | FP6 — typy manipulátorů | Wall.thickness/height, Junction.position | Controller → L1 → L3 |
| FP7 | GPU overlay kóty | FP7 — datový pipeline | L1 délky, L2 area + centroid | View (BLF) |

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
4. Krok 2–3 zopakuje pro každou místnost ze stavebního programu; plochy jsou průběžně čitelné z N-panelu (FP3 — metadata)

Pokrytí: FP2 (must-have), FP3 (must-have). Workflow plně průchozí v MVP.

**UC 1.2 — Kreslení dispozice tužkou**

1. Uživatel aktivuje Pencil Tool klávesou D → stav ČEKÁNÍ (FP1 — stavový automat)
2. Klikáním bodů kreslí dispozici; snap na existující junction při uzavírání cyklu (FP1 — snapping)
3. Uzavření cyklu → L1 detekce cyklu → L2 Room → L3 sync → GN generuje 3D stěny (FP3)
4. Uživatel vybere stěnu → N-panel zobrazí parametry → upraví tloušťku/výšku (FP2 — update stěn) → L1 update → L3 fáze 2 → GN reevaluace

Pokrytí: FP1 (must-have), FP2 (must-have), FP3 (must-have). Workflow plně průchozí v MVP.

**UC 2.1 — Obkreslení dodaného 2D půdorysu**

1. Uživatel vloží referenční obrázek půdorysu → aktivuje Pencil Tool klávesou D (FP1 — stavový automat)
2. Odklikává rohy místností přesně podle obrázku; snap na existující junction (FP1 — snapping)
3. Místnosti vznikají automaticky při uzavření cyklů → L1 detekce cyklu → L2 Room → L3 sync → GN generuje 3D stěny (FP3)
4. Výšky a tloušťky stěn nastaví v N-panelu (FP2 — update stěn)

Pokrytí: FP1 (must-have), FP2 (must-have), FP3 (must-have). Workflow plně průchozí v MVP.

**UC 2.2 — Příprava modelu pro renderovací pipeline**

1. Uživatel vybere stěnu → N-panel → přidá otvor zadáním parametrů (šířka, výška, výška parapetu) (FP2 — vazba otvorů)
2. GN Mesh Boolean vizuálně vyřízne otvor v reálném čase; otvor uložen jako reference v `Wall.openings` (L1) → L3 serializace → GN (FP2 — GN Mesh Boolean)
3. Případná změna rozměrů v N-panelu → update cyklus L1 → L3 → GN
4. Finalizační nástroj (FP4) → dialog s volbami → aplikace GN → UV konverze → konsolidace materiálů → statická mesh

Pokrytí: FP2 (must-have), FP4 (must-have). Workflow plně průchozí v MVP.

**UC 3.1 — Rychlý level blockout**

1. Game designer aktivuje Pencil Tool (FP1) → rychle načrtne sérii navazujících místností
2. Místnosti detekované automaticky při uzavření cyklů (FP3)
3. Uniformní výška stěn nastavena v N-panelu pro celý půdorys (FP2 — update stěn)

Pokrytí: FP1 (must-have), FP2 (must-have), FP3 (must-have). Workflow plně průchozí v MVP.

**UC 3.2 — Finalizace a export herní úrovně**

1. Game designer vybere stěnu → N-panel → přidá dveřní otvor zadáním parametrů (FP2 — otvory + GN Mesh Boolean)
2. Ověří plochy místností v N-panelu (FP3 — metadata místností)
3. Spuštění finalizačního nástroje → dialog s volbami (FP4 — možnosti finalizace)
4. Aplikace GN modifikátoru → konverze UV atributů → konsolidace materiálů → statická mesh připravená na FBX/GLTF export

Pokrytí: FP2 (must-have), FP3 (must-have), FP4 (must-have). Workflow plně průchozí v MVP.

Should-have scénáře z analýzy (UC 1.3, 2.3, 3.3) jsou navrhnuty a datově pokryty, ale nejsou průchozí v MVP — závisejí na funkcích FP5–FP7, jejichž implementace je záměrně odložena za MVP scope (kapitola 3.1). Návrh pro každou z těchto funkcí existuje (kapitola 3.4) a architektura je připravena je pojmout bez změny vrstev L1 a L2.

**UC 1.3 — Kontrola rozměrů vůči normovým minimům**

1. Uživatel zapne kótovací overlay v N-panelu → FP7 registruje draw_handler na `SpaceView3D` v režimu `POST_PIXEL`
2. Draw_handler čte délky z hran L1 (Euklidovská vzdálenost junction–junction) → transformuje středy hran do 2D souřadnic obrazovky (`view3d_utils`) → BLF vykreslí hodnoty
3. Draw_handler čte `room_area` a `room_name` z uzlů L2 → transformuje centroidy → BLF vykreslí štítky místností
4. Uživatel vizuálně ověří rozměry a případně upraví parametry stěn v N-panelu

Pokrytí: FP7 (should-have). **Průchod v MVP neúplný** — závisí na implementaci FP7; datový základ (L1 délky, L2 area/centroid) je dostupný od MVP.

**UC 2.3 — Rychlá editace vlastností prvků přes kontextovou nabídku**

1. Uživatel klikne RMB ve viewportu → FP5 vrhne raycast z pozice kurzoru přes L3 mesh → identifikuje plochu (místnost) nebo hranu (stěna)
2. GPU/BLF overlay vykreslí floating panel na pozici kurzoru s kontextovými akcemi (kapitola 3.4 — FP5)
3. Uživatel vybere „Změnit materiál podlahy" → addon zapíše `material_id` do L2 uzlu → L3 sync → GN reevaluace
4. RMB na stěnu → „Přidat otvor / Upravit tloušťku" → aktualizace L1 atributů → L3 fáze 2 → GN

Pokrytí: FP5 (should-have). **Průchod v MVP neúplný** — závisí na implementaci FP5; všechny navazující operace (zápis do L1/L2) jsou dostupné od MVP přes N-panel.

**UC 3.3 — Interaktivní adjustace rozložení místností**

1. Uživatel vybere junction ve viewportu → FP6 aktivuje GizmoGroup pro vybraný junction → zobrazí kruhový manipulátor v rovině XY
2. Uživatel táhne manipulátor → delta pohybu myši je zpracováno; Z-složka zahozena (2D lock) → `L1.move_junction()` aktualizuje souřadnice
3. L1 přepočítá délky a úhly všech připojených stěn → detekce cyklů → L2 přepočet area/perimeter sousedních místností → L3 sync fáze 1 + 2 → GN reevaluace
4. Pokud by posun způsobil protnutí stěn, planaritní kontrola L1 operaci odmítne

Pokrytí: FP6 (should-have). **Průchod v MVP neúplný** — závisí na implementaci FP6; výsledek (aktualizace L1/L2/L3) je identický s manuálním zadáním souřadnic v N-panelu.

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

Ověření, že každý scénář použití z analýzy (kapitola 2.4) je pokryt alespoň jedním FP a že každý FP má svůj scénář.

| | UC 1.1 | UC 1.2 | UC 2.1 | UC 2.2 | UC 3.1 | UC 3.2 | UC 1.3 | UC 2.3 | UC 3.3 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FP1 | | ✅ | ✅ | | ✅ | | | | |
| FP2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | | | |
| FP3 | ✅ | ✅ | ✅ | | ✅ | ✅ | | | |
| FP4 | | | | ✅ | | ✅ | | | |
| FP5 | | | | | | | | ✅ | |
| FP6 | | | | | | | | | ✅ |
| FP7 | | | | | | | ✅ | | |

Závěr: Každý must-have FP (FP1–FP4) je pokryt minimálně jedním scénářem a každý must-have scénář (UC 1.1–3.2) je plně průchozí v rámci MVP. Should-have FP (FP5–FP7) mají každý svůj dedikovaný scénář (UC 1.3, 2.3, 3.3); tyto scénáře **nejsou průchozí v MVP** — závisejí na implementaci příslušného should-have prvku, ale architektura a datový model pro ně jsou připraveny od MVP.
