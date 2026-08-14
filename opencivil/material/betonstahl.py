"""
opencivil/material/betonstahl.py -- Betonstahl nach SIA 262:2025.

VERANTWORTUNG:
Sortentabelle und Kennwertherleitung fuer Betonstahl. Aufbau wie bei
:mod:`opencivil.material.beton`: jeder abgeleitete Kennwert ist eine eigene,
einzeln nachvollziehbare und einzeln ueberschreibbare Berechnung.

Alle Formeln hier sind einheitenrein -- es gibt keine empirischen Sonderfaelle.

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.rechenwerk import Rechenwerk
    from opencivil.material.betonstahl import betonstahl

    werk = Rechenwerk()
    b500b = betonstahl("B500B").ins_rechenwerk(werk)
    print(werk.loese(b500b.id_von("f_yd")).wert(b500b.id_von("f_yd")))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional

from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, PROZENT, Groesse
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge


@dataclass(frozen=True)
class Stahlsorte:
    """Zeile der Sortentabelle."""

    f_yk: float
    """Charakteristische Fliessgrenze in N/mm^2."""

    f_yk_druck: float
    """Charakteristische Fliessgrenze auf Druck in N/mm^2."""

    eps_uk: float
    """Dehnung bei Hoechstlast in %."""

    eps_ud: float
    """Bemessungswert der Dehnung bei Hoechstlast in %."""


#: Betonstahlsorten nach SIA 262:2025, Tabelle 3.2.2.3.
#:
#: Uebernommen aus der Vorgaengerfassung des Werkzeugs. Vor dem produktiven
#: Einsatz gegen die gedruckte Norm pruefen.
STAHLSORTEN: Dict[str, Stahlsorte] = {
    "B500A": Stahlsorte(f_yk=500.0, f_yk_druck=500.0, eps_uk=2.5, eps_ud=2.0),
    "B500B": Stahlsorte(f_yk=500.0, f_yk_druck=500.0, eps_uk=5.0, eps_ud=4.5),
    "B500C": Stahlsorte(f_yk=500.0, f_yk_druck=500.0, eps_uk=7.5, eps_ud=6.5),
    "B700B": Stahlsorte(f_yk=700.0, f_yk_druck=700.0, eps_uk=5.0, eps_ud=4.5),
    "Stahl II": Stahlsorte(f_yk=345.0, f_yk_druck=345.0, eps_uk=5.0, eps_ud=4.5),
}


# ===========================================================================
# Kennwerte
# ===========================================================================

STAHL_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Eingaben aus der Sortentabelle ------------------------------------
    KennwertVorlage(
        kurzname="f_yk",
        symbol="f_{yk}",
        einheit=N_PRO_MM2,
        beschreibung="Charakteristische Fliessgrenze",
        referenz="SIA 262:2025, 3.2.2.3",
        stellen=0,
    ),
    KennwertVorlage(
        kurzname="f_yk_druck",
        symbol="f_{yk}^{-}",
        einheit=N_PRO_MM2,
        beschreibung="Charakteristische Fliessgrenze auf Druck",
        referenz="SIA 262:2025, 3.2.2.3",
        stellen=0,
    ),
    KennwertVorlage(
        kurzname="eps_uk",
        symbol=r"\varepsilon_{uk}",
        einheit=PROZENT,
        beschreibung="Dehnung bei Höchstlast",
        referenz="SIA 262:2025, 3.2.2.3",
        stellen=1,
    ),
    KennwertVorlage(
        kurzname="eps_ud",
        symbol=r"\varepsilon_{ud}",
        einheit=PROZENT,
        beschreibung="Bemessungswert der Dehnung bei Höchstlast",
        referenz="SIA 262:2025, 4.2.2.1",
        stellen=1,
    ),
    # -- Normvorgaben -------------------------------------------------------
    KennwertVorlage(
        kurzname="E_s",
        symbol="E_s",
        einheit=N_PRO_MM2,
        beschreibung="Elastizitätsmodul des Betonstahls",
        referenz="SIA 262:2025, 3.2.2.4",
        stellen=0,
        festwert=Groesse(200000, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="gamma_s",
        symbol=r"\gamma_s",
        beschreibung="Teilsicherheitsbeiwert für Betonstahl",
        referenz="SIA 262:2025, 2.4.2.6",
        stellen=2,
        festwert=Groesse(1.15, EINHEITSLOS),
        begruendung="Ständige und vorübergehende Bemessungssituation.",
    ),
    # -- Abgeleitete Kennwerte ---------------------------------------------
    KennwertVorlage(
        kurzname="f_yd",
        symbol="f_{yd}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert der Fliessgrenze",
        referenz="SIA 262:2025, 2.4.2.5",
        stellen=0,
        eingaben=("f_yk", "gamma_s"),
        vorlage_latex=r"\frac{@f_yk}{@gamma_s}",
        funktion=lambda f_yk, gamma_s: f_yk / gamma_s,
    ),
    KennwertVorlage(
        kurzname="f_yd_druck",
        symbol="f_{yd}^{-}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert der Fliessgrenze auf Druck",
        referenz="SIA 262:2025, 2.4.2.5",
        stellen=0,
        eingaben=("f_yk_druck", "gamma_s"),
        vorlage_latex=r"\frac{@f_yk_druck}{@gamma_s}",
        funktion=lambda f_yk_druck, gamma_s: f_yk_druck / gamma_s,
    ),
    KennwertVorlage(
        kurzname="eps_yd",
        symbol=r"\varepsilon_{yd}",
        einheit=PROZENT,
        beschreibung="Fliessdehnung (Bemessungswert)",
        referenz="SIA 262:2025, 4.2.2.4",
        stellen=3,
        eingaben=("f_yd", "E_s"),
        vorlage_latex=r"\frac{@f_yd}{@E_s}",
        funktion=lambda f_yd, E_s: f_yd / E_s,
    ),
)


# ===========================================================================
# Erzeugung
# ===========================================================================


def betonstahl(
    sorte: str = "B500B",
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
) -> Baustoff:
    """
    Erzeugt einen Betonstahl aus der Sortentabelle.

    :param sorte: Bezeichnung aus :data:`STAHLSORTEN`, z.B. ``'B500B'``.
    :param abweichungen: Zahlenwerte, die von der Tabelle abweichen.
    """
    if sorte not in STAHLSORTEN:
        raise ValueError(
            f"Unbekannte Betonstahlsorte '{sorte}'. Verfügbar: {', '.join(STAHLSORTEN)}."
        )
    s = STAHLSORTEN[sorte]
    werte: Dict[str, Groesse] = {
        "f_yk": Groesse(s.f_yk, N_PRO_MM2),
        "f_yk_druck": Groesse(s.f_yk_druck, N_PRO_MM2),
        "eps_uk": Groesse(s.eps_uk, PROZENT),
        "eps_ud": Groesse(s.eps_ud, PROZENT),
    }
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.BETONSTAHL,
        name=name or sorte,
        sorte=sorte,
        vorlagen=STAHL_VORLAGEN,
        werte=werte,
        praefix=praefix,
    )


def betonstahl_frei(
    name: str,
    werte: Mapping[str, Groesse],
    *,
    praefix: Optional[str] = None,
) -> Baustoff:
    """Erzeugt einen frei definierten Betonstahl ohne Sortentabelle."""
    return erzeuge(
        art=Baustoffart.BETONSTAHL,
        name=name,
        sorte="",
        vorlagen=STAHL_VORLAGEN,
        werte=werte,
        praefix=praefix or f"betonstahl.{name}",
    )
