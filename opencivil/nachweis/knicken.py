"""
opencivil/nachweis/knicken.py -- Nachweis am verformten System.

VERANTWORTUNG:
Prueft je Knickfall, ob sich unter der Druckkraft ueberhaupt eine
Gleichgewichtslage einstellt -- und wenn ja, ob der Querschnitt das dabei
entstehende Moment aufnimmt.

DAS VERFAHREN::

    alpha_i = min[ max(0.01/sqrt(l); 1/300) ; 1/200 ]      Schiefstellung
    e_0d    = max( d/30 ; alpha_i * l_cr/2 )               ungewollte Ausmitte
    e_1d    = |M_Ed,1 / N_Ed|                              gewollte Ausmitte
    e_2d    = |chi| * l_cr^2 / pi^2                        Ausmitte 2. Ordnung

    wiederhole:
        M_ziel = |N| * (e_0d + e_1d + e_2d)
        (eps_m, chi) = Gleichgewicht zu (N, M_ziel)
        e_2d neu aus chi
    bis M_ziel sich nicht mehr aendert

Die Kruemmung haengt am Moment, das Moment an der Ausmitte und die Ausmitte
wieder an der Kruemmung. Es gibt dafuer keine geschlossene Loesung; gesucht
wird der Fixpunkt. Laeuft die Folge ein, gibt es eine Gleichgewichtslage.
Waechst sie, kippt das System -- und zwar nicht wegen einer ueberschrittenen
Spannung, sondern weil es gar kein Gleichgewicht gibt. Genau das ist Knicken.

DER ERFUELLUNGSGRAD IST EIN VERHAELTNIS VON NORMALKRAEFTEN::

    N_Rd = groesste Druckkraft, die der Stab noch traegt
    alpha_eff = N_Rd / |N_Ed|

Gesucht wird ``N_Rd`` durch Halbieren: zu jeder Probekraft laeuft das
Verfahren oben, und getragen ist sie, wenn die Folge einlaeuft *und* der
Querschnitt das dabei entstehende Moment aufnimmt. Die gewollte Ausmitte
``e_1d`` bleibt dabei fest -- sie ist eine Eigenschaft des Systems, nicht der
Last; ``M_Ed,1`` waechst also mit. ``e_0d`` ist rein geometrisch und aendert
sich ohnehin nicht.

Ueber ``M_Rd`` zu vergleichen waere das naechstliegende gewesen und ist
trotzdem falsch: beim Knicken gibt es Faelle, in denen gar kein Moment mehr
herauskommt, weil die Folge davonlaeuft. Dann steht da kein Widerstand,
sondern nichts -- und ein Nachweis ohne Zahl sagt nicht, wie weit er daneben
liegt. Die Normalkraft dagegen hat immer einen Grenzwert.

ZWEI WAHLEN:
Womit gerechnet wird, waehlt das Kapitel zweimal (:class:`Rechenwahl`):

* **Verformung (e_2d)** -- die Gesetze des Loesers, der zu jedem Moment die
  Kruemmung sucht. Immer praezise ohne Vereinfachung, gewaehlt werden
  Kriechzahl und Werte (Vorgabe Bemessungswerte); die Kriechzahl weicht den
  Beton auf, und ein weicher Beton verformt sich mehr. Den Spannungsblock
  gibt es hier nicht mehr (:data:`~opencivil.nachweis.rechenwahl.VERFORMUNGSARTEN`,
  Benutzer, 2026-10-15): mit ihm hat das Moment ueber der Kruemmung flache
  Stuecke, und die Ausmitte ist nahe der Grenzkraft nicht eindeutig.
* **Widerstand (N_Rd)** -- die Resistenzlinie, die sagt, ob der Querschnitt
  das Moment am verformten System aufnimmt. Vorgabe die
  0.85·x-Vereinfachung mit Bemessungswerten. Waehlt das Kapitel dasselbe wie
  die Tragsicherheit, ist es deren Linie; sonst baut es eine eigene, mit
  eigener Herleitung.

Die Handrechnung steht bei keiner der beiden zur Wahl
(:data:`~opencivil.nachweis.rechenwahl.FASERARTEN`): beim Knicken zaehlt
die Normalkraft genau, Ebene fuer Ebene, und ein Polygon aus Eckpunkten
waere hier nur eine schlechtere Vereinfachung. Bis 2026-10-12 war sie die
Vorgabe des Widerstands.

NUR IN X-RICHTUNG:
Ein Knicknachweis braucht eine Knicklaenge, und die gehoert zu einer
Tragrichtung. Gerechnet wird darum nur mit der Bewehrung in x -- in y waere
die Breite der Platte die Laenge, und die ist keine Stuetze.

DER LOESER:
Die Iteration und die Suche nach N_Rd folgen sich in hunderten Ebenen mit
wenig verschiedenen Schnittgroessen. Gesucht werden sie darum mit Illinois,
von der zuletzt gefundenen Ebene aus
(:class:`~opencivil.nachweis.querschnittsloeser.QuerschnittsloeserIllinois`):
an den Pruefprojekten ein Drittel der Faserdurchlaeufe, dieselben
Grenzkraefte auf 0.01 kN. Wo ein Gesetz springt, halbiert der Loeser wie
vorher -- dort ist die Ebene nicht eindeutig; die Verformung rechnet seit
2026-10-15 ohnehin nur noch praezise.

DAS VERFAHREN GEHOERT KEINEM QUERSCHNITT:
Die Iteration und die Suche nach ``N_Rd`` brauchen vom Stab nur dreierlei:
die Ebene zu N und M, den Momentenwiderstand bei N und die statische Hoehe
(:class:`Knickstab`). Sie stehen darum in :class:`Knickverfahren`; die
Platte (:class:`Knicken`) und der gezeichnete Querschnitt
(:class:`~opencivil.nachweis.qa_knicken.KnickenQA`) sagen, woher die drei
kommen.

WAS IN DIE MITSCHRIFT GEHOERT:
Die Iteration Durchlauf fuer Durchlauf -- sie *ist* hier das Verfahren und
nicht bloss eine Nullstellensuche, die man auch anders haette machen koennen.
Dazu die Probe, dass die gefundene Dehnungsebene genau diese Schnittgroessen
erzeugt, und die Suche nach ``N_Rd`` als Verfahren beschrieben: von der
laeuft nur das Ergebnis mit, sonst stuenden vierzig Iterationstabellen da.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from opencivil.core.berechnung import (
    Ausfuehrung, Befundbezug, Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
    grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, M, Groesse
from opencivil.core.latex import Mathe, angabe, als_text, bedingung
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.nachweis import dehnungsfaecher
from opencivil.nachweis.biegung_normalkraft import (
    gleiche_linie, linienbezuege, resistenzlinie,
)
from opencivil.nachweis.querschnittsloeser import (
    Faserloeser, Querschnittsloeser, QuerschnittsloeserIllinois, protokoll_verfahren,
    protokoll_wirksamer_modul,
)
from opencivil.nachweis.rechenwahl import (
    Betonkennwerte, Rechenart, Rechenwahl, betonbezuege, bezuege_vereinen, gesetze,
    lagenbezuege, protokoll_gesetze, protokoll_rechenwahl, stahllagen, werte_nach_id,
)
from opencivil.nachweis.resistenzlinie import Widerstandslinie
from opencivil.querschnitt.platte import Richtung

#: Die Vorgaben der beiden Wahlen -- siehe Dateikopf.
VERFORMUNG = Rechenwahl(art=Rechenart.PARABEL)
WIDERSTAND = Rechenwahl(art=Rechenart.BLOCK)

#: Groesste Zahl an Durchlaeufen der Ausmitten-Iteration.
DURCHLAEUFE = 40

#: Wann die Iteration als eingelaufen gilt -- Aenderung des Moments.
SCHRANKE = 1e-4

#: Durchlaeufe der Halbierung, die N_Rd sucht. Das Fenster ist so breit wie
#: die getragene Kraft selbst; 14 Schritte bringen es auf deren
#: Sechzehntausendstel, bei 2000 kN also auf ein Zehntel Kilonewton. Jeder
#: weitere Schritt kostet eine vollstaendige Ausmitten-Iteration und aendert
#: nichts mehr an der Zahl, die in der Tabelle steht.
HALBIERUNGEN = 14

#: Wie weit die Suche nach oben gehen darf, als Vielfaches von |N_Ed|. Wer
#: einen Stab mit alpha_eff > 64 baut, hat kein Knickproblem.
OBERGRENZE = 64.0

#: Riegel der Schiefstellung, SIA 262:2025, 4.3.7.
ALPHA_UNTEN = 1.0 / 300.0
ALPHA_OBEN = 1.0 / 200.0

#: Warum die Wahl der Verformung zaehlt -- fuer jeden Knicknachweis derselbe Satz.
VERFORMUNG_NACH_WAHL = (
    "Die Verformung rechnet präzise, mit der Parabel; Kriechzahl und Werte "
    "wählt das Kapitel. Das Kriechen weicht den Beton auf: er verformt sich "
    "mehr, die Ausmitte zweiter Ordnung wächst, und der Stab knickt früher – "
    "φ = 0 läge dann auf der unsicheren Seite. Im Bereich der Gebrauchslasten "
    "unterscheidet sich die Parabel kaum vom linearen Gesetz, in der Nähe der "
    "Grenzlast erheblich, und genau dort entscheidet sich, ob es noch eine "
    "Gleichgewichtslage gibt. Den Spannungsblock gibt es hier nicht: mit ihm "
    "trüge auf flachen Stücken jede Krümmung dasselbe Moment, und die "
    "Ausmitte wäre nicht eindeutig."
)


@dataclass(frozen=True)
class Knickfall:
    """Eine zu pruefende Kombination aus Druckkraft und Moment 1. Ordnung."""

    name: str
    N_Ed: Groesse
    """Druck negativ -- wie ueberall in diesem Werkzeug."""

    M_Ed_1: Groesse
    laenge: Groesse
    knicklaenge: Groesse

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass(frozen=True)
class Durchlauf:
    """Ein Schritt der Ausmitten-Iteration -- eine Zeile der Mitschrift."""

    nummer: int
    e_2d_vorher: float
    """Ausmitte, mit der dieser Durchlauf begonnen hat -- im ersten null."""

    M_ziel: float
    """Moment am verformten System, aus ``e_2d_vorher``."""

    chi: float
    """Kruemmung im Gleichgewicht dazu. ``nan``, wenn es keine gibt."""

    e_2d: float
    """Ausmitte, die aus ``chi`` folgt -- der Start des naechsten Durchlaufs."""


@dataclass
class Gleichgewicht:
    """Was bei einer Probekraft herauskommt."""

    traegt: bool = False
    stabil: bool = False
    """Ob die Ausmitten-Iteration eingelaufen ist."""

    e_2d: float = 0.0
    M_ges: float = 0.0
    M_Rd: float = 0.0
    eps_m: float = 0.0
    chi: float = 0.0
    N_int: float = 0.0
    M_int: float = 0.0
    schritte: List[Durchlauf] = field(default_factory=list)


@dataclass
class Knickergebnis:
    """Alle Zwischenwerte eines Knickfalls."""

    fall: Knickfall
    alpha_i: float = 0.0
    d: float = 0.0
    """Statische Hoehe der untersten x-Lage, in m -- fuer die Mindestausmitte."""

    e_0d: float = 0.0
    e_1d: float = 0.0
    e_2d: float = 0.0
    M_ges: float = 0.0
    """Moment am verformten System, in Nm."""

    eps_m: float = 0.0
    chi: float = 0.0
    N_int: float = 0.0
    M_int: float = 0.0
    durchlaeufe: int = 0
    stabil: bool = False
    M_Rd: float = 0.0
    """Momentenwiderstand bei dieser Normalkraft, in Nm."""

    N_Rd: float = 0.0
    """Groesste Druckkraft mit Gleichgewicht, als Betrag in N."""

    M_bei_N_Rd: float = 0.0
    """
    Das Moment am verformten System bei ``N_Rd``, in Nm.

    Dort liegt der Stab an seiner Grenze, also ist es zugleich sein
    Momentenwiderstand bei dieser Normalkraft -- der Punkt sitzt damit auf
    der Interaktionslinie. Im M-N-Diagramm ist das der Widerstandspunkt des
    Knicknachweises.
    """

    schritte: List[Durchlauf] = field(default_factory=list)
    """Die Ausmitten-Iteration bei N_Ed -- Zeile fuer Zeile."""

    halbierungen: int = 0
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""


@dataclass
class Knickbefund:
    """
    Was der Knicknachweis festhaelt: die Linie seines Widerstands, je Fall
    die Zwischenwerte und den Loeser -- wer nachrechnen will, was bei einer
    anderen Druckkraft herauskaeme, braucht denselben. Steht nach dem Lauf in
    der Loesung, nicht am Nachweis.
    """

    linie: Widerstandslinie
    """
    Die Linie des Widerstands: die eigene, oder mit derselben Wahl die der
    Tragsicherheit -- dasselbe Objekt, einmal gerechnet.
    """

    loeser: Querschnittsloeser
    ergebnisse: List[Knickergebnis] = field(default_factory=list)


def schiefstellung(laenge: float) -> float:
    """``alpha_i = min[ max(0.01/sqrt(l); 1/300) ; 1/200 ]``, ``l`` in m."""
    if laenge <= 0.0:
        return ALPHA_OBEN
    return min(max(0.01 / math.sqrt(laenge), ALPHA_UNTEN), ALPHA_OBEN)


@dataclass(frozen=True)
class Knickstab:
    """Was das Verfahren vom Stab wissen muss -- siehe Dateikopf."""

    loeser: Faserloeser
    """Die Ebene zu einer Normalkraft und einem Moment, fuer die Verformung."""

    moment_bei: Callable[[float, bool], Optional[float]]
    """
    Der Momentenwiderstand bei der Druckkraft ``N`` (Betrag) -- auf der
    Seite des positiven Moments oder der anderen. ``None``, wo es keinen gibt.
    """

    d: float
    """Die statische Hoehe in m, fuer die Mindestausmitte."""


class Knickverfahren(Nachweis):
    """
    Nachweis am verformten System, je Knickfall -- das Verfahren, ohne zu
    sagen, woher der Stab kommt (:class:`Knickstab`).

    Der Nachweis ist erfüllt, wenn die Ausmitten-Iteration einläuft **und**
    der Querschnitt das Moment zweiter Ordnung aufnimmt.
    """

    THEMA = "Knicken"
    widerstand: Rechenwahl
    schnell: bool = False

    # -- Was das Bauteil sagt -----------------------------------------------

    def _m_rd_symbol(self, erg: "Knickergebnis") -> str:
        """Das Zeichen des Momentenwiderstands bei N_Ed in der Herleitung."""
        return f"M_{{{self.widerstand.index}}}(N_{{Ed}})"

    def _falltitel(self, fall: Knickfall) -> str:
        return f"Knicken – {fall.name}"

    # -- Rechnen ------------------------------------------------------------

    def _einen_fall(self, stab: Knickstab, fall: Knickfall) -> Knickergebnis:
        erg = Knickergebnis(fall=fall)
        N_Ed = fall.N_Ed.si
        l_cr = fall.knicklaenge.si

        if N_Ed >= 0.0:
            erg.begruendung = erg.hinweis = "N_Ed ≥ 0, kein Druck → kein Knicknachweis."
            erg.erfuellungsgrad = float("inf")
            erg.erfuellt = True
            return erg

        # Die statische Hoehe -- daraus die Mindestausmitte.
        erg.d = stab.d
        erg.alpha_i = schiefstellung(fall.laenge.si)
        erg.e_0d = max(erg.d / 30.0, erg.alpha_i * l_cr / 2.0)
        # Die gewollte Ausmitte ist eine Eigenschaft des Systems und bleibt
        # bei der Suche nach N_Rd fest -- M_Ed,1 waechst mit der Last.
        erg.e_1d = abs(fall.M_Ed_1.si / N_Ed)

        bei_N_Ed = self._gleichgewicht(stab, abs(N_Ed), erg, l_cr)
        erg.schritte = bei_N_Ed.schritte
        erg.durchlaeufe = len(bei_N_Ed.schritte)
        erg.stabil = bei_N_Ed.stabil
        erg.e_2d = bei_N_Ed.e_2d
        erg.M_ges = bei_N_Ed.M_ges
        erg.M_Rd = bei_N_Ed.M_Rd
        erg.eps_m, erg.chi = bei_N_Ed.eps_m, bei_N_Ed.chi
        erg.N_int, erg.M_int = bei_N_Ed.N_int, bei_N_Ed.M_int

        if self.schnell:
            # Dasselbe Ja oder Nein, nur ohne die Suche: getragen ist N_Ed
            # genau dann, wenn M_Rd fuer M_Ed,II reicht.
            verhaeltnis = (bei_N_Ed.M_Rd / abs(bei_N_Ed.M_ges)
                           if bei_N_Ed.stabil and bei_N_Ed.M_ges else 0.0)
            erg.N_Rd = abs(N_Ed) * verhaeltnis
            erg.M_bei_N_Rd = bei_N_Ed.M_Rd
        else:
            erg.N_Rd = self._grenzkraft(stab, abs(N_Ed), erg, l_cr,
                                        traegt=bei_N_Ed.traegt)
            # Bei N_Rd steht der Stab an seiner Grenze: das Moment am
            # verformten System *ist* dort der Widerstand.
            grenze = self._gleichgewicht(stab, erg.N_Rd, erg, l_cr)
            erg.M_bei_N_Rd = abs(grenze.M_ges) if grenze.stabil else grenze.M_Rd
        erg.erfuellungsgrad = erg.N_Rd / abs(N_Ed)
        erg.erfuellt = bei_N_Ed.traegt
        erg.begruendung = self._begruendung(erg, bei_N_Ed)
        if not bei_N_Ed.stabil:
            erg.hinweis = (
                f"N_Ed = {fall.N_Ed.formatiert(1, KN)} kN: keine Gleichgewichtslage "
                f"→ knickt. N_{self.widerstand.index} = grösste Druckkraft, bei der "
                f"der Stab steht.")
        return erg

    def _begruendung(self, erg: Knickergebnis, gg: Gleichgewicht) -> str:
        idx = self.widerstand.index
        grenze = (f"N_{idx} = {erg.N_Rd / 1e3:.1f} kN "
                  f"{'≥' if erg.erfuellt else '<'} "
                  f"|N_Ed| = {abs(erg.fall.N_Ed.si) / 1e3:.1f} kN.")
        if not gg.stabil:
            return f"Ausmitte läuft nicht ein → knickt. {grenze}"
        return (f"Stabil nach {len(gg.schritte)} Durchläufen: "
                f"e_0d + e_1d + e_2d = {erg.e_0d * 1e3:.1f} + {erg.e_1d * 1e3:.1f} "
                f"+ {erg.e_2d * 1e3:.1f} mm → M_Ed,II = {erg.M_ges / 1e3:.1f} kNm, "
                f"M_{idx} = {erg.M_Rd / 1e3:.1f} kNm. {grenze}")

    # -- Gleichgewicht bei einer Probekraft ---------------------------------

    def _gleichgewicht(self, stab: Knickstab, N: float, erg: Knickergebnis,
                       l_cr: float) -> Gleichgewicht:
        """
        Die Ausmitten-Iteration bei der Druckkraft ``N`` (Betrag).

        Getragen ist ``N``, wenn die Folge einlaeuft **und** der Querschnitt
        das Moment am verformten System aufnimmt. Beides gehoert zusammen: ein
        Stab, der kippt, ist so wenig nachgewiesen wie einer, dessen
        Querschnitt aufreisst.
        """
        gg = Gleichgewicht()
        e_2d = 0.0
        vorher: Optional[float] = None
        for nummer in range(1, DURCHLAEUFE + 1):
            M_ziel = N * (erg.e_0d + erg.e_1d + e_2d)
            ebene = stab.loeser.loese(N_Ed=-N, M_Ed=M_ziel)
            if not ebene.konvergiert:
                # Kein Gleichgewicht zu dieser Ausmitte: der Querschnitt
                # nimmt das Moment nicht mehr auf, die Folge waechst weiter.
                gg.schritte.append(
                    Durchlauf(nummer, e_2d, M_ziel, float("nan"), float("nan")))
                return gg
            neu = abs(ebene.chi) * l_cr * l_cr / (math.pi ** 2)
            gg.schritte.append(Durchlauf(nummer, e_2d, M_ziel, ebene.chi, neu))
            e_2d = neu
            eingelaufen = vorher is not None and abs(M_ziel - vorher) <= (
                SCHRANKE * max(abs(M_ziel), 1.0))
            if eingelaufen:
                gg.stabil = True
                gg.e_2d, gg.M_ges = e_2d, M_ziel
                gg.eps_m, gg.chi = ebene.eps_m, ebene.chi
                gg.N_int, gg.M_int = ebene.N_int, ebene.M_int
                break
            vorher = M_ziel
        else:
            return gg

        # Der Querschnitt muss das Moment am verformten System aufnehmen.
        gg.M_Rd = stab.moment_bei(N, gg.M_ges >= 0) or 0.0
        gg.traegt = gg.M_Rd >= abs(gg.M_ges)
        return gg

    def _grenzkraft(self, stab: Knickstab, N_Ed: float, erg: Knickergebnis,
                    l_cr: float, *, traegt: bool) -> float:
        """
        Die groesste getragene Druckkraft, durch Halbieren.

        Bei ``N = 0`` traegt der Stab immer: mit der Last verschwindet auch
        das Moment, denn ``e_1d`` ist fest. Das ist die untere Schranke, die
        das Halbieren braucht -- sie muss nicht gesucht werden.
        """
        def traegt_bei(N: float) -> bool:
            return self._gleichgewicht(stab, N, erg, l_cr).traegt

        if traegt:
            # Oben suchen: verdoppeln, bis es nicht mehr traegt.
            unten, oben = N_Ed, N_Ed * 2.0
            while oben <= N_Ed * OBERGRENZE and traegt_bei(oben):
                unten, oben = oben, oben * 2.0
            if oben > N_Ed * OBERGRENZE:
                # So weit ueber der Last, dass die Zahl nichts mehr aussagt.
                erg.halbierungen = 0
                return unten
        else:
            unten, oben = 0.0, N_Ed

        for schritt in range(1, HALBIERUNGEN + 1):
            erg.halbierungen = schritt
            mitte = 0.5 * (unten + oben)
            if traegt_bei(mitte):
                unten = mitte
            else:
                oben = mitte
        return unten

    def _urteil(self, erg: Knickergebnis) -> NachweisUrteil:
        # Verglichen werden Normalkraefte: N_Rd ist die groesste Druckkraft,
        # die noch eine Gleichgewichtslage hat. Das Moment zweiter Ordnung
        # steht in der Herleitung -- in der Tabelle waere es die Groesse, die
        # beim Knicken gerade verschwindet.
        machbar = erg.fall.N_Ed.si < 0.0
        # Beide Zahlen als Betrag: ein Widerstand mit umgekehrtem Vorzeichen
        # neben seiner Einwirkung liest sich wie ein Fehler.
        einwirkung = Zwischenwerte(f"{self.id}.{erg.fall.kennung}").kraft(
            "N_Ed", "N_{Ed}", abs(erg.fall.N_Ed.si), "Einwirkung")
        widerstand = self._n_rd(erg)
        return NachweisUrteil(
            art="K",
            ziel=self.d_ausnutzung[erg.fall.name].id,
            fall=erg.fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if machbar else None,
            widerstand=widerstand if machbar else None,
        )

    def _n_rd(self, erg: Knickergebnis) -> Wert:
        """Die Grenzkraft -- der Widerstand in Tabelle und Herleitung."""
        return Zwischenwerte(f"{self.id}.{erg.fall.kennung}").kraft(
            "N_Rd", f"N_{{{self.widerstand.index},K}}", erg.N_Rd, "Widerstand")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_verfahren(self, p: Protokoll) -> None:
        """Was jeder Knicknachweis vorweg schreibt: das Verfahren und seine Ausmitten."""
        p.titel("Knicken")
        p.erklaerung(
            "Nachgewiesen wird am verformten System. Die Ausmitte zweiter "
            "Ordnung hängt von der Krümmung ab, die Krümmung vom Moment und "
            "das Moment wieder von der Ausmitte – also wird die Folge so "
            "lange durchlaufen, bis sie einläuft. Läuft sie nicht ein, gibt es "
            "keine Gleichgewichtslage: das System knickt."
        )
        p.erklaerung(
            "Der Erfüllungsgrad ist ein Verhältnis von Normalkräften: N_Rd "
            "ist die grösste Druckkraft, unter der der Stab noch steht. Über "
            "Momente zu vergleichen ginge nur, solange es ein Gleichgewicht "
            "gibt – beim Knicken ist gerade das der Fall, der fehlt."
        )
        p.ansatz(
            r"\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ "
            rf"\frac{{1}}{{300}}\right);\ \frac{{1}}{{200}}\right] \qquad "
            r"e_{0d} = \max\left(\frac{d}{30};\ "
            r"\frac{\alpha_i \cdot l_{cr}}{2}\right)",
            titel="Ungewollte Ausmitte – allgemein",
            referenz="SIA 262:2025, 4.3.7")
        p.ansatz(
            r"e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad "
            r"e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} "
            r"\qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot "
            r"\left(e_{0d} + e_{1d} + e_{2d}\right)",
            titel="Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein")

    def _protokoll_fall(self, p: Protokoll, erg: Knickergebnis) -> None:
        fall = erg.fall
        p.titel(self._falltitel(fall), ebene=3)
        p.gleichung(
            rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)} \qquad "
            rf"M_{{Ed,1}} = {fall.M_Ed_1.als_latex(1, KNM)} \qquad "
            rf"l = {fall.laenge.als_latex(2)} \qquad "
            rf"l_{{cr}} = {fall.knicklaenge.als_latex(2)}",
            titel="Einwirkung und System")

        if fall.N_Ed.si >= 0.0:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        # Empirisch: die Norm setzt die Stablaenge in Metern ein.
        alpha_i = werte.zahl("alpha_i", r"\alpha_i", erg.alpha_i, stellen=5)
        p.formel(alpha_i,
                 r"\min\left[\max\left(\frac{0.01}{\sqrt{@l}};\ \frac{1}{300}\right);\ "
                 r"\frac{1}{200}\right]",
                 {"l": werte.wert("l", "l", fall.laenge, 2)},
                 titel="Schiefstellung", referenz="SIA 262:2025, 4.3.7",
                 empirisch={"l": M})
        p.formel(werte.laenge("e_0d", "e_{0d}", erg.e_0d),
                 r"\max\left(\frac{@d}{30};\ \frac{@alpha_i \cdot @l_cr}{2}\right)",
                 {"d": werte.laenge("d", "d", erg.d), "alpha_i": alpha_i,
                  "l_cr": werte.wert("l_cr", "l_{cr}", fall.knicklaenge, 2)},
                 titel="Ungewollte Ausmitte", referenz="SIA 262:2025, 4.3.7")
        p.formel(werte.laenge("e_1d", "e_{1d}", erg.e_1d),
                 r"\left|\frac{@M_Ed_1}{@N_Ed}\right|",
                 {"M_Ed_1": werte.moment("M_Ed_1", "M_{Ed,1}", fall.M_Ed_1.si),
                  "N_Ed": werte.kraft("N_Ed", "N_{Ed}", fall.N_Ed.si)},
                 titel="Gewollte Ausmitte")

        self._protokoll_iteration(p, erg)

        if not erg.stabil:
            p.text("Folge läuft nicht ein → keine Gleichgewichtslage unter "
                   "dieser Druckkraft.")
        else:
            p.gleichung(
                r" \qquad ".join([
                    angabe(werte.dehnung("eps_m", r"\varepsilon_m", erg.eps_m, stellen=4)),
                    angabe(werte.kruemmung("chi", r"\chi", erg.chi)),
                    angabe(werte.kraft("N_int", "N_{int}", erg.N_int)) + r" \;\checkmark",
                    angabe(werte.moment("M_int", "M_{int}", erg.M_int)) + r" \;\checkmark",
                ]),
                titel="Probe: die gefundene Ebene erzeugt die Schnittgrössen")
            p.gleichung(
                bedingung(angabe(werte.moment("M_Rd", self._m_rd_symbol(erg), erg.M_Rd)),
                          r"\ge",
                          angabe(werte.moment("M_II", "M_{Ed,II}", abs(erg.M_ges))),
                          erg.M_Rd >= abs(erg.M_ges), mit_urteil=False),
                titel="Querschnitt am verformten System")

        self._protokoll_grenzkraft(p, erg)

    def _protokoll_iteration(self, p: Protokoll, erg: Knickergebnis) -> None:
        """
        Die Ausmitten-Iteration, Durchlauf fuer Durchlauf.

        Anders als bei den Nullstellensuchen im Faserloeser steht sie hier
        vollstaendig da: sie ist nicht ein Weg zum Ergebnis, sondern das
        Verfahren selbst. Dass die Folge einlaeuft, *ist* die Aussage des
        Nachweises -- und das sieht man nur, wenn man die Folge sieht.
        """
        N = abs(erg.fall.N_Ed.si)
        p.ansatz(
            r"e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot "
            r"\frac{l_{cr}^{2}}{\pi^{2}} \qquad "
            r"M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + "
            r"e_{1d} + e_{2d}^{(k-1)}\right)",
            titel="Das Verfahren", referenz="SIA 262:2025, 4.3.7",
            name="Iteration der Ausmitte 2. Ordnung")
        p.erklaerung(
            "Zu jedem Moment wird die Dehnungsebene gesucht, die es im "
            "Gleichgewicht hält; aus deren Krümmung folgt die nächste "
            "Ausmitte. Begonnen wird mit e_2d = 0, also ohne Verformung."
        )
        zeilen = []
        for s in erg.schritte:
            gibts = s.chi == s.chi   # nan ist mit sich selbst nicht gleich
            zeilen.append([
                Mathe(str(s.nummer)),
                Mathe(f"{s.e_2d_vorher * 1e3:.2f}"),
                Mathe(f"{s.M_ziel / 1e3:.2f}"),
                Mathe(f"{s.chi:.5f}") if gibts else "kein Gleichgewicht",
                Mathe(f"{s.e_2d * 1e3:.2f}") if gibts else "–",
            ])
        p.tabelle(
            kopf=[Mathe("k"), Mathe(r"e_{2d}^{(k-1)}\ [\mathrm{mm}]"),
                  Mathe(r"M_{Ed,II}^{(k)}\ [\mathrm{kNm}]"),
                  Mathe(r"\chi^{(k)}\ [\mathrm{m}^{-1}]"),
                  Mathe(r"e_{2d}^{(k)}\ [\mathrm{mm}]")],
            zeilen=zeilen,
            titel=f"Ausmitten-Iteration bei N_Ed = {N / 1e3:.1f} kN",
            ausrichtung="rrrrr",
        )

    def _protokoll_grenzkraft(self, p: Protokoll, erg: Knickergebnis) -> None:
        """
        Der Erfuellungsgrad -- und wie N_Rd gefunden wurde.

        Von der Halbierung steht nur das Verfahren da. Jede Probekraft zieht
        eine eigene Ausmitten-Iteration nach sich; die alle abzudrucken hiesse,
        dreissig Tabellen fuer eine einzige Zahl zu zeigen.
        """
        N_Ed = abs(erg.fall.N_Ed.si)
        p.erklaerung(
            "Gesucht wird die grösste Druckkraft mit Gleichgewichtslage. Die "
            "gewollte Ausmitte e_1d bleibt dabei fest – sie gehört zum System "
            "und nicht zur Last, M_Ed,1 wächst also mit. Bei N = 0 trägt der "
            "Stab immer; von dort aus wird das Fenster halbiert, bis "
            "getragene und nicht getragene Kraft zusammenfallen."
        )
        n_rd = self._n_rd(erg)
        n_ed = Zwischenwerte(f"{self.id}.{erg.fall.kennung}").kraft(
            "N_Ed_betrag", r"\left|N_{Ed}\right|", N_Ed)
        p.gleichung(bedingung(angabe(n_rd), r"\ge", angabe(n_ed), erg.erfuellt,
                              mit_urteil=False),
                    titel="Grenzkraft des Stabes")
        grad_formel(p, self.d_ausnutzung[erg.fall.name], erg.erfuellungsgrad,
                    n_rd, n_ed, erg.erfuellt, mit_urteil=True)


class Knicken(Knickverfahren):
    """
    Nachweis am verformten System, je Knickfall -- an der Platte, nur in
    x-Richtung: die Iteration rechnet mit ihrem Querschnittsloeser, der
    Widerstand kommt aus ihrer Resistenzlinie.
    """

    def __init__(
        self,
        querschnitt,
        faelle: Sequence[Knickfall],
        mn_nachweis,
        *,
        verformung: Rechenwahl = VERFORMUNG,
        widerstand: Rechenwahl = WIDERSTAND,
        schnell: bool = False,
    ) -> None:
        if not faelle:
            raise ValueError("Der Knicknachweis braucht mindestens einen Fall.")
        self.posten = querschnitt.posten_in_richtung(Richtung.X)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': ohne Bewehrung in "
                f"x-Richtung ist kein Knicknachweis möglich.")

        self.querschnitt = querschnitt
        self.richtung = Richtung.X
        self.faelle = list(faelle)
        self.mn = mn_nachweis
        self.verformung = verformung
        self.widerstand = widerstand
        self.eigene_linie = not gleiche_linie(widerstand, mn_nachweis.wahl)
        """
        Ob das Knicken seine eigene Resistenzlinie baut. Mit derselben Wahl
        wie die Tragsicherheit ist es deren Linie -- einmal gerechnet und
        einmal hergeleitet.
        """
        self.schnell = schnell
        """
        Ob die Suche nach N_Rd uebersprungen wird.

        Sie kostet rund fuenfzehn vollstaendige Ausmitten-Iterationen und ist
        damit das Teuerste im ganzen Werkzeug. Fuer das *Urteil* ist sie
        entbehrlich: ``N_Rd >= |N_Ed|`` gilt genau dann, wenn der Querschnitt
        bei ``N_Ed`` das Moment zweiter Ordnung aufnimmt -- erfuellt oder
        nicht kommt also gleich heraus. Nur die Zahl daneben ist eine andere,
        naemlich das Verhaeltnis der Momente statt der Kraefte.

        Eingeschaltet wird das vom Bewehrungswerkzeug, das hunderte Male
        rechnet und nur wissen muss, ob es aufgeht.
        """

        basis = f"{querschnitt.id}.nachweis.knicken"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,K,{als_text(f.name)}}}",
                f"Erfüllungsgrad Knicken – {f.name}",
                "SIA 262:2025, 4.3.7",
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(self.richtung)),
        ] + betonbezuege(verformung.satz, querschnitt.beton) + lagenbezuege(
            self.posten, verformung.satz)
        befunde = []
        if self.eigene_linie:
            bezuege = bezuege_vereinen(
                bezuege, linienbezuege(querschnitt, self.posten, self.richtung, widerstand.satz))
        else:
            # Das Moment bei N liest die Iteration von der Linie des
            # M-N-Nachweises -- als dessen Befund, damit die Abhaengigkeit im
            # Graphen steht. Sonst rechnete ein Teillauf (das Auge) das
            # Knicken ohne Linie.
            befunde.append(Befundbezug("mn", mn_nachweis.id))

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            befunde=befunde,
            titel=f"Knicknachweis – {querschnitt.name}",
            referenz="SIA 262:2025, 4.3.7",
            abschnitt=querschnitt.abschnitt,
        )

    def _m_rd_symbol(self, erg: "Knickergebnis") -> str:
        return f"M_{{{self.widerstand.index},x}}(N_{{Ed}})"

    @staticmethod
    def stab(loeser: Querschnittsloeser, linie: Widerstandslinie) -> Knickstab:
        """
        Die Platte als Stab: ihr Loeser, ihre Resistenzlinie und die statische
        Hoehe der untersten x-Lage. Aus dem Befund wieder zu bauen, wer
        nachrechnen will (``befund.loeser``, ``befund.linie``).
        """
        return Knickstab(
            loeser=loeser, moment_bei=lambda N, positiv: linie.moment_bei(-N, positiv=positiv),
            d=max(l.z for l in loeser.lagen))

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        wahl = self.verformung
        w = Betonkennwerte.aus_eingaben(e, wahl.satz)

        # Jede Lage mit ihrem Stahl; das Fenster reicht im Zug bis zur
        # kleinsten Bruchdehnung der Lagen, an beiden Raendern.
        lagen = stahllagen(self.posten, wahl.satz, werte_nach_id(e))
        # Kriechen weicht den Beton auf; das Gesetz rechnet mit dem wirksamen
        # Modul. eps_c1d und eps_c2d bleiben, wie die Norm sie angibt.
        g = gesetze(wahl, w)
        # Gesucht mit Illinois, von der zuletzt gefundenen Ebene aus: die
        # Iteration und die Suche nach N_Rd folgen sich in hunderten Ebenen
        # mit wenig verschiedenen Schnittgroessen.
        loeser = g.loeser(h=h, b=b, lagen=lagen, eps_druck=w.eps_c2d,
                          klasse=QuerschnittsloeserIllinois)

        self._protokoll_ansatz(p, e, eps_druck=w.eps_c2d, eps_zug=loeser.eps_zug,
                               verdraengt=g.verdraengt, suche=loeser.suche)
        # Schnell rechnet die eigene Linie mit den Schritten der Suche, wie die
        # der Tragsicherheit: sonst zahlte die Bewehrungssuche fuer jede Platte
        # mit Knickfall eine ganze genaue Linie, seit die Handrechnung hier
        # nicht mehr zur Wahl steht.
        linie = (resistenzlinie(
            self.widerstand, e, p, querschnitt=self.querschnitt, posten=self.posten,
            richtung=self.richtung, basis=f"{self.id}.widerstand",
            vorsatz="Widerstand: ", ebene=3, wahltitel="Rechenwahl – Widerstand (N_Rd)",
            schritte=(dehnungsfaecher.SCHRITTE_SUCHE if self.schnell
                      else dehnungsfaecher.SCHRITTE))
            if self.eigene_linie else e.befund("mn").massgebend)
        befund = Knickbefund(linie=linie, loeser=loeser)
        if not self.eigene_linie:
            p.titel("Widerstand", ebene=3)
            protokoll_rechenwahl(p, self.widerstand, f"{self.id}.widerstand",
                                 titel="Rechenwahl – Widerstand (N_Rd)")
            p.text("Dieselbe Wahl wie die Tragsicherheit: der Momentenwiderstand bei "
                   "der Druckkraft kommt aus deren Resistenzlinie.")

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []

        stab = self.stab(loeser, linie)
        for fall in self.faelle:
            erg = self._einen_fall(stab, fall)
            befund.ergebnisse.append(erg)
            self._protokoll_fall(p, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                erg.erfuellungsgrad, EINHEITSLOS)
            urteile.append(self._urteil(erg))

        return Ausfuehrung(ergebnis, urteile, befund)

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, *, eps_druck: float,
                          eps_zug: float, verdraengt: bool, suche: str) -> None:
        self._protokoll_verfahren(p)
        p.titel("Verformung", ebene=3)
        wahl, basis = self.verformung, f"{self.id}.verformung"
        phi = protokoll_rechenwahl(p, wahl, basis, titel="Rechenwahl – Verformung (e_2d)")
        if wahl.art.mit_kriechzahl:
            protokoll_wirksamer_modul(p, e["E_cm"], phi, basis,
                                      titel="Steifigkeit des Betons",
                                      nachsatz=rf"\qquad {angabe(e[wahl.satz.beton])}")
        protokoll_gesetze(p, wahl, e, basis, titel="Werkstoffgesetze der Verformung",
                          posten=self.posten)
        p.erklaerung(VERFORMUNG_NACH_WAHL)
        p.titel("Wie die Dehnungsebene gefunden wird", ebene=3)
        protokoll_verfahren(p, eps_druck=eps_druck, eps_zug=eps_zug, verdraengt=verdraengt,
                            suche=suche)
        p.erklaerung(
            "Die Ausmitten-Iteration darüber steht dagegen vollständig da, "
            "Durchlauf für Durchlauf: sie ist das Verfahren selbst, und dass "
            "sie einläuft, ist die Aussage des Nachweises."
        )
