# Datový model - MultiGraph
- využití knihoven jako NetworkX v prostředí Blenderu umožňuje provádět prostorové analýzy, které jsou čistě geometrickými nástroji nedosažitelné
    - například použít algoritmus pro hledání nejkratší cesty (Dijkstra) pro ověření evakuačních tras nebo automaticky generovat sémantické popisky místností na základě jejich konektivity
- nejefektivnější systém za využití hybridního modelu
- tento model umožňuje například změnit typ oken v celé jižní straně budovy pouhou změnou jednoho parametru v grafu, což se okamžitě projeví v geometry nodes díky dynamickému čtění atributů
## Vrstva 1. Topologický skelet (Strukturální)
- čistá grafová data o junction bodech a stěnách
- NetworkX zde vypočítává planární embedding a identifikuje "Face" (místnosti) pomocí metod pro hledání cyklů
## Vrstva 2: Sémantický dual (NRG):
- uzly této vrstvy jsou mapovány na ID cyklů z Vrstvy 1
- změna geometrie ve Vrstvě 1 (např. posun stěny) aktualizuje pouze atribut "Area" v uzlu Vrstvy 2, aniž by se měnila její identita
## Synchronizační bridge (Named Attributes)
- python addon v každém kroku serializuje data z grafu do Named Attributes meshe v Blenderu (např. `room_id` na Face doméně, `wall_thickness` na Edge doméně)
- Geometry Nodes pak tato data čtou a generují 3D objemy v reálném čase

[Zdroje](../../files/00_sources.md#datová-reprezentace-logické-struktury-sítě-místností)