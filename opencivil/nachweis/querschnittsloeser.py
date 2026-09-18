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
from typing import Callable, List, Optional, Sequence, Tuple

#: Fasern ueber die Plattenhoehe. 60 reichen: die Betonspannung ist stetig,
#: und der Fehler der Mittelpunktsregel faellt mit dem Quadrat der Faserdicke.
FASERN = 60

#: Halbierungen je Bisektion. 60 bringt jedes Intervall auf 1e-18 seiner
#: Breite -- mehr als die doppelte Genauigkeit erlaubt.
SCHRITTE = 60

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


class Querschnittsloeser:
    """
    Der Querschnitt als Faserintegral, mit Suche nach der Dehnungsebene.

    ``beton`` und ``stahl`` sind Funktionen ``eps -> sigma`` in SI. Damit
    bleibt der Loeser frei von Annahmen ueber das Werkstoffgesetz: die
    Spannungsbegrenzung rechnet elastisch mit Kriechen, der Knicknachweis mit
    dem nichtlinearen Gesetz der Norm.

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
        # Mittelpunkte und Dicke der Fasern -- einmal gerechnet, tausendfach
        # gebraucht.
        self.dicke = h / fasern
        self.mitten = [(i + 0.5) * self.dicke for i in range(fasern)]

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
        halb = self.h / 2.0

        for z in self.mitten:
            sigma = self.beton(eps_m + chi * (z - halb))
            kraft = sigma * self.dicke * self.b
            N += kraft
            M += kraft * (z - halb)

        for lage in self.lagen:
            eps = eps_m + chi * (lage.z - halb)
            # Netto: der Stahl ersetzt den Beton an dieser Stelle.
            sigma = self.stahl(eps) - self.beton(eps)
            kraft = sigma * lage.a_s
            N += kraft
            M += kraft * (lage.z - halb)

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


def beton_elastisch(*, E_c: float) -> Callable[[float], float]:
    """
    Beton ohne Zugfestigkeit, im Druck linear.

    Fuer den gerissenen Gebrauchszustand. ``E_c`` ist bereits der wirksame
    Modul, also ``E_cm/(1+phi)``, falls Kriechen zaehlt.
    """
    def sigma(eps: float) -> float:
        return 0.0 if eps > 0.0 else E_c * eps
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
    """Linear bis zur Fliessgrenze, dann waagrecht; jenseits von ``eps_ud`` null."""
    def sigma(eps: float) -> float:
        if abs(eps) > eps_ud:
            return 0.0
        return math.copysign(min(abs(eps) * E_s, f_sd), eps)
    return sigma
