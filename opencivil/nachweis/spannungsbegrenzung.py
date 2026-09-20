"""
opencivil/nachweis/spannungsbegrenzung.py -- Stahlspannung unter häufiger Einwirkung.

VERANTWORTUNG:
Bestimmt je haeufigem Lastfall die Stahlspannung im gerissenen Querschnitt und
haelt sie gegen ``f_yd - 80 MPa`` (SIA 262:2025, Tabelle 17).

WARUM DIE GRENZE SO AUSSIEHT:
Das Ziel ist, das *Fliessen* der Bewehrung unter haeufiger Einwirkung zu
verhindern. Der Abstand von 80 MPa zur Bemessungsfliessgrenze ist der
Sicherheitsabstand dafuer. Er gilt nur bei erhoehter und hoher Anforderung --
bei normaler steht in der Tabelle ein Strich, der Nachweis entfaellt.

WIE DIE SPANNUNG ENTSTEHT:
Ueber :mod:`opencivil.nachweis.querschnittsloeser`: gesucht wird die
Dehnungsebene, die ``M_Ed,haeufig`` und ``N_Ed,haeufig`` im Gleichgewicht
haelt. Der Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem
wirksamen Modul ``E_cm/(1+phi)``. **Nur gezogene Bewehrung zaehlt** -- eine
gedrueckte Lage wuerde den Hebelarm vergroessern und den Nachweis guenstiger
machen, als er ist.

WAS IN DER MITSCHRIFT STEHT:
Das Verfahren in zwei Saetzen, dann die gefundene Ebene und die **Probe**:
mit diesem ``eps_m`` und ``chi`` entstehen genau ``N_Ed`` und ``M_Ed``. Die
Suche selbst steht nicht da -- sie ist kein Rechenschritt, den jemand
nachvollziehen soll.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, N_PRO_MM2, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import mit_index
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, beton_elastisch, stahl_bilinear,
)
from opencivil.nachweis.zustand2 import wertigkeit
from opencivil.querschnitt.platte import Richtung

#: Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.
FLIESSABSTAND = 80e6

#: Anforderungen, bei denen der Nachweis gefuehrt wird. Bei *normal* steht in
#: der Tabelle ein Strich.
GEFORDERT = ("erhoeht", "hoch")


@dataclass(frozen=True)
class Haeufigerfall:
    """Eine Schnittgroessenkombination unter haeufiger Einwirkung."""

    name: str
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return "".join(z if z.isalnum() else "_" for z in self.name)


@dataclass
class Fallergebnis:
    """Was der Nachweis fuer einen Lastfall gefunden hat."""

    fall: Haeufigerfall
    eps_m: float = 0.0
    chi: float = 0.0
    N_int: float = 0.0
    M_int: float = 0.0
    sigma_s: float = 0.0
    """Groesste Zugspannung in der Bewehrung, in Pa."""

    sigma_s_adm: float = 0.0
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    konvergiert: bool = True
    begruendung: str = ""
    hinweis: str = ""


class Spannungsbegrenzung(Nachweis):
    """
    Verhindern des Fliessens unter häufiger Einwirkung, je Tragrichtung.

    Ein Urteil je häufigem Lastfall. Gerechnet wird am gerissenen Querschnitt
    mit dem wirksamen Elastizitätsmodul; gezählt wird nur die gezogene
    Bewehrung.
    """

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        faelle: Sequence[Haeufigerfall],
    ) -> None:
        if not faelle:
            raise ValueError("Ohne häufigen Lastfall gibt es nichts zu begrenzen.")
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                f"liegt keine Bewehrung.")

        self.querschnitt = querschnitt
        self.richtung = richtung
        self.faelle = list(faelle)
        self.ergebnisse: List[Fallergebnis] = []

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.spannung.{r}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,\sigma,{r},{f.kennung}}}",
                einheit=EINHEITSLOS,
                beschreibung=(f"Erfüllungsgrad Stahlspannung "
                              f"{richtung.beschriftung} – {f.name}"),
                referenz="SIA 262:2025, Tabelle 17",
                stellen=2,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(richtung)),
            Eingabebezug("E_cm", querschnitt.beton.id_von("E_cm")),
            Eingabebezug("phi", querschnitt.id_von("kriechzahl")),
        ]
        for lage, art, _, as_id, z_id in self.posten:
            marke = f"{lage.nummer}{art.kuerzel}"
            bezuege += [
                Eingabebezug(f"a_s_{marke}", as_id),
                Eingabebezug(f"z_{marke}", z_id),
            ]
        stahl = self.posten[0][0].stahl
        bezuege += [
            Eingabebezug("E_s", stahl.id_von("E_s")),
            Eingabebezug("f_yd", stahl.id_von("f_yd")),
        ]
        self.s_E_cm = mit_index("E_{cm}", querschnitt.beton.symbol_index)
        self.s_f_yd = mit_index("f_{yd}", stahl.symbol_index)

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=(f"Stahlspannung unter häufiger Einwirkung "
                   f"{richtung.beschriftung} – {querschnitt.name}"),
            referenz="SIA 262:2025, Tabelle 17",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        E_cm = e.g("E_cm").si
        phi = e.g("phi").si
        E_s = e.g("E_s").si
        f_yd = e.g("f_yd").si
        sigma_adm = f_yd - FLIESSABSTAND

        lagen = [Stahllage(a_s=e.g(f"a_s_{l.nummer}{a.kuerzel}").si,
                           z=e.g(f"z_{l.nummer}{a.kuerzel}").si,
                           nummer=l.nummer)
                 for l, a, _, _, _ in self.posten]
        n = wertigkeit(E_s=E_s, E_cm=E_cm, phi=phi)
        E_c_eff = E_cm / (1.0 + phi)

        loeser = Querschnittsloeser(
            h=h, b=b, lagen=lagen,
            beton=beton_elastisch(E_c=E_c_eff),
            # Im Gebrauchszustand fliesst nichts; die Grenze steht nur da,
            # damit das Gesetz im Suchfenster monoton bleibt.
            stahl=stahl_bilinear(E_s=E_s, f_sd=f_yd))

        self._protokoll_ansatz(p, E_cm, phi, n, E_c_eff, f_yd, sigma_adm)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            erg = self._einen_fall(loeser, fall, sigma_adm)
            self.ergebnisse.append(erg)
            self._protokoll_fall(p, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
            urteile.append(self._urteil(erg))

        return ergebnis, urteile

    def _einen_fall(self, loeser: Querschnittsloeser, fall: Haeufigerfall,
                    sigma_adm: float) -> Fallergebnis:
        erg = Fallergebnis(fall=fall, sigma_s_adm=sigma_adm)
        ebene = loeser.loese(N_Ed=fall.N_Ed.si, M_Ed=fall.M_Ed.si)
        erg.konvergiert = ebene.konvergiert
        if not ebene.konvergiert:
            erg.begruendung = erg.hinweis = (
                f"Für {fall.name} lässt sich keine Dehnungsebene finden, die "
                f"M = {fall.M_Ed.formatiert(1, KNM)} kNm und "
                f"N = {fall.N_Ed.formatiert(1, KN)} kN im Gleichgewicht hält. "
                f"Der Querschnitt kann diese Kombination nicht aufnehmen.")
            return erg

        erg.eps_m, erg.chi = ebene.eps_m, ebene.chi
        erg.N_int, erg.M_int = ebene.N_int, ebene.M_int
        # Nur gezogene Bewehrung: eine gedrueckte Lage hat keine Zugspannung,
        # die zu begrenzen waere.
        zug = [s for s in ebene.sigma_s if s > 0.0]
        erg.sigma_s = max(zug) if zug else 0.0

        erg.erfuellungsgrad = (float("inf") if erg.sigma_s <= 0.0
                               else sigma_adm / erg.sigma_s)
        erg.erfuellt = erg.sigma_s <= sigma_adm
        erg.begruendung = (
            f"Gerissener Querschnitt: ε_m = {erg.eps_m * 1e3:.4f} ‰, "
            f"χ = {erg.chi:.5f} 1/m. Grösste Zugspannung "
            f"σ_s = {erg.sigma_s / 1e6:.0f} N/mm² gegen "
            f"σ_s,adm = {sigma_adm / 1e6:.0f} N/mm².")
        return erg

    def _urteil(self, erg: Fallergebnis) -> NachweisUrteil:
        r = self.richtung.value
        einwirkung = WertDef(
            id=f"{self.id}.{erg.fall.kennung}.sigma_s",
            symbol=rf"\sigma_{{s,{r}}}",
            einheit=N_PRO_MM2, beschreibung="Einwirkung", stellen=0,
        ).belegen(Groesse.aus_si(erg.sigma_s, N_PRO_MM2))
        widerstand = WertDef(
            id=f"{self.id}.sigma_s_adm",
            symbol=r"\sigma_{s,adm}",
            einheit=N_PRO_MM2, beschreibung="Widerstand", stellen=0,
        ).belegen(Groesse.aus_si(erg.sigma_s_adm, N_PRO_MM2))
        return NachweisUrteil(
            name=f"Stahlspannung {r} – {erg.fall.name}",
            art="σ_s",
            langname=f"Stahlspannung ({r})",
            fall=erg.fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if erg.konvergiert else None,
            widerstand=widerstand if erg.konvergiert else None,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, E_cm: float, phi: float,
                          n: float, E_c_eff: float, f_yd: float,
                          sigma_adm: float) -> None:
        p.titel(f"Stahlspannung unter häufiger Einwirkung – "
                f"{self.richtung.beschriftung}")
        p.text(
            "Unter häufiger Einwirkung darf die Bewehrung nicht fliessen. "
            "Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen "
            "Zug auf, im Druck rechnet er linear mit dem wirksamen Modul. "
            "Gezählt wird nur gezogene Bewehrung."
        )
        p.gleichung(
            rf"E_{{c,eff}} = \frac{{{self.s_E_cm}}}{{1 + \varphi}}"
            rf" = \frac{{{E_cm / 1e6:.0f}}}{{1 + {phi:.2f}}}"
            rf" = {E_c_eff / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \qquad n = {n:.2f}",
            titel="Wirksamer Elastizitätsmodul")
        p.gleichung(
            rf"\sigma_{{s,adm}} = {self.s_f_yd} - {FLIESSABSTAND / 1e6:.0f}"
            rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {f_yd / 1e6:.0f} - {FLIESSABSTAND / 1e6:.0f}"
            rf" = {sigma_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Zulässige Stahlspannung",
            referenz="SIA 262:2025, Tabelle 17")
        p.text(
            "Die Dehnungsebene wird gesucht, nicht hergeleitet: zwei "
            "Unbekannte (ε_m und χ) gegen zwei Gleichgewichtsbedingungen, "
            "gelöst durch fortgesetzte Halbierung. Nachgewiesen wird deshalb "
            "nicht der Weg, sondern das Ergebnis – dass die gefundene Ebene "
            "genau die angegebenen Schnittgrössen erzeugt."
        )

    def _protokoll_fall(self, p: Protokoll, erg: Fallergebnis) -> None:
        fall = erg.fall
        p.titel(f"Häufiger Lastfall – {fall.name}", ebene=3)
        p.gleichung(
            rf"M_{{Ed,häufig}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed,häufig}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

        if not erg.konvergiert:
            p.text(erg.begruendung)
            return

        p.gleichung(
            rf"\varepsilon_m = {erg.eps_m * 1e3:.4f}\,\text{{‰}} \qquad "
            rf"\chi = {erg.chi:.5f}\,\mathrm{{m}}^{{-1}}"
            rf" \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot "
            rf"\left(z - \tfrac{{h}}{{2}}\right)",
            titel="Gefundene Dehnungsebene")
        p.gleichung(
            rf"N_{{int}} = {erg.N_int / 1e3:.1f}\,\mathrm{{kN}} \;\checkmark"
            rf" \qquad M_{{int}} = {erg.M_int / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \;\checkmark",
            titel="Probe: die Ebene erzeugt die Einwirkung")

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        vergleich = r"\le" if erg.erfuellt else ">"
        p.gleichung(
            rf"\sigma_s = {erg.sigma_s / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \quad {vergleich} \quad \sigma_{{s,adm}} = "
            rf"{erg.sigma_s_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Grösste Zugspannung in der Bewehrung")
        grad = ("\\infty" if math.isinf(erg.erfuellungsgrad)
                else f"{erg.erfuellungsgrad:.2f}")
        p.gleichung(
            rf"\alpha_{{eff,\sigma}} = "
            rf"\frac{{\sigma_{{s,adm}}}}{{\sigma_s}} = {grad}",
            titel="Erfüllungsgrad")
