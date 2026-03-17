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

## Životní cyklus addonu v Blenderu
### [1. Fáze objevení a inicializace](./files/technicka_analyza_detail.md#1-fáze-objevení-a-inicializace)
### [2. Fáze registrace a aktivace](./files/technicka_analyza_detail.md#2-fáze-registrace-a-aktivace)
### [3. Fáze běhu a interakce](./files/technicka_analyza_detail.md#3-fáze-běhu-a-interakce)
### [4. Fáze deaktivace a odregistrace](./files/technicka_analyza_detail.md#4-fáze-deaktivace-a-odregistrace)

## Základní stavební kameny addonu - paradigmata
### Operátory
### Uživatelské rozhraní
### Vlastnosti a data

## Návrh - FP1 - Pencil Tool

## Návrh - FP2 - Generování a úprava parametrických objektů

## Návrh - FP3 - správa prostoru a metadat

## Návrh - FP4 - finalizační nástroj