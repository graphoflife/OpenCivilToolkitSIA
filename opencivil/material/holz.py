"""
opencivil/material/holz.py -- Holz nach SIA 265:2012.

VERANTWORTUNG:
Sortentabelle und Kennwerte fuer Vollholz und Brettschichtholz, aufgebaut
wie die anderen Baustoffe (:mod:`opencivil.material.basis`): jeder Kennwert
ist eine eigene, einzeln ueberschreibbare Berechnung.

DIE SORTENTABELLEN:
SIA 265:2012, 3.3.2, Tabelle 6 nennt fuer Vollholz -- C16, C24 und C30 aus
Nadelholz, D30 aus Buche oder Eiche --, 3.4.2.2, Tabelle 7 fuer
Brettschichtholz aus Nadelholz -- GL24k bis GL36h -- je die kennzeichnenden
Eigenschaften und die Bemessungswerte der Festigkeit und der Steifigkeit.
Die Norm gibt die Bemessungswerte selbst an, fuer Feuchteklasse 1 und ohne
stossartige Einwirkung (eta_w = eta_t = 1); aus der Biegefestigkeit
gerechnet waeren sie nicht dieselben, denn die Tabellen runden. Am
2026-11-26 gegen die gedruckten Tabellen geprueft.

FUER KNICKEN UND KIPPEN:
SIA 265:2012, Anhang B, Tabellen 43 und 44 nennt je Sorte die
kennzeichnende Druckfestigkeit in Faserrichtung und das 5%-Fraktil des
Elastizitaetsmoduls -- die relative Schlankheit (4.2.8.4, 4.2.9.3) rechnet
mit ihnen. Am 2026-11-26 gegen das Seitenbild geprueft.

DIE FEUCHTEKLASSE:
Wie feucht das Holz im Bauwerk im Mittel ist, ordnet es einer von drei
Klassen zu (3.2.1.2, Tabelle 3, :class:`Feuchteklasse`). Ihr Beiwert η_w
(Tabelle 4) mindert die Bemessungswerte der Tabellen 6 und 7, die fuer
Klasse 1 gelten -- eine Wahl des Bauteils, nicht des Materials. Ebenso η_t
(2.2.6): 1.4 bei stossartiger Einwirkung, sonst 1.

Der Elastizitaetsmodul in Faserrichtung gilt fuer Biegung, Zug und Druck
zugleich: die Tabellen nennen ihn einmal als kennzeichnende Eigenschaft,
einmal als Steifigkeit, mit derselben Zahl. Was sie sonst nennen, kommt mit
dem Nachweis, der es braucht -- der hoehere Querdruck mit Vorholz oder an
einem Endauflager, und dass C16 fuer Zugglieder nicht zugelassen ist.

DIE NORMVORGABEN:
Der Beiwert gamma_M/eta_M (2.2.5, Tabelle 1) steckt in den Bemessungswerten
schon drin -- 1.7 fuer Vollholz, 1.5 fuer Brettschichtholz --; er steht zur
Auskunft dabei. Die Dichte fuer das Eigengewicht kommt aus der mittleren
Raumlast in SIA 261:2020, Anhang A, Tabelle 28 -- Nadelholz, auch
verleimtes, 5 kN/m³, Laubholz 7.5 kN/m³ --, mit g = 10 m/s² (Benutzer,
2026-10-23). Die Rohdichte der Tabellen ist eine andere Groesse: das
5%-Fraktil, fuer die Verbindungen.

DAS GESETZ:
Linear bis zum Bruch (3.1.2.1), auf Zug bis f_t,0,d, auf Druck bis f_c,0,d
(:class:`~opencivil.querschnitt.werkstoffgesetz.Holzgesetz`). Kann ein
Bauteil plastisch stauchen, darf der Druck elastisch-plastisch gehen
(3.1.2.2); wie weit, sagt die Norm nicht -- nach Vorgabe, nicht
nachgeschlagen, bis :data:`STAUCHBARKEIT` mal die Stauchung an der Grenze
(:class:`~opencivil.querschnitt.werkstoffgesetz.HolzPlastisch`).

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.rechenwerk import Rechenwerk
    from opencivil.material.holz import holz

    werk = Rechenwerk()
    c24 = holz("C24").ins_rechenwerk(werk)
    print(werk.loese(c24.id_von("eps_t_0_d")).wert(c24.id_von("eps_t_0_d")))
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional

from opencivil.core.einheiten import EINHEITSLOS, KG_PRO_M3, N_PRO_MM2, PROMILLE, Groesse
from opencivil.core.wahl import Wahl
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage, erzeuge

#: Wo die Sortentabellen stehen -- jeder Wert aus ihnen nennt diese Stelle.
TABELLEN = "SIA 265:2012, 3.3.2, Tabelle 6; 3.4.2.2, Tabelle 7"

#: Wo der Beiwert gamma_M/eta_M steht.
TABELLE_1 = "SIA 265:2012, 2.2.5, Tabelle 1"

#: Wo die Werte fuer Knicken und Kippen stehen.
ANHANG_B = "SIA 265:2012, Anhang B, Tabellen 43 und 44"

#: Wo die Feuchteklassen stehen -- und ihr Beiwert eta_w.
TABELLE_3 = "SIA 265:2012, 3.2.1.2, Tabelle 3"
TABELLE_4 = "SIA 265:2012, 3.2.1.3, Tabelle 4"

#: Der Beiwert eta_t einer stossartigen Einwirkung -- sonst 1. Die Norm
#: laesst ihn zu, sie verlangt ihn nicht: der Benutzer waehlt je Fall.
ETA_T_STOSSARTIG = 1.4
REFERENZ_ETA_T = "SIA 265:2012, 2.2.6"

#: Was als stossartig gilt, in eigenen Worten nach 2.2.6.
STOSSARTIG = "etwa Anprall, Erdbeben oder dynamische Lasten aus dem Strassenverkehr"

#: Die Sorten, aus denen Tabelle 6 kein Zugglied zulaesst (Fussnote 2).
OHNE_ZUGGLIED = frozenset({"C16"})

#: Wo die Norm die Bemessungswerte der Tabellen mit eta_w und eta_t multipliziert.
REFERENZ_ETA = "SIA 265:2012, 3.3.2; 3.4.2.2"

#: Wo die mittleren Raumlasten stehen.
RAUMLASTEN = "SIA 261:2020, Anhang A, Tabelle 28"

#: Wie viele Stauchungen an der Druckgrenze weit der Druck elastisch-plastisch
#: geht -- nach Vorgabe, nicht nachgeschlagen: SIA 265:2012, 3.1.2.2 laesst
#: das Fliessen zu, ohne eine Grenze zu nennen.
STAUCHBARKEIT = 3.0


class Holzart(Enum):
    """Woraus eine Sorte ist -- das sagt den Beiwert und die Dichte."""

    NADELHOLZ = "Vollholz aus Nadelholz"
    LAUBHOLZ = "Vollholz aus Laubholz"
    BRETTSCHICHTHOLZ = "Brettschichtholz aus Nadelholz"

    @property
    def gamma_M_eta_M(self) -> float:
        """SIA 265:2012, 2.2.5, Tabelle 1."""
        return 1.5 if self is Holzart.BRETTSCHICHTHOLZ else 1.7

    @property
    def dichte(self) -> float:
        """kg/m³ -- die mittlere Raumlast nach SIA 261:2020, Tabelle 28, durch g = 10 m/s²."""
        return 750.0 if self is Holzart.LAUBHOLZ else 500.0

    @property
    def beta_c(self) -> float:
        """Der Hilfswert der Geradheit beim Knicken -- SIA 265:2012, 4.2.8.3."""
        return 0.1 if self is Holzart.BRETTSCHICHTHOLZ else 0.2


class Feuchteklasse(Wahl):
    """
    Wie feucht das Holz im Bauwerk im Mittel ist -- SIA 265:2012, 3.2.1.2,
    Tabelle 3, in eigenen Worten. Ihr Beiwert η_w mindert Festigkeit und
    Steifigkeit gegenueber Klasse 1 (Tabelle 4); fuer Vollholz und
    Brettschichtholz derselbe.
    """

    EINS = "1"
    ZWEI = "2"
    DREI = "3"

    @property
    def beschriftung(self) -> str:
        return f"Klasse {self.value}"

    @property
    def erklaerung(self) -> str:
        """Wo das Holz so feucht ist, in eigenen Worten."""
        return {
            Feuchteklasse.EINS: "Vor Regen und Wetter geschützt, etwa in einem Innenraum – im "
                                "Mittel höchstens 12 % Holzfeuchte.",
            Feuchteklasse.ZWEI: "Nur zum Teil geschützt oder dem Wetter ausgesetzt, etwa unter "
                                "einem offenen Dach – im Mittel 12 bis 20 %.",
            Feuchteklasse.DREI: "Nass: feucht oder im Wasser – im Mittel über 20 %.",
        }[self]

    @property
    def eta_w(self) -> float:
        """Der Beiwert des Tragwiderstands -- Tabelle 4."""
        return {Feuchteklasse.EINS: 1.0, Feuchteklasse.ZWEI: 0.8, Feuchteklasse.DREI: 0.6}[self]

    @property
    def eta_w_steifigkeit(self) -> float:
        """Der Beiwert der Steifigkeit -- Tabelle 4."""
        return {Feuchteklasse.EINS: 1.0, Feuchteklasse.ZWEI: 0.9, Feuchteklasse.DREI: 0.75}[self]


@dataclass(frozen=True)
class Holzsorte:
    """
    Eine Spalte von Tabelle 6 oder 7: N/mm², die Rohdichte in kg/m³ -- dazu
    die ihrer Sorte aus Anhang B, Tabelle 43 oder 44.
    """

    art: Holzart
    f_m_k: float
    E_0_mean: float
    rho_k: float
    f_m_d: float
    f_t_0_d: float
    f_c_0_d: float
    f_t_90_d: float
    f_c_90_d: float
    f_v_d: float
    E_90_mean: float
    G_mean: float
    f_c_0_k: float
    E_0_05: float


_N, _L, _B = Holzart.NADELHOLZ, Holzart.LAUBHOLZ, Holzart.BRETTSCHICHTHOLZ

#: Holzsorten nach SIA 265:2012, Tabelle 6 (Vollholz) und Tabelle 7
#: (Brettschichtholz), in deren Folge -- in der zweiten Zeile f_c,0,k und
#: E_0,05 aus Anhang B, Tabelle 43 und 44.
HOLZSORTEN: Dict[str, Holzsorte] = {
    #                 f_m,k  E_0,mean ρ_k  f_m,d f_t,0,d f_c,0,d f_t,90,d f_c,90,d f_v,d E_90  G
    "C16": Holzsorte(_N, 16.0, 8000.0, 310.0, 9.5, 5.5, 9.5, 0.1, 1.5, 1.5, 270.0, 500.0,
                     17.0, 5300.0),
    "C24": Holzsorte(_N, 24.0, 11000.0, 350.0, 14.0, 8.0, 12.0, 0.1, 1.8, 1.5, 300.0, 500.0,
                     21.0, 7300.0),
    "C30": Holzsorte(_N, 30.0, 12000.0, 380.0, 17.5, 10.5, 13.5, 0.1, 2.0, 1.5, 300.0, 500.0,
                     23.0, 8000.0),
    "D30": Holzsorte(_L, 30.0, 10000.0, 530.0, 17.0, 10.0, 13.0, 0.2, 5.3, 2.0, 600.0, 1000.0,
                     23.0, 8300.0),
    "GL24k": Holzsorte(_B, 24.0, 11000.0, 350.0, 16.0, 10.0, 13.0, 0.15, 1.9, 1.8, 300.0, 500.0,
                       21.0, 9400.0),
    "GL24h": Holzsorte(_B, 24.0, 11000.0, 380.0, 16.0, 12.0, 14.5, 0.15, 1.9, 1.8, 300.0, 500.0,
                       24.0, 9400.0),
    "GL28k": Holzsorte(_B, 28.0, 12000.0, 380.0, 18.5, 12.0, 16.0, 0.15, 2.0, 1.8, 300.0, 500.0,
                       24.0, 10200.0),
    "GL28h": Holzsorte(_B, 28.0, 12000.0, 410.0, 18.5, 14.0, 17.0, 0.15, 2.0, 1.8, 300.0, 500.0,
                       26.5, 10200.0),
    "GL32k": Holzsorte(_B, 32.0, 13000.0, 410.0, 21.0, 14.0, 17.5, 0.15, 2.1, 1.8, 400.0, 600.0,
                       26.5, 11100.0),
    "GL32h": Holzsorte(_B, 32.0, 13000.0, 430.0, 21.0, 16.0, 19.0, 0.15, 2.1, 1.8, 400.0, 600.0,
                       29.0, 11100.0),
    "GL36k": Holzsorte(_B, 36.0, 14000.0, 430.0, 24.0, 16.0, 18.0, 0.15, 2.2, 1.8, 400.0, 600.0,
                       29.0, 11900.0),
    "GL36h": Holzsorte(_B, 36.0, 14000.0, 450.0, 24.0, 18.0, 20.5, 0.15, 2.2, 1.8, 400.0, 600.0,
                       31.0, 11900.0),
}

#: Womit ein neues Holz anfaengt: die Sorte, die Tabelle 6 hervorhebt.
ERSTES_HOLZ = "C24"

#: Was aus der Spalte einer Sorte kommt, in N/mm² -- die Rohdichte steht extra.
_SPALTEN = ("f_m_k", "E_0_mean", "f_m_d", "f_t_0_d", "f_c_0_d", "f_t_90_d", "f_c_90_d",
            "f_v_d", "E_90_mean", "G_mean", "f_c_0_k", "E_0_05")


def eta_t(stossartig: bool) -> float:
    """Der Beiwert der Einwirkungsdauer: 1.4 bei stossartiger Einwirkung, sonst 1 (2.2.6)."""
    return ETA_T_STOSSARTIG if stossartig else 1.0


def zugglied_grund(stoff: Baustoff) -> str:
    """
    Warum dieses Holz kein Zugglied sein darf, als Satz -- leer, wo es darf
    (:data:`OHNE_ZUGGLIED`).
    """
    if stoff.sorte not in OHNE_ZUGGLIED:
        return ""
    return (f"Ein Zugglied aus {stoff.sorte} lässt SIA 265 nicht zu (Tabelle 6, Fussnote 2): "
            f"mit Zug ist «{stoff.name}» hier eines.")


def holzsorten_zum_anlegen() -> List[str]:
    """Die Sorten in der Reihenfolge, in der neue angelegt werden: C24, dann die Tabellen."""
    return [ERSTES_HOLZ] + [s for s in HOLZSORTEN if s != ERSTES_HOLZ]


def _tabellenwert(kurzname: str, symbol: str, beschreibung: str, stellen: int = 1,
                  einheit=N_PRO_MM2) -> KennwertVorlage:
    return KennwertVorlage(kurzname=kurzname, symbol=symbol, einheit=einheit,
                           beschreibung=beschreibung, referenz=TABELLEN, stellen=stellen)


HOLZ_VORLAGEN: tuple[KennwertVorlage, ...] = (
    # -- Kennzeichnende Eigenschaften (Tabellen 6 und 7) --------------------
    _tabellenwert("f_m_k", "f_{m,k}", "Biegefestigkeit, kennzeichnend", stellen=0),
    _tabellenwert("rho_k", r"\rho_k", "Rohdichte, 5%-Fraktil", stellen=0, einheit=KG_PRO_M3),
    # -- Bemessungswerte fuer Feuchteklasse 1 -------------------------------
    _tabellenwert("f_m_d", "f_{m,d}", "Bemessungswert der Biegefestigkeit"),
    _tabellenwert("f_t_0_d", "f_{t,0,d}", "Bemessungswert der Zugfestigkeit in Faserrichtung"),
    _tabellenwert("f_c_0_d", "f_{c,0,d}", "Bemessungswert der Druckfestigkeit in Faserrichtung"),
    _tabellenwert("f_t_90_d", "f_{t,90,d}", "Bemessungswert der Zugfestigkeit quer zur Faser",
                  stellen=2),
    _tabellenwert("f_c_90_d", "f_{c,90,d}", "Bemessungswert der Druckfestigkeit quer zur Faser"),
    _tabellenwert("f_v_d", "f_{v,d}", "Bemessungswert der Schubfestigkeit"),
    _tabellenwert("E_0_mean", "E_{0,mean}", "Elastizitätsmodul in Faserrichtung, Mittelwert",
                  stellen=0),
    _tabellenwert("E_90_mean", "E_{90,mean}", "Elastizitätsmodul quer zur Faser, Mittelwert",
                  stellen=0),
    _tabellenwert("G_mean", "G_{mean}", "Schubmodul, Mittelwert", stellen=0),
    # -- Fuer Knicken und Kippen (Anhang B) ---------------------------------
    KennwertVorlage(kurzname="f_c_0_k", symbol="f_{c,0,k}", einheit=N_PRO_MM2,
                    beschreibung="Druckfestigkeit in Faserrichtung, kennzeichnend",
                    referenz=ANHANG_B, stellen=1),
    KennwertVorlage(kurzname="E_0_05", symbol="E_{0,05}", einheit=N_PRO_MM2,
                    beschreibung="Elastizitätsmodul in Faserrichtung, 5%-Fraktil",
                    referenz=ANHANG_B, stellen=0),
    # -- Je Holzart ---------------------------------------------------------
    KennwertVorlage(
        kurzname="gamma_M_eta_M",
        symbol=r"\gamma_M/\eta_M",
        beschreibung="Widerstandsbeiwert durch Umrechnungsfaktor, in den Bemessungswerten enthalten",
        referenz=TABELLE_1,
        stellen=1,
    ),
    KennwertVorlage(
        kurzname="rho_mean",
        symbol=r"\rho_{mean}",
        einheit=KG_PRO_M3,
        beschreibung="Dichte für das Eigengewicht",
        referenz=f"{RAUMLASTEN}; mit g = 10 m/s²",
        stellen=0,
    ),
    # -- Abgeleitete Kennwerte ---------------------------------------------
    KennwertVorlage(
        kurzname="eps_t_0_d",
        symbol=r"\varepsilon_{t,0,d}",
        einheit=PROMILLE,
        beschreibung="Dehnung beim Zugbruch in Faserrichtung",
        referenz="SIA 265:2012, 3.1.2.1",
        stellen=2,
        eingaben=("f_t_0_d", "E_0_mean"),
        vorlage_latex=r"\frac{@f_t_0_d}{@E_0_mean}",
        funktion=lambda f_t_0_d, E_0_mean: f_t_0_d / E_0_mean,
    ),
    KennwertVorlage(
        kurzname="eps_c_0_d",
        symbol=r"\varepsilon_{c,0,d}",
        einheit=PROMILLE,
        beschreibung="Stauchung an der Druckgrenze in Faserrichtung",
        referenz="SIA 265:2012, 3.1.2.1",
        stellen=2,
        eingaben=("f_c_0_d", "E_0_mean"),
        vorlage_latex=r"\frac{@f_c_0_d}{@E_0_mean}",
        funktion=lambda f_c_0_d, E_0_mean: f_c_0_d / E_0_mean,
    ),
    KennwertVorlage(
        kurzname="eps_cu",
        symbol=r"\varepsilon_{cu}",
        einheit=PROMILLE,
        beschreibung="Grenzstauchung des Holzes, elastisch-plastisch",
        referenz="SIA 265:2012, 3.1.2.2; die Grenze nach Vorgabe",
        stellen=2,
        eingaben=("eps_c_0_d",),
        vorlage_latex=rf"{STAUCHBARKEIT:g} \cdot @eps_c_0_d",
        funktion=lambda eps_c_0_d: STAUCHBARKEIT * eps_c_0_d,
        begruendung=("Nach Vorgabe, nicht nachgeschlagen: die Norm lässt den Druck fliessen, "
                     "wo das Bauteil plastisch stauchen kann, und nennt keine Grenze. Die Linie "
                     f"endet bei {STAUCHBARKEIT:g} Stauchungen an der Druckgrenze."),
    ),
)


# ===========================================================================
# Erzeugung
# ===========================================================================


def holz(
    sorte: str = ERSTES_HOLZ,
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
    symbol_index: str = "",
) -> Baustoff:
    """
    Erzeugt ein Holz aus den Sortentabellen.

    :param sorte: Bezeichnung aus :data:`HOLZSORTEN`, z.B. ``'GL24h'``.
    :param abweichungen: Zahlenwerte, die von der Tabelle abweichen.
    """
    if sorte not in HOLZSORTEN:
        raise ValueError(f"Unbekannte Holzsorte '{sorte}'. Verfügbar: {', '.join(HOLZSORTEN)}.")
    s = HOLZSORTEN[sorte]
    werte: Dict[str, Groesse] = {kurz: Groesse(getattr(s, kurz), N_PRO_MM2) for kurz in _SPALTEN}
    werte["rho_k"] = Groesse(s.rho_k, KG_PRO_M3)
    werte["gamma_M_eta_M"] = Groesse(s.art.gamma_M_eta_M, EINHEITSLOS)
    werte["rho_mean"] = Groesse(s.art.dichte, KG_PRO_M3)
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.HOLZ,
        name=name or sorte,
        sorte=sorte,
        vorlagen=HOLZ_VORLAGEN,
        werte=werte,
        praefix=praefix,
        symbol_index=symbol_index,
    )
