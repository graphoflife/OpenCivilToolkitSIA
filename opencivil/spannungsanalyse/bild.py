"""
opencivil/spannungsanalyse/bild.py -- das Bild eines Querschnitts.

VERANTWORTUNG:
Die ersten zwei Fragen: aus Schnittgroessen oder aus Randdehnungen die
Dehnung und die Spannung ueber die Hoehe, die Kraefte des Stahls und die
Nulllinie (:class:`Querschnittsbild`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from opencivil.nachweis.querschnittsloeser import Faserloeser
from opencivil.querschnitt.gesetzwahl import Rechenart
from opencivil.querschnitt.werkstoffgesetz import RUNDUNG

#: Punkte ueber die Hoehe, mit denen Dehnung und Spannung gezeichnet werden.
#: Die Betonspannung hat am Nulldurchgang einen Knick; 41 Punkte zeigen ihn,
#: ohne dass die Kurve eckig wird.
STUETZSTELLEN = 41


# ===========================================================================
# Das Bild eines Querschnitts
# ===========================================================================

@dataclass(frozen=True)
class Faserpunkt:
    """Eine Stelle ueber die Hoehe, mit dem, was dort geschieht."""

    z: float
    """
    Abstand vom **oberen Rand**, in m -- dem gedrueckten bei positivem Moment.

    Dieselbe Achse, die der Loeser und der Lagenaufbau benutzen. Fuer eine
    Platte ist es die Oberkante: die 1. Lage liegt bei ``z = h -
    Randabstand`` und die 4. bei ``z = Randabstand``. Wer hier umdrehte,
    bekaeme ein Bild, das zum Nachweis nicht passt. Beim gezeichneten
    Querschnitt der Rand gegenueber der Zugseite.
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

    name: str = ""
    """Wie die Lage heisst -- «2. Lage Grundbewehrung», «Linie 1»."""


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


def _bild(loeser: Faserloeser, eps_m: float, chi: float) -> Querschnittsbild:
    """Dehnungen und Spannungen zu einer gegebenen Ebene -- ohne jede Suche."""
    kraefte = loeser.kraefte(eps_m, chi)
    oben = loeser.oben

    beton = []
    for i in range(STUETZSTELLEN):
        z = loeser.h * i / (STUETZSTELLEN - 1)    # von oben nach unten
        eps = eps_m + chi * (z + oben)
        beton.append(Faserpunkt(z=z, eps=eps, sigma=loeser.betonspannung(z + oben, eps)))

    stahl = []
    for lage, stab in zip(loeser.lagen, loeser.querschnitt.staebe):
        eps = eps_m + chi * (lage.z + oben)
        sigma = stab.gesetz(eps)
        stahl.append(Stahlpunkt(z=lage.z, eps=eps, sigma=sigma,
                                nummer=lage.nummer, a_s=lage.a_s,
                                kraft=sigma * lage.a_s, name=lage.text))

    return Querschnittsbild(eps_m=eps_m, chi=chi, N=kraefte.N, M=kraefte.M,
                            beton=beton, stahl=stahl)


def aus_schnittgroessen(loeser: Faserloeser, *, N: float, M: float,
                        art: Rechenart) -> Querschnittsbild:
    """
    Die Dehnungsebene zu ``N`` und ``M``, samt allem, was darauf steht.

    Gesucht wird mit demselben Verfahren wie in den Nachweisen. Findet sich
    keine Ebene, kommt das Bild leer zurueck und sagt warum -- geraten wird
    nicht. Verfehlt die Suche ihre Ebene, sagt es die Rechenart ``art``
    (:attr:`Rechenart.ohne_ebene`).
    """
    ebene = loeser.loese(N_Ed=N, M_Ed=M)
    if not ebene.konvergiert:
        return Querschnittsbild(
            eps_m=0.0, chi=0.0, N=N, M=M, konvergiert=False,
            hinweis=(art.ohne_ebene if ebene.verfehlt else
                     "Zu dieser Kombination gibt es keine Gleichgewichtslage: "
                     "der Querschnitt nimmt sie nicht auf."))
    return _bild(loeser, ebene.eps_m, ebene.chi)


def aus_dehnungen(loeser: Faserloeser, *,
                  eps_oben: float, eps_unten: float) -> Querschnittsbild:
    """
    Der umgekehrte Weg: die Ebene ist gegeben, gesucht sind die Kraefte.

    Hier gibt es nichts zu suchen -- aus den beiden Randdehnungen folgen
    Mitteldehnung und Kruemmung unmittelbar, und das Faserintegral liefert
    Normalkraft und Moment in einem Durchgang.
    """
    # z laeuft vom oberen Rand nach unten, also ist die Randdehnung unten die
    # bei z = h und die obere die bei z = 0. Die Mitteldehnung gilt am Arm
    # null: bei der Platte auf halber Hoehe, beim gezeichneten Querschnitt im
    # Schwerpunkt.
    chi = (eps_unten - eps_oben) / loeser.h if loeser.h > 0 else 0.0
    eps_m = eps_oben - chi * loeser.oben
    bild = _bild(loeser, eps_m, chi)
    # Druck und Zug je gegen ihre eigene Grenze: −5 ‰ liegt jenseits des
    # Betons, auch wenn der Stahl bis 45 ‰ reicht. Bis 2026-10-16 stand hier
    # das Groessere der beiden, und der Hinweis blieb aus.
    if (min(eps_oben, eps_unten) < -(loeser.eps_druck + RUNDUNG)
            or max(eps_oben, eps_unten) > loeser.eps_zug + RUNDUNG):
        bild.hinweis = (
            f"Die Randdehnung liegt ausserhalb dessen, wofür die "
            f"Werkstoffgesetze gelten (−{loeser.eps_druck * 1e3:.1f} ‰ bis "
            f"+{loeser.eps_zug * 1e3:.1f} ‰). Jenseits davon geben sie null "
            f"zurück, und die Spannungen unten sind keine Aussage mehr.")
    return bild
