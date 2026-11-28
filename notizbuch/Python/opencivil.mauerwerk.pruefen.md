---
erzeugt: 00eba589f375
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/pruefen.py
> was einer Wand fehlt oder an ihr nicht stimmt.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/pruefen.py)

## VERANTWORTUNG

Die Meldungen der Zeichnung einer Wand, in dieser Folge:

- ein Umriss, aus dem sich nicht rechnen lässt – zu wenig Ecken, sich
  selbst kreuzend, ohne Fläche: rot;
- noch keine Wand: grau; mehr als ein Umriss der Wand, eine Wand oder
  Öffnung, die kein Rechteck mit waagrechten und senkrechten Seiten ist: rot;
- eine Öffnung, die über die Wand hinaus reicht, zwei, die sich
  überschneiden: rot;
- ein Sturz, der über die Wand hinaus oder in eine andere Öffnung reicht,
  zwei Stürze, die sich überschneiden: rot;
- eine unübliche Dicke: ein Hinweis ([[opencivil.mauerwerk.pruefen#dickenhinweis|dickenhinweis]]).

Wo die Lasten liegen, prüft [[opencivil.mauerwerk.pruefen#lasten_pruefen|lasten_pruefen]], sobald die Zeichnung
rechnet: eine Last neben der Wand oder in einer Öffnung ist rot, ebenso eine,
die waagrecht tiefer schiebt als bis zum oberen Rand der höchsten Öffnung –
darunter rechnet das Werkzeug keine ([[opencivil.mauerwerk.scheibe|scheibe]]).

Was nur fehlt, steht grau und hält die Rechnung an; was falsch ist, steht
rot (Benutzer, 2026-11-19).


## ÜBLICHE DICKEN (nach Vorgabe, nicht nachgeschlagen)

Je Art der Steine die Masse, in denen sie üblich gehandelt werden
([[opencivil.mauerwerk.pruefen#Konstanten|UEBLICHE_DICKEN]]) – die Norm nennt keine. Eine andere Dicke
rechnet das Werkzeug gleich; der Hinweis sagt nur, dass sie unüblich ist.

## Inhalt

### pruefen

```python
def pruefen(wand: Wand) -> List[Meldung]
```

Siehe Dateikopf – leer, wenn sich die Wand rechnen lässt.

### _umriss

```python
def _umriss(u: Umriss) -> Optional[Meldung]
```

Was an einem Umriss nicht stimmt – rot, mit seinem Namen.

### _oeffnungen

```python
def _oeffnungen(wand: Rechteck, oeffnungen: Tuple[Oeffnung, ...]) -> List[Meldung]
```

Was an Öffnungen und Stürzen einer rechteckigen Wand nicht stimmt – alle sind Rechtecke.

### lasten_pruefen

```python
def lasten_pruefen(wand: Wand) -> List[Meldung]
```

Je Last, die nicht ganz auf der Wand oder in einer Öffnung liegt, eine
rote Meldung – nur für eine Wand, deren Zeichnung rechnet. Auf dem Rand
einer Öffnung zählt nicht: oben liegt die Last am Sturz, unten auf der
Brüstung. Dazu je Last, die waagrecht unter dem oberen Rand der höchsten
Öffnung schiebt, eine rote.

### _in_oeffnung

```python
def _in_oeffnung(last: Wandlast, r: Rechteck) -> bool
```

Ob eine Last ins Innere der Öffnung `r` reicht – auf ihrem Rand nicht.

### _wohin

```python
def _wohin(wand: Rechteck, sturz: Rechteck) -> str
```

Wo ein Sturz über die Wand hinaus reicht, als Satzteil: «oben und links».

### dickenhinweis

```python
def dickenhinweis(sorte: str, t_mm: float) -> Optional[Meldung]
```

Ein Hinweis, wenn `t_mm` keine übliche Dicke der Steine der Sorte
`sorte` ist – `None`, wenn sie es ist oder die Sorte keine Liste hat.


## Konstanten

- `UEBLICHE_DICKEN = {'MB': (100, 125, 150, 175, 200, 250, 300), 'MBL': (100, 125, 150, 17…` – In welchen Dicken die Steine einer Sorte üblich sind, in mm – siehe Dateikopf.
- `KEIN_RECHTECK = 'ist kein Rechteck mit waagrechten und senkrechten Seiten'`

## Braucht

- [[opencivil.core.sprache]]
- [[opencivil.material.mauerwerk]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.scheibe]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt.aufbau.mauerwerk]]
- [[opencivil.web.mauerwerkdaten]]
