"""
opencivil/stabwerk/stellen.py -- die massgebenden Stellen eines Balkensystems fuer einen Querschnitt.

VERANTWORTUNG:
Aus dem Befund eines ebenen oder raeumlichen Balkensystems je Kombination
die Stellen, an denen die Schnittgroessen einer Gruppe von Staeben
massgebend sind (:func:`massgebende_stellen`) -- fuer die Nachweise einer
Querschnittsanalyse, deren Querschnitt diese Staebe haben (Plan vom
2026-11-27, Schritt 12). Dazu ihre Herleitung (:class:`Stellenherleitung`).

DIE STELLEN:
Je Kombination und ueber alle gewaehlten Staebe zusammen: das groesste und
das kleinste M_y, M_z und N, das groesste |V_z|, |V_y| und |T|
(:data:`KRITERIEN`) -- je mit den uebrigen Schnittgroessen an derselben
Stelle. Springt dort etwas, gilt jede Seite, auf der die Schnittgroesse
ihren Extremwert hat -- unter einer Einzellast beim groessten Moment also
beide --, und der Name sagt sie. Was ueberall null ist, gibt
keine Stelle -- in der Ebene M_z, V_y und T --, und eine Stelle, die
mehreres zugleich ist, steht einmal da, mit allen Gruenden. Bei gleichen
Werten gilt die vorderste Stelle des ersten Stabs
(:func:`~opencivil.stabwerk.verlauf.grenzwerte`). Die Folge: die
Kombinationen wie im System, darin die Gruende wie in :data:`KRITERIEN`.

VORZEICHEN -- NACH VORGABE, NICHT NACHGESCHLAGEN:
Die Stellen tragen die Vorzeichen der Querschnittsanalyse
(:data:`IN_DER_ANALYSE`): der Querschnitt vom Anfang des Stabs her gesehen,
seine Unterseite auf der gestrichelten Faser. Dann sind ``N``, ``V_z``,
``M_y`` und ``T`` die des Stabs (:mod:`~opencivil.stabwerk.verlauf`) --
in der Ebene ``N``, ``V`` und ``M`` von Hand --, ``M_z`` und ``V_y`` haben
das andere Vorzeichen: ein positives ``M_z`` des Stabs zieht an seiner
Seite ``+y``, von seinem Anfang her gesehen rechts, das der Analyse links.

EINHEITEN:
SI-Basis: N, Nm, m.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import MM
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.core.sprache import aufgezaehlt
from opencivil.stabwerk.verlauf import SCHNITTGROESSEN, Extrem, Stabverlauf, grenzwerte

#: Je Schnittgroesse des Stabs ihr Vorzeichen in der Querschnittsanalyse --
#: siehe Dateikopf.
IN_DER_ANALYSE: Dict[str, int] = {"N": 1, "V_y": -1, "V_z": 1, "T": 1, "M_y": 1, "M_z": -1}

#: Welche Stellen massgebend sind, je ``(Groesse, Art)``: ``max`` und ``min``
#: der Wert mit Vorzeichen, ``betrag`` der groesste Betrag -- in dieser Folge
#: stehen ihre Gruende.
KRITERIEN: Tuple[Tuple[str, str], ...] = (
    ("M_y", "max"), ("M_y", "min"), ("M_z", "max"), ("M_z", "min"),
    ("N", "max"), ("N", "min"), ("V_z", "betrag"), ("V_y", "betrag"), ("T", "betrag"),
)

#: Was als null gilt, in N und Nm: darunter gibt eine Groesse keine Stelle.
NULL = 1e-3


def grund(groesse: str, art: str) -> str:
    """Wie ein Kriterium in einem Namen heisst: «max M_y», «max |V_z|»."""
    return f"max |{groesse}|" if art == "betrag" else f"{art} {groesse}"


@dataclass(frozen=True)
class Stelle:
    """Eine massgebende Stelle: wo, warum und die Schnittgroessen dort, mit denen der Analyse."""

    kombination: str
    stab: str
    x: float
    """Wo auf dem Stab, in m ab seinem Anfang."""

    seite: str
    """
    Wo etwas springt, ob die Werte «links» davon gelten, zum Anfang des
    Stabs hin, oder «rechts» -- leer, wo nichts springt.
    """

    werte: Dict[str, float]
    """Je Schnittgroesse (:data:`~opencivil.stabwerk.verlauf.SCHNITTGROESSEN`) ihr Wert in N oder Nm."""

    gruende: Tuple[str, ...] = field(default=())

    @property
    def name(self) -> str:
        """
        Wie sie als Lastfall heisst: «GZT, L3 bei x = 2.50 m», an einem
        Sprung «GZT, L3 bei x = 2.50 m links». Warum sie massgebend ist,
        sagt die Herleitung.
        """
        seite = f" {self.seite}" if self.seite else ""
        return f"{self.kombination}, {self.stab} bei x = {self.x:.2f} m{seite}"


def massgebende_stellen(kombinationen: Sequence[Tuple[str, Mapping[str, Stabverlauf]]],
                        staebe: Sequence[str]) -> List[Stelle]:
    """
    Je Kombination -- ``(Name, je Stab sein Verlauf)`` -- die massgebenden
    Stellen der Staebe ``staebe``, siehe Dateikopf. Ein Stab, den eine
    Kombination nicht kennt, zaehlt dort nicht.
    """
    heraus: List[Stelle] = []
    for name, verlaeufe in kombinationen:
        gewaehlt = {s: verlaeufe[s] for s in staebe if s in verlaeufe}
        if not gewaehlt:
            continue
        je_ort: Dict[Tuple[str, float, bool], Stelle] = {}
        for groesse, art in KRITERIEN:
            wahl = _gewaehlt(gewaehlt, groesse, art)
            if wahl is None:
                continue
            stab, x, wert = wahl
            for seite, werte in _seiten(gewaehlt[stab], x, groesse, wert):
                ort = (stab, round(x, 9), seite)
                alt = je_ort.get(ort)
                gruende = (*(alt.gruende if alt else ()), grund(groesse, art))
                je_ort[ort] = Stelle(name, stab, x, seite, werte, gruende)
        heraus.extend(je_ort.values())
    return heraus


def _gewaehlt(verlaeufe: Mapping[str, Stabverlauf], groesse: str,
              art: str) -> Optional[Tuple[str, float, float]]:
    """Stab, Stelle und Wert eines Kriteriums ueber alle Staebe -- in der Analyse; null: keiner."""
    vorzeichen = IN_DER_ANALYSE[groesse]
    extreme = {stab: _in_der_analyse(v.extrem(groesse), vorzeichen) for stab, v in verlaeufe.items()}
    werte = grenzwerte(extreme)
    w = {"max": werte.groesst, "min": werte.kleinst, "betrag": werte.massgebend}[art]
    if abs(w.wert) < NULL:
        return None
    return w.stab, w.x, w.wert


def _in_der_analyse(extrem: Extrem, vorzeichen: int) -> Extrem:
    """Kleinster und groesster Wert mit dem Vorzeichen der Analyse."""
    if vorzeichen > 0:
        return extrem
    (x_klein, klein), (x_gross, gross) = extrem.kleinst, extrem.groesst
    return Extrem(kleinst=(x_gross, -gross), groesst=(x_klein, -klein))


def _seiten(verlauf: Stabverlauf, x: float, groesse: str,
            wert: float) -> List[Tuple[str, Dict[str, float]]]:
    """
    Die Schnittgroessen an der Stelle, in der Analyse, je mit ihrer Seite
    (:attr:`Stelle.seite`): springt dort etwas, jede Seite, auf der
    ``groesse`` den Wert ``wert`` hat -- sonst eine ohne Seite.
    """
    seiten = [(s, _werte(verlauf.bei(x, links=s == "links"))) for s in ("links", "rechts")]
    (_, links), (_, rechts) = seiten
    if all(_gleich(rechts[g], links[g]) for g in SCHNITTGROESSEN):
        return [("", rechts)]
    return ([(s, w) for s, w in seiten if _gleich(w[groesse], wert)]
            or [min(seiten, key=lambda sw: abs(sw[1][groesse] - wert))])


def _gleich(a: float, b: float) -> bool:
    """Ob zwei Schnittgroessen gleich sind -- bis auf :data:`NULL` und die Rundung."""
    return abs(a - b) <= NULL + 1e-9 * max(abs(a), abs(b))


def _werte(roh: Mapping[str, float]) -> Dict[str, float]:
    # «+ 0.0» macht aus einer gekehrten Null wieder eine: sonst stuende «-0.0» da.
    return {g: IN_DER_ANALYSE[g] * roh[g] + 0.0 for g in SCHNITTGROESSEN}


# ===========================================================================
# Die Herleitung
# ===========================================================================


#: Die Spalten der Tabelle: Groesse, Kopf und Einheit -- die Folge der Felder eines Lastfalls.
SPALTEN: Tuple[Tuple[str, str, str], ...] = (
    ("N", "N", "kN"), ("V_y", "V_y", "kN"), ("V_z", "V_z", "kN"), ("T", "T", "kNm"),
    ("M_y", "M_y", "kNm"), ("M_z", "M_z", "kNm"),
)


class Stellenherleitung(Prozedur):
    """
    Woher die Lastfaelle einer Querschnittsanalyse aus einem Balkensystem
    kommen: das System, die Staebe, die Regel und je Stelle ihre Werte. Sie
    rechnet nichts -- die Stellen stehen fest, bevor die Nachweise gebaut
    werden, denn die laufen ueber sie. Sie liest den Schwerpunkt des
    Querschnitts: dort liegt die Achse des Stabs, und dort wirken auch die
    Lastfaelle der Analyse. So steht sie in der Herleitung nach den Werten
    des Querschnitts.
    """

    THEMA = "Stellen aus dem Balkensystem"

    def __init__(self, id: str, *, system: str, staebe: Sequence[str], wahl: str,
                 stellen: Sequence[Tuple[str, Stelle]], hinweise: Sequence[str],
                 schwerpunkt: Tuple[str, str], **angaben) -> None:
        """
        ``system`` sein Name -- leer, wenn es das System nicht mehr gibt --,
        ``staebe`` die gerechneten, ``wahl`` wie sie gewaehlt sind,
        ``stellen`` je Stelle ihr Name als Lastfall; ``hinweise``, je ein
        Satz, warum es keine gibt oder was fehlt; ``schwerpunkt`` die
        Wert-IDs von ``y_S`` und ``z_S`` des Querschnitts.
        """
        super().__init__(id, ausgaben=[], bezuege=[
            Eingabebezug("y_S", schwerpunkt[0]), Eingabebezug("z_S", schwerpunkt[1])], **angaben)
        self.system, self.staebe, self.wahl = system, list(staebe), wahl
        self.stellen, self.hinweise = list(stellen), list(hinweise)

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Stellen aus dem Balkensystem")
        if not self.stellen:
            p.text(" ".join(["Aus dem Balkensystem kommt kein Lastfall.", *self.hinweise]))
            return Ausfuehrung({})
        regel = ", ".join(grund(g, a) for g, a in KRITERIEN)
        p.text(f"Aus dem Balkensystem «{self.system}»: {self.wahl}, "
               f"{aufgezaehlt(self.staebe)}. Je Kombination über diese Stäbe zusammen die "
               f"Stellen mit {regel} – was überall null ist, gibt keine –, je mit den übrigen "
               f"Schnittgrössen an derselben Stelle. Jede ist ein Lastfall der Nachweise. Wo "
               f"etwas springt, sagt ihr Name die Seite – links zum Anfang des Stabs hin, rechts "
               f"zu seinem Ende –, und hat eine Grösse dort ihren Extremwert auf beiden Seiten, "
               f"zählen beide.")
        for satz in self.hinweise:
            p.hinweis(satz)
        p.annahme(f"Die Achse des Stabs liegt im Schwerpunkt des Querschnitts, "
                  f"y_S = {e.g('y_S').formatiert(1, MM)} mm und "
                  f"z_S = {e.g('z_S').formatiert(1, MM)} mm: dort wirken die Schnittgrössen des "
                  f"Systems wie jeder Lastfall der Analyse.")
        p.annahme("Der Querschnitt ist vom Anfang des Stabs her gesehen, seine Unterseite auf "
                  "der gestrichelten Faser: N, V_z, M_y und T sind die des Systems, M_z und V_y "
                  "haben das andere Vorzeichen (nach Vorgabe, nicht nachgeschlagen).")
        p.tabelle(
            kopf=["Lastfall", "massgebend für",
                  *(Mathe(rf"{k}\ [\mathrm{{{einheit}}}]") for _, k, einheit in SPALTEN)],
            zeilen=[[name, ", ".join(s.gruende),
                     *(Mathe(fest(s.werte[g] / 1e3, 2)) for g, _, _ in SPALTEN)]
                    for name, s in self.stellen],
            titel="Die massgebenden Stellen", ausrichtung="lL" + "r" * len(SPALTEN))
        return Ausfuehrung({})
