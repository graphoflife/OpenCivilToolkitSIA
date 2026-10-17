---
erzeugt: 1ca6362f4149
art: modul
tags: [modul]
---
> [!abstract] opencivil/bewehrungssuche/bewertung.py
> wie weit eine Bewehrung vom Ziel ist.
> Paket [[opencivil.bewehrungssuche]] · [Quelltext](../../opencivil/bewehrungssuche/bewertung.py)

## VERANTWORTUNG

Die Platte, gegen die gesucht wird ([[opencivil.bewehrungssuche.bewertung#arbeitskopie|arbeitskopie]]), und die eine Zahl,
an der sich jede Suche ausrichtet ([[opencivil.bewehrungssuche.bewertung#Bewertung|Bewertung]]). Laengs- und
Buegelsuche stehen beide darauf.


## WELCHE NACHWEISE ZAEHLEN

Die, die gebaut werden -- und gebaut wird nur, was eingeschaltet ist. Die
Schalter der Oberflaeche steuern also unmittelbar die Suche, ohne dass hier
eine zweite Liste gepflegt werden muesste. Ohne Kraefte fallen zusaetzlich
die Einwirkungen weg (siehe [[opencivil.bewehrungssuche.bewertung#arbeitskopie|arbeitskopie]]).

## Inhalt

### Bewertung

```python
@dataclass
class Bewertung
```

Wie weit eine Bewehrung von der Erfuellung entfernt ist.

- `rueckstand: float` – Summe der Fehlbetraege, `sum(max(0, 1 - alpha))` ueber alle Nachweise. **Nicht** der schlechteste Grad. Der war die erste Fassung, und er hat die Suche zum Stehen gebracht: halten zwei Nachweise gleichzeitig das Minimum -- etwa sproedes Versagen in der 1. und in der 4. Lage bei gleicher Bewehrung --, dann hebt kein einzelner Schritt es, weil der jeweils andere stehen bleibt. Die Suche sah eine Ebene und gab auf, obwohl der naechste Durchmesser offensichtlich geholfen haette. Die Summe der Fehlbetraege kennt diese Ebene nicht: sie faellt, sobald *irgendein* unerfuellter Nachweis besser wird. Null heisst genau, dass alle aufgehen.
- `grad: float` – Der schlechteste Erfuellungsgrad -- nur zum Berichten.
- `nachweis: str`
- `anzahl: int` – Wie viele *gefuehrte* Urteile gefaellt wurden. Ohne die stillen: gegen einen Nachweis, den niemand fuehrt, sucht die Suche nicht, also zaehlt sie ihn auch nicht mit -- sonst haette sie einen Rueckstand aufzuholen, den niemand verlangt hat.
- `fehler: str = ''`

#### Bewertung.abstand

```python
def abstand(self, erwartet: int=1) -> float
```

Wie weit diese Bewehrung vom Ziel entfernt ist -- die eine Zahl, an
der sich die Suche ausrichtet.

Das ist der Rueckstand **plus ein voller Punkt fuer jeden Nachweis,
den es gar nicht gibt**. `erwartet` ist die Zahl der Urteile, die
die Platte voll bewehrt faellt; fehlt eines, ist die Lage, der es
gilt, unbewehrt -- und ein Nachweis, der sich nicht einmal aufstellen
laesst, ist so schlecht wie einer, der bei null steht.

Ohne diesen Zuschlag hat die Suche eine Abkuerzung: nimm allen Stahl
weg, dann gibt es keinen Nachweis mehr, und kein Nachweis heisst
Rueckstand null. Sie hat sie gefunden, kaum dass leere Lagen suchbar
waren -- und zwar nicht erst beim Annehmen des Ergebnisses, sondern
schon bei der Wahl des naechsten Schritts.

#### Bewertung.erfuellt

```python
def erfuellt(self, erwartet: int=1) -> bool
```

Ob alle erwarteten Nachweise da sind und alle aufgehen.

### bewerte

```python
def bewerte(projekt) -> Bewertung
```

Rechnen und sagen, wie weit es noch ist.

Gezaehlt wird jedes Urteil, das nicht still ist -- still heisst
ausgeschaltet, und gegen einen Nachweis zu suchen, den niemand fuehrt,
hiesse dem Benutzer Bewehrung aufzudraengen, die er nicht verlangt hat.
Der Duktilitaetsnachweis faellt so von selbst heraus:
[[opencivil.bewehrungssuche.bewertung#arbeitskopie|arbeitskopie]] schaltet ihn ab.

### vorab_pruefen

```python
def vorab_pruefen(projekt, kennung: str) -> None
```

Was an der Platte nicht stimmen kann, meldet sich vor der Suche -- als
Fehler und nicht als «nicht gefunden». In der Bewertung wird jede
Ausnahme ein Nein ([[opencivil.bewehrungssuche.bewertung#bewerte|bewerte]]); eine Platte mit h = 0 hiess dort,
keine Bewehrung reiche. Geprueft wird, was die Suche rechnet: die Platte
mit den Materialien (`Projekt.nur`), Form und Inhalt -- gebaut wird
nicht, eine Platte ohne Bewehrung darf ihre Suche haben.

### arbeitskopie

```python
def arbeitskopie(projekt, kennung: str, *, kraefte: bool, leeren: bool=True)
```

Die Platte, gegen die gesucht wird -- ohne das, was die Suche nicht fuehren
kann.

**Ohne Duktilitaet, immer.** Sie ist der einzige Nachweis, der durch mehr
Bewehrung *schlechter* wird: er begrenzt die Druckzonenhoehe, und die
waechst mit der Stahlflaeche. Eine Suche, die von unten aufsteigt, kann ihn
darum nicht erfuellen, sondern nur verletzen -- sie haette gegen ihn kein
Mittel ausser aufzugeben. Also bleibt er draussen, und das Ergebnis sagt
hinterher, ob er mit der gefundenen Bewehrung noch aufgeht.

**Ohne Bewehrung, sofern `leeren`.** Das Werkzeug *ermittelt* die
Bewehrung; es legt nicht zu dem dazu, was zufaellig dasteht. Die
Buegelsuche laeuft danach und braucht die gefundene Laengsbewehrung --
sie setzt `leeren=False`, denn ohne statische Hoehe gibt es keinen
Querkraftwiderstand.

Ohne `kraefte` fallen zusaetzlich alle Lastfaelle weg -- Kombinationen,
Knickfaelle, haeufige und quasi-staendige. Uebrig bleiben die Nachweise, die eine Platte
unabhaengig von der Belastung erfuellen muss.

Abgeschaltet wird hier und nicht beim Bewerten: gebaut wird nur, was
eingeschaltet ist, und gezaehlt wird, was gebaut wurde. An dieser einen
Regel soll die Suche nichts vorbeischmuggeln.


## Braucht

- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.bewehrungssuche]]
- [[opencivil.bewehrungssuche.buegel]]
- [[opencivil.bewehrungssuche.dicke]]
- [[opencivil.bewehrungssuche.laengs]]
