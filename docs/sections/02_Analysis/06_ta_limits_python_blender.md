# Limity výkonu Pythonu v Blenderu
- python je v prostředí blenderu interpretovaným jazykem
- je potřeba náročné operace delegovat na stranu Blenderu nebo GPU, které využívají C++
- zkušnosti z vývoje komplexních importérů a generativních nástrojů ukazují, že čistý Python je řádově pomalejší při úlohách vyžadující hromadné zpracování dat
- v kontextu architektonického kreslení jsou hlavními limitujícími faktory:
    1. **Iterace přes mesh data** - procházení vrcholů pomocí for smyčky je pomalé
    2. **Počet objektů v `bpy.data.objects`** - blender zpomaluje exponenciálně s rostoucím počtem unikátních objektů ve scéně
    3. **Časté aktulizace DepsGraphu** - každá změna geometrie vynucuje přepočet grafu závislosti, 

## Metody delegování výpočtů na C++ jádro
k překonání těchto limitů se v profesionálních add-onech využívají následující techniky:
#### Využítí foreach_set a foreach_get
- tyto metody umožňují přenášet celá pole dat  mezi Pythonem a C++ strukturami Blenderu jedinou operací
- operátor vypočítá novou pozici stěny, namísto nastavování každého vrcholu zvlášť by měl použít NumPy pole a metodu `foreach_set`, což přinese zrychlení
#### Delegování na modifikátory
- místo aby Python generoval detailní geometrii, měl by vytvořit pouze základní čárový model a na něj aplikovat modifikátory jako Solidify, Bevel nebo Array
- modifikátory jsou implementovány v C++, plně využívají multithreading a jsou optimalizovány pro real-time aktualizaci při změně parametrů
- python operátor pak v modálním běhu pouze mění číselné hodnoty jako modifier.thickness, což je operace s téměř nulovou režií
#### Geometry nodes jako výpočetní backend
- moderním přístupem je využití Geometry Nodes jako vysoce výkonného generativního motoru
- python add-on může vytvořit uzel Geometry Nodes, který obsahuje veškerou logiku pro stavbu domu a přes API pouze manipulovat se vstupními hodnotami tohoto uzlu
- výpočet samotné geometrie pak probíhá v nativním kódu Blenderu, který je o několik řádů rychlejší a efektivnější než jakýkoli skript v Pythonu

[Zdroje](../../files/00_sources.md#limity-výkonu-pythonu-v-blenderu)