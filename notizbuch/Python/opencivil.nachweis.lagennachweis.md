---
erzeugt: 6ab6bff5b69a
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/lagennachweis.py
> ein Nachweis je Platte, ein Urteil je Bewehrungslage.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/lagennachweis.py)

## VERANTWORTUNG

Die Schablone ([[opencivil.nachweis.lagennachweis#Lagennachweis|Lagennachweis]]) der Nachweise, die jede Lage einer
Platte fuer sich ansehen -- Duktilitaet, sproedes Versagen, Zwaengung auf
Biegung und auf Normalkraft. Hier steht einmal, was sie teilen: welche
Lagen und ihre Posten, je Lage ein Erfuellungsgrad mit derselben Kennung,
demselben Zeichen und derselben Benennung, die Bezuege auf Posten und
Staehle, die Schleife ueber die Lagen mit Befund und Urteil und die
Begruendung einer Lage ohne Stahl. Was je Nachweis anders ist, geben seine
Methoden: was alle Lagen brauchen ([[opencivil.nachweis.lagennachweis#Lagennachweis.ansatz|Lagennachweis.ansatz]]), die eine
Lage ([[opencivil.nachweis.lagennachweis#Lagennachweis.eine_lage|eine_lage]]) und ihre Herleitung
([[opencivil.nachweis.lagennachweis#Lagennachweis.protokoll_lage|protokoll_lage]]).


## LAGEN OHNE STAHL

Sproedes Versagen, Zwaengung auf Biegung und Duktilitaet lassen eine Lage
ohne Stahl weg (Benutzer, 2026-10-19) -- der Aufbau gibt sie ihnen nicht.
Bekommen sie trotzdem eine, ist das ein Fehler des Aufbaus und meldet sich
(`NUR_MIT_STAHL`). Nur die Zwaengung auf Normalkraft prueft jede Lage,
auch die leere: gerade sie faellt durch und soll es sichtbar tun.

Bis 2026-11-10 stand das viermal da, je mit eigener Lagenwahl,
Stahl-Entdoppelung, Gradkennung und Sammelschleife; der allgemeine Nachweis
trug `ohne_bewehrung` mit, und in drei der vier lief dieser Zweig nie.

## Inhalt

### Lagennachweis

```python
class Lagennachweis(Nachweis)
```

Ein Nachweis je Platte, ein Urteil je Lage -- siehe Dateikopf.

- `KUERZEL: str = ''` – Im Zeichen des Grads: α_eff,D,2 -- «D».
- `BENENNUNG: str = ''` – Im Text des Grads: «Erfüllungsgrad Duktilität – 2. Lage» -- «Duktilität».
- `REFERENZ: str = ''`
- `NUR_MIT_STAHL: bool = True` – Ob er nur Lagen mit Stahl bekommt -- siehe Dateikopf.

#### Lagennachweis.lagen_waehlen

```python
@staticmethod
def lagen_waehlen(querschnitt, richtung: Richtung, nummern: Sequence[int]) -> List[Bewehrungslage]
```

Die gewaehlten Lagen einer Richtung -- keine ist ein Fehler des Aufbaus.

#### Lagennachweis.ohne_bewehrung

```python
@staticmethod
def ohne_bewehrung(nummer: int) -> str
```

Die Begruendung einer Lage ohne Stahl.

#### Lagennachweis.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Lagennachweis.ansatz

```python
@abstractmethod
def ansatz(self, e: Eingaben, p: Protokoll) -> Any
```

Was alle Lagen brauchen, mit seiner Herleitung -- es geht an jede Lage weiter.

#### Lagennachweis.eine_lage

```python
@abstractmethod
def eine_lage(self, e: Eingaben, lage: Bewehrungslage, ansatz: Any) -> Any
```

Das Ergebnis einer Lage, mit `ausgang` und `begruendung`.

#### Lagennachweis.protokoll_lage

```python
@abstractmethod
def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Any, ansatz: Any) -> None
```

Die Herleitung einer Lage.

#### Lagennachweis.ausgaben_der_lage

```python
def ausgaben_der_lage(self, erg: Any) -> Mapping[str, Groesse]
```

Was eine Lage ausser ihrem Grad ausgibt -- meist nichts.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.sproedes_versagen]]
