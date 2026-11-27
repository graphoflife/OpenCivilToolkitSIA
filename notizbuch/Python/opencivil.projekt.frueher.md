---
erzeugt: 23c2aa5e803a
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


## Konstanten

- `_MIT_WASSER = ('grundbrueche', 'pfaehle')` – Die Listen, deren Eintraege bis 2026-11-27 ein `gamma_w` hatten.
- `Alt = Tuple[str, int, float]` – Wo ein Eintrag mit einer alten Zahl stand: Liste, Stelle, Zahl in kN/m³.
- `_SPANNUNGEN = ('sigma_p0', 'sigma_pinf')` – Was ein Spannglied bis 2026-11-27 statt seiner Faktoren hatte.

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.material.fluessigkeit]]
- [[opencivil.material.spannstahl]]
- [[opencivil.projekt.projekt]]
- [[opencivil.querschnitt.spannglieder]]

## Gebraucht von

- [[opencivil.projekt.projekt]]
