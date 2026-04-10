# FP6 — Interaktivní 3D manipulátory
3D manipulátory (gizma) jsou interaktivní ovládací prvky přímo ve 3D viewportu — umožňují intuitivní úpravy parametrů stěn a junctionů taháním myší, bez zadávání čísel do panelů. Klíčovým návrhovým požadavkem je zachování planarity Vrstvy 1: všechny manipulátory mají geometrické omezení, které vylučuje neplatné přechody (zejména pohyb mimo rovinu XY).

## Typy manipulátorů *(should-have)*

**Manipulátor tloušťky stěny**
- Obousměrná šipka kolmá na osu vybrané stěny
- Pohyb omezen na rovinu XY (kolmo na osu stěny)
- Aktualizuje atribut `wall_thickness` ve Vrstvě 1 → Vrstva 3 fáze 2 → GN reevaluace
- Topologie Vrstvy 1 (junctiony, hrany) zůstává nezměněna

**Manipulátor výšky stěny**
- Svislá šipka na středu vybrané stěny
- Pohyb omezen výhradně na osu Z
- Aktualizuje atribut `wall_height` ve Vrstvě 1 → Vrstva 3 fáze 2 → GN reevaluace
- Z-souřadnice junctionů ve Vrstvě 1 se nemění (Vrstva 1 je striktně 2D)

**Manipulátor pohybu junctionu**
- Kruh na vybraném junctionu, umožňuje tahání v rovině
- Pohyb striktně omezen na rovinu XY — Z-složka tahu je zahozena
- Aktualizuje souřadnice junctionu ve Vrstvě 1 → přepočet délek a úhlů všech připojených stěn → detekce cyklů → L2 + L3 sync (fáze 1 + fáze 2)

## Geometrické omezení (2D lock) *(should-have)*

Zámek do roviny XY je kritické bezpečnostní opatření: pokud by uživatel omylem posunul junction mimo rovinu, strukturální graf by přestal být planární a detekce cyklů by selhala. Omezení je vynuceno zpracováním delta pohybu myši — vertikální složka je před zápisem do Vrstvy 1 zahozena. Implementace využívá rozhraní Gizmo API (`bpy.types.Gizmo`, `bpy.types.GizmoGroup`).
