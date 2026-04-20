# FP1 — Interaktivní kreslení (Pencil Tool)
Nástroj Tužka je primární vstupní rozhraní addonu — modální operátor (Controller), který zachytává vstupy z myši a klávesnice a překládá je na operace nad Vrstvou 1 strukturálního grafu. Veškerá logika kreslení probíhá v 2D rovině (XY), Z-souřadnice je ignorována. Vizuální náhled (préview stěny, HUD s délkou a úhlem) kreslí GPU overlay nezávisle na datovém modelu — zápis do Vrstvy 1 nastane až po potvrzení bodu uživatelem, ne průběžně.

## Stavový automat

Operátor je řízen striktním stavovým automatem, který garantuje, že stěna nikdy nevznikne bez platného počátečního bodu a že nelze skončit v nekonzistentním stavu.

```mermaid
stateDiagram-v2
    [*] --> NEAKTIVNÍ
    NEAKTIVNÍ --> ČEKÁNÍ : aktivace nástroje
    ČEKÁNÍ --> KRESLENÍ : umístění počátečního junctionu
    KRESLENÍ --> KRESLENÍ : potvrzení stěny,\nkoncový bod = nový počáteční
    KRESLENÍ --> KRESLENÍ : vrácení posledního bodu
    ČEKÁNÍ --> ČEKÁNÍ : vrácení posledního bodu
    KRESLENÍ --> ČEKÁNÍ : zrušení aktuální čáry
    KRESLENÍ --> [*] : potvrzení sezení
    ČEKÁNÍ --> [*] : potvrzení sezení
    KRESLENÍ --> [*] : přerušení sezení (bez uložení)
    ČEKÁNÍ --> [*] : přerušení sezení (bez uložení)
```

- **NEAKTIVNÍ** — nástroj je registrován, ale nepřijímá vstupy; jiné nástroje Blenderu fungují normálně
- **ČEKÁNÍ** — nástroj aktivní, kurzor sleduje myš, žádný počáteční bod není umístěn; GPU overlay zobrazuje existující geometrii a snap indikátory; vrácení posledního bodu funguje i v tomto stavu (odstraní naposledy umístěný bod z aktuální sezení)
- **KRESLENÍ** — první junction umístěn; GPU overlay kreslí náhled stěny od počátečního bodu ke kurzoru v reálném čase; HUD zobrazuje délku a úhel

Z obou stavů lze sezení buď **potvrdit** (všechny stěny se synchronizují do meshe a zapíší do undo stacku) nebo **přerušit** (všechny stěny a junctiony umístěné v aktuální sezení se odstraní z grafu, mesh zůstane nezměněn). Zrušení aktuální čáry (přechod KRESLENÍ → ČEKÁNÍ) neodstraňuje dříve potvrzené stěny téže sezení — pouze ukončí rozpracovanou linii.

## Snapping *(must-have / should-have)*

Snapping je výpočet provedený nad pozicí kurzoru před každým zápisem do Vrstvy 1. Priorita od nejvyšší:
1. **Snap na existující junction** *(must-have)* — pokud je kurzor do 15 pixelů od existujícího junctionu ve Vrstvě 1, přichytí se na jeho přesné souřadnice
2. **Snap na osu** *(should-have)* — pokud je odchylka kurzoru od osy X nebo Y menší než 10 pixelů relativně k poslednímu junctionu, souřadnice se zarovná na přímku
3. **Snap na mřížku** *(should-have)* — volitelné zarovnání na konfigurovaný rastr (0.1 m, 0.5 m, 1.0 m)
4. **Snap na úhel** *(should-have)* — zarovnání na násobky 45°

Aktivní snap se vizuálně indikuje kruhem u kurzoru. Uživatel může snap dočasně potlačit podržením Shift.

## Interakce s datovým modelem

Zápis do Vrstvy 1 nastane vždy až po potvrzení, nikdy průběžně při pohybu myši:

- **Potvrzení bodu** → `L1.add_junction(x, y)` nebo reuse existujícího junctionu v toleranci → vrátí `junction_id`
- **Potvrzení stěny** → `L1.add_wall(j_start, j_end, thickness, height, material)` → spustí detekci cyklů → Vrstva 2 aktualizuje místnosti → Vrstva 3 synchronizační cyklus (fáze 1 + fáze 2)
- **Vrácení** → `L1.remove_wall(last_wall_id)` + odstranění osiřelých junctionů → L2 + L3 sync
- **Zrušení** → žádný zápis do dat; GPU overlay se vypne

## Vizuální zpětná vazba (GPU overlay) *(must-have)*

Veškeré kreslení préview probíhá v GPU draw_handler registrovaném na 3D Viewport — neukládá se do geometrie ani datového modelu:

- náhled stěny: čára od posledního junctionu ke kurzoru; odlišná barva od potvrzených stěn
- HUD: délka navrhované stěny a úhel k poslednímu úseku (aktualizováno při každém pohybu myši); ve stavu ČEKÁNÍ zobrazuje zprávu „Waiting for input"
- snap indikátor: barevný kruh u kurzoru při aktivním snapu
- nápověda kláves: ikony kláves a myši zobrazené v dolní stavové liště Blenderu (STATUSBAR_HT_header); stav ČEKÁNÍ zobrazuje LMB / Z / ESC; stav KRESLENÍ zobrazuje aktualizovanou sadu; HUD nápovědu kláves nezobrazuje

## Způsob generování stěny podle preview čáry *(should-have)*

Preview čára, kterou uživatel táhne myší, reprezentuje osu stěny — avšak fyzická stěna má tloušťku, a tloušťka musí být někam „rozložena". Mód generování určuje, na kterou stranu od preview čáry se tloušťka stěny rozkládá. Tři dostupné módy odpovídají konvenci používané ve vektorových nástrojích (Illustrator, Inkscape) a CAD programech:

- **Střed (Center)** — stěna je symetricky na obou stranách preview čáry; preview čára splývá s osou stěny. Výchozí mód. Vhodný pro schematické kreslení, kde přesná poloha povrchu stěny není prioritou.
- **Levá strana (Left)** — stěna se generuje zcela nalevo od směru kreslení (tj. celá tloušťka leží na levé straně preview čáry). Preview čára odpovídá pravému líci stěny. Vhodné pro kreslení stěny podél existující hrany (např. vnější obvodová stěna).
- **Pravá strana (Right)** — symetricky opačně; stěna leží zcela napravo od směru kreslení. Preview čára odpovídá levému líci stěny.

Pojmy „levá" a „pravá" jsou vztaženy k **směru kreslení** (od počátečního junctionu ke kurzoru), nikoli k pohledu kamery ani k ose scény. Při kreslení zleva doprava je „levá strana" stěny horní (vyšší Y), při kreslení shora dolů je „levá strana" stěna napravo (vyšší X) — uživatel to vnímá jako přichycení stěny k té straně čáry, na které drží prst.

Mód lze přepínat klávesou `Tab` kdykoli během aktivního nástroje (ve stavu ČEKÁNÍ i KRESLENÍ) bez přerušení sezení. Aktuální mód je zobrazen v levém horním rohu viewportu nebo v sekci active tool panelu. Přepnutí módu okamžitě překreslí preview, změna se projeví na následujících nově umístěných stěnách — dříve potvrzené stěny téže sezení se nemění.
