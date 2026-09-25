"""
opencivil/spannungsanalyse.py -- den Querschnitt ansehen, ohne ihn nachzuweisen.

VERANTWORTUNG:
Drei Auswertungen am selben Faserintegral, das auch die Nachweise benutzen:

1. **Aus Schnittgroessen** -- ``N`` und ``M`` hinein, Dehnungsebene und
   Spannungsverteilung heraus.
2. **Aus Dehnungen** -- Randdehnungen hinein, Spannungen und Schnittgroessen
   heraus. Die Umkehrung von 1, und ohne Suche: die Ebene steht ja schon da.
3. **Momenten-Kruemmungs-Linie** -- eine Normalkraft hinein, der Verlauf
   ``M(chi)`` von null bis ``M_Rd`` heraus, mit Zugversteifung.

KEIN NACHWEIS:
Hier wird nichts gegen etwas gehalten. Es gibt keinen Erfuellungsgrad und kein
Urteil -- das ist der Unterschied zu allem anderen in diesem Werkzeug und der
Grund, warum die Auswertungen nicht im :class:`Rechenwerk` stehen. Sie
beantworten eine Frage, die man beim Entwerfen stellt: *was passiert
eigentlich im Querschnitt?*

DIE ZUGVERSTEIFUNG:
Unterhalb des Rissmoments ist der Querschnitt ungerissen und deutlich steifer,
als die Nachweise ihn rechnen -- dort wird der Beton auf Zug grundsaetzlich
nicht angesetzt. Fuer eine Verformungsbetrachtung waere das falsch herum: man
bekaeme eine Kruemmung, die es bei kleinen Momenten gar nicht gibt.

Gerechnet werden darum **beide** Zustaende, und zwar mit demselben Loeser und
nur mit verschiedenen Betongesetzen -- Zustand I nimmt Zug linear auf,
Zustand II gar nicht. Dazwischen wird interpoliert::

    zeta = 0                        fuer M <= M_Riss   (ungerissen)
    zeta = 1 - (M_Riss / M)^2       fuer M >  M_Riss
    chi  = (1 - zeta) * chi_I + zeta * chi_II

Das ist die uebliche Form. Welcher Beiwert vor dem Quadrat steht -- 1.0 fuer
kurzzeitige, 0.5 fuer dauernde oder wiederholte Einwirkung -- ist eine
Normfrage, die hier offen bleibt; eingebaut ist 1.0, also der steifere und
damit fuer eine Verformung *unguenstigere* Fall nicht. Siehe TODO.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, Werkstoffsatz, beton_nichtlinear,
    stahl_bilinear, wirksamer_modul,
)
from opencivil.nachweis.sproedes_versagen import rissmoment
from opencivil.querschnitt.platte import Richtung

if TYPE_CHECKING:
    from opencivil.core.rechenwerk import Loesung
    from opencivil.projekt import Aufbau

#: Punkte ueber die Hoehe, mit denen Dehnung und Spannung gezeichnet werden.
#: Die Betonspannung hat am Nulldurchgang einen Knick; 41 Punkte zeigen ihn,
#: ohne dass die Kurve eckig wird.
STUETZSTELLEN = 41

#: Punkte der Momenten-Kruemmungs-Linie.
KURVENPUNKTE = 40

#: Halbierungen bei der Suche nach ``M_Rd``.
HALBIERUNGEN = 24

#: Beiwert der Zugversteifung. 1.0 = kurzzeitige Einwirkung.
ZUGVERSTEIFUNG = 1.0


class Analyseart(str, Enum):
    """Welche der drei Fragen gestellt wird."""

    SCHNITTGROESSEN = "schnittgroessen"
    DEHNUNGEN = "dehnungen"
    MOMENT_KRUEMMUNG = "moment_kruemmung"

    @property
    def beschriftung(self) -> str:
        return {
            Analyseart.SCHNITTGROESSEN: "Aus N und M",
            Analyseart.DEHNUNGEN: "Aus Randdehnungen",
            Analyseart.MOMENT_KRUEMMUNG: "Momenten-Krümmungs-Linie",
        }[self]


# ===========================================================================
# Das Bild eines Querschnitts
# ===========================================================================

@dataclass(frozen=True)
class Faserpunkt:
    """Eine Stelle ueber die Hoehe, mit dem, was dort geschieht."""

    z: float
    """
    Abstand von der **Oberkante**, in m.

    Dieselbe Achse, die der Loeser und der Lagenaufbau benutzen: dort ist
    ``z`` der Abstand von der gedrueckten Randfaser bei positivem Moment, und
    fuer eine Platte ist das die Oberkante. Die 1. Lage liegt damit bei
    ``z = h - Randabstand`` und die 4. bei ``z = Randabstand``. Wer hier
    umdrehte, bekaeme ein Bild, das zum Nachweis nicht passt.
    """

    eps: float
    sigma: float
    """in Pa, Zug positiv."""


@dataclass(frozen=True)
class Stahlpunkt(Faserpunkt):
    """Dasselbe fuer eine Bewehrungslage."""

    nummer: int
    a_s: float
    kraft: float
    """``sigma * a_s`` in N -- was die Lage traegt."""


@dataclass
class Querschnittsbild:
    """Dehnungsebene, Spannungen und die daraus entstehenden Schnittgroessen."""

    eps_m: float
    chi: float
    N: float
    M: float
    beton: List[Faserpunkt] = field(default_factory=list)
    stahl: List[Stahlpunkt] = field(default_factory=list)
    konvergiert: bool = True
    hinweis: str = ""

    @property
    def nulllinie(self) -> Optional[float]:
        """
        Wo die Dehnung null wird, von der Oberkante aus.

        ``None``, wenn der ganze Querschnitt auf einer Seite liegt -- dann
        gibt es keine Nulllinie, und eine hinzurechnen hiesse, eine Zahl zu
        zeigen, die es nicht gibt.
        """
        if not self.beton or abs(self.chi) < 1e-12:
            return None
        oben, unten = self.beton[0], self.beton[-1]
        if (oben.eps > 0.0) == (unten.eps > 0.0):
            return None
        return oben.z - oben.eps / self.chi


def _bild(loeser: Querschnittsloeser, eps_m: float, chi: float) -> Querschnittsbild:
    """Dehnungen und Spannungen zu einer gegebenen Ebene -- ohne jede Suche."""
    kraefte = loeser.kraefte(eps_m, chi)
    halb = loeser.h / 2.0

    beton = []
    for i in range(STUETZSTELLEN):
        z = loeser.h * i / (STUETZSTELLEN - 1)    # von oben nach unten
        eps = eps_m + chi * (z - halb)
        beton.append(Faserpunkt(z=z, eps=eps, sigma=loeser.beton(eps)))

    stahl = []
    for lage in loeser.lagen:
        eps = eps_m + chi * (lage.z - halb)
        sigma = loeser.stahl(eps)
        stahl.append(Stahlpunkt(z=lage.z, eps=eps, sigma=sigma,
                                nummer=lage.nummer, a_s=lage.a_s,
                                kraft=sigma * lage.a_s))

    return Querschnittsbild(eps_m=eps_m, chi=chi, N=kraefte.N, M=kraefte.M,
                            beton=beton, stahl=stahl)


def aus_schnittgroessen(loeser: Querschnittsloeser, *,
                        N: float, M: float) -> Querschnittsbild:
    """
    Die Dehnungsebene zu ``N`` und ``M``, samt allem, was darauf steht.

    Gesucht wird mit demselben Verfahren wie in den Nachweisen. Findet sich
    keine Ebene, kommt das Bild leer zurueck und sagt warum -- geraten wird
    nicht.
    """
    ebene = loeser.loese(N_Ed=N, M_Ed=M)
    if not ebene.konvergiert:
        return Querschnittsbild(
            eps_m=0.0, chi=0.0, N=N, M=M, konvergiert=False,
            hinweis=("Zu dieser Kombination gibt es keine Gleichgewichtslage: "
                     "der Querschnitt nimmt sie nicht auf."))
    return _bild(loeser, ebene.eps_m, ebene.chi)


def aus_dehnungen(loeser: Querschnittsloeser, *,
                  eps_oben: float, eps_unten: float) -> Querschnittsbild:
    """
    Der umgekehrte Weg: die Ebene ist gegeben, gesucht sind die Kraefte.

    Hier gibt es nichts zu suchen -- aus den beiden Randdehnungen folgen
    Mitteldehnung und Kruemmung unmittelbar, und das Faserintegral liefert
    Normalkraft und Moment in einem Durchgang.
    """
    # z laeuft von der Oberkante nach unten, also ist die Randdehnung unten
    # die bei z = h und die obere die bei z = 0.
    eps_m = 0.5 * (eps_oben + eps_unten)
    chi = (eps_unten - eps_oben) / loeser.h if loeser.h > 0 else 0.0
    bild = _bild(loeser, eps_m, chi)
    aussen = max(abs(eps_oben), abs(eps_unten))
    if aussen > max(loeser.eps_druck, loeser.eps_zug):
        bild.hinweis = (
            f"Die Randdehnung liegt ausserhalb dessen, wofür die "
            f"Werkstoffgesetze gelten (−{loeser.eps_druck * 1e3:.1f} ‰ bis "
            f"+{loeser.eps_zug * 1e3:.1f} ‰). Jenseits davon geben sie null "
            f"zurück, und die Spannungen unten sind keine Aussage mehr.")
    return bild


# ===========================================================================
# Momenten-Kruemmungs-Linie
# ===========================================================================

@dataclass(frozen=True)
class Kurvenpunkt:
    """Ein Moment und die drei Kruemmungen, die dazu gehoeren."""

    M: float
    chi_I: Optional[float]
    """Ungerissen -- ``None``, wenn der Zustand dort keine Lösung hat."""

    chi_II: Optional[float]
    """Gerissen, ohne Zugfestigkeit des Betons."""

    chi: float
    """Was gilt: interpoliert über die Zugversteifung."""

    zeta: float


@dataclass
class Momentenkurve:
    """Der Verlauf ``M(chi)`` bei festgehaltener Normalkraft."""

    N: float
    M_Riss: float
    M_Rd: float
    punkte: List[Kurvenpunkt] = field(default_factory=list)
    hinweis: str = ""

    @property
    def tragfaehig(self) -> bool:
        return self.M_Rd > 0.0


def _groesstes_moment(loeser: Querschnittsloeser, N: float) -> float:
    """
    Das groesste Moment mit Gleichgewichtslage, durch Halbieren.

    Eigenstaendig statt aus dem M-N-Nachweis geholt: die Analyse soll auch an
    einer Platte laufen, fuer die kein Nachweis eingeschaltet ist.
    """
    if not loeser.loese(N_Ed=N, M_Ed=0.0).konvergiert:
        return 0.0
    unten, oben = 0.0, 1.0
    while oben < 1e9 and loeser.loese(N_Ed=N, M_Ed=oben).konvergiert:
        unten, oben = oben, oben * 4.0
    for _ in range(HALBIERUNGEN):
        mitte = 0.5 * (unten + oben)
        if loeser.loese(N_Ed=N, M_Ed=mitte).konvergiert:
            unten = mitte
        else:
            oben = mitte
    return unten


def moment_kruemmung(gerissen: Querschnittsloeser,
                     ungerissen: Querschnittsloeser, *,
                     N: float, M_Riss: float,
                     beiwert: float = ZUGVERSTEIFUNG) -> Momentenkurve:
    """
    Die Linie von null bis ``M_Rd``, mit Zugversteifung.

    Zu jedem Moment werden beide Zustaende gerechnet und dann gemischt. Dass
    dafuer zweimal derselbe Loeser laeuft und nur das Betongesetz wechselt,
    ist Absicht: eine zweite, nachgebaute Formel fuer den ungerissenen
    Zustand waere eine zweite Wahrheit ueber denselben Querschnitt.
    """
    M_Rd = _groesstes_moment(gerissen, N)
    kurve = Momentenkurve(N=N, M_Riss=M_Riss, M_Rd=M_Rd)
    if M_Rd <= 0.0:
        kurve.hinweis = (
            "Schon ohne Moment gibt es keine Gleichgewichtslage – die "
            "Normalkraft allein übersteigt, was der Querschnitt aufnimmt.")
        return kurve

    for i in range(KURVENPUNKTE + 1):
        M = M_Rd * i / KURVENPUNKTE
        chi_II = _kruemmung(gerissen, N, M)
        chi_I = _kruemmung(ungerissen, N, M)
        zeta = 0.0 if M <= M_Riss else 1.0 - beiwert * (M_Riss / M) ** 2
        zeta = min(max(zeta, 0.0), 1.0)
        if chi_II is None:
            continue
        chi = chi_II if chi_I is None else (1.0 - zeta) * chi_I + zeta * chi_II
        kurve.punkte.append(Kurvenpunkt(M=M, chi_I=chi_I, chi_II=chi_II,
                                        chi=chi, zeta=zeta))
    if M_Riss >= M_Rd:
        kurve.hinweis = (
            "Das Rissmoment liegt über dem Biegewiderstand: der Querschnitt "
            "reisst und versagt im selben Augenblick. Genau das prüft der "
            "Nachweis gegen sprödes Versagen.")
    return kurve


def _kruemmung(loeser: Querschnittsloeser, N: float, M: float) -> Optional[float]:
    ebene = loeser.loese(N_Ed=N, M_Ed=M)
    return ebene.chi if ebene.konvergiert else None


def beton_ungerissen(*, E_c: float) -> Callable[[float], float]:
    """
    Beton linear in beiden Richtungen -- der ungerissene Vergleichszustand.

    Ohne Abminderung im Zug und ohne Abbruch bei ``f_ct``. Das ist Absicht:
    gebraucht wird die *Steifigkeit* des ungerissenen Querschnitts, und
    oberhalb des Rissmoments gilt dieser Zustand ohnehin nur noch als
    Bezugsgroesse der Interpolation. Ein Gesetz, das bei ``f_ct`` abfiele,
    waere ausserdem nicht mehr monoton, und die Bisektion des Loesers braucht
    Monotonie.
    """
    def sigma(eps: float) -> float:
        return E_c * eps
    return sigma


# ===========================================================================
# Die Analysen einer Platte
# ===========================================================================


@dataclass(frozen=True)
class Loeserpaar:
    """
    Die beiden Querschnittsloeser einer Tragrichtung -- gerissen und nicht.

    Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
    andere -- Hoehe, Breite, Lagen, Stahlgesetz, Suchfenster -- ist dasselbe,
    und das muss es sein: sonst verglichen die beiden Zustaende zwei
    verschiedene Querschnitte. Dazu das Rissmoment, denn zwischen den beiden
    wird darueber interpoliert.
    """

    gerissen: Querschnittsloeser
    ungerissen: Querschnittsloeser
    M_Riss: float


def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float],
               *, satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG,
               ) -> Optional[Loeserpaar]:
    """
    Das Loeserpaar einer Platte in einer Richtung -- ``None`` ohne Bewehrung.

    ``wert`` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
    ``satz`` sagt, mit welchen Festigkeiten die Werkstoffgesetze rechnen; die
    Analyse zeigt den Querschnitt mit denen der Tragsicherheit.

    Stand frueher in der Schnittstelle zur Oberflaeche. Dort war sie ohne
    Oberflaeche nicht erreichbar, und ein Test baute sie als eigene Kopie
    nach -- er pruefte seine Kopie statt der echten.
    """
    posten = querschnitt.posten_in_richtung(richtung)
    if not posten:
        return None
    lagen = [Stahllage(a_s=wert(as_id), z=wert(z_id), nummer=lage.nummer)
             for lage, _, _, as_id, z_id in posten]
    stahl = posten[0][0].stahl
    beton = querschnitt.beton
    E_c_eff = wirksamer_modul(wert(beton.id_von("E_cm")), wert(querschnitt.id_von("kriechzahl")))
    gemeinsam = dict(
        h=wert(querschnitt.id_von("h")), b=wert(querschnitt.id_breite(richtung)),
        lagen=lagen,
        stahl=stahl_bilinear(E_s=wert(stahl.id_von("E_s")),
                             f_sd=wert(stahl.id_von(satz.stahl)),
                             eps_ud=wert(stahl.id_von("eps_ud"))),
        eps_druck=wert(beton.id_von("eps_c2d")),
        eps_zug=wert(stahl.id_von("eps_ud")))
    gerissen = Querschnittsloeser(
        beton=beton_nichtlinear(f_cd=wert(beton.id_von(satz.beton)), E_c=E_c_eff,
                                eps_c1d=wert(beton.id_von("eps_c1d")),
                                eps_c2d=wert(beton.id_von("eps_c2d"))),
        **gemeinsam)
    ungerissen = Querschnittsloeser(beton=beton_ungerissen(E_c=E_c_eff), **gemeinsam)
    M_Riss = rissmoment(h=gemeinsam["h"], b=gemeinsam["b"],
                        f_ctm=wert(beton.id_von("f_ctm"))).M_Riss
    return Loeserpaar(gerissen=gerissen, ungerissen=ungerissen, M_Riss=M_Riss)


@dataclass
class Analyse:
    """Ein Spannungsfall der Beschreibung -- und was die Auswertung ergab."""

    fall: Any
    """Der :class:`SpannungsfallEintrag`, wie er in der Beschreibung steht."""

    art: Analyseart
    richtung: Richtung
    h: float = 0.0
    """Plattendicke in m -- fuer das Bild."""

    bild: Optional[Querschnittsbild] = None
    kurve: Optional["Momentenkurve"] = None
    hinweis: str = ""
    """Warum es nichts auszuwerten gab, falls es nichts gab."""

    @property
    def moeglich(self) -> bool:
        return self.bild is not None or self.kurve is not None


def auswerten(fall, art: Analyseart, paar: Loeserpaar) -> Tuple[
        Optional[Querschnittsbild], Optional["Momentenkurve"]]:
    """Die eine der drei Fragen stellen, die dieser Fall stellt -- in SI."""
    if art is Analyseart.DEHNUNGEN:
        return aus_dehnungen(paar.gerissen, eps_oben=fall.eps_oben / 1e3,
                             eps_unten=fall.eps_unten / 1e3), None
    if art is Analyseart.MOMENT_KRUEMMUNG:
        return None, moment_kruemmung(paar.gerissen, paar.ungerissen,
                                      N=fall.N_Ed * 1e3, M_Riss=paar.M_Riss)
    return aus_schnittgroessen(paar.gerissen, N=fall.N_Ed * 1e3,
                               M=fall.M_Ed * 1e3), None


def analysen(aufbau: "Aufbau", loesung: "Loesung") -> Dict[str, List[Analyse]]:
    """
    Die Auswertungen am Querschnitt, je Platte.

    Kein Nachweis: hier steht kein Erfuellungsgrad und kein Urteil, sondern
    eine Antwort auf die Frage, was im Querschnitt geschieht. Gerechnet wird
    trotzdem mit demselben Faserintegral und denselben Werkstoffgesetzen wie
    in den Nachweisen -- ein zweites Modell daneben waere eine zweite
    Wahrheit ueber denselben Querschnitt.
    """
    def wert(kid: str) -> float:
        return loesung.werte[kid].groesse.si

    ergebnis: Dict[str, List[Analyse]] = {}
    for kennung, faelle in aufbau.spannungsfaelle.items():
        querschnitt = aufbau.querschnitte.get(kennung)
        if querschnitt is None:
            continue
        paare: Dict[Richtung, Optional[Loeserpaar]] = {}
        liste: List[Analyse] = []
        for fall in faelle:
            try:
                richtung = Richtung(fall.richtung)
            except ValueError:
                richtung = Richtung.X
            if richtung not in paare:
                try:
                    paare[richtung] = loeserpaar(querschnitt, richtung, wert)
                except KeyError:
                    # Ein Wert dieser Richtung wurde nicht gerechnet -- dann
                    # gibt es fuer sie keinen Querschnitt zum Auswerten.
                    paare[richtung] = None
            paar = paare[richtung]
            analyse = Analyse(fall=fall, art=Analyseart(fall.art), richtung=richtung)
            if paar is None:
                analyse.hinweis = (
                    f"In {richtung.beschriftung} liegt keine Bewehrung – ohne "
                    f"sie gibt es keinen Querschnitt zum Auswerten.")
            else:
                analyse.h = paar.gerissen.h
                analyse.bild, analyse.kurve = auswerten(fall, analyse.art, paar)
            liste.append(analyse)
        ergebnis[kennung] = liste
    return ergebnis
