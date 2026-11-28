---
erzeugt: 3b9d2809c013
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/vorgaben.py
> die Zahlen, die ein Nachweis aus seiner Beschreibung liest.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/vorgaben.py)

## VERANTWORTUNG

Je Nachweis eine Tafel seiner Vorgaben, in Gruppen ([[opencivil.core.vorgaben#Gruppe|Gruppe]]): was die
Herleitung in ihren Kästen zeigt und die Maske in ihren Kacheln – dieselben
Felder in derselben Folge, mit demselben Zeichen ([[opencivil.core.vorgaben#Feld|Feld]]). Eine Gruppe
kann sich nach Wahlen der Beschreibung richten (`nach`): drainiert liest
der Grundbruch anderes als undrainiert. Die Rechnung fragt sie mit ihren
eigenen Wahlen ([[opencivil.core.vorgaben#Gruppe.fuer|Gruppe.fuer]]), der Katalog schreibt sie für jede
Stellung aus ([[opencivil.core.vorgaben#Gruppe.als_dict|Gruppe.als_dict]]), und die Maske nimmt die zu ihrem
Eintrag (`eingabegruppen` in `web/js/bausteine.js`), je Gruppe eine
Kachel (`gruppenkapitel` in `web/js/kapitel.js`).

Bis 2026-11-20 schrieben die Masken von Durchstanzen, Grundbruch, Setzung und
Pfahl die Tafeln von Hand ab: ein neues Feld des Kerns erschien dort nie, und
die Zeichen liefen auseinander (k_δ im Kern, δ_k/φ_k in der Maske).


## ZWEI TEXTE

Die Herleitung beschreibt eine Zahl ausführlich, die Maske hat für ihre
Beschriftung eine Zeile, die abschneidet, was übersteht – und mit ihm das
Zeichen. Ein Feld trägt darum beide: die `beschreibung` und, wo sie zu lang
ist, eine kurze `beschriftung`; die Maske zeigt die Beschreibung im Titel
über dem Feld, mit dem `hinweis` und der Normstelle. Die Schrittweite der
Pfeile (`schritt`) braucht nur die Maske. Die Einheit und die Grenzen nimmt
sie vom Feld der Beschreibung (`katalog.felder`) – dort steht, in welcher
Einheit der Kern eine Zahl liest.


## ENGER NACH DEN WAHLEN

Ein Feld kann nach den Wahlen enger begrenzt sein als sein Feld in der
Beschreibung ([[opencivil.core.vorgaben#Feld|Feld.bis]]): η_a eines Pfahls ist höchstens der
Grenzwert seiner Grundlage. Die Maske weist eine grössere Zahl ab, mit dem
Satz des Feldes. Legen die Wahlen die Zahl fest ([[opencivil.core.vorgaben#Feld|Feld.fest]]), steht
sie grau in der Maske, und die Herleitung rechnet mit ihr statt mit der
Zahl der Beschreibung – η_a aus der Grundlage (Benutzer, 2026-11-27).


## WIEDERHOLTE GRUPPEN

Die Schichten unter einem Fundament oder an einem Pfahl haben je dieselben
Felder: eine Gruppe als Vorlage, je Schicht mit ihrer Nummer
([[opencivil.core.vorgaben#Feld.nummeriert|Feld.nummeriert]]). «#» in einer Beschreibung steht für die Schicht –
in der Herleitung «Schicht 2», in der Maske, deren Karte schon so heisst,
«Schicht». Hat eine Schicht mehrere Gruppen, wie am Pfahl, teilen sie sich
ihren Kasten und ihre Karte: ihre Titel sagen der Maske nur, wo sie einen
Schalter zwischen die Felder setzt (`eingabezeilen`).

## Inhalt

### mit_index

```python
def mit_index(zeichen: str, i: int) -> str
```

Ein Zeichen mit der Nummer `i` im Index: `d` wird `d_{1}`, `M_E`
`M_{E,1}`, `s_{u,k}` `s_{u,k,1}`.

### Feld

```python
@dataclass(frozen=True)
class Feld
```

Eine Zahl, die ein Nachweis liest – in der Herleitung und in der Maske.

- `kurz: str` – Der Kurzname: so heisst das Feld der Beschreibung, aus dem die Zahl kommt.
- `zeichen: str` – LaTeX, ohne Mathematikumgebung.
- `einheit: Einheit` – Die Einheit in der Herleitung.
- `beschreibung: str`
- `stellen: int = 2` – Nachkommastellen in der Herleitung.
- `referenz: str = ''`
- `beschriftung: str = ''` – Die Beschriftung in der Maske, wo die Beschreibung zu lang ist – leer: die Beschreibung.
- `schritt: float = 1.0` – Wie weit ein Pfeil in der Maske die Zahl verschiebt.
- `hinweis: str = ''` – Was die Maske über dem Feld dazu sagt – etwa, wie ein Winkel zählt.
- `bis: Optional[float] = None` – Wie gross die Zahl nach den Wahlen höchstens ist, in [[opencivil.core.vorgaben#Feld|einheit]] – wo das enger ist als die Grenze ihres Feldes. Die Maske weist eine grössere ab und sagt [[opencivil.core.vorgaben#Feld|bis_satz]]; im Kern prüft die Beschreibung selbst (`regeln`), denn nur sie weiss, ob die Zahl gilt.
- `bis_satz: str = ''` – Warum die Zahl höchstens [[opencivil.core.vorgaben#Feld|bis]] ist – der Satz, mit dem die Maske eine grössere abweist.
- `fest: bool = False` – Ob die Wahlen die Zahl auf [[opencivil.core.vorgaben#Feld|bis]] festlegen: die Maske zeigt sie grau, und die Herleitung rechnet mit ihr statt mit der Zahl der Beschreibung ([[opencivil.core.vorgaben#Feld.vorgabe|vorgabe]]).

#### Feld.vorgabe

```python
def vorgabe(self, praefix: str, abschnitt: Abschnitt, gruppe: str, groesse: Groesse) -> Tuple[WertDef, Vorgabe]
```

Die Definition der Zahl und ihre Vorgabe in der Herleitung, im Kasten
`gruppe` – `groesse`, die Zahl der Beschreibung, oder, ist das
Feld [[opencivil.core.vorgaben#Feld|fest]], seine Zahl [[opencivil.core.vorgaben#Feld|bis]].

#### Feld.nummeriert

```python
def nummeriert(self, i: int) -> 'Feld'
```

Das Feld der Schicht `i`: `d` wird `d_1`, sein Zeichen `d_{1}`, «#» «Schicht 1».

#### Feld.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

Was die Maske von ihm braucht – «#» steht dort für die Schicht ihrer
Karte. `bis` mit seinem Satz und `fest` nur, wo es sie gibt.

### Gruppe

```python
@dataclass(frozen=True)
class Gruppe
```

Ein Kasten der Herleitung, eine Kachel der Maske.

- `titel: str`
- `felder: Callable[..., Sequence[Feld]]` – Die Felder, die gelten, in ihrer Folge – aus den Stellungen der Wahlen in [[opencivil.core.vorgaben#Gruppe|nach]].
- `nach: Tuple[str, ...] = ()` – Nach welchen Wahlen sie sich richtet: die Namen ihrer Felder in der Beschreibung.

#### Gruppe.fuer

```python
def fuer(self, objekt: Any) -> Tuple[Feld, ...]
```

Die Felder, die für `objekt` gelten – eine Beschreibung oder ihre
Rechnung: beide tragen die Wahlen unter denselben Namen.

#### Gruppe.als_dict

```python
def als_dict(self, stellungen: Mapping[str, Sequence[Any]]) -> Dict[str, Any]
```

Für die Maske: je Stellung der Wahlen die Felder, unter den Werten der
Wahlen mit «\|» dazwischen – ohne Wahl unter «». `stellungen` sagt
je Wahl, welche Werte sie annehmen kann.


## Konstanten

- `SCHICHT = 'Schicht'` – Wofür «#» in der Beschreibung eines wiederholten Feldes steht.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.durchstanzen.stelle]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.fachwerkmodell.verfahren]]
- [[opencivil.geotechnik.fundament]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.pfahl.pfahl]]
