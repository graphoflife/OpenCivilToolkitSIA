"""
opencivil/nachweis/qa_gebrauch.py -- Gebrauchsnachweise des gezeichneten Querschnitts.

VERANTWORTUNG:
Was die Platte unter Gebrauchslast nachweist, am gezeichneten Querschnitt:

* die Stahlspannung -- unter quasi-staendiger Einwirkung aus der Rissbreite
  begrenzt, unter haeufiger gegen das Fliessen (:class:`SpannungsbegrenzungQA`);
* die Zwaengung auf Normalkraft, am ganzen Querschnitt
  (:class:`RissnormalkraftQA`), und auf Biegung, je Richtung
  (:class:`ZwaengungBiegungQA`).

Die Grenzen sind die der Platte, aus denselben Funktionen
(:func:`~opencivil.nachweis.mindestbewehrung.zulaessige_stahlspannung`,
``f_yd - 80 N/mm²``), und die Woerter, unter denen die Stahlspannungen
erscheinen, aus denselben Grenzen (:mod:`~opencivil.nachweis.spannungsbegrenzung`).
Anders ist, woran sie gemessen werden.

JE STAB:
Die Platte haelt je Lage den dicksten Stab gegen die Rissbreite. Hier haelt
jeder gezogene Stab gegen seine eigene Grenze, und massgebend ist der
kleinste Erfuellungsgrad (Benutzer, 2026-10-15) -- wie ein Stab zu seiner
Grenze kommt, steht in :mod:`opencivil.nachweis.stabgrenzen`, wie die Ebene
unter Gebrauchslast gefunden wird, in :mod:`opencivil.nachweis.gebrauchsebene`.

ZWAENGUNG AUF NORMALKRAFT:
Es reisst der ganze Querschnitt, und die Bewehrung muss aufnehmen, was der
Beton dabei abgibt (Benutzer, 2026-10-15)::

    t        = min(b; h)                  kleinere Abmessung des Betons,
                                          wahlweise hoechstens 500 mm
    k_t      = 1 / (1 + 0.5 · t)
    N_Riss   = Σ A_c · k_t · f_ctm        je Beton
    N_s,adm  = Σ A_s,i · sigma_s,adm,i   >=  N_Riss

Bei der Platte nimmt jede Lage die Haelfte -- zusammen derselbe Gedanke.

ZWAENGUNG AUF BIEGUNG:
Je Richtung wie das sproede Versagen: dasselbe Rissmoment
(:func:`~opencivil.nachweis.rissgroessen.rissmoment`), gehalten gegen
das Moment, bei dem der erste gezogene Stab sein ``sigma_s,adm`` erreicht --
am gerissenen Querschnitt, elastisch, ohne Normalkraft, mit eigenem φ
(Benutzer, 2026-10-15). Die Platte rechnet dasselbe von Hand, mit dem
Hebelarm ``d - x/3`` und ohne die gedrueckte Bewehrung; hier wirkt sie mit.

NACH VORGABE, NICHT NACHGESCHLAGEN:
Der ganze Querschnitt bei der Normalkraft, ``t`` als kleinere Abmessung, die
Grenze je Stab, der fiktive Durchmesser und das Moment am elastisch
gerissenen Querschnitt. Siehe ``notizbuch/Notizen/TODO.md``.

EINHEITEN:
SI-Basis wie im ganzen Querschnittsmodul; die Zeichnung in mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Type

from opencivil.core.berechnung import (
    Ausfuehrung, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, MM, Groesse
from opencivil.core.latex import Mathe, als_text, angabe, bedingung, fest, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.material.basis import Baustoff, mit_index
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.nachweis.gebrauchsebene import (
    EINACHSIG, KEINE, SUCHE_DER_EBENE, Gebrauchsebene, gebrauchsebene, protokoll_ebene,
)
from opencivil.nachweis.querschnittsloeser import VERFEHLTE_EBENE
from opencivil.nachweis.rechenwahl import protokoll_gesetze_nach_wahl, protokoll_rechenwahl
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.nachweis.richtungsnachweise import richtungen
from opencivil.nachweis.rissgroessen import (
    DICKENGRENZE, beiwert_dicke, bruttoquerschnitt, protokoll_rissmoment,
    protokoll_spannung_ungerissen, protokoll_zugfestigkeit, rissaktive_dicke, rissbezuege,
    rissmoment,
)
from opencivil.nachweis.schiefe_biegung import protokoll_dehnungsebene
from opencivil.nachweis.spannungsbegrenzung import (
    VERGLEICH_BEIM_FLIESSEN, VORGABE, GrenzeGegenFliessen, Spannungsgrenze, Vergleich,
    protokoll_festlegungen,
)
from opencivil.nachweis.stabgrenzen import (
    GRENZE_JE_STAB, Grenzen, Stabangabe, grenzen_aus_rissbreite, grenzen_gegen_fliessen,
    protokoll_fliessgrenzen, protokoll_rissbreitengrenzen, stabangaben,
)
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.querschnitt.interaktion import Querschnitt, illinois

#: Wann das Moment der Zwaengung auf Biegung gefunden ist: wie nahe der
#: erste gezogene Stab seiner Grenze kommen muss, als Teil von ihr.
GRENZ_SCHRANKE = 1e-7


# ===========================================================================
# Stahlspannung
# ===========================================================================


@dataclass
class Fallergebnis:
    """Was der Nachweis fuer einen Lastfall gefunden hat."""

    fall: Lastfall
    ebene: Gebrauchsebene = KEINE
    stab: int = 0
    """Der massgebende Stab: der gezogene mit dem kleinsten Erfuellungsgrad."""

    eps_s: float = 0.0
    sigma_s: float = 0.0
    E_s: float = 0.0
    eps_y: float = 0.0
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    vergleich: Optional[Vergleich] = None
    """Fehlt nur, wenn sich keine Gleichgewichtslage fand."""

    begruendung: str = ""
    hinweis: str = ""

    @property
    def fliesst(self) -> bool:
        return self.eps_s > self.eps_y


class SpannungsbegrenzungQA(Nachweis):
    """
    Die Stahlspannung je Lastfall gegen ihre Grenze -- aus der Rissbreite
    oder gegen das Fliessen, je nach ``grenze``. Ein Urteil je Lastfall.
    """

    @property
    def thema(self) -> str:
        return self.grenze.thema

    @property
    def langname(self) -> str:
        return self.grenze.langname

    def __init__(self, analyse: Querschnittsanalyse, faelle: Sequence[Lastfall], *,
                 grenze: Type[Spannungsgrenze], anforderung: Rissanforderung,
                 wahl: Rechenwahl = VORGABE, einachsig: bool = False) -> None:
        if not faelle:
            raise ValueError("Ohne Lastfall gibt es nichts zu begrenzen.")
        self.analyse = analyse
        self.faelle = list(faelle)
        self.grenze = grenze
        self.anforderung = anforderung
        self.wahl = wahl
        self.einachsig = einachsig
        basis = f"{analyse.id}.nachweis.{grenze.idteil}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{grenze.symbolteil},{als_text(f.name)}}}",
                             f"Erfüllungsgrad {grenze.thema} – {f.name}", grenze.referenz)
            for f in self.faelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege(),
                         titel=f"Stahlspannung unter {grenze.einwirkung} Einwirkung – "
                               f"{analyse.name}",
                         referenz=grenze.referenz, abschnitt=analyse.abschnitt)

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        a = self.analyse
        q, herkunft, _ = a.querschnitt(e.si_nach_id(), self.wahl)
        staebe = stabangaben(a, q, herkunft)
        grenzen = (grenzen_gegen_fliessen(a, e, staebe) if self.grenze is GrenzeGegenFliessen
                   else grenzen_aus_rissbreite(a, e, staebe, self.anforderung))
        self._protokoll_ansatz(p, e, staebe, grenzen)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for fall in self.faelle:
            # Ausgeschaltete Lastfaelle rechnen mit und schweigen dabei.
            leise = self.leise(fall.name)
            erg = self._einen_fall(e, q, staebe, grenzen, fall)
            if not leise:
                self._protokoll_fall(p, e, staebe, grenzen, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(erg.erfuellungsgrad,
                                                                EINHEITSLOS)
            urteile.append(self._urteil(erg, still=leise))
        return Ausfuehrung(ergebnis, urteile)

    def _einen_fall(self, e: Eingaben, q: Querschnitt, staebe: Sequence[Stabangabe],
                    grenzen: Grenzen, fall: Lastfall) -> Fallergebnis:
        erg = Fallergebnis(fall=fall)
        if not staebe:
            erg.begruendung = erg.hinweis = "Ohne Bewehrung gibt es keine Stahlspannung."
            return erg
        erg.ebene = ebene = gebrauchsebene(q, N=fall.N, M_y=fall.M_y, M_z=fall.M_z,
                                           einachsig=self.einachsig)
        if not ebene.konvergiert:
            erg.begruendung = erg.hinweis = (
                self.wahl.art.ohne_ebene if ebene.verfehlt else
                f"Keine Dehnungsebene für N = {fall.N / 1e3:.1f} kN, "
                f"M_y = {fall.M_y / 1e3:.1f} kNm"
                + ("" if self.einachsig else f", M_z = {fall.M_z / 1e3:.1f} kNm")
                + " → nicht aufnehmbar.")
            return erg

        # Gemessen an der Dehnung, wie bei der Platte: auf dem Plateau haben
        # mehrere Staebe dieselbe Spannung, aber nur einer ist am weitesten
        # gedehnt. Ohne gezogenen Stab steht die strengste Grenze da.
        E_s = [self.analyse.kennwert(e, s.stahl, "E_s") for s in staebe]
        gezogen = [(grenzen.sigma(i) / (E_s[i] * eps), -eps, i)
                   for i, eps in enumerate(ebene.eps_s) if eps > 0.0]
        i = erg.stab = min(gezogen)[2] if gezogen else grenzen.strengste
        erg.E_s = E_s[i]
        erg.eps_s = ebene.eps_s[i] if gezogen else 0.0
        erg.sigma_s = ebene.sigma_s[i] if gezogen else 0.0
        erg.eps_y = abs(self.analyse.kennwert(e, staebe[i].stahl,
                                              self.wahl.satz.stahl)) / erg.E_s
        gedehnt = erg.E_s * erg.eps_s
        erg.erfuellungsgrad = math.inf if gedehnt <= 0.0 else grenzen.sigma(i) / gedehnt
        erg.erfuellt = gedehnt <= grenzen.sigma(i)
        erg.vergleich = self._vergleich(erg, grenzen)
        erg.begruendung = f"{staebe[i].element.name}: {erg.vergleich.satz}"
        return erg

    def _vergleich(self, erg: Fallergebnis, grenzen: Grenzen) -> Vergleich:
        """Spannungen oder Dehnungen -- die eine Stelle, die das entscheidet."""
        werte = Zwischenwerte(f"{self.id}.{erg.fall.kennung}")
        gruppe = grenzen.gruppe(erg.stab)
        if erg.fliesst:
            eps_adm = gruppe.sigma / erg.E_s
            return Vergleich(
                einwirkung=werte.dehnung("eps_s", r"\varepsilon_s", erg.eps_s, "Einwirkung"),
                widerstand=werte.dehnung("eps_s_adm", r"\varepsilon_{s,adm}", eps_adm,
                                         "Widerstand"),
                satz=(f"Stahl fliesst (ε_s = {erg.eps_s * 1e3:.2f} ‰ > ε_y = "
                      f"{erg.eps_y * 1e3:.2f} ‰): ε_s {'≤' if erg.erfuellt else '>'} "
                      f"ε_s,adm = {eps_adm * 1e3:.2f} ‰."))
        return Vergleich(
            einwirkung=werte.spannung("sigma_s", r"\sigma_s", erg.sigma_s, "Einwirkung"),
            widerstand=gruppe.wert,
            satz=(f"σ_s = {erg.sigma_s / 1e6:.0f} N/mm² {'≤' if erg.erfuellt else '>'} "
                  f"σ_s,adm = {gruppe.sigma / 1e6:.0f} N/mm²."))

    def _urteil(self, erg: Fallergebnis, *, still: bool) -> NachweisUrteil:
        vergleich = erg.vergleich
        return NachweisUrteil(
            art=self.grenze.art, ziel=self.d_ausnutzung[erg.fall.name].id,
            fall=erg.fall.name, erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung, hinweis=erg.hinweis,
            einwirkung=vergleich.einwirkung if vergleich else None,
            widerstand=vergleich.widerstand if vergleich else None, still=still)

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, staebe: Sequence[Stabangabe],
                          grenzen: Grenzen) -> None:
        g = self.grenze
        p.titel(f"Stahlspannung unter {g.einwirkung} Einwirkung")
        p.erklaerung(
            f"{g.einleitung} Gerechnet wird am gerissenen Querschnitt: der Beton nimmt "
            f"keinen Zug auf, die Bewehrung wirkt auf Zug und auf Druck. Jeder gezogene "
            f"Stab hält gegen seine Grenze; massgebend ist der mit dem kleinsten "
            f"Erfüllungsgrad.")
        protokoll_rechenwahl(p, self.wahl, self.id)
        if g is GrenzeGegenFliessen:
            protokoll_fliessgrenzen(p, e, self.analyse, grenzen, self.id)
        else:
            protokoll_rissbreitengrenzen(p, e, self.analyse, staebe, grenzen,
                                         self.anforderung, self.id, referenz=g.referenz)
        protokoll_festlegungen(p, self.wahl)
        protokoll_gesetze_nach_wahl(p, e, self.analyse, self.wahl, self.id,
                          titel="Werkstoffgesetze im Gebrauchszustand")
        if g is GrenzeGegenFliessen:
            g.festlegung(p)
        else:
            p.erklaerung("Drittens die Grenze: dieselbe wie bei der Zwängung, mit f_yk "
                         "und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch "
                         f"die Rissbreite. {GRENZE_JE_STAB}")
        p.erklaerung(VERGLEICH_BEIM_FLIESSEN)
        p.titel("Wie die Dehnungsebene gefunden wird", ebene=3)
        protokoll_dehnungsebene(p)
        p.erklaerung(EINACHSIG if self.einachsig else SUCHE_DER_EBENE)
        p.erklaerung(VERFEHLTE_EBENE)

    def _protokoll_fall(self, p: Protokoll, e: Eingaben, staebe: Sequence[Stabangabe],
                        grenzen: Grenzen, erg: Fallergebnis) -> None:
        fall = erg.fall
        index = self.grenze.lastindex
        p.titel(f"{self.grenze.fallwort} – {fall.name}", ebene=3)
        teile = [rf"N_{{Ed,{index}}} = {fest(fall.N / 1e3, 1)}\ \mathrm{{kN}}",
                 rf"M_{{y,Ed,{index}}} = {fest(fall.M_y / 1e3, 1)}\ \mathrm{{kNm}}"]
        if not self.einachsig:
            teile.append(rf"M_{{z,Ed,{index}}} = {fest(fall.M_z / 1e3, 1)}\ \mathrm{{kNm}}")
        p.gleichung(r" \qquad ".join(teile), titel="Einwirkung")
        if erg.vergleich is None:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        protokoll_ebene(p, werte, erg.ebene, self.einachsig)
        if erg.eps_s <= 0.0:
            p.text("Kein Stab ist gezogen – es gibt keine Zugspannung zu begrenzen.")
        else:
            self._tabelle_gezogen(p, staebe, grenzen, erg.ebene)
            p.text(f"Massgebend: {staebe[erg.stab].ort}.")
        wirkt, grenze = erg.vergleich.einwirkung, erg.vergleich.widerstand
        if erg.fliesst:
            stahl = staebe[erg.stab].stahl
            E_s = e[self.analyse._name(stahl, "E_s")]
            p.text(f"Stahl fliesst (σ_s = {erg.sigma_s / 1e6:.0f} N/mm²) → "
                   f"Vergleich über die Dehnung.")
            p.formel(werte.dehnung("eps_y", r"\varepsilon_y", erg.eps_y),
                     r"\frac{@f_s}{@E_s}",
                     {"f_s": e[self.analyse._name(stahl, self.wahl.satz.stahl)], "E_s": E_s},
                     titel="Grösste Zugdehnung in der Bewehrung", name=FLIESSDEHNUNG,
                     nachsatz=rf"\quad < \quad {angabe(wirkt)}")
            p.formel(grenze, r"\frac{@sigma}{@E_s}",
                     {"sigma": grenzen.gruppe(erg.stab).wert, "E_s": E_s},
                     titel="Zulässige Dehnung",
                     nachsatz=vergleich(r"\ge", angabe(wirkt), erg.erfuellt))
        else:
            p.gleichung(bedingung(angabe(wirkt), r"\le", angabe(grenze), erg.erfuellt),
                        titel="Grösste Zugspannung in der Bewehrung")
        grad_formel(p, self.d_ausnutzung[fall.name], erg.erfuellungsgrad, grenze, wirkt,
                    erg.erfuellt)

    @staticmethod
    def _tabelle_gezogen(p: Protokoll, staebe: Sequence[Stabangabe], grenzen: Grenzen,
                         ebene: Gebrauchsebene) -> None:
        """
        Je Element mit gezogenen Staeben der unguenstigste: Dehnung, Spannung,
        Grenze -- bei einer verschmierten Linie das Stueck, das seiner Grenze
        am naechsten kommt.
        """
        je_element: Dict[str, int] = {}
        for i, eps in enumerate(ebene.eps_s):
            if eps <= 0.0:
                continue
            kennung = staebe[i].element.kennung
            bisher = je_element.get(kennung)
            if bisher is None or (ebene.sigma_s[i] / grenzen.sigma(i)
                                  > ebene.sigma_s[bisher] / grenzen.sigma(bisher)):
                je_element[kennung] = i
        zeilen = [[staebe[i].element.name, Mathe(fest(ebene.eps_s[i] * 1e3, 3)),
                   Mathe(fest(ebene.sigma_s[i] / 1e6, 0)),
                   Mathe(fest(grenzen.sigma(i) / 1e6, 0))]
                  for i in je_element.values()]
        p.tabelle(kopf=["Element", Mathe(r"\varepsilon_s\ [‰]"),
                        Mathe(r"\sigma_s\ [\mathrm{N/mm^2}]"),
                        Mathe(r"\sigma_{s,adm}\ [\mathrm{N/mm^2}]")],
                  zeilen=zeilen, titel="Gezogene Bewehrung, je Element der ungünstigste Stab",
                  ausrichtung="lrrr")


# ===========================================================================
# Zwaengung auf Normalkraft
# ===========================================================================


def betonflaechen(analyse: Querschnittsanalyse) -> List[Tuple[Baustoff, float]]:
    """
    Die Flaeche jedes Betons, in m² -- ein Polygon zaehlt fuer seinen Beton
    und wird dem abgezogen, in dem es liegt, wie in der Interaktion.
    """
    flaechen: Dict[str, List] = {}
    for i, f in enumerate(analyse.flaechen):
        A = abs(geo.flaechenwerte(f.punkte).A) * 1e-6
        eltern = analyse.eltern[i]
        fremd = analyse.flaechen[eltern].stoff if eltern is not None else None
        for stoff, vorzeichen in ((f.stoff, 1.0), (fremd, -1.0)):
            if stoff is not None:
                flaechen.setdefault(stoff.id, [stoff, 0.0])[1] += vorzeichen * A
    return [(stoff, A) for stoff, A in flaechen.values() if A > 0.0]


class RissnormalkraftQA(Nachweis):
    """Der ganze Querschnitt reisst: seine Risskraft gegen alle Staebe zusammen."""

    THEMA = "Zwängung auf Normalkraft"
    LANGNAME = "Risse: Zwängung Normalkraft"

    def __init__(self, analyse: Querschnittsanalyse, *, anforderung: Rissanforderung,
                 begrenzt: bool) -> None:
        self.analyse = analyse
        self.anforderung = anforderung
        self.begrenzt = begrenzt
        basis = f"{analyse.id}.nachweis.rissnormalkraft"
        self.d_grad = grad_def(f"{basis}.erfuellungsgrad", r"\alpha_{eff,NR}",
                               "Erfüllungsgrad Rissnormalkraft – ganzer Querschnitt",
                               "SIA 262:2025, 4.4.2")
        super().__init__(basis, ausgaben=[self.d_grad], bezuege=analyse.grundbezuege(),
                         titel=f"Sprödes Versagen unter Zwängung – {analyse.name}",
                         referenz="SIA 262:2025, 4.4.2", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        a = self.analyse
        werte = Zwischenwerte(self.id)
        p.titel("Sprödes Versagen unter Zwängung")
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Die Bewehrung muss die Kraft übernehmen können, die "
            "der Beton beim Reissen abgibt – erst dann kündigt sich das "
            "Versagen an.")
        p.erklaerung(
            "Eine aufgezwungene Verkürzung zieht den ganzen Querschnitt: es reisst der "
            "ganze Beton, und alle Stäbe teilen sich seine Risskraft, jeder bis zu seiner "
            "zulässigen Spannung. Die rissaktive Dicke t ist die kleinere Abmessung des "
            "Betons.")
        N_Riss = self._risskraft(p, e, werte)

        q, herkunft, _ = a.querschnitt(e.si_nach_id(), VORGABE)
        staebe = stabangaben(a, q, herkunft)
        if not staebe:
            p.text("Ohne Bewehrung → kein Nachweis.")
            return self._ergebnis(0.0, False, "Ohne Bewehrung → kein Nachweis.", N_Riss, None)
        grenzen = grenzen_aus_rissbreite(a, e, staebe, self.anforderung)
        protokoll_rissbreitengrenzen(p, e, a, staebe, grenzen, self.anforderung, self.id,
                                     referenz="SIA 262:2025, 4.4.2")
        mehrere = len(grenzen.gruppen) > 1
        glieder = []
        for nummer, gruppe in enumerate(grenzen.gruppen, start=1):
            A_s = werte.flaeche(f"A_s{nummer}" if mehrere else "A_s",
                                rf"A_{{s,{nummer}}}" if mehrere else "A_s",
                                sum(staebe[i].flaeche for i in gruppe.staebe))
            glieder.append((A_s, gruppe.wert))
        N_s_adm_si = sum(A.groesse.si * s.groesse.si for A, s in glieder)
        N_s_adm = werte.kraft("N_s_adm", r"N_{s,adm}", N_s_adm_si, "Widerstand")
        erfuellt = N_s_adm_si >= N_Riss.groesse.si
        p.formel(N_s_adm, " + ".join(f"@A{i} \\cdot @s{i}" for i in range(len(glieder))),
                 {**{f"A{i}": A for i, (A, _) in enumerate(glieder)},
                  **{f"s{i}": s for i, (_, s) in enumerate(glieder)}},
                 titel="Aufnehmbare Risskraft", name="Aufnehmbare Risskraft",
                 nachsatz=vergleich(r"\ge", angabe(N_Riss), erfuellt))
        grad = math.inf if N_Riss.groesse.si == 0.0 else N_s_adm_si / N_Riss.groesse.si
        grad_formel(p, self.d_grad, grad, N_s_adm, N_Riss, erfuellt)
        return self._ergebnis(
            grad, erfuellt,
            f"N_s,adm = {N_s_adm_si / 1e3:.1f} kN {'≥' if erfuellt else '<'} "
            f"N_Riss = {N_Riss.groesse.si / 1e3:.1f} kN.", N_Riss, N_s_adm)

    def _risskraft(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte) -> Wert:
        """Rissaktive Dicke, wirksame Zugfestigkeit je Beton und die Risskraft."""
        ecken = self.analyse.beton_ecken
        b = (max(pt[0] for pt, _ in ecken) - min(pt[0] for pt, _ in ecken)) * 1e-3
        h = (max(pt[1] for pt, _ in ecken) - min(pt[1] for pt, _ in ecken)) * 1e-3
        grenze = ""
        if self.begrenzt:
            grenze = Groesse.aus_si(DICKENGRENZE, MM).als_latex(0) + r";\ "
        t = werte.laenge("t", "t", rissaktive_dicke(h=h, b=b, zug=True, begrenzt=self.begrenzt))
        p.formel(t, rf"\min\left[{grenze}@b;\ @h\right]",
                 {"b": werte.laenge("b", "b", b, "Ausdehnung des Betons in y"),
                  "h": werte.laenge("h", "h", h, "Ausdehnung des Betons in z")},
                 titel=("Rissaktive Dicke: die kleinere Abmessung, höchstens 500 mm"
                        if self.begrenzt else "Rissaktive Dicke: die kleinere Abmessung"),
                 name="Rissaktive Dicke des gezeichneten Querschnitts")
        k_t = beiwert_dicke(t.groesse.si)
        glieder = []
        for stoff, A_c in betonflaechen(self.analyse):
            unter = Zwischenwerte(f"{self.id}.{kennung_aus(stoff.id)}")
            f_ctm = e[self.analyse._name(stoff, "f_ctm")]
            f_ct_eff = protokoll_zugfestigkeit(
                p, unter, k_t=k_t, f_ct_eff=k_t * abs(f_ctm.groesse.si), h=t, f_ctm=f_ctm,
                teiler=1, referenz="SIA 262:2025, 4.4.2",
                titel=f"Beiwert für die rissaktive Dicke, {stoff.name}")
            glieder.append((unter.flaeche("A_c", mit_index("A_c", stoff.symbol_index), A_c,
                                          f"Betonfläche {stoff.name}"), f_ct_eff))
        N_Riss = werte.kraft("N_Riss", "N_{Riss}",
                             sum(A.groesse.si * f.groesse.si for A, f in glieder), "Einwirkung")
        p.formel(N_Riss, " + ".join(f"@A{i} \\cdot @f{i}" for i in range(len(glieder))),
                 {**{f"A{i}": A for i, (A, _) in enumerate(glieder)},
                  **{f"f{i}": f for i, (_, f) in enumerate(glieder)}},
                 titel="Risskraft des ganzen Querschnitts",
                 name="Risskraft des ganzen Querschnitts")
        return N_Riss

    def _ergebnis(self, grad: float, erfuellt: bool, begruendung: str, N_Riss: Wert,
                  N_s_adm: Optional[Wert]) -> Ausfuehrung:
        ohne = N_s_adm is None
        urteil = NachweisUrteil(
            art="N_Riss", ziel=self.d_grad.id, fall="ganzer Querschnitt", erfuellt=erfuellt,
            erfuellungsgrad=Groesse(grad, EINHEITSLOS), begruendung=begruendung,
            hinweis=begruendung if ohne else "",
            einwirkung=None if ohne else N_Riss, widerstand=N_s_adm)
        return Ausfuehrung({self.d_grad.id: Groesse(grad, EINHEITSLOS)}, [urteil])


# ===========================================================================
# Zwaengung auf Biegung
# ===========================================================================


class ZwaengungBiegungQA(Nachweis):
    """
    Je Richtung das Rissmoment gegen das Moment, bei dem der erste gezogene
    Stab sein ``sigma_s,adm`` erreicht.
    """

    THEMA = "Zwängung auf Biegung"
    LANGNAME = "Risse: Zwängung Biegung"

    def __init__(self, analyse: Querschnittsanalyse, *, einachsig: bool,
                 anforderung: Rissanforderung,
                 kriechzahl: float) -> None:
        self.analyse = analyse
        self.einachsig = einachsig
        self.anforderung = anforderung
        self.wahl = Rechenwahl(kriechzahl=kriechzahl, satz=VORGABE.satz, art=VORGABE.art)
        basis = f"{analyse.id}.nachweis.zwang_biegung"
        self.d_ausnutzung: Dict[str, WertDef] = {
            name: grad_def(f"{basis}.{kennung_aus(name)}.erfuellungsgrad",
                           rf"\alpha_{{eff,ZB,{als_text(name)}}}",
                           f"Erfüllungsgrad Zwängung auf Biegung – {name}",
                           "SIA 262:2025, 4.4.2")
            for name, _, _ in richtungen(einachsig)}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege() + rissbezuege(analyse),
                         titel=f"Zwängung auf Biegung – {analyse.name}",
                         referenz="SIA 262:2025, 4.4.2", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        a = self.analyse
        q, herkunft, _ = a.querschnitt(e.si_nach_id(), self.wahl)
        staebe = stabangaben(a, q, herkunft)
        self._protokoll_ansatz(p, e)
        grenzen = grenzen_aus_rissbreite(a, e, staebe, self.anforderung)
        protokoll_rissbreitengrenzen(p, e, a, staebe, grenzen, self.anforderung, self.id,
                                     referenz="SIA 262:2025, 4.4.2")
        protokoll_dehnungsebene(p)
        p.erklaerung(EINACHSIG if self.einachsig else SUCHE_DER_EBENE)

        brutto = bruttoquerschnitt(a, e.si_nach_id())
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for name, M_y, M_z in richtungen(self.einachsig):
            d_grad = self.d_ausnutzung[name]
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            p.titel(name, ebene=3)
            riss = rissmoment(brutto, M_y, M_z, einachsig=self.einachsig)
            gefunden = self._an_der_grenze(q, staebe, grenzen, M_y, M_z, riss.M_Riss)
            if gefunden is None:
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                ergebnis[d_grad.id] = Groesse(math.inf, EINHEITSLOS)
                continue
            M_s_adm_si, ebene, stab = gefunden
            M_Riss = protokoll_rissmoment(p, e, a, werte, brutto, riss, M_y, M_z,
                                          einachsig=self.einachsig,
                                          referenz="SIA 262:2025, 4.4.2")
            M_s_adm = werte.moment("M_s_adm", r"M_{s,adm}", M_s_adm_si, "Widerstand")
            p.wert(M_s_adm, titel="Moment, bei dem der erste gezogene Stab σ_s,adm erreicht")
            protokoll_ebene(p, werte, ebene, self.einachsig)
            gruppe = grenzen.gruppe(stab)
            sigma_s = werte.spannung("sigma_s", r"\sigma_s", ebene.sigma_s[stab])
            p.gleichung(rf"{angabe(sigma_s)} = {angabe(gruppe.wert)}",
                        titel=f"An der Grenze: {staebe[stab].ort}")
            erfuellt = M_s_adm_si >= riss.M_Riss
            p.gleichung(bedingung(angabe(M_s_adm), r"\ge", angabe(M_Riss), erfuellt),
                        titel="Zwängung auf Biegung")
            grad = M_s_adm_si / riss.M_Riss
            grad_formel(p, d_grad, grad, M_s_adm, M_Riss, erfuellt)
            ergebnis[d_grad.id] = Groesse(grad, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                art="ZB", ziel=d_grad.id, fall=name, erfuellt=erfuellt,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung=(f"{staebe[stab].element.name} erreicht σ_s,adm = "
                             f"{gruppe.sigma / 1e6:.0f} N/mm² bei M_s,adm = "
                             f"{M_s_adm_si / 1e3:.1f} kNm {'≥' if erfuellt else '<'} "
                             f"M_Riss = {riss.M_Riss / 1e3:.1f} kNm."),
                einwirkung=M_Riss, widerstand=M_s_adm))
        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung(ergebnis, self.teilurteile(urteile))

    def _an_der_grenze(self, q: Querschnitt, staebe: Sequence[Stabangabe], grenzen: Grenzen,
                       M_y: float, M_z: float, M_start: float
                       ) -> Optional[Tuple[float, Gebrauchsebene, int]]:
        """
        Das Moment ohne Normalkraft, bei dem der erste gezogene Stab seine
        Grenze erreicht -- samt Ebene und Stab. ``None``, wo auf der gezogenen
        Seite des Schwerpunkts kein Stab liegt.

        Bleibt alles linear, ist es ein Dreisatz: die Spannungen wachsen mit
        dem Moment. Gerechnet wird darum bei ``M_start`` und beim
        gedreisatzten Moment; stimmt es dort nicht, weil der Beton ueber
        ``f_ck`` kommt, sucht Illinois weiter. Eine Ebene, die sich nicht
        findet, liegt jenseits der Grenze: der Stahl fliesst dort laengst.
        """
        neigung: List[Optional[float]] = [None]

        def auswertung(M: float):
            # Linear bleibt die Neigung beim Dreisatz dieselbe: von ihr aus.
            ebene = gebrauchsebene(q, N=0.0, M_y=M * M_y, M_z=M * M_z,
                                   einachsig=self.einachsig, start=neigung[0])
            if ebene.konvergiert:
                neigung[0] = ebene.psi
            if not ebene.konvergiert:
                return 1.0, (M, ebene, -1)
            anteile = [(ebene.sigma_s[i] / grenzen.sigma(i), i)
                       for i, eps in enumerate(ebene.eps_s) if eps > 0.0]
            anteil, i = max(anteile) if anteile else (0.0, -1)
            return anteil - 1.0, (M, ebene, i)

        M_a = M_start
        fa, gefunden = auswertung(M_a)
        for _ in range(60):
            if gefunden[1].konvergiert:
                break
            M_a /= 2.0
            fa, gefunden = auswertung(M_a)
        ebene = gefunden[1]
        if not ebene.konvergiert or gefunden[2] < 0:
            return None
        n = (math.cos(ebene.psi), math.sin(ebene.psi))
        sy, sz = q.bezug
        if not any(n[0] * (s.lage[0] - sy) + n[1] * (s.lage[1] - sz) > 0.0 for s in staebe):
            return None
        M_b = M_a / (fa + 1.0)
        fb, gefunden = auswertung(M_b)
        if abs(fb) <= GRENZ_SCHRANKE:
            return gefunden
        # Vom Dreisatz aus weiter, bis die Seite wechselt.
        for _ in range(60):
            if (fa > 0.0) != (fb > 0.0):
                break
            M_a, fa = M_b, fb
            M_b *= 2.0 if fb < 0.0 else 0.5
            fb, gefunden = auswertung(M_b)
        gefunden = illinois(auswertung, M_a, fa, M_b, fb, schranke_x=1e-9 * M_b,
                            schranke_f=GRENZ_SCHRANKE)
        return gefunden if gefunden is not None and gefunden[2] >= 0 else None

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel("Zwängung auf Biegung")
        p.erklaerung(
            "Eine aufgezwungene Krümmung erzeugt beim Reissen ein Moment, das "
            "die Bewehrung übernehmen muss – ohne über die zulässige "
            "Stahlspannung zu kommen. Nicht zu verwechseln mit dem Nachweis "
            "gegen sprödes Versagen: dort steht der Biegewiderstand gegen das "
            "Rissmoment, hier die Stahlspannung gegen ihre Grenze.")
        p.erklaerung(
            "Am gezeichneten Querschnitt je Richtung: dasselbe Rissmoment wie beim "
            "spröden Versagen, gehalten gegen das Moment, bei dem der erste gezogene "
            "Stab seine zulässige Spannung erreicht. Das Rissmoment gehört dem "
            "ungerissenen Bruttoquerschnitt, das Moment der Bewehrung dem gerissenen – "
            "elastisch, ohne Normalkraft, mit der Kriechzahl dieses Nachweises; die "
            "gedrückte Bewehrung wirkt mit.")
        p.ansatz(r"\max_i \frac{\sigma_{s,i}(M_{s,adm})}{\sigma_{s,adm,i}} = 1"
                 r"\qquad M_{s,adm} \ge M_{Riss}",
                 titel="Zwängung auf Biegung, je Stab", referenz="SIA 262:2025, 4.4.2",
                 name="Moment der Bewehrung bei zulässiger Stahlspannung")
        protokoll_spannung_ungerissen(p, einachsig=self.einachsig)
        protokoll_rechenwahl(p, self.wahl, self.id)
        protokoll_gesetze_nach_wahl(p, e, self.analyse, self.wahl, self.id,
                          titel="Werkstoffgesetze im gerissenen Zustand")
        p.erklaerung(GRENZE_JE_STAB)
