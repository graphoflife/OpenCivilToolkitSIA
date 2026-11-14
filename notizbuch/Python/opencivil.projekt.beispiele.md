---
erzeugt: c4222148d40f
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/beispiele.py
> die Prüfprojekte: das Beispiel und «Jeder Nachweis».
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/beispiele.py)

## VERANTWORTUNG

Das Beispiel, mit dem die Oberflaeche startet ([[opencivil.projekt.beispiele#beispiel|beispiel]]), und das
Pruefprojekt, das jeden Nachweis einmal laut fuehrt ([[opencivil.projekt.beispiele#jeder_nachweis|jeder_nachweis]]).
Beide sind ueber die Fassade des Projekts gebaut, wie ein Benutzer es in
Python taete; aus ihnen stammen der Schnappschuss des Berichts und die
Formelsammlung. [[opencivil.projekt.projekt#Projekt|Projekt.beispiel <opencivil.projekt.projekt.Projekt.beispiel>]]
und [[opencivil.projekt.projekt#Projekt|Projekt.jeder_nachweis <opencivil.projekt.projekt.Projekt.jeder_nachweis>]]
fuehren hierher. Bis 2026-11-10 standen sie in der Klasse des Projekts, die
damit fast neunhundert Zeilen hatte.

## Inhalt

### beispiel

```python
def beispiel() -> Projekt
```

Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet.

Gebaut über dieselben Methoden, die man ohne Oberfläche benutzt. So
steht die Fassade an einer Stelle vorgeführt -- und der
Schnappschuss-Test prüft sie mit: baute sie etwas anderes als die
Einträge von Hand, die hier vorher standen, änderte sich der Bericht.

### jeder_nachweis

```python
def jeder_nachweis() -> Projekt
```

Jeder Nachweis einmal laut -- und die Fälle, die das Beispiel nie zeigt.

Zusammen mit [[opencivil.projekt.beispiele#beispiel|beispiel]] führt es jeden Nachweis einmal laut; ein
Test wacht darüber. Aus den beiden stammen der Schnappschuss des
Berichts und die Formelsammlung der Oberfläche -- darum steht es hier
und nicht bei den Tests.

Erhöhte Anforderung mit allen Schaltern und begrenzter rissaktiver
Dicke, häufige und quasi-ständige Lastfälle abgeleitet und eigene, Bügel
mit Stabzahl in y, ein Knickfall, die Verformung im Feld und am
Kragarm; eine zweite Platte mit x aussen und b = 500 mm, die im Feld
nicht aufgeht, auch nicht in der Durchbiegung, und deren Stahl unter
Dauerlast fliesst, dazu Querkraft ohne Bügel -- einmal über m_Rd,
einmal darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
gemessen wird, und ⌀40 in y unter der x-Bewehrung -- die fliesst bei
x = h/2 nicht. Gebaut über die Fassade, wie ein Benutzer es in Python
täte.

### _decken

```python
def _decken(p: Projekt) -> None
```

Zwei Decken. Die des Kolloquiums 4 (Stahlbeton II): eine Platte auf
einer Wand und drei Stützen, versteckte Unterzüge in zwei Stufen, fest
30 % in x, und als einziger Lastfall q_d = 18.6 kN/m² auf der ganzen
Platte, das Eigengewicht darin. Und eine, die jede Wahl einmal braucht:
zwei Platten verschiedener Dicke in einem L, automatisch aufgeteilt, mit
einer Zone, einer eingespannten Wand, einem Rand an einer Symmetrieachse
und einer Stütze mit Stützenbereich von Hand -- daneben eine schiefe
Platte, deren Streifen ihren Rändern folgen. Sie hat die Lastfälle und
Kombinationen einer frischen Decke und jede Art Last: auf einer ganzen
Platte, gezeichnet, längs einer Linie und an einem Punkt.

### _durchstanzstellen

```python
def _durchstanzstellen(p: Projekt) -> None
```

Jede Lage der gestützten Fläche, jede Form der Stütze, jede
Näherungsstufe und beide Wege zu k_e: eine Innenstütze mit Flächenlast;
eine Rundstütze am Rand, k_e aus der Exzentrizität; eine Eckstütze, die
ohne Durchstanzbewehrung aufgeht, mit den Randstreifen bis zum zweiten
Rand (Figur 25); eine Randstütze in Stufe 3, deren r_s senkrecht zum Rand
auf 2/3 · b_sr steigt; eine lange Ovalstütze in einer Bodenplatte, mit
Momenten von Hand und einer Aussparung neben der Ecke; ein Wandende und
eine Wandecke, an denen Stufe 2 wie Stufe 1 rechnet und für die es noch
keinen Vorschlag gibt. Innen-, Rand- und Ovalstütze brauchen
Durchstanzbewehrung; eine zweite Innenstütze trägt so viel, dass es einen
Stahlpilz braucht.

### _grundbrueche

```python
def _grundbrueche(p: Projekt) -> None
```

Jede Lage des Grundwassers und beide Arten des Bodens: drainiert mit
Kohäsion, geneigter Sohle, geneigtem Gelände, Auflast und dem
Wasser im Gleitkörper, dazu eine Last, so schräg, dass die Klammer
eines Lastneigungsfaktors unter null fällt; das Wasser über der Sohle
und auf ihrer Höhe, dort ein langer Streifen; undrainiert flach und
tief eingebunden, einmal so schräg belastet, dass es keinen
Widerstand gibt.

### _setzungen

```python
def _setzungen(p: Projekt) -> None
```

Das Beispiel der Tabelle 8.4 des Kapitels -- ein Bauwerk 15 × 8 m, starr,
auf Kiessand über Ton; der Kiessand setzt sich dort nicht, hier fast
nicht --, das mit 20 mm nicht aufgeht; dazu ein schlaffer Damm mit
Wiederbelastung, und eine Berechnung ohne Schicht.

### _pfaehle

```python
def _pfaehle(p: Projekt) -> None
```

Jede Spielart des Pfahls. Ein Bohrpfahl im Kies, das Grundwasser teilt
eine Schicht, die oberste trägt nicht; sein Fuss schert örtlich ab, in
der Moräne liegt K über K_0, und er wird auch gezogen. Ein Bohrpfahl
im Ton, undrainiert an Mantel und Fuss, der auf Druck nicht aufgeht.
Ein Mikropfahl mit Rohr aus einem statischen Versuch, mit Abrostung
und η_i über dem Regelwert; einer mit Vollstab aus Erfahrung, die
Mantelreibung aus dem geotechnischen Bericht, der Spitzendruck
eingegeben.

### _erstes

```python
def _erstes(p: Projekt, art: str) -> str
```

Die Kennung des ersten Materials dieser Art im Projekt.

### _alles_einmal

```python
def _alles_einmal(p: Projekt, decke: QuerschnittEintrag, analyse: QuerschnittsanalyseEintrag) -> None
```

Jede Vorlage, Kennwerte von Hand, Platte und Analyse als
Querschnitt, beide mit E_eq; ein Beton des Projekts und zwei eigene
Materialien -- Stahl und ein weicherer Beton --, ein Stab mit dem
Material gemäss Querschnitt; Gelenke und ein Knoten, dessen Drehung
keine Steifigkeit hat; Federn am Lager, Bettung, feste Linienlager mit
und ohne Stab; jede Lastart, auch projiziert.

### _beweglich

```python
def _beweglich(p: Projekt) -> None
```

Ein Träger auf zwei Rollen: nichts hält ihn waagrecht -- eine Meldung statt einer Zahl.


## Braucht

- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.skript]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]

## Gebraucht von

- [[opencivil.projekt.projekt]]
