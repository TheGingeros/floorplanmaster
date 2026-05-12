#import "@preview/treet:0.1.1": *


#set text(font: "DejaVu Sans Mono", size: 9pt)
#let dots() = box(width: 1fr, repeat[.])

#tree-list[
  - readme.txt #dots() Přehled obsahu archivu a pokyny k použití
  - src/ #dots() Kompletní zdrojový kód doplňku pro Blender
    - readme.md #dots() Instalace a návod k použití doplňku
  - typst/ #dots() Kompletní zdrojové soubory Typst této práce
    - main.pdf #dots() Finální text práce ve formátu PDF
]
