# 3.5.2 N-panel (Sidebar)

N-panel (Sidebar) ve 3D Viewportu je standardní místem, kam Blender addony umísťují trvalé parametrické rozhraní. Addon přidává záložku s názvem **FloorPlanMaster**, která sdružuje všechny ovládací prvky do jednoho přehledného místa dostupného stiskem `N`. Záložka je rozdělena do tří skládacích sekcí odpovídajících odlišným účelům: spouštění akcí (Nástroje), prohlížení a editace existujících prvků (Místnosti) a konfigurace globálních parametrů scény (Nastavení). Toto členění přejímá vzor z Archipack, kde je panel rovněž rozdělen na sekci operátorů a sekci parametrů vybraného objektu — při výběru prvku se jeho parametry automaticky zobrazí v příslušné části panelu bez nutnosti klikání na tlačítko Properties.

## Sekce Nástroje

Sekce Nástroje obsahuje tlačítka operátorů — akce, které vždy pracují s 3D kurzorem nebo spouštějí modální smyčku, nikoli s výběrem stávajících prvků. Toto odlišení je záměrné: Blender konvencí je, že akce modifikující výběr patří do jiných sekcí nebo kontextové nabídky, zatímco akce vkládající nové prvky jsou dostupné nezávisle na výběru.

Sekce obsahuje:

- **Nakreslit tužkou** — alternativa ke klávesové zkratce `D`; aktivuje Pencil Tool (FP1) a přepne kurzor do aktivního stavu; identická akce jako klik na ikonu v Toolbaru
- **Vložit místnost** — otevře inline formulář přímo v panelu se vstupními poli: šířka, hloubka (nebo volitelně plocha a poměr stran), výška stěn, tloušťka stěn; po potvrzení vloží pravoúhlou místnost se středem v pozici 3D kurzoru (FP2); výhodou oproti klávesové zkratce je, že uživatel vidí výchozí hodnoty a může je přepsat bez nutnosti pamatovat si přesnou klávesovou sekvenci
- **Finalizovat** — spustí finalizační pipeline (FP4); zobrazí pop-over dialog s volbami výstupu (organizace objektů ve scéně, přiřazení materiálů, zachování originálu)
- **Přidat otvor** — aktivuje se pouze pokud je vybraná stěna; vloží parametrický otvor (dveře nebo okno) na danou hranu Vrstvy 1 (FP2 — should-have)

## Sekce Místnosti

Sekce Místnosti je hlavním přehledem datového modelu — seznam všech uzlů Vrstvy 2 (RoomGraph) se základními metrikami. Vzor odpovídá technice „list panel s automatickým výběrem", kterou používá Blender nativně v Object Data Properties pro vertex groups nebo shape keys: kliknutí na položku v seznamu synchronně vybere odpovídající prvek ve viewportu.

**Seznam místností** zobrazuje pro každou místnost:
- název místnosti (`room_name`) editovatelný přímo v řádku seznamu
- typ místnosti (`room_type`) jako barevný štítek (obývák, ložnice, koupelna…)
- plochu v nastaveném systému jednotek (aktualizuje se automaticky při každé změně Vrstvy 1)

Kliknutím na položku v seznamu dojde k:
1. výběru místnosti ve viewportu (Vrstva 3 — plochy odpovídající danému cyklu jsou označeny)
2. zobrazení gizmos pro vybranou místnost (FP6 — tloušťka a výška přilehlých stěn)
3. rozbalení detailního pohledu přímo pod položkou v panelu

**Detailní pohled vybrané místnosti** zobrazuje pod vybranou položkou:
- editovatelný název místnosti a výběr z enumu typů místností
- obvod místnosti a počet stěn (pouze pro čtení)
- vnořený seznam stěn místnosti — pro každou stěnu délku a tloušťku; kliknutím na stěnu v tomto seznamu se vybere příslušná hrana ve viewportu a zobrazí se gizmos výšky a tloušťky dané stěny

Oddělení výpisu stěn do vnořeného pohledu pod místností (namísto globálního seznamu stěn) odráží hierarchii datového modelu: stěny mají smysl pouze v kontextu místnosti, globální seznam stěn by pro větší půdorysy byl nepřehledný a porušoval by hierarchii Vrstva 1 → Vrstva 2.

## Sekce Nastavení

Sekce Nastavení obsahuje globální parametry scény uložené v `Scene PropertyGroup` (soulad s pravidlem persistence nastavení z kapitoly 3.1). Tyto parametry se aplikují na nově vytvářené prvky; existující prvky se nemodifikují, aby uživatel nepřišel o záměrně nastavené hodnoty.

| Parametr | Výchozí hodnota | Popis |
| :--- | :--- | :--- |
| Systém jednotek | Metrický | Přepíná zobrazení rozměrů v kótování i panelu; hodnoty jsou interně vždy v metrech |
| Hustota mřížky | 0,5 m | Rastrová vzdálenost pro volitelný snap na mřížku (FP1 — should-have) |
| Výchozí tloušťka stěny | 0,3 m | Přednabídnuto při každém novém kreslení nebo vkládání místnosti |
| Výchozí výška stěny | 2,5 m | Přednabídnuto pro nové stěny |
| Velikost textu kót | 14 px | Velikost BLF textu overlay kótování (FP7) |

Záměrně jsou do Nastavení zařazeny pouze parametry ovlivňující chování celého projektu, nikoliv parametry jednotlivých prvků — ty patří do detailního pohledu místnosti nebo jsou dostupné přes gizmos.
