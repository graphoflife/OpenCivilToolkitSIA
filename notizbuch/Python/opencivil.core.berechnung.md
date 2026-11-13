---
erzeugt: 68aee99a2997
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/berechnung.py
> Berechnungen als Objekte.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/berechnung.py)

## VERANTWORTUNG

Jeder Rechenschritt ist ein Objekt, das weiss, welche Werte es braucht, welche
es liefert, wie gerechnet wird und wie das Ergebnis aufzuschreiben ist.


## DREI AUSPRAEGUNGEN

* [[opencivil.core.berechnung#Formel|Formel]]   -- ein Einzeiler: eine Ausgabe, eine analytische Formel.
* [[opencivil.core.berechnung#Prozedur|Prozedur]] -- ein ganzer Ablauf: mehrere Ausgaben, Iterationen,
  Fallunterscheidungen; schreibt ihren Ablauf selbst ins Protokoll.
* [[opencivil.core.nachweis#Nachweis|Nachweis]] -- ein Vergleich von Einwirkung
  und Widerstand mit Urteil und Erfuellungsgrad; er hat seine eigene Datei.


## VARIANTEN -- WELCHE FORMEL GILT?

?
Oft haengt es von den vorhandenen Eingaben ab, welche Formel anzuwenden ist.
Dafuer duerfen mehrere Berechnungen denselben Wert liefern. Der Loeser waehlt
unter ihnen in zwei Stufen:

1. *Verfuegbarkeit* -- sind alle Pflichteingaben ueberhaupt beschaffbar?
2. *Anwendbarkeit*  -- [[opencivil.core.berechnung#Berechnung.anwendbar|Berechnung.anwendbar]] darf zusaetzlich von den
   tatsaechlichen Zahlenwerten abhaengen (z.B. "nur fuer f_ck \<= 50 N/mm^2").

Die Begruendung der Wahl landet im Protokoll -- der Leser sieht, warum gerade
diese Formel gegriffen hat.


## FEHLER WERDEN NICHT VERSCHLUCKT

Im alten Code fing der Wertzugriff jede Ausnahme ab, warnte und lieferte einen
veralteten Wert zurueck -- eine defekte Formel ergab damit eine plausible
falsche Zahl. Hier fuehrt jeder Rechenfehler zu einem [[opencivil.core.berechnung#BerechnungsFehler|BerechnungsFehler]]
mit Angabe der schuldigen Berechnung; die urspruengliche Ausnahme bleibt als
Ursache erhalten.

## Inhalt

### BerechnungsFehler

```python
class BerechnungsFehler(Exception)
```

Eine Berechnung ist gescheitert. Die Ursache bleibt angehaengt.

### Eingabebezug

```python
@dataclass(frozen=True)
class Eingabebezug
```

Bindet einen lokalen Formelnamen an eine globale Wert-ID.

- `name: str` – Kurzer Name in Formel und Vorlage, z.B. `f_ck`.
- `wert_id: str` – Globale ID des Wertes, z.B. `beton.C30_37.f_ck`.
- `optional: bool = False` – Wenn True, darf der Wert fehlen; die Berechnung prueft mit `hat()`.

### Befundbezug

```python
@dataclass(frozen=True)
class Befundbezug
```

Bindet einen lokalen Namen an den Befund einer anderen Berechnung.

Fuer eine Rechnung, die mehr als eine Zahl einer anderen braucht: die
Querkraft den Momentenwiderstand bei ihrer Normalkraft samt seiner
Herleitung, das Knicken die Resistenzlinie der Tragsicherheit. Der
Loeser rechnet die andere Berechnung vorher und reicht ihren Befund
durch ([[opencivil.core.berechnung#Eingaben.befund|Eingaben.befund]]) -- die Abhaengigkeit steht so im Graphen,
wie ein Wert es tut.

- `name: str`
- `berechnung_id: str`

### Eingaben

```python
class Eingaben(Mapping[str, Wert])
```

Die aufgeloesten Eingaben einer Berechnung, unter ihren lokalen Namen.

Ist selbst eine `Mapping`, damit sie direkt an die LaTeX-Hilfen
weitergereicht werden kann. Die Befunde anderer Berechnungen
([[opencivil.core.berechnung#Befundbezug|Befundbezug]]) stehen daneben, unter [[opencivil.core.berechnung#Eingaben.befund|befund]].

#### Eingaben.befund

```python
def befund(self, name: str) -> Any
```

Der Befund einer anderen Berechnung, unter seinem lokalen Namen.

#### Eingaben.hat

```python
def hat(self, name: str) -> bool
```

Prueft, ob eine optionale Eingabe vorliegt.

#### Eingaben.g

```python
def g(self, name: str) -> Groesse
```

Nur die Groesse -- die Kurzform fuers Rechnen.

#### Eingaben.si_nach_id

```python
def si_nach_id(self) -> Callable[[str], float]
```

Die Zahl einer Eingabe in SI, nach ihrer Wert-ID -- fuer, wer seine
Werte nach ID liest: die Stahllagen der Platte, die Werkstoffe des
gezeichneten Querschnitts. So lesen sie aus einer Loesung wie aus den
Eingaben eines Nachweises.

#### Eingaben.groessen

```python
def groessen(self) -> Dict[str, Groesse]
```

Alle Eingaben als `name -> Groesse`, passend fuer `funktion(**...)`.

#### Eingaben.teilmenge

```python
def teilmenge(self, *namen: str) -> 'Eingaben'
```

Auswahl einzelner Eingaben -- praktisch fuer LaTeX-Vorlagen.

### Ausfuehrung

```python
@dataclass(frozen=True)
class Ausfuehrung
```

Was eine Berechnung in einem Lauf liefert: ihre Ausgaben -- und, wo es
mehr gibt, ihre Urteile und ihren Befund.

Der **Befund** ist alles, was ueber die Ausgabewerte hinausgeht und
spaeter jemand lesen will: Resistenzlinien, Fallergebnisse, das Ergebnis
eines Balkensystems. Er steht nach dem Lauf in der Loesung
([[opencivil.core.rechenwerk#Loesung|befunde]]), nicht am Objekt.
Ein Objekt beschreibt eine Rechnung, eine Loesung haelt fest, was sie
ergab -- so laesst sich eine Loesung aufheben und wiederverwenden, ohne
die Objekte umzuhaengen, die sie hervorgebracht haben.

[[opencivil.core.berechnung#Berechnung.rechne|Berechnung.rechne]] liefert die Ausgaben als Groessen,
[[opencivil.core.berechnung#Berechnung.ausfuehren|Berechnung.ausfuehren]] daraus Werte.

- `ausgaben: Mapping[str, Any]`
- `urteile: Tuple['NachweisUrteil', ...] = ()`
- `befund: Any = None`

### Berechnung

```python
class Berechnung(ABC)
```

Basisklasse aller Rechenschritte.

Unterklassen implementieren [[opencivil.core.berechnung#Berechnung.rechne|rechne]]. Aufgerufen wird immer
[[opencivil.core.berechnung#Berechnung.ausfuehren|ausfuehren]], das die Ergebnisse prueft und in [[opencivil.core.wert#Wert|Wert]] verpackt.

Eine Berechnung darf ohne Ausgabe sein -- ein Nachweis ohne Lastfall, ein
Balkensystem: was sie findet, steht dann allein in ihrem Befund. Zum
Rechnen nennt man sie unter ihrer ID als Ziel (siehe
[[opencivil.core.rechenwerk#Rechenwerk.loese|loese]]).

- `THEMA: str = ''` – Unter welchem Thema ihre Formeln in der Formelsammlung stehen -- ein Nachweis nennt sich selbst. Leer: das Thema ihres Abschnitts.

#### Berechnung.thema

```python
@property
def thema(self) -> str
```

#### Berechnung.ausgabe_ids

```python
@property
def ausgabe_ids(self) -> Tuple[str, ...]
```

#### Berechnung.pflicht_eingaben

```python
@property
def pflicht_eingaben(self) -> Tuple[str, ...]
```

Wert-IDs, ohne die nicht gerechnet werden kann.

#### Berechnung.optionale_eingaben

```python
@property
def optionale_eingaben(self) -> Tuple[str, ...]
```

#### Berechnung.alle_eingaben

```python
@property
def alle_eingaben(self) -> Tuple[str, ...]
```

#### Berechnung.ausgabe_def

```python
def ausgabe_def(self, wert_id: str) -> WertDef
```

#### Berechnung.ausgabe_quelle

```python
@property
def ausgabe_quelle(self) -> Quelle
```

Als was die Ergebnisse gelten sollen.

Normalfall ist `BERECHNET`. [[opencivil.core.berechnung#Vorgabe|Vorgabe]] setzt das auf `VORGABE`,
damit im Bericht erkennbar bleibt, dass hier nichts hergeleitet wurde.

#### Berechnung.anwendbar

```python
def anwendbar(self, eingaben: Eingaben) -> Tuple[bool, str]
```

Darf diese Variante mit diesen Werten verwendet werden?

Standardmaessig ja. Ueberschreiben, wenn die Gueltigkeit vom Zahlenwert
abhaengt, z.B.:

```
def anwendbar(self, e):
    if e.g("f_ck") > Groesse(50, MPA):
        return False, "gilt nur bis C50/60"
    return True, "f_ck liegt im Gueltigkeitsbereich"
```

:return: (anwendbar, Begruendung fuers Protokoll)

#### Berechnung.rechne

```python
@abstractmethod
def rechne(self, e: Eingaben, p: Protokoll) -> Union[Mapping[str, Groesse], Ausfuehrung]
```

Fuehrt die Rechnung aus und schreibt sie ins Protokoll.

:param e: aufgeloeste Eingaben unter ihren lokalen Namen
:param p: Mitschrift -- hier wird die Herleitung festgehalten
:return: `{Wert-ID: Groesse}` fuer jede deklarierte Ausgabe --
oder eine [[opencivil.core.berechnung#Ausfuehrung|Ausfuehrung]] mit diesen Groessen, wo es dazu
Urteile oder einen Befund gibt

#### Berechnung.ausfuehren

```python
def ausfuehren(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

Ruft [[opencivil.core.berechnung#Berechnung.rechne|rechne]] auf und prueft dessen Ergebnis.

Verpackt jede Groesse in einen [[opencivil.core.wert#Wert|Wert]] mit der deklarierten
Definition -- dabei wird auch die Dimension geprueft. Urteile und
Befund reicht es unveraendert durch.

### Formel

```python
class Formel(Berechnung)
```

Eine Ausgabe, eine analytische Formel.

Die Vorlage wird nur *analytisch* geschrieben; die Fassung mit Zahlen und
Einheiten entsteht daraus automatisch:

```python
Formel(
    id="beton.C30_37.f_cd",
    ausgabe=f_cd_def,
    eingaben={"eta_fc": "beton.C30_37.eta_fc",
              "f_ck":   "beton.C30_37.f_ck",
              "gamma_c":"beton.C30_37.gamma_c"},
    vorlage=r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}",
    funktion=lambda eta_fc, f_ck, gamma_c: eta_fc * f_ck / gamma_c,
)
```

ergibt im Bericht:

```
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
       = \frac{0.933 \cdot 30\,\mathrm{N/mm^2}}{1.5}
       = 18.7\,\mathrm{N/mm^2}
```

#### Formel.anwendbar

```python
def anwendbar(self, eingaben: Eingaben) -> Tuple[bool, str]
```

#### Formel.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

### Vorgabe

```python
class Vorgabe(Berechnung)
```

Liefert einen festen Wert ohne Herleitung -- Normvorgabe oder Vorlagenwert.

Erlaubt es, auch Konstanten (Teilsicherheitsbeiwerte, Tabellenwerte) als
ordentliche Knoten im Rechengraph zu fuehren, statt sie im Code zu
verstecken. Der Benutzer kann sie damit ueberall gleich ueberschreiben.

#### Vorgabe.ausgabe_quelle

```python
@property
def ausgabe_quelle(self) -> Quelle
```

#### Vorgabe.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

### Prozedur

```python
class Prozedur(Berechnung)
```

Ein mehrstufiger Ablauf: Iterationen, Fallunterscheidungen, mehrere Ausgaben.

Unterklassen implementieren [[opencivil.core.berechnung#Prozedur|rechne]] und schreiben dabei ihren Ablauf
ins Protokoll -- Ansatz, Startwerte, Zwischenschritte (gerne als Tabelle),
Abbruchkriterium, Ergebnis. Der Leser muss die Rechnung von Hand
nachvollziehen koennen; nur das Endergebnis auszugeben genuegt nicht.

Beispielgeruest:

```
class Nulllinienlage(Prozedur):
    def rechne(self, e, p):
        p.text("Die Nulllinie wird iterativ aus dem Kraeftegleichgewicht bestimmt.")
        zeilen = []
        for schritt in range(...):
            ...
            zeilen.append([Mathe(str(schritt)), Mathe(x.formatiert(1)),
                           Mathe(fehler.formatiert(2))])
        p.tabelle([Mathe("i"), Mathe("x"), Mathe(r"\Delta F")], zeilen,
                  titel="Iterationsverlauf")
        p.formel(...)
        return {...}
```


## Konstanten

- `FormelFunktion = Callable[..., Union[Groesse, EmpirischesErgebnis]]` – Eine Rechenfunktion bekommt die Eingaben als Groessen unter ihren lokalen Namen und liefert eine Groesse -- oder ein EmpirischesErgebnis, wenn die Normformel dimensionell inhomogen ist.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.decke.werk]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.lagennachweis]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]
