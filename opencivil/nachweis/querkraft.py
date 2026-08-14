"""
opencivil/nachweis/querkraft.py -- Querkraftnachweis ohne Querkraftbewehrung.

VERANTWORTUNG:
Bestimmt den Querkraftwiderstand einer Platte je Tragrichtung und prueft ihn
gegen die angegebenen Querkraefte.

ANSATZ::

    v_Rd = k_d * tau_cd * d_v

    k_d   = 1 / (1 + eps_v * d * k_g)
    k_g   = 48 / (16 + D_max * min[1.0; (60/f_ck)^2])
    m_Dd  = |N_Ed| * h / 6                      Dekompressionsmoment
    eps_v = f_yd * (m_Ed - m_Dd) / (E_s * (m_Rd(N_Ed) - m_Dd))

    d_v = d - Einlagenhoehe,  falls  h/6 < Einlagenhoehe < d
    d_v = d                   sonst

``d`` ist die statische Hoehe der *gezogenen* Bewehrung und haengt damit vom
Vorzeichen des Moments ab: bei positivem Moment liegt der Zug unten, bei
negativem oben.

ZUG SCHLIESST DEN NACHWEIS AUS:
Bei einer Normalzugkraft (N_Ed > 0) wird ``v_Rd = 0`` gesetzt. Ohne
Querkraftbewehrung ist auf einen Querkraftwiderstand dann nicht zu zaehlen.

EINHEITEN:
Die Formeln der Norm sind dimensionell inhomogen -- ``d`` und ``D_max`` gehen
in Millimeter ein, ``f_ck`` in N/mm^2. Sie laufen deshalb ueber
:func:`opencivil.core.einheiten.empirisch`, das diese Voraussetzung erzwingt
und im Bericht als Annahme ausweist. ``v_Rd`` ergibt sich in N/mm, also kN/m --
eine Querkraft je Laufmeter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, KN_PRO_M, KNM, MM, N_PRO_MM2, Groesse, empirisch,
)
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.querschnitt.platte import Plattenquerschnitt, Richtung


@dataclass(frozen=True)
class Querkraftfall:
    """Eine zu pruefende Kombination fuer den Querkraftnachweis."""

    name: str
    V_Ed: Groesse
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return "".join(z if z.isalnum() else "_" for z in self.name)


@dataclass
class Querkraftergebnis:
    """Alle Zwischenwerte eines Falls, damit die Herleitung vollstaendig ist."""

    fall: Querkraftfall
    d: float = 0.0
    d_v: float = 0.0
    k_g: float = 0.0
    k_d: float = 0.0
    eps_v: float = 0.0
    m_Dd: float = 0.0
    m_Rd: float = 0.0
    """Momentenwiderstand bei der wirkenden Normalkraft, in Nm."""

    v_Rd: float = 0.0
    """in N/m."""

    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""


class Querkraft(Nachweis):
    """Querkraftwiderstand ohne Querkraftbewehrung, je Tragrichtung."""

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        faelle: Sequence[Querkraftfall],
        richtung: Richtung,
        mn_nachweis,
    ) -> None:
        if not faelle:
            raise ValueError("Der Querkraftnachweis braucht mindestens einen Fall.")
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} liegt "
                f"keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.faelle = list(faelle)
        self.ergebnisse: List[Querkraftergebnis] = []

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.querkraft.{r}"
        self.d_grad: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,V,{r},{f.kennung}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Erfüllungsgrad Querkraft {richtung.beschriftung} – {f.name}",
                referenz="SIA 262:2025, 4.3.3.2",
                stellen=2,
            )
            for f in self.faelle
        }
        self.d_v_rd: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.v_Rd",
                symbol=f"v_{{Rd,{r}}}",
                einheit=KN_PRO_M,
                beschreibung=f"Querkraftwiderstand {richtung.beschriftung} – {f.name}",
                referenz="SIA 262:2025, 4.3.3.2.1",
                stellen=1,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("D_max", querschnitt.id_von("D_max")),
            Eingabebezug("einlagenhoehe", querschnitt.id_von("einlagenhoehe")),
            Eingabebezug("f_ck", querschnitt.beton.id_von("f_ck")),
            Eingabebezug("tau_cd", querschnitt.beton.id_von("tau_cd")),
        ]
        for lage, art, _, as_id, z_id in self.posten:
            bezuege.append(Eingabebezug(f"z_{lage.nummer}{art.kuerzel}", z_id))
        stahl = self.posten[0][0].stahl
        bezuege += [
            Eingabebezug("f_yd", stahl.id_von("f_yd")),
            Eingabebezug("E_s", stahl.id_von("E_s")),
        ]
        # Der Momentenwiderstand bei der wirkenden Normalkraft kommt aus dem
        # M-N-Nachweis -- je Fall einer. Als Eingang statt als mitgegebene Zahl,
        # damit die Abhaengigkeit im Graphen steht und die Rueckverfolgung sie
        # zeigt.
        for f in self.faelle:
            bezuege.append(Eingabebezug(
                f"m_Rd_{f.kennung}", mn_nachweis.d_m_rd[f.name].id))

        super().__init__(
            basis,
            ausgaben=list(self.d_grad.values()) + list(self.d_v_rd.values()),
            bezuege=bezuege,
            titel=f"Querkraftnachweis {richtung.beschriftung} – {querschnitt.name}",
            referenz="SIA 262:2025, 4.3.3.2",
        )

    # -- Rechnen ------------------------------------------------------------

    def _statische_hoehe(self, e: Eingaben, h: float, moment_positiv: bool) -> float:
        """
        Statische Hoehe der gezogenen Bewehrung, in m ab der gedrueckten Kante.

        Bei positivem Moment liegt der Zug unten: gemessen wird von der
        Oberkante zur untersten Lage. Bei negativem Moment umgekehrt.
        """
        tiefen = [e.g(f"z_{l.nummer}{a.kuerzel}").si for l, a, _, _, _ in self.posten]
        return max(tiefen) if moment_positiv else h - min(tiefen)

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        tau_cd = e.g("tau_cd")
        f_yd = e.g("f_yd").si
        E_s = e.g("E_s").si
        einlage = e.g("einlagenhoehe").si
        m_rd = {f.name: abs(e.g(f"m_Rd_{f.kennung}").si) for f in self.faelle}

        self._protokoll_ansatz(p, e)

        k_g_erg = empirisch(
            lambda D_max, f_ck: 48.0 / (16.0 + D_max * min(1.0, (60.0 / f_ck) ** 2)),
            ergebnis=EINHEITSLOS,
            D_max=(e.g("D_max"), MM),
            f_ck=(e.g("f_ck"), N_PRO_MM2),
        )
        k_g = k_g_erg.wert.si
        p.gleichung(
            r"k_g = \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ "
            r"\left(\frac{60}{f_{ck}}\right)^{2}\right]}"
            rf" = {k_g:.3f}",
            titel="Beiwert der Gesteinskörnung", referenz="SIA 262:2025, 4.3.3.2.1")
        p.annahme(k_g_erg.annahmen_text())

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []
        zeilen: List[List[str]] = []

        for fall in self.faelle:
            erg = self._einen_fall(fall, h, tau_cd, f_yd, E_s, einlage, k_g,
                                   m_rd[fall.name])
            self.ergebnisse.append(erg)

            ergebnis[self.d_v_rd[fall.name].id] = Groesse.aus_si(erg.v_Rd, KN_PRO_M)
            ergebnis[self.d_grad[fall.name].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)

            urteile.append(NachweisUrteil(
                name=f"Querkraft {self.richtung.value} – {fall.name}",
                erfuellt=erg.erfuellt,
                erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
                begruendung=erg.begruendung,
                einwirkung=WertDef(
                    id=f"{self.id}.{fall.kennung}.V_Ed", symbol=f"V_{{Ed,{self.richtung.value}}}",
                    einheit=KN_PRO_M, beschreibung="Einwirkung", stellen=1,
                ).belegen(fall.V_Ed.als(KN_PRO_M) if fall.V_Ed.dimension == KN_PRO_M.dimension
                          else Groesse.aus_si(fall.V_Ed.si, KN_PRO_M)),
                widerstand=self.d_v_rd[fall.name].belegen(
                    Groesse.aus_si(erg.v_Rd, KN_PRO_M)),
            ))

            zeilen.append([
                rf"\text{{{fall.name}}}",
                f"{erg.d * 1e3:.0f}", f"{erg.d_v * 1e3:.0f}",
                f"{erg.eps_v * 1e3:.3f}", f"{erg.k_d:.3f}",
                f"{erg.v_Rd / 1e3:.1f}",
            ])

        p.tabelle(
            kopf=[r"\text{Fall}", r"d\ [\mathrm{mm}]", r"d_v\ [\mathrm{mm}]",
                  r"\varepsilon_v\ [\text{‰}]", r"k_d", r"v_{Rd}\ [\mathrm{kN/m}]"],
            zeilen=zeilen, titel="Querkraftwiderstand je Fall", ausrichtung="lrrrrr")
        return ergebnis, urteile

    def _einen_fall(
        self, fall: Querkraftfall, h: float, tau_cd: Groesse,
        f_yd: float, E_s: float, einlage: float, k_g: float,
        m_Rd: float,
    ) -> Querkraftergebnis:
        erg = Querkraftergebnis(fall=fall)
        M_Ed, N_Ed, V_Ed = fall.M_Ed.si, fall.N_Ed.si, fall.V_Ed.si

        erg.d = self._statische_hoehe_aus(h, M_Ed >= 0)
        erg.d_v = erg.d - einlage if (h / 6.0 < einlage < erg.d) else erg.d

        if N_Ed > 0:
            # Normalzugkraft: ohne Querkraftbewehrung kein Widerstand.
            erg.v_Rd = 0.0
            erg.erfuellungsgrad = 0.0
            erg.erfuellt = False
            erg.begruendung = (
                f"N_Ed = {N_Ed / 1e3:.1f} kN ist eine Zugkraft. Ohne "
                f"Querkraftbewehrung wird v_Rd = 0 gesetzt.")
            return erg

        erg.m_Dd = abs(N_Ed) * h / 6.0
        erg.m_Rd = m_Rd
        zaehler = abs(M_Ed) - erg.m_Dd
        nenner = m_Rd - erg.m_Dd

        if zaehler <= 0.0:
            # Das Moment bleibt unter dem Dekompressionsmoment: der Querschnitt
            # ist ungerissen, eps_v = 0 und k_d damit am groessten.
            erg.eps_v = 0.0
        elif nenner <= 0.0:
            # Der Widerstand liegt nicht ueber dem Dekompressionsmoment -- die
            # Formel gibt dann nichts her. Auf einen Querkraftwiderstand ist
            # hier nicht zu zaehlen; der M-N-Nachweis zeigt das Versagen ohnehin.
            erg.v_Rd = 0.0
            erg.erfuellungsgrad = 0.0
            erg.erfuellt = False
            erg.begruendung = (
                f"m_Rd(N_Ed) = {m_Rd / 1e3:.1f} kNm liegt nicht über dem "
                f"Dekompressionsmoment m_Dd = {erg.m_Dd / 1e3:.1f} kNm. "
                f"Der Querkraftwiderstand ist so nicht bestimmbar.")
            return erg
        else:
            erg.eps_v = f_yd * zaehler / (E_s * nenner)

        # k_d ist empirisch: d geht in Millimeter ein.
        erg.k_d = 1.0 / (1.0 + erg.eps_v * (erg.d * 1e3) * k_g)
        erg.v_Rd = erg.k_d * tau_cd.in_einheit(N_PRO_MM2) * (erg.d_v * 1e3) * 1e3  # N/m

        erg.erfuellungsgrad = float("inf") if V_Ed == 0 else abs(erg.v_Rd) / abs(V_Ed)
        erg.erfuellt = erg.erfuellungsgrad >= 1.0
        erg.begruendung = (
            f"v_Rd = k_d · τ_cd · d_v = {erg.k_d:.3f} · "
            f"{tau_cd.formatiert(2, N_PRO_MM2)} N/mm² · {erg.d_v * 1e3:.0f} mm "
            f"= {erg.v_Rd / 1e3:.1f} kN/m.")
        return erg

    def _statische_hoehe_aus(self, h: float, moment_positiv: bool) -> float:
        tiefen = self._tiefen
        return max(tiefen) if moment_positiv else h - min(tiefen)

    def rechne(self, e: Eingaben, p: Protokoll):
        # Die Lagentiefen werden mehrfach gebraucht; einmal einsammeln.
        self._tiefen = [e.g(f"z_{l.nummer}{a.kuerzel}").si for l, a, _, _, _ in self.posten]
        return super().rechne(e, p)

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.text(
            "Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die "
            "statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und "
            "die Dehnung auf halber Höhe. Bei einer Normalzugkraft wird der "
            "Widerstand zu null gesetzt."
        )
        p.gleichung(
            r"v_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad "
            r"k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.2.1")
        p.gleichung(
            r"m_{Dd} = \frac{|N_{Ed}| \cdot h}{6} \qquad "
            r"\varepsilon_v = \frac{f_{yd} \cdot (m_{Ed} - m_{Dd})}"
            r"{E_s \cdot \left(m_{Rd}(N_{Ed}) - m_{Dd}\right)}",
            titel="Dekompressionsmoment und Dehnung")
