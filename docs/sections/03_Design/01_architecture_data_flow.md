# Tok dat: Základní operace
Zatímco předchozí kapitoly definovaly statickou strukturu systému, tato sekce ukazuje architekturu FloorPlanMaster v pohybu. Představuje přesný chronologický tok dat během tří nejčastějších uživatelských interakcí a ilustruje, jak se teoretický vzor MVC a třívrstvý datový model propisují do plynulého uživatelského zážitku.

Každá z těchto operací využívá architekturu jiným způsobem. Při kreslení půdorysu (změna topologie) vykonává systém nejkomplexnější kaskádu kroků: modální operátor řídí dočasný GPU náhled a postupně buduje strukturální graf, což automaticky spouští detekci nových místností a generování fyzické BMesh sítě. Naopak úprava vlastností (např. změna tloušťky stěny) je extrémně lehká operace – nemění základní síť, pouze aktualizuje číselné hodnoty v grafech a serializuje je do pojmenovaných atributů pro překreslení přes Geometry Nodes. Celý tento nedestruktivní ekosystém pak uzavírá proces finalizace, který na vyžádání uživatele odstřihne dynamické vazby a trvale zapeče vygenerovanou geometrii do standardních 3D objektů připravených pro export či render.

## 1. Kreslení půdorysu (FP1 - Nástroj Tužka)

```
Uživatel aktivuje nástroj Tužka (modální operátor)
            ↓
Modální vstup do stavu DRAWING (čeká na vstup)
            ↓
Uživatel klikne na bod 1 (vytvoření propojovacího bodu)
  • Operátor ověří pozici (přichycování, mřížka)
  • Zjistí aktuálně aktivní podlaží (Model budovy)
  • Vrstva 1 (aktivního podlaží): Přidá uzel do strukturálního grafu
  • Vrstva 3 (BMesh): Vytvoří reálný vrchol (vertex) v základní síti Blenderu
  • Vrstva 3 (Atributy): Zapíše/aktualizuje pojmenované atributy na tomto vrcholu
            ↓
Uživatel pohne myší (generování náhledu)
  • Modální je ve stavu DRAWING
  • Vypočítá geometrii náhledu stěny
  • Vykreslí náhled přes modul GPU
            ↓
Uživatel klikne na bod 2 (potvrzení stěny)
  • Modální ověří stěnu (délka, úhly)
  • Vrstva 1 (aktivního podlaží): Přidá hranu do strukturálního grafu
  • Vrstva 3 (BMesh): Vytvoří reálnou hranu v základní síti Blenderu spojující dané vrcholy
  • Vrstva 3 (Atributy): Zapíše pojmenované atributy na tuto hranu (např. `wall_id`, `wall_thickness`)
  • NetworkX detekuje nové cykly
            ↓
Vrstva 2 AUTOMATICKÁ AKTUALIZACE: Graf místností aktualizován
  • Detekce cyklů identifikuje nové místnosti
  • Přiřadí perzistentní ID místností
  • Vypočítá plochu, sousedství
            ↓
Vrstva 3: Serializace do pojmenovaných atributů
  • Aktualizuje atributy sítě
  • Geometry Nodes spustí obnovení
            ↓
Pohled se aktualizuje s 3D geometrií
            ↓
Opakování nebo stisk Enter/ESC pro ukončení
```

## 2. Úprava vlastností místnosti

```
Uživatel otevře panel Vlastnosti
            ↓
Vybere místnost ze seznamu nebo klikne na místnost v 3D
            ↓
Upraví parametr (např. tloušťka stěny, barva)
            ↓
Vrstva 1 nebo 2: Aktualizuje data grafu
            ↓
Vrstva 3: Serializuje atribut do pojmenovaných atributů
            ↓
Driver Geometry Nodes se aktualizuje
            ↓
Pohled se znovu vykreslí s novým parametrem
(ID místnosti nezměněno → nedestruktivní úprava)
```

## 3. Finalizace (FP4 - Převod na trvalou geometrii)

```
Uživatel klikne na tlačítko "Finalizace"
            ↓
Operátor čte pojmenované atributy
            ↓
Geometry Nodes zapečou výstup do sítě
            ↓
Volitelné: Vytvoří jednotlivé objekty místností
            ↓
Volitelné: Sloučí do jednoho objektu
            ↓
Volitelné: Uloží do souboru (Blender .blend soubor obsahuje všechny vrstvy)
```