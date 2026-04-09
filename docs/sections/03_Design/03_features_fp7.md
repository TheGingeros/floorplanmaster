# FP7 — Automatické kótování
Technická analýza ([porovnání přístupů k vykreslování kótovacího textu](../../02_Analysis/06_ta_ui_gpu.md#porovnání-přístupů-k-vykreslování-kótovacího-textu)) identifikovala **GPU draw_handler + BLF** jako jedinou variantu zaručující čitelnost textu nezávisle na úhlu kamery. Vizuální podoba kótování — barvy, font, přepínač viditelnosti — je součástí návrhu UI (kapitola 3.4).

## Datový pipeline *(must-have)*

Kótování čte data výhradně z Vrstvy 1 a Vrstvy 2 — do geometrie scény ani do GN modifikátoru nevstupuje a není součástí finalizované sítě (FP4).

**Délky stěn**
- Pro každou hranu Vrstvy 1: Euklidovská vzdálenost mezi souřadnicemi junctionů
- Pozice textu: střed hrany transformovaný do 2D souřadnic obrazovky (`view3d_utils`)
- Hodnota zobrazena v nastaveném systému jednotek (metrický / imperiální)

**Metriky místností**
- Plocha (`room_area`) a název místnosti čteny z uzlu Vrstvy 2
- Pozice textu: centroid místnosti transformovaný do 2D souřadnic obrazovky
- Aktualizace nastane při každé změně topologie Vrstvy 1 (přepočet centroidu)

## Implementace draw_handleru *(must-have)*

Draw_handler je registrován na `SpaceView3D` v režimu `POST_PIXEL` (souřadnice obrazovky) — text se tak vykresluje jako 2D overlay bez závislosti na hloubce scény. Registrace a odregistrace jsou vázány na globální přepínač viditelnosti kótování; při odregistraci je handler okamžitě uvolněn z paměti, aby nedocházelo k hromadění handlerů po opakovaném přepnutí.
