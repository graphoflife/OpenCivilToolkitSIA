"""
opencivil/nachweis/qa_verbund.py -- die Lastfaelle eines Verbundquerschnitts nach SIA 264:2014.

VERANTWORTUNG:
Zwei Nachweise je Lastfall, mit ihrer Herleitung -- gerechnet wird in
:mod:`opencivil.verbund.widerstand`:

* **Biegung und Normalkraft** (:class:`VerbundBiegungQA`): der plastische
  Zustand bei ``N_Ed`` in der Richtung des Moments, mit dem, was grosse
  Querkraft den Blechen nimmt. Er gilt, wo jedes Blech in Klasse 1 oder 2
  liegt und gezogener Betonstahl in der Duktilitaetsklasse B oder C ist
  (5.1.2.3); mit ``β`` fuer S420 und S460 (5.1.2.2). Die Herleitung zeigt
  die Probe wie im Stahl (:func:`~opencivil.nachweis.qa_stahl.probe`).
* **Querkraft** (:class:`VerbundQuerkraftQA`): wie im Stahl, denn der Stahl
  traegt sie allein (4.3.2.2). ``V_Rd`` lesen beide aus den Kennzahlen
  (:mod:`opencivil.nachweis.qa_verbund_kennzahlen`).

WAS FEHLT -- GRAU:
* Wo plastisch nicht gerechnet werden darf
  (:attr:`~opencivil.verbund.widerstand.Fall.grund`): elastisch nach 5.1.2.4
  und 5.1.2.5 rechnet das Werkzeug noch nicht.
* Torsion: ein ``T_Ed`` steht in der Einwirkung, nachgewiesen wird es nicht
  (nach Vorgabe, nicht nachgeschlagen).
* Die Verduebelung, Knicken und Kippen gehoeren dem Traeger.

VORZEICHEN:
N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt der
Analyse.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.latex import als_text
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.qa_stahl import (
    JENSEITS, StahlQuerkraftQA, einwirkung, minderung, probe, querkraefte,
)
from opencivil.nachweis.qa_verbund_kennzahlen import (
    REFERENZ_14, REFERENZ_ZUG, VOLLE_VERDUEBELUNG, KennzahlenVerbundQA,
)
from opencivil.nachweis.qa_verbund_werte import (
    MIT_BETA, Verbundwerte, beta, klasse_text, klassen, stoffbezuege,
)
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.stahlbau import widerstand as wd
from opencivil.verbund import widerstand as vw

#: Warum Torsion nicht nachgewiesen wird -- siehe Dateikopf.
OHNE_TORSION = ("Torsion weist das Werkzeug beim Verbundquerschnitt nicht nach (nach Vorgabe, "
                "nicht nachgeschlagen).")


def _bezuege(analyse: Querschnittsanalyse,
             kennzahlen: KennzahlenVerbundQA) -> List[Eingabebezug]:
    """Schwerpunkt, Kennwerte der Materialien und die Querkraftwiderstaende der Kennzahlen."""
    return ([Eingabebezug("y_S", analyse.id_von("y_S")), Eingabebezug("z_S", analyse.id_von("z_S"))]
            + stoffbezuege(kennzahlen.verbund)
            + [Eingabebezug(f"V_{r}_Rd", kennzahlen.d[f"V_{r}_Rd"].id)
               for r in kennzahlen.richtungen])


class VerbundBiegungQA(Nachweis):
    """Biegung und Normalkraft eines Verbundquerschnitts, je Lastfall -- siehe Dateikopf."""

    THEMA = "Verbundquerschnitt"
    LANGNAME = "Biegung und Normalkraft"
    ART = "M-N"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 kennzahlen: KennzahlenVerbundQA) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.kennzahlen = kennzahlen
        self.verbund = kennzahlen.verbund
        basis = f"{analyse.id}.nachweis.verbund"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Biegung und Normalkraft – {f.name}",
                             vw.REFERENZ_PLASTISCH)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=_bezuege(analyse, kennzahlen),
                         titel=f"Biegung und Normalkraft – {analyse.name}",
                         referenz="SIA 264:2014, 5.1.2", abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        werte = Verbundwerte(self.verbund, e, self.analyse.wahl)
        bezug = (e.g("y_S").si * 1e3, e.g("z_S").si * 1e3)
        self._ansatz(p, werte)
        urteile = [self._ein_fall(p, werte, bezug, fall, self._rechnen(e, werte, bezug, fall))
                   for fall in self.lastfaelle]
        return Ausfuehrung({}, urteile)

    def _rechnen(self, e: Eingaben, werte: Verbundwerte, bezug: Tuple[float, float],
                 fall: Lastfall) -> Optional[vw.Fall]:
        """Der Lastfall am Querschnitt -- ``None`` ohne Normalkraft und Moment."""
        biegung = self.analyse.biegung
        M_y, M_z = biegung.wirkt(fall.M_y, fall.M_z)
        if fall.N == 0.0 and biegung.betrag(M_y, M_z) * 1e3 <= wd.KEIN_MOMENT:
            return None
        kraefte = querkraefte(e, self.verbund.stahl, self.kennzahlen, self.analyse, fall)
        return vw.rechnen(self.verbund, werte.zug, werte.druck, werte.eps, fall.N, M_y * 1e3,
                          M_z * 1e3, kraefte, bezug, biegung, werte.hochfest)

    def _ansatz(self, p: Protokoll, werte: Verbundwerte) -> None:
        p.erklaerung(
            "Je Lastfall der plastische Zustand bei N_Ed, dessen Moment in die Richtung der "
            "Einwirkung zeigt: Baustahl und Betonstahl ganz gezogen oder ganz gedrückt, der Beton "
            "nur gedrückt, mit 0.85 f_cd über die ganze Druckzone. Er gilt, wenn jedes Blech an "
            "seiner Nulllinie in Klasse 1 oder 2 liegt und gezogener Betonstahl in der "
            "Duktilitätsklasse B oder C ist. Grosse Querkraft mindert die Bleche, in denen sie "
            "steht, wie im Stahl. Die Normalkraft bleibt, das Moment wächst in seiner Richtung, "
            "bis der Widerstand erreicht ist.")
        p.annahme(VOLLE_VERDUEBELUNG)
        p.annahme("Die Klasse an der plastischen Nulllinie des Lastfalls – nach Vorgabe, nicht "
                  "nachgeschlagen: die Norm sagt nicht, bei welcher Laststufe α gilt.")
        p.text(werte.kurz())
        p.ansatz(r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}",
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")

    def _ein_fall(self, p: Protokoll, werte: Verbundwerte, bezug: Tuple[float, float],
                  fall: Lastfall, x: Optional[vw.Fall]) -> NachweisUrteil:
        zwischen = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        einwirkung(p, self.analyse, fall, torsion=OHNE_TORSION)
        if x is None:
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        minderung(p, zwischen, x.querkraefte, x.abgemindert, self.verbund.stahl,
                  referenz=vw.REFERENZ_QUERKRAFT)
        N_Ed = zwischen.kraft("N_Ed", "N_{Ed}", fall.N)
        if x.alpha_N is not None:
            p.text(JENSEITS)
            return self._normalkraft(p, zwischen, x, N_Ed, d_grad, fall,
                                     "N_Ed jenseits der reinen Normalkraft.")
        _, wer = klassen(p, x.zustaende, x.freie, "Bleche im Lastfall")
        if x.grund:
            p.hinweis(x.grund)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, x.grund)
        p.wert(zwischen.zahl("klasse", r"\mathrm{QK}", float(x.klasse), stellen=0),
               titel=f"Querschnittsklasse – massgebend {wer}" if wer else "Querschnittsklasse",
               referenz=vw.REFERENZ_KLASSE)
        if x.ohne_moment:
            return self._normalkraft(p, zwischen, x, N_Ed, d_grad, fall, "Reine Normalkraft.")
        return self._plastisch(p, zwischen, x, bezug, d_grad, fall)

    def _normalkraft(self, p: Protokoll, zwischen: Zwischenwerte, x: vw.Fall, N_Ed: Wert,
                     d_grad: WertDef, fall: Lastfall, text: str) -> NachweisUrteil:
        """Ohne Moment, oder wo die Normalkraft allein nicht traegt: ``N_Ed`` gegen ``N_pl,Rd``."""
        zug = x.N > 0.0
        N_Rd = zwischen.kraft("N_Rd", "N_{pl,Rd}^{+}" if zug else "N_{pl,Rd}^{-}",
                              x.starr.zugkraft if zug else -x.starr.druckkraft)
        p.wert(N_Rd, titel=f"{'Zug' if zug else 'Druck'}widerstand, Σ f A je Werkstoff",
               referenz=REFERENZ_ZUG if zug else REFERENZ_14)
        v = Vergleich(N_Ed, N_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, text)

    def _plastisch(self, p: Protokoll, zwischen: Zwischenwerte, x: vw.Fall,
                   bezug: Tuple[float, float], d_grad: WertDef,
                   fall: Lastfall) -> NachweisUrteil:
        M_Ed = zwischen.moment("M_Ed", "M_{Ed}", x.moment / 1e3)
        pl = x.plastisch
        M_Rd = probe(p, zwischen, x.starr.bloecke(pl.linie), self.verbund.namen, bezug,
                     self.analyse.biegung, pl,
                     titel="Kräfte im plastischen Zustand – je Teil und Zone",
                     referenz=vw.REFERENZ_PLASTISCH, symbol=r"M_{pl,Rd}")
        b = beta(p, zwischen, x.beta) if x.beta is not None else None
        if b is not None:
            M_pl = M_Rd
            M_Rd = zwischen.moment("M_Rd_beta", r"M_{Rd}", b.groesse.si * M_pl.groesse.si)
            p.formel(M_Rd, r"@beta \cdot @M", {"beta": b, "M": M_pl},
                     titel="Plastischer Momentenwiderstand, mit β gemindert",
                     referenz=vw.REFERENZ_BETA, name=MIT_BETA)
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v,
                           f"Plastisch, Klasse {klasse_text(x.klasse)}, bei N_Ed = "
                           f"{x.N / 1e3:.1f} kN.")


class VerbundQuerkraftQA(StahlQuerkraftQA):
    """Die Querkraft eines Verbundquerschnitts, je Lastfall: wie im Stahl -- siehe Dateikopf."""

    THEMA = "Verbundquerschnitt"
    REFERENZ = vw.REFERENZ_SCHUB
