---
erzeugt: 18576f6b8640
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/frueher.py
> was eine Projektdatei von frueher anders schreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/frueher.py)

## VERANTWORTUNG

Alte Speicherstaende muessen nicht weiter gehen (Benutzer, 2026-10-11). Wo
sich eine alte Angabe ohne Rueckfrage in die neue Form bringen laesst und
dasselbe rechnet, liest das Projekt sie trotzdem
([[opencivil.projekt.projekt#Projekt.aus_dict|aus_dict]]): vor dem strengen
Lesen nimmt es sie heraus, danach setzt es sie in der neuen Form ein – mit
denselben Methoden, mit denen man ein Projekt in Python baut.


## DAS WASSER (2026-11-27)

Bis dahin hatten Grundbruch und Pfahl je eine Zahl `gamma_w`, die Raumlast
des Grundwassers, mit 10 kN/m³ als Vorgabe. Seither waehlen sie eine
Fluessigkeit aus den Materialien (`wasser`, [[opencivil.material.fluessigkeit]]).


## DIE SPANNUNGEN DER SPANNGLIEDER (2026-11-27)

Bis dahin hatte ein Spannglied die Spannungen `sigma_p0` und
`sigma_pinf` in N/mm², leer die Vorgabe. Seither die Faktoren
`anteil_p0` und `anteil_pinf` ([[opencivil.projekt.spannglieder]]).
Eine leere Spannung wird die Vorgabe ihres Faktors, eine Zahl der Faktor,
der sie ergibt – mit f_pk des Spannstahls, wie die Datei ihn nennt
([[opencivil.projekt.frueher#spannungen_als_faktoren|spannungen_als_faktoren]]). So rechnet das Glied wie zuvor, auch wo
der Faktor dann 0.7258… heisst.


## DER UMRECHNUNGSFAKTOR EINES PFAHLS (2026-11-27)

Bis dahin war η_a eines Pfahls immer eine Zahl von Hand, Vorgabe 0.7.
Seither waehlt ein Schalter (`umrechnung`), ob η_a der Grenzwert der
Grundlage ist oder von Hand kommt; neu angelegt aus der Grundlage. Ein Pfahl
ohne den Schalter behaelt seine Zahl von Hand, wo sie vom Grenzwert
abweicht, sonst nimmt er den Grenzwert – so rechnet er wie zuvor
([[opencivil.projekt.frueher#umrechnung_setzen|umrechnung_setzen]]).


## DIE WAENDE EINES GEBAEUDES (2026-11-27)

Bis dahin trug ein Gebaeude im Erdbeben Waende (`waende`): je eine
Querschnittsanalyse, `n` gleiche in der Lage 0 oder 90 Grad, mit ihrem
η_EI, ueber die ganze Hoehe; die Grundschwingzeit aus den Waenden hiess
`waende`. Seither nimmt jedes Geschoss einen Kern – eine Analyse mit
allen Waenden, wie sie im Grundriss liegen – und sein η_EI; die
Grundschwingzeit heisst `kern` ([[opencivil.projekt.erdbeben]]). Die
Waende werden ein Kern ([[opencivil.projekt.frueher#kern_einsetzen|kern_einsetzen]]): eine neue Analyse, darin
jede Wand `n` mal, die in 90 Grad gedreht, nebeneinander und 1 m
auseinander. So bleiben sie getrennte Teile, jeder zaehlt um seinen eigenen
Schwerpunkt wie zuvor jede Wand, und das Gebaeude rechnet wie zuvor – nur
zaehlt eine Analyse aus getrennten Polygonen nun auch je Teil, wie in jedem
Kern. Jedes Geschoss nimmt ihn mit dem η_EI der Waende. Waende ohne Analyse
fallen weg: sie trugen nichts bei. Verschiedene η_EI, eine Analyse, die es
nicht gibt, oder eine Wand, die sich nicht lesen laesst, gehen nicht ohne
Rueckfrage in einen Kern: die Datei meldet sich dann beim Lesen.

## Inhalt

### gamma_w_heraus

```python
def gamma_w_heraus(roh: Any) -> Tuple[Any, List[Alt]]
```

`roh` ohne die Zahlen `gamma_w`, dazu je Eintrag, der eine hatte, wo
er steht und welche. Was keine Zahl ist, bleibt stehen und meldet sich
beim Lesen.

### wasser_einsetzen

```python
def wasser_einsetzen(projekt: 'Projekt', alte: List[Alt]) -> None
```

Je Zahl eine Fluessigkeit, die so viel wiegt: zu 10 kN/m³, der Vorgabe
von damals, das Wasser – das des Projekts, wenn es schon eines hat –,
zu einer anderen eine eigene Fluessigkeit mit der Dichte dazu. Jeder
Eintrag nimmt die seine; so rechnet die Datei wie zuvor.

### _alt

```python
def _alt(eintrag: Any) -> bool
```

Ob ein Eintrag noch eine Zahl `gamma_w` hat und keine Fluessigkeit.

### umrechnung_setzen

```python
def umrechnung_setzen(roh: Any) -> Any
```

`roh` mit dem Schalter η_a an jedem Pfahl, der keinen hat – siehe Dateikopf.

### _umrechnung

```python
def _umrechnung(pfahl: Any) -> Any
```

Ein Pfahl mit dem Schalter – `pfahl` selbst, wo er ihn schon hat oder
die Grundlage keine ist: das meldet dann das Lesen.

### spannungen_als_faktoren

```python
def spannungen_als_faktoren(roh: Any) -> Any
```

`roh` mit Faktoren statt der Spannungen der Spannglieder – siehe
Dateikopf. Was sich nicht umrechnen laesst, weil der Spannstahl fehlt
oder eine Spannung keine Zahl ist, bleibt stehen und meldet sich beim
Lesen.

### _zugfestigkeiten

```python
def _zugfestigkeiten(materialien: Any) -> Dict[str, float]
```

Je Spannstahl der Datei sein f_pk in N/mm²: ueberschrieben, abgewichen oder der Sorte.

### _faktoren

```python
def _faktoren(glied: Any, f_pk: Mapping[str, float]) -> Any
```

Ein Glied mit Faktoren statt Spannungen – `glied` selbst, wo das nicht geht.

### waende_heraus

```python
def waende_heraus(roh: Any) -> Tuple[Any, List[Waende]]
```

`roh` ohne die Waende der Gebaeude, mit `kern` statt `waende` als
Grundschwingzeit und dem η_EI der Waende in jedem Geschoss, dazu je
Gebaeude mit Waenden, die eine Analyse haben, wo es steht und welche –
siehe Dateikopf. Was sich nicht so lesen laesst, bleibt stehen und
meldet sich beim Lesen.

### _waende

```python
def _waende(gebaeude: Any, analysen: AbstractSet[Any]) -> Optional[Tuple[Any, List[Wand]]]
```

Das gemeinsame η_EI der Waende eines Gebaeudes und je Wand mit Analyse,
was der Kern von ihr braucht – `None`, wo es keine Waende hat oder
sie nicht ohne Rueckfrage in einen Kern gehen.

### kern_einsetzen

```python
def kern_einsetzen(projekt: 'Projekt', alte: List[Waende]) -> None
```

Je Gebaeude mit Waenden von frueher ein Kern aus ihnen, den jedes
Geschoss nimmt – eine neue Analyse «Kern …» mit dem Namen des
Gebaeudes, siehe Dateikopf.

### _kopieren

```python
def _kopieren(wand: QuerschnittsanalyseEintrag, kern: QuerschnittsanalyseEintrag, gedreht: bool, links: float) -> float
```

Polygone, Staebe und Stablinien einer Wand in den Kern – um 90 Grad
gedreht, wo sie so lag, rechts von `links` und unten auf z = 0. Gibt
zurueck, wo sie rechts endet, in mm.

### _ohne

```python
def _ohne(felder: Mapping[str, Any], *weg: str) -> Dict[str, Any]
```

Die Felder eines Elements ohne seine Kennung und ohne `weg`.


## Konstanten

- `_MIT_WASSER = ('grundbrueche', 'pfaehle')` – Die Listen, deren Eintraege bis 2026-11-27 ein `gamma_w` hatten.
- `Alt = Tuple[str, int, float]` – Wo ein Eintrag mit einer alten Zahl stand: Liste, Stelle, Zahl in kN/m³.
- `_ETA_A_BIS_DAHIN = 0.7` – η_a eines Pfahls ohne Zahl in der Datei, bis 2026-11-27.
- `_SPANNUNGEN = ('sigma_p0', 'sigma_pinf')` – Was ein Spannglied bis 2026-11-27 statt seiner Faktoren hatte.
- `_ABSTAND = 1000.0` – So weit liegen die Waende von frueher im Kern auseinander, in mm: sie beruehren sich nicht und bleiben getrennte Teile.
- `Wand = Tuple[str, bool, int]` – Je Wand von frueher mit Analyse: deren Kennung, ob sie um 90 Grad gedreht lag, und wie oft sie zaehlte.
- `Waende = Tuple[int, List[Wand]]` – Ein Gebaeude mit Waenden von frueher: seine Stelle in der Liste und seine Waende.

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.material.fluessigkeit]]
- [[opencivil.material.spannstahl]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.spannglieder]]

## Gebraucht von

- [[opencivil.projekt.projekt]]
