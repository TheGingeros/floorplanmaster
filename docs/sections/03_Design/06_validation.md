# 3.6 Validace a chybové stavy

Datový model (3.2) definoval povolené rozsahy atributů a návrh funkcí (3.3) popsal, které operace data mění. Tato sekce specifikuje, jak validace probíhá za běhu — kde se detekuje, jak se propaguje ke View a jak se systém vypořádá s nekonzistentními daty.

Validace probíhá na hranici mezi Controllerem a Modelem — Controller předá uživatelský vstup, Model provede validaci a vrátí výsledek. View (GPU overlay a N-panel) výsledek zobrazí. Žádná vrstva neprovádí validaci za jinou.

## Typy chyb

| Kód | Popis | Vrstva detekce | Reakce |
| :--- | :--- | :--- | :--- |
| `E_WALL_TOO_SHORT` | Délka navrhované stěny je pod minimem (< 0,05 m) | Vrstva 1 | Potvrzení zablokováno, HUD zobrazí varování |
| `E_WALL_DUPLICATE` | Stěna mezi dvěma junctiony již existuje | Vrstva 1 | Potvrzení zablokováno, existující stěna zvýrazněna |
| `E_OPENING_TOO_LARGE` | Otvor (okno/dveře) je větší než délka hostitelské stěny | Vrstva 1 | Operace odmítnuta, chybová zpráva v N-panelu |
| `E_OPENING_OVERLAP` | Dva otvory na stejné stěně se překrývají | Vrstva 1 | Operace odmítnuta, oba otvory zvýrazněny |
| `E_NO_ACTIVE_FLOORPLAN` | Operace vyžaduje aktivní objekt půdorysu, žádný není vybrán | Controller | Operátor se nespustí, zpráva v status baru |
| `E_FINALIZE_EMPTY` | Finalizace spuštěna na prázdném půdorysu (žádné stěny) | Vrstva 1 | Dialog varuje, operace vyžaduje potvrzení |
| `E_SYNC_MISMATCH` | Pojmenované atributy jsou nekonzistentní s grafem (detekováno při načtení) | Vrstva 3 | Automatická resynchronizace; pokud selže, varování v konzoli |

## Feedback uživateli

Addon komunikuje chybové stavy třemi kanály podle závažnosti:

- **HUD overlay** (GPU draw_handler) — okamžitá vizuální zpětná vazba při kreslení; zobrazuje varování přímo u kurzoru pro chyby `E_WALL_TOO_SHORT` a `E_WALL_DUPLICATE`
- **N-panel** — trvalý stav; chyby parametrů otvorů (`E_OPENING_TOO_LARGE`, `E_OPENING_OVERLAP`) se zobrazí jako červeně podbarvené pole s textovým popisem
- **Blender status bar** — jednořádkové hlášení pro chyby operátoru (`E_NO_ACTIVE_FLOORPLAN`); standardní konvence Blenderu

## Validace při načtení souboru

Při otevření `.blend` souboru s existujícím půdorysem addon ověří konzistenci dat (Vrstva 3 ↔ Vrstva 1/2). Pokud jsou data konzistentní, addon je tiše načte. Pokud je detekována nekonzistence (`E_SYNC_MISMATCH`), provede se automatická resynchronizace na základě pojmenovaných atributů jako autoritativního zdroje — graf se rekonstruuje.
