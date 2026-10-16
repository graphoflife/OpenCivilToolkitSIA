"""
opencivil/bericht/zusammenfassung.py -- was in der Zusammenfassung steht.

VERANTWORTUNG:
Je Bauteil -- Platte, Querschnittsanalyse oder Grundbruch -- die gefuehrten
Urteile und darunter die still verfehlten; dazu, was ueber der
Nachweistabelle steht (Angaben, Bewehrung oder die Faktoren des Grundbruchs)
und was darunter (Hinweise, stille Maengel). Als Bloecke und Saetze, nicht als
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
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import NachweisUrteil
from opencivil.core.einheiten import MM, Groesse
from opencivil.core.latex import Mathe, Zelle, als_text
from opencivil.core.protokoll import GleichungBlock, TabellenBlock
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.geotechnik import grundbruch
from opencivil.querschnitt.platte import BREITE_Y_MM, Plattenquerschnitt

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau


@dataclass(frozen=True)
class Zeile:
    """Ein Urteil, wie es in der Zusammenfassung steht."""

    nachweis: str
    """
    Die Nachweisart ausgeschrieben. Jedes Urteil hat sie: :meth:`Nachweis.rechne`
    stempelt sie auf, aus ``LANGNAME`` oder dem Thema des Nachweises.
    """

    fall: str
    """Der Fall oder die Lage; leer, wo es keinen gibt."""

    widerstand: Optional[Wert]
    einwirkung: Optional[Wert]
    urteil: NachweisUrteil
    """Fuer alles Weitere: erfuellt, Grad, Begruendung, Hinweis."""

    @classmethod
    def aus(cls, urteil: NachweisUrteil) -> "Zeile":
        return cls(nachweis=urteil.langname,
                   fall=urteil.fall, widerstand=urteil.widerstand,
                   einwirkung=urteil.einwirkung, urteil=urteil)

    @property
    def bezeichnung(self) -> str:
        """Nachweis und Fall in einem -- fuer einen Satz, wo keine Spalten sind."""
        return " – ".join(teil for teil in (self.nachweis, self.fall) if teil)


@dataclass(frozen=True)
class Bauteil:
    """Die Zusammenfassung eines Bauteils -- einer Platte oder einer Analyse."""

    kennung: str
    name: str
    """Leer fuer die eine Gruppe eines Rechenwerks ohne Bauteile."""

    zeilen: List[Zeile]
    """Die gefuehrten Urteile -- je Nachweis mit Lagen nur die schlechtere."""

    stille: List[Zeile]
    """Was ausgeschaltet ist und trotzdem nicht aufgeht."""

    art: str = "platte"
    """``platte`` oder ``querschnittsanalyse`` -- was ueber der Tabelle steht,
    haengt daran."""

    @property
    def leer(self) -> bool:
        return not self.zeilen and not self.stille


@dataclass(frozen=True)
class Zusammenfassung:
    """Alle Bauteile, das Gesamturteil und was beim Aufbau auffiel."""

    bauteile: List[Bauteil]
    erfuellt: bool
    """Ob alle gefuehrten Nachweise aufgehen."""

    gefuehrt: bool
    """Ob ueberhaupt einer gefuehrt wurde -- sonst gibt es kein Gesamturteil."""

    warnungen: List[str]


def zusammenfassen(aufbau: Optional["Aufbau"], loesung: Loesung) -> Zusammenfassung:
    """
    Die Zeilen je Bauteil, in der Reihenfolge der Beschreibung: erst die
    Platten, dann die Querschnittsanalysen. Ein Balkensystem fuehrt keine
    Nachweise und hat darum hier keine Gruppe -- seine Ergebnisse stehen in
    seiner Herleitung.

    Die Urteile kommen fertig aus der Loesung: ohne die stillen, und je
    Nachweis, der seine Lagen sammelt, nur die schlechteste. Hier zu filtern
    hiesse, diese Regel ein zweites Mal zu schreiben.

    Ohne Aufbau -- ein Rechenwerk, das keine Bauteile kennt -- stehen alle
    Urteile in einer Gruppe ohne Namen. Ein Weg fuer beide Faelle, nicht zwei.
    """
    if aufbau is None:
        bauteile = [Bauteil(
            kennung="", name="",
            zeilen=[Zeile.aus(u) for u in loesung.gefuehrte_urteile],
            stille=[Zeile.aus(u) for u in loesung.stille_maengel],
        )]
    else:
        bauteile = [
            Bauteil(
                kennung=b.kennung,
                name=b.name,
                zeilen=[Zeile.aus(u) for u in
                        aufbau.urteile_von(b.kennung, loesung.gefuehrte_urteile)],
                stille=[Zeile.aus(u) for u in
                        aufbau.urteile_von(b.kennung, loesung.stille_maengel)],
                art=b.art.name,
            )
            for b in aufbau.bauteile() if b.nachweise
        ]
    return Zusammenfassung(
        bauteile=bauteile,
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

#: Widerstand und Einwirkung: die Oberflaeche setzt sie uebereinander in eine
#: Zelle, der Bericht behaelt beide Spalten.
STAPEL_SPALTEN = (2, 3)

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


def nachweistabelle(bauteil: Bauteil) -> TabellenBlock:
    """Je gefuehrtes Urteil eine Zeile, in der Folge von :attr:`Bauteil.zeilen`."""
    return TabellenBlock(
        kopf=NACHWEISKOPF,
        zeilen=[[z.nachweis, z.fall or "–", _groesse(z.widerstand),
                 _groesse(z.einwirkung), Mathe(z.urteil.gradtext(latex=True))]
                for z in bauteil.zeilen],
        ausrichtung=AUSRICHTUNG,
    )


def hinweise(bauteil: Bauteil) -> List[str]:
    """
    Was unter der Tabelle stehen muss, nach Grund gebuendelt.

    Nur was eine Pruefung ausdruecklich meldet (siehe
    :attr:`NachweisUrteil.hinweis`): ein Widerstand von null erklaert sich
    nicht von selbst. Eine ganze Tragrichtung ohne Bewehrung laesst aber jeden
    ihrer Nachweise aus demselben Grund ausfallen -- sechsmal derselbe Satz
    waere keine Erklaerung, sondern eine Wand.
    """
    nach_grund: Dict[str, List[str]] = {}
    for zeile in bauteil.zeilen:
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
            + ", ausgeschaltet.")
    return f"{satz} {zeile.urteil.begruendung}".rstrip()


# ===========================================================================
# Ueber der Tabelle
# ===========================================================================


def angaben(aufbau: "Aufbau", kennung: str,
            loesung: Loesung) -> Tuple[GleichungBlock, Optional[TabellenBlock]]:
    """
    Was ueber der Nachweistabelle eines Bauteils steht: eine Zeile mit den
    Angaben und eine Tabelle -- bei der Platte ihre Lagen, bei der
    Querschnittsanalyse ihre Staebe und Schubwaende, beim Grundbruch die
    Faktoren der Tragfaehigkeitsformel. Die stehen erst nach dem Rechnen
    fest; darum die Loesung.
    """
    platte = aufbau.querschnitte.get(kennung)
    if platte is not None:
        return plattenangaben(platte), bewehrungsuebersicht(platte, loesung.werte)
    fundament = aufbau.grundbrueche.get(kennung)
    if fundament is not None:
        nachweis = aufbau.grundbruch.get(kennung)
        befund = loesung.befunde.get(nachweis.id) if nachweis is not None else None
        return (grundbruch.angaben(fundament, loesung.werte),
                grundbruch.faktortabelle(befund) if befund is not None else None)
    return aufbau.querschnittsanalysen[kennung].angaben()


@dataclass(frozen=True)
class Kennzahl:
    """Eine Zahl, die eine Platte beschreibt -- gleich welche Lastfaelle es gibt."""

    beschriftung: str
    wert: Wert
    erklaerung: str = ""
    feste_stellen: bool = False
    """Mit allen Stellen, auch nachlaufenden Nullen -- der Vergroesserungsfaktor."""

    @property
    def text(self) -> str:
        """Die Zahl, wie sie dasteht -- ohne Einheit."""
        if self.feste_stellen:
            return f"{self.wert.groesse.in_einheit(self.wert.einheit):.{self.wert.definition.stellen}f}"
        return self.wert.formatiert()


#: Die Kennzahlen einer Platte, in dieser Folge: Kurzname in
#: :class:`~opencivil.nachweis.kennzahlen.Plattenkennzahlen`, Beschriftung,
#: Erklaerung.
_HAND = "Handrechnung mit Bemessungswerten"
_KENNZAHLEN = (
    ("M_Rd_pos", "Momentenwiderstand, Zug unten", _HAND),
    ("M_Rd_neg", "Momentenwiderstand, Zug oben", _HAND),
    ("N_Rd_zug", "Zugwiderstand", _HAND),
    ("N_Rd_druck", "Druckwiderstand", _HAND),
    ("x_d_pos", "Bezogene Druckzonenhöhe, Zug unten", _HAND),
    ("x_d_neg", "Bezogene Druckzonenhöhe, Zug oben", _HAND),
    ("V_Rd_max", "Querkraftwiderstand ohne Bügel, grösster",
     "N_Ed = 0, M_Ed = 0 – das Kleinere beider Seiten"),
    ("V_Rd_min", "Querkraftwiderstand ohne Bügel, kleinster",
     "N_Ed = 0, M_Ed = M_Rd – das Kleinere beider Seiten"),
    ("V_Rd_buegel", "Querkraftwiderstand mit Bügeln",
     "N_Ed = 0, günstigste Neigung – das Kleinere beider Seiten"),
)


def kennzahlen(aufbau: "Aufbau", kennung: str, loesung: Loesung) -> List[Kennzahl]:
    """
    Die Kennzahlen einer Platte, wie Zusammenfassung und Bericht sie zeigen:
    Bewehrungsmass und Distanzhalter, die Vergroesserungsfaktoren omega_w und
    omega_w', die Eckwerte der Handrechnung und der Querkraftwiderstand bei
    N_Ed = 0 (Benutzer, 2026-10-16). Was nicht gerechnet wurde -- eine
    Platte ohne x-Bewehrung --, fehlt.
    """
    platte = aufbau.querschnitte.get(kennung)
    if platte is None:
        return []
    zeilen: List[Kennzahl] = []

    def dazu(beschriftung: str, wert_id: str, erklaerung: str = "",
             feste_stellen: bool = False) -> None:
        wert = loesung.werte.get(wert_id)
        if wert is not None:
            zeilen.append(Kennzahl(beschriftung, wert, erklaerung, feste_stellen))

    dazu("Bewehrungsmass", platte.id_von("bewehrungsmass"), "Stahldichte 7850 kg/m³")
    dazu("Höhe der Distanzhalter", platte.id_von("distanzhalter"),
         "OK innere untere Lage bis UK innere obere Lage")
    faktor = aufbau.vergroesserung.get(kennung)
    for seite, definition in (faktor.d_omega.items() if faktor else ()):
        dazu(f"Vergrösserungsfaktor, Zug {seite}", definition.id,
             "SIA 262:2025, 4.4.3.2.5", feste_stellen=True)
    werte = aufbau.kennzahlen.get(kennung)
    for kurz, beschriftung, erklaerung in (_KENNZAHLEN if werte else ()):
        if kurz in werte.d:
            dazu(beschriftung, werte.d[kurz].id, erklaerung)
    return zeilen


def kennzahlentabelle(zeilen: Sequence[Kennzahl]) -> TabellenBlock:
    """Die Kennzahlen als Tabelle des Berichts: Beschriftung, Zeichen, Wert."""
    return TabellenBlock(
        kopf=["Kennzahl", "Zeichen", "Wert"],
        zeilen=[[k.beschriftung, Mathe(k.wert.symbol),
                 Mathe(rf"{k.text}\,{k.wert.einheit.latex}" if k.wert.einheit.latex
                       else k.text)]
                for k in zeilen],
        titel="Kennzahlen", ausrichtung="llr")


def plattenangaben(qs: Plattenquerschnitt) -> GleichungBlock:
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


def bewehrungsuebersicht(qs: Plattenquerschnitt, werte: Dict[str, Wert]) -> TabellenBlock:
    """
    Überdeckungen und Lagen, wie man die Platte im Schnitt sieht.

    Von oben nach unten gelesen: obere Überdeckung, 4. bis 1. Lage, untere
    Überdeckung. Dieselbe Folge wie in der Eingabemaske -- wer beides
    nebeneinander hat, soll nicht umdenken müssen.

    Grundbewehrung und Zulage stehen in einer Zeile, getrennt durch ``+`` --
    die Lage ist eine Lage, auch wenn sie aus zwei Posten besteht. Zuletzt
    die Höhe ihrer Stabachse über der Unterkante, ``h - z`` aus dem
    Lagenaufbau (Benutzer, 2026-10-16); liegen Grund und Zulage verschieden
    hoch, beide, getrennt durch ``/``.
    """
    strich = "–"
    tiefen: Dict[int, List[float]] = {}
    for lage, _, _, _, z_id in qs.posten_ids:
        if z_id in werte:
            tiefen.setdefault(lage.nummer, []).append(werte[z_id].groesse.si)

    def hoehe(nummer: int) -> Zelle:
        zahlen = [Groesse.aus_si(qs.h.si - z, MM).formatiert(1) for z in tiefen.get(nummer, [])]
        return Mathe(" / ".join(dict.fromkeys(zahlen))) if zahlen else strich

    def menge(posten) -> str:
        if not posten.vorhanden:
            return ""
        durchmesser = rf"\varnothing {posten.durchmesser.formatiert(0)}"
        if posten.ueber_abstand:
            return rf"{durchmesser}@{posten.abstand.formatiert(0)}"
        return rf"{posten.anzahl:g} \times {durchmesser}"

    zeilen: List[List[Zelle]] = [[
        "Überdeckung oben", strich,
        Mathe(qs.ueberdeckung_oben.als_latex(0, MM)), strich, strich]]
    for lage in reversed(qs.lagen):
        posten = [menge(lage.grund), menge(lage.zulage)]
        vorhanden = [t for t in posten if t]
        zeilen.append([
            f"{lage.nummer}. Lage",
            lage.richtung.value,
            Mathe(" + ".join(vorhanden)) if vorhanden else strich,
            lage.stahl.name if (vorhanden and lage.stahl) else strich,
            hoehe(lage.nummer) if vorhanden else strich,
        ])
    zeilen.append(["Überdeckung unten", strich,
                   Mathe(qs.ueberdeckung_unten.als_latex(0, MM)), strich, strich])

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
            strich,
        ])

    return TabellenBlock(
        kopf=["Lage", "Richtung", "Bewehrung", "Stahl", "Höhe ab UK [mm]"],
        zeilen=zeilen,
        titel="Bewehrung von oben nach unten",
        ausrichtung="llllr",
    )
