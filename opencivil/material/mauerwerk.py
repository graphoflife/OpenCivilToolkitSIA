"""
opencivil/material/mauerwerk.py -- Mauerwerk nach SIA 266:2015.

VERANTWORTUNG:
Sortentabelle und Kennwerte des Standardmauerwerks, aufgebaut wie die
anderen Baustoffe (:mod:`opencivil.material.basis`): jeder Kennwert ist
eine eigene, einzeln ueberschreibbare Berechnung. Deklariertes Mauerwerk
(3.1.2.2, mit dem Buchstaben D) legt man als eigenes Material an und setzt
die Werte seiner Deklaration -- die Wand prueft dann die Mindestwerte nach
3.1.3.1 (:data:`MINDESTWERTE`).

DIE SORTEN:
Je Art der Steine eine (3.1.1.1): Backsteine MB, Leichtbacksteine MBL,
Zementsteine MC, Leichtzementsteine MCL, Kalksandsteine MK,
Porenbetonsteine MP und Porenbetonleichtsteine MPL. Fuer Standardmauerwerk
nennt Tabelle 1 die Druckfestigkeit f_xk senkrecht zu den Lagerfugen und die
Biegezugfestigkeit f_txk, Tabelle 7 die Bemessungswerte mit γ_M = 2.0
(Gl. (3)) -- auch f_yd senkrecht zu den Stossfugen, offen und vollfugig
vermauert, fuer das Tabelle 1 keinen kennzeichnenden Wert nennt. f_yk ist
darum γ_M · f_yd der Tabelle 7: so gibt Gl. (3) deren Zahl wieder. Am
2026-11-28 gegen die gedruckten Tabellen geprueft.

DIE STEIFIGKEIT:
E_xk = 1000 f_xk und G_k = 0.4 E_xk fuer Standardmauerwerk (3.1.4.1,
Gl. (2)), die Bemessungswerte durch γ_M (4.2.1.4, Gl. (5)) -- G_d ebenso,
das gibt die Zahlen der Tabelle 7, die auf eine Stelle rundet. Der
Endkriechwert φ nach Tabelle 2, je nachdem, wie die Steine gebunden sind.
μ_d = 0.6 fuer die Reibung in den Lagerfugen (4.2.1.3).

WAS DIE WAND WAEHLT, NICHT DAS MATERIAL:
Ob das Mauerwerk im Verband steht -- dann gelten alle Werte der Tabelle 7
mal 0.85 (4.2.1.1) -- und ob die Stossfugen vollfugig vermauert sind: beides
ist eine Wahl der Wand (:mod:`opencivil.mauerwerk`), ihre Herleitung zeigt
die Werte, mit denen sie rechnet.

NACH VORGABE, NICHT NACHGESCHLAGEN:
- Porenbetonsteine gelten in Tabelle 2 als hydrothermisch gebunden, wie
  Kalksandsteine: beide haerten im Dampf.
- Die Dichte fuer das Eigengewicht: die Raumlast eines unverputzten
  Mauerwerks nach SIA 261:2020, Anhang A, Tabelle 28, durch g = 10 m/s² --
  je Sorte die Zeile der gelochten Steine ihrer Art. Leichtsteine haben
  dort keine eigene Zeile und nehmen die ihrer Art; Porenbeton die der
  Gasbetonsteine, MP die hochwertigen, MPL die normalen.

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.rechenwerk import Rechenwerk
    from opencivil.material.mauerwerk import mauerwerk

    werk = Rechenwerk()
    mb = mauerwerk("MB").ins_rechenwerk(werk)
    print(werk.loese(mb.id_von("f_xd")).wert(mb.id_von("f_xd")))
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Tuple

from opencivil.core.einheiten import EINHEITSLOS, KG_PRO_M3, N_PRO_MM2, Groesse
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge

#: Wo die Werte des Standardmauerwerks stehen.
TABELLE_1 = "SIA 266:2015, 3.1.3.3, Tabelle 1"
TABELLE_2 = "SIA 266:2015, 3.1.4.2, Tabelle 2"
TABELLE_7 = "SIA 266:2015, 4.2.1.1, Tabelle 7"

#: Wo die mittleren Raumlasten stehen.
RAUMLASTEN = "SIA 261:2020, Anhang A, Tabelle 28"

#: Der Widerstandsbeiwert -- SIA 266:2015, 4.2.1.1 und 4.2.1.4.
GAMMA_M = 2.0

#: Der Faktor auf alle Bemessungswerte, wenn das Mauerwerk im Verband steht
#: (SIA 266:2015, 4.2.1.1, unter Tabelle 7).
VERBAND = 0.85

#: Was deklariertes Mauerwerk mindestens haben muss (SIA 266:2015, 3.1.3.1):
#: je Kennwert die Zahl in N/mm².
MINDESTWERTE: Tuple[Tuple[str, str, float], ...] = (
    ("f_xk", "f_{xk}", 1.8),
    ("f_yk", "f_{yk}", 0.5),
    ("E_xk", "E_{xk}", 1800.0),
)
REFERENZ_MINDESTWERTE = "SIA 266:2015, 3.1.3.1"


class Bindung(Enum):
    """Wie die Steine gebunden sind -- das sagt den Endkriechwert (Tabelle 2)."""

    GEBRANNT = "gebrannte Steine"
    ZEMENT = "zementgebundene Steine"
    HYDROTHERMISCH = "hydrothermisch gebundene Steine"

    @property
    def phi(self) -> float:
        """Der Richtwert des Endkriechwerts -- SIA 266:2015, Tabelle 2."""
        return 1.0 if self is Bindung.GEBRANNT else 1.5


@dataclass(frozen=True)
class Mauerwerkssorte:
    """Ein Standardmauerwerk: Tabelle 1 und 7, die Bindung und die Raumlast."""

    steine: str
    """Woraus es gemauert ist, in der Mehrzahl -- «Backsteine»."""

    f_xk: float
    f_txk: float
    f_yd: float
    """Bemessungswert senkrecht zu den Stossfugen, offen vermauert -- Tabelle 7."""

    f_yd_v: float
    """Dasselbe, vollfugig vermauert -- Tabelle 7."""

    bindung: Bindung
    raumlast: float
    """kN/m³ -- die Zeile in Tabelle 28 der SIA 261, siehe Dateikopf."""


MAUERWERKSSORTEN: Dict[str, Mauerwerkssorte] = {
    "MB": Mauerwerkssorte("Backsteine", 7.0, 0.15, 1.1, 1.6, Bindung.GEBRANNT, 13.0),
    "MBL": Mauerwerkssorte("Leichtbacksteine", 1.8, 0.10, 0.3, 0.5, Bindung.GEBRANNT, 13.0),
    "MC": Mauerwerkssorte("Zementsteine", 7.0, 0.25, 1.8, 2.6, Bindung.ZEMENT, 18.0),
    "MCL": Mauerwerkssorte("Leichtzementsteine", 1.8, 0.10, 0.5, 0.7, Bindung.ZEMENT, 18.0),
    "MK": Mauerwerkssorte("Kalksandsteine", 7.0, 0.15, 1.1, 1.6, Bindung.HYDROTHERMISCH, 18.0),
    "MP": Mauerwerkssorte("Porenbetonsteine", 3.0, 0.25, 0.5, 0.7, Bindung.HYDROTHERMISCH, 7.0),
    "MPL": Mauerwerkssorte("Porenbetonleichtsteine", 1.8, 0.15, 0.3, 0.4,
                           Bindung.HYDROTHERMISCH, 6.0),
}

#: Womit ein neues Mauerwerk anfaengt.
ERSTES_MAUERWERK = "MB"


def mauerwerkssorten_zum_anlegen() -> List[str]:
    """Die Sorten in der Folge von Tabelle 1 -- die erste ist MB."""
    return list(MAUERWERKSSORTEN)


def _tabellenwert(kurzname: str, symbol: str, beschreibung: str, referenz: str,
                  stellen: int = 2) -> KennwertVorlage:
    return KennwertVorlage(kurzname=kurzname, symbol=symbol, einheit=N_PRO_MM2,
                           beschreibung=beschreibung, referenz=referenz, stellen=stellen)


def _durch_gamma(kurzname: str, symbol: str, beschreibung: str, eingabe: str, referenz: str,
                 stellen: int = 2) -> KennwertVorlage:
    """
    Ein Bemessungswert: der kennzeichnende durch γ_M. Das Rechenwerk gibt
    die Eingaben mit ihren Kurznamen.
    """
    def durch_gamma(**e: float) -> float:
        return e[eingabe] / e["gamma_M"]

    return KennwertVorlage(
        kurzname=kurzname, symbol=symbol, einheit=N_PRO_MM2, beschreibung=beschreibung,
        referenz=referenz, stellen=stellen, eingaben=(eingabe, "gamma_M"),
        vorlage_latex=rf"\frac{{@{eingabe}}}{{@gamma_M}}", funktion=durch_gamma)


MAUERWERK_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Kennzeichnende Werte (Tabellen 1 und 7) ----------------------------
    _tabellenwert("f_xk", "f_{xk}", "Druckfestigkeit senkrecht zu den Lagerfugen, kennzeichnend",
                  TABELLE_1, stellen=1),
    _tabellenwert("f_yk", "f_{yk}", "Druckfestigkeit senkrecht zu den Stossfugen, kennzeichnend",
                  f"{TABELLE_7}; γ_M · f_yd"),
    _tabellenwert("f_yk_v", "f_{yk,v}",
                  "Druckfestigkeit senkrecht zu den Stossfugen, vollfugig vermauert, kennzeichnend",
                  f"{TABELLE_7}; γ_M · f_yd"),
    _tabellenwert("f_txk", "f_{txk}",
                  "Biegezugfestigkeit senkrecht zu den Lagerfugen, kennzeichnend", TABELLE_1),
    KennwertVorlage(kurzname="gamma_M", symbol=r"\gamma_M", einheit=EINHEITSLOS,
                    beschreibung="Widerstandsbeiwert des Mauerwerks",
                    referenz="SIA 266:2015, 4.2.1.1", stellen=1,
                    festwert=Groesse(GAMMA_M, EINHEITSLOS)),
    # -- Bemessungswerte (Gl. (3)) ------------------------------------------
    _durch_gamma("f_xd", "f_{xd}", "Bemessungswert der Druckfestigkeit senkrecht zu den Lagerfugen",
                 "f_xk", "SIA 266:2015, 4.2.1.1, Gl. (3)"),
    _durch_gamma("f_yd", "f_{yd}", "Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen",
                 "f_yk", "SIA 266:2015, 4.2.1.1, Gl. (3)"),
    _durch_gamma("f_yd_v", "f_{yd,v}",
                 "Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen, vollfugig "
                 "vermauert", "f_yk_v", "SIA 266:2015, 4.2.1.1, Gl. (3)"),
    # -- Steifigkeit (3.1.4, 4.2.1.4) ---------------------------------------
    KennwertVorlage(
        kurzname="E_xk", symbol="E_{xk}", einheit=N_PRO_MM2,
        beschreibung="Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend",
        referenz="SIA 266:2015, 3.1.4.1", stellen=0, eingaben=("f_xk",),
        vorlage_latex=r"1000 \cdot @f_xk", funktion=lambda f_xk: 1000.0 * f_xk),
    KennwertVorlage(
        kurzname="G_k", symbol="G_k", einheit=N_PRO_MM2, beschreibung="Schubmodul, kennzeichnend",
        referenz="SIA 266:2015, 3.1.4.1, Gl. (2)", stellen=0, eingaben=("E_xk",),
        vorlage_latex=r"0.4 \cdot @E_xk", funktion=lambda E_xk: 0.4 * E_xk),
    _durch_gamma("E_xd", "E_{xd}", "Bemessungswert des Elastizitätsmoduls senkrecht zu den "
                 "Lagerfugen", "E_xk", "SIA 266:2015, 4.2.1.4, Gl. (5)", stellen=0),
    _durch_gamma("G_d", "G_d", "Bemessungswert des Schubmoduls", "G_k",
                 "SIA 266:2015, Tabelle 7; Gl. (2) und (5)", stellen=0),
    # -- Reibung, Kriechen, Eigengewicht ------------------------------------
    KennwertVorlage(kurzname="mu_d", symbol=r"\mu_d", einheit=EINHEITSLOS,
                    beschreibung="Bemessungswert des Reibungsbeiwerts in den Lagerfugen",
                    referenz="SIA 266:2015, 4.2.1.3", stellen=1,
                    festwert=Groesse(0.6, EINHEITSLOS)),
    KennwertVorlage(kurzname="phi", symbol=r"\varphi", einheit=EINHEITSLOS,
                    beschreibung="Endkriechwert, Richtwert", referenz=TABELLE_2, stellen=1),
    KennwertVorlage(kurzname="rho", symbol=r"\rho", einheit=KG_PRO_M3,
                    beschreibung="Dichte für das Eigengewicht",
                    referenz=f"{RAUMLASTEN}; mit g = 10 m/s², nach Vorgabe", stellen=0),
)


def mauerwerk(
    sorte: str = ERSTES_MAUERWERK,
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
    symbol_index: str = "",
) -> Baustoff:
    """
    Erzeugt ein Mauerwerk aus der Sortentabelle.

    :param sorte: Bezeichnung aus :data:`MAUERWERKSSORTEN`, z.B. ``'MB'``.
    :param abweichungen: Zahlenwerte, die von der Tabelle abweichen -- bei
                         deklariertem Mauerwerk die Werte der Deklaration.
    """
    if sorte not in MAUERWERKSSORTEN:
        raise ValueError(f"Unbekanntes Mauerwerk '{sorte}'. Verfügbar: "
                         f"{', '.join(MAUERWERKSSORTEN)}.")
    s = MAUERWERKSSORTEN[sorte]
    werte: Dict[str, Groesse] = {
        "f_xk": Groesse(s.f_xk, N_PRO_MM2), "f_txk": Groesse(s.f_txk, N_PRO_MM2),
        "f_yk": Groesse(GAMMA_M * s.f_yd, N_PRO_MM2),
        "f_yk_v": Groesse(GAMMA_M * s.f_yd_v, N_PRO_MM2),
        "phi": Groesse(s.bindung.phi, EINHEITSLOS),
        "rho": Groesse(s.raumlast * 100.0, KG_PRO_M3),
    }
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.MAUERWERK,
        name=name or sorte,
        sorte=sorte,
        vorlagen=MAUERWERK_VORLAGEN,
        werte=werte,
        praefix=praefix,
        symbol_index=symbol_index,
    )
