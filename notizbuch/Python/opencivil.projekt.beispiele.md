---
erzeugt: 012cbf733f63
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
steht die Fassade an einer Stelle vorgeführt – und der
Schnappschuss-Test prüft sie mit: baute sie etwas anderes als die
Einträge von Hand, die hier vorher standen, änderte sich der Bericht.

### jeder_nachweis

```python
def jeder_nachweis() -> Projekt
```

Jeder Nachweis einmal laut – und die Fälle, die das Beispiel nie zeigt.

Zusammen mit [[opencivil.projekt.beispiele#beispiel|beispiel]] führt es jeden Nachweis einmal laut; ein
Test wacht darüber. Aus den beiden stammen der Schnappschuss des
Berichts und die Formelsammlung der Oberfläche – darum steht es hier
und nicht bei den Tests.

Erhöhte Anforderung mit allen Schaltern und begrenzter rissaktiver
Dicke, häufige und quasi-ständige Lastfälle abgeleitet und eigene, Bügel
mit Stabzahl in y, ein Knickfall, die Verformung im Feld und am
Kragarm; eine zweite Platte mit x aussen und b = 500 mm, die im Feld
nicht aufgeht, auch nicht in der Durchbiegung, und deren Stahl unter
Dauerlast fliesst, dazu Querkraft ohne Bügel – einmal über m_Rd,
einmal darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
gemessen wird, und ⌀40 in y unter der x-Bewehrung – die fliesst bei
x = h/2 nicht. Gebaut über die Fassade, wie ein Benutzer es in Python
täte.

### _decken

```python
def _decken(p: Projekt) -> None
```

Drei Decken. Die des Kolloquiums 4 (Stahlbeton II): eine Platte auf
einer Wand und drei Stützen, Träger in zwei Stufen, fest
30 % in x, und als einziger Lastfall q_d = 18.6 kN/m² auf der ganzen
Platte, das Eigengewicht darin. Und eine, die jede Wahl einmal braucht:
zwei Platten verschiedener Dicke in einem L, automatisch aufgeteilt, mit
einer Zone, einer eingespannten Wand, einem Rand an einer Symmetrieachse
und einer Stütze mit Stützenbereich von Hand – daneben eine schiefe
Platte, deren Streifen ihren Rändern folgen. Sie hat die Lastfälle und
Kombinationen einer frischen Decke und jede Art Last: auf einer ganzen
Platte, gezeichnet, längs einer Linie und an einem Punkt. Die erste
zeigt m_x, m_y, die Lager und M und V des Trägers T4, der auf den drei
anderen liegt; die zweite jedes Bild der Streifenmethode einmal. Die
dritte ist die erste nach der FEM, T4 als Unterzug 300 mm unter der
Platte, mit einem Schnitt quer durch die Felder: sie zeigt jedes Bild
der Platte einmal, auch die Durchbiegung, das längs des Schnitts und M
und V von T4.

### _fachwerkmodell

```python
def _fachwerkmodell(p: Projekt) -> None
```

Eine Wandscheibe 6 × 3 m mit einer Türe, links fest, rechts auf einem
Rollenlager, oben zwei Lasten – eine schräg.

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

Das Beispiel der Tabelle 8.4 des Kapitels – ein Bauwerk 15 × 8 m, starr,
auf Kiessand über Ton; der Kiessand setzt sich dort nicht, hier fast
nicht –, das mit 20 mm nicht aufgeht; dazu ein schlaffer Damm mit
Wiederbelastung, und eine Berechnung ohne Schicht.

### _pfaehle

```python
def _pfaehle(p: Projekt) -> None
```

Jede Spielart des Pfahls. Ein Bohrpfahl im Kies, das Grundwasser teilt
eine Schicht, die oberste trägt nicht; sein Fuss schert örtlich ab, in
der Moräne liegt K über K_0, und er wird auch gezogen, quer mit einem
Moment am frei drehbaren Kopf. Ein Bohrpfahl im Ton, undrainiert an
Mantel und Fuss, der auf Druck nicht aufgeht, der Kopf eingespannt –
sein Moment zählt dann nicht. Ein Mikropfahl mit Rohr aus einem
statischen Versuch, ohne Schichten und darum ohne Steifigkeit, mit
Abrostung und η_i über dem Regelwert; einer mit Vollstab aus Erfahrung,
die Mantelreibung aus dem geotechnischen Bericht, der Spitzendruck
eingegeben, quer leicht belastet – und schon das trägt er nicht: ein
gezogener Stab hält quer wenig, und am Terrain drückt er den Kies
stärker, als dieser hält.

### _gebaeude

```python
def _gebaeude(p: Projekt) -> None
```

Was das Wohnhaus des Beispiels nie zeigt. Ein Lager mit T_1 von Hand und
ohne Kern – die Kraefte je Geschoss bleiben ohne Verteilung –, in
Zone Z3b auf Baugrund E, Bauwerksklasse III: in x liegt T_1 unter T_B
(31), in y zwischen T_C und T_D (33) und ueber 4 T_C, (39) geht dort
nicht auf. Sein Grundriss ist nicht regelmaessig und das Dach schwerer
als das Erdgeschoss: das Verfahren gilt nicht. Ein schlanker Turm auf
einem Kern aus einer Winkelwand, deren y und z keine Hauptachsen sind,
oben duenner als unten – in y schwingt er langsamer als T_D (34) –,
duktil bemessen mit q = 3.0: dafuer steht der graue Satz zu den Waenden.
Und ein Gebaeude, dessen Dach noch keinen Kern hat: es rechnet nicht.

### _tragwand

```python
def _tragwand(kennung: str, name: str, ecken: list, beton: str) -> QuerschnittsanalyseEintrag
```

Ein Kern fuer das Erdbeben: ein Polygon aus Beton, ohne Bewehrung und ohne Lastfall.

### _wand

```python
def _wand(a: QuerschnittsanalyseEintrag, y1: float, z1: float, y2: float, z2: float, *, beton: str, stahl: str) -> None
```

Eine Wand eines Kerns: ein Rechteck von (y1, z1) bis (y2, z2) in mm, an
beiden langen Seiten Staebe ⌀ 12 alle 150 mm, die Achsen 50 mm vom Rand.

### _erstes

```python
def _erstes(p: Projekt, art: str) -> str
```

Die Kennung des ersten Materials dieser Art im Projekt – kurz, weil oft gebraucht.

### charakteristisch

```python
def charakteristisch(eintrag) -> dict
```

Charakteristische Werte fuer jedes Material, auf das der Eintrag zeigt.

### _alles_einmal

```python
def _alles_einmal(p: Projekt, decke: QuerschnittEintrag, analyse: QuerschnittsanalyseEintrag) -> None
```

Jede Vorlage, Kennwerte von Hand, Platte und Analyse als Querschnitt,
beide mit E_eq; jede Form der Stahlprofile um beide Achsen – ohne Stab,
ausser dem HEB –, das Rundrohr ohne Achse, das Doppel-T ohne Stab; ein
Beton und ein Baustahl des Projekts und ein eigenes Material, ein
weicherer Beton; ein Stab mit dem Material gemäss Querschnitt; Gelenke
und ein Knoten, dessen Drehung keine Steifigkeit hat; Federn am Lager,
Bettung, feste Linienlager mit und ohne Stab; jede Lastart, auch
projiziert.

### _beweglich

```python
def _beweglich(p: Projekt) -> None
```

Ein Träger auf zwei Rollen: nichts hält ihn waagrecht – eine Meldung statt einer Zahl.

### _raumrahmen

```python
def _raumrahmen(p: Projekt, decke: QuerschnittEintrag, analyse: QuerschnittsanalyseEintrag) -> None
```

Ein Rahmen im Raum, der alles einmal braucht: Stützen aus Beton, Stahl
und Holz, je mit anderem Lager – eingespannt, gelenkig mit Drehfeder,
verschieblich und in y gehalten –, Riegel in x und y, einer gedreht und
einer mit Gelenk, ein geneigter Kragarm, ein gebetteter Fundamentbalken;
Querschnitte nach Vorlage, als Profil – dazu ein Rundrohr ohne Stab,
mit I_z wie I_y –, von Hand, aus einer Platte mit E_eq und aus einer
Querschnittsanalyse, deren I_T sie dafür rechnet – beide mit dem
Material gemäss Querschnitt –, ein eigenes Material mit G; Lasten in
jeder Richtung, Torsion, projiziert, an Knoten.

### _spannbeton

```python
def _spannbeton(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein Träger 400 × 800 mm mit Betonstahl oben und unten und drei
Spanngliedern aus Y1860, je eines in jedem Gesetz: vier Litzen mit
Vordehnung und Verbund, die Faktoren der Spannungen nach Vorgabe; eines
ohne Verbund mit eingegebener Fläche, 280 mm² wie zwei Litzen ⌀15.3, und
eigenen Faktoren; zwei schlaff mit Restfestigkeit. Die
Duktilität sieht Spannstahl in der Zugzone, sprödes Versagen und
Zwängung messen am Rissmoment mit Vorspannung, die Stahlspannung gilt
dem Betonstahl, und die Linie beginnt bei der Krümmung, die die
Vorspannung allein weckt. Am Auflager trägt das erste Glied, um 5°
geneigt, die Querkraft mit; das zweite, um -4° geneigt und neben dem
Schwerpunkt, wirkt ihr entgegen und dreht den Kasten der Schubwände; das
schlaffe zählt seine Neigung nicht.

### _stahltraeger

```python
def _stahltraeger(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein IPE 600 aus S355, zweiachsig, jede Klasse einmal (SIA 263:2013):
im Feld plastisch, schief, mit einer Querkraft über der Hälfte von V_Rd,
die dem Steg nimmt, und mit Torsion, die nur ein Hinweis ist; mit mehr
Druck nach (54), mit noch mehr am wirksamen Querschnitt nach (60), und
reiner Druck nach (55).

Dazu Knicken und Kippen, wieder jede Klasse: im Feld nach (50) und (51),
mit Kippen unter einem dreieckigen Moment; mit Druck in Klasse 3; am
wirksamen Querschnitt nach (62) und (63); reiner Druck nach 5.3.8; und
seitlich gehalten nur (50).

### _holztraeger

```python
def _holztraeger(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein Rechteck 160 × 400 mm aus GL24h in Feuchteklasse 2, zweiachsig, jede
Gleichung von SIA 265:2012, 4.2 einmal: Zug mit Biegung nach (21) und
Querkraft in beiden Richtungen mit Torsion nach (25); Druck mit Biegung
nach (22) und Querkraft allein nach (23); stossartig Biegung allein nach
(14) und Torsion allein nach (24); Zug allein nach (6), Druck allein
nach (10). Unter 600 mm Hoehe mit k_h.

Dazu ein Stab: Druck und Biegung mit Knicken und Kippen nach (37), Druck
allein nach (29), stossartig Biegung allein nach (38), mit k_m \< 1.


## Braucht

- [[opencivil.decke.feld]]
- [[opencivil.decke.schnitt]]
- [[opencivil.material.holz]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.beispiele_verbund]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.skript]]
- [[opencivil.projekt.staebe]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]

## Gebraucht von

- [[opencivil.projekt.projekt]]
