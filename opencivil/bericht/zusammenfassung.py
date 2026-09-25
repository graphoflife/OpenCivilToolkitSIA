"""
opencivil/bericht/zusammenfassung.py -- was in der Zusammenfassung steht.

VERANTWORTUNG:
Je Platte die gefuehrten Urteile und darunter die still verfehlten; dazu,
was ueber der Nachweistabelle steht (Angaben zur Platte, Bewehrung) und was
darunter (Hinweise, stille Maengel). Als Bloecke und Saetze, nicht als
Aussehen: dieselben Stuecke setzt die Oberflaeche
(:func:`opencivil.web.api.zusammenfassungen`) und der Bericht
(:func:`opencivil.bericht.gliederung.bericht`), jede Darstellung auf ihre Art.

WARUM EIN EIGENES MODUL:
Vorher baute jede Darstellung ihre Zeilen selbst, und sie liefen schon
auseinander, bevor jemand es merkte: die Oberflaeche nannte einen still
verfehlten Nachweis mit seinem ausgeschriebenen Namen, die Konsole mit dem
langen Urteilsnamen; die eine liess leere Platten weg, die andere nicht; der
Bericht fasste die Nachweise flach zusammen, ohne Platten, sodass zwei
Kombinationen «Feld» zweier Platten nicht zu unterscheiden waren. Welche
Urteile zu einer Platte gehoeren, wie ein Nachweis in der Spalte heisst und
was unter der Tabelle steht, steht jetzt hier und nur hier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

from opencivil.core.berechnung import NachweisUrteil
from opencivil.core.einheiten import MM, Groesse
from opencivil.core.latex import Mathe, Zelle, als_text
from opencivil.core.protokoll import GleichungBlock, TabellenBlock
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.querschnitt.platte import BREITE_Y_MM

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau, QuerschnittEintrag


@dataclass(frozen=True)
class Zeile:
    """Ein Urteil, wie es in der Zusammenfassung steht."""

    nachweis: str
    """Die Nachweisart ausgeschrieben -- faellt sie aus, das Kuerzel, dann der Name."""

    fall: str
    """Der Fall oder die Lage; leer, wo es keinen gibt."""

    widerstand: Optional[Wert]
    einwirkung: Optional[Wert]
    urteil: NachweisUrteil
    """Fuer alles Weitere: erfuellt, Grad, Begruendung, Hinweis."""

    @classmethod
    def aus(cls, urteil: NachweisUrteil) -> "Zeile":
        return cls(nachweis=urteil.langname or urteil.art or urteil.name,
                   fall=urteil.fall, widerstand=urteil.widerstand,
                   einwirkung=urteil.einwirkung, urteil=urteil)

    @property
    def bezeichnung(self) -> str:
        """Nachweis und Fall in einem -- fuer einen Satz, wo keine Spalten sind."""
        return " – ".join(teil for teil in (self.nachweis, self.fall) if teil)


@dataclass(frozen=True)
class Platte:
    """Die Zusammenfassung einer Platte."""

    kennung: str
    name: str
    """Leer fuer die eine Gruppe eines Rechenwerks ohne Platten."""

    zeilen: List[Zeile]
    """Die gefuehrten Urteile -- je Nachweis mit Lagen nur die schlechtere."""

    stille: List[Zeile]
    """Was ausgeschaltet ist und trotzdem nicht aufgeht."""

    @property
    def leer(self) -> bool:
        return not self.zeilen and not self.stille


@dataclass(frozen=True)
class Zusammenfassung:
    """Alle Platten, das Gesamturteil und was beim Aufbau auffiel."""

    platten: List[Platte]
    erfuellt: bool
    """Ob alle gefuehrten Nachweise aufgehen."""

    gefuehrt: bool
    """Ob ueberhaupt einer gefuehrt wurde -- sonst gibt es kein Gesamturteil."""

    warnungen: List[str]


def zusammenfassen(aufbau: Optional["Aufbau"], loesung: Loesung) -> Zusammenfassung:
    """
    Die Zeilen je Platte, in der Reihenfolge der Beschreibung.

    Die Urteile kommen fertig aus der Loesung: ohne die stillen, und je
    Nachweis, der seine Lagen sammelt, nur die schlechteste. Hier zu filtern
    hiesse, diese Regel ein zweites Mal zu schreiben.

    Ohne Aufbau -- ein Rechenwerk, das keine Platten kennt -- stehen alle
    Urteile in einer Gruppe ohne Namen. Ein Weg fuer beide Faelle, nicht zwei.
    """
    if aufbau is None:
        platten = [Platte(
            kennung="", name="",
            zeilen=[Zeile.aus(u) for u in loesung.gefuehrte_urteile],
            stille=[Zeile.aus(u) for u in loesung.stille_maengel],
        )]
    else:
        platten = [
            Platte(
                kennung=kennung,
                name=querschnitt.name,
                zeilen=[Zeile.aus(u) for u in
                        aufbau.urteile_von(kennung, loesung.gefuehrte_urteile)],
                stille=[Zeile.aus(u) for u in
                        aufbau.urteile_von(kennung, loesung.stille_maengel)],
            )
            for kennung, querschnitt in aufbau.querschnitte.items()
        ]
    return Zusammenfassung(
        platten=platten,
        erfuellt=loesung.alle_nachweise_erfuellt,
        gefuehrt=bool(loesung.gefuehrte_urteile),
        warnungen=list(aufbau.warnungen) if aufbau is not None else [],
    )


# ===========================================================================
# Die Nachweistabelle
# ===========================================================================

#: Eine Spalte *Urteil* gibt es nicht: sie stand neben dem Erfuellungsgrad
#: und sagte dasselbe noch einmal. *Nachweis* und *Bezeichnung* stehen
#: dagegen getrennt -- vorher stand dort ``M-N: Feld``, und zwei Kombinationen
#: gleichen Namens in x und y ergaben zweimal dieselbe Zeile.
NACHWEISKOPF: List[Zelle] = [
    "Nachweis", "Bezeichnung", "Widerstand", "Einwirkung", Mathe(r"\alpha_{eff}"),
]

#: Welche Spalte den Erfuellungsgrad traegt. Die Oberflaeche hinterlegt genau
#: sie -- zaehlen statt raten, sonst haenge die Einfaerbung an der Reihenfolge
#: der Kopfzeile.
GRAD_SPALTE = 4

#: Nachweis und Bezeichnung duerfen umbrechen: mit zwei Formeln daneben
#: liefe die Tabelle im Bericht sonst ueber den Rand.
AUSRICHTUNG = "LLrrr"


def _groesse(wert: Optional[Wert]) -> Zelle:
    """Feste Stellenzahl -- in einer Spalte steht immer dieselbe Groesse."""
    if wert is None:
        return "–"
    zahl = wert.groesse.in_einheit(wert.einheit)
    return Mathe(rf"{wert.symbol} = {zahl:.{wert.definition.stellen}f}"
                 rf"{wert.einheit.als_latex()}")


def nachweistabelle(platte: Platte) -> TabellenBlock:
    """Je gefuehrtes Urteil eine Zeile, in der Folge von :attr:`Platte.zeilen`."""
    return TabellenBlock(
        kopf=NACHWEISKOPF,
        zeilen=[[z.nachweis, z.fall or "–", _groesse(z.widerstand),
                 _groesse(z.einwirkung), Mathe(z.urteil.gradtext(latex=True))]
                for z in platte.zeilen],
        ausrichtung=AUSRICHTUNG,
    )


def hinweise(platte: Platte) -> List[str]:
    """
    Was unter der Tabelle stehen muss, nach Grund gebuendelt.

    Nur was eine Pruefung ausdruecklich meldet (siehe
    :attr:`NachweisUrteil.hinweis`): ein Widerstand von null erklaert sich
    nicht von selbst. Eine ganze Tragrichtung ohne Bewehrung laesst aber jeden
    ihrer Nachweise aus demselben Grund ausfallen -- sechsmal derselbe Satz
    waere keine Erklaerung, sondern eine Wand.
    """
    nach_grund: Dict[str, List[str]] = {}
    for zeile in platte.zeilen:
        if zeile.urteil.hinweis:
            nach_grund.setdefault(zeile.urteil.hinweis, []).append(zeile.bezeichnung)
    return [f"{', '.join(namen)}: {grund}" for grund, namen in nach_grund.items()]


def stiller_hinweis(zeile: Zeile) -> str:
    """
    Ein ausgeschalteter Nachweis, der nicht aufgeht -- als Satz.

    Er steht weder in der Tabelle noch in der Herleitung. Die Begruendung ist
    darum das Einzige, was sagt, woran es fehlt.
    """
    grad = zeile.urteil.gradtext()
    satz = (f"{zeile.bezeichnung}: nicht erfüllt"
            + (f" (α_eff = {grad})" if grad else "")
            + ". Dieser Nachweis ist ausgeschaltet und steht nicht in der "
              "Herleitung.")
    return f"{satz} {zeile.urteil.begruendung}".rstrip()


# ===========================================================================
# Ueber der Tabelle
# ===========================================================================


def plattenangaben(qs: "QuerschnittEintrag") -> GleichungBlock:
    """
    Beton, Dicke und betrachtete Breite -- eine Zeile ueber der Tabelle.

    Die Breite in y steht nur da, wenn sie von der eingegebenen abweicht.
    Sonst waere es bei jeder Platte dieselbe Zahl zweimal.
    """
    latex = (rf"{als_text('Beton ' + qs.beton.name)} \qquad "
             rf"h = {qs.h.als_latex(0, MM)} \qquad "
             rf"b_x = {qs.b.als_latex(0, MM)}")
    if abs(qs.b.si - BREITE_Y_MM / 1000.0) > 1e-9:
        latex += rf" \qquad b_y = {Groesse(BREITE_Y_MM, MM).als_latex(0, MM)}"
    return GleichungBlock(latex=latex, titel="Angaben zur Platte")


def bewehrungsuebersicht(qs: "QuerschnittEintrag") -> TabellenBlock:
    """
    Überdeckungen und Lagen, wie man die Platte im Schnitt sieht.

    Von oben nach unten gelesen: obere Überdeckung, 4. bis 1. Lage, untere
    Überdeckung. Dieselbe Folge wie in der Eingabemaske -- wer beides
    nebeneinander hat, soll nicht umdenken müssen.

    Grundbewehrung und Zulage stehen in einer Zeile, getrennt durch ``+`` --
    die Lage ist eine Lage, auch wenn sie aus zwei Posten besteht.
    """
    strich = "–"

    def menge(posten) -> str:
        if not posten.vorhanden:
            return ""
        durchmesser = rf"\varnothing {posten.durchmesser.formatiert(0)}"
        if posten.ueber_abstand:
            return rf"{durchmesser}@{posten.abstand.formatiert(0)}"
        return rf"{posten.anzahl:g} \times {durchmesser}"

    zeilen: List[List[Zelle]] = [[
        "Überdeckung oben", strich,
        Mathe(qs.ueberdeckung_oben.als_latex(0, MM)), strich]]
    for lage in reversed(qs.lagen):
        posten = [menge(lage.grund), menge(lage.zulage)]
        vorhanden = [t for t in posten if t]
        zeilen.append([
            f"{lage.nummer}. Lage",
            lage.richtung.value,
            Mathe(" + ".join(vorhanden)) if vorhanden else strich,
            lage.stahl.name if (vorhanden and lage.stahl) else strich,
        ])
    zeilen.append(["Überdeckung unten", strich,
                   Mathe(qs.ueberdeckung_unten.als_latex(0, MM)), strich])

    # Die Bügel stehen am Ende und nicht in der Stapelfolge: sie sitzen über
    # die ganze Höhe und haben darin keinen Platz.
    if qs.hat_buegel:
        b = qs.querkraftbewehrung
        # Kurzform wie bei den Lagen: Durchmesser und die beiden Teilungen,
        # sonst nichts. Der Bügelquerschnitt steht in der Herleitung, wo er
        # auch hergeleitet wird -- in einer Übersicht ist er nur Ballast.
        menge_y = (b.abstand_y.formatiert(0) if b.ueber_abstand_y
                   else rf"{b.anzahl_y:g}\,\text{{Stk}}")
        zeilen.append([
            "Querkraftbewehrung",
            "x/y",
            Mathe(rf"\varnothing {b.durchmesser.formatiert(0)}"
                  rf"@{b.abstand_x.formatiert(0)}@{menge_y}"),
            b.stahl.name if b.stahl else strich,
        ])

    return TabellenBlock(
        kopf=["Lage", "Richtung", "Bewehrung", "Stahl"],
        zeilen=zeilen,
        titel="Bewehrung von oben nach unten",
        ausrichtung="llll",
    )
