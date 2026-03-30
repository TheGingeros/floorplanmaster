# Principy návrhu
Vývoj robustního nástroje pro Blender vyžaduje více než jen funkční kód; vyžaduje jasně definovanou architektonickou filozofii. Návrh FloorPlanMaster stojí na pěti základních pilířích, které zajišťují, že systém zůstane stabilní, snadno udržovatelný a uživatelsky responzivní i při zpracování velmi komplexních půdorysů.

Základním stavebním kamenem je striktní oddělení zájmů a modularita. Izolace matematického jádra od 3D prostředí nejen zpřehledňuje kód, ale umožňuje bleskové nezávislé testování a snadné přidávání nových funkcí. Z pohledu koncového uživatele je pak absolutní prioritou nedestruktivní workflow a okamžitá vizuální odezva. Toho je dosaženo chytrým rozložením zátěže mezi rychlé GPU vykreslování pro dočasné náhledy a výkonné Geometry Nodes pro stabilní geometrii. Celý tento moderní přístup je navíc plně podřízen nativním standardům a osvědčeným postupům Blenderu, což zaručuje, že se addon chová jako přirozená součást ekosystému, včetně bezchybné podpory historie kroků (Undo/Redo).

## 1. Oddělení zájmů
   - Logika grafu (vrstvy 1, 2) nezávislá na Blenderu/GN (vrstva 3)
   - Operátory fungují jako tenké řadiče, ne složitá logika
   - Utility jsou bezstavové a opakovaně použitelné

## 2. Nedestruktivní úpravy
   - Identity místností/stěn přetrvávají přes změny parametrů
   - Undo/Redo podporováno přes systém operátorů Blenderu
   - Parametry lze upravovat nekonečně

## 3. Zpětná vazba v reálném čase
   - Náhled během kreslení (modul GPU)
   - Živé aktualizace při změně vlastností (GN drivers)
   - Responzivní UX i se složitými dispozicemi

## 4. Modularita
   - Každá vrstva se dá testovat nezávisle
   - Operace grafu nepotřebují kontext Blenderu
   - Snadné přidávání nových funkcí (okna, dveře, poznámky)

## 5. Osvědčené postupy Blenderu
   - Dodržujte konvence pojmenování Blenderu
   - Používejte modální operátory pro interaktivní nástroje
   - Využívejte Geometry Nodes pro nedestruktivní geometrii
   - Správná podpora undo/redo