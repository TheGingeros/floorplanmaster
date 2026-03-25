# Technická Analýza - Blender add-on pro parametrické modelování prostorových dispozic

## Architektura Blenderu a Blender API
- Blender je modulární systém postavený na unikátním způsoby správy dat - dualita systému DNA a RNA
- blender využívá kombinaci vzoru MVC - model view controller, což umožňuje oddělit uživatelské rozhraní - view, od vnitřní logiky - model a zpracování vstupů - controller
- addony tedy můžou definovat vlastní výpočty např. v GN - model, zatímco blende se stará o jejich vykreslení do viewportu a zachytávání událostí myši přes python API

### [Modulární systém](./files/definice.md#modulární-systém)
### [Systém DNA](./files/definice.md#systém-dna)
### [Systém RNA](./files/definice.md#systém-rna)
[Zdroje](./files/sources.md#modularita-systém-dna-a-rna)

### [Vzor MVC - Model-View-Controller](./files/definice.md#vzor-mvc---model-view-controller)

## 1. Interaktivní kreslení a interakce ve viewportu - jak ovládat a spravovat prvky ve viewportu
### [Modální operátory - modal operators - FP1](./files/02_options_and_limits_blender_api.md#modální-operátory---modal-operators---fp1)
### [Vykreslování vlastního UI ve scéně - FP7](./files/02_options_and_limits_blender_api.md#vykreslování-vlastního-ui-ve-scéně---fp7)
### [Limity výkonu Pythonu v Blenderu](./files/02_options_and_limits_blender_api.md#limity-výkonu-pythonu-v-blenderu)

## 2. Reprezentace geometrie - jak generovat a reprezentovat stěny a geometrii
### [BMesh](./files/02_geometry_and_topology_representation.md#datová-struktura-bmesh-a-její-význam-pro-architektonické-modelování)
### [Geometry Nodes](./files/02_geometry_and_topology_representation.md#geometry-nodes-a-paradigma-polí)
### [Porovnání BMesh vs Geometry Nodes](./files/02_geometry_and_topology_representation.md#porovnání-bmesh-a-geometry-nodes-pro-generování-3d-stěn)

## 3. Datová reprezentace logické struktury sítě místností - jak reprezentovat síť stěn a místností na pozadí
### [Abstraktní grafy - grafová reprezentace](./files/02_geometry_and_topology_representation.md#abstraktní-grafy---grafová-reprezentace)
### [Datový model](./files/02_geometry_and_topology_representation.md#datový-model---multigraph)

## 4. Tvorba otvorů pro okna a dveře - nedestruktivní workflow - jak vytvářet otvory pro okna a dveře v síti stěn
### [Boolean operace spravované přes Python API](./files/02_geometry_and_topology_representation.md#boolean-operace-spravované-přes-python-api)

### [Mesh Boolean v Geometry Nodes](./files/02_geometry_and_topology_representation.md#mesh-boolean-v-geometry-nodes)

### [Metody bez Booleovských operací (Procedurální dekompozice)](./files/02_geometry_and_topology_representation.md#metody-bez-booleovských-operací-procedurální-dekompozice)

### [Srovnání metod](./files/02_geometry_and_topology_representation.md#srovnání-metod)

### [Problém coplanárních ploch a integrity sítě](./files/02_geometry_and_topology_representation.md#problém-coplanárních-ploch-a-integrity-sítě)


## 5. Ukládání dat a správa metadat - jak ukládat potřebná data pro doplňek
### [Systémy pro správu metadat a uživatelských parametrů](./files/02_saving_data_and_metadata.md#systémy-pro-správu-metadat-a-uživatelských-parametrů)
### [Vazby dat, Scéna, Objekt, Mesh](./files/02_saving_data_and_metadata.md#vazby-dat-scéna-objekt-mesh)
### [Systém prostorových závislostí](./files/02_saving_data_and_metadata.md#systém-prostorových-závislostí)

## 6. Návrh uživatelského rozhraní - jak definovat a vykreslovat UI
todo
## 7. Finalizační nástroj
todo
## 8. Architektura samotného kódu - jak obecně strukturovat implementaci addonu atd.
todo