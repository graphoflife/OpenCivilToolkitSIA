"""
opencivil/material/profilblech.py -- Profilblechstahl nach SIA 264:2014.

VERANTWORTUNG:
Sortentabelle und Kennwerte des Stahls, aus dem die Profilbleche einer
Blechverbunddecke sind, aufgebaut wie der Baustahl
(:mod:`opencivil.material.baustahl`): jeder Kennwert ist eine eigene, einzeln
ueberschreibbare Berechnung. Das Blech selbst -- seine Rippen und seine
Flaeche aus dem Datenblatt -- gehoert zur Blechverbunddecke, einem Element
der Querschnittsanalyse (:mod:`opencivil.projekt.blechdecken`); seine Form
rechnet :mod:`opencivil.querschnitt.profilblech`, und ``m`` und ``k`` des
Laengsschubs stehen an der Analyse. Nichts davon gehoert zum Material.

DIE SORTENTABELLE:
SIA 264:2014, 3.3.1, Tabelle 1 nennt fuer die Sorten SE 220 G bis SE 550 G
nach SN EN 10346 die Streckgrenze ``f_yp`` und die Zugfestigkeit ``f_u``,
fuer Dicken bis 3 mm. Die Bruchdehnung der Tabelle braucht keine Rechnung;
sie fehlt hier. Am 2026-11-27 gegen die gedruckte Tabelle geprueft.

DIE NORMVORGABEN:
Den Elastizitaetsmodul nennt SIA 264 nicht selbst: nach 3.1.1 gelten die
Eigenschaften der SIA 263, also ``E_a`` aus 3.2.2.1. Der
Widerstandsbeiwert ``γ_ap = 1.05`` steht in 4.1.5, der Bemessungswert
``f_yp/γ_ap`` in 4.1.3, Gleichung (1).

DIE ERSTE SORTE:
SE 350 G -- nach 3.3.1 sind SE 320 G und SE 350 G ueblich (nach Vorgabe,
nicht nachgeschlagen, welche von beiden zuerst steht).

DAS GESETZ:
Wie beim Baustahl elastisch -- ideal plastisch, in Zug und Druck gleich
(:class:`~opencivil.querschnitt.werkstoffgesetz.Profilblechgesetz`). Die Norm
nennt keine Linie und keine Grenzdehnung; nach Vorgabe, nicht
nachgeschlagen, endet sie wie beim Baustahl bei
:data:`~opencivil.material.baustahl.DUKTILITAET` mal der Fliessdehnung.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional

from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, PROMILLE, Groesse
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge
from opencivil.material.baustahl import DUKTILITAET
from opencivil.material.betonstahl import FLIESSDEHNUNG

#: Wo die Sortentabelle steht -- jeder Wert aus ihr nennt diese Stelle.
TABELLE_1 = "SIA 264:2014, 3.3.1, Tabelle 1"


@dataclass(frozen=True)
class Profilblechsorte:
    """Eine Zeile von Tabelle 1, in N/mm²."""

    f_yp: float
    f_u: float


#: Profilblechstahl nach SIA 264:2014, Tabelle 1 -- in ihrer Folge.
PROFILBLECHSORTEN: Dict[str, Profilblechsorte] = {
    "SE 220 G": Profilblechsorte(220.0, 300.0),
    "SE 250 G": Profilblechsorte(250.0, 330.0),
    "SE 280 G": Profilblechsorte(280.0, 360.0),
    "SE 320 G": Profilblechsorte(320.0, 390.0),
    "SE 350 G": Profilblechsorte(350.0, 420.0),
    "SE 550 G": Profilblechsorte(550.0, 560.0),
}

#: Womit ein neuer Profilblechstahl anfaengt -- siehe Dateikopf.
ERSTES_PROFILBLECH = "SE 350 G"


def profilblechsorten_zum_anlegen() -> List[str]:
    """Die Sorten in der Folge, in der neue angelegt werden: die erste, dann die Tabelle."""
    return [ERSTES_PROFILBLECH] + [s for s in PROFILBLECHSORTEN if s != ERSTES_PROFILBLECH]


# ===========================================================================
# Kennwerte
# ===========================================================================


PROFILBLECH_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Eingaben aus der Sortentabelle ------------------------------------
    KennwertVorlage(kurzname="f_yp", symbol="f_{yp}", einheit=N_PRO_MM2,
                    beschreibung="Streckgrenze des Profilblechstahls", referenz=TABELLE_1,
                    stellen=0),
    KennwertVorlage(kurzname="f_u", symbol="f_u", einheit=N_PRO_MM2,
                    beschreibung="Zugfestigkeit", referenz=TABELLE_1, stellen=0),
    # -- Normvorgaben -------------------------------------------------------
    KennwertVorlage(
        kurzname="E_a",
        symbol="E_a",
        einheit=N_PRO_MM2,
        beschreibung="Elastizitätsmodul des Stahls",
        referenz="SIA 264:2014, 3.1.1; SIA 263:2013, 3.2.2.1",
        stellen=0,
        festwert=Groesse(210000, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="gamma_ap",
        symbol=r"\gamma_{ap}",
        beschreibung="Widerstandsbeiwert des Profilblechstahls",
        referenz="SIA 264:2014, 4.1.5",
        stellen=2,
        festwert=Groesse(1.05, EINHEITSLOS),
    ),
    # -- Abgeleitete Kennwerte ---------------------------------------------
    KennwertVorlage(
        kurzname="eps_yp",
        symbol=r"\varepsilon_{yp}",
        einheit=PROMILLE,
        beschreibung="Fliessdehnung des Profilblechstahls",
        referenz="SIA 264:2014, 3.1.1",
        name=FLIESSDEHNUNG,
        stellen=2,
        eingaben=("f_yp", "E_a"),
        vorlage_latex=r"\frac{@f_yp}{@E_a}",
        funktion=lambda f_yp, E_a: f_yp / E_a,
    ),
    KennwertVorlage(
        kurzname="f_ypd",
        symbol="f_{ypd}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert der Streckgrenze",
        referenz="SIA 264:2014, 4.1.3, (1); 4.1.5",
        stellen=0,
        eingaben=("f_yp", "gamma_ap"),
        vorlage_latex=r"\frac{@f_yp}{@gamma_ap}",
        funktion=lambda f_yp, gamma_ap: f_yp / gamma_ap,
    ),
    KennwertVorlage(
        kurzname="eps_ud",
        symbol=r"\varepsilon_{ud}",
        einheit=PROMILLE,
        beschreibung="Grenzdehnung des Profilblechstahls",
        referenz="SIA 264:2014, 3.1.1; als Grenzdehnung nach Vorgabe",
        stellen=1,
        eingaben=("eps_yp",),
        vorlage_latex=rf"{DUKTILITAET:g} \cdot @eps_yp",
        funktion=lambda eps_yp: DUKTILITAET * eps_yp,
        begruendung=("Nach Vorgabe, nicht nachgeschlagen: die Norm nennt keine Grenzdehnung. "
                     f"Die Linie endet wie beim Baustahl bei {DUKTILITAET:g} Fliessdehnungen."),
    ),
)


# ===========================================================================
# Erzeugung
# ===========================================================================


def profilblech(
    sorte: str = ERSTES_PROFILBLECH,
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
    symbol_index: str = "",
) -> Baustoff:
    """
    Erzeugt einen Profilblechstahl aus der Sortentabelle.

    :param sorte: Bezeichnung aus :data:`PROFILBLECHSORTEN`, z.B. ``'SE 350 G'``.
    :param abweichungen: Zahlenwerte, die von der Tabelle abweichen.
    """
    if sorte not in PROFILBLECHSORTEN:
        raise ValueError(f"Unbekannte Sorte des Profilblechstahls '{sorte}'. Verfügbar: "
                         f"{', '.join(PROFILBLECHSORTEN)}.")
    s = PROFILBLECHSORTEN[sorte]
    werte: Dict[str, Groesse] = {"f_yp": Groesse(s.f_yp, N_PRO_MM2),
                                 "f_u": Groesse(s.f_u, N_PRO_MM2)}
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.PROFILBLECH,
        name=name or sorte,
        sorte=sorte,
        vorlagen=PROFILBLECH_VORLAGEN,
        werte=werte,
        praefix=praefix,
        symbol_index=symbol_index,
    )
