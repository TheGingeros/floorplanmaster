# Shrnutí sezení — FloorPlanMaster návrh (kapitola 3), část 2

**Datum:** 6. dubna 2026

---

## Přehled

Sezení navázalo na předchozí shrnutí (`session_summary.md`). Hlavní téma: přestavba struktury kapitoly 3 (Návrh) — odstranění nevhodných sekcí a nahrazení smysluplným obsahem v souladu se zavedennými pravidly.

---

## Dokončené úkoly

### Rozhodnutí o 3.5 „Nefunkční požadavky v návrhu" — ✅

- Zjištění: stavové automaty pro FP1 (modální operátor) a FP4 (finalizace) jsou již kompletně popsány v příslušných FP souborech — samostatná sekce je redundantní.
- Rozhodnutí: celou sekci 3.5 vymazat i se všemi přidruženými soubory (`05_state_management.md`, `05_nonfunc_np1.md`, `05_nonfunc_np2.md`, `05_nonfunc_np3.md`).

### Rozhodnutí o 3.7 „API rozhraní a třídy" — ✅

- Zjištění: `06_api_interfaces.md` obsahoval kompletní Python třídy s implementačními těly metod (kód uvnitř `add_junction`, `remove_junction`, atd.) — jde o API dokumentaci / implementaci, nikoli návrh.
- Vše relevantní na návrhové úrovni je již pokryto v 3.1 (názvy tříd, odpovědnosti), 3.2 (datový model) a 3.3 (které metody se volají kdy).
- Rozhodnutí: sekci 3.7 vymazat.

### Nová struktura kapitoly 3 — ✅

| Sekce | Soubor | Stav |
| :--- | :--- | :--- |
| 3.1 Architektura systému | `01_architecture.md` | Existující |
| 3.2 Datový model | `02_data_model.md` | Existující |
| 3.3 Návrh funkcí | `03_features.md` | Existující |
| 3.4 Uživatelské rozhraní | `04_ui_ux.md` | Existující |
| 3.5 MVP scope a rozšiřitelnost | `05_extensibility.md` | **Nový** |
| 3.6 Validace a chybové stavy | `06_validation.md` | **Nový** |

### Obsah nových souborů

**`05_extensibility.md` — MVP scope a rozšiřitelnost:**
- Tabulka záměrně vyloučených funkcí z MVP (více podlaží, DXF import, střechy, BIM export)
- 4 směry rozšiřitelnosti architektury (více podlaží, nové typy prvků, alternativní export, nové nástroje kreslení)
- Každý bod vysvětluje, proč architektura rozšíření umožňuje bez přepsání jádra

**`06_validation.md` — Validace a chybové stavy:**
- 7 definovaných chybových kódů (`E_WALL_TOO_SHORT`, `E_WALL_DUPLICATE`, `E_OPENING_TOO_LARGE`, `E_OPENING_OVERLAP`, `E_NO_ACTIVE_FLOORPLAN`, `E_FINALIZE_EMPTY`, `E_SYNC_MISMATCH`)
- Každý kód má: popis, vrstvu detekce, reakci systému
- 3 feedback kanály podle závažnosti: HUD overlay, N-panel, Blender status bar
- Validace při načtení souboru (resynchronizace z pojmenovaných atributů jako autoritativního zdroje)

---

## Smazané soubory

| Soubor | Důvod |
| :--- | :--- |
| `05_state_management.md` | Redundantní — stavy jsou v FP1 a FP4 |
| `05_nonfunc_np1.md` | Odstraněna celá sekce NP traceability |
| `05_nonfunc_np2.md` | Odstraněna celá sekce NP traceability |
| `05_nonfunc_np3.md` | Odstraněna celá sekce NP traceability |
| `06_api_interfaces.md` | Implementační kód, nepatří do návrhu |

---

## Upravené soubory

| Soubor | Co se změnilo |
| :--- | :--- |
| `docs/03_design.md` | Nová struktura 3.1–3.6; opraven odkaz `06_api.md` → `06_api_interfaces.md` (a poté odstraněn) |

---

## Zavedená pravidla (platí z předchozí sezení, potvrzena)

| Pravidlo | Popis |
| :--- | :--- |
| Max 2 úrovně nadpisů | Pouze `#` a `##` v jednom souboru |
| Žádné implementační detaily v návrhu | Žádné Python třídy s kódem, žádné method bodies, žádné signatury |
| Srovnání patří do TA | Návrhový soubor pouze konstatuje zvolenou strategii + odkaz na TA |
| Stavové automaty v FP souborech | Stav operátoru patří do příslušného FP souboru, ne do samostatné sekce |
| API dokumentace patří do implementace | Referenční dokumentace tříd a metod nepatří do kapitoly Návrh |
