"""
opencivil/material/beton.py -- Beton nach SIA 262:2025.

VERANTWORTUNG:
Sortentabelle und Kennwertherleitung fuer Beton. Jeder abgeleitete Kennwert ist
eine eigene Berechnung im Rechenwerk und damit einzeln nachvollziehbar und
einzeln ueberschreibbar.

ZU DEN EMPIRISCHEN FORMELN:
``tau_cd`` und ``E_cm`` sind dimensionell inhomogen -- die Norm setzt dort
stillschweigend voraus, dass in N/mm^2 gerechnet wird. Sie laufen deshalb ueber
:func:`opencivil.core.einheiten.empirisch`, das diese Voraussetzung erzwingt und
im Bericht als Annahme ausweist. Alle uebrigen Formeln sind einheitenrein und
werden ganz normal gerechnet.

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.rechenwerk import Rechenwerk
    from opencivil.material.beton import beton

    werk = Rechenwerk()
    c30 = beton("C30/37").ins_rechenwerk(werk)
    loesung = werk.loese(c30.id_von("f_cd"))
    print(loesung.wert(c30.id_von("f_cd")))
"""

from __future__ import annotations

import math
from typing import Dict, Mapping, Optional

from opencivil.core.einheiten import (
    EINHEITSLOS, MPA, N_PRO_MM2, PROMILLE, Groesse, empirisch,
)
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge

# ===========================================================================
# Sortentabelle
# ===========================================================================

#: Betonsorten nach SIA 262:2025, Tabelle 3.1.2.2.7 -- (f_ck, f_ctm) in N/mm^2.
#:
#: Uebernommen aus der Vorgaengerfassung des Werkzeugs. Vor dem produktiven
#: Einsatz gegen die gedruckte Norm pruefen.
BETONSORTEN: Dict[str, tuple[float, float]] = {
    "C12/15": (12.0, 1.6),
    "C16/20": (16.0, 1.9),
    "C20/25": (20.0, 2.2),
    "C25/30": (25.0, 2.6),
    "C30/37": (30.0, 2.9),
    "C35/45": (35.0, 3.2),
    "C40/50": (40.0, 3.5),
    "C45/55": (45.0, 3.8),
    "C50/60": (50.0, 4.1),
}


# ===========================================================================
# Kennwerte
# ===========================================================================


def _tau_cd(f_ck: Groesse, gamma_c: Groesse):
    """SIA 262:2025, 2.4.2.4 -- empirisch, f_ck in N/mm^2."""
    return empirisch(
        lambda f_ck, gamma_c: 0.3 * math.sqrt(f_ck) / gamma_c,
        ergebnis=N_PRO_MM2,
        f_ck=(f_ck, N_PRO_MM2),
        gamma_c=(gamma_c, EINHEITSLOS),
    )


def _e_cm(k_e: Groesse, f_cm: Groesse):
    """SIA 262:2025, 3.1.2.3.3 -- empirisch, f_cm in N/mm^2."""
    return empirisch(
        lambda k_e, f_cm: k_e * f_cm ** (1.0 / 3.0),
        ergebnis=N_PRO_MM2,
        k_e=(k_e, EINHEITSLOS),
        f_cm=(f_cm, N_PRO_MM2),
    )


def _eta_fc(f_ck: Groesse) -> Groesse:
    """SIA 262:2025, 2.4.2.3 -- einheitenrein, da nur ein Verhaeltnis eingeht."""
    verhaeltnis = (Groesse(40, N_PRO_MM2) / f_ck) ** (1.0 / 3.0)
    return min(verhaeltnis, Groesse(1.0, EINHEITSLOS))


#: Alle Betonkennwerte in der Reihenfolge, in der sie im Bericht erscheinen.
BETON_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Eingaben aus der Sortentabelle ------------------------------------
    KennwertVorlage(
        kurzname="f_ck",
        symbol="f_{ck}",
        einheit=N_PRO_MM2,
        beschreibung="Charakteristische Zylinderdruckfestigkeit",
        referenz="SIA 262:2025, 3.1.2.2.7",
        stellen=1,
    ),
    KennwertVorlage(
        kurzname="f_ctm",
        symbol="f_{ctm}",
        einheit=N_PRO_MM2,
        beschreibung="Mittelwert der Zugfestigkeit",
        referenz="SIA 262:2025, 3.1.2.2.7",
        stellen=2,
    ),
    # -- Normvorgaben -------------------------------------------------------
    KennwertVorlage(
        kurzname="gamma_c",
        symbol=r"\gamma_c",
        beschreibung="Teilsicherheitsbeiwert für Beton",
        referenz="SIA 262:2025, 2.4.2.6",
        stellen=2,
        festwert=Groesse(1.5, EINHEITSLOS),
        begruendung="Ständige und vorübergehende Bemessungssituation.",
    ),
    KennwertVorlage(
        kurzname="gamma_cE",
        symbol=r"\gamma_{cE}",
        beschreibung="Teilsicherheitsbeiwert für den Elastizitätsmodul",
        referenz="SIA 262:2025, 4.2.1.15",
        stellen=2,
        festwert=Groesse(1.0, EINHEITSLOS),
    ),
    KennwertVorlage(
        kurzname="k_e",
        symbol="k_e",
        beschreibung="Beiwert für die Gesteinskörnung",
        referenz="SIA 262:2025, 3.1.2.3.3",
        stellen=0,
        festwert=Groesse(10000, EINHEITSLOS),
        begruendung="Regelwert für übliche Gesteinskörnung.",
    ),
    KennwertVorlage(
        kurzname="eps_c1d",
        symbol=r"\varepsilon_{c1d}",
        einheit=PROMILLE,
        beschreibung="Dehnung am Ende des ansteigenden Astes",
        referenz="SIA 262:2025, 4.2.1.4",
        stellen=2,
        festwert=Groesse(2.0, PROMILLE),
    ),
    KennwertVorlage(
        kurzname="eps_c2d",
        symbol=r"\varepsilon_{c2d}",
        einheit=PROMILLE,
        beschreibung="Bruchdehnung des Betons",
        referenz="SIA 262:2025, 4.2.1.4",
        stellen=2,
        festwert=Groesse(3.5, PROMILLE),
    ),
    # -- Abgeleitete Kennwerte ---------------------------------------------
    KennwertVorlage(
        kurzname="eta_fc",
        symbol=r"\eta_{fc}",
        beschreibung="Beiwert zur Berücksichtigung der Festigkeitsminderung",
        referenz="SIA 262:2025, 2.4.2.3",
        stellen=3,
        eingaben=("f_ck",),
        vorlage_latex=(
            r"\min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{@f_ck}"
            r"\right)^{1/3};\ 1.0\right]"
        ),
        funktion=_eta_fc,
    ),
    KennwertVorlage(
        kurzname="f_cd",
        symbol="f_{cd}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert der Betondruckfestigkeit",
        referenz="SIA 262:2025, 2.4.2.3",
        stellen=1,
        eingaben=("eta_fc", "f_ck", "gamma_c"),
        vorlage_latex=r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}",
        funktion=lambda eta_fc, f_ck, gamma_c: eta_fc * f_ck / gamma_c,
    ),
    KennwertVorlage(
        kurzname="tau_cd",
        symbol=r"\tau_{cd}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert der Schubspannungsgrenze",
        referenz="SIA 262:2025, 2.4.2.4",
        stellen=2,
        eingaben=("f_ck", "gamma_c"),
        vorlage_latex=r"\frac{0.3 \cdot \sqrt{@f_ck}}{@gamma_c}",
        funktion=_tau_cd,
    ),
    KennwertVorlage(
        kurzname="f_cm",
        symbol="f_{cm}",
        einheit=N_PRO_MM2,
        beschreibung="Mittelwert der Zylinderdruckfestigkeit",
        referenz="SIA 262:2025, 3.1.2.2.2",
        stellen=1,
        eingaben=("f_ck",),
        vorlage_latex=r"@f_ck + 8\,\mathrm{N}/\mathrm{mm}^{2}",
        funktion=lambda f_ck: f_ck + Groesse(8, N_PRO_MM2),
    ),
    KennwertVorlage(
        kurzname="E_cm",
        symbol="E_{cm}",
        einheit=N_PRO_MM2,
        beschreibung="Mittelwert des Elastizitätsmoduls",
        referenz="SIA 262:2025, 3.1.2.3.3",
        stellen=0,
        eingaben=("k_e", "f_cm"),
        vorlage_latex=r"@k_e \cdot \sqrt[3]{@f_cm}",
        funktion=_e_cm,
    ),
    KennwertVorlage(
        kurzname="E_cd",
        symbol="E_{cd}",
        einheit=N_PRO_MM2,
        beschreibung="Bemessungswert des Elastizitätsmoduls",
        referenz="SIA 262:2025, 4.2.1.15",
        stellen=0,
        eingaben=("E_cm", "gamma_cE"),
        vorlage_latex=r"\frac{@E_cm}{@gamma_cE}",
        funktion=lambda E_cm, gamma_cE: E_cm / gamma_cE,
    ),
    KennwertVorlage(
        kurzname="k_sigma",
        symbol=r"k_{\sigma}",
        beschreibung="Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung",
        referenz="SIA 262:2025, 4.2.1.6",
        stellen=3,
        eingaben=("E_cd", "f_cd"),
        vorlage_latex=r"\frac{@E_cd}{400 \cdot @f_cd}",
        funktion=lambda E_cd, f_cd: E_cd / (400 * f_cd),
    ),
)


# ===========================================================================
# Erzeugung
# ===========================================================================


def beton(
    sorte: str = "C30/37",
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
) -> Baustoff:
    """
    Erzeugt einen Beton aus der Sortentabelle.

    :param sorte: Bezeichnung aus :data:`BETONSORTEN`, z.B. ``'C30/37'``.
    :param name: abweichender Anzeigename, sonst die Sorte.
    :param praefix: eigener Namensraum, falls mehrere Betone derselben Sorte
                    im Modell vorkommen sollen.
    :param abweichungen: Zahlenwerte, die von der Sortentabelle abweichen --
                    fuer selbst definierte Materialien.
    """
    if sorte not in BETONSORTEN:
        raise ValueError(
            f"Unbekannte Betonsorte '{sorte}'. Verfügbar: {', '.join(BETONSORTEN)}."
        )
    f_ck, f_ctm = BETONSORTEN[sorte]
    werte: Dict[str, Groesse] = {
        "f_ck": Groesse(f_ck, N_PRO_MM2),
        "f_ctm": Groesse(f_ctm, N_PRO_MM2),
    }
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.BETON,
        name=name or sorte,
        sorte=sorte,
        vorlagen=BETON_VORLAGEN,
        werte=werte,
        praefix=praefix,
    )


def beton_frei(
    name: str,
    werte: Mapping[str, Groesse],
    *,
    praefix: Optional[str] = None,
) -> Baustoff:
    """
    Erzeugt einen frei definierten Beton ohne Sortentabelle.

    Erwartet mindestens ``f_ck`` und ``f_ctm``; alles Weitere kann angegeben
    werden, um Normvorgaben zu ersetzen.
    """
    return erzeuge(
        art=Baustoffart.BETON,
        name=name,
        sorte="",
        vorlagen=BETON_VORLAGEN,
        werte=werte,
        praefix=praefix or f"beton.{name}",
    )
