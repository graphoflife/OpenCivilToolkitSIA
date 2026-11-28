"""
opencivil/mauerwerk/kennwerte.py -- mit welchen Werten ihres Mauerwerks eine Wand rechnet.

VERANTWORTUNG:
Die eine Regel, wie die Wahl der Wand die Bemessungswerte ihres Mauerwerks
ändert (:func:`wandwerte`): im Verband gelten alle Werte der Tabelle 7 und
der Gl. (3) mal 0.85 (SIA 266:2015, 4.2.1.1) -- f_xd, f_yd, E_xd und G_d;
μ_d nicht, es steht nicht dort (4.2.1.3). Sind die Stossfugen vollfugig
vermauert, gilt f_yd dieser Zeile der Tabelle 7. Dazu, was deklariertes
Mauerwerk mindestens haben muss (:func:`unter_mindestwerten`, 3.1.3.1) --
gemessen an den Werten, mit denen die Wand rechnet, also auch an
abweichenden oder überschriebenen eines Standardmauerwerks.

EINHEITEN:
Wie im Material: Festigkeiten und Moduln in N/mm², μ_d ohne Einheit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping

from opencivil.material.mauerwerk import MINDESTWERTE, REFERENZ_MINDESTWERTE, VERBAND
from opencivil.stabwerk.system import Meldung

#: Wo die Regel des Verbands steht.
REFERENZ_VERBAND = "SIA 266:2015, 4.2.1.1"

#: Was die Wand von ihrem Mauerwerk liest: die Bemessungswerte, dazu die
#: kennzeichnenden Werte, die deklariertes Mauerwerk mindestens haben muss.
GELESEN = ("f_xd", "f_yd", "f_yd_v", "E_xd", "G_d", "mu_d", *(k for k, _, _ in MINDESTWERTE))


@dataclass(frozen=True)
class Wandwerte:
    """Die Bemessungswerte, mit denen eine Wand rechnet -- in N/mm², ``mu_d`` ohne Einheit."""

    faktor: float
    """0.85 im Verband, sonst 1."""

    f_xd: float
    f_yd: float
    """Wie die Stossfugen vermauert sind: nicht vollfugig oder vollfugig."""

    E_xd: float
    G_d: float
    mu_d: float


def quelle(kurz: str, vollfugig: bool) -> str:
    """Aus welchem Wert des Mauerwerks der Wert ``kurz`` kommt: vollfugig f_yd aus f_yd_v."""
    return "f_yd_v" if kurz == "f_yd" and vollfugig else kurz


def wandwerte(werte: Mapping[str, float], verband: bool, vollfugig: bool) -> Wandwerte:
    """Siehe Dateikopf -- ``werte`` je Kurzname des Materials seine Zahl."""
    k = VERBAND if verband else 1.0
    return Wandwerte(faktor=k, f_xd=k * werte["f_xd"], f_yd=k * werte[quelle("f_yd", vollfugig)],
                     E_xd=k * werte["E_xd"], G_d=k * werte["G_d"], mu_d=werte["mu_d"])


def unter_mindestwerten(werte: Mapping[str, float], name: str) -> List[Meldung]:
    """
    Je kennzeichnender Wert unter dem Mindestwert deklarierten Mauerwerks
    eine rote Meldung -- ``name`` ist der des Mauerwerks.
    """
    return [Meldung(f"Das Mauerwerk «{name}» hat {kurz} = {werte[kurz]:g} N/mm² – "
                    f"{REFERENZ_MINDESTWERTE} verlangt mindestens {mindest:g} N/mm².")
            for kurz, _, mindest in MINDESTWERTE if werte[kurz] < mindest]
