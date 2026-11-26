"""
opencivil/material/spannstahl.py -- Spannstahl nach SIA 262:2025.

VERANTWORTUNG:
Sortentabelle, Erzeugnisse und Kennwerte fuer Spannstahl, aufgebaut wie
Beton und Betonstahl (:mod:`opencivil.material.basis`): jeder Kennwert ist
eine eigene, einzeln ueberschreibbare Berechnung.

SORTEN UND ERZEUGNISSE:
Tabelle 7 (3.3.2.2) nennt je Erzeugnis -- Draht, Litze oder Stab mit seinem
Durchmesser -- die Querschnittsflaeche A_p, die Zugfestigkeit f_pk und die
0.1-%-Dehngrenze f_p0.1k. Die Festigkeiten haengen nur an der Sorte: jede
Sorte Y… hat in allen ihren Zeilen dieselben. Darum ist die Sorte das
Material, und die Erzeugnisse stehen bei ihr (:class:`Erzeugnis`): ein
Spannglied waehlt eines davon, und die Flaeche kommt aus der Tabelle -- eine
Litze 15.7 mm hat 150 mm², nicht π·d²/4. Die Sorten stehen in der Folge der
Tabelle 10 (4.2.3.1), Y1860 zuerst. Am 2026-11-26 gegen die gedruckten
Tabellen 7 und 10 geprueft.

DER MODUL:
Er haengt am Erzeugnis, nicht an der Sorte: 200 GPa fuer Draehte und Staebe
(3.3.2.4.1), 195 GPa fuer Litzen (3.3.2.4.2). Beide stehen als Kennwerte da,
wie beim Baustahl die beiden Spalten der Dicke; welcher gilt, sagt das
Erzeugnis (:meth:`Erzeugnis.modul`).

DAS GESETZ:
Figur 17 (4.2.3.3) idealisiert nur den Zug: mit E_p bis f_pd, dann
waagrecht bis eps_ud = 2 % (Tabelle 10) -- ideal plastisch, wie 4.2.3.5 es
zulaesst (:class:`~opencivil.querschnitt.werkstoffgesetz.Spannstahlgesetz`).
f_pd = f_p0.1k / gamma_s nach Gleichung (5) (2.4.2.5) mit gamma_s = 1.15
(2.4.2.6). Tabelle 10 nennt dieselben Zahlen gerundet: 1390 statt 1391
N/mm² bei Y1860 -- gerechnet wird ungerundet, wie f_yd des Betonstahls.

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.rechenwerk import Rechenwerk
    from opencivil.material.spannstahl import spannstahl

    werk = Rechenwerk()
    y1860 = spannstahl("Y1860").ins_rechenwerk(werk)
    print(werk.loese(y1860.id_von("f_pd")).wert(y1860.id_von("f_pd")))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Tuple

from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, PROZENT, Groesse
from opencivil.core.wahl import Wahl
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge
from opencivil.material.betonstahl import FLIESSDEHNUNG

#: Wo die Sortentabelle steht -- jeder Wert aus ihr nennt diese Stelle.
TABELLE_7 = "SIA 262:2025, 3.3.2.2, Tabelle 7"


class Erzeugnisart(Wahl):
    """Was Tabelle 7 unterscheidet: Draht, Litze oder Stab (glatt oder gerippt)."""

    DRAHT = "draht"
    LITZE = "litze"
    STAB = "stab"

    @property
    def beschriftung(self) -> str:
        return {Erzeugnisart.DRAHT: "Draht", Erzeugnisart.LITZE: "Litze",
                Erzeugnisart.STAB: "Stab"}[self]

    @property
    def mehrzahl(self) -> str:
        return {Erzeugnisart.DRAHT: "Drähte", Erzeugnisart.LITZE: "Litzen",
                Erzeugnisart.STAB: "Stäbe"}[self]

    @property
    def kuerzel(self) -> str:
        """Was die Bezeichnung der Tabelle hinter die Sorte setzt: C, S7 oder H."""
        return {Erzeugnisart.DRAHT: "C", Erzeugnisart.LITZE: "S7", Erzeugnisart.STAB: "H"}[self]

    @property
    def modul(self) -> str:
        """Der Kurzname des Moduls, der fuer diese Art gilt (3.3.2.4)."""
        return "E_p_litze" if self is Erzeugnisart.LITZE else "E_p"


@dataclass(frozen=True)
class Erzeugnis:
    """Eine Zeile von Tabelle 7: Art, Durchmesser in mm, Querschnittsflaeche A_p in mm²."""

    art: Erzeugnisart
    durchmesser: float
    flaeche: float

    @property
    def modul(self) -> str:
        """Der Kurzname des Moduls, mit dem es rechnet: ``E_p`` oder ``E_p_litze``."""
        return self.art.modul

    def bezeichnung(self, sorte: str) -> str:
        """Wie Tabelle 7 es nennt, mit dem Dezimalpunkt des Werkzeugs: «Y1860S7-15.7»."""
        return f"{sorte}{self.art.kuerzel}-{self.durchmesser:.1f}"


@dataclass(frozen=True)
class Spannstahlsorte:
    """Eine Sorte: f_pk und f_p0.1k in N/mm², dazu ihre Erzeugnisse aus Tabelle 7."""

    f_pk: float
    f_p01k: float
    erzeugnisse: Tuple[Erzeugnis, ...]


def _reihe(art: Erzeugnisart, *zeilen: Tuple[float, float]) -> Tuple[Erzeugnis, ...]:
    return tuple(Erzeugnis(art, d, a) for d, a in zeilen)


_D, _L, _S = Erzeugnisart.DRAHT, Erzeugnisart.LITZE, Erzeugnisart.STAB

#: Die Staebe der Sorten Y1030, Y1050 und Y1230 -- in Tabelle 7 je dieselben vier.
_STAEBE = _reihe(_S, (26.0, 531.0), (26.5, 552.0), (32.0, 804.0), (36.0, 1018.0))

#: Spannstahlsorten nach SIA 262:2025, Tabelle 7, in der Folge der Tabelle 10.
SPANNSTAHLSORTEN: Dict[str, Spannstahlsorte] = {
    "Y1860": Spannstahlsorte(1860.0, 1600.0, _reihe(_D, (3.0, 7.1), (4.0, 12.6), (5.0, 19.6))
                             + _reihe(_L, (12.9, 100.0), (15.3, 140.0), (15.7, 150.0))),
    "Y1770": Spannstahlsorte(1770.0, 1520.0, _reihe(_D, (6.0, 28.3))
                             + _reihe(_L, (15.3, 140.0), (15.7, 150.0))),
    "Y1670": Spannstahlsorte(1670.0, 1440.0, _reihe(_D, (7.0, 38.5), (8.0, 50.3))),
    "Y1570": Spannstahlsorte(1570.0, 1300.0, _reihe(_D, (10.0, 78.5))),
    "Y1230": Spannstahlsorte(1230.0, 1080.0, _STAEBE),
    "Y1100": Spannstahlsorte(1100.0, 900.0, _reihe(_S, (20.0, 314.0))),
    "Y1050": Spannstahlsorte(1050.0, 950.0, _STAEBE),
    "Y1030": Spannstahlsorte(1030.0, 830.0, _STAEBE),
}

#: Womit ein neuer Spannstahl anfaengt: die Folge der Tabelle 10.
ERSTER_SPANNSTAHL = "Y1860"


def spannstahlsorten_zum_anlegen() -> List[str]:
    """Die Sorten in der Reihenfolge, in der neue angelegt werden -- wie in Tabelle 10."""
    return [ERSTER_SPANNSTAHL] + [s for s in SPANNSTAHLSORTEN if s != ERSTER_SPANNSTAHL]


# ===========================================================================
# Kennwerte
# ===========================================================================

SPANNSTAHL_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Eingaben aus der Sortentabelle ------------------------------------
    KennwertVorlage(
        kurzname="f_pk",
        symbol="f_{pk}",
        einheit=N_PRO_MM2,
        beschreibung="Zugfestigkeit",
        referenz=TABELLE_7,
        stellen=0,
    ),
    KennwertVorlage(
        kurzname="f_p01k",
        symbol="f_{p0.1k}",
        einheit=N_PRO_MM2,
        beschreibung="Fliessgrenze (0.1-%-Dehngrenze)",
        referenz=TABELLE_7,
        stellen=0,
    ),
    # -- Normvorgaben -------------------------------------------------------
    KennwertVorlage(
        kurzname="E_p",
        symbol="E_p",
        einheit=N_PRO_MM2,
        beschreibung="Elastizitätsmodul von Drähten und Stäben",
        referenz="SIA 262:2025, 3.3.2.4.1",
        stellen=0,
        festwert=Groesse(200000, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="E_p_litze",
        symbol=r"E_p^{\mathrm{Litze}}",
        einheit=N_PRO_MM2,
        beschreibung="Elastizitätsmodul von Litzen",
        referenz="SIA 262:2025, 3.3.2.4.2",
        stellen=0,
        festwert=Groesse(195000, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="gamma_s",
        symbol=r"\gamma_s",
        beschreibung="Teilsicherheitsbeiwert für Spannstahl",
        referenz="SIA 262:2025, 2.4.2.6",
        stellen=2,
        festwert=Groesse(1.15, EINHEITSLOS),
    ),
    KennwertVorlage(
        kurzname="eps_ud",
        symbol=r"\varepsilon_{ud}",
        einheit=PROZENT,
        beschreibung="Bemessungswert der Bruchdehnung",
        referenz="SIA 262:2025, 4.2.3.1, Tabelle 10; 4.2.3.6",
        stellen=1,
        festwert=Groesse(2.0, PROZENT),
    ),
    # -- Abgeleitete Kennwerte ---------------------------------------------
    KennwertVorlage(
        kurzname="f_pd",
        symbol="f_{pd}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert der Fliessgrenze",
        referenz="SIA 262:2025, 2.4.2.5, (5); 4.2.3.1, Tabelle 10",
        stellen=0,
        eingaben=("f_p01k", "gamma_s"),
        vorlage_latex=r"\frac{@f_p01k}{@gamma_s}",
        funktion=lambda f_p01k, gamma_s: f_p01k / gamma_s,
    ),
    KennwertVorlage(
        kurzname="eps_pd",
        symbol=r"\varepsilon_{pd}",
        einheit=PROZENT,
        beschreibung="Fliessdehnung von Drähten und Stäben (Bemessungswert)",
        referenz="SIA 262:2025, 4.2.3.3, Figur 17",
        name=FLIESSDEHNUNG,
        stellen=3,
        eingaben=("f_pd", "E_p"),
        vorlage_latex=r"\frac{@f_pd}{@E_p}",
        funktion=lambda f_pd, E_p: f_pd / E_p,
    ),
    KennwertVorlage(
        kurzname="eps_pd_litze",
        symbol=r"\varepsilon_{pd}^{\mathrm{Litze}}",
        einheit=PROZENT,
        beschreibung="Fliessdehnung von Litzen (Bemessungswert)",
        referenz="SIA 262:2025, 4.2.3.3, Figur 17",
        name=FLIESSDEHNUNG,
        stellen=3,
        eingaben=("f_pd", "E_p_litze"),
        vorlage_latex=r"\frac{@f_pd}{@E_p_litze}",
        funktion=lambda f_pd, E_p_litze: f_pd / E_p_litze,
    ),
)


# ===========================================================================
# Erzeugung
# ===========================================================================


def spannstahl(
    sorte: str = ERSTER_SPANNSTAHL,
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
    symbol_index: str = "",
) -> Baustoff:
    """
    Erzeugt einen Spannstahl aus der Sortentabelle.

    :param sorte: Bezeichnung aus :data:`SPANNSTAHLSORTEN`, z.B. ``'Y1860'``.
    :param abweichungen: Zahlenwerte, die von der Tabelle abweichen.
    """
    if sorte not in SPANNSTAHLSORTEN:
        raise ValueError(
            f"Unbekannte Spannstahlsorte '{sorte}'. Verfügbar: {', '.join(SPANNSTAHLSORTEN)}."
        )
    s = SPANNSTAHLSORTEN[sorte]
    werte: Dict[str, Groesse] = {
        "f_pk": Groesse(s.f_pk, N_PRO_MM2),
        "f_p01k": Groesse(s.f_p01k, N_PRO_MM2),
    }
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.SPANNSTAHL,
        name=name or sorte,
        sorte=sorte,
        vorlagen=SPANNSTAHL_VORLAGEN,
        werte=werte,
        praefix=praefix,
        symbol_index=symbol_index,
    )
