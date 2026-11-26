"""
opencivil/spannungsanalyse/rissfrei.py -- das Paar eines Querschnitts, der nicht reisst.

VERANTWORTUNG:
Wie ein gezeichneter Querschnitt aus Baustahl oder Holz zu den sechs Fragen
kommt (:class:`RissfreiesPaar`, ein
:class:`~opencivil.spannungsanalyse.linie.Paar`, seit 2026-11-26). Ohne Beton
reisst er nicht: er hat einen Zustand, seine beiden Loeser sind derselbe, und
jede Linie laeuft ganz ueber die Verformung, von der festgehaltenen Kraft
allein bis zum Ende. Fliessen beginnt, wo eine Faser ihren elastischen
Bereich verlaesst -- Baustahl auf Zug und Druck, Holz auf Druck, wenn es dort
elastisch-plastisch rechnet
(:attr:`~opencivil.querschnitt.werkstoffgesetz.Gesetz.fliessbereich`). Seine
Ebenen findet er wie der Stahlbeton
(:class:`~opencivil.spannungsanalyse.schnitt.AmSchnitt`).

DER AEQUIVALENTE MODUL:
Bezogen auf den Querschnitt selbst, mit dem Modul seines Materials: ``E_a``
beim Baustahl, ``E_0,mean`` beim Holz. Solange keine Faser fliesst, ist
``E_eq`` genau dieser Modul -- kippt die Nulllinie, mit ``I - I_yz²/I_quer``
(:meth:`~opencivil.nachweis.rissgroessen.Bruttoquerschnitt.traegheit`).

NACH VORGABE, NICHT NACHGESCHLAGEN:
Ist der Querschnitt aus mehreren Materialien derselben Art -- zwei Hoelzer,
zwei Baustaehle --, misst sich der Modul an dem mit der groessten Flaeche.

EINHEITEN:
SI-Basis wie im ganzen Querschnittsmodul.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Dict, Mapping, Tuple

from opencivil.core.latex import ohne_namen_im_index
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import kennung_aus
from opencivil.material.basis import Baustoff, Baustoffart, mit_index
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.nachweis.querschnittsloeser import Faserloeser
from opencivil.nachweis.rissgroessen import Bruttoquerschnitt, protokoll_traegheit
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.gesetzwahl import Rechenwahl, Werkstoffsatz, holz_text
from opencivil.querschnitt.werkstoffgesetz import Gesetz
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.linie import Modulbezug, Zustaende
from opencivil.spannungsanalyse.schnitt import AmSchnitt, Zerlegung, zerlegung

if TYPE_CHECKING:
    from opencivil.core.wert import Wert
    from opencivil.spannungsanalyse.linie import Linie


#: Je Art der Kennwert, an dessen Modul sich ``E_eq`` misst.
_MODUL = {Baustoffart.BAUSTAHL: "E_a", Baustoffart.HOLZ: "E_0_mean"}


@dataclass(frozen=True)
class RissfreiesPaar(AmSchnitt):
    """
    Das Paar eines Querschnitts ohne Beton in einer Zugrichtung: ein Loeser
    fuer beide Zustaende, dazu seine Zerlegung fuer die kippende Nulllinie,
    seine Traegheitsmomente fuer den Modul und was die Herleitung braucht.
    """

    gerissen: Faserloeser
    """Der eine Zustand -- «gerissen» heisst er nur, weil jedes Paar so fragt."""

    seite: Zugseite
    wahl: Rechenwahl
    zerlegung: Zerlegung
    """Derselbe Zustand in jeder Richtung -- fuer die kippende Nulllinie."""

    brutto: Bruttoquerschnitt
    """Die Traegheitsmomente des Querschnitts mit der Wahl der Biegung -- ohne Ecken: er reisst nicht."""

    A: float
    """Flaeche des Querschnitts, m²."""

    stoffe: Tuple[Baustoff, ...]
    """Die Materialien der Flaechen, jedes einmal -- zuerst das mit der groessten Flaeche."""

    gesetze: Tuple[Gesetz, ...]
    """Je Material sein Gesetz, wie die Wahl es will."""

    E: float
    """Der Modul des ersten Materials, Pa -- Massstab des aequivalenten Moduls."""

    ids: Mapping[str, str] = field(default_factory=dict)
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung: A und I."""

    OHNE_FLIESSEN = "Bis zum Bruch fliesst keine Faser: der Querschnitt bleibt linear, bis er bricht."

    #: Ohne Beton kriecht nichts.
    mit_kriechzahl = False

    #: Spannglieder liegen nur im Beton.
    vorgespannt = False

    @property
    def ungerissen(self) -> Faserloeser:
        """Derselbe Loeser: ohne Beton gibt es keinen zweiten Zustand."""
        return self.gerissen

    def ebenen(self) -> Zustaende:
        """Eine Ebenensuche fuer beide Zustaende (:meth:`~opencivil.spannungsanalyse.schnitt.AmSchnitt.zustand`)."""
        eine = self.zustand(self.zerlegung, self.gerissen)
        return Zustaende(eine, eine)

    def rissmoment_bei(self, N: float) -> None:
        """Kein Riss."""
        return None

    def rissnormalkraft_bei(self, M: float) -> None:
        """Kein Riss."""
        return None

    @property
    def flaeche(self) -> str:
        """Woraus die Flaeche ist: «Baustahl» oder «Holz»."""
        return self.stoffe[0].art.beschriftung

    @property
    def rechenart(self) -> str:
        """Wie das Holz rechnet, in Worten -- beim Baustahl gibt es nichts zu waehlen."""
        return holz_text(self.wahl, [s for s in self.stoffe if s.art is Baustoffart.HOLZ])

    @property
    def beschriftung(self) -> str:
        """Die Wahl in Worten: wie das Holz rechnet, dazu der Wertesatz."""
        return ", ".join(filter(None, (self.rechenart, self.wahl.saetze.kurz)))

    @property
    def modulbezug(self) -> Modulbezug:
        """Der Querschnitt selbst, mit dem Modul seines ersten Materials."""
        stoff = self.stoffe[0]
        kurzname = _MODUL[stoff.art]
        zeichen = ohne_namen_im_index(stoff.definition(kurzname).symbol)
        text = zeichen.replace("{", "").replace("}", "")
        return Modulbezug(
            I=self.brutto.traegheit(self.seite.um_y), A=self.A, E=self.E, zeichen=zeichen,
            text=text,
            erklaerung=(f"Der äquivalente E-Modul ist der Modul, den derselbe Querschnitt "
                        f"bräuchte, um sich unter der laufenden Kraft linear-elastisch gleich "
                        f"stark zu verformen. Solange keine Faser fliesst, ist es {text}."),
            hinweis=(f"E_eq: der E-Modul, den derselbe Querschnitt linear-elastisch bräuchte, "
                     f"um sich gleich stark zu verformen; gezählt ab dem Zustand ohne laufende "
                     f"Kraft. Solange keine Faser fliesst, ist es {text}."))

    # -- Die Herleitung ----------------------------------------------------------

    def herleitung_gesetze(self, p: Protokoll, w: Zwischenwerte, linie: "Linie",
                           ein: Callable[[str], "Wert"], werte: Mapping[str, "Wert"]
                           ) -> Tuple["Wert", "Wert", "Wert"]:
        """
        Was vor dem Ende der Linie steht: dass nichts reisst, das Gesetz jedes
        Materials, wo es zu fliessen beginnt und wo die Linie endet. Zurueck
        die Tiefe und ``A``, ``I`` des Querschnitts.
        """
        wahl = self.wahl
        p.erklaerung(
            "Ohne Beton reisst der Querschnitt nicht: er hat einen Zustand, und die Linie "
            "läuft von Anfang an über die Verformung. Zu jeder Krümmung (bei der N-ε-Linie: "
            "zu jeder Dehnung) wird die Ebene gesucht, die die festgehaltene Grösse trägt.")
        fliessen = []
        for stoff, gesetz in zip(self.stoffe, self.gesetze):
            kennwerte = {rolle: werte[stoff.id_von(k)]
                         for rolle, k in wahl.kennwerte(stoff).items()}
            titel = f"Werkstoffgesetz {stoff.name}"
            if stoff.art is not Baustoffart.HOLZ:
                titel += f", {wahl.satz(stoff).beschriftung}"
            gesetz.protokoll(p, kennwerte, titel=titel,
                             basis=f"{w.basis}.{kennung_aus(stoff.id)}")
            if gesetz.fliessbereich is not None:
                fliessen.append((stoff, kennwerte))
        if any(s.art is Baustoffart.HOLZ for s in self.stoffe):
            p.text("Das Holz rechnet immer mit Bemessungswerten.")
        satz = wahl.saetze.einheitlich
        if any(s.art is Baustoffart.BAUSTAHL for s in self.stoffe):
            if satz is Werkstoffsatz.CHARAKTERISTISCH:
                p.text("Mit charakteristischen Werten: f_y statt f_yd.")
            elif satz is None:
                p.text("Mit gemischten Werten: jeder Baustahl rechnet mit seinem Wertesatz, wie "
                       "gewählt. Ein Widerstand heisst darum weder Rd noch Rk, sondern schlicht R.")

        h = w.laenge("h", "h", self.gerissen.h, "Ausdehnung des Querschnitts in Zugrichtung")
        A, I = ein("A"), ein("I")
        if fliessen:
            p.erklaerung(
                "Der Fliessbeginn ist der Punkt, an dem die erste Faser ihren elastischen "
                "Bereich verlässt: Baustahl auf Zug oder Druck, Holz auf Druck. Danach wächst "
                "die Kraft nur noch wenig, bis eine Grenzdehnung erreicht ist. Im Bild heisst "
                "die Kraft beim Fliessbeginn M_y bzw. N_y, am Ende M_Rd bzw. N_Rd – mit "
                "charakteristischen Werten Rk statt Rd.")
            for stoff, kennwerte in fliessen:
                # Der Baustahl fliesst bei f/E_a, das Holz auf Druck bei f_c,0,d/E_0,mean.
                stahl = stoff.art is Baustoffart.BAUSTAHL
                f, E = ((kennwerte["f_s"], kennwerte["E_s"]) if stahl
                        else (kennwerte["f_c"], kennwerte["E"]))
                kurz, symbol = (("eps_y", r"\varepsilon_{y}") if stahl
                                else ("eps_c_0_d", r"\varepsilon_{c,0,d}"))
                if len(fliessen) > 1:
                    kurz = f"{kurz}_{kennung_aus(stoff.id)}"
                    symbol = mit_index(symbol, stoff.symbol_index)
                p.formel(w.dehnung(kurz, symbol, f.groesse.si / E.groesse.si),
                         r"\frac{@f}{@E}", {"f": f, "E": E},
                         titel=f"Dehnung bei Fliessbeginn, {stoff.name}",
                         name=FLIESSDEHNUNG if stahl else "")
        else:
            p.erklaerung(
                "Keine Faser fliesst: das Holz rechnet linear bis zum Bruch, und die Linie "
                "bleibt gerade bis zu ihrem Ende.")
        p.erklaerung(
            "Die Linie endet bei der grössten Verformung, zu der es noch ein Gleichgewicht "
            "gibt – dort erreicht die erste Faser die Grenze ihres Gesetzes, wie oben "
            "angegeben.")
        return h, A, I

    def herleitung_traegheit(self, p: Protokoll, w: Zwischenwerte, I: "Wert") -> "Wert":
        """Der Bezug ueber dem Moment: der Querschnitt selbst -- gekippt mit ``I - I_yz²/I_quer``."""
        if self.brutto.biegung.einachsig:
            p.wert(I, titel="Trägheitsmoment des Querschnitts")
            return I
        p.erklaerung(
            "Unter reiner Biegung kippt die Nulllinie, und senkrecht zur Achse der Biegung "
            "krümmt sich der Querschnitt darum stärker, als I allein sagt: wie einer mit "
            "I_red. Sonst zeigte ein unsymmetrischer Querschnitt schon seiner Form wegen "
            "einen kleineren Modul.")
        return protokoll_traegheit(p, w, self.brutto, self.seite.um_y, I, name="I_red",
                                   symbol="I_{red}", titel="Trägheitsmoment unter reiner Biegung")

    def herleitung_flaeche(self, p: Protokoll, w: Zwischenwerte, A: "Wert") -> "Wert":
        """Der Bezug ueber der Normalkraft: der Querschnitt selbst."""
        p.wert(A, titel="Fläche des Querschnitts")
        return A


def rissfreies_paar(analyse: Querschnittsanalyse, seite: Zugseite, wert: Callable[[str], float],
                    wahl: Rechenwahl) -> RissfreiesPaar:
    """
    Das Paar eines gezeichneten Querschnitts ohne Beton in einer Zugrichtung.
    ``wert`` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
    """
    z = zerlegung(*analyse.querschnitt(wert, wahl))
    q = z.querschnitt
    r = q.richtung(seite.psi)
    # Je Material seine Flaeche: das groesste gibt den Modul des Bezugs.
    flaechen: Dict[int, float] = {}
    for gruppe, w in zip(r.fasern.gruppen, r.gruppen_werkstoff):
        flaechen[w] = flaechen.get(w, 0.0) + sum(gruppe.flaechen)
    folge = sorted(flaechen, key=lambda w: -flaechen[w])
    stoffe = tuple(analyse.stoff_von_werkstoff(w) for w in folge)
    um_y = seite.um_y
    return RissfreiesPaar(
        gerissen=z.in_richtung(seite.psi).loeser, seite=seite, wahl=wahl, zerlegung=z,
        brutto=Bruttoquerschnitt(
            I_y=wert(analyse.id_von("I_y")), I_z=wert(analyse.id_von("I_z")),
            I_yz=wert(analyse.id_von("I_yz")), ecken=(), biegung=analyse.biegung),
        A=wert(analyse.id_von("A")),
        stoffe=stoffe, gesetze=tuple(q.werkstoffe[w].gesetz for w in folge),
        E=wert(stoffe[0].id_von(_MODUL[stoffe[0].art])),
        ids={"A": analyse.id_von("A"), "I": analyse.id_von("I_y" if um_y else "I_z")})
