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
Zwei ineinandergeschachtelte Bisektionen. Bei festem ``chi`` waechst
``N(eps_m)`` monoton -- mehr Dehnung heisst mehr Zug --, also laesst sich
``eps_m`` eindeutig so waehlen, dass ``N = N_Ed``. Damit wird ``M`` eine
Funktion von ``chi`` allein, und die waechst ebenfalls monoton. Die aeussere
Bisektion sucht darin die Kruemmung.

**Beide Bisektionen brauchen einen gueltigen Dehnungsbereich.** Jenseits der
Bruchdehnungen geben die Werkstoffgesetze null zurueck; dort ist nichts mehr
monoton, und die Suche findet Scheinloesungen. Das Fenster fuer ``eps_m``
haengt darum von ``chi`` ab -- siehe :meth:`Querschnittsloeser._fenster`.

Beide Bisektionen sind robust: kein Startwert kann danebenliegen, kein
Newton-Schritt kann davonlaufen. Sie kosten mehr Auswertungen als ein
Newton-Verfahren -- bei rund 60 Fasern und 60 Halbierungen ist das
unbedeutend.

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
Dehnungsgrenzen, in denen jede gilt. Das steht in :class:`Faserloeser`. Die
Platte baut beides aus Hoehe, Breite und Lagen (:class:`Querschnittsloeser`),
der gezeichnete Querschnitt je Zugseite aus seinen Polygonen
(:mod:`opencivil.spannungsanalyse.schnitt`). Dort ist ``eps_m`` die Dehnung
im Schwerpunkt statt auf halber Hoehe; ``oben`` und ``unten`` sagen, wo die
Raender liegen.

EINHEITEN:
Alles in SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Callable, List, Optional, Sequence, Tuple

from opencivil.core.protokoll import Zwischenwerte
from opencivil.querschnitt.fasern import (
    FASERN, Dehnungsgrenze, Dehnungsgrenzen, Fasergruppe, Faserquerschnitt, Stab,
)
from opencivil.querschnitt.gesetzwahl import wirksamer_modul
from opencivil.querschnitt.werkstoffgesetz import Gesetz, Stahlgesetz

#: Obergrenze der Halbierungen je Bisektion. Erreicht wird sie fast nie --
#: abgebrochen wird ueber die Schranken darunter, sobald das Fenster eng
#: genug ist. Die Zahl steht nur da, damit keine Schleife ewig laeuft.
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

#: Aeusserste Dehnungen, innerhalb derer gesucht wird -- Stauchung und
#: Dehnung. **Der Suchbereich muss im gueltigen Bereich beider Gesetze
#: bleiben:** jenseits der Bruchdehnung geben sie null zurueck, und damit
#: waere ``N(eps_m)`` nicht mehr monoton. Genau daran scheiterte die erste
#: Fassung -- die Bisektion sah bei -0.5 dieselbe Normalkraft wie bei 0.
EPS_DRUCK = 0.003
EPS_ZUG = 0.045


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

    nummer: int = 0
    """Nur zur Zuordnung in der Mitschrift."""

    von_unten: Optional[bool] = None
    """
    Ob die Lage zur unteren Seite gehoert -- bei der Platte die 1. und 2.
    Lage (:attr:`Bewehrungslage.von_unten`). Die Handrechnung fasst je Seite
    zusammen (:func:`lagen_je_seite`); ohne Angabe entscheidet die Tiefe.
    """

    text: str = ""
    """Wie die Lage in Tabellen heisst -- «2. Lage Grundbewehrung»."""


def lagen_je_seite(lagen: Sequence[Stahllage], h: float) -> List[Stahllage]:
    """
    Je Seite eine Lage, im Schwerpunkt ihrer Flaechen -- wie die Handrechnung.

    Die Seite sagt :attr:`Stahllage.von_unten`, sonst die Tiefe gegen
    ``h/2``. Unten zuerst; eine Seite ohne Flaeche faellt weg. Die
    zusammengefasste Lage behaelt den Stahl ihrer Seite. Zwei verschiedene
    Staehle auf einer Seite liessen sich nicht zu einer Lage machen -- die
    Platte hat sie nicht, je Seite und Richtung liegt eine Lage, und Grund-
    und Zulage teilen ihren Stahl.
    """
    heraus = []
    for unten in (True, False):
        seite = [l for l in lagen
                 if (l.von_unten if l.von_unten is not None else l.z > h / 2.0) is unten]
        a_s = sum(l.a_s for l in seite)
        if a_s <= 0.0:
            continue
        if any(l.stahl != seite[0].stahl for l in seite):
            raise ValueError(
                f"Auf der {'unteren' if unten else 'oberen'} Seite liegen verschiedene "
                f"Stähle -- je Seite eine Lage im Schwerpunkt gibt es nur mit einem.")
        heraus.append(Stahllage(a_s=a_s, z=sum(l.a_s * l.z for l in seite) / a_s,
                                stahl=seite[0].stahl, sorte=seite[0].sorte,
                                nummer=seite[0].nummer, von_unten=unten))
    return heraus


def bruchdehnung(lagen: Sequence[Stahllage]) -> float:
    """
    Wie weit das Suchfenster im Zug reicht: bis zur kleinsten Bruchdehnung
    der Lagen. Jenseits davon gaebe das Gesetz dieser Lage null zurueck, und
    die Bisektion faende Scheinloesungen. Bei einer Sorte ist es ihr
    ``eps_ud``; bei zweien die kleinere -- das Fenster gilt an beiden
    Raendern. Ohne Lage gilt :data:`EPS_ZUG`.
    """
    return min((l.stahl.eps_ud for l in lagen), default=EPS_ZUG)


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
             titel=titel, nachsatz=nachsatz, name="Wirksamer Elastizitätsmodul")


def protokoll_verfahren(p, *, eps_druck: float, eps_zug: float,
                        fasern: int = FASERN, verdraengt: bool = True,
                        suche: Optional[str] = None) -> None:
    """
    Der Ablauf der Suche, in die Mitschrift geschrieben.

    Steht hier und nicht bei den Nachweisen, die den Loeser benutzen: sonst
    stuende dieselbe Beschreibung zweimal da, und beim naechsten Eingriff in
    das Verfahren aendert man eine davon.

    Beschrieben wird der *Ablauf*, nicht jeder Zwischenwert. Die Halbierungen
    abzudrucken hiesse, hundert Zeilen zu zeigen, von denen nur die letzte
    etwas behauptet -- und die wird ohnehin durch die Probe belegt. Wie
    gesucht wird, sagt der Loeser selbst (``suche``, sein
    :attr:`Faserloeser.suche`); ohne Angabe das Halbieren.
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
        titel="Dehnungsebene und innere Kräfte")
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
    p.erklaerung(suche or Faserloeser.SUCHE)
    p.erklaerung(
        f"Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen "
        f"({-eps_druck * 1e3:.1f} ‰ bis {eps_zug * 1e3:.1f} ‰). Jenseits "
        f"davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht "
        f"mehr monoton, und die Halbierung liefe auf eine beliebige Stelle "
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


def plattenfasern(
    *, h: float, b: float, beton: Gesetz, staebe: Sequence[Tuple[float, float, Gesetz]],
    fasern: int = FASERN, verdraengt: bool = True,
) -> Faserquerschnitt:
    """
    Die Platte als Fasern: gleich dicke Scheiben ueber die Hoehe, der Arm ab
    der Mittelebene, dazu je Lage ``(Flaeche, z, Gesetz)`` ein Stab.

    Der Loeser und die genaue Resistenzlinie
    (:class:`~opencivil.nachweis.resistenzlinie.Ebenenlinie`) rechnen mit
    demselben Querschnitt -- darum steht er einmal da. ``verdraengt`` wie bei
    :class:`Querschnittsloeser`. Jede Faser und jeder Stab kennt seine Dicke:
    gemittelt wird damit, wo das Gesetz springt
    (:mod:`opencivil.querschnitt.fasern`). Bis 2026-10-17 sagte das ein
    Schalter ``gemittelt``, den jeder Aufrufer aus der Rechenart ableitete.
    """
    dicke = h / fasern
    return Faserquerschnitt(
        gruppen=[Fasergruppe(
            gesetz=beton,
            arme=tuple((i + 0.5) * dicke - h / 2.0 for i in range(fasern)),
            flaechen=dicke * b,
            dicken=(dicke,) * fasern)],
        # Netto: der Stahl ersetzt den Beton an seiner Stelle -- ausser
        # in der Handrechnung, die den Beton durchgehend zaehlt.
        staebe=[Stab(arm=z - h / 2.0, flaeche=a_s, gesetz=gesetz,
                     verdraengt=beton if verdraengt else None, dicke=dicke)
                for a_s, z, gesetz in staebe])


class Faserloeser:
    """
    Ein Querschnitt aus Fasern, mit Suche nach der Dehnungsebene.

    ``querschnitt`` sind die Fasern samt Staeben, ``grenzen`` die
    Dehnungsgrenzen, innerhalb derer jedes Gesetz gilt -- mehr braucht die
    Suche nicht. Dazu, was Bilder und Linien vom Querschnitt wissen muessen:
    die Arme der Raender ``oben`` und ``unten`` -- oben ist gedrueckt, wenn
    ein positives Moment wirkt --, die Lagen mit ihrem Stahl, eine je Stab
    der Fasern, und die Spannung des Betons an einer Stelle
    (``beton(arm, eps)``). ``eps_druck`` und ``eps_zug`` sind die
    aeussersten Dehnungen, fuer die die Gesetze gelten. Wer nur sucht -- ein
    Nachweis, der die Ebene zu einem Lastfall braucht --, laesst sie weg.

    Eine Lage liegt in der Tiefe ``z`` unter dem oberen Rand; ihr Arm ist
    ``z + oben``.
    """

    #: Wie gesucht wird, in der Mitschrift (:func:`protokoll_verfahren`).
    SUCHE = (
        "Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer "
        "festgehaltenen Krümmung χ wird ε_m so lange halbiert, bis N_int die "
        "verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung "
        "immer mehr Zug bedeutet. Aussen: mit diesem ε_m bleibt ein Moment "
        "übrig, und χ wird so lange halbiert, bis auch M_int stimmt – hier "
        "trägt die Monotonie, dass mehr Krümmung mehr Moment heisst."
    )

    @property
    def suche(self) -> str:
        """Wie dieser Loeser sucht, in Worten -- fuer die Mitschrift."""
        return self.SUCHE

    def __init__(self, *, querschnitt: Faserquerschnitt, grenzen: Dehnungsgrenzen,
                 oben: float = 0.0, unten: float = 0.0, lagen: Sequence[Stahllage] = (),
                 beton: Optional[Callable[[float, float], float]] = None,
                 eps_druck: float = 0.0, eps_zug: float = 0.0) -> None:
        self.querschnitt = querschnitt
        self.grenzen = grenzen
        self.oben = oben
        self.unten = unten
        self.h = unten - oben
        self.lagen = list(lagen)
        self.betonspannung = beton
        self.eps_druck = abs(eps_druck)
        self.eps_zug = abs(eps_zug)
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
        gueltigen Dehnungsbereich faellt. Bei der Platte: beide Raender
        zwischen ``-eps_druck`` und ``eps_zug``, siehe
        :meth:`Dehnungsgrenzen.fenster`.
        """
        return self.grenzen.fenster(chi)

    def _eps_zu_normalkraft(self, chi: float, N_ziel: float) -> Optional[float]:
        """
        Die mittlere Dehnung, bei der ``N = N_ziel`` gilt -- bei festem ``chi``.

        ``N(eps_m)`` waechst im gueltigen Bereich monoton: mehr Dehnung heisst
        mehr Zug. Eine Bisektion findet die Stelle also sicher, sofern sie im
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
        wie in :meth:`_eps_zu_normalkraft` durch Halbieren, innerhalb dessen,
        was die Grenzen bei dieser Dehnung zulassen.
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
        Die Dehnungsebene zu diesen Schnittgroessen.

        Aeussere Bisektion ueber ``chi``: zu jedem ``chi`` wird ``eps_m`` so
        bestimmt, dass die Normalkraft stimmt, und das uebrig bleibende Moment
        gegen ``M_Ed`` gehalten. ``M(chi)`` waechst monoton -- mehr Kruemmung
        heisst mehr Moment --, solange der Querschnitt nicht versagt.
        """
        # Ohne Einwirkung ist die Ebene exakt null. Die Bisektion faende sie
        # nur bis auf ihre Schranken -- ein Rest von 1e-11, der als
        # Stahlspannung von einem Pascal einen Erfuellungsgrad von 3e8 ergab.
        if N_Ed == 0.0 and M_Ed == 0.0:
            return self._ergebnis(0.0, 0.0)

        def moment(chi: float) -> Optional[float]:
            eps_m = self._eps_zu_normalkraft(chi, N_Ed)
            if eps_m is None:
                return None
            return self.kraefte(eps_m, chi).M

        # Groesste Kruemmung je Richtung, bei der ueberhaupt noch ein Fenster
        # bleibt. Bei der Platte beide (eps_druck + eps_zug) / h.
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
        Wo ``f`` zwischen ``unten`` und ``oben`` null wird -- ``f`` steigt,
        unten ist es negativ, oben nicht. Halbiert, bis das Fenster schmaler
        ist als ``schranke``; ``None``, wenn ``f`` unterwegs keinen Wert hat.
        ``f_unten`` und ``f_oben`` braucht das Halbieren nicht -- sie sind
        fuer eine Suche, die mit ihnen schneller ist
        (:class:`FaserloeserIllinois`).
        """
        for _ in range(SCHRITTE):
            if oben - unten <= schranke:
                break
            mitte = 0.5 * (unten + oben)
            wert = f(mitte)
            if wert is None:
                return None
            if wert < 0.0:
                unten = mitte
            else:
                oben = mitte
        return 0.5 * (unten + oben)

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


class FaserloeserIllinois(Faserloeser):
    """
    Derselbe Loeser, der eine Nullstelle mit dem Illinois-Verfahren sucht
    statt durch Halbieren -- in denselben Klammern, bis auf dieselbe Breite.

    Fuer den gezeichneten Querschnitt unter Gebrauchslast
    (:mod:`opencivil.nachweis.qa_gebrauch`): dort wird je Lastfall die
    Nulllinie gedreht, und jede Neigung ist eine ganze Suche. Halbiert
    braucht eine Suche rund vierzig Schritte, mit Illinois ein Viertel davon:
    zwischen zwei Knicken der Gesetze ist die Kraft eine Gerade, und dort
    trifft die Sekante.

    Dazu faengt er bei der Kruemmung und der Dehnung an, die er zuletzt
    gefunden hat (:meth:`loese`): beim Knicken folgen sich viele Ebenen mit
    wenig verschiedenen Schnittgroessen, und das Eingrenzen von der groessten
    Kruemmung her kostete jede von ihnen mehr als die Suche selbst. Darum
    sucht auch das Knicken der Platte so (:class:`QuerschnittsloeserIllinois`);
    ihre Stahlspannungen und Analysen halbieren weiter.

    **Nur wo die Ebene eindeutig ist.** Springt ein Gesetz -- der
    Spannungsblock --, hat das Moment ueber der Kruemmung flache Stuecke: dort
    traegt jede Kruemmung dasselbe Moment, und welche gefunden wird, haengt am
    Weg der Suche. Mit einem Gedaechtnis hinge das Ergebnis dann an der
    Reihenfolge der Rechnungen -- an der Stuetze des Pruefprojekts war die
    Grenzkraft so 4200 statt 4099.5 kN. Mit springendem Gesetz sucht er darum
    wie jeder :class:`Faserloeser`, halbiert und von vorn (:attr:`halbiert`).
    Gesetze ohne Sprung -- Parabel, elastisch -- haben flache Stuecke erst am
    vollplastischen Querschnitt; an den Pruefprojekten bleibt dort jede Zahl,
    wie sie war.

    Wer ihn fuer eine einzige Frage baut, hat kein Gedaechtnis, an dem das
    Ergebnis haengen koennte: der darf ihn auch bei springendem Gesetz mit
    Illinois suchen lassen (``halbiert=False``) -- so die kippende Nulllinie
    der Spannung-Dehnung-Analyse
    (:class:`~opencivil.spannungsanalyse.schnitt.KippendeNulllinie`).
    """

    SUCHE = (
        "Gesucht wird in zwei geschachtelten Suchen. Innen: zu einer "
        "festgehaltenen Krümmung χ wird ε_m gesucht, bis N_int die verlangte "
        "Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr "
        "Zug bedeutet. Aussen: mit diesem ε_m bleibt ein Moment übrig, und χ "
        "wird gesucht, bis auch M_int stimmt – hier trägt die Monotonie, dass "
        "mehr Krümmung mehr Moment heisst. Beide Suchen beginnen bei der "
        "Ebene, die zuletzt gefunden wurde, grenzen die Stelle mit wachsenden "
        "Schritten ein und treffen sie dann mit dem Illinois-Verfahren: einer "
        "Sekante, die abwechselnd von beiden Seiten herankommt."
    )

    @property
    def suche(self) -> str:
        return Faserloeser.SUCHE if self.halbiert else self.SUCHE

    def __init__(self, *, halbiert: Optional[bool] = None, **angaben) -> None:
        super().__init__(**angaben)
        self._zuletzt: Optional[float] = None
        """Die Kruemmung der zuletzt gefundenen Ebene -- von dort sucht die naechste."""
        self._eps_zuletzt: Optional[float] = None
        """Die zuletzt gefundene Mitteldehnung -- von dort sucht die naechste."""
        self.halbiert = self.querschnitt.springt if halbiert is None else halbiert
        """
        Ob er wie jeder :class:`Faserloeser` sucht -- ohne Angabe, wo ein Gesetz
        springt, siehe oben.
        """

    def _eps_zu_normalkraft(self, chi: float, N_ziel: float) -> Optional[float]:
        """
        Wie beim :class:`Faserloeser`, aber von der zuletzt gefundenen
        Dehnung aus eingegrenzt: die Kruemmungen einer Suche liegen nahe
        beieinander, und mit ihnen die Dehnungen.
        """
        if self.halbiert:
            return super()._eps_zu_normalkraft(chi, N_ziel)
        eps = None
        if self._eps_zuletzt is not None:
            eps = self._eps_von(chi, N_ziel, self._eps_zuletzt)
        if eps is None:
            eps = super()._eps_zu_normalkraft(chi, N_ziel)
        if eps is not None:
            self._eps_zuletzt = eps
        return eps

    def _eps_von(self, chi: float, N_ziel: float, eps: float) -> Optional[float]:
        """Von ``eps`` aus mit wachsenden Schritten eingrenzen, im Fenster -- dann Illinois."""
        fenster = self._fenster(chi)
        if fenster is None:
            return None
        unten, oben = fenster
        a = min(max(eps, unten), oben)

        def zu_viel(e: float) -> float:
            return self.kraefte(e, chi).N - N_ziel

        fa = zu_viel(a)
        if fa == 0.0:
            return a
        schritt = 1e-6
        for _ in range(SCHRITTE):
            b = min(max(a - schritt if fa > 0.0 else a + schritt, unten), oben)
            fb = zu_viel(b)
            if fb == 0.0:
                return b
            if (fb > 0.0) != (fa > 0.0):
                break
            if b in (unten, oben):
                return None
            a, fa = b, fb
            schritt *= 4.0
        else:
            return None
        if fa < fb:
            return self._suchen(zu_viel, a, b, EPS_SCHRANKE, fa, fb)
        return self._suchen(zu_viel, b, a, EPS_SCHRANKE, fb, fa)

    def loese(self, *, N_Ed: float, M_Ed: float) -> Ebene:
        """
        Die Dehnungsebene -- von der zuletzt gefundenen Kruemmung aus
        eingegrenzt, wo es eine gibt, sonst wie jeder :class:`Faserloeser`.
        Was die naechste Suche nicht eingrenzen kann oder verfehlt, sucht sie
        von vorn.
        """
        if self.halbiert:
            return super().loese(N_Ed=N_Ed, M_Ed=M_Ed)
        ebene = None
        if self._zuletzt is not None and not (N_Ed == 0.0 and M_Ed == 0.0):
            ebene = self._von_zuletzt(N_Ed, M_Ed, self._zuletzt)
        if ebene is None or ebene.verfehlt:
            ebene = super().loese(N_Ed=N_Ed, M_Ed=M_Ed)
        if ebene.konvergiert:
            self._zuletzt = ebene.chi
        return ebene

    def _von_zuletzt(self, N_Ed: float, M_Ed: float, chi: float) -> Optional[Ebene]:
        """
        Von ``chi`` aus mit wachsenden Schritten, bis das Moment die Seite
        wechselt -- das Moment waechst mit der Kruemmung --, dann Illinois.
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
        a = chi
        for _ in range(SCHRITTE):
            if fa == 0.0:
                b, fb = a, fa
                break
            b = a - schritt if fa > 0.0 else a + schritt
            fb = zu_viel(b)
            if fb is None:
                return None
            if (fb > 0.0) != (fa > 0.0):
                break
            a, fa = b, fb
            schritt *= 2.0
        else:
            return None
        unten, oben = (a, b) if fa < fb else (b, a)
        f_unten, f_oben = min(fa, fb), max(fa, fb)
        gefunden = self._suchen(zu_viel, unten, oben, CHI_SCHRANKE, f_unten, f_oben)
        if gefunden is None:
            return None
        eps_m = self._eps_zu_normalkraft(gefunden, N_Ed)
        return None if eps_m is None else self._mit_probe(eps_m, gefunden, N_Ed, M_Ed)

    def _suchen(self, f: Callable[[float], Optional[float]], unten: float, oben: float,
                schranke: float, f_unten: Optional[float] = None,
                f_oben: Optional[float] = None) -> Optional[float]:
        if self.halbiert:
            return super()._suchen(f, unten, oben, schranke, f_unten, f_oben)
        fa = f(unten) if f_unten is None else f_unten
        fb = f(oben) if f_oben is None else f_oben
        if fa is None or fb is None:
            return None
        a, b = unten, oben
        if fa == 0.0:
            return a
        for _ in range(SCHRITTE):
            if fb == 0.0 or abs(b - a) <= schranke:
                break
            c = b - fb * (b - a) / (fb - fa)
            fc = f(c)
            if fc is None:
                return None
            if (fc > 0.0) != (fb > 0.0):
                a, fa = b, fb
            else:
                # Bleibt ein Ende zweimal stehen, wird sein Wert halbiert --
                # sonst kroeche die Sekante nur von einer Seite heran.
                fa *= 0.5
            b, fb = c, fc
        return b


class Querschnittsloeser(Faserloeser):
    """
    Der Querschnitt einer Platte als Faserintegral -- aus Hoehe, Breite und
    Lagen gebaut, gesucht wird wie bei jedem :class:`Faserloeser`.

    ``beton`` ist ein Werkstoffgesetz ``eps -> sigma`` in SI
    (:mod:`opencivil.querschnitt.werkstoffgesetz`), ``stahl`` macht aus dem
    Stahl einer Lage eines -- ohne Angabe das :class:`Stahlgesetz` der Lage
    selbst, jenseits von ``eps_ud`` null; die Handrechnung gibt ihren Stahl
    nur auf Zug mit. Damit bleibt der Loeser
    frei von Annahmen ueber das Werkstoffgesetz: die Spannungsbegrenzung rechnet
    elastisch mit Kriechen und charakteristischen Festigkeiten, der
    Knicknachweis mit dem nichtlinearen Gesetz der Norm und Bemessungswerten
    -- siehe :class:`Werkstoffsatz`.

    **Das Suchfenster muss zu den Gesetzen passen.** ``eps_druck`` und
    ``eps_zug`` duerfen nicht weiter reichen als der Bereich, in dem beide
    Gesetze monoton sind -- jenseits ihrer Bruchdehnung geben sie null zurueck,
    und dort findet die Bisektion Scheinloesungen. Ohne ``eps_zug`` reicht das
    Fenster darum bis zur kleinsten Bruchdehnung der Lagen; ``eps_druck``
    passt zur Parabel (:class:`~opencivil.querschnitt.werkstoffgesetz.Betongesetz`),
    wer es weitet, muss das Gesetz mitweiten.

    Ohne ``grenzen`` gelten beide Werte an beiden Raendern. Wer andere
    Grenzen braucht -- die Spannung-Dehnung-Analyse die des Dehnungsfaechers,
    mit ``eps_ud`` am Stahl statt am Betonrand --, gibt sie mit. Ein Gesetz,
    das springt (der Spannungsblock), wird ueber jede Faser gemittelt statt
    in ihrer Mitte gelesen: sonst springt mit ihm die Normalkraft, und keine
    Ebene trifft sie genau. Ohne ``verdraengt`` zaehlt der Beton auch dort,
    wo der Stahl liegt -- so rechnet die Handrechnung.

    Welche Gesetze zu welcher Wahl gehoeren, sagt
    :func:`opencivil.nachweis.rechenwahl.gesetze`.
    """

    def __init__(
        self,
        *,
        h: float,
        b: float,
        lagen: Sequence[Stahllage],
        beton: Gesetz,
        stahl: Optional[Callable[[Stahlgesetz], Stahlgesetz]] = None,
        fasern: int = FASERN,
        eps_druck: float = EPS_DRUCK,
        eps_zug: Optional[float] = None,
        grenzen: Optional[Sequence[Dehnungsgrenze]] = None,
        verdraengt: bool = True,
    ) -> None:
        lagen = list(lagen)
        eps_druck = abs(eps_druck)
        eps_zug = abs(eps_zug if eps_zug is not None else bruchdehnung(lagen))
        stahl = stahl or (lambda s: s)
        querschnitt = plattenfasern(
            h=h, b=b, beton=beton,
            staebe=[(l.a_s, l.z, stahl(l.stahl)) for l in lagen],
            fasern=fasern, verdraengt=verdraengt)
        super().__init__(
            querschnitt=querschnitt,
            # Der gueltige Bereich der Gesetze gilt an beiden Raendern -- wenn
            # niemand andere Grenzen mitgibt.
            grenzen=Dehnungsgrenzen(grenzen or [
                Dehnungsgrenze(arm=-h / 2.0, eps_min=-eps_druck, eps_max=eps_zug),
                Dehnungsgrenze(arm=h / 2.0, eps_min=-eps_druck, eps_max=eps_zug),
            ]),
            oben=-h / 2.0, unten=h / 2.0, lagen=lagen,
            beton=lambda arm, eps: beton(eps), eps_druck=eps_druck, eps_zug=eps_zug)
        self.b = b
        self.beton = beton
        self.fasern = fasern


class QuerschnittsloeserIllinois(FaserloeserIllinois, Querschnittsloeser):
    """
    Die Fasern der Platte (:class:`Querschnittsloeser`), gesucht wie am
    gezeichneten Querschnitt: mit Illinois, von der zuletzt gefundenen Ebene
    aus (:class:`FaserloeserIllinois`). Fuer das Knicken der Platte -- dort
    kostete das Halbieren beinahe die ganze Rechenzeit (Benutzer,
    2026-10-15).
    """
