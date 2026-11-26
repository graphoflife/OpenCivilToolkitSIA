"""
opencivil/nachweis/querschnittsloeser.py -- Dehnungsebene zu gegebenen Schnittgrössen.

VERANTWORTUNG:
Sucht zu ``(N_Ed, M_Ed)`` die Dehnungsebene ``(eps_m, chi)``, die den
Querschnitt ins Gleichgewicht bringt -- und liefert damit die Spannungen in
jeder Lage.

WARUM EIN EIGENER LOESER:
Mit Normalkraft gibt es keine geschlossene Loesung mehr. Zwei Unbekannte, zwei
Gleichgewichtsbedingungen; das Werkstoffgesetz des Betons ist nichtlinear. Ein
fremdes Paket kaeme dafuer nicht in Frage: dieses Werkzeug laeuft auch im
Browser ueber Pyodide, ohne Abhaengigkeiten.

DAS VERFAHREN:
Zwei ineinandergeschachtelte Suchen. Bei festem ``chi`` waechst
``N(eps_m)`` monoton -- mehr Dehnung heisst mehr Zug --, also laesst sich
``eps_m`` eindeutig so waehlen, dass ``N = N_Ed``. Damit wird ``M`` eine
Funktion von ``chi`` allein, und die waechst ebenfalls monoton. Die aeussere
Suche findet darin die Kruemmung. Wie beide suchen -- halbiert oder mit
Illinois --, bekommt der Loeser mit (:mod:`opencivil.core.suche`), und so
schreibt er es auch in die Mitschrift (:func:`verfahren`).

**Beide Suchen brauchen einen gueltigen Dehnungsbereich.** Jenseits der
Bruchdehnungen geben die Werkstoffgesetze null zurueck; dort ist nichts mehr
monoton, und die Suche findet Scheinloesungen. Das Fenster fuer ``eps_m``
haengt darum von ``chi`` ab -- siehe :meth:`Faserloeser._fenster`.

Beide Suchen sind robust: sie bleiben eingegrenzt, kein Startwert kann
danebenliegen, kein Newton-Schritt kann davonlaufen. Halbiert kosten sie
mehr Auswertungen als ein Newton-Verfahren -- bei rund 60 Fasern und 60
Halbierungen ist das unbedeutend; mit Illinois ein Viertel davon.

WAS IN DIE MITSCHRIFT GEHOERT:
Nicht die Suche, sondern die **Probe**. Geschrieben wird die gefundene Ebene
und der Nachweis, dass mit ihr ``N_int = N_Ed`` und ``M_int = M_Ed``
herauskommt. Wer das nachrechnen will, integriert zwei Mal ueber die Hoehe --
das geht von Hand. Den Weg dorthin muss er nicht nachvollziehen. Dasselbe
Vorgehen wie bei der Neigungssuche des Querkraftnachweises.

Die Probe rechnet der Loeser auch selbst (:meth:`Faserloeser._mit_probe`):
die Suchen enden, wo ihr Fenster eng genug ist, und erst die Probe sagt, ob
dort ``N_Ed`` und ``M_Ed`` herauskommen. Springt ein Gesetz -- der
Spannungsblock --, endet eine Suche auch an einem Sprung, wo es keine Ebene
gibt. Dann ist sie verfehlt (:attr:`Ebene.verfehlt`), und der Nachweis sagt
das statt der Probe. Bis 2026-10-15 stand die Probe dort trotzdem, mit
Haekchen: an einer Platte h = 250 mm, ⌀12 oben und unten, unter
N = -600 kN und M = 14.5 kNm erzeugte die Ebene der 0.85·x-Vereinfachung
mit charakteristischen Werten -170 kN und 1.4 kNm.

VORZEICHEN:
    eps > 0   Zug
    N   > 0   Zug
    M   > 0   Zug unten
``chi`` ist die Kruemmung: ``eps(z) = eps_m + chi * (z - h/2)``, mit ``z`` ab
Oberkante. Ein positives ``chi`` zieht also unten.

JEDER QUERSCHNITT AUS FASERN:
Die Suche braucht nur zweierlei: die Fasern mit ihren Kraeften und die
Dehnungsgrenzen, in denen jede gilt. Das steht in :class:`Faserloeser`.
Beides kommt aus der Interaktion
(:class:`~opencivil.querschnitt.interaktion.Querschnitt`), in einer
Zugrichtung zerlegt: bei der Platte ein Rechteck mit je Lage einem Stab
(:meth:`~opencivil.nachweis.rechenwahl.Gesetze.loeser`), beim gezeichneten
Querschnitt seine Polygone (:mod:`opencivil.spannungsanalyse.schnitt`).
``eps_m`` ist die Dehnung im Bezugspunkt -- bei der Platte auf halber Hoehe,
beim gezeichneten Querschnitt im Schwerpunkt; ``oben`` und ``unten`` sagen,
wo die Raender liegen. Bis 2026-11-20 baute die Platte ihre Fasern und
Grenzen selbst, als Rechteck ein zweites Mal.

EINHEITEN:
Alles in SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Callable, Dict, Optional, Sequence, Tuple

from opencivil.core.protokoll import Zwischenwerte
from opencivil.core.suche import HALBIEREN, Suche, eingrenzen
from opencivil.querschnitt.fasern import FASERN, Dehnungsgrenzen, Faserquerschnitt
from opencivil.querschnitt.gesetzwahl import REFERENZ_KRIECHEN, wirksamer_modul
from opencivil.querschnitt.lagenaufbau import schwerpunkt
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz
from opencivil.querschnitt.zugseite import Zugseite

#: Obergrenze der Schritte, mit denen :meth:`Faserloeser._rand` den Rand des
#: Gleichgewichts sucht; die Suchen nach der Ebene haben ihre eigene
#: (:data:`opencivil.core.suche.SCHRITTE`). Erreicht wird sie fast nie --
#: abgebrochen wird ueber :data:`CHI_SCHRANKE`, sobald das Fenster eng genug
#: ist. Die Zahl steht nur da, damit keine Schleife ewig laeuft.
SCHRITTE = 60

#: Wann das Dehnungsfenster eng genug ist. Der Startbereich ist rund 0.05
#: breit; 1e-11 ist ein Zehntausendstel eines Promille und liegt weit unter
#: allem, was eine Eingabe hergibt. Ohne diese Schranke lief die Bisektion
#: stur sechzig Mal -- die letzten zehn Durchlaeufe aendern in doppelter
#: Genauigkeit nichts mehr und kosten doch jedesmal einen Faserdurchgang.
EPS_SCHRANKE = 1e-11

#: Dasselbe fuer die Kruemmung, in 1/m.
CHI_SCHRANKE = 1e-10

#: Wie genau die gefundene Ebene ihre Schnittgroessen treffen muss -- als Teil
#: der Druckkraft des ganzen Querschnitts bei seiner Grenzstauchung, beim
#: Moment mal seiner Hoehe (:func:`probenschranken`). Die Suchen treffen weit
#: genauer: in den beiden Pruefprojekten bleiben 1684 Ebenen unter 0.4 % der
#: Schranke (2026-10-15). Eine Ebene, die an einem Sprung des Spannungsblocks
#: haengen bleibt, liegt um Hunderte Kilonewton daneben.
PROBE_SCHRANKE = 1e-6


@dataclass(frozen=True)
class Stahllage:
    """
    Eine Bewehrungslage samt ihrem Stahl -- die eine Gestalt, in der jede
    Rechnung am Plattenquerschnitt eine Lage sieht: der Loeser, die genaue
    Resistenzlinie, die Handrechnung, die Spannung-Dehnung-Analyse. Gebaut
    wird sie an einer Stelle,
    :func:`~opencivil.nachweis.rechenwahl.stahllagen`.
    """

    a_s: float
    """Querschnitt in m^2, bezogen auf die betrachtete Breite."""

    z: float
    """Tiefenlage ab Oberkante, in m."""

    stahl: Stahlgesetz
    """
    Der Stahl dieser Lage, mit den Festigkeiten des Wertesatzes -- ``f_yd``
    oder ``f_yk`` im Feld ``f_yd``. Jede Lage traegt ihren eigenen: der Editor
    laesst je Seite einen anderen Stahl waehlen. Bis 2026-10-12 bekam der
    Loeser einen einzigen, den der ersten Lage, und unten B700B mit oben
    B500B rechnete die obere Lage mit f_yd = 609 statt 435 N/mm².
    """

    sorte: str = ""
    """Die Kennung des Stahls (``s1``) -- unter ihr heissen seine Eingaben."""

    stahlname: str = ""
    """Der Name des Stahls («B500B») -- so heisst die Grenze seiner Dehnung."""

    nummer: int = 0
    """Nur zur Zuordnung in der Mitschrift."""

    seite: Optional[Zugseite] = None
    """
    Die Seite, an der die Lage liegt -- bei der Platte unten die 1. und 2.
    Lage (:attr:`~opencivil.querschnitt.platte.Bewehrungslage.seite`). Ohne
    Angabe laesst sie sich nicht je Seite zusammenfassen (:func:`je_seite`).
    """

    text: str = ""
    """Wie die Lage in Tabellen heisst -- «2. Lage Grundbewehrung»."""

    index: str = ""
    """
    Ihr Index in den Symbolen -- ``1,x,g``
    (:attr:`~opencivil.querschnitt.lagenaufbau.Postenbezug.index`), die
    zusammengefasste Lage den ihrer Teile, ``1,x`` (:func:`gemeinsamer_index`).
    """

    teile: Tuple["Stahllage", ...] = ()
    """Woraus sie zusammengefasst ist (:func:`je_seite`) -- fuer die Herleitung ihres Schwerpunkts."""

    vorgespannt: bool = False
    """Ob die Lage ein Spannglied ist -- ihr Stahl ist anders gedehnt als der Beton dort."""


def gemeinsamer_index(teile: Sequence[Stahllage]) -> str:
    """
    Der Index der zusammengefassten Lage: das, was ihre Teile gemein haben.

    Grundbewehrung und Zulage einer Lage heissen ``1,x,g`` und ``1,x,z`` --
    zusammengefasst also ``1,x``. Gehen die Teile auseinander, bleibt der Index
    leer; eine erfundene Bezeichnung waere schlimmer als gar keine.
    """
    staemme = {t.index.rsplit(",", 1)[0] for t in teile if t.index}
    return staemme.pop() if len(staemme) == 1 else ""


def je_seite(lagen: Sequence[Stahllage]) -> Dict[Zugseite, Stahllage]:
    """
    Je Seite eine Lage im Schwerpunkt ihrer Flaechen, unter
    :attr:`Stahllage.seite` -- die eine Regel fuer den Loeser in der
    Handrechnung (:meth:`~opencivil.nachweis.rechenwahl.Gesetze.lagen`) und die
    Resistenzlinie aus Handrechnung (:func:`~opencivil.nachweis.handrechnung.seiten`).
    So rechnen beide «derselbe Querschnitt», wie
    :mod:`~opencivil.querschnitt.gesetzwahl` es verspricht.

    - **Die Seite sagt die Lage, nicht die Tiefe.** Grundbewehrung und
      Zulage derselben Lage liegen auf leicht verschiedenen Hoehen, weil ihre
      Durchmesser verschieden sind. Eine Lage ohne Seite ist ein Fehler.
    - **Eine Seite ohne Flaeche fehlt.** Unten zuerst.
    - **Je Seite ein Stahl.** Zwei liessen sich nicht zu einer Lage machen;
      die Platte hat sie nicht, sie hat einen Stahl fuer alle Lagen
      (Benutzer, 2026-10-24).

    Die zusammengefasste Lage behaelt ihre Teile, den Stahl ihrer Seite und
    den gemeinsamen Index; ihr Name nennt die Teile. Bis 2026-11-10 stand die
    Regel zweimal da und antwortete verschieden: ohne Seite entschied hier
    die Tiefe, in der Handrechnung galt bei zwei Staehlen der schwaechere,
    und eine leere Seite fiel hier weg, dort stand sie mit ihrer Hoehe. Die
    zusammengefasste Lage des Loesers hatte keinen Namen.
    """
    ohne = [l.nummer for l in lagen if l.seite is None]
    if ohne:
        raise ValueError(
            f"Je Seite zusammenfassen geht nur mit Lagen, die ihre Seite kennen – "
            f"{len(ohne)} kennen sie nicht.")
    heraus: Dict[Zugseite, Stahllage] = {}
    for seite in Zugseite:
        teile = tuple(l for l in lagen if l.seite is seite and l.a_s > 0.0)
        if not teile:
            continue
        if any(l.stahl != teile[0].stahl for l in teile):
            raise ValueError(
                f"{seite.value.capitalize()} liegen verschiedene Stähle – je Seite eine Lage "
                f"im Schwerpunkt gibt es nur mit einem.")
        a_s, z = schwerpunkt((l.a_s, l.z) for l in teile)
        heraus[seite] = Stahllage(
            a_s=a_s, z=z, stahl=teile[0].stahl, sorte=teile[0].sorte,
            stahlname=teile[0].stahlname, nummer=teile[0].nummer,
            seite=seite, text=" + ".join(l.text for l in teile),
            index=gemeinsamer_index(teile), teile=teile)
    return heraus


@dataclass(frozen=True)
class Ebene:
    """Die gefundene Dehnungsebene samt Proberechnung."""

    eps_m: float
    """Dehnung auf halber Hoehe."""

    chi: float
    """Kruemmung in 1/m."""

    N_int: float
    M_int: float
    """Was die Ebene tatsaechlich erzeugt -- die Probe."""

    sigma_s: Tuple[float, ...]
    """Stahlspannung je Lage, in Pa."""

    eps_s: Tuple[float, ...]
    """Stahldehnung je Lage."""

    konvergiert: bool = True

    verfehlt: bool = False
    """
    Die Suche lief zu Ende, aber ihre Ebene erzeugt die Einwirkung nicht: sie
    blieb an einem Sprung haengen, wie ihn der Spannungsblock hat. Bei viel
    Druck und wenig Moment liegt der Block immer ganz an einem Rand und gibt
    mehr Moment, als einwirkt -- dazwischen gibt es keine Ebene. Dann ist
    ``konvergiert`` falsch, und ``eps_m`` und ``chi`` sind die Stelle des
    Sprungs, durch die eine Linie laeuft
    (:func:`~opencivil.spannungsanalyse.moment_kruemmung`).
    """

    def bei(self, z: float, h: float) -> float:
        """Die Dehnung in der Tiefe ``z``."""
        return self.eps_m + self.chi * (z - h / 2.0)



def wirksamer_modul_wert(E_cm, phi: float, basis: str):
    """``E_c,eff`` als Zwischenwert der Herleitung, unter ``{basis}.E_c_eff``."""
    return Zwischenwerte(basis).spannung("E_c_eff", "E_{c,eff}",
                                         wirksamer_modul(E_cm.groesse.si, phi))


def protokoll_wirksamer_modul(p, E_cm, phi, basis: str, *, titel: str,
                              nachsatz: str = "") -> None:
    """
    Die Zeile zu :func:`wirksamer_modul`, aus den Werten ``E_cm`` und
    ``phi`` -- fuer jeden Nachweis, der mit dem aufgeweichten Beton rechnet.
    """
    p.formel(wirksamer_modul_wert(E_cm, phi.groesse.si, basis),
             r"\frac{@E_cm}{1 + @phi}", {"E_cm": E_cm, "phi": phi},
             titel=titel, nachsatz=nachsatz, name="Wirksamer Elastizitätsmodul",
             referenz=REFERENZ_KRIECHEN)


def protokoll_verfahren(p, *, eps_c2d: float, suche: Suche,
                        fasern: int = FASERN, verdraengt: bool = True) -> None:
    """
    Der Ablauf der Suche, in die Mitschrift geschrieben.

    Steht hier und nicht bei den Nachweisen, die den Loeser benutzen: sonst
    stuende dieselbe Beschreibung zweimal da, und beim naechsten Eingriff in
    das Verfahren aendert man eine davon.

    Beschrieben wird der *Ablauf*, nicht jeder Zwischenwert. Die Halbierungen
    abzudrucken hiesse, hundert Zeilen zu zeigen, von denen nur die letzte
    etwas behauptet -- und die wird ohnehin durch die Probe belegt. Wie
    gesucht wird, sagt die Suche des Loesers (``suche``, sein
    :attr:`Faserloeser.suche`) -- vorher stand dort immer das Halbieren,
    auch wo mit Illinois gesucht wurde.
    """
    p.erklaerung(
        "Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene "
        "Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der "
        "Mittelebene ε_m und die Krümmung χ – und ihnen stehen zwei "
        "Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen "
        "lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind."
    )
    p.ansatz(
        r"\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}"
        r"\right) \qquad "
        r"N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A "
        r"\qquad "
        r"M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot "
        r"\left(z - \frac{h}{2}\right)\,\mathrm{d}A",
        titel="Dehnungsebene und innere Kräfte", referenz="SIA 262:2025, 4.3.2.3")
    p.erklaerung(
        f"Das Integral über den Beton wird als Summe über {fasern} Fasern "
        f"gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der "
        f"Stahl kommt Lage für Lage dazu, und die von ihm verdrängte "
        f"Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal "
        f"zählt." if verdraengt else
        f"Das Integral über den Beton wird als Summe über {fasern} Fasern "
        f"gleicher Dicke gebildet; der Stahl kommt Lage für Lage dazu. Wie in "
        f"der Handrechnung zählt der Beton auch dort, wo der Stahl liegt."
    )
    p.erklaerung(verfahren(suche))
    p.erklaerung(
        f"Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen der "
        f"Gesetze: der Beton an den Rändern bis {-eps_c2d * 1e3:.1f} ‰ und, "
        f"ist der ganze Querschnitt gedrückt, im Punkt C bis ε_c1d; jeder "
        f"Stahl an seiner Lage bis zu seiner Bruchdehnung ε_ud. Jenseits "
        f"davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht "
        f"mehr monoton, und die Suche liefe auf eine beliebige Stelle "
        f"zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine "
        f"Gleichgewichtslage – dann sagt der Nachweis das und rät nicht."
    )
    p.erklaerung(
        "Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass "
        "die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. "
        "Diese Probe steht bei jedem Fall."
    )
    p.erklaerung(VERFEHLTE_EBENE)


#: Was die Mitschrift ueber eine verfehlte Ebene sagt (:attr:`Ebene.verfehlt`)
#: -- bei der Platte wie am gezeichneten Querschnitt.
VERFEHLTE_EBENE = (
    "Erzeugt die gefundene Ebene die Einwirkung nicht, gibt es zu ihr keine "
    "Ebene, und der Nachweis sagt das, statt die Probe abzuhaken. Das kommt "
    "vor, wo ein Gesetz springt wie der Spannungsblock: bei viel Druck und "
    "wenig Moment liegt der Block immer ganz an einem Rand und gibt mehr "
    "Moment, als einwirkt."
)


def probenschranken(querschnitt: Faserquerschnitt,
                    grenzen: Dehnungsgrenzen) -> Tuple[float, float]:
    """
    Wie weit ``N_int`` und ``M_int`` einer gefundenen Ebene neben dem Ziel
    liegen duerfen (:data:`PROBE_SCHRANKE`): gemessen an der Druckkraft des
    ganzen Querschnitts bei seiner Grenzstauchung, das Moment dazu mal seiner
    Hoehe. Am Querschnitt, nicht an der Einwirkung: wie genau eine Suche
    trifft, haengt an ihm -- eine kleine Last auf einem grossen Querschnitt
    trifft sie nicht genauer.
    """
    # Bei chi = 0 bleibt immer ein Fenster: jede Grenze laesst die Dehnung null zu.
    gestaucht, _ = grenzen.fenster(0.0)
    druck = abs(querschnitt.kraefte(gestaucht, 0.0).N)
    arme = [g.arm for g in grenzen.grenzen]
    return PROBE_SCHRANKE * druck, PROBE_SCHRANKE * druck * (max(arme) - min(arme))


def wie_gesucht(suche: Suche) -> str:
    """
    Wie die beiden geschachtelten Suchen die Stelle finden, als Teil eines
    Satzes: «beide durch Halbieren» -- mit Illinois dazu, dass sie bei der
    zuletzt gefundenen Ebene beginnen.
    """
    if suche.vom_letzten:
        return (f"beide {suche.wie}; beide beginnen bei der Ebene, die zuletzt "
                f"gefunden wurde, und grenzen die Stelle von dort mit wachsenden "
                f"Schritten ein")
    return f"beide {suche.wie}"


def verfahren(suche: Suche) -> str:
    """Wie ein Loeser mit dieser Suche die Ebene findet, in Worten -- fuer die Mitschrift."""
    return (
        f"Gesucht wird in zwei geschachtelten Suchen, {wie_gesucht(suche)}. "
        f"Innen: zu einer festgehaltenen Krümmung χ wird ε_m gesucht, bis N_int "
        f"die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung "
        f"immer mehr Zug bedeutet. Aussen: mit diesem ε_m bleibt ein Moment "
        f"übrig, und χ wird gesucht, bis auch M_int stimmt – hier trägt die "
        f"Monotonie, dass mehr Krümmung mehr Moment heisst.")


class Faserloeser:
    """
    Ein Querschnitt aus Fasern, mit Suche nach der Dehnungsebene.

    ``querschnitt`` sind die Fasern samt Staeben, ``grenzen`` die
    Dehnungsgrenzen, innerhalb derer jedes Gesetz gilt -- mehr braucht die
    Suche nicht. Dazu, was Bilder und Linien vom Querschnitt wissen muessen:
    die Arme der Raender ``oben`` und ``unten`` -- oben ist gedrueckt, wenn
    ein positives Moment wirkt --, die Lagen mit ihrem Stahl, eine je Stab
    der Fasern, und die Spannung des Betons an einer Stelle
    (``beton(arm, eps)``). Wo die Gesetze gelten, sagen allein die Grenzen,
    jede mit ihrem Namen: bis 2026-10-18 trug der Loeser dazu ``eps_druck``
    und ``eps_zug``, ein zweites, groberes Fenster an beiden Raendern, und das
    Bild aus Randdehnungen meldete danach Ebenen als ungueltig, die es nicht
    waren.

    Eine Lage liegt in der Tiefe ``z`` unter dem oberen Rand; ihr Arm ist
    ``z + oben``.

    WIE GESUCHT WIRD:
    ``suche`` (:mod:`opencivil.core.suche`): ohne Angabe halbiert er, von
    vorn. Mit :data:`~opencivil.core.suche.ILLINOIS` faengt er bei der
    Kruemmung und der Dehnung an, die er zuletzt gefunden hat: beim Knicken
    folgen sich viele Ebenen mit wenig verschiedenen Schnittgroessen, und das
    Eingrenzen von der groessten Kruemmung her kostete jede von ihnen mehr als
    die Suche selbst. Halbiert braucht eine Suche rund vierzig Schritte, mit
    Illinois ein Viertel davon.

    **Illinois nur, wo die Ebene eindeutig ist.** Springt ein Gesetz -- der
    Spannungsblock --, hat das Moment ueber der Kruemmung flache Stuecke: dort
    traegt jede Kruemmung dasselbe Moment, und welche gefunden wird, haengt am
    Weg der Suche. Mit dem Gedaechtnis hinge das Ergebnis dann an der
    Reihenfolge der Rechnungen -- an der Stuetze des Pruefprojekts war die
    Grenzkraft so 4200 statt 4099.5 kN. Mit springendem Gesetz halbiert er
    darum von vorn, gleich welche Suche er bekommt -- ausser sie taugt dort
    (:attr:`~opencivil.core.suche.Suche.auch_bei_sprung`): wer den Loeser fuer
    eine einzige Frage baut, hat kein Gedaechtnis, an dem das Ergebnis haengen
    koennte -- so die kippende Nulllinie der Spannung-Dehnung-Analyse
    (:class:`~opencivil.spannungsanalyse.schnitt.KippendeNulllinie`). Gesetze
    ohne Sprung -- Parabel, elastisch -- haben flache Stuecke erst am
    vollplastischen Querschnitt; an den Pruefprojekten bleibt dort jede Zahl,
    wie sie war.
    """

    def __init__(self, *, querschnitt: Faserquerschnitt, grenzen: Dehnungsgrenzen,
                 oben: float = 0.0, unten: float = 0.0, lagen: Sequence[Stahllage] = (),
                 beton: Optional[Callable[[float, float], float]] = None,
                 suche: Suche = HALBIEREN) -> None:
        self.suche = suche if suche.auch_bei_sprung or not querschnitt.springt else HALBIEREN
        """Wie er sucht -- wo ein Gesetz springt, halbierend, siehe oben. Die
        Mitschrift liest es hier, statt die Regel nachzubauen."""
        self._zuletzt: Optional[float] = None
        """Die Kruemmung der zuletzt gefundenen Ebene -- von dort sucht die naechste."""
        self._eps_zuletzt: Optional[float] = None
        """Die zuletzt gefundene Mitteldehnung -- von dort sucht die naechste."""
        self.querschnitt = querschnitt
        self.grenzen = grenzen
        self.oben = oben
        self.unten = unten
        self.h = unten - oben
        self.lagen = list(lagen)
        self.betonspannung = beton
        #: Die inneren Kraefte einer Dehnungsebene -- der Beton ueber Fasern,
        #: der Stahl Lage fuer Lage, siehe :meth:`Faserquerschnitt.kraefte`.
        #: Unmittelbar gebunden statt durch eine Methode gereicht: die
        #: Bisektionen rufen sie hunderttausendfach, und jeder Umweg ist ein
        #: Aufruf mehr.
        self.kraefte = querschnitt.kraefte

    # -- Rueckwaerts --------------------------------------------------------

    def _fenster(self, chi: float) -> Optional[Tuple[float, float]]:
        """
        In welchem Bereich ``eps_m`` liegen darf, damit keine Faser aus dem
        gueltigen Dehnungsbereich faellt -- siehe :meth:`Dehnungsgrenzen.fenster`.
        """
        return self.grenzen.fenster(chi)

    def _eps_zu_normalkraft(self, chi: float, N_ziel: float) -> Optional[float]:
        """
        Die mittlere Dehnung, bei der ``N = N_ziel`` gilt -- bei festem ``chi``.

        Faengt die Suche bei der zuletzt gefundenen an, wird von dort
        eingegrenzt (:meth:`_eps_von`): die Kruemmungen einer Suche liegen
        nahe beieinander, und mit ihnen die Dehnungen. Sonst im ganzen
        Fenster (:meth:`_eps_im_fenster`).
        """
        eps = None
        if self.suche.vom_letzten and self._eps_zuletzt is not None:
            eps = self._eps_von(chi, N_ziel, self._eps_zuletzt)
        if eps is None:
            eps = self._eps_im_fenster(chi, N_ziel)
        if eps is not None:
            self._eps_zuletzt = eps
        return eps

    def _eps_im_fenster(self, chi: float, N_ziel: float) -> Optional[float]:
        """
        Die mittlere Dehnung zu ``N_ziel``, gesucht im ganzen Fenster.

        ``N(eps_m)`` waechst im gueltigen Bereich monoton: mehr Dehnung heisst
        mehr Zug. Die Suche findet die Stelle also sicher, sofern sie im
        Fenster liegt.
        """
        fenster = self._fenster(chi)
        if fenster is None:
            return None
        unten, oben = fenster
        zu_wenig = self.kraefte(unten, chi).N - N_ziel
        if zu_wenig > 0.0:
            return None
        zu_viel = self.kraefte(oben, chi).N - N_ziel
        if zu_viel < 0.0:
            return None
        return self._suchen(lambda eps: self.kraefte(eps, chi).N - N_ziel,
                            unten, oben, EPS_SCHRANKE, zu_wenig, zu_viel)

    def mitteldehnung(self, chi: float, N: float) -> Optional[float]:
        """
        Die Dehnung auf halber Hoehe, bei der die Ebene mit der Kruemmung
        ``chi`` die Normalkraft ``N`` traegt -- ``None``, wo es keine gibt.
        Fuer Linien, die ueber die Kruemmung laufen statt ueber das Moment.
        """
        return self._eps_zu_normalkraft(chi, N)

    def kruemmung(self, eps_m: float, M: float) -> Optional[float]:
        """
        Die Kruemmung, bei der die Ebene mit der Dehnung ``eps_m`` auf halber
        Hoehe das Moment ``M`` traegt -- ``None``, wo es keine gibt.

        Bei fester Dehnung waechst das Moment mit der Kruemmung: die eine
        Seite wird mehr gedehnt, die andere mehr gestaucht. Gesucht wird darum
        wie in :meth:`_eps_zu_normalkraft`, mit der Suche des Loesers, innerhalb
        dessen, was die Grenzen bei dieser Dehnung zulassen.
        """
        fenster = self.grenzen.kruemmungsfenster(eps_m)
        if fenster is None:
            return None
        unten, oben = fenster
        rand = self.grenzen.kruemmungsgrenze(positiv=True)
        unten, oben = max(unten, -self.grenzen.kruemmungsgrenze(positiv=False)), min(oben, rand)
        if unten > oben:
            return None
        zu_wenig = self.kraefte(eps_m, unten).M - M
        zu_viel = self.kraefte(eps_m, oben).M - M
        if zu_wenig > 0.0 or zu_viel < 0.0:
            return None
        return self._suchen(lambda chi: self.kraefte(eps_m, chi).M - M,
                            unten, oben, CHI_SCHRANKE, zu_wenig, zu_viel)

    def loese(self, *, N_Ed: float, M_Ed: float) -> Ebene:
        """
        Die Dehnungsebene zu diesen Schnittgroessen -- von der zuletzt
        gefundenen Kruemmung aus eingegrenzt, wo die Suche dort anfaengt und es
        eine gibt (:meth:`_von_zuletzt`), sonst von vorn (:meth:`_von_vorn`).
        Was die naechste Suche nicht eingrenzen kann oder verfehlt, sucht sie
        von vorn.
        """
        ebene = None
        if (self.suche.vom_letzten and self._zuletzt is not None
                and not (N_Ed == 0.0 and M_Ed == 0.0)):
            ebene = self._von_zuletzt(N_Ed, M_Ed, self._zuletzt)
        if ebene is None or ebene.verfehlt:
            ebene = self._von_vorn(N_Ed, M_Ed)
        if ebene.konvergiert:
            self._zuletzt = ebene.chi
        return ebene

    def _von_vorn(self, N_Ed: float, M_Ed: float) -> Ebene:
        """
        Die Dehnungsebene, gesucht ueber die ganze Kruemmung.

        Aeussere Suche ueber ``chi``: zu jedem ``chi`` wird ``eps_m`` so
        bestimmt, dass die Normalkraft stimmt, und das uebrig bleibende Moment
        gegen ``M_Ed`` gehalten. ``M(chi)`` waechst monoton -- mehr Kruemmung
        heisst mehr Moment --, solange der Querschnitt nicht versagt.
        """
        # Ohne Einwirkung ist die Ebene exakt null. Die Bisektion faende sie
        # nur bis auf ihre Schranken -- ein Rest von 1e-11, der als
        # Stahlspannung von einem Pascal einen Erfuellungsgrad von 3e8 ergab.
        # Nicht mit einem vorgedehnten Spannglied: es zieht schon bei der
        # Dehnung null, und der Querschnitt verformt sich ohne Last.
        if N_Ed == 0.0 and M_Ed == 0.0 and self._null_im_gleichgewicht:
            return self._ergebnis(0.0, 0.0)

        def moment(chi: float) -> Optional[float]:
            eps_m = self._eps_zu_normalkraft(chi, N_Ed)
            if eps_m is None:
                return None
            return self.kraefte(eps_m, chi).M

        # Groesste Kruemmung je Richtung, bei der ueberhaupt noch ein Fenster
        # bleibt (:meth:`Dehnungsgrenzen.kruemmungsgrenze`).
        unten, oben = self._rand(-self.grenzen.kruemmungsgrenze(positiv=False),
                                 N_Ed, moment, M_Ed, nach_oben=False)
        if unten is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)
        oben = self._rand(self.grenzen.kruemmungsgrenze(positiv=True),
                          N_Ed, moment, M_Ed, nach_oben=True)[0]
        if oben is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)

        def zu_viel(chi: float) -> Optional[float]:
            m = moment(chi)
            return None if m is None else m - M_Ed

        # Ein Fehlen im eingegrenzten Fenster sollte nicht vorkommen; wenn
        # doch, lieber ehrlich nicht konvergiert melden als raten.
        chi = self._suchen(zu_viel, unten, oben, CHI_SCHRANKE)
        if chi is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)
        eps_m = self._eps_zu_normalkraft(chi, N_Ed)
        if eps_m is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)
        return self._mit_probe(eps_m, chi, N_Ed, M_Ed)

    @cached_property
    def _null_im_gleichgewicht(self) -> bool:
        """Ob die Ebene null ohne Last im Gleichgewicht ist -- nicht mit einer Vordehnung."""
        null = self.kraefte(0.0, 0.0)
        return null.N == 0.0 and null.M == 0.0

    @cached_property
    def _probenschranken(self) -> Tuple[float, float]:
        """:func:`probenschranken` dieses Querschnitts -- einmal gerechnet."""
        return probenschranken(self.querschnitt, self.grenzen)

    def _mit_probe(self, eps_m: float, chi: float, N_Ed: float, M_Ed: float) -> Ebene:
        """
        Die gefundene Ebene, mit ihrer Probe: erzeugt sie ``N_Ed`` und
        ``M_Ed`` nicht, ist sie verfehlt (:attr:`Ebene.verfehlt`).
        """
        ebene = self._ergebnis(eps_m, chi)
        dN, dM = self._probenschranken
        if abs(ebene.N_int - N_Ed) <= dN and abs(ebene.M_int - M_Ed) <= dM:
            return ebene
        return replace(ebene, konvergiert=False, verfehlt=True)

    def _suchen(self, f: Callable[[float], Optional[float]], unten: float, oben: float,
                schranke: float, f_unten: Optional[float] = None,
                f_oben: Optional[float] = None) -> Optional[float]:
        """
        Wo ``f`` zwischen ``unten`` und ``oben`` null wird -- mit der Suche
        dieses Loesers. ``f_unten`` und ``f_oben`` sind fuer eine Suche, die
        mit ihnen schneller ist (:class:`~opencivil.core.suche.Illinois`).
        """
        return self.suche.finde(f, unten, oben, schranke, f_unten, f_oben)

    def _rand(self, start: float, N_Ed: float,
              moment: Callable[[float], Optional[float]], M_Ed: float,
              *, nach_oben: bool) -> Tuple[Optional[float], None]:
        """
        Eine Kruemmung, bei der das Moment ``M_Ed`` sicher ueber- bzw.
        unterschreitet -- der Startpunkt der aeusseren Bisektion.

        Von der theoretischen Grenze aus wird herangetastet: dort ist das
        Fenster leer oder die Normalkraft nicht erreichbar. Zwanzig
        Halbierungen genuegen, um auf eine loesbare Stelle zu kommen.

        Nahe am Widerstand genuegen sie nicht. Zwischen der letzten Stufe
        ohne Gleichgewicht und der ersten mit -- an der Platte des Beispiels
        0.08 und 0.04 1/m -- liegen Kruemmungen, die das Moment noch
        erreichen, und das Halbieren springt ueber sie hinweg: 234.9 kNm
        hiessen dort «kein Gleichgewicht», obwohl der Querschnitt bis
        235.4 kNm traegt. Trifft das Halbieren nicht, wird darum die Grenze
        zwischen den beiden Stufen gesucht -- die groesste Kruemmung mit
        Gleichgewicht -- und dort noch einmal gefragt. Wo das Halbieren
        trifft, bleibt alles, wie es war.
        """
        def trifft(m: Optional[float]) -> bool:
            return m is not None and ((m >= M_Ed) if nach_oben else (m <= M_Ed))

        chi = start
        ohne: Optional[float] = None   # die letzte Stufe ohne Gleichgewicht
        mit: Optional[float] = None    # die erste mit
        for _ in range(SCHRITTE):
            m = moment(chi)
            if trifft(m):
                return chi, None
            if m is None and mit is None:
                ohne = chi
            elif m is not None and mit is None:
                mit = chi
            chi *= 0.5
            if abs(chi) < 1e-12:
                break
        if trifft(moment(0.0)):
            return 0.0, None
        if ohne is None or mit is None:
            return None, None
        for _ in range(SCHRITTE):
            if abs(ohne - mit) <= CHI_SCHRANKE:
                break
            mitte = 0.5 * (ohne + mit)
            if moment(mitte) is None:
                ohne = mitte
            else:
                mit = mitte
        return (mit, None) if trifft(moment(mit)) else (None, None)

    def _ergebnis(self, eps_m: float, chi: float, *,
                  konvergiert: bool = True) -> Ebene:
        staebe = self.querschnitt.staebe
        dehnungen = tuple(eps_m + chi * s.arm for s in staebe)
        kraefte = self.kraefte(eps_m, chi)
        return Ebene(
            eps_m=eps_m, chi=chi,
            N_int=kraefte.N, M_int=kraefte.M,
            sigma_s=tuple(s.gesetz(e) for s, e in zip(staebe, dehnungen)),
            eps_s=dehnungen,
            konvergiert=konvergiert)

    def _eps_von(self, chi: float, N_ziel: float, eps: float) -> Optional[float]:
        """Von ``eps`` aus mit wachsenden Schritten eingrenzen, im Fenster -- dann die Suche."""
        fenster = self._fenster(chi)
        if fenster is None:
            return None
        unten, oben = fenster
        a = min(max(eps, unten), oben)

        def zu_viel(e: float) -> float:
            return self.kraefte(e, chi).N - N_ziel

        klammer = eingrenzen(zu_viel, a, zu_viel(a), 1e-6, faktor=4.0, unten=unten, oben=oben)
        if klammer is None:
            return None
        von, bis, f_von, f_bis = klammer
        return self._suchen(zu_viel, von, bis, EPS_SCHRANKE, f_von, f_bis)

    def _von_zuletzt(self, N_Ed: float, M_Ed: float, chi: float) -> Optional[Ebene]:
        """
        Von ``chi`` aus mit wachsenden Schritten, bis das Moment die Seite
        wechselt -- das Moment waechst mit der Kruemmung --, dann die Suche.
        ``None``, wo unterwegs keine Ebene die Normalkraft traegt; die Ebene
        mit ihrer Probe, die auch verfehlt sein kann (:meth:`_mit_probe`).
        """
        def zu_viel(k: float) -> Optional[float]:
            eps_m = self._eps_zu_normalkraft(k, N_Ed)
            return None if eps_m is None else self.kraefte(eps_m, k).M - M_Ed

        fa = zu_viel(chi)
        if fa is None:
            return None
        schritt = max(abs(chi), self.grenzen.kruemmungsgrenze(positiv=True) * 1e-6) / 4.0
        klammer = eingrenzen(zu_viel, chi, fa, schritt, faktor=2.0)
        if klammer is None:
            return None
        unten, oben, f_unten, f_oben = klammer
        gefunden = self._suchen(zu_viel, unten, oben, CHI_SCHRANKE, f_unten, f_oben)
        if gefunden is None:
            return None
        eps_m = self._eps_zu_normalkraft(gefunden, N_Ed)
        return None if eps_m is None else self._mit_probe(eps_m, gefunden, N_Ed, M_Ed)

