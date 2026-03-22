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

## Možnosti a limity Blender API

## Reprezentace geometrie a topologie

## Ukládání dat a správa metadat

## Návrh uživatelského rozhraní a interakce

## Finalizační nástroj

## Architektura samotného kódu

## Návrh implementace jednotlivých požadavků:
TODO
### FP1 Pencil Tool

### FP2 Generování a úprava parametrických objektů

### FP3 správa prostoru a metadat

### FP4 Finalizační nástroj

### FP5 Kontextová nabídka

### FP6 Interaktivní 3D manipulátory

### FP7 Automatické kótování

### NP1 Architektura a technologie

### NP2 Výkon a Nedestruktivnost

### NP3 Použitelnost a UX