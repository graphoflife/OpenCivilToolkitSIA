"""
opencivil/verbund/duebel.py -- Kopfbolzenduebel nach SIA 264:2014, 6.1.

VERANTWORTUNG:
Was ein Kopfbolzenduebel traegt und wie viele es braucht, ohne Herleitung,
in N, mm und N/mm² -- die Herleitung schreiben die Kennzahlen
(:mod:`opencivil.nachweis.qa_verbund_kennzahlen`) und die Nachweise je
Lastfall (:mod:`opencivil.nachweis.qa_verbund`):

* ob Stahl und Beton voll verduebelt angenommen sind oder mit Kopfbolzen-
  duebeln gerechnet wird (:class:`Verduebelung`);
* der Duebel (:class:`Kopfbolzen`): Schaftdurchmesser ``d`` von 16 bis
  25 mm, Laenge ``h_D`` ab ``4 d`` -- so ist er verformungsfaehig
  (6.1.1.3), und nur fuer ihn nennt 6.1.2.1 einen Widerstand --,
  Zugfestigkeit ``f_u``; ihre Vorgabe 450 N/mm² ist die der
  Kopfbolzenduebel in SIA 263:2013, Tabelle 3. Die Grenzen weisen schon
  die Felder ab (:class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`);
* sein Schubwiderstand ``P_Rd`` (6.1.2.1): der kleinere aus der
  Betonstauchung (30) und dem Versagen des Duebels (31), mit ``f_u``
  hoechstens 500 N/mm² und ``γ_v = 1.25``;
* je Lastfall der Abschnitt bis zum Momentennullpunkt (:class:`Abschnitt`):
  wie viele Duebel dort sitzen, ``N``, und wie weit die Momentennullpunkte
  auseinander liegen, ``L_e``;
* der kleinste Verduebelungsgrad (:func:`eta_min`, 6.1.1.6, (29)) -- und
  ob ein Lastfall im Bereich negativer Momente liegt, wo er eins ist
  (:func:`negativ`).

DIE DUEBEL TRAGEN DIE KRAFT DES BETONS:
Zwischen dem Schnitt und dem Momentennullpunkt tragen die ``N`` Duebel die
Kraft, die Beton und Betonstahl ausserhalb der Profile zusammen im Schnitt
haben -- Kammerbeton zaehlt zum Stahl
(:attr:`~opencivil.verbund.querschnitt.Verbundquerschnitt.fuge`); am
Momentennullpunkt haben sie keine (nach Vorgabe, nicht nachgeschlagen: mit
einer Normalkraft kann dort schon ein Teil im Beton stecken). Die volle
Verduebelung braucht ``N_f = |N_c,f| / P_Rd`` Duebel, ``N_c,f`` die Kraft
des Betons im plastischen Zustand bei voller Verduebelung; ``η = N/N_f`` ist
der Verduebelungsgrad.

γ_v BLEIBT:
Auch wo die Tragsicherheit charakteristische Werte waehlt, rechnet der
Duebel mit ``γ_v = 1.25``: er ist kein Material des Projekts, das eine
eigene Wahl haette (nach Vorgabe, nicht nachgeschlagen).

(29) -- UND OHNE DOPPELTE SYMMETRIE:
Teilweise verduebelt sein darf ein Traeger nur im Bereich positiver Momente
(6.1.1.6), und dort nur, wenn ``η`` die Grenze von (29) haelt; (29) gilt
fuer doppelsymmetrische Stahlprofile, mit ``f_y`` des Profils. Fuer andere
nennt die Norm keine Grenze; das Werkzeug verlangt dort volle Verduebelung,
``η ≥ 1`` (nach Vorgabe, nicht nachgeschlagen).

DER BEREICH NEGATIVER MOMENTE:
Im gezeichneten Querschnitt sagt das Vorzeichen eines Moments nicht, ob es
positiv ist: die Platte kann oben oder unten liegen. Das Werkzeug sieht den
Bereich negativer Momente, wo Beton und Betonstahl ausserhalb der Profile bei
voller Verduebelung
zusammen gezogen sind oder die plastische Nulllinie die Seite zieht, auf der
der Beton liegt (:func:`negativ`) -- so auch ueber Kammerbeton, der
gedrueckt mehr traegt als der gezogene Betonstahl der Platte (nach Vorgabe,
nicht nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from opencivil.core.wahl import Wahl

REFERENZ_P_RD = "SIA 264:2014, 6.1.2.1, (30) und (31)"
REFERENZ_GRAD = "SIA 264:2014, 6.1.1.6, (29)"
REFERENZ_VOLL = "SIA 264:2014, 6.1.1.6"
REFERENZ_LAENGE = "SIA 264:2014, 6.1.1.3"
REFERENZ_F_U = "SIA 263:2013, 3.4.3, Tabelle 3"

#: Der Widerstandsbeiwert der Verduebelung (6.1.2.1).
GAMMA_V = 1.25

#: Die Beiwerte von (30) und (31).
BETONSTAUCHUNG = 0.29
SCHAFT = 0.8

#: Wo ``d`` liegen muss, in mm, und wie lang der Duebel mindestens ist, in ``d``.
D_AB, D_BIS = 16.0, 25.0
LAENGE_IN_D = 4.0

#: Bis wohin ``f_u`` zaehlt, in N/mm² (6.1.2.1) -- und die Vorgabe aus SIA 263, Tabelle 3.
F_U_HOECHSTENS = 500.0
F_U_VORGABE = 450.0

#: (29): der Bezug der Fliessgrenze in N/mm², die Beiwerte, die Untergrenze und
#: bis wohin ``L_e`` in m die Formel gilt -- darueber verlangt sie volle Verduebelung.
F_Y_BEZUG = 355.0
GRAD_GRUND, GRAD_JE_METER = 0.75, 0.03
GRAD_AB = 0.4
L_E_BIS = 25.0


class Verduebelung(Wahl):
    """Wie Stahl und Beton verbunden sind -- einmal fuer die ganze Analyse."""

    VOLL = "voll"
    KOPFBOLZEN = "kopfbolzen"

    @property
    def beschriftung(self) -> str:
        return {Verduebelung.VOLL: "voll angenommen",
                Verduebelung.KOPFBOLZEN: "Kopfbolzendübel"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Verduebelung.VOLL:
                "Stahl und Beton tragen zusammen, ohne Schlupf, wie 5.1.2.1 es annimmt – "
                "ob Dübel dafür reichen, prüft das Werkzeug nicht.",
            Verduebelung.KOPFBOLZEN:
                "Je Lastfall tragen die Dübel bis zum Momentennullpunkt N · P_Rd: das Werkzeug "
                "prüft den Verdübelungsgrad (29) und rechnet, wo die Dübel nicht reichen, mit "
                "Teilverdübelung (6.1.1.6).",
        }[self]


@dataclass(frozen=True)
class Kopfbolzen:
    """Ein Kopfbolzenduebel -- siehe Dateikopf. ``d`` und ``h`` in mm, ``f_u`` in N/mm²."""

    d: float
    h: float
    f_u: float

    @property
    def f_u_wirksam(self) -> float:
        """``f_u``, hoechstens 500 N/mm² (6.1.2.1)."""
        return min(self.f_u, F_U_HOECHSTENS)

    def betonstauchung(self, f_ck: float, E_cm: float) -> float:
        """(30): was der Beton um den Duebel traegt, in N -- ``f_ck`` und ``E_cm`` in N/mm²."""
        return BETONSTAUCHUNG * self.d ** 2 * math.sqrt(f_ck * E_cm) / GAMMA_V

    def schaft(self) -> float:
        """(31): was der Schaft traegt, in N."""
        return SCHAFT * self.f_u_wirksam * math.pi * self.d ** 2 / 4.0 / GAMMA_V


@dataclass(frozen=True)
class Abschnitt:
    """
    Was ein Lastfall ueber die Duebel weiss: wie viele zwischen seinem
    Schnitt und dem naechsten Momentennullpunkt sitzen, ``N`` in (29), und
    wie weit die Momentennullpunkte auseinander liegen, ``L_e`` in m. Leer,
    solange es nicht angegeben ist.
    """

    anzahl: Optional[int] = None
    L_e: Optional[float] = None


def negativ(n: Tuple[float, float], zum_beton: Optional[Tuple[float, float]],
            N_c: float) -> bool:
    """
    Ob ein Lastfall im Bereich negativer Momente liegt -- siehe Dateikopf:
    ``N_c`` die Kraft in Beton und Betonstahl ausserhalb der Profile bei
    voller Verduebelung, in N
    (Zug positiv), ``n`` die Zugrichtung ihrer Nulllinie, ``zum_beton`` vom
    Baustahl zum Beton (``None``, wo der Beton keine Seite hat).
    """
    zieht = zum_beton is not None and n[0] * zum_beton[0] + n[1] * zum_beton[1] > 0.0
    return N_c > 0.0 or zieht


def eta_min(f_y: float, L_e: float) -> float:
    """
    Der kleinste Verduebelungsgrad nach (29) fuer ein doppelsymmetrisches
    Profil mit der Fliessgrenze ``f_y`` in N/mm², ``L_e`` in m.
    """
    if L_e > L_E_BIS:
        return 1.0
    return max(GRAD_AB, 1.0 - F_Y_BEZUG / f_y * (GRAD_GRUND - GRAD_JE_METER * L_e))
