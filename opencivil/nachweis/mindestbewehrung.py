"""
opencivil/nachweis/mindestbewehrung.py -- Nachweise gegen sprödes Versagen.

VERANTWORTUNG:
Prueft, ob die Bewehrung uebernehmen kann, was der Beton beim Reissen abgibt --
ohne dabei ueber die zulaessige Stahlspannung zu kommen.

WARUM:
Ein unbewehrter oder zu schwach bewehrter Querschnitt reisst und versagt im
selben Augenblick. Genau das soll nicht passieren: die Bewehrung muss die
Risskraft aufnehmen koennen, damit sich das Versagen ankuendigt.

RISSNORMALKRAFT (Normalkraft-Zwaengung)::

    h_eff    = min(500 mm; h)   falls begrenzt, sonst h
    k_t      = 1 / (1 + 0.5 * h_eff)          h_eff in Metern
    f_ct,eff = k_t * f_ctm
    N_Riss   = h_eff/2 * b * f_ct,eff
    N_s,adm  = A_s * sigma_s,adm  >=  N_Riss

``h_eff/2`` ist die gezogene Haelfte des Querschnitts. ``k_t`` traegt dem
Rechnung, dass eine dicke Platte nicht ueber ihre ganze Hoehe gleichzeitig
reisst.

ZULAESSIGE STAHLSPANNUNG:
Bei *normaler* Anforderung gilt ``f_yk`` -- die Bewehrung darf fliessen, sie
muss nur da sein. Bei *erhoehter* und *hoher* Anforderung begrenzt zusaetzlich
die nominelle Rissbreite::

    sigma_s,adm = min( sqrt(9 * E_s * f_ctm * w_nom / durchmesser); f_yk )

Gerechnet wird mit ``f_yk`` und nicht ``f_yd``: nachgewiesen wird nicht die
Tragfaehigkeit, sondern dass die Bewehrung den Riss ueberlebt.

EINHEITEN:
Alles in SI-Basis. Die Wurzelformel ist dimensionell stimmig -- ``E_s * f_ctm``
gibt Pa^2, ``w_nom/durchmesser`` ist dimensionslos, die Wurzel also Pa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import mit_index
from opencivil.nachweis.sproedes_versagen import (
    MOMENTENTEILER, Rissgroessen as Momentgroessen, rissmoment,
)
from opencivil.nachweis.zustand2 import gerissen, wertigkeit
from opencivil.querschnitt.platte import Bewehrungslage, Richtung, posten_index

#: Nominelle Rissbreite je Anforderung, in m. ``None`` heisst: keine Grenze aus
#: der Rissbreite, dann gilt allein ``f_yk``.
RISSBREITE: Dict[str, Optional[float]] = {
    "normal": None,
    "erhoeht": 0.5e-3,
    "hoch": 0.2e-3,
}

#: Groesste Plattendicke, fuer die eine Zwaengung angesetzt wird, in m.
#: Gilt nur, wenn die Begrenzung eingeschaltet ist.
DICKENGRENZE = 0.500



@dataclass(frozen=True)
class Rissgroessen:
    """Was allein von der Platte abhaengt, nicht von der einzelnen Lage."""

    h_eff: float
    """Rissaktive Plattendicke in m."""

    k_t: float
    f_ct_eff: float
    N_Riss: float
    """Risskraft in N, bezogen auf die betrachtete Breite."""


def rissnormalkraft(*, h: float, b: float, f_ctm: float,
                    begrenzt: bool) -> Rissgroessen:
    """
    Die Kraft, die der Beton beim Reissen abgibt.

    Alles in SI-Basis; ``h`` und ``b`` in m, ``f_ctm`` in Pa, Rueckgabe in N.
    """
    h_eff = min(DICKENGRENZE, h) if begrenzt else h
    k_t = 1.0 / (1.0 + 0.5 * h_eff)
    f_ct_eff = k_t * f_ctm
    return Rissgroessen(h_eff=h_eff, k_t=k_t, f_ct_eff=f_ct_eff,
                        N_Riss=h_eff / 2.0 * b * f_ct_eff)


def zulaessige_stahlspannung(
    *, anforderung: str, f_yk: float, E_s: float, f_ctm: float,
    durchmesser: float,
) -> float:
    """
    Die Spannung, bis zu der die Bewehrung beansprucht werden darf.

    Bei normaler Anforderung ``f_yk``. Sonst zusaetzlich begrenzt durch die
    nominelle Rissbreite -- je duenner der Stab, desto mehr darf er tragen,
    weil sich der Riss auf mehr Staebe verteilt.

    Alles in SI-Basis. Ohne Bewehrung (``durchmesser = 0``) faellt die
    Begrenzung weg; die Flaeche ist dann ohnehin null und der Nachweis
    scheitert an ihr.
    """
    w_nom = RISSBREITE.get(anforderung)
    if w_nom is None or durchmesser <= 0.0:
        return f_yk
    return min(math.sqrt(9.0 * E_s * f_ctm * w_nom / durchmesser), f_yk)


@dataclass
class Lagenergebnis:
    """Was der Nachweis fuer eine Lage gefunden hat."""

    lage: Bewehrungslage
    a_s: float = 0.0
    durchmesser: float = 0.0
    """Der groesste Stabdurchmesser der Lage, in m -- er bestimmt die Rissbreite."""

    f_yk: float = 0.0
    E_s: float = 0.0
    """Die Kennwerte des Stahls dieser Lage -- fuer die Mitschrift."""

    sigma_s_adm: float = 0.0
    N_s_adm: float = 0.0
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""

    @property
    def machbar(self) -> bool:
        return self.a_s > 0.0


class Rissnormalkraft(Nachweis):
    """
    Sprödes Versagen unter Normalkraft-Zwängung, je Tragrichtung.

    Zwei Urteile: die untere und die obere Lage dieser Richtung. Beide müssen
    die Risskraft aufnehmen können -- ein Zwang kennt keine Zugseite, er
    beansprucht den Querschnitt über die ganze Höhe.
    """

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        *,
        anforderung: str,
        begrenzt: bool,
    ) -> None:
        if anforderung not in RISSBREITE:
            raise ValueError(
                f"Unbekannte Rissanforderung '{anforderung}'. Möglich sind: "
                f"{', '.join(RISSBREITE)}.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.anforderung = anforderung
        self.begrenzt = begrenzt
        self.ergebnisse: List[Lagenergebnis] = []
        self.groessen: Optional[Rissgroessen] = None

        # Genau zwei Lagen je Richtung -- auch die leeren, denn gerade sie
        # fallen durch und sollen es sichtbar tun.
        self.lagen = [l for l in querschnitt.lagen if l.richtung is richtung]
        self.posten_je_lage: Dict[int, List[Tuple]] = {
            l.nummer: [e for e in querschnitt.posten_ids if e[0].nummer == l.nummer]
            for l in self.lagen
        }

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.rissnormalkraft.{r}"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: WertDef(
                id=f"{basis}.lage{l.nummer}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,NR,{l.nummer},{r}}}",
                einheit=EINHEITSLOS,
                beschreibung=(f"Erfüllungsgrad Rissnormalkraft – "
                              f"{l.nummer}. Lage {r}"),
                referenz="SIA 262:2025, 4.4.2",
                stellen=2,
            )
            for l in self.lagen
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_von("b")),
            Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
        ]
        for nummer, eintraege in self.posten_je_lage.items():
            for lage, art, _, as_id, _ in eintraege:
                marke = f"{nummer}{art.kuerzel}"
                bezuege += [
                    Eingabebezug(f"a_s_{marke}", as_id),
                    Eingabebezug(f"phi_{marke}",
                                 querschnitt.id_von(f"lage.{marke}.phi")),
                ]
        for stahl in {l.stahl.id: l.stahl for l in self.lagen if l.stahl}.values():
            kurz = _kennung(stahl.id)
            bezuege += [
                Eingabebezug(f"f_yk__{kurz}", stahl.id_von("f_yk")),
                Eingabebezug(f"E_s__{kurz}", stahl.id_von("E_s")),
            ]

        self.s_f_ctm = mit_index("f_{ctm}", querschnitt.beton.symbol_index)

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=(f"Sprödes Versagen unter Zwängung {richtung.beschriftung} – "
                   f"{querschnitt.name}"),
            referenz="SIA 262:2025, 4.4.2",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        f_ctm = e.g("f_ctm").si

        self.groessen = rissnormalkraft(h=h, b=b, f_ctm=f_ctm,
                                        begrenzt=self.begrenzt)
        self._protokoll_ansatz(p, h, b, f_ctm)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for lage in self.lagen:
            erg = self._eine_lage(e, lage, f_ctm=f_ctm)
            self.ergebnisse.append(erg)
            self._protokoll_lage(p, erg, f_ctm)
            ergebnis[self.d_ausnutzung[lage.nummer].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
            urteile.append(self._urteil(erg))

        return ergebnis, urteile

    def _eine_lage(self, e: Eingaben, lage: Bewehrungslage, *,
                   f_ctm: float) -> Lagenergebnis:
        erg = Lagenergebnis(lage=lage)
        eintraege = self.posten_je_lage[lage.nummer]
        marken = [f"{lage.nummer}{art.kuerzel}" for _, art, _, _, _ in eintraege]

        erg.a_s = sum(e.g(f"a_s_{m}").si for m in marken)
        if erg.a_s <= 0.0:
            erg.begruendung = erg.hinweis = (
                f"Nachweis nicht machbar, weil die {lage.nummer}. Lage nicht "
                f"definiert ist. Ohne Bewehrung kann die Risskraft niemand "
                f"übernehmen – gegen sprödes Versagen ist hier nichts vorhanden.")
            return erg

        # Der dickste Stab bestimmt die Rissbreite: er verteilt den Riss auf
        # die wenigsten Stäbe und bekommt damit die grösste Spannung.
        erg.durchmesser = max(e.g(f"phi_{m}").si for m in marken)
        kurz = _kennung(lage.stahl.id)
        erg.f_yk = e.g(f"f_yk__{kurz}").si
        erg.E_s = e.g(f"E_s__{kurz}").si
        erg.sigma_s_adm = zulaessige_stahlspannung(
            anforderung=self.anforderung,
            f_yk=erg.f_yk, E_s=erg.E_s, f_ctm=f_ctm,
            durchmesser=erg.durchmesser)
        erg.N_s_adm = erg.a_s * erg.sigma_s_adm

        N_Riss = self.groessen.N_Riss
        erg.erfuellungsgrad = (float("inf") if N_Riss == 0
                               else erg.N_s_adm / N_Riss)
        erg.erfuellt = erg.N_s_adm >= N_Riss
        erg.begruendung = (
            f"A_s = {erg.a_s * 1e6:.0f} mm² bei σ_s,adm = "
            f"{erg.sigma_s_adm / 1e6:.0f} N/mm² ergibt "
            f"N_s,adm = {erg.N_s_adm / 1e3:.1f} kN gegen "
            f"N_Riss = {N_Riss / 1e3:.1f} kN.")
        return erg

    def _urteil(self, erg: Lagenergebnis) -> NachweisUrteil:
        nummer = erg.lage.nummer
        r = self.richtung.value
        einwirkung = WertDef(
            id=f"{self.id}.N_Riss",
            symbol=r"N_{Riss}",
            einheit=KN, beschreibung="Einwirkung", stellen=1,
        ).belegen(Groesse.aus_si(self.groessen.N_Riss, KN))
        widerstand = WertDef(
            id=f"{self.id}.lage{nummer}.N_s_adm",
            symbol=rf"N_{{s,adm,{nummer},{r}}}",
            einheit=KN, beschreibung="Widerstand", stellen=1,
        ).belegen(Groesse.aus_si(erg.N_s_adm, KN))
        return NachweisUrteil(
            name=f"Rissnormalkraft {r} – {nummer}. Lage",
            art="N_Riss",
            fall=f"{nummer}. Lage {r}",
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if erg.machbar else None,
            widerstand=widerstand if erg.machbar else None,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, h: float, b: float,
                          f_ctm: float) -> None:
        g = self.groessen
        p.titel(f"Sprödes Versagen unter Zwängung – {self.richtung.beschriftung}")
        p.text(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Die Bewehrung muss die Kraft übernehmen können, die "
            "der Beton beim Reissen abgibt – erst dann kündigt sich das "
            "Versagen an."
        )

        if self.begrenzt:
            p.gleichung(
                rf"h_{{eff}} = \min\left[{DICKENGRENZE * 1e3:.0f}\,\mathrm{{mm}};\ "
                rf"h\right] = \min\left[{DICKENGRENZE * 1e3:.0f};\ {h * 1e3:.0f}"
                rf"\right] = {g.h_eff * 1e3:.0f}\,\mathrm{{mm}}",
                titel="Rissaktive Plattendicke")
        else:
            p.gleichung(
                rf"h_{{eff}} = h = {g.h_eff * 1e3:.0f}\,\mathrm{{mm}}",
                titel="Rissaktive Plattendicke")

        p.gleichung(
            r"k_t = \frac{1}{1 + 0.5 \cdot h_{eff}}"
            rf" = \frac{{1}}{{1 + 0.5 \cdot {g.h_eff:.3f}}} = {g.k_t:.3f}",
            titel="Beiwert für die Plattendicke",
            referenz="SIA 262:2025, 4.4.2")
        p.gleichung(
            rf"f_{{ct,eff}} = k_t \cdot {self.s_f_ctm} = {g.k_t:.3f} \cdot "
            rf"{f_ctm / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {g.f_ct_eff / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Wirksame Zugfestigkeit")
        p.gleichung(
            r"N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff}"
            rf" = \frac{{{g.h_eff * 1e3:.0f}}}{{2}} \cdot {b * 1e3:.0f} \cdot "
            rf"{g.f_ct_eff / 1e6:.2f}"
            rf" = {g.N_Riss / 1e3:.1f}\,\mathrm{{kN}}",
            titel="Risskraft der gezogenen Querschnittshälfte")

    def _protokoll_lage(self, p: Protokoll, erg: Lagenergebnis,
                        f_ctm: float) -> None:
        nummer = erg.lage.nummer
        r = self.richtung.value
        p.titel(f"Rissnormalkraft – {nummer}. Lage {r}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        index = self._index(erg)
        s_a_s = f"A_{{s,{index}}}" if index else "A_s"
        s_sigma = rf"\sigma_{{s,adm,{index}}}" if index else r"\sigma_{s,adm}"
        s_f_yk = mit_index("f_{yk}", erg.lage.stahl.symbol_index)
        w_nom = RISSBREITE[self.anforderung]

        if w_nom is None:
            p.gleichung(
                rf"{s_sigma} = {s_f_yk} = {erg.sigma_s_adm / 1e6:.0f}"
                rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
                titel="Zulässige Stahlspannung (normale Anforderung)")
        else:
            p.gleichung(
                rf"{s_sigma} = \min\left[\sqrt{{\frac{{9 \cdot E_s \cdot "
                rf"{self.s_f_ctm} \cdot w_{{nom}}}}{{\varnothing_{{{index}}}}}}};\ "
                rf"{s_f_yk}\right]"
                "\n= "
                rf"\min\left[\sqrt{{\frac{{9 \cdot {erg.E_s / 1e6:.0f} \cdot "
                rf"{f_ctm / 1e6:.2f} \cdot {w_nom * 1e3:.1f}}}"
                rf"{{{erg.durchmesser * 1e3:.0f}}}}};\ "
                rf"{erg.f_yk / 1e6:.0f}\right]"
                rf" = {erg.sigma_s_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
                titel=(f"Zulässige Stahlspannung (Rissbreite "
                       f"w_nom = {w_nom * 1e3:.1f} mm)"),
                referenz="SIA 262:2025, 4.4.2")

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        vergleich = r"\ge" if erg.erfuellt else "<"
        p.gleichung(
            rf"N_{{s,adm,{index}}} = {s_a_s} \cdot {s_sigma}"
            rf" = {erg.a_s * 1e6:.0f}\,\mathrm{{mm}}^{{2}} \cdot "
            rf"{erg.sigma_s_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {erg.N_s_adm / 1e3:.1f}\,\mathrm{{kN}}"
            rf" \quad {vergleich} \quad N_{{Riss}} = "
            rf"{self.groessen.N_Riss / 1e3:.1f}\,\mathrm{{kN}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Aufnehmbare Risskraft")

        grad = ("\\infty" if math.isinf(erg.erfuellungsgrad)
                else f"{erg.erfuellungsgrad:.2f}")
        p.gleichung(
            rf"\alpha_{{eff,NR,{index}}} = \frac{{N_{{s,adm,{index}}}}}"
            rf"{{N_{{Riss}}}} = \frac{{{erg.N_s_adm / 1e3:.1f}}}"
            rf"{{{self.groessen.N_Riss / 1e3:.1f}}} = {grad}",
            titel="Erfüllungsgrad")

    def _index(self, erg: Lagenergebnis) -> str:
        """Der Symbolindex der Lage -- ``1,x`` statt ``1,x,g``."""
        eintraege = self.posten_je_lage[erg.lage.nummer]
        if not eintraege:
            return ""
        lage, art, *_ = eintraege[0]
        if len(eintraege) == 1:
            return posten_index(lage, art)
        return f"{lage.nummer},{lage.richtung.value}"


def _kennung(text: str) -> str:
    return "".join(z if z.isalnum() else "_" for z in text)


# ===========================================================================
# Rissmoment
# ===========================================================================


@dataclass
class Momentlagenergebnis:
    """Was der Nachweis gegen das Rissmoment fuer eine Lage gefunden hat."""

    lage: Bewehrungslage
    a_s: float = 0.0
    z_s: float = 0.0
    """Gemeinsamer Schwerpunkt der Lage ab Oberkante, in m."""

    d: float = 0.0
    """Statische Hoehe ab der gedrueckten Randfaser, in m."""

    durchmesser: float = 0.0
    f_yk: float = 0.0
    E_s: float = 0.0
    sigma_s_adm: float = 0.0

    n: float = 0.0
    x: float = 0.0
    hebelarm: float = 0.0
    M_s_adm: float = 0.0

    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""

    @property
    def machbar(self) -> bool:
        return self.a_s > 0.0


class ZwaengungBiegung(Nachweis):
    """
    Zwängung auf Biegung, je gewählter Lage.

    Zwei Urteile: die untere Lage (positives Moment) und die obere (negatives).
    Beim Reissen gibt der Beton sein Moment ab; die Bewehrung muss es
    übernehmen können, ohne über ``sigma_s,adm`` zu kommen.

    Der aufnehmbare Moment wird am **gerissenen** Querschnitt bestimmt --
    unmittelbar nach dem Riss ist der Querschnitt genau dort, und die
    Spannungen sind Gebrauchsspannungen, also elastisch. Eine plastische
    Druckzone gibt es in diesem Augenblick nicht.
    """

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        lagen: Sequence[int],
        *,
        anforderung: str,
        kriechzahl: float,
    ) -> None:
        if anforderung not in RISSBREITE:
            raise ValueError(
                f"Unbekannte Rissanforderung '{anforderung}'. Möglich sind: "
                f"{', '.join(RISSBREITE)}.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.anforderung = anforderung
        self.kriechzahl = kriechzahl
        self.ergebnisse: List[Momentlagenergebnis] = []
        self.groessen: Optional[Momentgroessen] = None

        gewaehlt = sorted(set(lagen))
        self.lagen = [l for l in querschnitt.lagen
                      if l.richtung is richtung and l.nummer in gewaehlt]
        if not self.lagen:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in "
                f"{richtung.beschriftung} ist keine der gewählten Lagen vorhanden.")
        self.posten_je_lage: Dict[int, List[Tuple]] = {
            l.nummer: [e for e in querschnitt.posten_ids if e[0].nummer == l.nummer]
            for l in self.lagen
        }

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.zwang_biegung.{r}"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: WertDef(
                id=f"{basis}.lage{l.nummer}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,ZB,{l.nummer},{r}}}",
                einheit=EINHEITSLOS,
                beschreibung=(f"Erfüllungsgrad Zwängung auf Biegung – "
                              f"{l.nummer}. Lage {r}"),
                referenz="SIA 262:2025, 4.4.2",
                stellen=2,
            )
            for l in self.lagen
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_von("b")),
            Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
            Eingabebezug("E_cm", querschnitt.beton.id_von("E_cm")),
            Eingabebezug("phi", querschnitt.id_von("kriechzahl")),
        ]
        for nummer, eintraege in self.posten_je_lage.items():
            for lage, art, _, as_id, z_id in eintraege:
                marke = f"{nummer}{art.kuerzel}"
                bezuege += [
                    Eingabebezug(f"a_s_{marke}", as_id),
                    Eingabebezug(f"z_{marke}", z_id),
                    Eingabebezug(f"phi_{marke}",
                                 querschnitt.id_von(f"lage.{marke}.phi")),
                ]
        for stahl in {l.stahl.id: l.stahl for l in self.lagen if l.stahl}.values():
            kurz = _kennung(stahl.id)
            bezuege += [
                Eingabebezug(f"f_yk__{kurz}", stahl.id_von("f_yk")),
                Eingabebezug(f"E_s__{kurz}", stahl.id_von("E_s")),
            ]

        self.s_f_ctm = mit_index("f_{ctm}", querschnitt.beton.symbol_index)
        self.s_E_cm = mit_index("E_{cm}", querschnitt.beton.symbol_index)

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=(f"Zwängung auf Biegung {richtung.beschriftung} – "
                   f"{querschnitt.name}"),
            referenz="SIA 262:2025, 4.4.2",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        f_ctm = e.g("f_ctm").si
        E_cm = e.g("E_cm").si
        phi = e.g("phi").si

        self.groessen = rissmoment(h=h, b=b, f_ctm=f_ctm)
        E_s = _erster_E_s(e, self.lagen)
        n = wertigkeit(E_s=E_s, E_cm=E_cm, phi=phi)
        self._protokoll_ansatz(p, h, b, f_ctm, E_s=E_s, E_cm=E_cm, phi=phi, n=n)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for lage in self.lagen:
            erg = self._eine_lage(e, lage, h=h, b=b, f_ctm=f_ctm, E_cm=E_cm, phi=phi)
            self.ergebnisse.append(erg)
            self._protokoll_lage(p, erg, b=b, f_ctm=f_ctm)
            ergebnis[self.d_ausnutzung[lage.nummer].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
            urteile.append(self._urteil(erg))

        return ergebnis, urteile

    def _eine_lage(self, e: Eingaben, lage: Bewehrungslage, *, h: float,
                   b: float, f_ctm: float, E_cm: float,
                   phi: float) -> Momentlagenergebnis:
        erg = Momentlagenergebnis(lage=lage)
        eintraege = self.posten_je_lage[lage.nummer]
        marken = [f"{lage.nummer}{art.kuerzel}" for _, art, _, _, _ in eintraege]

        flaechen = [(e.g(f"a_s_{m}").si, e.g(f"z_{m}").si) for m in marken]
        erg.a_s = sum(a for a, _ in flaechen)
        if erg.a_s <= 0.0:
            erg.begruendung = erg.hinweis = (
                f"Nachweis nicht machbar, weil die {lage.nummer}. Lage nicht "
                f"definiert ist. Ohne Bewehrung kann das Rissmoment niemand "
                f"übernehmen – gegen sprödes Versagen ist hier nichts vorhanden.")
            return erg

        erg.z_s = sum(a * z for a, z in flaechen) / erg.a_s
        # Ab der gedrueckten Randfaser: eine untere Lage wird bei positivem
        # Moment gezogen, gedrueckt ist dann oben.
        erg.d = erg.z_s if lage.von_unten else h - erg.z_s
        erg.durchmesser = max(e.g(f"phi_{m}").si for m in marken)

        kurz = _kennung(lage.stahl.id)
        erg.f_yk = e.g(f"f_yk__{kurz}").si
        erg.E_s = e.g(f"E_s__{kurz}").si
        erg.sigma_s_adm = zulaessige_stahlspannung(
            anforderung=self.anforderung,
            f_yk=erg.f_yk, E_s=erg.E_s, f_ctm=f_ctm,
            durchmesser=erg.durchmesser)

        erg.n = wertigkeit(E_s=erg.E_s, E_cm=E_cm, phi=phi)
        riss = gerissen(n=erg.n, a_s=erg.a_s, b=b, d=erg.d)
        erg.x = riss.x
        erg.hebelarm = riss.z
        erg.M_s_adm = erg.sigma_s_adm * erg.a_s * erg.hebelarm

        M_Riss = self.groessen.M_Riss
        erg.erfuellungsgrad = (float("inf") if M_Riss == 0
                               else erg.M_s_adm / M_Riss)
        erg.erfuellt = erg.M_s_adm >= M_Riss
        erg.begruendung = (
            f"Im gerissenen Querschnitt x = {erg.x * 1e3:.1f} mm, "
            f"z = {erg.hebelarm * 1e3:.1f} mm. Mit σ_s,adm = "
            f"{erg.sigma_s_adm / 1e6:.0f} N/mm² ergibt das "
            f"M_s,adm = {erg.M_s_adm / 1e3:.1f} kNm gegen "
            f"M_Riss = {M_Riss / 1e3:.1f} kNm.")
        return erg

    def _urteil(self, erg: Momentlagenergebnis) -> NachweisUrteil:
        nummer = erg.lage.nummer
        r = self.richtung.value
        einwirkung = WertDef(
            id=f"{self.id}.M_Riss",
            symbol=r"M_{Riss}",
            einheit=KNM, beschreibung="Einwirkung", stellen=1,
        ).belegen(Groesse.aus_si(self.groessen.M_Riss, KNM))
        widerstand = WertDef(
            id=f"{self.id}.lage{nummer}.M_s_adm",
            symbol=rf"M_{{s,adm,{nummer},{r}}}",
            einheit=KNM, beschreibung="Widerstand", stellen=1,
        ).belegen(Groesse.aus_si(erg.M_s_adm, KNM))
        return NachweisUrteil(
            name=f"Zwängung Biegung {r} – {nummer}. Lage",
            art="ZB",
            fall=f"{nummer}. Lage {r}",
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if erg.machbar else None,
            widerstand=widerstand if erg.machbar else None,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, h: float, b: float, f_ctm: float,
                          *, E_s: float, E_cm: float, phi: float,
                          n: float) -> None:
        g = self.groessen
        p.titel(f"Zwängung auf Biegung – {self.richtung.beschriftung}")
        p.text(
            "Eine aufgezwungene Krümmung erzeugt beim Reissen ein Moment, das "
            "die Bewehrung übernehmen muss – ohne über die zulässige "
            "Stahlspannung zu kommen. Nicht zu verwechseln mit dem Nachweis "
            "gegen sprödes Versagen: dort steht der Biegewiderstand gegen das "
            "Rissmoment, hier die Stahlspannung gegen ihre Grenze."
        )
        p.gleichung(
            rf"k_t = \frac{{1}}{{1 + 0.5 \cdot h/{MOMENTENTEILER:.0f}}}"
            rf" = \frac{{1}}{{1 + 0.5 \cdot {h:.3f}/{MOMENTENTEILER:.0f}}}"
            rf" = {g.k_t:.3f}",
            titel="Beiwert für die Plattendicke",
            referenz="SIA 262:2025, 4.4.2")
        p.gleichung(
            rf"f_{{ct,eff}} = k_t \cdot {self.s_f_ctm} = {g.k_t:.3f} \cdot "
            rf"{f_ctm / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {g.f_ct_eff / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Wirksame Zugfestigkeit")
        p.gleichung(
            r"M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6}"
            rf" = {g.f_ct_eff / 1e6:.2f} \cdot "
            rf"\frac{{{h * 1e3:.0f}^{{2}} \cdot {b * 1e3:.0f}}}{{6}}"
            rf" = {g.M_Riss / 1e3:.1f}\,\mathrm{{kNm}}",
            titel="Rissmoment des ungerissenen Querschnitts")
        p.text(
            "Das Rissmoment gilt für den ungerissenen Bruttoquerschnitt – den "
            "Zustand vor dem Riss. Der Widerstand dagegen wird am gerissenen "
            "Querschnitt bestimmt, also für den Augenblick danach. Dass zwei "
            "verschiedene Querschnitte auftreten, ist genau die Frage: reicht "
            "die Bewehrung für das, was der Beton abgibt?"
        )
        p.gleichung(
            rf"n = \frac{{E_s}}{{{self.s_E_cm}}} \cdot \left(1 + \varphi\right)"
            rf" = \frac{{{E_s / 1e6:.0f}}}{{{E_cm / 1e6:.0f}}} \cdot "
            rf"\left(1 + {phi:.2f}\right) = {n:.2f}",
            titel="Wertigkeit im gerissenen Zustand")
        p.text(
            "Das Kriechen weicht den Beton auf: E_c,eff = E_cm/(1+φ), und die "
            "Wertigkeit ist E_s/E_c,eff. Ein grösseres φ senkt damit den "
            "Hebelarm und liegt auf der sicheren Seite."
        )

    def _protokoll_lage(self, p: Protokoll, erg: Momentlagenergebnis, *,
                        b: float, f_ctm: float) -> None:
        nummer = erg.lage.nummer
        r = self.richtung.value
        p.titel(f"Zwängung auf Biegung – {nummer}. Lage {r}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        index = self._index(erg)
        s_a_s = f"A_{{s,{index}}}" if index else "A_s"
        s_d = f"d_{{{index}}}" if index else "d"
        s_sigma = rf"\sigma_{{s,adm,{index}}}" if index else r"\sigma_{s,adm}"
        s_f_yk = mit_index("f_{yk}", erg.lage.stahl.symbol_index)
        w_nom = RISSBREITE[self.anforderung]

        seite = "unten" if erg.lage.von_unten else "oben"
        p.gleichung(
            rf"{s_d} = {erg.d * 1e3:.1f}\,\mathrm{{mm}}",
            titel=f"Statische Höhe ab der gedrückten Randfaser ({seite})")

        if w_nom is None:
            p.gleichung(
                rf"{s_sigma} = {s_f_yk} = {erg.sigma_s_adm / 1e6:.0f}"
                rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
                titel="Zulässige Stahlspannung (normale Anforderung)")
        else:
            p.gleichung(
                rf"{s_sigma} = \min\left[\sqrt{{\frac{{9 \cdot E_s \cdot "
                rf"{self.s_f_ctm} \cdot w_{{nom}}}}{{\varnothing_{{{index}}}}}}};\ "
                rf"{s_f_yk}\right]"
                "\n= "
                rf"\min\left[\sqrt{{\frac{{9 \cdot {erg.E_s / 1e6:.0f} \cdot "
                rf"{f_ctm / 1e6:.2f} \cdot {w_nom * 1e3:.1f}}}"
                rf"{{{erg.durchmesser * 1e3:.0f}}}}};\ "
                rf"{erg.f_yk / 1e6:.0f}\right]"
                rf" = {erg.sigma_s_adm / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
                titel=(f"Zulässige Stahlspannung (Rissbreite "
                       f"w_nom = {w_nom * 1e3:.1f} mm)"),
                referenz="SIA 262:2025, 4.4.2")

        p.gleichung(
            rf"\rho = \frac{{n \cdot {s_a_s}}}{{b}} \qquad "
            rf"x = \sqrt{{\rho^{{2}} + 2 \cdot {s_d} \cdot \rho}} - \rho"
            "\n= "
            rf"\sqrt{{{erg.n * erg.a_s / b * 1e3:.2f}^{{2}} + 2 \cdot "
            rf"{erg.d * 1e3:.1f} \cdot {erg.n * erg.a_s / b * 1e3:.2f}}} - "
            rf"{erg.n * erg.a_s / b * 1e3:.2f}"
            rf" = {erg.x * 1e3:.1f}\,\mathrm{{mm}}",
            titel="Nulllinie des gerissenen Querschnitts")
        p.gleichung(
            rf"z = {s_d} - \frac{{x}}{{3}} = {erg.d * 1e3:.1f} - "
            rf"\frac{{{erg.x * 1e3:.1f}}}{{3}} = {erg.hebelarm * 1e3:.1f}"
            rf"\,\mathrm{{mm}}",
            titel="Innerer Hebelarm")
        p.text(
            "Die Betondruckspannung verläuft dreieckig – null in der Nulllinie, "
            "am grössten an der gedrückten Kante. Ihre Resultierende liegt "
            "deshalb bei x/3 von dieser Kante."
        )

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        vergleich = r"\ge" if erg.erfuellt else "<"
        p.gleichung(
            rf"M_{{s,adm,{index}}} = {s_sigma} \cdot {s_a_s} \cdot z"
            rf" = {erg.sigma_s_adm / 1e6:.0f} \cdot {erg.a_s * 1e6:.0f} \cdot "
            rf"{erg.hebelarm * 1e3:.1f}"
            rf" = {erg.M_s_adm / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \quad {vergleich} \quad M_{{Riss}} = "
            rf"{self.groessen.M_Riss / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Aufnehmbares Moment der Bewehrung")

        grad = ("\\infty" if math.isinf(erg.erfuellungsgrad)
                else f"{erg.erfuellungsgrad:.2f}")
        p.gleichung(
            rf"\alpha_{{eff,ZB,{index}}} = \frac{{M_{{s,adm,{index}}}}}"
            rf"{{M_{{Riss}}}} = \frac{{{erg.M_s_adm / 1e3:.1f}}}"
            rf"{{{self.groessen.M_Riss / 1e3:.1f}}} = {grad}",
            titel="Erfüllungsgrad")

    def _index(self, erg: Momentlagenergebnis) -> str:
        eintraege = self.posten_je_lage[erg.lage.nummer]
        if not eintraege:
            return ""
        lage, art, *_ = eintraege[0]
        if len(eintraege) == 1:
            return posten_index(lage, art)
        return f"{lage.nummer},{lage.richtung.value}"


def _erster_E_s(e: Eingaben, lagen: Sequence[Bewehrungslage]) -> float:
    """
    Der Elastizitaetsmodul fuer die Wertigkeit im Ansatz.

    Im Ansatz steht n einmal; je Lage wird es mit dem Stahl dieser Lage
    gerechnet. Bei einer Platte mit zwei Sorten weichen die Zahlen dann ab --
    massgebend ist, was in der Lagenrechnung steht.
    """
    for lage in lagen:
        if lage.stahl:
            return e.g(f"E_s__{_kennung(lage.stahl.id)}").si
    return 0.0
