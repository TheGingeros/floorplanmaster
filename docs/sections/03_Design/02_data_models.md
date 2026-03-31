# 3.2 Specifikace datových modelů
Zatímco předchozí kapitola definovala procesy a tok dat (architekturu MVC), tato sekce představuje exaktní „slovník“ celého addonu. Definuje fyzické struktury, pravidla a hranice, ve kterých se data mohou pohybovat. Slouží jako striktní programátorský kontrakt mezi matematickým jádrem v Pythonu a 3D prostředím Blenderu.

Abychom předešli zhroucení planárních algoritmů při navrhování komplexních objektů, neukládají se data do jedné ploché struktury, ale podléhají přísné hierarchii podlaží. Na samém vrcholu stojí zastřešující model Budovy (Správce podlaží), který izoluje jednotlivá patra do zcela nezávislých 2D vesmírů. Teprve uvnitř těchto pater žijí naše tři známé vrstvy: Strukturální graf uchovávající 2D topologii (Vrstva 1), Graf místností definující sémantiku a sousedství (Vrstva 2) a Pojmenované atributy sloužící jako optimalizovaný číselný most pro grafickou kartu (Vrstva 3).

Následující specifikace neslouží jen jako přehled proměnných. Detailně definuje povolené datové typy, API metody, a především tvrdá validační omezení, která garantují, že uživatel nemůže vytvořit architektonicky neplatný stav.

## [Hierarchie budovy (Zastřešující modely)](./02_data_models_building.md)
- Model budovy
- Model podlaží

## [Vrstva 1: Strukturální graf - Detailní specifikace](./02_data_modes_layer_1.md)
- Model uzlu propojovacího bodu
- Model hrany stěny
- Operace strukturálního grafu

## [Vrstva 2: Graf místností - Detailní specifikace](./02_data_models_layer_2.md)
- Model uzlu místnosti
- Model hrany sousedství
- Operace grafu místností

## [Vztah mezi vrstvou 1 a 2](./02_data_models_layers12.md)
- Mapování
- Pravidla synchronizace

## [Vrstva 3: Pojmenované atributy - Kompletní specifikace](./02_data_models_layer_3.md)

- Tabulka atributů
- Formát serializace
- Časování synchronizace

## [Pravidla validace parametrů](./02_data_models_rules.md)

- Parametry stěny
- Parametry místnosti
- Převod jednotek