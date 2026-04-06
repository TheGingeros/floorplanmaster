# FP4 — Finalizační nástroj
Technická analýza ([Finalizační nástroj](../../02_Analysis/06_ta_finalize_tool.md)) popisuje mechanismus Dependency Graphu, bezpečnou aplikaci GN modifikátorů, správu UV map a konsolidaci materiálových slotů. Tato sekce definuje návrhová rozhodnutí: co finalizační nástroj provede, jaké volby uživatel dostane a jak operace interaguje s datovým modelem.

Nástroj Finalizace provede nevratný převod parametrického modelu (grafy + Geometry Nodes) do statické polygonové sítě vhodné pro export, UV mapování nebo herní engine. Jde o jednosměrnou operaci — po finalizaci nelze parametricky upravovat původní datový model. Proto addon před zahájením vygeneruje krok Undo jako záchranný bod.

## Stavový automat

```mermaid
stateDiagram-v2
    [*] --> NEAKTIVNÍ
    NEAKTIVNÍ --> DIALOG : spuštění nástroje
    DIALOG --> BAKING : potvrzení voleb
    DIALOG --> NEAKTIVNÍ : zrušení
    BAKING --> HOTOVO : úspěšná finalizace
    BAKING --> CHYBA : selhání (invalid mesh)
    CHYBA --> NEAKTIVNÍ : zobrazení chybové zprávy
    HOTOVO --> [*]
```

## Možnosti finalizace

Uživatel před zahájením zvolí v dialogu:

| Volba | Popis |
| :--- | :--- |
| **Organizace výstupu** | Celý půdorys jako jeden objekt / samostatné objekty per místnost / separace stěny + podlahy + stropy |
| **Přiřazení materiálů** | Automaticky z metadat Vrstvy 2 (`floor_material_id`, `wall_material_id`) nebo ponechat výchozí Blender materiál |
| **Čistění atributů** | Odstranit pojmenované atributy z výsledné sítě (úspora dat pro export) |
| **Zachovat originál** | Duplikovat a finalizovat kopii vs. finalizovat přímo (destruktivní) |

## Interakce s datovým modelem

Pokud je zvolena možnost „zachovat originál", finalizace **nesmí** modifikovat Vrstvy 1 ani 2:

1. Aplikace GN modifikátoru → statická mesh vznikne z aktuálního stavu pojmenovaných atributů a GN stromu (přes `evaluated_get(depsgraph)`)
2. Přiřazení materiálů dle `material_id` atributů z Vrstvy 3
3. **Konverze UV atributů** — po aplikaci GN modifikátoru existují UV data jako pojmenované atributy na doméně Face Corner; musí být explicitně konvertovány na UV vrstvy (`MeshUVLoopLayer`), jinak je exportéry FBX a glTF ignorují (viz [technická analýza: Správa UV map](../../02_Analysis/06_ta_finalize_tool.md#správa-uv-map-a-atributů-v-procedurálním-potrubí))
4. **Konsolidace materiálových slotů** — Join Geometry v GN produkuje duplicitní materiálové sloty; před exportem se provede deduplikace: identické materiály sloučeny, indexy polygonů přemapovány, prázdné sloty odstraněny (viz [technická analýza: Správa materiálových slotů](../../02_Analysis/06_ta_finalize_tool.md#správa-materiálových-slotů-a-konsolidace-geometrie))
5. Volitelné odstranění pojmenovaných atributů z výsledné sítě
6. Generování kroku Undo (záchranný bod před nevratnou operací)
