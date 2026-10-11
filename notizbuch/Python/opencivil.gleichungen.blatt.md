---
erzeugt: 71cd7f109505
art: modul
tags: [modul]
---
> [!abstract] opencivil/gleichungen/blatt.py
> ein Blatt Gleichungen als Berechnung.
> Paket [[opencivil.gleichungen]] · [Quelltext](../../opencivil/gleichungen/blatt.py)

## VERANTWORTUNG

Rechnet die Zeilen eines Blatts der Reihe nach und schreibt jede in die
Herleitung -- unter «Analytische Gleichungen – Name», wie jede andere
Berechnung unter ihrer Ueberschrift. Projektwerte kommen als Eingaben aus dem
Rechenwerk; das Blatt laeuft darum nach dem, was es liest.


## JEDE ZEILE FUER SICH

Ein Fehler bleibt bei seiner Zeile -- und bei den Zeilen, die das dort
Definierte brauchen. Er bricht weder das Blatt ab noch den Lauf der Platten.
Eine Neudefinition gilt ab ihrer Zeile, wie beim Lesen von oben nach unten.


## DIE ZEILEN IN DER LOESUNG

Was eine Zeile ergibt, steht nach dem Lauf in der Loesung und damit in der
Werteliste des Berichts: `gleichungen.g1.z003` heisst «Name, Zeile 3».
Vorab erklaeren kann das Blatt diese Werte nicht -- welche Zeilen aufgehen
und in welcher Einheit, steht erst nach dem Rechnen fest. Erklaert ist nur
das Ziel, die Zahl der aufgegangenen Zeilen; es steht in keiner Werteliste.

## Inhalt

### Zeilenergebnis

```python
@dataclass
class Zeilenergebnis
```

Was die Oberflaeche neben einer Zeile zeigt.

- `ergebnis: str = ''` – Das Ergebnis als LaTeX, `21\,\mathrm{m}^{2}` -- aus dem Kern gesetzt.
- `fehler: str = ''`
- `name: str = ''` – Was die Zeile definiert, als LaTeX -- leer bei Auswertung und Text.
- `wert: Optional[Wert] = None` – Was die Zeile ergibt -- `None` bei Text, leeren Zeilen und Fehlern.

### Gleichungsblatt

```python
class Gleichungsblatt(Prozedur)
```

Ein Blatt aus [[opencivil.projekt.gleichungen#GleichungsblattEintrag|GleichungsblattEintrag]], im Rechenwerk.

Ohne Thema: seine Formeln sind die des Benutzers und stehen schon als
Liste da -- die Formelsammlung sammelt die des Werkzeugs.

#### Gleichungsblatt.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll)
```

#### Gleichungsblatt.ausfuehren

```python
def ausfuehren(self, e: Eingaben, p: Protokoll) -> Dict[str, Wert]
```

Wie jede Berechnung -- und dazu, was die Zeilen ergeben haben, damit es
in der Loesung steht (siehe oben). Die Beschreibung bekommen die Werte
erst hier: in der Herleitung stuende sie sonst als Titel ueber jeder
Zeile.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.gleichungen.ausdruck]]
- [[opencivil.projekt.gleichungen]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
