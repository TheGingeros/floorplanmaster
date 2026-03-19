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
### [5. Fáze Odinstalace](./files/technicka_analyza_detail.md#5-odinstalace)

## Základní stavební kameny addonu - paradigmata
TODO
### Operátory
### Uživatelské rozhraní
### Vlastnosti a data

## Teorie grafů a topologická reprezentace prostorových uspořádání
- základním kamenem by měla být schopnost softwaru porozumět prostorovým vztahům mezi jednotlivými vkládanými elementy
- půdorys je z hlediska lidské percepce souborem ploch tvořící pokoje a chodby
- z hlediska výpočetní geometrie a informatiky je složitou topologickou sítí, kterou lze nejlépe abstrahovat, reprezentovat a analyzovat pomocí teorie grafů
### [Aplikace grafů při strukturální analýze půdorysů](./files/technicka_analyza_detail.md#aplikace-grafů-při-strukturální-analýze-půdorysů)

## Návrh implementace jednotlivých požadavků:
TODO
### FP1 Pencil Tool

### FP2 Generování a úprava parametrických objektů

### FP3 správa prostoru a metadat

### FP4 Finalizační nástroj

### FP5 Kontextová nabídka

### FP6 Interaktivní 3D manipulátory

### NP1 Architektura a technologie

### NP2 Výkon a Nedestruktivnost

### NP3 Použitelnost a UX

### NP4 Automatické kótování