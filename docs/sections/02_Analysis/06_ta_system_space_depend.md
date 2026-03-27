# Systém prostorových závislostí
- typický požadavkem je, aby se okno automaticky posunulo nebo přizpůsobilo při změně délky stěny atd
## Hiearchie Parent-Child a omezení (Constraints)
- parent-child je nejjednodušším způsobem, jak zajistit přenos transformací
- pro architektonické prvky je však standardní parenting často nedostatečný, protože přenáší transformaci celého objektu, ale nereaguje na změny vnitřní geometrie
- vhodnějším nástrojem je omezení `Child Of` v kombinaci s nastavením `Set Inverse`
    - umožňuje jemnější kontrolu nad tím, které kanály (lokace, rotace, měřítko) jsou ovlivněny rodičem
    - toto řešení neřeší situaci, kdy se stěna prodlouží v editačním režimu
### Systém ovladačů
- umožňují definovat hodnotu vlastnosti pomocí Python výrazu, který může referovat jiné vlastnosti v rámci scény
-  lze využít Drivers k propojení pozice okna s parametry stěny uloženými v `PropertyGroup`
- Například x-ová souřadnice okna může být definována jako: $$\text{pos\_x} = \text{wall.length} \times \text{window.relative\_position}$$
- výhodou je, že se vyhodnocují v rámci grafu závislostí Blenderu, což zajišťuje vysoký výkon a okamžitou odezvu v uživatelském rozhraní
- nevýhodou je nestabilita: při přejmenování objektů nebo změně struktury datablocků může dojít k přerušení vazeb, pokud není implementován robustní systém správy jmen
## Reaktivita pomocí Vertex Groups a Hook modifikátorů
- aby okno sledovalo pohyb určité části stěny, lze využít kombinaci skupin vrcholů (Vertex Groups) a modifikátoru `Hook`
1. na stěně se vytvoří skupina vrcholů v místě, kde je osazeno okno
2. na tuto skupinu se aplikuje modifikátor `Hook`, jehož řídicím objektem (Hook Object) je prázdný objekt (Empty), který slouží jako rodič okna
3. jakýkoli pohyb vrcholů stěny v editačním režimu se nyní přenáší na Empty objekt a tím i na samotné okno
- mnohem stabilnější než čistě skriptované řešení, protože využívá nativní výpočetní řetězec Blenderu, který je optimalizován pro reálný čas
## Automatizace pomocí aplikačních handlerů
- pro případy, které nelze vyřešit modifikátory nebo ovladači (např. komplexní topologické změny), je nutné nasadit systém aplikačních handlerů
- `bpy.app.handlers.depsgraph_update_post` - tento handler je vyvolán po každé aktualizaci scény
- v rámci handlerů lze provádět následující operace:
    - kontrola integrity vazeb (např. zda stále existuje stěna, ke které je okno přiřazeno)
    - dynamická regenerace meshe stěny při změně parametrů v `PropertyGroup` (např. přidání nového segmentu stěny)
    - synchronizace materiálů mezi souvisejícími prvky
- při používání handlerů je důležité dbát na efektivitu - výpočty by měly být prováděny pouze pro objekty označené příznakem "is_dirty", aby nedocházelo k degradaci výkonu při práci s rozsáhlými scénami