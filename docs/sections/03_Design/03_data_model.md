# 3.3 Datový model
Architektura (kapitola 3.2) definuje třívrstvou hybridní architekturu a tok dat mezi vrstvami. Tato sekce přibližuje pohled na úroveň samotných dat — exaktně definuje strukturu datových entit (uzly, hrany, plochy), jejich parametry (unikátní ID, tloušťka, výška, materiál, obvod, plocha) a validační pravidla. Zatímco předchozí kapitola řešila vrstvy a toky, tato část specifikuje strukturu "balíčků" informací, které těmito vrstvami protékají.

Datový model operuje na úrovni jednoho podlaží. Vrstva 1 uchovává topologii stěn a propojovacích bodů, Vrstva 2 z ní odvozuje sémantiku místností a vztahů sousedství. Vrstva 3 přenáší data obou grafů do Blender mesh ve formě pojmenovaných atributů, kde je Geometry Nodes čtou a vizualizují.

## [Vrstva 1: Strukturální graf](./03_data_model_layer1.md)
## [Vrstva 2: Graf místností](./03_data_model_layer2.md)

## [Vrstva 3: Atributový bridge](./03_data_model_layer3.md)

## [Vztah mezi vrstvami](./03_data_model_relations.md)

## Validační pravidla
Validace se aplikuje před zápisem dat do datových modelů. Zabraňuje vzniku degenerované geometrie, která by způsobila vizuální artefakty nebo selhání algoritmů.

- **Parametry stěny**:
    - tloušťka: $0{,}05 \leq t \leq 1{,}0$ m — příliš tenké stěny způsobují Z-fighting, příliš tlusté nemají architektonický smysl
    - výška: $1{,}0 \leq h \leq 10{,}0$ m
    - úhel napojení: $0° < \alpha \leq 180°$
- **Parametry místnosti**:
    - minimální plocha: $> 1{,}0\, m^2$ — menší prostory typicky indikují chybu v kreslení, ne reálnou místnost
    - poměr stran: $0{,}1 \leq \frac{šířka}{délka} \leq 10{,}0$ — filtruje topologický „šum" (úzké štěrbiny)
    - minimálně 3 vrcholy (trojúhelník)
- **Jednotky**: veškeré interní výpočty v Pythonu i serializovaná data ve Vrstvě 3 jsou vždy v metrech; převod jednotek se aplikuje výhradně na prezentační vrstvě (UI) při zobrazování uživateli a parsování vstupů
