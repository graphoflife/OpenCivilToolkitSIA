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

VORZEICHEN:
    eps > 0   Zug
    N   > 0   Zug
    M   > 0   Zug unten
``chi`` ist die Kruemmung: ``eps(z) = eps_m + chi * (z - h/2)``, mit ``z`` ab
Oberkante. Ein positives ``chi`` zieht also unten.

EINHEITEN:
Alles in SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Sequence, Tuple

from opencivil.core.protokoll import Zwischenwerte

#: Fasern ueber die Plattenhoehe. 60 reichen: die Betonspannung ist stetig,
#: und der Fehler der Mittelpunktsregel faellt mit dem Quadrat der Faserdicke.
FASERN = 60

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

#: Aeusserste Dehnungen, innerhalb derer gesucht wird -- Stauchung und
#: Dehnung. **Der Suchbereich muss im gueltigen Bereich beider Gesetze
#: bleiben:** jenseits der Bruchdehnung geben sie null zurueck, und damit
#: waere ``N(eps_m)`` nicht mehr monoton. Genau daran scheiterte die erste
#: Fassung -- die Bisektion sah bei -0.5 dieselbe Normalkraft wie bei 0.
EPS_DRUCK = 0.003
EPS_ZUG = 0.045


@dataclass(frozen=True)
class Stahllage:
    """Eine Bewehrungslage, wie der Loeser sie braucht."""

    a_s: float
    """Querschnitt in m^2, bezogen auf die betrachtete Breite."""

    z: float
    """Tiefenlage ab Oberkante, in m."""

    nummer: int = 0
    """Nur zur Zuordnung in der Mitschrift."""


@dataclass(frozen=True)
class Schnittkraefte:
    """Was eine Dehnungsebene an inneren Kraeften erzeugt."""

    N: float
    """in N, Zug positiv."""

    M: float
    """in Nm um die halbe Hoehe, Zug unten positiv."""


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

    def bei(self, z: float, h: float) -> float:
        """Die Dehnung in der Tiefe ``z``."""
        return self.eps_m + self.chi * (z - h / 2.0)



def wirksamer_modul(E_cm: float, phi: float) -> float:
    """``E_c,eff = E_cm / (1 + phi)`` -- das Kriechen weicht den Beton auf."""
    return E_cm / (1.0 + phi)


def protokoll_wirksamer_modul(p, e, basis: str, *, titel: str,
                              nachsatz: str = "") -> None:
    """
    Die Zeile zu :func:`wirksamer_modul`, aus den Eingaben ``E_cm`` und
    ``phi`` -- fuer jeden Nachweis, der mit dem aufgeweichten Beton rechnet.
    """
    modul = wirksamer_modul(e.g("E_cm").si, e.g("phi").si)
    p.formel(Zwischenwerte(basis).spannung("E_c_eff", "E_{c,eff}", modul),
             r"\frac{@E_cm}{1 + @phi}", {"E_cm": e["E_cm"], "phi": e["phi"]},
             titel=titel, nachsatz=nachsatz)


def protokoll_verfahren(p, *, eps_druck: float, eps_zug: float,
                        fasern: int = FASERN) -> None:
    """
    Der Ablauf der Suche, in die Mitschrift geschrieben.

    Steht hier und nicht bei den Nachweisen, die den Loeser benutzen: sonst
    stuende dieselbe Beschreibung zweimal da, und beim naechsten Eingriff in
    das Verfahren aendert man eine davon.

    Beschrieben wird der *Ablauf*, nicht jeder Zwischenwert. Die Halbierungen
    abzudrucken hiesse, hundert Zeilen zu zeigen, von denen nur die letzte
    etwas behauptet -- und die wird ohnehin durch die Probe belegt.
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
        f"zählt."
    )
    p.erklaerung(
        "Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer "
        "festgehaltenen Krümmung χ wird ε_m so lange halbiert, bis N_int die "
        "verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung "
        "immer mehr Zug bedeutet. Aussen: mit diesem ε_m bleibt ein Moment "
        "übrig, und χ wird so lange halbiert, bis auch M_int stimmt – hier "
        "trägt die Monotonie, dass mehr Krümmung mehr Moment heisst."
    )
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

class Querschnittsloeser:
    """
    Der Querschnitt als Faserintegral, mit Suche nach der Dehnungsebene.

    ``beton`` und ``stahl`` sind Funktionen ``eps -> sigma`` in SI. Damit
    bleibt der Loeser frei von Annahmen ueber das Werkstoffgesetz: die
    Spannungsbegrenzung rechnet elastisch mit Kriechen und charakteristischen
    Festigkeiten, der Knicknachweis mit dem nichtlinearen Gesetz der Norm und
    Bemessungswerten -- siehe :class:`Werkstoffsatz`.

    **Das Suchfenster muss zu den Gesetzen passen.** ``eps_druck`` und
    ``eps_zug`` duerfen nicht weiter reichen als der Bereich, in dem beide
    Gesetze monoton sind -- jenseits ihrer Bruchdehnung geben sie null zurueck,
    und dort findet die Bisektion Scheinloesungen. Die Vorgaben passen zu
    :func:`beton_nichtlinear` und :func:`stahl_bilinear`; wer sie weitet, muss
    die Gesetze mitweiten.
    """

    def __init__(
        self,
        *,
        h: float,
        b: float,
        lagen: Sequence[Stahllage],
        beton: Callable[[float], float],
        stahl: Callable[[float], float],
        fasern: int = FASERN,
        eps_druck: float = EPS_DRUCK,
        eps_zug: float = EPS_ZUG,
    ) -> None:
        self.h = h
        self.b = b
        self.lagen = list(lagen)
        self.beton = beton
        self.stahl = stahl
        self.fasern = fasern
        self.eps_druck = abs(eps_druck)
        self.eps_zug = abs(eps_zug)
        # Hebelarme und Flaeche der Fasern -- einmal gerechnet, hunderttausendfach
        # gebraucht. Gespeichert wird der Abstand zur Mittelebene und nicht die
        # Lage ueber Unterkante: gebraucht wird in jedem Durchgang nur der Arm,
        # und die Verschiebung jedesmal neu abzuziehen kostet bei sechzig
        # Fasern mal tausend Aufrufen spuerbar Zeit.
        self.dicke = h / fasern
        self.mitten = [(i + 0.5) * self.dicke for i in range(fasern)]
        self.arme = [z - h / 2.0 for z in self.mitten]
        self.faserflaeche = self.dicke * b
        self.stahlarme = [(l.z - h / 2.0) for l in self.lagen]

    # -- Vorwaerts ----------------------------------------------------------

    def kraefte(self, eps_m: float, chi: float) -> Schnittkraefte:
        """
        Die inneren Kraefte einer Dehnungsebene.

        Der Beton wird ueber Fasern integriert, der Stahl Lage fuer Lage. Wo
        Stahl liegt, wird die von ihm verdraengte Betonflaeche abgezogen --
        sonst zaehlte dieselbe Flaeche zweimal.
        """
        N = 0.0
        M = 0.0
        # Ortsgebunden: diese Schleife laeuft in jedem Nachweis hunderttausende
        # Male, und jeder Zugriff ueber self kostet darin eine Suche.
        beton = self.beton
        flaeche = self.faserflaeche

        for arm in self.arme:
            kraft = beton(eps_m + chi * arm) * flaeche
            N += kraft
            M += kraft * arm

        stahl = self.stahl
        for lage, arm in zip(self.lagen, self.stahlarme):
            eps = eps_m + chi * arm
            # Netto: der Stahl ersetzt den Beton an dieser Stelle.
            kraft = (stahl(eps) - beton(eps)) * lage.a_s
            N += kraft
            M += kraft * arm

        return Schnittkraefte(N=N, M=M)

    # -- Rueckwaerts --------------------------------------------------------

    def _fenster(self, chi: float) -> Optional[Tuple[float, float]]:
        """
        In welchem Bereich ``eps_m`` liegen darf, damit keine Faser aus dem
        gueltigen Dehnungsbereich faellt.

        Die Randdehnungen sind ``eps_m +- |chi|*h/2``. Beide muessen zwischen
        ``-eps_druck`` und ``eps_zug`` bleiben. Ist das Fenster leer, ist die
        Kruemmung fuer diesen Querschnitt zu gross.
        """
        rand = abs(chi) * self.h / 2.0
        unten = -self.eps_druck + rand
        oben = self.eps_zug - rand
        return (unten, oben) if unten <= oben else None

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
        if self.kraefte(unten, chi).N > N_ziel:
            return None
        if self.kraefte(oben, chi).N < N_ziel:
            return None
        for _ in range(SCHRITTE):
            if oben - unten <= EPS_SCHRANKE:
                break
            mitte = 0.5 * (unten + oben)
            if self.kraefte(mitte, chi).N < N_ziel:
                unten = mitte
            else:
                oben = mitte
        return 0.5 * (unten + oben)

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

        # Groesste Kruemmung, bei der ueberhaupt noch ein Fenster bleibt.
        grenze = (self.eps_druck + self.eps_zug) / self.h
        unten, oben = self._rand(-grenze, N_Ed, moment, M_Ed, nach_oben=False)
        if unten is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)
        oben = self._rand(grenze, N_Ed, moment, M_Ed, nach_oben=True)[0]
        if oben is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)

        for _ in range(SCHRITTE):
            if oben - unten <= CHI_SCHRANKE:
                break
            mitte = 0.5 * (unten + oben)
            m = moment(mitte)
            if m is None:
                # Sollte im eingegrenzten Fenster nicht vorkommen; wenn doch,
                # lieber ehrlich nicht konvergiert melden als raten.
                return self._ergebnis(0.0, 0.0, konvergiert=False)
            if m < M_Ed:
                unten = mitte
            else:
                oben = mitte

        chi = 0.5 * (unten + oben)
        eps_m = self._eps_zu_normalkraft(chi, N_Ed)
        if eps_m is None:
            return self._ergebnis(0.0, 0.0, konvergiert=False)
        return self._ergebnis(eps_m, chi)

    def _rand(self, start: float, N_Ed: float,
              moment: Callable[[float], Optional[float]], M_Ed: float,
              *, nach_oben: bool) -> Tuple[Optional[float], None]:
        """
        Eine Kruemmung, bei der das Moment ``M_Ed`` sicher ueber- bzw.
        unterschreitet -- der Startpunkt der aeusseren Bisektion.

        Von der theoretischen Grenze aus wird herangetastet: dort ist das
        Fenster leer oder die Normalkraft nicht erreichbar. Zwanzig
        Halbierungen genuegen, um auf eine loesbare Stelle zu kommen.
        """
        chi = start
        for _ in range(SCHRITTE):
            m = moment(chi)
            if m is not None and ((m >= M_Ed) if nach_oben else (m <= M_Ed)):
                return chi, None
            chi *= 0.5
            if abs(chi) < 1e-12:
                break
        m = moment(0.0)
        if m is not None and ((m >= M_Ed) if nach_oben else (m <= M_Ed)):
            return 0.0, None
        return None, None

    def _ergebnis(self, eps_m: float, chi: float, *,
                  konvergiert: bool = True) -> Ebene:
        halb = self.h / 2.0
        dehnungen = tuple(eps_m + chi * (l.z - halb) for l in self.lagen)
        kraefte = self.kraefte(eps_m, chi)
        return Ebene(
            eps_m=eps_m, chi=chi,
            N_int=kraefte.N, M_int=kraefte.M,
            sigma_s=tuple(self.stahl(e) for e in dehnungen),
            eps_s=dehnungen,
            konvergiert=konvergiert)


# ===========================================================================
# Werkstoffgesetze fuer den Loeser
# ===========================================================================


class Werkstoffsatz(str, Enum):
    """
    Mit welchen Festigkeiten die Werkstoffgesetze rechnen.

    **Bemessung** -- ``f_cd`` und ``f_yd``. Fuer die Tragsicherheit: gefragt
    ist, was der Querschnitt *darf*, und dahinein gehoert der
    Teilsicherheitsbeiwert.

    **Charakteristisch** -- ``f_ck`` und ``f_yk``. Fuer die
    Gebrauchstauglichkeit: gefragt ist, was der Querschnitt *tut*, und Stahl
    fliesst bei ``f_yk``, nicht bei ``f_yd``. Mit dem Plateau bei ``f_yd``
    laege jede Stahlspannung unter 435 N/mm², und eine Grenze darueber --
    ``f_yk`` bei normaler Rissanforderung -- waere nie zu ueberschreiten: ein
    Nachweis, der per Konstruktion immer aufgeht.

    Der Satz bestimmt, **wo die Plateaus liegen**, und sonst nichts. Die
    Moduln und Dehnungsgrenzen sind in beiden Saetzen dieselben. Er steht hier
    als Name und nicht als zwei Zahlen an jeder Aufrufstelle: welche Werte ein
    Nachweis ansetzt, ist eine Entscheidung, und eine Entscheidung soll man
    lesen koennen, statt sie aus ``f_sd=...`` erschliessen zu muessen. Jeder
    Nutzer des Loesers nennt darum seinen Satz -- der Knicknachweis und die
    Spannung-Dehnung-Analyse ``BEMESSUNG``, die Spannungsbegrenzung
    ``CHARAKTERISTISCH``.
    """

    BEMESSUNG = "bemessung"
    CHARAKTERISTISCH = "charakteristisch"

    @property
    def stahl(self) -> str:
        """Kurzname der Stahlfestigkeit -- dort beginnt das Fliessplateau."""
        return "f_yd" if self is Werkstoffsatz.BEMESSUNG else "f_yk"

    @property
    def beton(self) -> str:
        """Kurzname der Betonfestigkeit -- dort endet der Anstieg im Druck."""
        return "f_cd" if self is Werkstoffsatz.BEMESSUNG else "f_ck"

    @property
    def stahl_zeichen(self) -> str:
        """Das Formelzeichen dazu, fuer die Herleitung -- ``f_{yd}``."""
        return "f_{yd}" if self is Werkstoffsatz.BEMESSUNG else "f_{yk}"

    @property
    def beton_zeichen(self) -> str:
        """Das Formelzeichen dazu, fuer die Herleitung -- ``f_{cd}``."""
        return "f_{cd}" if self is Werkstoffsatz.BEMESSUNG else "f_{ck}"


def beton_elastisch(*, E_c: float,
                    f_c: float = math.inf) -> Callable[[float], float]:
    """
    Beton ohne Zugfestigkeit, im Druck linear bis ``f_c``, dann waagrecht.

    Fuer den gerissenen Gebrauchszustand. ``E_c`` ist bereits der wirksame
    Modul, also ``E_cm/(1+phi)``, falls Kriechen zaehlt. ``f_c`` ist die
    Festigkeit aus dem :class:`Werkstoffsatz` -- im Gebrauchszustand ``f_ck``.

    Linear und nicht als Parabel: im Gebrauchszustand liegt die
    Betonspannung weit unter der Festigkeit, und dort ist die Parabel eine
    Gerade. Die Grenze steht trotzdem da, damit eine Druckzone, die doch
    einmal so weit kommt, nicht mehr aufnimmt, als der Beton hergibt. Ohne
    ``f_c`` bleibt das Gesetz unbegrenzt linear -- fuer Rechnungen, die mit
    Festigkeiten nichts zu tun haben.

    Ein Vergleich und nicht ``max()``: das Gesetz laeuft je Nachweisfall
    rund siebzigtausend Mal, und der Funktionsaufruf kostete doppelt so viel
    wie die Rechnung selbst -- gemessen 28 ms je Platte.
    """
    grenze = -f_c

    def sigma(eps: float) -> float:
        if eps > 0.0:
            return 0.0
        s = E_c * eps
        return s if s > grenze else grenze
    return sigma


def beton_nichtlinear(*, f_cd: float, E_c: float,
                      eps_c1d: float = 0.002,
                      eps_c2d: float = 0.003) -> Callable[[float], float]:
    """
    Parabel-Rechteck-Beziehung nach SIA 262, als Funktion fuer den Loeser.

    Keine Zugfestigkeit, Plateau zwischen ``eps_c1d`` und ``eps_c2d``, danach
    Versagen (Spannung null). ``k_sigma = E_c/(400*f_cd)`` -- so steht es im
    Vorbild.
    """
    k_sigma = E_c / (400.0 * f_cd) if f_cd > 0 else 0.0

    def sigma(eps: float) -> float:
        if eps >= 0.0:
            return 0.0
        if eps < -eps_c2d:
            return 0.0
        if eps <= -eps_c1d:
            return -f_cd
        eta = -eps / eps_c1d
        return -f_cd * (k_sigma * eta - eta * eta) / (1.0 + eta * (k_sigma - 2.0))
    return sigma


def stahl_bilinear(*, E_s: float, f_sd: float,
                   eps_ud: float = 0.045) -> Callable[[float], float]:
    """
    Linear bis zur Fliessgrenze, dann waagrecht; jenseits von ``eps_ud`` null.

    ``f_sd`` ist die Grenze, ab der es waagrecht geht -- ``f_yd`` oder
    ``f_yk``, je nach :class:`Werkstoffsatz`.
    """
    def sigma(eps: float) -> float:
        if abs(eps) > eps_ud:
            return 0.0
        return math.copysign(min(abs(eps) * E_s, f_sd), eps)
    return sigma
