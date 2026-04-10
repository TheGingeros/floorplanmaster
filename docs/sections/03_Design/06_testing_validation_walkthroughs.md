# Průchod scénáři použití

Teoretický průchod každým scénářem z analýzy (kapitola 2.4) ověřuje, že navržená architektura a funkce společně pokrývají celý uživatelský workflow. Must-have scénáře (UC 1.1–3.2) jsou plně průchozí v MVP; should-have scénáře (UC 1.3, 2.3, 3.3) jsou průchozí až po implementaci příslušných prvků FP5–FP7.

## Must-have scénáře (UC 1.1–3.2)

Must-have scénáře pokrývají kompletní workflow v rámci MVP. Každý průchod je plně realizovatelný s must-have prvky FP1–FP4.

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

## Should-have scénáře (UC 1.3, 2.3, 3.3)

Should-have scénáře jsou navrhnuty a datově pokryty, ale nejsou průchozí v MVP — závisejí na funkcích FP5–FP7, jejichž implementace je záměrně odložena za MVP scope (kapitola 3.1). Návrh pro každou z těchto funkcí existuje (kapitola 3.4) a architektura je připravena je pojmout bez změny vrstev L1 a L2.

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
