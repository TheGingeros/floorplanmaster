# Technická rozhodnutí a zdůvodnění
Při návrhu jakéhokoliv komplexního softwaru neexistují absolutně dokonalá řešení, ale pouze řada promyšlených kompromisů. Tato sekce slouží jako transparentní záznam nejdůležitějších architektonických voleb, které formují FloorPlanMaster.

Namísto pouhého výčtu použitých technologií zde explicitně obhajujeme, proč byla daná cesta upřednostněna před logickými alternativami. Ať už jde o integraci robustní knihovny NetworkX pro složitou prostorovou matematiku, nebo strategickou sázku na moderní Geometry Nodes namísto tradičního BMesh modelování, každé z těchto rozhodnutí s sebou nese určitou daň. Následující přehled tyto kompromisy – od nutnosti správy externích závislostí až po vyšší složitost správy stavů – otevřeně pojmenovává a dokazuje, že jejich celkový přínos pro výkon, čistotu kódu a nedestruktivní uživatelský zážitek drtivě převažuje nad zavrhnutými variantami.

## Tabulka rozhodnutí

| Rozhodnutí | Hlavní přínos (Proč) | Zamítnutá alternativa | Kompromis (Cena za řešení) |
|----------|-----|-------------|-----------|
| **NetworkX (Logika)** | Hotové algoritmy pro planární grafy, spolehlivá detekce cyklů a cest. | Psaní vlastní odlehčené třídy grafu. | Externí závislost; nutnost řešit automatickou instalaci modulu do interního Pythonu Blenderu. |
| **Geometry Nodes (3D)** | Real-time vykreslování, nedestruktivní workflow, hardwarová akcelerace. | Přímé generování finální sítě přes BMesh či staré modifikátory. | Složitější ladění (debugging) uzlového stromu a skrytá logika mimo Python. |
| **Pojmenované atributy** | Přímé a nativní napojení dat z Pythonu do GN s minimální režií. | Ukládání všech metadat do Vlastních vlastností (Custom Props) nebo JSONu. | Omezení zápisu – data musí být striktně navázána na existující fyzickou topologii (vrcholy, hrany). |
| **Modální operátory** | Zajišťují hladkou interakci a umožňují kreslení dočasných GPU náhledů. | Běžné jednorázové operátory (využívající jen Redo panel). | Výrazně složitější kód a nutnost manuální správy stavového automatu (State Machine). |
| **Planární 2D graf** | Automaticky validuje topologii, zabraňuje neplatnému křížení stěn a definuje jasné místnosti. | Povolení neplanárního či plně 3D grafu. | Nemožnost v jedné vrstvě půdorysu reprezentovat sémanticky oddělené, ale fyzicky se překrývající prostory (např. vnitřní balkony). |