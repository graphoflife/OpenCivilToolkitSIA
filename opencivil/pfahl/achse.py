"""
opencivil/pfahl/achse.py -- was die Nachweise längs der Pfahlachse teilen.

VERANTWORTUNG:
:class:`Achsnachweis`: je Kombination ein Erfüllungsgrad, und wie ein Fall
ausgeht -- N_Ed ≥ 0 drückt und steht gegen den Widerstand auf Druck,
N_Ed < 0 zieht und steht als Z_Ed = −N_Ed gegen den auf Zug
(:meth:`Achsnachweis.faelle`). Äusserer und innerer Widerstand
unterscheiden sich nur darin, woher die beiden Widerstände kommen.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

from opencivil.core.berechnung import Eingabebezug
from opencivil.core.latex import als_text
from opencivil.core.nachweis import Nachweis, NachweisUrteil, Vergleich, grad_def
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.pfahl.pfahl import Kombination, Pfahl


class Achsnachweis(Nachweis):
    """Siehe Dateikopf."""

    INDEX: str = ""
    """Der Index des Widerstands: «a» für R_a,d, «i» für R_i,d."""

    TITEL: str = ""
    """Wie die Herleitung ihn überschreibt: «Äusserer Widerstand»."""

    WORT: str = ""
    """Wie ein Satz ihn nennt: «äusserer Widerstand»."""

    def __init__(self, pfahl: Pfahl, kombinationen: Sequence[Kombination], *, basis: str,
                 bezuege: Sequence[Eingabebezug]) -> None:
        if not kombinationen:
            raise ValueError("Ein Pfahlnachweis braucht mindestens eine Kombination.")
        self.pfahl = pfahl
        self.kombinationen = list(kombinationen)
        self.d_ausnutzung: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{self.INDEX},{als_text(k.name)}}}",
                             f"Erfüllungsgrad {self.WORT} – {k.name}")
            for k in self.kombinationen}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=list(bezuege), titel=f"{self.TITEL} – {pfahl.name}",
                         abschnitt=pfahl.abschnitt)

    def faelle(self, p: Protokoll, R: Wert, R_zug: Wert) -> List[NachweisUrteil]:
        """Je Kombination ihre Normalkraft gegen den Widerstand ihrer Richtung."""
        return [self._fall(p, k, R, R_zug) for k in self.kombinationen]

    def _fall(self, p: Protokoll, k: Kombination, R_druck: Wert,
              R_zug: Wert) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{k.kennung}")
        p.titel(f"{self.TITEL} – {k.name}", ebene=3)
        N = k.N_Ed.si
        if N >= 0.0:
            E = werte.kraft("N_Ed", "N_{Ed}", N, "Druckkraft am Kopf")
            R, was, namen = R_druck, "Druck", ("N_Ed", f"R_{self.INDEX},d")
        else:
            p.text("N_Ed ist negativ: der Pfahl wird gezogen, mit Z_Ed = −N_Ed.")
            E = werte.kraft("Z_Ed", "Z_{Ed}", -N, "Zugkraft am Kopf")
            R, was, namen = R_zug, "Zug", ("Z_Ed", f"R_{self.INDEX},d,Z")
        v = Vergleich(E, R)
        v.bedingung(p, f"Einwirkung gegen Widerstand auf {was}")
        v.zeile(p, self.d_ausnutzung[k.name], mit_urteil=True)
        return self.urteil(self.d_ausnutzung[k.name], k.name, v,
                           f"{namen[0]} = {E.formatiert()} kN {'≤' if v.erfuellt else '>'} "
                           f"{namen[1]} = {R.formatiert()} kN.")
