"""
opencivil/stabwerk3d/stab.py -- der raeumliche Stab: drei ebene in einem.

VERANTWORTUNG:
Was ein Stab im Raum zum System beitraegt, in seinen eigenen Achsen: die
Achsen selbst, die Steifigkeitsmatrix 12 × 12, die Bettung und die Lasten --
in seinen Achsen, als arbeitsgleiche Knotenkraefte und als Resultierende.
Zusammengebaut wird in :mod:`~opencivil.stabwerk.system`.

DIE ACHSEN DES STABS:
``x`` laeuft vom Anfang zum Ende. ``z`` steht senkrecht dazu in der
lotrechten Ebene durch den Stab und zeigt nach unten: dort liegt die
gestrichelte Faser, wie in der Ebene. ``y = z × x`` ergaenzt zum
Rechtssystem. Bei einem lotrechten Stab gibt es keine lotrechte Ebene durch
ihn; dort ist ``y`` die Achse ``-y`` des Systems.

In einem Rahmen in der x-z-Ebene liegt ``z`` darum auf der gestrichelten
Faser des 2D-Balkensystems -- bei jedem Stab, der nach rechts oder lotrecht
laeuft: ``y`` ist dort ``-y`` des Systems, und ``N``, ``V_z`` und ``M_y``
sind ``N``, ``V`` und ``M`` der Ebene. Laeuft ein Stab nach links, liegt
die gestrichelte Faser der Ebene oben, ``z`` bleibt unten: ``V_z`` und
``M_y`` haben dort das andere Vorzeichen. Der Drehwinkel ``β``
dreht ``y`` und ``z`` im Rechtssinn um ``x``. Bei ``β = 0`` steht der Steg
eines Profils, das sich um ``y`` biegt, in der lotrechten Ebene des Stabs.

Lotrecht heisst: weniger als :data:`~opencivil.stabwerk3d.raum.TOLERANZ`
daneben -- so genau rundet das Zeichenfenster.

IN DER EBENE:
Liegt das ganze System in der x-z-Ebene und bleibt darin
(:data:`~opencivil.stabwerk.art.EBENE`), ist ``y`` jedes Stabs ``-y``
des Systems, wie sonst nur bei einem lotrechten (:func:`achsen_eben`).
``z = x × y`` steht dann rechts des Stabs, vom Anfang zum Ende gesehen, auf
der gestrichelten Faser des 2D-Balkensystems -- auch wenn er nach links
laeuft. So sind ``N``, ``V_z`` und ``M_y`` in jedem Stab ``N``, ``V`` und
``M`` der Ebene, und eine Drehung um ``y`` des Stabs ist eine im
Gegenuhrzeigersinn.

DREI EBENE STAEBE:
Ein gerader Stab mit den Hauptachsen y und z, ohne Schubverformung und mit
Torsion nach St. Venant, zerfaellt in drei Teile, die nichts voneinander
wissen: die Biegung in der x-z-Ebene samt Laengskraft, die Biegung in der
x-y-Ebene und die Torsion -- sie verhaelt sich wie die Laengskraft, mit
``G·I_T`` statt ``E·A``. Jeder Teil ist ein ebener Stab
(:mod:`opencivil.stabwerk.stab`), dessen y-Achse links liegt und dessen
Moment an der rechten, gestrichelten Faser zieht. Steifigkeit,
arbeitsgleiche Lasten, Bettung, Teilen und Verlauf kommen darum von dort,
ueber die Zuordnung :data:`EBENE_Z`, :data:`EBENE_Y`, :data:`TORSION`::

    Ebene z:   x und -z     u, -w, θ_y     M_y zieht an +z
    Ebene y:   x und -y     -v, -θ_z      M_z zieht an +y
    Torsion:   θ_x wie u, das Torsionsmoment wie N

Je Ende sechs Unbekannte, in dieser Folge::

    u   v   w      laengs, in y, in z
    θx  θy  θz     Drehungen um x, y und z im Rechtssinn

Ein U-Profil hat seinen Schubmittelpunkt neben dem Schwerpunkt; hier
liegen beide auf der Achse, und Woelbkrafttorsion gibt es nicht (nach
Vorgabe, nicht nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple, Union

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.modell import Lastart
from opencivil.stabwerk3d import raum
from opencivil.stabwerk3d.modell import Stablast
from opencivil.stabwerk3d.raum import TOLERANZ, Vektor

Matrix = List[List[float]]

#: Wie die ebenen Unbekannten (u, v, θ am Anfang, dann am Ende) einer Ebene
#: auf die raeumlichen fallen: (eben, raeumlich, Vorzeichen).
EBENE_Z = ((0, 0, 1.0), (1, 2, -1.0), (2, 4, 1.0), (3, 6, 1.0), (4, 8, -1.0), (5, 10, 1.0))
EBENE_Y = ((1, 1, -1.0), (2, 5, -1.0), (4, 7, -1.0), (5, 11, -1.0))
TORSION = ((0, 3, 1.0), (3, 9, 1.0))

#: Die Zuordnung in Zeichen -- fuer die Herleitung.
ZERLEGUNG_LATEX = (
    r"\mathbf{k} = \mathbf{k}_{z}(EA, EI_y) \oplus \mathbf{k}_{y}(EI_z) \oplus "
    r"\mathbf{k}_{T}(GI_T) \qquad "
    r"\mathbf{d}_{z} = (u, -w, \theta_y)_{a,b} \qquad "
    r"\mathbf{d}_{y} = (-v, -\theta_z)_{a,b} \qquad "
    r"\mathbf{d}_{T} = (\theta_x)_{a,b}"
)

#: Die Drehung von den Achsen des Systems in die des Stabs.
DREHUNG_LATEX = (
    r"\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad "
    r"\mathbf{T} = \operatorname{diag}(\mathbf{R}, \mathbf{R}, \mathbf{R}, \mathbf{R}) \qquad "
    r"\mathbf{R} = \begin{bmatrix} \mathbf{e}_x^{\mathsf{T}} \\ \mathbf{e}_y^{\mathsf{T}} \\ "
    r"\mathbf{e}_z^{\mathsf{T}} \end{bmatrix} \qquad "
    r"\mathbf{e}_z \parallel -\mathbf{e}_Z + (\mathbf{e}_Z \cdot \mathbf{e}_x)\,\mathbf{e}_x"
    r" \qquad \mathbf{e}_y = \mathbf{e}_z \times \mathbf{e}_x"
)


def achsen(a, b, drehung: float = 0.0) -> Tuple[float, Tuple[Vektor, Vektor, Vektor]]:
    """
    Laenge und Achsen ``(x, y, z)`` eines Stabs von ``a`` nach ``b`` --
    Einheitsvektoren im System, siehe Dateikopf.
    """
    d = (b.x - a.x, b.y - a.y, b.z - a.z)
    L = math.sqrt(sum(c * c for c in d))
    ex = tuple(c / L for c in d)
    if _lotrecht(d):
        ey0 = (0.0, -1.0, 0.0)
        ez0 = raum.kreuz(ex, ey0)
    else:
        # -Z ohne seinen Teil laengs des Stabs: nach unten, senkrecht zu x.
        roh = (ex[2] * ex[0], ex[2] * ex[1], ex[2] * ex[2] - 1.0)
        n = math.sqrt(sum(c * c for c in roh))
        ez0 = tuple(c / n for c in roh)
        ey0 = raum.kreuz(ez0, ex)
    c, s = math.cos(drehung), math.sin(drehung)
    ey = tuple(c * p + s * q for p, q in zip(ey0, ez0))
    ez = tuple(-s * p + c * q for p, q in zip(ey0, ez0))
    return L, (ex, ey, ez)


def achsen_eben(a, b) -> Tuple[float, Tuple[Vektor, Vektor, Vektor]]:
    """
    Laenge und Achsen eines Stabs in der x-z-Ebene: ``y`` ist ``-y`` des
    Systems, ``z = x × y`` liegt rechts des Stabs -- siehe Dateikopf.
    """
    d = (b.x - a.x, b.y - a.y, b.z - a.z)
    L = math.sqrt(sum(c * c for c in d))
    ex = tuple(c / L for c in d)
    ey = (0.0, -1.0, 0.0)
    return L, (ex, ey, raum.kreuz(ex, ey))


def _lotrecht(d: Sequence[float]) -> bool:
    """Ob ein Stab in Richtung ``d`` lotrecht steht -- waagrecht weniger lang als die Toleranz."""
    return math.hypot(d[0], d[1]) <= TOLERANZ


def drehung_umgekehrt(d: Sequence[float], drehung: float, halbe_drehung: float = math.pi) -> float:
    """
    Der Drehwinkel eines Stabs in Richtung ``d``, wenn er umgekehrt laeuft
    -- so, dass der Querschnitt bleibt, wie er steht: ``z`` bleibt, ``y``
    kehrt um wie ``x``. Liegt der Stab nicht lotrecht, bleibt ``z`` bei
    ``β = 0`` dasselbe, und es ist ``-β``; lotrecht kehrt es um, und es ist
    ``π - β``. Zwischen ``-π`` und ``π`` -- in Grad mit ``halbe_drehung =
    180``, ohne den Umweg ueber rad und seine Rundung.
    """
    neu = halbe_drehung - drehung if _lotrecht(d) else -drehung
    return math.remainder(neu, 2.0 * halbe_drehung)


def _einsetzen(k: Matrix, eben: Matrix, ebene) -> None:
    for i, I, si in ebene:
        for j, J, sj in ebene:
            k[I][J] += si * sj * eben[i][j]


def steifigkeit(L: float, EA: float, EI_y: float, EI_z: float, GI_T: float) -> Matrix:
    """Die Steifigkeitsmatrix 12 × 12 in den Achsen des Stabs."""
    k = st.nullmatrix(12)
    _einsetzen(k, st.steifigkeit(L, EA, EI_y), EBENE_Z)
    _einsetzen(k, st.steifigkeit(L, 0.0, EI_z), EBENE_Y)
    _einsetzen(k, st.steifigkeit(L, GI_T, 0.0), TORSION)
    return k


def bettung(L: float, k_y: float = 0.0, k_z: float = 0.0, k_x: float = 0.0) -> Matrix:
    """Die konsistente Bettungsmatrix 12 × 12 -- quer in y und z, laengs in x; in N/m²."""
    k = st.nullmatrix(12)
    _einsetzen(k, st.bettung(L, (k_z, k_z), k_x), EBENE_Z)
    _einsetzen(k, st.bettung(L, (k_y, k_y), 0.0), EBENE_Y)
    return k


# ===========================================================================
# Lasten in den Achsen des Stabs
# ===========================================================================


@dataclass
class Lasten:
    """
    Die Lasten eines Stabs in seinen Achsen, je Teil eine ebene Liste. Jede
    Last steht in allen dreien -- wo sie nichts tut, mit null --, damit die
    drei Verlaeufe an denselben Stellen springen.
    """

    z: List[st.Teillast] = field(default_factory=list)
    y: List[st.Teillast] = field(default_factory=list)
    t: List[st.Teillast] = field(default_factory=list)

    def dazu(self, andere: "Lasten") -> None:
        self.z += andere.z
        self.y += andere.y
        self.t += andere.t

    @property
    def mit_torsion(self) -> bool:
        """Ob eine davon den Stab um seine Achse dreht."""
        return any(l.Px if isinstance(l, st.Punkt) else (l.px_a or l.px_b) for l in self.t)


def strecke(a: float, b: float, p_a: Vektor = (0.0, 0.0, 0.0), p_b: Vektor = (0.0, 0.0, 0.0),
            m_a: Vektor = (0.0, 0.0, 0.0), m_b: Vektor = (0.0, 0.0, 0.0)) -> Lasten:
    """
    Eine Last auf ``[a, b]``, linear: Kraft je Laenge ``p`` und Moment je
    Laenge ``m``, je in x, y und z des Stabs, in N/m und Nm/m.
    """
    return Lasten(
        z=[st.Strecke(a, b, px_a=p_a[0], px_b=p_b[0], py_a=-p_a[2], py_b=-p_b[2],
                      m_a=m_a[1], m_b=m_b[1])],
        y=[st.Strecke(a, b, py_a=-p_a[1], py_b=-p_b[1], m_a=-m_a[2], m_b=-m_b[2])],
        t=[st.Strecke(a, b, px_a=m_a[0], px_b=m_b[0])])


def punkt(a: float, P: Vektor = (0.0, 0.0, 0.0), M: Vektor = (0.0, 0.0, 0.0)) -> Lasten:
    """Eine Last an der Stelle ``a``: Kraft ``P`` in N und Moment ``M`` in Nm, in den Achsen des Stabs."""
    return Lasten(z=[st.Punkt(a, Px=P[0], Py=-P[2], M=M[1])],
                  y=[st.Punkt(a, Py=-P[1], M=-M[2])],
                  t=[st.Punkt(a, Px=M[0])])


def aufteilen(lasten: Lasten, von: float, bis: float, *, ende: bool) -> Lasten:
    """Die Lasten, die auf ``[von, bis]`` liegen -- wie in der Ebene (:func:`opencivil.stabwerk.stab.aufteilen`)."""
    return Lasten(*(st.aufteilen(teil, von, bis, ende=ende)
                    for teil in (lasten.z, lasten.y, lasten.t)))


def knotenlasten(L: float, lasten: Lasten) -> List[float]:
    """Die arbeitsgleichen Knotenkraefte (12) in den Achsen des Stabs."""
    f = [0.0] * 12
    for ebene, teil in ((EBENE_Z, lasten.z), (EBENE_Y, lasten.y), (TORSION, lasten.t)):
        eben = st.knotenlasten(L, teil)
        for i, I, s in ebene:
            f[I] += s * eben[i]
    return f


def eben(werte: Sequence[float], ebene) -> List[float]:
    """Die sechs ebenen Werte einer Ebene aus den zwoelf raeumlichen -- Verschiebungen wie Kraefte."""
    heraus = [0.0] * 6
    for i, I, s in ebene:
        heraus[i] = s * werte[I]
    return heraus


def eben_matrix(k: Matrix, ebene) -> Matrix:
    """Die ebene Matrix 6 × 6 einer Ebene aus der raeumlichen 12 × 12 -- umgekehrt wie beim Einsetzen."""
    heraus = st.nullmatrix(6)
    for i, I, si in ebene:
        for j, J, sj in ebene:
            heraus[i][j] = si * sj * k[I][J]
    return heraus


def lastbereich(last, L: float) -> Union[Tuple[float, float], str]:
    """
    Wo eine Last auf einem Stab der Laenge ``L`` liegt, ``(von, bis)`` in m
    -- oder ein Satz, warum nicht: eine Stelle ausserhalb des Stabs. Eine
    Einzellast steht bei ``von``.
    """
    von = last.von
    bis = L if last.bis is None else last.bis
    if last.art.verteilt:
        if von < -TOLERANZ or bis > L + TOLERANZ or bis < von - TOLERANZ:
            return (f"die Last reicht von {von:g} bis {bis:g} m, der Stab ist aber "
                    f"{L:.3f} m lang.")
        return max(0.0, von), min(L, bis)
    if von < -TOLERANZ or von > L + TOLERANZ:
        return f"die Last steht bei {von:g} m, der Stab ist aber {L:.3f} m lang."
    return min(max(von, 0.0), L), bis


def lokal(last: Stablast, L: float, achsen: Sequence[Vektor]) -> Union[Lasten, str]:
    """
    Eine Last des Modells in den Achsen ihres Stabs -- oder ein Satz, warum
    nicht: eine Stelle ausserhalb des Stabs.
    """
    bereich = lastbereich(last, L)
    if isinstance(bereich, str):
        return bereich
    von, bis = bereich
    e = last.richtung.vektor(achsen)
    richtung = tuple(raum.skalar(achse, e) for achse in achsen)
    if last.art.kraft and last.projiziert and last.richtung.im_system:
        richtung = raum.mal(last.richtung.projektion(achsen), richtung)
    a = raum.mal(last.wert_a, richtung)
    b = a if last.wert_b is None else raum.mal(last.wert_b, richtung)
    if last.art is Lastart.LINIENLAST:
        return strecke(von, bis, p_a=a, p_b=b)
    if last.art is Lastart.LINIENMOMENT:
        return strecke(von, bis, m_a=a, m_b=b)
    if last.art is Lastart.EINZELLAST:
        return punkt(von, P=a)
    return punkt(von, M=a)


def resultierende(lasten: Lasten, anfang: Vektor, achsen: Sequence[Vektor], *,
                  laengs: bool = True, quer_y: bool = True, quer_z: bool = True,
                  torsion: bool = True) -> List[float]:
    """
    Kraft und Moment um den Ursprung ``(F, M)`` der Lasten eines Stabs, der
    bei ``anfang`` beginnt -- nur die gewaehlten Anteile. Die ebenen Lasten
    tragen ihre Werte in den Achsen ihrer Ebene, siehe Dateikopf.
    """
    ex, ey, ez = achsen
    summe = [0.0] * 6

    def ebene_z(x: float, px: float, py: float, m: float) -> None:
        kraft = raum.plus(raum.mal(px if laengs else 0.0, ex), raum.mal(-py if quer_z else 0.0, ez))
        raum.addiere(summe, raum.plus(anfang, raum.mal(x, ex)), kraft,
                     raum.mal(m if quer_z else 0.0, ey))

    def ebene_y(x: float, px: float, py: float, m: float) -> None:
        raum.addiere(summe, raum.plus(anfang, raum.mal(x, ex)),
                     raum.mal(-py if quer_y else 0.0, ey), raum.mal(-m if quer_y else 0.0, ez))

    def drillung(x: float, px: float, py: float, m: float) -> None:
        summe[3:] = raum.plus(summe[3:], raum.mal(px if torsion else 0.0, ex))

    for teil, wirkung in ((lasten.z, ebene_z), (lasten.y, ebene_y), (lasten.t, drillung)):
        for last in teil:
            if isinstance(last, st.Punkt):
                wirkung(last.a, last.Px, last.Py, last.M)
                continue
            halb, mitte = (last.b - last.a) / 2.0, (last.a + last.b) / 2.0
            if halb <= 0.0:
                continue
            for stelle, gewicht in st.GAUSS3:
                x = mitte + halb * stelle
                wirkung(x, *(halb * gewicht * w for w in last.bei(x)))
    return summe
