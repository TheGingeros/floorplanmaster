# Analýza okrajových případů

Návrh musí spolehlivě reagovat i na nestandardní vstupy a situace. Následující analýza ověřuje, že architektura a datový model tyto případy pokrývají.

## Topologické edge cases (Vrstva 1)

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Stěna s nulovým rozpětím (start = end junction) | Odmítnuta validací L1 — prostý graf neumožňuje smyčkové hrany | Validační pravidla (kapitola 3.3) |
| Duplicitní stěna mezi dvěma junctions | Odmítnuta validací L1 — prostý graf povoluje max jednu hranu mezi dvěma uzly | Validační pravidla (kapitola 3.3) |
| Smazání stěny sdílené dvěma místnostmi | L1 odebere hranu → dva cykly se sloučí v jeden → L2 node fusion (ID zachovaného uzlu přetrvá) | Tok dat — odebrání hrany (kapitola 3.2) |
| Smazání posledního junctionu izolované stěny | L1 odebere stěnu i osiřelé junctions → L2 žádná změna (nebyl cyklus) | FP1 — vrácení |
| Posun junctionu tak, že stěny se protnou | Planaritní kontrola L1 detekuje neplatný stav → operace odmítnuta nebo junction vrácen na poslední platnou pozici | Principy návrhu — planarita (kapitola 3.2) |

## Sémantické edge cases (Vrstva 2)

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Místnost s plochou pod minimem (< 1 m²) | Cyklus detekován, ale Room nevytvořen kvůli validaci minimální plochy | Validační pravidla (kapitola 3.3) |
| Místnost s extrémním poměrem stran | Validace aspect ratio (0.1–10.0) → Room nevytvořen | Validační pravidla (kapitola 3.3) |
| Všechny stěny místnosti smazány najednou | Každé odebrání hrany spouští detekci cyklů → postupný zánik místností → L2 konzistentní | Tok dat (kapitola 3.2) |
| Změna geometrie bez změny topologie (posun junctionu) | ID místnosti a metadata přetrvávají; přepočítá se pouze area, perimeter, centroid | Model místnosti (kapitola 3.3) |

## UI edge cases

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Dvojitý stisk ESC v Pencil Tool | Stav KRESLENÍ → ČEKÁNÍ (první ESC); ČEKÁNÍ → NEAKTIVNÍ (druhý ESC) — stavový automat neumožňuje přeskočení | FP1 — stavový automat |
| RMB na prázdný prostor (žádný element) | Kontextová nabídka zobrazí globální akce (mřížka, kótování) | FP5 — kontext: prázdný prostor |
| Gizmo výšky — tah pod nulu | Minimální výška vynucena validačním pravidlem (≥ 1.0 m); gizmo nepřekročí limit | FP6 + validace (kapitola 3.3) |
| Vložení otvoru širšího než stěna | Validace šířky otvoru vůči délce stěny → operace odmítnuta se srozumitelnou chybovou zprávou | FP2 — vazba otvorů + NP3 (UX) |

## Persistence edge cases

| Situace | Očekávané chování | Pokrytí návrhem |
| :--- | :--- | :--- |
| Načtení .blend souboru bez room metadata Custom Property | Rekonstrukce L1 a L2 z named attributes na mesh → místnosti existují, ale bez uživatelských názvů | FP3 — perzistence dat |
| Undo po přidání stěny | Blender Undo obnoví snapshot mesh → rekonstrukce L1 + L2 ze stavu před přidáním | FP3 — perzistence dat |
| Undo po finalizaci (s volbou „zachovat originál") | Blender Undo odstraní finalizovanou kopii → parametrický originál nedotčen | FP4 — interakce s modelem |
