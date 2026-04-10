# FP5 - Kontextová nabídka
Kontextová nabídka zpřístupňuje akce specifické pro kliknutý prvek prostřednictvím plovoucí overlay vrstvy, která se zobrazí přímo u kurzoru. Addon využívá raycast k identifikaci cílového prvku a pomocí GPU nebo BLF modulů vykresluje vlastní UI vrstu překrývající 3D viewport.
## Základ požadavku - should have:
- po kliknutí na určitý objekt/prvek se přímo na daném místě na obrazovce objeví malá plovoucí nabídka s akcemi
- addon musí zachytávat události myši, provést raycast a zjistit, na jakou část objektu uživatel kliknul
- pomocí modulu gpu nebo blf nakreslit a ovládat vlastní UI vrstu překrývající 3D viewport