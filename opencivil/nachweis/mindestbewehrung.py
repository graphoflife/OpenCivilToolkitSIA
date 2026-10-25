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
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import (
    NICHT_FUEHRBAR, Ausfuehrung, Ausgang, Eingabebezug, Eingaben, Fallausgang, Fallbefund,
    Nachweis, NachweisUrteil, Vergleich, grad_def,
)
from opencivil.core.einheiten import MM, Groesse
from opencivil.core.latex import angabe, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.rissgroessen import (
    DICKENGRENZE, Rissgroessen as Momentgroessen, beiwert_dicke,
    protokoll_rissmoment_rechteck, protokoll_zugfestigkeit, rissaktive_dicke,
    rissmoment_rechteck, rissmoment_wert,
)
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.nachweis.zustand2 import gerissen, wertigkeit
from opencivil.querschnitt.lagenaufbau import Postenbezug, lage_aus_posten, protokoll_lage
from opencivil.querschnitt.platte import Bewehrungslage, Richtung


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
    h_eff = rissaktive_dicke(h=h, zug=True, begrenzt=begrenzt)
    k_t = beiwert_dicke(h_eff)
    f_ct_eff = k_t * f_ctm
    return Rissgroessen(h_eff=h_eff, k_t=k_t, f_ct_eff=f_ct_eff,
                        N_Riss=h_eff / 2.0 * b * f_ct_eff)


def zulaessige_stahlspannung(
    *, anforderung: Rissanforderung, f_yk: float, E_s: float, f_ctm: float,
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
    w_nom = anforderung.rissbreite
    if w_nom is None or durchmesser <= 0.0:
        return f_yk
    return min(math.sqrt(9.0 * E_s * f_ctm * w_nom / durchmesser), f_yk)


def protokoll_zulaessige_stahlspannung(
    p: Protokoll, sigma: Wert, *, anforderung: Rissanforderung, f_yk: Wert, E_s: Wert,
    f_ctm: Wert, durchmesser: Wert, basis: str, referenz: str = "",
) -> None:
    """
    Wie :func:`zulaessige_stahlspannung` zu ihrer Zahl kommt -- eine
    Herleitung fuer jeden Nachweis, der sie braucht.

    ``sigma`` ist das Resultat unter dem Symbol, unter dem es im Nachweis
    steht; ``durchmesser`` der Stab, der die Rissbreite bestimmt. Die Formel
    ist dimensionsrein -- (N/mm²)² unter der Wurzel -- und steht darum mit
    Einheiten da.
    """
    w_nom = anforderung.rissbreite
    if w_nom is None or durchmesser.groesse.si <= 0.0:
        p.formel(sigma, "@f_yk", {"f_yk": f_yk},
                 titel="Zulässige Stahlspannung (normale Anforderung)",
                 referenz=referenz)
        return
    w = Zwischenwerte(basis).laenge("w_nom", "w_{nom}", w_nom)
    p.formel(
        sigma,
        r"\min\left[\sqrt{\frac{9 \cdot @E_s \cdot @f_ctm \cdot @w_nom}{@dm}};\ @f_yk\right]",
        {"E_s": E_s, "f_ctm": f_ctm, "w_nom": w, "dm": durchmesser, "f_yk": f_yk},
        titel=f"Zulässige Stahlspannung (Rissbreite w_nom = {w.formatiert()} mm)",
        referenz=referenz)


def _protokoll_stahlspannung(
    p: Protokoll, e: Eingaben, werte: Zwischenwerte, erg, *,
    posten: Sequence[Postenbezug], anforderung: Rissanforderung,
) -> Wert:
    """
    ``sigma_s,adm`` einer Lage -- fuer beide Zwängungen dieselbe Herleitung.

    Liegen mehrere Posten in der Lage und begrenzt die Rissbreite, steht
    zuerst da, welcher Stab der dickste ist: er bestimmt die Rissbreite.
    Die Spannung gehoert der ganzen Lage und traegt deren Index, wie
    Widerstand und Erfuellungsgrad in der Tabelle.
    """
    lage = erg.lage.index
    staebe = [e[q.name("phi")] for q in posten]
    if len(staebe) == 1:
        durchmesser = staebe[0]
    else:
        durchmesser = werte.laenge("phi", rf"\varnothing_{{{lage}}}",
                                   erg.durchmesser, stellen=0)
        if anforderung.rissbreite is not None:
            glieder = r";\ ".join(f"@d{i}" for i in range(len(staebe)))
            p.formel(durchmesser, rf"\max\left[{glieder}\right]",
                     {f"d{i}": s for i, s in enumerate(staebe)},
                     titel="Dickster Stab der Lage")
    stahl = erg.lage.stahl
    sigma = werte.spannung("sigma_s_adm", rf"\sigma_{{s,adm,{lage}}}",
                           erg.sigma_s_adm)
    protokoll_zulaessige_stahlspannung(
        p, sigma, anforderung=anforderung, f_yk=e[stahl.eingabename("f_yk")],
        E_s=e[stahl.eingabename("E_s")], f_ctm=e["f_ctm"], durchmesser=durchmesser,
        basis=werte.basis, referenz="SIA 262:2025, 4.4.2")
    return sigma


@dataclass
class Lagenergebnis(Fallausgang):
    """Was der Nachweis fuer eine Lage gefunden hat: N_s,adm gegen N_Riss."""

    lage: Bewehrungslage
    a_s: float = 0.0
    durchmesser: float = 0.0
    """Der groesste Stabdurchmesser der Lage, in m -- er bestimmt die Rissbreite."""

    sigma_s_adm: float = 0.0
    N_s_adm: float = 0.0
    ausgang: Ausgang = NICHT_FUEHRBAR
    begruendung: str = ""


class Rissnormalkraft(Nachweis):
    """
    Sprödes Versagen unter Normalkraft-Zwängung.

    Ein Urteil je Lage der Tragrichtung: die untere und die obere müssen beide
    die Risskraft aufnehmen können -- ein Zwang kennt keine Zugseite, er
    beansprucht den Querschnitt über die ganze Höhe. In der Zusammenfassung
    steht die ungünstigere der beiden; die Urteile sind als Teile derselben
    Frage gestempelt (siehe ``Nachweis.teilurteile``).
    """

    THEMA = "Zwängung auf Normalkraft"
    ART = "N_Riss"
    LANGNAME = "Risse: Zwängung Normalkraft"

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        *,
        anforderung: Rissanforderung,
        begrenzt: bool,
    ) -> None:
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.anforderung = anforderung
        self.begrenzt = begrenzt

        # Genau zwei Lagen je Richtung -- auch die leeren, denn gerade sie
        # fallen durch und sollen es sichtbar tun.
        self.lagen = [l for l in querschnitt.lagen if l.richtung is richtung]
        self.posten_je_lage: Dict[int, List[Postenbezug]] = {
            l.nummer: querschnitt.posten_der_lage(l) for l in self.lagen}

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.rissnormalkraft.{r}"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: grad_def(
                f"{basis}.lage{l.nummer}.erfuellungsgrad",
                rf"\alpha_{{eff,NR,{l.nummer},{r}}}",
                (f"Erfüllungsgrad Rissnormalkraft – "
                 f"{l.nummer}. Lage {r}"),
                "SIA 262:2025, 4.4.2",
            )
            for l in self.lagen
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(richtung)),
            Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
        ]
        for posten in self.posten_je_lage.values():
            for q in posten:
                bezuege += q.bezuege("a_s", "phi")
        for stahl in {l.stahl.id: l.stahl for l in self.lagen if l.stahl}.values():
            bezuege += [stahl.bezug("f_yk"), stahl.bezug("E_s")]

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

        groessen = rissnormalkraft(h=h, b=b, f_ctm=f_ctm, begrenzt=self.begrenzt)
        self._protokoll_ansatz(p, e, groessen)

        urteile: List[NachweisUrteil] = []
        befund = Fallbefund()

        for lage in self.lagen:
            erg = self._eine_lage(e, lage, f_ctm=f_ctm, groessen=groessen)
            befund.ergebnisse.append(erg)
            self._protokoll_lage(p, e, erg)
            urteile.append(self.urteil(self.d_ausnutzung[lage.nummer], f"{lage.nummer}. Lage",
                                       erg.ausgang, erg.begruendung))

        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung({}, self.teilurteile(urteile), befund)

    def _eine_lage(self, e: Eingaben, lage: Bewehrungslage, *,
                   f_ctm: float, groessen: Rissgroessen) -> Lagenergebnis:
        erg = Lagenergebnis(lage=lage)
        posten = self.posten_je_lage[lage.nummer]

        erg.a_s = sum(e.g(q.name("a_s")).si for q in posten)
        if erg.a_s <= 0.0:
            erg.begruendung = self.ohne_bewehrung(lage.nummer)
            return erg

        # Der dickste Stab bestimmt die Rissbreite: er verteilt den Riss auf
        # die wenigsten Stäbe und bekommt damit die grösste Spannung.
        erg.durchmesser = max(e.g(q.name("phi")).si for q in posten)
        E_s = e.g(lage.stahl.eingabename("E_s")).si
        erg.sigma_s_adm = zulaessige_stahlspannung(
            anforderung=self.anforderung,
            f_yk=e.g(lage.stahl.eingabename("f_yk")).si, E_s=E_s, f_ctm=f_ctm,
            durchmesser=erg.durchmesser)
        erg.N_s_adm = erg.a_s * erg.sigma_s_adm

        erg.ausgang = v = Vergleich(self._n_riss(groessen), self._n_s_adm(erg))
        erg.begruendung = (
            f"N_s,adm = {erg.a_s * 1e6:.0f} mm² · {erg.sigma_s_adm / 1e6:.0f} N/mm² "
            f"= {erg.N_s_adm / 1e3:.1f} kN {'≥' if v.erfuellt else '<'} "
            f"N_Riss = {groessen.N_Riss / 1e3:.1f} kN.")
        return erg

    def _n_riss(self, groessen: Rissgroessen) -> Wert:
        """Die Risskraft -- die Einwirkung in Tabelle und Herleitung."""
        return Zwischenwerte(self.id).kraft("N_Riss", "N_{Riss}", groessen.N_Riss,
                                            "Einwirkung")

    def _n_s_adm(self, erg: Lagenergebnis) -> Wert:
        """Was die Lage aufnimmt -- der Widerstand in Tabelle und Herleitung."""
        nummer, r = erg.lage.nummer, self.richtung.value
        return Zwischenwerte(f"{self.id}.lage{nummer}").kraft(
            "N_s_adm", rf"N_{{s,adm,{nummer},{r}}}", erg.N_s_adm, "Widerstand")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, g: Rissgroessen) -> None:
        werte = Zwischenwerte(self.id)
        p.titel(f"Sprödes Versagen unter Zwängung – {self.richtung.beschriftung}")
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Die Bewehrung muss die Kraft übernehmen können, die "
            "der Beton beim Reissen abgibt – erst dann kündigt sich das "
            "Versagen an."
        )

        h_eff = werte.laenge("h_eff", "h_{eff}", g.h_eff)
        if self.begrenzt:
            grenze = Groesse.aus_si(DICKENGRENZE, MM).als_latex(0)
            p.formel(h_eff, rf"\min\left[{grenze};\ @h\right]", {"h": e["h"]},
                     titel="Rissaktive Plattendicke")
        else:
            p.formel(h_eff, "@h", {"h": e["h"]}, titel="Rissaktive Plattendicke")

        f_ct_eff = protokoll_zugfestigkeit(
            p, werte, k_t=g.k_t, f_ct_eff=g.f_ct_eff, h=h_eff, f_ctm=e["f_ctm"],
            teiler=1, referenz="SIA 262:2025, 4.4.2")
        p.formel(self._n_riss(g), r"\frac{@h_eff}{2} \cdot @b \cdot @f_ct_eff",
                 {"h_eff": h_eff, "b": e["b"], "f_ct_eff": f_ct_eff},
                 titel="Risskraft der gezogenen Querschnittshälfte")

    def _protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Lagenergebnis) -> None:
        nummer = erg.lage.nummer
        p.titel(f"Rissnormalkraft – {nummer}. Lage {self.richtung.value}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        posten = self.posten_je_lage[nummer]
        werte = Zwischenwerte(f"{self.id}.lage{nummer}")
        a_s, _ = protokoll_lage(p, e, werte, posten, a_s=erg.a_s)
        sigma = _protokoll_stahlspannung(p, e, werte, erg, posten=posten,
                                         anforderung=self.anforderung)

        v = erg.ausgang
        p.formel(v.widerstand, r"@A_s \cdot @sigma", {"A_s": a_s, "sigma": sigma},
                 titel="Aufnehmbare Risskraft",
                 nachsatz=vergleich(r"\ge", angabe(v.einwirkung), v.erfuellt))
        v.zeile(p, self.d_ausnutzung[nummer])



# ===========================================================================
# Rissmoment
# ===========================================================================


@dataclass
class Momentlagenergebnis(Fallausgang):
    """Was der Nachweis gegen das Rissmoment fuer eine Lage gefunden hat."""

    lage: Bewehrungslage
    a_s: float = 0.0
    z_s: float = 0.0
    """Gemeinsamer Schwerpunkt der Lage ab Oberkante, in m."""

    d: float = 0.0
    """Statische Hoehe ab der gedrueckten Randfaser, in m."""

    durchmesser: float = 0.0
    sigma_s_adm: float = 0.0

    n: float = 0.0
    rho: float = 0.0
    """``n * A_s / b``, die Hilfsgroesse der Nulllinie, in m."""

    x: float = 0.0
    hebelarm: float = 0.0
    M_s_adm: float = 0.0

    ausgang: Ausgang = NICHT_FUEHRBAR
    """M_s,adm gegen M_Riss -- nicht fuehrbar ohne Bewehrung in der Lage."""

    begruendung: str = ""


class Biegezwang(Nachweis):
    """
    Was die Zwaengung auf Biegung an der Platte (:class:`ZwaengungBiegung`)
    und am gezeichneten Querschnitt
    (:class:`~opencivil.nachweis.qa_gebrauch.ZwaengungBiegungQA`) teilt: Name,
    Thema, Normstelle und den ersten Satz der Herleitung.

    Mehr teilen sie nicht. Die Platte rechnet je Lage von Hand, mit dem
    Hebelarm ``d - x/3``; der gezeichnete Querschnitt sucht je Zugseite das
    Moment, bei dem der erste gezogene Stab seine Grenze erreicht. Gleich ist
    nur der Vergleich ``M_s,adm >= M_Riss`` -- ein gemeinsamer Nachweis haette
    fast nur weitergereicht (Benutzer, 2026-10-17).
    """

    THEMA = "Zwängung auf Biegung"
    LANGNAME = "Risse: Zwängung Biegung"
    REFERENZ = "SIA 262:2025, 4.4.2"
    ART = "ZB"

    #: Der erste Satz der Herleitung.
    EINLEITUNG = (
        "Eine aufgezwungene Krümmung erzeugt beim Reissen ein Moment, das "
        "die Bewehrung übernehmen muss – ohne über die zulässige "
        "Stahlspannung zu kommen. Nicht zu verwechseln mit dem Nachweis "
        "gegen sprödes Versagen: dort steht der Biegewiderstand gegen das "
        "Rissmoment, hier die Stahlspannung gegen ihre Grenze."
    )


class ZwaengungBiegung(Biegezwang):
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
        anforderung: Rissanforderung,
        kriechzahl: float,
    ) -> None:
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.anforderung = anforderung
        self.kriechzahl = kriechzahl

        gewaehlt = sorted(set(lagen))
        self.lagen = [l for l in querschnitt.lagen
                      if l.richtung is richtung and l.nummer in gewaehlt]
        if not self.lagen:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in "
                f"{richtung.beschriftung} ist keine der gewählten Lagen vorhanden.")
        self.posten_je_lage: Dict[int, List[Postenbezug]] = {
            l.nummer: querschnitt.posten_der_lage(l) for l in self.lagen}

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.zwang_biegung.{r}"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: grad_def(
                f"{basis}.lage{l.nummer}.erfuellungsgrad",
                rf"\alpha_{{eff,ZB,{l.nummer},{r}}}",
                f"Erfüllungsgrad {self.THEMA} – {l.nummer}. Lage {r}",
                self.REFERENZ,
            )
            for l in self.lagen
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(richtung)),
            Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
            Eingabebezug("E_cm", querschnitt.beton.id_von("E_cm")),
        ]
        for posten in self.posten_je_lage.values():
            for q in posten:
                bezuege += q.bezuege("a_s", "z", "phi")
        for stahl in {l.stahl.id: l.stahl for l in self.lagen if l.stahl}.values():
            bezuege += [stahl.bezug("f_yk"), stahl.bezug("E_s")]

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=f"{self.THEMA} {richtung.beschriftung} – {querschnitt.name}",
            referenz=self.REFERENZ,
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        f_ctm = e.g("f_ctm").si
        E_cm = e.g("E_cm").si
        phi = self.kriechzahl

        groessen = rissmoment_rechteck(h=h, b=b, f_ctm=f_ctm)
        self._protokoll_ansatz(p, e, groessen)

        urteile: List[NachweisUrteil] = []
        befund = Fallbefund()
        M_Riss = rissmoment_wert(self.id, groessen)

        for lage in self.lagen:
            erg = self._eine_lage(e, lage, b=b, f_ctm=f_ctm, E_cm=E_cm, phi=phi,
                                  M_Riss=M_Riss)
            befund.ergebnisse.append(erg)
            self._protokoll_lage(p, e, erg)
            urteile.append(self.urteil(self.d_ausnutzung[lage.nummer], f"{lage.nummer}. Lage",
                                       erg.ausgang, erg.begruendung))

        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung({}, self.teilurteile(urteile), befund)

    def _eine_lage(self, e: Eingaben, lage: Bewehrungslage, *,
                   b: float, f_ctm: float, E_cm: float, phi: float,
                   M_Riss: Wert) -> Momentlagenergebnis:
        erg = Momentlagenergebnis(lage=lage)
        posten = self.posten_je_lage[lage.nummer]

        erg.a_s, z, d = lage_aus_posten(e, posten)
        if erg.a_s <= 0.0:
            erg.begruendung = self.ohne_bewehrung(lage.nummer)
            return erg
        erg.z_s, erg.d = z, d
        erg.durchmesser = max(e.g(q.name("phi")).si for q in posten)

        E_s = e.g(lage.stahl.eingabename("E_s")).si
        erg.sigma_s_adm = zulaessige_stahlspannung(
            anforderung=self.anforderung,
            f_yk=e.g(lage.stahl.eingabename("f_yk")).si, E_s=E_s, f_ctm=f_ctm,
            durchmesser=erg.durchmesser)

        erg.n = wertigkeit(E_s=E_s, E_cm=E_cm, phi=phi)
        riss = gerissen(n=erg.n, a_s=erg.a_s, b=b, d=erg.d)
        erg.rho = riss.rho
        erg.x = riss.x
        erg.hebelarm = riss.z
        erg.M_s_adm = erg.sigma_s_adm * erg.a_s * erg.hebelarm

        erg.ausgang = v = Vergleich(M_Riss, self._m_s_adm(erg))
        erg.begruendung = (
            f"Gerissen: x = {erg.x * 1e3:.1f} mm, z = {erg.hebelarm * 1e3:.1f} mm, "
            f"σ_s,adm = {erg.sigma_s_adm / 1e6:.0f} N/mm² → "
            f"M_s,adm = {erg.M_s_adm / 1e3:.1f} kNm {'≥' if v.erfuellt else '<'} "
            f"M_Riss = {M_Riss.groesse.si / 1e3:.1f} kNm.")
        return erg

    def _m_s_adm(self, erg: Momentlagenergebnis) -> Wert:
        """Was die Lage aufnimmt -- der Widerstand in Tabelle und Herleitung."""
        nummer, r = erg.lage.nummer, self.richtung.value
        return Zwischenwerte(f"{self.id}.lage{nummer}").moment(
            "M_s_adm", rf"M_{{s,adm,{nummer},{r}}}", erg.M_s_adm, "Widerstand")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben,
                          groessen: Momentgroessen) -> None:
        p.titel(f"{self.THEMA} – {self.richtung.beschriftung}")
        p.erklaerung(self.EINLEITUNG)
        protokoll_rissmoment_rechteck(p, e, groessen, basis=self.id, referenz=self.REFERENZ)
        p.erklaerung(
            "Das Rissmoment gilt für den ungerissenen Bruttoquerschnitt – den "
            "Zustand vor dem Riss. Der Widerstand dagegen wird am gerissenen "
            "Querschnitt bestimmt, also für den Augenblick danach. Dass zwei "
            "verschiedene Querschnitte auftreten, ist genau die Frage: reicht "
            "die Bewehrung für das, was der Beton abgibt?"
        )
        E_s = _erster_E_s(e, self.lagen)
        if E_s is not None:
            werte = Zwischenwerte(self.id)
            n = wertigkeit(E_s=E_s.groesse.si, E_cm=e.g("E_cm").si, phi=self.kriechzahl)
            p.formel(werte.zahl("n", "n", n, stellen=2),
                     r"\frac{@E_s}{@E_cm} \cdot \left(1 + @phi\right)",
                     {"E_s": E_s, "E_cm": e["E_cm"],
                      "phi": werte.zahl("phi", r"\varphi", self.kriechzahl, stellen=2)},
                     titel="Wertigkeit im gerissenen Zustand")
        p.erklaerung(
            "Das Kriechen weicht den Beton auf: E_c,eff = E_cm/(1+φ), und die "
            "Wertigkeit ist E_s/E_c,eff. Ein grösseres φ senkt damit den "
            "Hebelarm und liegt auf der sicheren Seite."
        )

    def _protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Momentlagenergebnis) -> None:
        nummer = erg.lage.nummer
        p.titel(f"{self.THEMA} – {nummer}. Lage {self.richtung.value}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        posten = self.posten_je_lage[nummer]
        werte = Zwischenwerte(f"{self.id}.lage{nummer}")
        a_s, d = protokoll_lage(p, e, werte, posten, a_s=erg.a_s, z=erg.z_s, d=erg.d)
        sigma = _protokoll_stahlspannung(p, e, werte, erg, posten=posten,
                                         anforderung=self.anforderung)

        rho = werte.laenge("rho", r"\rho", erg.rho, stellen=2)
        p.formel(rho, r"\frac{@n \cdot @A_s}{@b}",
                 {"n": werte.zahl("n", "n", erg.n, stellen=2), "A_s": a_s, "b": e["b"]},
                 titel="Hilfsgrösse der Nulllinie")
        x = werte.laenge("x", "x", erg.x)
        p.formel(x, r"\sqrt{@rho^{2} + 2 \cdot @d \cdot @rho} - @rho",
                 {"rho": rho, "d": d}, titel="Nulllinie des gerissenen Querschnitts")
        hebelarm = werte.laenge("hebelarm", "z", erg.hebelarm)
        p.formel(hebelarm, r"@d - \frac{@x}{3}", {"d": d, "x": x},
                 titel="Innerer Hebelarm")
        p.erklaerung(
            "Die Betondruckspannung verläuft dreieckig – null in der Nulllinie, "
            "am grössten an der gedrückten Kante. Ihre Resultierende liegt "
            "deshalb bei x/3 von dieser Kante."
        )

        v = erg.ausgang
        p.formel(v.widerstand, r"@sigma \cdot @A_s \cdot @z",
                 {"sigma": sigma, "A_s": a_s, "z": hebelarm},
                 titel="Aufnehmbares Moment der Bewehrung",
                 nachsatz=vergleich(r"\ge", angabe(v.einwirkung), v.erfuellt))
        v.zeile(p, self.d_ausnutzung[nummer])


def _erster_E_s(e: Eingaben, lagen: Sequence[Bewehrungslage]) -> Optional[Wert]:
    """
    Der Elastizitaetsmodul fuer die Wertigkeit im Ansatz.

    Im Ansatz steht n einmal; je Lage wird es mit dem Stahl dieser Lage
    gerechnet. Bei einer Platte mit zwei Sorten weichen die Zahlen dann ab --
    massgebend ist, was in der Lagenrechnung steht. ``None``, wenn keine der
    Lagen einen Stahl traegt.
    """
    for lage in lagen:
        if lage.stahl:
            return e[lage.stahl.eingabename("E_s")]
    return None
