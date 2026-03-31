# Pravidla validace parametrů
Tato závěrečná sekce specifikuje bezpečnostní pojistky (guardrails) celého datového modelu. I když čistě matematické grafy ve Vrstvě 1 a 2 teoreticky snesou záporné hodnoty nebo nulové vzdálenosti, fyzický 3D svět a algoritmy Geometry Nodes by na takových datech selhaly (např. stěny se zápornou tloušťkou by vytvořily převrácené normály, nulové plochy by způsobily dělení nulou). Tato validační pravidla slouží jako první obranná linie a aplikují se v Controlleru ještě předtím, než jsou data vůbec zapsána do datových modelů.

## Parametry stěny
Tyto limity definují fyzikální a konstrukční mantinely stěn. Zabraňují vzniku degenerované geometrie, jako jsou nekonečně tenké "papírové" stěny, které by způsobovaly vizuální artefakty (Z-fighting) a problémy při navazování rohů.

```
thickness: 0.05 ≤ value ≤ 1.0 (metry)
height: 1.0 ≤ value ≤ 10.0 (metry)
angle: 0° ≤ value ≤ 180°
offset: -0.5 ≤ value ≤ 0.5 (metry)
```

## Parametry místnosti
U místností nehlídáme jen matematickou existenci uzavřeného polygonu, ale především jeho sémantický smysl. Extrémně malé plochy (pod 1 m²) nebo absurdní poměry stran (např. 10 cm široká, ale 10 metrů dlouhá štěrbina) většinou neindikují skutečnou místnost, ale spíše topologickou chybu – typicky drobnou nedokonalost při kreslení, kdy uživatel nepřesně napojil dvě zdi. Tyto limity filtrují topologický „šum“.

```
area: > 1.0 (m²)  # Minimální místnost 1 m²
height: > 0
perimeter: > 4.0 (alespoň 2x2 čtverec)
aspect_ratio: 0.1 ≤ (width/length) ≤ 10.0  # Rozumné tvary
```

## Převod jednotek
Zlaté architektonické pravidlo tohoto addonu zní: **Veškeré interní výpočty v Pythonu (Vrstva 1 a 2) i serializovaná data v Blender síti (Vrstva 3) jsou vždy uchovávány striktně v metrech.** Tím se předchází matematickým chybám při zaokrouhlování. Systém převodu jednotek se aplikuje výhradně na prezentační vrstvě (UI) – tedy při zobrazování čísel uživateli a při parsování jeho vstupů z textových polí.

```python
UNIT_CONVERSIONS = {
    "m": 1.0,        # Metry (základní interní jednotka)
    "cm": 0.01,
    "mm": 0.001,
    "ft": 0.3048,
    "in": 0.0254,
}

# Příklad: Převést 3m na stopy (pouze pro zobrazení v UI)
value_in_m = 3.0
value_in_ft = value_in_m / UNIT_CONVERSIONS["ft"]  # ~9.84 ft
```