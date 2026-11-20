---
erzeugt: 9568e52b23b3
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/uebersetzt.py
> das Uebersetzte fuer den naechsten Start.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/uebersetzt.py)

## WOZU

Beim Einbinden uebersetzt Python jede Quelldatei in Bytecode, und in Pyodide
ist das rund die Haelfte des Einlesens. Von sich aus haelt Pyodide das
Uebersetzte nicht fest (`sys.dont_write_bytecode`). Der Faden der Seite
(`web/js/kern_arbeiter.js`) laesst Python die `.pyc`-Dateien schreiben,
packt sie einige Sekunden nach dem Start mit [[opencivil.web.uebersetzt#packen|packen]] in ein Stueck und
legt es in einen Speicher des Browsers. Beim naechsten Besuch setzt
[[opencivil.web.uebersetzt#einsetzen|einsetzen]] sie vor dem Einbinden wieder an ihren Ort, und Python
uebersetzt nur noch, was fehlt.

Mitliefern ginge nicht: Bytecode gilt nur fuer seine Fassung von Python, und
die im Browser ist eine andere als die auf dem Rechner. So uebersetzt
Pyodide selbst, einmal je Stand der Quellen.


## AM INHALT GEPRUEFT

Ob ein `.pyc` noch zu seiner Quelle passt, prueft Python sonst an deren
Zeit und Groesse. Die Zeit hilft hier nicht -- jeder Start legt die Quellen
neu an --, und auf die Groesse allein ist kein Verlass: eine geaenderte
Ziffer laesst sie gleich, und still liefe der alte Code. Darum legt
[[opencivil.web.uebersetzt#packen|packen]] jedes `.pyc` als eines ab, das Python am Inhalt der Quelle
prueft (hash-basiert, PEP 552): beim Einbinden vergleicht es diesen mit dem,
aus dem uebersetzt wurde, und uebersetzt neu, wenn er abweicht. Ins Stueck
kommt nur, was zu den Quellen von jetzt passt.

## Inhalt

### einsetzen

```python
def einsetzen(stueck: str | os.PathLike, wurzel: str | os.PathLike) -> int
```

Setzt die `.pyc`-Dateien aus `stueck` an ihren Ort unter `wurzel`
und gibt zurueck, wie viele es waren.

Ob eines gilt, prueft Python beim Einbinden selbst, am Inhalt seiner
Quelle; ein veraltetes uebersetzt es neu.

### packen

```python
def packen(stueck: str | os.PathLike, wurzel: str | os.PathLike) -> bool
```

Schreibt jedes `.pyc` unter `wurzel`, das zu seiner Quelle passt, in
ein Stueck nach `stueck` -- jedes am Inhalt der Quelle geprueft.

Gibt zurueck, ob das Stueck neu ist. Liegt dort schon dasselbe, etwa weil
es so eingesetzt wurde und nichts neu zu uebersetzen war, bleibt es
liegen: dann gibt es nichts abzulegen.

### _am_inhalt_geprueft

```python
def _am_inhalt_geprueft(pyc: Path) -> Optional[bytes]
```

Das `.pyc` mit einem Kopf, der Python am Inhalt der Quelle pruefen
laesst -- oder `None`, wenn es nicht zu ihr passt, sie fehlt oder es
fuer eine andere Fassung von Python uebersetzt ist.

### _zeit_und_groesse

```python
def _zeit_und_groesse(stand: os.stat_result) -> bytes
```

Was ein an der Zeit gepruefter Kopf von der Quelle festhaelt: Sekunde und Groesse, je 4 Byte.


## Konstanten

- `AM_INHALT = 3` – Kennzeichen im Kopf eines `.pyc`: hash-basiert (Bit 0) und an der Quelle geprueft (Bit 1), PEP 552.
