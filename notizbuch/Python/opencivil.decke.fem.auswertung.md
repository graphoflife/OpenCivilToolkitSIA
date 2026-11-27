---
erzeugt: f3bb98788d81
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/auswertung.py
> die FEM an einer Stelle, längs eines Schnitts, im Träger.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/auswertung.py)

## VERANTWORTUNG

Was Bilder und Bericht von einem Fall der FEM lesen, in denselben Formen
wie bei der Streifenmethode ([[opencivil.decke.schnitt|schnitt]]): die Werte an
einer Stelle, den Verlauf längs eines Schnitts, Moment und Querkraft eines
Trägers und die Stellen, an denen die grössten Werte gesucht werden. Neu
gerechnet wird hier nichts: über ein Dreieck ist jede Grösse linear
zwischen den geglätteten Werten an seinen Ecken
([[opencivil.decke.fem.rechnung|rechnung]]), `v_0` der Betrag aus `v_x` und
`v_y` dort.


## DAS BILD DER PLATTE

Jedes Dreieck des Netzes ist eine Zelle ([[opencivil.decke.fem.auswertung#bild|bild]]). In ihrem
Schwerpunkt stehen die Werte dort, und ihr Gefälle ist das der Ebene durch
die Werte an ihren Ecken – dasselbe, was die Streifenmethode für eine
Zelle ausgleicht ([[opencivil.decke.feld#gefaelle|gefaelle]]): auf einem
Dreieck trifft die Ebene die Ecken genau, für `v_0` beinahe.


## LÄNGS EINES SCHNITTS

In jedem Dreieck, durch das er läuft, sieht der Verlauf an Eintritt und
Austritt hin, knapp innen ([[opencivil.decke.feld#Konstanten|INNEN]]): so
springt er, wo die Werte über eine Kante springen, und dazwischen ist er
genau – `v_0` hat dort, wo er gekrümmt ist, sein Grösstes an einem Ende.


## DER TRÄGER

Sein Moment und seine Querkraft über die ganze Breite `b`: was der Balken
trägt und was die Platte über die Breite trägt, `b` mal das Mittel von
`m_t` und `v_t` quer zu seiner Achse, in seiner Richtung `t`
(Entscheid 10 des Plans vom 2026-11-27). So hat auch ein Träger ohne Höhe
seine Schnittkräfte: dann trägt nur die Platte. Quer wird an [[opencivil.decke.fem.auswertung#Konstanten|QUER]]
gleich verteilten Stellen gemittelt, längs an beiden Enden jedes Stücks
und in seiner Mitte.

## Inhalt

### gemischt

```python
def gemischt(ecken: Sequence[Femwerte], anteile: Sequence[float]) -> Femwerte
```

Die Werte an einer Stelle eines Dreiecks aus denen an seinen Ecken, mit ihren Schwerpunktkoordinaten.

### an_stelle

```python
def an_stelle(ergebnis: Femergebnis, fall: Femfall, p: Punkt) -> Femwerte
```

Die Werte an der Stelle `p` – neben den Platten null.

### proben

```python
def proben(ergebnis: Femergebnis, fall: Femfall) -> List[Tuple[Punkt, Femwerte]]
```

Wo Bild und Bericht die grössten Werte suchen: an jedem Knoten je Sektor
– über ein Dreieck linear, liegen sie dort; `v_0` auch, denn der
Betrag ist am grössten an einer Ecke.

### bild

```python
def bild(ergebnis: Femergebnis, fall: Femfall) -> Bild
```

Je Dreieck des Netzes eine Zelle, mit den Werten in ihrem Schwerpunkt und ihrem Gefälle – gesucht wird an [[opencivil.decke.fem.auswertung#proben|proben]].

### verlauf

```python
def verlauf(ergebnis: Femergebnis, fall: Femfall, a: Punkt, b: Punkt) -> Verlauf
```

Der Verlauf längs des Schnitts von `a` nach `b` – ohne Länge leer.

### traeger

```python
def traeger(ergebnis: Femergebnis, fall: Femfall, u: Traeger) -> Verlauf
```

Moment und Querkraft des Trägers `u` über seine ganze Breite, längs
seiner Achse ab `a` – aus seinem Balken und der Platte daneben. Seine
Lager sind die Linienlager, die er kreuzt, und die Stützen auf ihm.


## Konstanten

- `QUER = 8` – An so vielen Stellen quer zum Träger wird die Platte gemittelt – gerade, damit keine auf der Achse liegt.
- `MITTE = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)` – Die Schwerpunktkoordinaten des Schwerpunkts.

## Braucht

- [[opencivil.decke.feld]]
- [[opencivil.decke.fem.belastung]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.schnitt]]

## Gebraucht von

- [[opencivil.decke.fem.herleitung]]
- [[opencivil.web.deckendaten]]
