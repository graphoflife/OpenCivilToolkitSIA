---
erzeugt: 3754ff42ec18
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/mauerwerkdaten.py
> was die Oberflaeche von einer Wand aus Mauerwerk zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/mauerwerkdaten.py)

## VERANTWORTUNG

Aus dem Befund einer Wand die Daten ihrer Zeichnung ([[opencivil.web.mauerwerkdaten#uebersicht|uebersicht]]):
ihre Meldungen – die zu Mauerwerk und Dicke auch fuer sich, fuer die
Kachel der Maske –, ob sie rechnet, ihre Pfeiler und je Oeffnung die
Flaeche ihres Sturzes – der Kern weiss, wie weit er aufliegt; die Seite zeichnet
ihn nur. Dazu der Teil des Katalogs, den nur die Wand braucht
([[opencivil.web.mauerwerkdaten#katalog|katalog]]). Umriss und Oeffnungen zeichnet die Oberflaeche nach dem
Projekt.


## EINHEITEN

In m, wie im Zeichenfenster; die ueblichen Dicken in mm, wie das Feld.

## Inhalt

### zeichnung

```python
def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung einer Wand unter ihre Teile legt – auch wenn sie nicht rechnet.

### uebersicht

```python
def uebersicht(befund: Optional[Wandbefund]) -> Dict[str, Any]
```

`bereit`: ob die Wand rechnet; `werte` ihre Bemessungswerte
([[opencivil.web.mauerwerkdaten#_werte|_werte]]); `meldungen` alle je ``{text,
elemente, fehler, unfertig}`, `zum_mauerwerk`` die zu Mauerwerk und
Dicke darunter noch einmal; `pfeiler` je `{name, x0, x1, y0, y1, b}`
und `stuerze` je `{oeffnung, sturz, x0, y0, x1, y1}` in m – leer,
solange die Zeichnung nicht rechnet. Ohne Befund ist alles leer.

### _werte

```python
def _werte(befund: Wandbefund) -> Dict[str, Any]
```

Die Bemessungswerte: der Name des Mauerwerks, der Faktor des Verbands und
je Wert `{zeichen, mauerwerk, wand, stellen}` – der des Mauerwerks und
der, mit dem die Wand rechnet, in N/mm², `mu_d` ohne Einheit.

### unfertig

```python
def unfertig(grund: str) -> Dict[str, Any]
```

Die Uebersicht einer Wand, die nicht rechnet, weil ihr etwas fehlt –
`grund` ein Satzteil ohne Punkt: grau, kein Fehler (Benutzer, 2026-11-19).

### katalog

```python
def katalog() -> Dict[str, Any]
```

Womit die Kennungen der Teile beginnen, je Liste, die Stellungen der
Schalter – wie gemauert, die Stossfugen, Kopf und Fuss, die Ränder links
und rechts, die Art eines Sturzes – und je Sorte die üblichen Dicken in mm.


## Konstanten

- `WERTE = (('f_xd', 'f_xd', 2), ('f_yd', 'f_yd', 2), ('E_xd', 'E_xd', 0), ('G_d…` – Was die Zusammenfassung von den Bemessungswerten zeigt: Kurzname, Zeichen, Stellen.

## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.core.sprache]]
- [[opencivil.mauerwerk.kennwerte]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt]]
- [[opencivil.projekt.mauerwerk]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
