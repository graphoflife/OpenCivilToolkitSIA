"""
opencivil/nachweis/qa_verbund_kennzahlen.py -- was ein Verbundquerschnitt aufnimmt, ohne Einwirkung.

VERANTWORTUNG:
Die Kennzahlen eines Querschnitts aus Baustahl und Beton nach SIA 264:2014,
wie die des Stahls (:mod:`opencivil.nachweis.qa_stahl_kennzahlen`) --
gerechnet immer, ob es Lastfaelle gibt oder nicht:

* die Festigkeiten je Werkstoff
  (:func:`~opencivil.nachweis.qa_verbund_werte.festigkeiten`);
* der Zugwiderstand: Baustahl und Betonstahl, der Beton traegt keinen Zug
  (4.3.2.1);
* der Druckwiderstand ohne Knicken wie (14), wo jedes Blech bei Druck in
  Klasse 1 oder 2 liegt;
* je Zugseite der plastische Momentenwiderstand bei ``N = 0`` mit voller
  Verduebelung (5.1.2.1), mit ``β`` nach 5.1.2.2 -- gerechnet in
  :mod:`opencivil.verbund.widerstand`;
* mit Profilen der Querkraftwiderstand: ihn traegt der Stahl allein
  (4.3.2.2), wie im Stahlquerschnitt;
* mit Kopfbolzenduebeln ihr Schubwiderstand ``P_Rd`` (6.1.2.1) -- gerechnet
  in :mod:`opencivil.verbund.duebel`. Mehrere Betone: (30) mit dem, der am
  wenigsten traegt (nach Vorgabe, nicht nachgeschlagen). Wie viele Duebel
  ein Lastfall braucht, sagt sein Nachweis.

WAS FEHLT -- GRAU IN DER HERLEITUNG:
Wo ein Widerstand plastisch nicht gilt -- ein Blech ueber Klasse 2,
gezogener Betonstahl ohne Duktilitaetsklasse B oder C, ``x_p/h`` ueber 0.4
--, steht er auf null, und ein Satz sagt, warum: elastisch nach 5.1.2.4
rechnet das Werkzeug noch nicht. Die Momentenwiderstaende gelten mit
voller Verduebelung; was die Duebel eines Lastfalls erlauben, rechnet sein
Nachweis. Knicken und Kippen gehoeren dem Traeger.
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from opencivil.core.berechnung import Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import KN, KNM, Groesse
from opencivil.material.basis import Baustoffart
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.nachweis.qa_stahl import MOMENT_UM, krafttabelle, momentsummen
from opencivil.nachweis.qa_stahl_kennzahlen import querkraft
from opencivil.nachweis.qa_verbund_werte import (
    MIT_BETA, SPANNUNG, Verbundwerte, beta, festigkeiten, klassen, stoffbezuege,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.plastisch import DRUCK
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stabwerk.stabquerschnitt import keine_hauptachsen
from opencivil.stahlbau.querschnitt import normale
from opencivil.verbund import duebel as vd
from opencivil.verbund import widerstand as vw
from opencivil.verbund.querschnitt import Verbundquerschnitt

REFERENZ_ZUG = "SIA 264:2014, 4.3.2.1; 5.1.2.1"
REFERENZ_14 = "SIA 264:2014, 5.3.2.4, (14)"

#: (14) als Ansatz und sein Name -- die Verbundstuetze schreibt ihn auch.
ANSATZ_14 = r"N_{pl,Rd} = A_a\, f_{yd} + A_c\, 0.85\, f_{cd} + A_s\, f_{sd}"
NAME_14 = "Plastischer Normalkraftwiderstand im Verbund"

#: Was in den Kennzahlen fehlt, wo ein Widerstand plastisch nicht gilt -- siehe Dateikopf.
AUF_NULL = "Der Widerstand steht darum auf null."

#: Die Annahme hinter den Momentenwiderstaenden der Kennzahlen -- und mit Duebeln der Satz dazu.
VOLLE_VERDUEBELUNG = ("Gerechnet mit voller Verdübelung, wie 5.1.2.1 es annimmt: Stahl und Beton "
                      "tragen zusammen, ohne Schlupf.")
MIT_DUEBELN = "Was die Dübel eines Lastfalls erlauben, rechnet sein Nachweis."


def _achse(seite: Zugseite) -> str:
    """Um welche Achse ein Moment diese Seite zieht."""
    return "y" if seite.um_y else "z"


def verbund_von(analyse: Querschnittsanalyse) -> Verbundquerschnitt:
    """Der Verbundquerschnitt einer Analyse: ihre Flaechen und ihre Bewehrung."""
    return Verbundquerschnitt(analyse.flaechen, analyse.eltern, analyse.bewehrungselemente)


class KennzahlenVerbundQA(Kennzahlprozedur):
    """Die Kennzahlen eines Verbundquerschnitts -- siehe Dateikopf."""

    THEMA = "Kennzahlen"

    def __init__(self, analyse: Querschnittsanalyse,
                 duebel: Optional[vd.Kopfbolzen] = None) -> None:
        self.analyse = analyse
        self.verbund = verbund_von(analyse)
        self.stahl = self.verbund.stahl
        self.duebel = duebel
        """Die Kopfbolzenduebel -- ``None``: volle Verduebelung angenommen, ohne Duebel."""
        basis = f"{analyse.id}.kennzahlen"
        dazu = self.anlegen(basis)
        dazu("N_Rd_zug", r"N_{pl,Rd}^{+}", KN, "Zugwiderstand des Verbundquerschnitts",
             "Zugwiderstand", "Baustahl und Betonstahl – der Beton trägt keinen Zug",
             referenz=REFERENZ_ZUG)
        dazu("N_Rd_druck", r"N_{pl,Rd}^{-}", KN,
             "Druckwiderstand des Verbundquerschnitts, ohne Knicken", "Druckwiderstand",
             "plastisch, ohne Knicken – null, wo ein Blech über Klasse 2 liegt",
             referenz=REFERENZ_14)
        for seite in analyse.zugseiten:
            dazu(f"M_Rd_{seite.value}", rf"M_{{{_achse(seite)},Rd}}^{{{seite.zeichen}}}", KNM,
                 f"Plastischer Momentenwiderstand bei N = 0, {seite.beschriftung}",
                 f"Momentenwiderstand, {seite.beschriftung}",
                 "plastisch, volle Verdübelung, ohne Kippen – null, wo er so nicht gilt",
                 referenz=vw.REFERENZ_PLASTISCH)
        # Querkraft tragen nur Profile; in y nur, wo auch um z gebogen wird.
        self.richtungen = ([] if not self.stahl.profile
                           else ["z", "y"] if Zugseite.LINKS in analyse.zugseiten else ["z"])
        for r in self.richtungen:
            dazu(f"V_{r}_Rd", rf"V_{{{r},Rd}}", KN, f"Querkraftwiderstand in {r}, Stahl allein",
                 f"Querkraftwiderstand in {r}", "je Profil allein, zusammen – der Stahl allein",
                 referenz=vw.REFERENZ_SCHUB)
        if duebel is not None:
            dazu("P_Rd", r"P_{Rd}", KN, "Schubwiderstand eines Kopfbolzendübels", "Dübelwiderstand",
                 "der kleinere aus Betonstauchung und Versagen des Dübels",
                 referenz=vd.REFERENZ_P_RD)

        bezuege = ([Eingabebezug(k, analyse.id_von(k))
                    for k in ("y_S", "z_S", "I_y", "I_z", "I_yz")]
                   + stoffbezuege(self.verbund))
        if duebel is not None:
            bezuege += [self.verbund.gruppen[g].stoff.bezug("E_cm")
                        for g in self.verbund.gruppen_der(Baustoffart.BETON)]
        super().__init__(basis, bezuege=bezuege, titel=f"Kennzahlen – {analyse.name}",
                         abschnitt=analyse.abschnitt)

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was der Verbundquerschnitt aufnimmt, ohne Bezug auf einen Lastfall: die "
            "Widerstände gegen Zug, Druck und Biegung, plastisch nach SIA 264, und mit Profilen "
            "gegen Querkraft – die trägt der Stahl allein (4.3.2.2). Mit Kopfbolzendübeln dazu, "
            "was einer trägt. Knicken und Kippen gehören dem Träger und sind hier nicht dabei.")
        ergebnis: Dict[str, Groesse] = {}
        werte = Verbundwerte(self.verbund, e, self.analyse.wahl)
        bezug = (e.g("y_S").si * 1e3, e.g("z_S").si * 1e3)
        self._hinweise(p, e)
        p.titel("Festigkeiten", ebene=3)
        festigkeiten(p, werte)
        self._normalkraft(p, werte, ergebnis)
        for seite in self.analyse.zugseiten:
            self._biegung(p, werte, ergebnis, seite, bezug)
        if self.richtungen:
            querkraft(p, werte.stahl, self.stahl, self.richtungen,
                      lambda r, V: self._belegen(ergebnis, f"V_{r}_Rd", V))
        if self.duebel is not None:
            self._duebel(p, e, ergebnis, self.duebel)
        return ergebnis

    # -- Kopfbolzenduebel ---------------------------------------------------------

    def _duebel(self, p: Protokoll, e: Eingaben, ergebnis: Dict[str, Groesse],
                k: vd.Kopfbolzen) -> None:
        """``P_Rd`` nach (30) und (31) -- siehe Dateikopf."""
        p.titel("Kopfbolzendübel", ebene=3)
        zwischen = Zwischenwerte(f"{self.id}.duebel")
        p.text(f"Kopfbolzendübel ⌀{k.d:g} mm, h_D = {k.h:g} mm – mindestens 4 d = "
               f"{vd.LAENGE_IN_D * k.d:g} mm: verformungsfähig ({vd.REFERENZ_LAENGE}).")
        d = zwischen.laenge("d", "d", k.d * 1e-3, "Schaftdurchmesser des Kopfbolzendübels")
        gamma_v = zwischen.zahl("gamma_v", r"\gamma_v", vd.GAMMA_V,
                                "Widerstandsbeiwert der Verdübelung")
        p.wert(gamma_v, titel="Widerstandsbeiwert, auch mit charakteristischen Werten",
               referenz="SIA 264:2014, 6.1.2.1")
        betone = self.verbund.gruppen_der(Baustoffart.BETON)
        werte = {g: (e[self.verbund.gruppen[g].stoff.eingabename("f_ck")],
                     e[self.verbund.gruppen[g].stoff.eingabename("E_cm")]) for g in betone}
        g = min(betone, key=lambda g: werte[g][0].groesse.si * werte[g][1].groesse.si)
        f_ck, E_cm = werte[g]
        if len(betone) > 1:
            p.text(f"Mehrere Betone: (30) mit {self.verbund.gruppen[g].name}, der am wenigsten "
                   f"trägt (nach Vorgabe, nicht nachgeschlagen).")
        P_c = zwischen.kraft("P_Rd_c", r"P_{Rd,c}",
                             k.betonstauchung(f_ck.groesse.si / 1e6, E_cm.groesse.si / 1e6),
                             "Schubwiderstand, Betonstauchung")
        p.formel(P_c, r"\frac{0.29 \cdot @d^{2}}{@g} \cdot \sqrt{@f_ck \cdot @E_cm}",
                 {"d": d, "g": gamma_v, "f_ck": f_ck, "E_cm": E_cm},
                 titel=f"Betonstauchung, {self.verbund.gruppen[g].name}",
                 referenz="SIA 264:2014, 6.1.2.1, (30)",
                 name="Schubwiderstand eines Kopfbolzendübels – Betonstauchung")
        if k.f_u > vd.F_U_HOECHSTENS:
            p.text(f"f_u = {k.f_u:g} N/mm² angegeben; (31) rechnet mit höchstens "
                   f"{vd.F_U_HOECHSTENS:g} N/mm² (6.1.2.1).")
        f_u = zwischen.spannung("f_u", "f_u", k.f_u_wirksam * 1e6,
                                "Zugfestigkeit des Dübels, höchstens 500 N/mm²")
        P_s = zwischen.kraft("P_Rd_s", r"P_{Rd,s}", k.schaft(),
                             "Schubwiderstand, Versagen des Dübels")
        p.formel(P_s, r"\frac{0.8 \cdot @f_u}{@g} \cdot \frac{\pi \cdot @d^{2}}{4}",
                 {"f_u": f_u, "d": d, "g": gamma_v}, titel="Versagen des Dübels",
                 referenz="SIA 264:2014, 6.1.2.1, (31)",
                 name="Schubwiderstand eines Kopfbolzendübels – Versagen des Dübels")
        p.formel(self._belegen(ergebnis, "P_Rd", min(P_c.groesse.si, P_s.groesse.si)),
                 r"\min\left(@c;\ @s\right)", {"c": P_c, "s": P_s},
                 titel="Schubwiderstand eines Kopfbolzendübels", referenz=vd.REFERENZ_P_RD)

    def _hinweise(self, p: Protokoll, e: Eingaben) -> None:
        freie = self.stahl.freie
        if freie:
            namen = ", ".join(f"«{t.flaeche.name}»" for t in freie)
            p.hinweis(f"Frei gezeichnet aus Baustahl: {namen}. Wie diese Flächen gehalten sind, "
                      "weiss das Werkzeug nicht: wo sie gedrückt sind, liegen sie über Klasse 2, "
                      "und der Verbundquerschnitt rechnet dort nicht plastisch. Querkraft tragen "
                      "nur Profile.")
        text = keine_hauptachsen(
            f"Querschnittsanalyse «{self.analyse.name}»",
            *(e.g(k).si for k in ("I_y", "I_z", "I_yz")), was="den Querschnitt",
            folge="Die Widerstände gelten mit der Nulllinie parallel zu y oder z und sind "
                  "darum nur genähert.")
        if text:
            p.hinweis(text)
        p.annahme(VOLLE_VERDUEBELUNG if self.duebel is None
                  else f"{VOLLE_VERDUEBELUNG} {MIT_DUEBELN}")

    # -- Normalkraft --------------------------------------------------------------

    def _summe(self, p: Protokoll, werte: Verbundwerte, ergebnis: Dict[str, Groesse],
               kurz: str, festigkeit: Sequence[float], *, vorzeichen: float, titel: str,
               referenz: str) -> None:
        """``Σ f A`` je Werkstoff als Tabelle, die Summe als Kennzahl."""
        flaechen = self.verbund.flaechen_je_gruppe()
        p.tabelle(
            kopf=["Werkstoff", Mathe(r"A\ [\mathrm{mm}^2]"), Mathe("f" + SPANNUNG),
                  Mathe(r"f\, A\ [\mathrm{kN}]")],
            zeilen=[[gruppe.name, Mathe(fest(A, 0)), Mathe(fest(f, 1)),
                     Mathe(fest(f * A * 1e-3, 1))]
                    for gruppe, A, f in zip(self.verbund.gruppen, flaechen, festigkeit)],
            titel=f"{titel}: je Werkstoff", ausrichtung="lrrr")
        summe = vorzeichen * sum(f * A for f, A in zip(festigkeit, flaechen))
        p.wert(self._belegen(ergebnis, kurz, summe), titel=f"{titel}, zusammen",
               referenz=referenz)

    def _normalkraft(self, p: Protokoll, werte: Verbundwerte,
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Normalkraft", ebene=3)
        p.text("Der Beton trägt keinen Zug; die Fläche des Betons ist ohne das, was Stahl und "
               "Stäbe in ihm einnehmen.")
        self._summe(p, werte, ergebnis, "N_Rd_zug", werte.zug, vorzeichen=1.0,
                    titel="Zugwiderstand", referenz=REFERENZ_ZUG)
        klasse, wer = klassen(p, self.verbund.zustaende(DRUCK, werte.eps),
                              self.verbund.freie_gedrueckt(DRUCK), "Bleche bei Druck")
        if klasse > 2:
            p.hinweis(f"{vw.UEBER_KLASSE_2} Massgebend: {wer}. {AUF_NULL}")
            p.wert(self._belegen(ergebnis, "N_Rd_druck", 0.0), titel="Druckwiderstand")
            return
        p.ansatz(ANSATZ_14, titel="Plastischer Normalkraftwiderstand, Teil für Teil",
                 referenz=REFERENZ_14, name=NAME_14)
        self._summe(p, werte, ergebnis, "N_Rd_druck", werte.druck, vorzeichen=-1.0,
                    titel=f"Druckwiderstand in Klasse {klasse}", referenz=REFERENZ_14)

    # -- Biegung ----------------------------------------------------------------------

    def _biegung(self, p: Protokoll, werte: Verbundwerte, ergebnis: Dict[str, Groesse],
                 seite: Zugseite, bezug) -> None:
        p.titel(f"Biegung, {seite.beschriftung}", ebene=3)
        zwischen = Zwischenwerte(f"{self.id}.{seite.value}")
        x = vw.biegewiderstand(self.verbund, werte.zug, werte.druck, werte.eps, seite, bezug,
                               werte.hochfest)
        n = normale(seite)
        quer = "z" if seite.um_y else "y"
        p.wert(zwischen.laenge(f"{quer}_pl", rf"{quer}_{{pl}}", x.linie.v * (n[0] + n[1]) * 1e-3,
                               "Lage der plastischen Nulllinie"),
               titel="Plastische Nulllinie bei N = 0: so viel Kraft gezogen wie gedrückt")
        klassen(p, x.zustaende, x.freie, f"Bleche bei Biegung, {seite.beschriftung}")
        kurz = f"M_Rd_{seite.value}"
        if x.grund:
            p.hinweis(f"{x.grund} {AUF_NULL}")
            p.wert(self._belegen(ergebnis, kurz, 0.0), titel="Momentenwiderstand")
            return
        bloecke = x.starr.bloecke(x.linie)
        krafttabelle(p, zwischen, bloecke, self.verbund.namen, x.plastisch.linien,
                     titel=f"Kräfte im plastischen Zustand, {seite.beschriftung}")
        achse = _achse(seite)
        M = momentsummen(bloecke, bezug)[achse]
        M_pl = zwischen.moment(f"M_{achse}_int", f"M_{{{achse},pl,Rd}}", M,
                               "Plastischer Momentenwiderstand, ohne β")
        p.formel(M_pl, MOMENT_UM[achse], {}, titel=f"Probe: Moment um {achse}")
        b = beta(p, zwischen, x.beta) if x.beta is not None else None
        if b is None:
            p.wert(self._belegen(ergebnis, kurz, M),
                   titel=f"Plastischer Momentenwiderstand, {seite.beschriftung}",
                   referenz=vw.REFERENZ_PLASTISCH)
            return
        p.formel(self._belegen(ergebnis, kurz, b.groesse.si * M), r"@beta \cdot @M",
                 {"beta": b, "M": M_pl}, titel="Plastischer Momentenwiderstand, mit β gemindert",
                 referenz=vw.REFERENZ_BETA, name=MIT_BETA)
