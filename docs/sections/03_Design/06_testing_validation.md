# 3.6 Testování a validace návrhu

Předchozí kapitoly 3.1–3.5 definovaly MVP scope, architekturu, datový model, funkce a uživatelské rozhraní. Před zahájením implementace je nezbytné provést důkladnou kontrolu celého návrhu — ověřit, že architektura, datové toky a funkce společně spolehlivě pokrývají zadání z MVP scope (kapitola 3.1) a neobsahují logické mezery. Tato kapitola plní roli kontroly návrhu prostřednictvím kontrolních seznamů, teoretických průchodů scénáři a analýzy okrajových případů.

## [Pokrytí požadavků](./06_testing_validation_requirements.md)

## [Průchod scénáři použití](./06_testing_validation_walkthroughs.md)

## [Analýza okrajových případů](./06_testing_validation_edge_cases.md)

## Kontrolní tabulka: scénáře × požadavky

Ověření, že každý scénář použití z analýzy (kapitola 2.4) je pokryt alespoň jedním FP a že každý FP má svůj scénář.

| | UC 1.1 | UC 1.2 | UC 2.1 | UC 2.2 | UC 3.1 | UC 3.2 | UC 1.3 | UC 2.3 | UC 3.3 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FP1 | | ✅ | ✅ | | ✅ | | | | |
| FP2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | | | |
| FP3 | ✅ | ✅ | ✅ | | ✅ | ✅ | | | |
| FP4 | | | | ✅ | | ✅ | | | |
| FP5 | | | | | | | | ✅ | |
| FP6 | | | | | | | | | ✅ |
| FP7 | | | | | | | ✅ | | |

Závěr: Každý must-have FP (FP1–FP4) je pokryt minimálně jedním scénářem a každý must-have scénář (UC 1.1–3.2) je plně průchozí v rámci MVP. Should-have FP (FP5–FP7) mají každý svůj dedikovaný scénář (UC 1.3, 2.3, 3.3); tyto scénáře **nejsou průchozí v MVP** — závisejí na implementaci příslušného should-have prvku, ale architektura a datový model pro ně jsou připraveny od MVP.
