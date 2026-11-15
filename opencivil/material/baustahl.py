"""
opencivil/material/baustahl.py -- Baustahl nach SIA 263:2013.

VERANTWORTUNG:
Sortentabelle und Kennwerte fuer Baustahl, aufgebaut wie Beton und
Betonstahl (:mod:`opencivil.material.basis`): jeder Kennwert ist eine eigene,
einzeln ueberschreibbare Berechnung.

DIE SORTENTABELLE:
SIA 263:2013, 3.2.2.3, Tabelle 1 nennt fuer S235, S275, S355 und S460 die
Streckgrenze, die Fliessschubspannung und die Zugfestigkeit, je fuer Dicken
bis 40 mm und fuer 40 mm < t ≤ 100 mm. Beide Spalten stehen als Kennwerte da;
welche gilt, haengt an der Dicke des Erzeugnisses, nicht am Material. Am
2026-11-15 gegen die gedruckte Tabelle geprueft.

DIE NORMVORGABEN:
Dichte, Elastizitaetsmodul, Schubmodul und Querdehnungszahl stehen in
3.2.2.1, die Widerstandsbeiwerte in 4.1.3. Die Waermedehnzahl (3.2.2.2) fehlt
noch: das Werkzeug kennt keine Temperatur als Einheit, und keine Rechnung
braucht sie.

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.rechenwerk import Rechenwerk
    from opencivil.material.baustahl import baustahl

    werk = Rechenwerk()
    s355 = baustahl("S355").ins_rechenwerk(werk)
    print(werk.loese(s355.id_von("eps_y")).wert(s355.id_von("eps_y")))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional

from opencivil.core.einheiten import EINHEITSLOS, KG_PRO_M3, N_PRO_MM2, PROMILLE, Groesse
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge
from opencivil.material.betonstahl import FLIESSDEHNUNG

#: Wo die Sortentabelle steht -- jeder Wert aus ihr nennt diese Stelle.
TABELLE_1 = "SIA 263:2013, 3.2.2.3, Tabelle 1"


@dataclass(frozen=True)
class Baustahlsorte:
    """Eine Zeile von Tabelle 1, in N/mm² -- links bis 40 mm Dicke, rechts darueber."""

    f_y: float
    tau_y: float
    f_u: float
    f_y_dick: float
    tau_y_dick: float
    f_u_dick: float


#: Baustahlsorten nach SIA 263:2013, Tabelle 1.
BAUSTAHLSORTEN: Dict[str, Baustahlsorte] = {
    "S235": Baustahlsorte(235.0, 135.0, 360.0, 215.0, 124.0, 340.0),
    "S275": Baustahlsorte(275.0, 160.0, 430.0, 255.0, 147.0, 410.0),
    "S355": Baustahlsorte(355.0, 205.0, 510.0, 335.0, 193.0, 490.0),
    "S460": Baustahlsorte(460.0, 265.0, 550.0, 430.0, 248.0, 530.0),
}

#: Womit ein neuer Baustahl anfaengt: die Folge der Tabelle.
ERSTER_BAUSTAHL = "S235"


def baustahlsorten_zum_anlegen() -> List[str]:
    """Die Sorten in der Reihenfolge, in der neue angelegt werden -- wie in Tabelle 1."""
    return [ERSTER_BAUSTAHL] + [s for s in BAUSTAHLSORTEN if s != ERSTER_BAUSTAHL]


# ===========================================================================
# Kennwerte
# ===========================================================================


def _tabellenwert(kurzname: str, symbol: str, beschreibung: str) -> KennwertVorlage:
    return KennwertVorlage(kurzname=kurzname, symbol=symbol, einheit=N_PRO_MM2,
                           beschreibung=beschreibung, referenz=TABELLE_1, stellen=0)


#: Was ueber 40 mm Dicke gilt, steht unter demselben Zeichen mit ``t>40`` oben.
DICK = "für 40 mm < t ≤ 100 mm"

BAUSTAHL_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Eingaben aus der Sortentabelle ------------------------------------
    _tabellenwert("f_y", "f_y", "Streckgrenze"),
    _tabellenwert("tau_y", r"\tau_y", "Fliessschubspannung"),
    _tabellenwert("f_u", "f_u", "Zugfestigkeit"),
    _tabellenwert("f_y_dick", "f_y^{t>40}", f"Streckgrenze {DICK}"),
    _tabellenwert("tau_y_dick", r"\tau_y^{t>40}", f"Fliessschubspannung {DICK}"),
    _tabellenwert("f_u_dick", "f_u^{t>40}", f"Zugfestigkeit {DICK}"),
    # -- Normvorgaben -------------------------------------------------------
    KennwertVorlage(
        kurzname="E_a",
        symbol="E_a",
        einheit=N_PRO_MM2,
        beschreibung="Elastizitätsmodul des Baustahls",
        referenz="SIA 263:2013, 3.2.2.1",
        stellen=0,
        festwert=Groesse(210000, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="G_a",
        symbol="G_a",
        einheit=N_PRO_MM2,
        beschreibung="Schubmodul des Baustahls",
        referenz="SIA 263:2013, 3.2.2.1",
        stellen=0,
        festwert=Groesse(81000, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="nu_a",
        symbol=r"\nu_a",
        beschreibung="Querdehnungszahl des Baustahls",
        referenz="SIA 263:2013, 3.2.2.1",
        stellen=1,
        festwert=Groesse(0.3, EINHEITSLOS),
    ),
    KennwertVorlage(
        kurzname="rho_a",
        symbol=r"\rho_a",
        einheit=KG_PRO_M3,
        beschreibung="Dichte des Baustahls",
        referenz="SIA 263:2013, 3.2.2.1",
        stellen=0,
        festwert=Groesse(7850, KG_PRO_M3),
    ),
    KennwertVorlage(
        kurzname="gamma_M1",
        symbol=r"\gamma_{M1}",
        beschreibung="Widerstandsbeiwert für Festigkeits- und Stabilitätsnachweise",
        referenz="SIA 263:2013, 4.1.3",
        stellen=2,
        festwert=Groesse(1.05, EINHEITSLOS),
    ),
    KennwertVorlage(
        kurzname="gamma_M2",
        symbol=r"\gamma_{M2}",
        beschreibung="Widerstandsbeiwert für Verbindungsmittel und Nettoquerschnitt",
        referenz="SIA 263:2013, 4.1.3",
        stellen=2,
        festwert=Groesse(1.25, EINHEITSLOS),
    ),
    # -- Abgeleitete Kennwerte ---------------------------------------------
    KennwertVorlage(
        kurzname="eps_y",
        symbol=r"\varepsilon_y",
        einheit=PROMILLE,
        beschreibung="Fliessdehnung des Baustahls",
        referenz="SIA 263:2013, 3.2.2.4",
        name=FLIESSDEHNUNG,
        stellen=2,
        eingaben=("f_y", "E_a"),
        vorlage_latex=r"\frac{@f_y}{@E_a}",
        funktion=lambda f_y, E_a: f_y / E_a,
    ),
)


# ===========================================================================
# Erzeugung
# ===========================================================================


def baustahl(
    sorte: str = ERSTER_BAUSTAHL,
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
    symbol_index: str = "",
) -> Baustoff:
    """
    Erzeugt einen Baustahl aus der Sortentabelle.

    :param sorte: Bezeichnung aus :data:`BAUSTAHLSORTEN`, z.B. ``'S355'``.
    :param abweichungen: Zahlenwerte, die von der Tabelle abweichen.
    """
    if sorte not in BAUSTAHLSORTEN:
        raise ValueError(
            f"Unbekannte Baustahlsorte '{sorte}'. Verfügbar: {', '.join(BAUSTAHLSORTEN)}."
        )
    s = BAUSTAHLSORTEN[sorte]
    werte: Dict[str, Groesse] = {
        kurz: Groesse(getattr(s, kurz), N_PRO_MM2)
        for kurz in ("f_y", "tau_y", "f_u", "f_y_dick", "tau_y_dick", "f_u_dick")
    }
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.BAUSTAHL,
        name=name or sorte,
        sorte=sorte,
        vorlagen=BAUSTAHL_VORLAGEN,
        werte=werte,
        praefix=praefix,
        symbol_index=symbol_index,
    )
