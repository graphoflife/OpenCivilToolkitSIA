"""
opencivil/nachweis/qa_verbund.py -- die Lastfaelle eines Verbundquerschnitts nach SIA 264:2014.

VERANTWORTUNG:
Die Nachweise je Lastfall, mit ihrer Herleitung -- gerechnet wird in
:mod:`opencivil.verbund.widerstand` und :mod:`opencivil.verbund.duebel`:

* **Biegung und Normalkraft** (:class:`VerbundBiegungQA`): der plastische
  Zustand bei ``N_Ed`` in der Richtung des Moments, mit dem, was grosse
  Querkraft den Blechen nimmt. Er gilt, wo jedes Blech in Klasse 1 oder 2
  liegt und gezogener Betonstahl in der Duktilitaetsklasse B oder C ist
  (5.1.2.3); mit ``β`` fuer S420 und S460 (5.1.2.2). Tragen die
  Kopfbolzenduebel weniger, als der gedrueckte Beton bei voller
  Verduebelung braucht, mit Teilverduebelung (6.1.1.6). Die Herleitung
  zeigt die Probe wie im Stahl (:func:`~opencivil.nachweis.qa_stahl.probe`).
* **Verduebelung**, im selben Nachweis, wo Kopfbolzenduebel gewaehlt sind:
  der Verduebelungsgrad ``η = N/N_f`` gegen (29) -- gegen eins im Bereich
  negativer Momente (:func:`~opencivil.verbund.duebel.negativ`) oder wo das
  Profil nicht doppelsymmetrisch ist. ``P_Rd`` steht in den Kennzahlen.
* **Querkraft** (:class:`VerbundQuerkraftQA`): wie im Stahl, denn der Stahl
  traegt sie allein (4.3.2.2). ``V_Rd`` lesen beide aus den Kennzahlen
  (:mod:`opencivil.nachweis.qa_verbund_kennzahlen`).

WAS FEHLT -- GRAU:
* Wo plastisch nicht gerechnet werden darf
  (:attr:`~opencivil.verbund.widerstand.Fall.grund`): elastisch nach 5.1.2.4
  und 5.1.2.5 rechnet das Werkzeug noch nicht. Die Verduebelung folgt dem
  plastischen Zustand: wo er nicht gilt, steht sie nicht da.
* Einem Lastfall die Zahl seiner Duebel -- Biegung und Normalkraft rechnen
  dann mit voller Verduebelung --, oder ``L_e``, wo (29) es braucht.
* Torsion: ein ``T_Ed`` steht in der Einwirkung, nachgewiesen wird es nicht
  (nach Vorgabe, nicht nachgeschlagen).
* Knicken und Kippen gehoeren dem Traeger, ebenso der Laengsschub in der
  Platte (5.1.4) und die Regeln der Durchbildung (7.1).

VORZEICHEN:
N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt der
Analyse.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.einheiten import M, Groesse
from opencivil.core.latex import als_text
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Ausgang, Nachweis, NachweisUrteil,
    Vergleich, grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.qa_stahl import (
    JENSEITS, StahlQuerkraftQA, einwirkung, minderung, probe, querkraefte,
)
from opencivil.nachweis.qa_verbund_kennzahlen import REFERENZ_14, REFERENZ_ZUG, KennzahlenVerbundQA
from opencivil.nachweis.qa_verbund_werte import (
    MIT_BETA, Verbundwerte, beta, klasse_text, klassen, stoffbezuege,
)
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.querschnitt.plastisch import Starrplastisch
from opencivil.stahlbau import widerstand as wd
from opencivil.verbund import duebel as vd
from opencivil.verbund import widerstand as vw

#: Warum Torsion nicht nachgewiesen wird -- siehe Dateikopf.
OHNE_TORSION = ("Torsion weist das Werkzeug beim Verbundquerschnitt nicht nach (nach Vorgabe, "
                "nicht nachgeschlagen).")

#: Wie die Verduebelung in die Lastfaelle eingeht -- ohne Duebel und mit.
VOLL_ANGENOMMEN = ("Verdübelung voll angenommen, wie 5.1.2.1 es tut: Stahl und Beton tragen "
                   "zusammen, ohne Schlupf. Die Dübel prüft das Werkzeug, wo in der Kachel "
                   "«Verdübelung» Kopfbolzendübel gewählt sind.")
MIT_DUEBELN = ("Bis zum Momentennullpunkt tragen die N Dübel eines Lastfalls N · P_Rd. Ist das "
               "weniger als die Kraft, die Beton und Betonstahl ausserhalb der Profile bei voller "
               "Verdübelung zusammen haben, rechnet der Fall mit Teilverdübelung (6.1.1.6): sie "
               "tragen dann nur N · P_Rd, und Stahl und Beton haben je ihre eigene Nulllinie. Am "
               "Momentennullpunkt trägt der Beton nichts (nach Vorgabe, nicht nachgeschlagen).")

#: Was einem Lastfall fuer die Verduebelung fehlen kann -- grau.
OHNE_ANZAHL = ("Für diesen Lastfall fehlt noch die Zahl der Dübel bis zum Momentennullpunkt – "
               "Biegung und Normalkraft rechnen mit voller Verdübelung.")
OHNE_L_E = "Für (29) fehlt diesem Lastfall noch L_e, der Abstand der Momentennullpunkte."
OHNE_MOMENT = ("Ohne Moment prüft das Werkzeug die Dübel nicht: (29) gilt dem Längsschub aus "
               "Biegung bis zum Momentennullpunkt (nach Vorgabe, nicht nachgeschlagen).")

#: Warum volle Verduebelung verlangt ist, wo (29) nicht gilt.
NEGATIV = ("Im Bereich negativer Momente lässt 6.1.1.6 keine Teilverdübelung zu: verlangt ist "
           "volle Verdübelung. Das Werkzeug sieht ihn, wo Beton und Betonstahl ausserhalb der "
           "Profile zusammen gezogen sind oder das Moment die Seite des Betons zieht (nach "
           "Vorgabe, nicht nachgeschlagen).")
KAMMER = ("Kammerbeton zählt zum Stahl: er ist mit dem Steg verbunden (5.2.1.2), nicht über "
          "die Dübel in der Fuge (nach Vorgabe, nicht nachgeschlagen).")
UNSYMMETRISCH = ("(29) gilt für doppelsymmetrische Stahlprofile; für diesen Baustahl nennt die "
                 "Norm keine Grenze. Verlangt ist darum volle Verdübelung (nach Vorgabe, nicht "
                 "nachgeschlagen).")

REFERENZ_TEIL = "SIA 264:2014, 6.1.1.6; 5.1.2.1"


def _bezuege(analyse: Querschnittsanalyse,
             kennzahlen: KennzahlenVerbundQA) -> List[Eingabebezug]:
    """Schwerpunkt, Kennwerte der Materialien und was die Kennzahlen fuer die Faelle haben."""
    lesen = [f"V_{r}_Rd" for r in kennzahlen.richtungen]
    if kennzahlen.duebel is not None:
        lesen.append("P_Rd")
    return ([Eingabebezug("y_S", analyse.id_von("y_S")), Eingabebezug("z_S", analyse.id_von("z_S"))]
            + stoffbezuege(kennzahlen.verbund)
            + [Eingabebezug(k, kennzahlen.d[k].id) for k in lesen])


class VerbundBiegungQA(Nachweis):
    """Biegung und Normalkraft eines Verbundquerschnitts, je Lastfall -- siehe Dateikopf."""

    THEMA = "Verbundquerschnitt"
    LANGNAME = "Biegung und Normalkraft"
    ART = "M-N"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 kennzahlen: KennzahlenVerbundQA,
                 abschnitte: Optional[Mapping[str, vd.Abschnitt]] = None) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.kennzahlen = kennzahlen
        self.verbund = kennzahlen.verbund
        self.duebel = kennzahlen.duebel
        self.abschnitte = dict(abschnitte or {})
        """Je Lastfall, was er ueber die Duebel weiss -- mit seinem Namen."""

        basis = f"{analyse.id}.nachweis.verbund"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Biegung und Normalkraft – {f.name}",
                             vw.REFERENZ_PLASTISCH)
            for f in self.lastfaelle}
        self.d_duebel: Dict[str, WertDef] = {} if self.duebel is None else {
            f.name: grad_def(f"{basis}.{f.kennung}.verduebelung",
                             rf"\alpha_{{eff,\eta,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Verdübelung – {f.name}", vd.REFERENZ_GRAD)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=[*self.d_ausnutzung.values(), *self.d_duebel.values()],
                         bezuege=_bezuege(analyse, kennzahlen),
                         titel=f"Biegung und Normalkraft – {analyse.name}",
                         referenz="SIA 264:2014, 5.1.2; 6.1.1", abschnitt=analyse.abschnitt)

    def _abschnitt(self, fall: Lastfall) -> vd.Abschnitt:
        return self.abschnitte.get(fall.name, vd.Abschnitt())

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        werte = Verbundwerte(self.verbund, e, self.analyse.wahl)
        bezug = (e.g("y_S").si * 1e3, e.g("z_S").si * 1e3)
        self._ansatz(p, werte)
        urteile: List[NachweisUrteil] = []
        for fall in self.lastfaelle:
            urteile += self._ein_fall(p, e, werte, bezug, fall)
        return Ausfuehrung({}, urteile)

    def _rechnen(self, e: Eingaben, werte: Verbundwerte, bezug: Tuple[float, float],
                 fall: Lastfall) -> Optional[vw.Fall]:
        """Der Lastfall am Querschnitt -- ``None`` ohne Normalkraft und Moment."""
        biegung = self.analyse.biegung
        M_y, M_z = biegung.wirkt(fall.M_y, fall.M_z)
        if fall.N == 0.0 and biegung.betrag(M_y, M_z) * 1e3 <= wd.KEIN_MOMENT:
            return None
        kraefte = querkraefte(e, self.verbund.stahl, self.kennzahlen, self.analyse, fall)
        anzahl = self._abschnitt(fall).anzahl
        duebel = (anzahl * e.g("P_Rd").si if self.duebel is not None and anzahl is not None
                  else None)
        return vw.rechnen(self.verbund, werte.zug, werte.druck, werte.eps, fall.N, M_y * 1e3,
                          M_z * 1e3, kraefte, bezug, biegung, werte.hochfest, duebel)

    def _ansatz(self, p: Protokoll, werte: Verbundwerte) -> None:
        p.erklaerung(
            "Je Lastfall der plastische Zustand bei N_Ed, dessen Moment in die Richtung der "
            "Einwirkung zeigt: Baustahl und Betonstahl ganz gezogen oder ganz gedrückt, der Beton "
            "nur gedrückt, mit 0.85 f_cd über die ganze Druckzone. Er gilt, wenn jedes Blech an "
            "seiner Nulllinie in Klasse 1 oder 2 liegt und gezogener Betonstahl in der "
            "Duktilitätsklasse B oder C ist. Grosse Querkraft mindert die Bleche, in denen sie "
            "steht, wie im Stahl. Die Normalkraft bleibt, das Moment wächst in seiner Richtung, "
            "bis der Widerstand erreicht ist.")
        p.annahme(VOLL_ANGENOMMEN if self.duebel is None else MIT_DUEBELN)
        if self.duebel is not None and self.verbund.fuge[1]:
            p.annahme(KAMMER)
        p.annahme("Die Klasse an der plastischen Nulllinie des Lastfalls – nach Vorgabe, nicht "
                  "nachgeschlagen: die Norm sagt nicht, bei welcher Laststufe α gilt.")
        p.text(werte.kurz())
        p.ansatz(r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}",
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")

    def _ein_fall(self, p: Protokoll, e: Eingaben, werte: Verbundwerte,
                  bezug: Tuple[float, float], fall: Lastfall) -> List[NachweisUrteil]:
        x = self._rechnen(e, werte, bezug, fall)
        zwischen = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        einwirkung(p, self.analyse, fall, torsion=OHNE_TORSION)
        if x is None:
            p.text(OHNE_EINWIRKUNG)
            return [self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)]
        minderung(p, zwischen, x.querkraefte, x.abgemindert, self.verbund.stahl,
                  referenz=vw.REFERENZ_QUERKRAFT)
        N_Ed = zwischen.kraft("N_Ed", "N_{Ed}", fall.N)
        if x.alpha_N is not None:
            p.text(JENSEITS)
            return [self._normalkraft(p, zwischen, x, N_Ed, d_grad, fall,
                                      "N_Ed jenseits der reinen Normalkraft.")]
        _, wer = klassen(p, x.zustaende, x.freie, "Bleche im Lastfall, mit Teilverdübelung"
                         if x.teil is not None else "Bleche im Lastfall")
        if x.grund:
            p.hinweis(x.grund)
            return [self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, x.grund)]
        p.wert(zwischen.zahl("klasse", r"\mathrm{QK}", float(x.klasse), stellen=0),
               titel=f"Querschnittsklasse – massgebend {wer}" if wer else "Querschnittsklasse",
               referenz=vw.REFERENZ_KLASSE)
        if x.ohne_moment:
            if self.duebel is not None:
                p.text(OHNE_MOMENT)
            return [self._normalkraft(p, zwischen, x, N_Ed, d_grad, fall, "Reine Normalkraft.")]
        return self._plastisch(p, e, werte, zwischen, x, bezug, d_grad, fall)

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

    def _plastisch(self, p: Protokoll, e: Eingaben, werte: Verbundwerte,
                   zwischen: Zwischenwerte, x: vw.Fall, bezug: Tuple[float, float],
                   d_grad: WertDef, fall: Lastfall) -> List[NachweisUrteil]:
        M_Ed = zwischen.moment("M_Ed", "M_{Ed}", x.moment / 1e3)
        pl = x.plastisch
        # Mit Duebeln je Seite der Fuge: was in der Kammer liegt, steht fuer sich.
        teile = (None if self.duebel is None
                 else self.verbund.getrennt(werte.zug, werte.druck, x.abgemindert.stahl))
        bloecke = (x.starr.bloecke(pl.linie) if teile is None
                   else [*teile[1].bloecke(pl.linie), *teile[0].bloecke(pl.linie)])
        M_Rd = probe(p, zwischen, bloecke, self.verbund.namen, bezug,
                     self.analyse.biegung, pl,
                     titel="Kräfte im plastischen Zustand – je Teil und Zone"
                           + (", volle Verdübelung" if self.duebel is not None else ""),
                     referenz=vw.REFERENZ_PLASTISCH, symbol=r"M_{pl,Rd}")
        weitere: List[NachweisUrteil] = []
        if teile is not None:
            urteil, M_teil = self._verduebelung(p, e, werte, zwischen, x, bezug, fall, teile)
            weitere.append(urteil)
            if M_teil is not None:
                M_Rd = M_teil
        b = beta(p, zwischen, x.beta) if x.beta is not None else None
        if b is not None:
            M_pl = M_Rd
            M_Rd = zwischen.moment("M_Rd_beta", r"M_{Rd}", b.groesse.si * M_pl.groesse.si)
            p.formel(M_Rd, r"@beta \cdot @M", {"beta": b, "M": M_pl},
                     titel="Plastischer Momentenwiderstand, mit β gemindert",
                     referenz=vw.REFERENZ_BETA, name=MIT_BETA)
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        wie = "Teilverdübelt" if x.teil is not None else "Plastisch"
        return [self.urteil(d_grad, fall.name, v,
                            f"{wie}, Klasse {klasse_text(x.klasse)}, bei N_Ed = "
                            f"{x.N / 1e3:.1f} kN."), *weitere]

    # -- Verduebelung -------------------------------------------------------------

    def _verduebelung(self, p: Protokoll, e: Eingaben, werte: Verbundwerte,
                      zwischen: Zwischenwerte, x: vw.Fall, bezug: Tuple[float, float],
                      fall: Lastfall, teile: Tuple[Starrplastisch, Starrplastisch],
                      ) -> Tuple[NachweisUrteil, Optional[Wert]]:
        """
        ``η`` gegen (29) oder eins -- und mit Teilverduebelung ihr
        Momentenwiderstand (siehe Dateikopf). ``teile``: Beton und Stahl je
        auf ihrer Seite der Fuge.
        """
        d_grad = self.d_duebel[fall.name]
        anzahl = self._abschnitt(fall).anzahl

        def urteil(ausgang: Ausgang, text: str) -> NachweisUrteil:
            return self.urteil(d_grad, fall.name, ausgang, text, art="Dübel",
                               langname="Verdübelung")

        p.titel("Verdübelung", ebene=4)
        gedrueckt = x.N_c < 0.0
        N_c = zwischen.kraft("N_c_f", "N_{c,f}", abs(x.N_c),
                             "Kraft in Beton und Betonstahl ausserhalb der Profile, bei voller "
                             "Verdübelung")
        p.formel(N_c, r"\left|\sum F_{i}\right|_{\mathrm{Beton,\ Betonstahl}}", {},
                 titel="Beton und Betonstahl ausserhalb der Profile bei voller Verdübelung, "
                       "zusammen " + ("gedrückt" if gedrueckt else "gezogen"),
                 name="Kraft im Beton bei voller Verdübelung")
        if anzahl is None:
            p.hinweis(OHNE_ANZAHL)
            return urteil(NICHT_FUEHRBAR, OHNE_ANZAHL), None
        if x.N_c == 0.0:
            text = ("Ausserhalb der Profile tragen Beton und Betonstahl nichts: die Dübel "
                    "bleiben ohne Längsschub.")
            p.text(text)
            return urteil(UNBESCHRAENKT, text), None
        P_Rd = e["P_Rd"]
        N = zwischen.zahl("N", "N", float(anzahl),
                          "Dübel zwischen dem Schnitt und dem Momentennullpunkt", stellen=0)
        p.wert(N, titel="Dübel bis zum Momentennullpunkt, wie angegeben")
        N_f = zwischen.zahl("N_f", "N_f", abs(x.N_c) / P_Rd.groesse.si,
                            "Dübel für volle Verdübelung", stellen=2)
        p.formel(N_f, r"\frac{@N_c}{@P}", {"N_c": N_c, "P": P_Rd},
                 titel="Dübel für volle Verdübelung", referenz=vd.REFERENZ_GRAD,
                 name="Dübel für volle Verdübelung")
        eta = zwischen.zahl("eta", r"\eta", anzahl / N_f.groesse.si, "Verdübelungsgrad")
        p.formel(eta, r"\frac{@N}{@N_f}", {"N": N, "N_f": N_f}, titel="Verdübelungsgrad",
                 referenz=vd.REFERENZ_GRAD, name="Verdübelungsgrad")
        verlangt = self._verlangt(p, werte, zwischen, x, self._abschnitt(fall))
        if verlangt is None:
            ausgang: Ausgang = NICHT_FUEHRBAR
            text = OHNE_L_E
        else:
            ausgang = Vergleich(verlangt, eta)
            ausgang.zeile(p, d_grad)
            text = f"η = {eta.groesse.si:.2f}, verlangt {verlangt.groesse.si:.2f}."
        if x.teil is None:
            return urteil(ausgang, text), None
        return urteil(ausgang, text), self._teilverduebelt(p, x, bezug, fall, N, P_Rd, teile)

    def _verlangt(self, p: Protokoll, werte: Verbundwerte, zwischen: Zwischenwerte,
                  x: vw.Fall, abschnitt: vd.Abschnitt) -> Optional[Wert]:
        """Der kleinste Verduebelungsgrad: nach (29) oder eins -- ``None``, wo ``L_e`` fehlt."""
        negativ = vd.negativ(x.plastisch.linie.n, self.verbund.zum_beton, x.N_c)
        if negativ or not self.verbund.doppelsymmetrisch:
            p.text(NEGATIV if negativ else UNSYMMETRISCH)
            eins = zwischen.zahl("eta_min", r"\eta_{min}", 1.0, "Verlangter Verdübelungsgrad")
            p.wert(eins, titel="Volle Verdübelung verlangt", referenz=vd.REFERENZ_VOLL)
            return eins
        if abschnitt.L_e is None:
            p.hinweis(OHNE_L_E)
            return None
        L_e = zwischen.wert("L_e", "L_e", Groesse(abschnitt.L_e, M), 1,
                            "Abstand der Momentennullpunkte")
        f_y_zahl = werte.stahl.zahl(self.verbund.stahl.teile[0].gruppe, "f_y")
        f_y = zwischen.spannung("f_y", "f_y", f_y_zahl * 1e6, "Fliessgrenze des Profils")
        eta_min = zwischen.zahl("eta_min", r"\eta_{min}", vd.eta_min(f_y_zahl, abschnitt.L_e),
                                "Kleinster Verdübelungsgrad")
        if abschnitt.L_e > vd.L_E_BIS:
            p.wert(eta_min, titel=f"L_e über {vd.L_E_BIS:g} m: volle Verdübelung verlangt",
                   referenz=vd.REFERENZ_GRAD)
        else:
            p.formel(eta_min, r"\max\left(1 - \frac{355\ \mathrm{N}/\mathrm{mm}^{2}}{@f_y} \cdot "
                              r"\left(0.75 - 0.03 \cdot @L_e\right);\ 0.4\right)",
                     {"f_y": f_y, "L_e": L_e}, titel="Kleinster Verdübelungsgrad, Profil "
                                                     "doppelsymmetrisch",
                     referenz=vd.REFERENZ_GRAD, empirisch={"L_e": M},
                     name="Kleinster Verdübelungsgrad")
        return eta_min

    def _teilverduebelt(self, p: Protokoll, x: vw.Fall, bezug: Tuple[float, float],
                        fall: Lastfall, N: Wert, P_Rd: Wert,
                        teile: Tuple[Starrplastisch, Starrplastisch]) -> Wert:
        """Der Momentenwiderstand mit Teilverduebelung, mit seiner Probe."""
        p.titel("Teilverdübelung", ebene=4)
        teil = Zwischenwerte(f"{self.id}.{fall.kennung}.teil")
        F = teil.kraft("F_D", "F_D", x.duebel,
                       "Was die Dübel bis zum Momentennullpunkt tragen")
        p.formel(F, r"@N \cdot @P", {"N": N, "P": P_Rd},
                 titel="Was die Dübel tragen – weniger als N_c,f", referenz=REFERENZ_TEIL,
                 name="Was die Dübel tragen")
        stahl = "der Stahl mit dem Kammerbeton" if self.verbund.fuge[1] else "der Baustahl"
        p.text(f"Beton und Betonstahl ausserhalb der Profile tragen zusammen nur diese Kraft, "
               f"{stahl} den Rest von N_Ed; jeder Teil hat seine eigene Nulllinie, beide mit "
               "derselben Zugrichtung.")
        beton, baustahl = teile
        bloecke = [*baustahl.bloecke(x.teil.stahl), *beton.bloecke(x.teil.beton)]
        return probe(p, teil, bloecke, self.verbund.namen, bezug, self.analyse.biegung, x.teil,
                     titel="Kräfte mit Teilverdübelung – je Teil und Zone",
                     referenz=REFERENZ_TEIL, symbol=r"M_{Rd}")


class VerbundQuerkraftQA(StahlQuerkraftQA):
    """Die Querkraft eines Verbundquerschnitts, je Lastfall: wie im Stahl -- siehe Dateikopf."""

    THEMA = "Verbundquerschnitt"
    REFERENZ = vw.REFERENZ_SCHUB
