# FP7 - Automatické kótování
Kótovací overlay průběžně zobrazuje délky stěn a plochy místností jako dynamický text přímo ve viewportu bez nutnosti přepínat do jiného nástroje. Texty jsou generovány modulem BLF přes draw handler a aktualizují se v reálném čase při každé změně půdorysu.
## Základ požadavku - should have:
- **vizualizace rozměrů** - neustále ukazují velikost, aniž by se musela překreslovat
- generování dynamických textů přes modul blf přímo do viewportu přes draw_handler
