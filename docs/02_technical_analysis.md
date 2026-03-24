# Technická Analýza - Blender add-on pro parametrické modelování prostorových dispozic

## 1. Architektura Blenderu a Blender API
- Blender je modulární systém postavený na unikátním způsoby správy dat - dualita systému DNA a RNA
- blender využívá kombinaci vzoru MVC - model view controller, což umožňuje oddělit uživatelské rozhraní - view, od vnitřní logiky - model a zpracování vstupů - controller
- addony tedy můžou definovat vlastní výpočty např. v GN - model, zatímco blende se stará o jejich vykreslení do viewportu a zachytávání událostí myši přes python API

### [Modulární systém](./files/definice.md#modulární-systém)
### [Systém DNA](./files/definice.md#systém-dna)
### [Systém RNA](./files/definice.md#systém-rna)
[Zdroje](./files/sources.md#modularita-systém-dna-a-rna)

### [Vzor MVC - Model-View-Controller](./files/definice.md#vzor-mvc---model-view-controller)

## Interaktivní kreslení a interakce ve viewportu
### [Modální operátory - modal operators - FP1](./files/02_options_and_limits_blender_api.md#modální-operátory---modal-operators---fp1)
### [Vykreslování vlastního UI ve scéně - FP7](./files/02_options_and_limits_blender_api.md#vykreslování-vlastního-ui-ve-scéně---fp7)
### [Limity výkonu Pythonu v Blenderu](./files/02_options_and_limits_blender_api.md#limity-výkonu-pythonu-v-blenderu)

## 2. Reprezentace geometrie
### BMesh
### Geometry Nodes
### Porovnání BMesh vs Geometry Nodes
### Tvorba otvorů pro okna a dveře - nedestruktivní workflow
## 3. Datová reprezentace logické struktury sítě místností

## Ukládání dat a správa metadat

## Návrh uživatelského rozhraní a interakce

## Finalizační nástroj

## Architektura samotného kódu
