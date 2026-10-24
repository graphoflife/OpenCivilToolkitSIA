---
erzeugt: 84888b6294ee
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/balkendaten.py
> was die Oberflaeche von einem Balkensystem zeigt.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/balkendaten.py)

## VERANTWORTUNG

Aus dem Befund eines gerechneten Systems
([[opencivil.stabwerk.rechnung#Systembefund|Systembefund]]) die Daten fuer die Oberflaeche, in den Einheiten der Anzeige -- kN, kNm, mm,
mrad, Stellen in m:

* mit jeder Rechnung eine knappe Uebersicht ([[opencivil.web.balkendaten#uebersicht|uebersicht]]): die
  Meldungen mit den Elementen, die sie betreffen, die Knoten ohne
  Drehsteifigkeit, und je Fall die Extremwerte und die Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder ([[opencivil.web.balkendaten#verlauf|verlauf]]):
  je Stab Proben von N, V, M und der Verschiebung, je Knoten seine
  Verschiebung -- oder dass seine Drehung nicht bestimmbar ist;
* je Querschnitt sein Umriss fuer das Bildchen in seiner Zeile
  ([[opencivil.web.balkendaten#umrisse|umrisse]]).

Die Verlaeufe sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch wenn niemand die Bilder ansieht -- dasselbe wie bei
den Diagrammen der Querschnittsanalyse. Gerechnet wird hier nichts, nur
umgerechnet und in Listen gelegt.

## Inhalt

### uebersicht

```python
def uebersicht(befund: Optional[Systembefund]) -> Dict[str, Any]
```

Was die Oberflaeche nach jeder Rechnung von einem System weiss -- ohne
die Verlaeufe. Ohne Befund lief es nicht, etwa weil ein Baustoff fehlt.

### verlauf

```python
def verlauf(befund: Systembefund, name: str) -> Dict[str, Any]
```

Die Bilder eines Falls: je Stab die Proben, je Knoten die Verschiebung.

### faelle

```python
def faelle(befund: Optional[Systembefund]) -> List[str]
```

Die Namen der gerechneten Faelle, Lastfaelle zuerst.

### umrisse

```python
def umrisse(system: Balkensystem, aufbau: Any, loesung: Any) -> Dict[str, List[List[List[float]]]]
```

Je Querschnitt eines Systems sein Umriss in mm, fuer das Bildchen in
seiner Zeile (Benutzer, 2026-10-24): die Vorlage mit ihren Massen, der
Streifen b × h einer Platte, die Polygone einer Analyse -- Aussparungen
mit, das Bild fuellt gerade-ungerade. Kennwerte von Hand haben keinen,
ebenso ein Querschnitt, der nicht geht oder dessen Werte fehlen.


## Konstanten

- `PROBEN_JE_STAB = 24` – Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.

## Braucht

- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
