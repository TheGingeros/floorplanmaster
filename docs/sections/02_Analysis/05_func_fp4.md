# FP4 - Finalizační nástroj
Finalizační nástroj uzavírá nedestruktivní životní cyklus modelu. Po dokončení návrhu převede parametrický systém do statické mesh geometrie připravené pro UV mapování, export do herního enginu nebo zařazení do renderovací pipeline.
## Základ požadavku - must have:
- **Aplikace použitých modifikátorů a finalizace** - jakmile je návrh hotový, uživatel potřebuje z tohoto parametrického systému vytvořit obyčejný 3D model pro další zpracování, např. UV mapování nebo export do herního enginu, systém projde vybrané objekty a postupně trvale aplikovat všechny generátory