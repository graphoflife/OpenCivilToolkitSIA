"""
opencivil/nachweis/qa_blechverbund.py -- eine Blechverbunddecke nach SIA 264:2014, 5.4.

VERANTWORTUNG:
Was eine Querschnittsanalyse mit einer Blechverbunddecke rechnet -- ihr
Beton, ihr Profilblech, Betonstahl darin --, mit Herleitung; gerechnet wird
in :mod:`opencivil.verbund.blechdecke`, die Form des Blechs kennt
:mod:`opencivil.querschnitt.profilblech`:

* die Kennzahlen (:class:`KennzahlenBlechQA`): die Festigkeiten, die Form
  des Blechs mit ``d_p`` und ``b_0`` (Figur 18), Zug- und Druckwiderstand,
  der plastische Momentenwiderstand bei Zug unten und bei Zug oben
  (5.4.3.2), der Querkraftwiderstand (26) und der Laengsschubwiderstand nach
  der m-k-Methode (28) und die Schlankheit ``L/d_p`` (5.4.4.3);
* je Lastfall Biegung und Normalkraft (:class:`BlechBiegungQA`): der
  plastische Zustand bei ``N_Ed``, dessen Moment die Seite von ``M_y,Ed``
  zieht;
* je Lastfall Querkraft und Laengsschub (:class:`BlechSchubQA`): ``V_z,Ed``
  gegen die Widerstaende der Kennzahlen.

DIE DECKE TRAEGT IN EINER RICHTUNG (5.4.1.1):
entlang ihrer Rippen. Gerechnet wird einachsig um y, mit ``N``, ``M_y`` und
``V_z`` fuer die ganze gezeichnete Breite ``b = n·b_s``; ``M_z``, ``V_y`` und
``T`` eines Lastfalls weist das Werkzeug nicht nach.

WAS FEHLT -- GRAU:
``d_p`` ueber 150 mm, wo (26) auf SIA 262 verweist; eine Angabe zum
Laengsschub; die Durchbiegung, wo ``L/d_p`` ueber 26 liegt. Was das Werkzeug
an der Decke gar nicht rechnet, nennt die Herleitung der Kennzahlen
(:data:`NICHT_GERECHNET`).

VORZEICHEN:
N > 0 Zug; M_y > 0 zieht unten -- um den Schwerpunkt der Analyse.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, M, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.material.basis import Baustoff
from opencivil.nachweis.qa_stahl import (
    JENSEITS, MOMENT_UM, einwirkung, krafttabelle, momentsummen, probe,
)
from opencivil.nachweis.qa_verbund_kennzahlen import verbund_von
from opencivil.nachweis.qa_verbund_werte import SPANNUNG, Verbundwerte, festigkeiten, stoffbezuege
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.querschnitt.biegung import EINACHSIG
from opencivil.querschnitt.gesetzwahl import Werkstoffsatz
from opencivil.querschnitt.plastisch import Block, Starrplastisch
from opencivil.querschnitt.profilblech import Profilblech
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import widerstand as wd
from opencivil.verbund import blechdecke as bd
from opencivil.verbund.duebel import GAMMA_V

#: Was eine Blechverbunddecke traegt -- siehe Dateikopf.
EINE_RICHTUNG = ("Eine Blechverbunddecke trägt in Richtung ihrer Rippen (5.4.1.1): nachgewiesen "
                 "werden N, M_y und V_z über die ganze gezeichnete Breite b – M_z, V_y und T "
                 "nicht.")
OHNE_TORSION = ("Torsion weist das Werkzeug bei der Blechverbunddecke nicht nach: sie trägt in "
                "Richtung ihrer Rippen (5.4.1.1).")

#: Was das Werkzeug an der Decke nicht rechnet.
NICHT_GERECHNET = ("Nicht gerechnet: das Durchstanzen unter Einzellasten (27), die Endverankerung "
                   "(5.4.3.6), der Bauzustand (5.4.4.4), die Mindestbewehrung über den Stützen "
                   "(5.4.4.6) und die Schwingungen (5.4.4.7).")

#: Warum bei negativem Moment das Blech fehlt -- und was folgt, wo dann nichts Zug traegt.
OHNE_BLECH = "Bei negativem Moment zählt das Blech nicht, auch gezogen nicht (5.4.3.2)."
OHNE_ZUG = ("Nichts trägt hier Zug: der Beton nicht, das Blech zählt bei negativem Moment nicht "
            "(5.4.3.2), und Betonstahl liegt keiner in der Decke. Der Widerstand ist null.")
GEGENRICHTUNG = ("Bei dieser Normalkraft zeigt selbst das grösste Moment, das die Decke mit dieser "
                 "Zugseite trägt, in die Gegenrichtung: in Richtung der Einwirkung trägt sie "
                 "keines. Der Widerstand ist null.")

#: Die Dicke des Blechs (:mod:`opencivil.querschnitt.profilblech`).
DICKE = ("Das Blech ist gleich dick, seine Fläche gleichmässig über die Abwicklung verteilt; "
         "Sicken und Ausrundungen zählen nicht (nach Vorgabe, nicht nachgeschlagen).")

#: (26) mit charakteristischen Werten.
TAU_BEMESSUNG = ("τ_cd bleibt ein Bemessungswert, auch wo die Tragsicherheit den Beton "
                 "charakteristisch rechnet: (26) nennt nur ihn (nach Vorgabe, nicht "
                 "nachgeschlagen).")

#: Wo die Angaben zum Laengsschub stehen.
KACHEL = "in der Kachel «Längsschub»"

#: Die Namen der Formeln in der Formelsammlung -- in jeder Fassung derselbe.
RIPPENBREITE = "Rippenbreite einer Blechverbunddecke"
SCHUBLAENGE = "Schublänge einer Blechverbunddecke"

#: Die Seiten, die ein Moment der Decke zieht -- unten mit dem Blech, oben ohne (5.4.3.2).
SEITEN = (Zugseite.UNTEN, Zugseite.OBEN)


def _stellen(zahl: float, hoechstens: int = 4) -> int:
    """So viele Stellen, wie die eingegebene Zahl hat -- sie wird nicht gerundet gezeigt."""
    for stellen in range(hoechstens):
        if abs(round(zahl, stellen) - zahl) < 1e-12:
            return stellen
    return hoechstens


def _bezug(e: Eingaben) -> Tuple[float, float]:
    """Der Schwerpunkt der Analyse in mm -- der Bezugspunkt der Momente."""
    return e.g("y_S").si * 1e3, e.g("z_S").si * 1e3


class KennzahlenBlechQA(Kennzahlprozedur):
    """Die Kennzahlen einer Blechverbunddecke -- siehe Dateikopf."""

    THEMA = "Blechverbunddecke"

    def __init__(self, analyse: Querschnittsanalyse, blech: Profilblech,
                 laengsschub: bd.Laengsschub) -> None:
        self.analyse = analyse
        self.verbund = verbund_von(analyse)
        self.blech = blech
        self.form = blech.form
        self.laengsschub = laengsschub
        self.beton: Baustoff = next(f.stoff for f in analyse.flaechen
                                    if f.kennung == blech.kennung)
        """Der Beton der Decke -- die Flaeche mit der Kennung ihres Blechs."""

        basis = f"{analyse.id}.kennzahlen"
        dazu = self.anlegen(basis)
        dazu("N_Rd_zug", r"N_{pl,Rd}^{+}", KN, "Zugwiderstand der Blechverbunddecke",
             "Zugwiderstand", "Blech und Betonstahl – der Beton trägt keinen Zug",
             referenz=bd.REFERENZ_BIEGUNG)
        dazu("N_Rd_druck", r"N_{pl,Rd}^{-}", KN,
             "Druckwiderstand der Blechverbunddecke, ohne Knicken", "Druckwiderstand",
             "Beton und Betonstahl – das Blech zählt gedrückt nicht", referenz=bd.REFERENZ_BIEGUNG)
        for seite in SEITEN:
            dazu(f"M_Rd_{seite.value}", rf"M_{{y,Rd}}^{{{seite.zeichen}}}", KNM,
                 f"Plastischer Momentenwiderstand bei N = 0, {seite.beschriftung}",
                 f"Momentenwiderstand, {seite.beschriftung}",
                 "plastisch, mit dem Blech" if seite is Zugseite.UNTEN
                 else "plastisch, ohne das Blech (5.4.3.2)", referenz=bd.REFERENZ_BIEGUNG)
        if self.form.d_p <= bd.D_P_BIS:
            dazu("V_Rd", r"V_{Rd}", KN, "Querkraftwiderstand der Decke über ihre Breite b",
                 "Querkraftwiderstand", "(26) über die ganze Breite b",
                 referenz=bd.REFERENZ_QUERKRAFT)
        if not laengsschub.fehlt:
            dazu("V_L_Rd", r"V_{L,Rd}", KN, "Längsschubwiderstand nach der m-k-Methode",
                 "Längsschubwiderstand", "zwischen Blech und Beton, über die ganze Breite b",
                 referenz=bd.REFERENZ_LAENGSSCHUB)
        if laengsschub.L is not None:
            dazu("L_d_p", r"L/d_p", EINHEITSLOS, "Schlankheit der Decke", "Schlankheit",
                 f"bis {bd.SCHLANKHEIT:g} muss die Durchbiegung nicht gerechnet werden",
                 referenz=bd.REFERENZ_SCHLANKHEIT)

        bezuege = ([Eingabebezug(k, analyse.id_von(k)) for k in ("y_S", "z_S")]
                   + stoffbezuege(self.verbund) + [self.beton.bezug("tau_cd")])
        super().__init__(basis, bezuege=bezuege, titel=f"Kennzahlen – {analyse.name}",
                         abschnitt=analyse.abschnitt)

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was die Blechverbunddecke aufnimmt, ohne Bezug auf einen Lastfall: die Widerstände "
            "gegen Zug, Druck und Biegung, plastisch wie im Verbundträger, gegen Querkraft und "
            "gegen den Längsschub zwischen Blech und Beton nach der m-k-Methode – alle über die "
            "ganze gezeichnete Breite b. Dazu die Schlankheit L/d_p: bis 26 muss die "
            "Durchbiegung nicht gerechnet werden.")
        ergebnis: Dict[str, Groesse] = {}
        werte = Verbundwerte(self.verbund, e, self.analyse.wahl)
        p.annahme(EINE_RICHTUNG)
        p.titel("Festigkeiten", ebene=3)
        festigkeiten(p, werte)
        form = self._form(p)
        self._normalkraft(p, werte, ergebnis)
        for seite in SEITEN:
            self._biegung(p, werte, ergebnis, seite, _bezug(e))
        self._querkraft(p, e, form, ergebnis)
        self._laengsschub(p, form, ergebnis)
        self._schlankheit(p, form, ergebnis)
        p.hinweis(NICHT_GERECHNET)
        return ergebnis

    def _form(self, p: Protokoll) -> Dict[str, Wert]:
        """Die Form des Blechs als Tabelle, ``d_p`` und ``b_0`` als Formeln -- siehe Dateikopf."""
        f = self.form
        z = Zwischenwerte(f"{self.id}.blech")
        w = {
            "h": z.laenge("h", "h", f.h * 1e-3, "Dicke der Decke"),
            "b_s": z.laenge("b_s", "b_s", f.b_s * 1e-3, "Rippenabstand"),
            "b_o": z.laenge("b_o", "b_o", f.b_o * 1e-3, "Breite einer Rippe oben"),
            "b_u": z.laenge("b_u", "b_u", f.b_u * 1e-3, "Breite einer Rippe unten"),
            "L_w": z.laenge("L_w", "L_w", f.L_w * 1e-3, "Länge eines Stegs"),
            "s": z.laenge("s", "s", f.s * 1e-3, "Abgewickelte Länge des Blechs je Rippe"),
            "t": z.laenge("t", "t", f.t * 1e-3, "Dicke des Blechs", stellen=2),
            "e": z.laenge("e", "e", f.e * 1e-3, "Schwerpunkt des Blechs über seiner Unterkante"),
            "h_c": z.laenge("h_c", "h_c", f.h_c * 1e-3, "Beton über den Rippen"),
            "b": z.laenge("b", "b", f.breite * 1e-3, "Breite der Decke, n · b_s"),
            "A_p": z.flaeche("A_p", "A_p", f.flaeche * 1e-6, "Fläche des Blechs über die Breite b"),
        }
        p.titel("Profilblech", ebene=3)
        p.text(f"{f.rippen} Rippen im Abstand b_s = {f.b_s:g} mm, "
               f"{'hinterschnitten' if f.hinterschnitten else 'offen'}; h = {f.h:g} mm, "
               f"h_p = {f.h_p:g} mm, b_o = {f.b_o:g} mm, b_u = {f.b_u:g} mm, "
               f"A_p = {f.A_p:g} mm² je m nach dem Datenblatt.")
        p.ansatz(r"L_w = \sqrt{h_p^2 + \left(\frac{b_o - b_u}{2}\right)^2} \qquad "
                 r"s = b_s - b_o + 2\, L_w + b_u \qquad t = \frac{A_p\, b_s}{s} \qquad "
                 r"e = \frac{h_p\, (L_w + b_s - b_o)}{s}",
                 titel="Das Blech je Rippe: Steg, Abwicklung, Dicke und Schwerpunkt",
                 name="Kennwerte eines Profilblechs")
        p.tabelle(kopf=["Grösse", "Bedeutung", "Wert"],
                  zeilen=[[Mathe(w[k].symbol), w[k].beschreibung, Mathe(w[k].zahl_latex())]
                          for k in ("L_w", "s", "t", "e", "h_c", "b", "A_p")],
                  titel="Das Blech aus seinen Massen", ausrichtung="llr")
        p.annahme(DICKE)
        d_p = z.laenge("d_p", "d_p", f.d_p * 1e-3, "Statische Höhe der Decke")
        p.formel(d_p, "@h - @e", {"h": w["h"], "e": w["e"]},
                 titel="Statische Höhe – bis zum Schwerpunkt des Blechs",
                 referenz=bd.REFERENZ_STATISCHE_HOEHE,
                 name="Statische Höhe einer Blechverbunddecke")
        b_0 = z.laenge("b_0", "b_0", f.b_0 * 1e-3, "Rippenbreite")
        if f.hinterschnitten:
            p.formel(b_0, "@b_o", {"b_o": w["b_o"]},
                     titel="Rippenbreite, hinterschnitten: oben, wo die Rippe am schmalsten ist",
                     referenz=bd.REFERENZ_FORM, name=RIPPENBREITE)
        else:
            p.formel(b_0, r"\frac{@b_o + @b_u}{2}", {"b_o": w["b_o"], "b_u": w["b_u"]},
                     titel="Rippenbreite, offen: auf halber Höhe der Rippe",
                     referenz=bd.REFERENZ_FORM, name=RIPPENBREITE)
        return {**w, "d_p": d_p, "b_0": b_0}

    # -- Normalkraft und Biegung ----------------------------------------------------

    def _normalkraft(self, p: Protokoll, werte: Verbundwerte,
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Normalkraft", ebene=3)
        verbund = self.verbund
        flaechen = verbund.flaechen_je_gruppe()
        p.tabelle(
            kopf=["Werkstoff", Mathe(r"A\ [\mathrm{mm}^2]"),
                  Mathe(r"\text{gezogen}" + SPANNUNG), Mathe(r"\text{gedrückt}" + SPANNUNG)],
            zeilen=[[gruppe.name, Mathe(fest(A, 0)), Mathe(fest(zug, 1)), Mathe(fest(druck, 1))]
                    for gruppe, A, zug, druck in zip(verbund.gruppen, flaechen, werte.zug,
                                                     werte.druck)],
            titel="Fläche und Festigkeit je Werkstoff", ausrichtung="lrrr")
        p.text("Die Fläche des Betons ist ohne die Stäbe in ihm; das Blech liegt an seinem Rand.")
        p.wert(self._belegen(ergebnis, "N_Rd_zug",
                             sum(f * A for f, A in zip(werte.zug, flaechen))),
               titel="Zugwiderstand: Σ A · f gezogen", referenz=bd.REFERENZ_BIEGUNG)
        p.wert(self._belegen(ergebnis, "N_Rd_druck",
                             -sum(f * A for f, A in zip(werte.druck, flaechen))),
               titel="Druckwiderstand: Σ A · f gedrückt", referenz=bd.REFERENZ_BIEGUNG)

    def _biegung(self, p: Protokoll, werte: Verbundwerte, ergebnis: Dict[str, Groesse],
                 seite: Zugseite, bezug: Tuple[float, float]) -> None:
        p.titel(f"Biegung, {seite.beschriftung}", ebene=3)
        zwischen = Zwischenwerte(f"{self.id}.{seite.value}")
        starr, zustand = bd.plastisch(self.verbund, werte.zug, werte.druck, 0.0,
                                      seite.vorzeichen, bezug)
        if seite is Zugseite.OBEN:
            p.text(OHNE_BLECH)
        kurz = f"M_Rd_{seite.value}"
        bloecke = starr.bloecke(zustand.linie)
        if not _zieht(bloecke):
            p.hinweis(OHNE_ZUG)
            p.wert(self._belegen(ergebnis, kurz, 0.0), titel="Momentenwiderstand")
            return
        krafttabelle(p, zwischen, bloecke, self.verbund.namen, zustand.linien,
                     titel=f"Kräfte im plastischen Zustand, {seite.beschriftung}")
        M = momentsummen(bloecke, bezug)["y"]
        M_pl = zwischen.moment("M_y_int", r"M_{y,pl,Rd}", M, "Plastischer Momentenwiderstand")
        p.formel(M_pl, MOMENT_UM["y"], {}, titel="Probe: Moment um y")
        p.wert(self._belegen(ergebnis, kurz, M),
               titel=f"Plastischer Momentenwiderstand, {seite.beschriftung}",
               referenz=bd.REFERENZ_BIEGUNG)

    # -- Querkraft, Laengsschub, Schlankheit ------------------------------------------

    def _querkraft(self, p: Protokoll, e: Eingaben, form: Dict[str, Wert],
                   ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Querkraft", ebene=3)
        f = self.form
        if "V_Rd" not in self.d:
            p.hinweis(f"d_p = {f.d_p:.1f} mm liegt über {bd.D_P_BIS:g} mm: dann gelten für die "
                      f"Querkraft die Regeln der SIA 262 (5.4.3.3), und die rechnet das Werkzeug "
                      f"für die Decke noch nicht.")
            return
        if self.analyse.wahl.satz(self.beton) is not Werkstoffsatz.BEMESSUNG:
            p.text(TAU_BEMESSUNG)
        z = Zwischenwerte(f"{self.id}.querkraft")
        k_d = z.zahl("k_d", "k_d", bd.K_D, f"Beiwert für d_p bis {bd.D_P_BIS:g} mm", stellen=1)
        tau = e[self.beton.eingabename("tau_cd")]
        V = bd.querkraft(tau.groesse.si / 1e6, f.d_p, f.b_0, f.b_s) * f.breite
        p.formel(self._belegen(ergebnis, "V_Rd", V),
                 r"@k_d \cdot @tau \cdot @d_p \cdot \frac{@b_0}{@b_s} \cdot @b",
                 {"k_d": k_d, "tau": tau, "d_p": form["d_p"], "b_0": form["b_0"],
                  "b_s": form["b_s"], "b": form["b"]},
                 titel="Querkraftwiderstand über die Breite b: (26) mal b",
                 referenz=bd.REFERENZ_QUERKRAFT, name="Querkraftwiderstand einer Blechverbunddecke")

    def _laengsschub(self, p: Protokoll, form: Dict[str, Wert],
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Längsschub – m-k-Methode", ebene=3)
        ls = self.laengsschub
        if ls.fehlt:
            p.hinweis(f"Für den Längsschub fehlt noch {ls.fehlt_in_worten} – {KACHEL}.")
            return
        z = Zwischenwerte(f"{self.id}.laengsschub")
        p.text(f"{ls.feld.erklaerung} {ls.last.erklaerung}")
        if not ls.last.mit_abstand:
            L = z.wert("L", "L", Groesse(ls.L, M), _stellen(ls.L, 3), "Spannweite")
            L_s = z.laenge("L_s", "L_s", ls.L_s * 1e-3, "Schublänge")
            faktor = "" if ls.feld is bd.Feld.EINFELD else rf"{ls.feld.faktor:g} \cdot "
            p.formel(L_s, rf"\frac{{{faktor}@L}}{{4}}", {"L": L},
                     titel=f"Schublänge, gleichmässig verteilt – {ls.feld.beschriftung}",
                     referenz=bd.REFERENZ_SCHUBLAENGE, name=SCHUBLAENGE)
        else:
            L_s = z.laenge("L_s", "L_s", ls.L_s * 1e-3, "Schublänge", stellen=_stellen(ls.L_s))
            p.wert(L_s, titel="Schublänge – der Abstand a der Einzellasten vom nächsten Auflager",
                   referenz=bd.REFERENZ_SCHUBLAENGE)
            if ls.feld is not bd.Feld.EINFELD:
                p.text("Der Abstand a gilt im gleichwertigen Einfeld, wie eingegeben (nach "
                       "Vorgabe, nicht nachgeschlagen).")
        m = z.spannung("m", "m", ls.m * 1e6, "Beiwert m aus Versuchen", stellen=_stellen(ls.m))
        k = z.spannung("k", "k", ls.k * 1e6, "Beiwert k aus Versuchen", stellen=_stellen(ls.k))
        g_v = z.zahl("gamma_v", r"\gamma_v", GAMMA_V, "Widerstandsbeiwert für Verbund", stellen=2)
        p.wert(g_v, titel="Widerstandsbeiwert für Verbund, auch mit charakteristischen Werten",
               referenz=bd.REFERENZ_LAENGSSCHUB)
        f = self.form
        V_L = bd.laengsschub(f.breite, f.d_p, f.flaeche, ls.L_s, ls.m, ls.k)
        p.formel(self._belegen(ergebnis, "V_L_Rd", V_L),
                 r"@b \cdot @d_p \cdot \frac{@m \cdot \frac{@A_p}{@b \cdot @L_s} + @k}{@g}",
                 {"b": form["b"], "d_p": form["d_p"], "m": m, "A_p": form["A_p"],
                  "L_s": L_s, "k": k, "g": g_v},
                 titel="Längsschubwiderstand zwischen Blech und Beton",
                 referenz=bd.REFERENZ_LAENGSSCHUB, name="Längsschubwiderstand nach der m-k-Methode")

    def _schlankheit(self, p: Protokoll, form: Dict[str, Wert],
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Schlankheit", ebene=3)
        L = self.laengsschub.L
        if L is None:
            p.hinweis(f"Für die Schlankheit L/d_p fehlt noch die Spannweite L – {KACHEL}.")
            return
        z = Zwischenwerte(f"{self.id}.schlankheit")
        wert = self._belegen(ergebnis, "L_d_p", L * 1e3 / self.form.d_p)
        p.formel(wert, r"\frac{@L}{@d_p}",
                 {"L": z.wert("L", "L", Groesse(L, M), _stellen(L, 3), "Spannweite"),
                  "d_p": form["d_p"]},
                 titel="Schlankheit der Decke", referenz=bd.REFERENZ_SCHLANKHEIT,
                 name="Schlankheit einer Blechverbunddecke")
        if wert.groesse.si <= bd.SCHLANKHEIT:
            p.text(f"L/d_p ≤ {bd.SCHLANKHEIT:g}: die Durchbiegung muss nicht gerechnet werden "
                   f"(5.4.4.3).")
        else:
            p.hinweis(f"L/d_p liegt über {bd.SCHLANKHEIT:g}: die Durchbiegung ist zu rechnen "
                      f"(5.4.4.2) – das Werkzeug rechnet sie für die Decke noch nicht.")


def _zieht(bloecke: Sequence[Block]) -> bool:
    """Ob im plastischen Zustand etwas Zug traegt -- ohne Zug gibt es kein Moment."""
    return any(b.F > 0.0 for b in bloecke)


class BlechBiegungQA(Nachweis):
    """Biegung und Normalkraft einer Blechverbunddecke, je Lastfall -- siehe Dateikopf."""

    THEMA = "Blechverbunddecke"
    LANGNAME = "Biegung und Normalkraft"
    ART = "M-N"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 kennzahlen: KennzahlenBlechQA) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.verbund = kennzahlen.verbund
        basis = f"{analyse.id}.nachweis.blech"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Biegung und Normalkraft – {f.name}",
                             bd.REFERENZ_BIEGUNG)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=([Eingabebezug(k, analyse.id_von(k)) for k in ("y_S", "z_S")]
                                  + stoffbezuege(self.verbund)),
                         titel=f"Biegung und Normalkraft – {analyse.name}",
                         referenz=bd.REFERENZ_BIEGUNG, abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        werte = Verbundwerte(self.verbund, e, self.analyse.wahl)
        p.erklaerung(
            "Je Lastfall der plastische Zustand bei N_Ed, dessen Moment die Seite von M_y,Ed "
            "zieht – wie im Verbundträger: Blech und Betonstahl ganz gezogen, der Beton nur "
            "gedrückt, mit 0.85 f_cd über die ganze Druckzone. Bei negativem Moment zählt das "
            "Blech nicht. Die Normalkraft bleibt, das Moment wächst, bis der Widerstand "
            "erreicht ist.")
        p.text(werte.kurz())
        p.ansatz(r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M_{Ed} = |M_{y,Ed}|",
                 titel="Erfüllungsgrad bei fester Normalkraft – einachsig um y",
                 referenz=bd.REFERENZ_EINACHSIG)
        return Ausfuehrung({}, [self._ein_fall(p, werte, _bezug(e), fall)
                                for fall in self.lastfaelle])

    def _ein_fall(self, p: Protokoll, werte: Verbundwerte, bezug: Tuple[float, float],
                  fall: Lastfall) -> NachweisUrteil:
        d_grad = self.d_ausnutzung[fall.name]
        zwischen = Zwischenwerte(f"{self.id}.{fall.kennung}")
        p.titel(fall.name, ebene=3)
        einwirkung(p, self.analyse, fall, torsion=OHNE_TORSION)
        moment = abs(fall.M_y) * 1e3
        if fall.N == 0.0 and moment <= wd.KEIN_MOMENT:
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        if fall.M_y < 0.0:
            p.text(OHNE_BLECH)
        starr, zustand = bd.plastisch(self.verbund, werte.zug, werte.druck, fall.N,
                                      fall.M_y * 1e3, bezug)
        if zustand is None:
            p.text(JENSEITS)
            return self._normalkraft(p, zwischen, starr, d_grad, fall,
                                     "N_Ed jenseits der reinen Normalkraft.")
        if moment <= wd.KEIN_MOMENT:
            return self._normalkraft(p, zwischen, starr, d_grad, fall, "Reine Normalkraft.")
        M_Ed = zwischen.moment("M_Ed", "M_{Ed}", moment / 1e3)
        bloecke = starr.bloecke(zustand.linie)
        begruendung = (f"Plastisch, bei N_Ed = {fall.N / 1e3:.1f} kN"
                       + (", ohne das Blech." if fall.M_y < 0.0 else "."))
        if not _zieht(bloecke) and fall.N == 0.0:
            p.hinweis(OHNE_ZUG)
            M_Rd = zwischen.moment("M_Rd", r"M_{pl,Rd}", 0.0)
            begruendung = OHNE_ZUG
        else:
            M_Rd = probe(p, zwischen, bloecke, self.verbund.namen, bezug, EINACHSIG, zustand,
                         titel="Kräfte im plastischen Zustand – je Teil und Zone",
                         referenz=bd.REFERENZ_BIEGUNG, symbol=r"M_{pl,Rd}")
            if zustand.M_y * fall.M_y < 0.0:
                p.hinweis(GEGENRICHTUNG)
                M_Rd = zwischen.moment("M_Rd_richtung", r"M_{Rd}", 0.0)
                begruendung = GEGENRICHTUNG
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, begruendung)

    def _normalkraft(self, p: Protokoll, zwischen: Zwischenwerte, starr: Starrplastisch,
                     d_grad: WertDef, fall: Lastfall, text: str) -> NachweisUrteil:
        """Ohne Moment, oder wo die Normalkraft allein nicht traegt: ``N_Ed`` gegen ``N_pl,Rd``."""
        zug = fall.N > 0.0
        N_Ed = zwischen.kraft("N_Ed", "N_{Ed}", fall.N)
        N_Rd = zwischen.kraft("N_Rd", "N_{pl,Rd}^{+}" if zug else "N_{pl,Rd}^{-}",
                              starr.zugkraft if zug else -starr.druckkraft)
        p.wert(N_Rd, titel=f"{'Zug' if zug else 'Druck'}widerstand, Σ A · f je Werkstoff",
               referenz=bd.REFERENZ_BIEGUNG)
        v = Vergleich(N_Ed, N_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, text)


class BlechSchubQA(Nachweis):
    """Querkraft und Laengsschub einer Blechverbunddecke, je Lastfall -- siehe Dateikopf."""

    THEMA = "Blechverbunddecke"
    LANGNAME = "Querkraft und Längsschub"
    ART = "V"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 kennzahlen: KennzahlenBlechQA) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.kennzahlen = kennzahlen
        basis = f"{analyse.id}.nachweis.blech_schub"
        self.d_querkraft: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.querkraft",
                             rf"\alpha_{{eff,V,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Querkraft – {f.name}", bd.REFERENZ_QUERKRAFT)
            for f in self.lastfaelle}
        self.d_laengsschub: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.laengsschub",
                             rf"\alpha_{{eff,L,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Längsschub – {f.name}", bd.REFERENZ_LAENGSSCHUB)
            for f in self.lastfaelle}
        self.lesen = [k for k in ("V_Rd", "V_L_Rd") if k in kennzahlen.d]
        """Was die Kennzahlen an Widerstaenden haben -- was fehlt, sagen sie selbst."""
        super().__init__(basis, ausgaben=[*self.d_querkraft.values(),
                                          *self.d_laengsschub.values()],
                         bezuege=[Eingabebezug(k, kennzahlen.d[k].id) for k in self.lesen],
                         titel=f"Querkraft und Längsschub – {analyse.name}",
                         referenz="SIA 264:2014, 5.4.3.3; 5.4.3.5", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        p.erklaerung(
            "Je Lastfall die Querkraft V_z,Ed über die ganze Breite der Decke, gegen ihren "
            "Querkraftwiderstand und gegen den Längsschubwiderstand zwischen Blech und Beton – "
            "beide aus den Kennzahlen.")
        urteile: List[NachweisUrteil] = []
        for fall in self.lastfaelle:
            urteile += self._ein_fall(p, e, fall)
        return Ausfuehrung({}, urteile)

    def _ein_fall(self, p: Protokoll, e: Eingaben, fall: Lastfall) -> List[NachweisUrteil]:
        p.titel(fall.name, ebene=3)
        dq, dl = self.d_querkraft[fall.name], self.d_laengsschub[fall.name]

        def querkraft(ausgang, text: str) -> NachweisUrteil:
            return self.urteil(dq, fall.name, ausgang, text, langname="Querkraft")

        def laengsschub(ausgang, text: str) -> NachweisUrteil:
            return self.urteil(dl, fall.name, ausgang, text, art="V_L", langname="Längsschub")

        if fall.V_z == 0.0:
            p.text(OHNE_EINWIRKUNG)
            return [querkraft(UNBESCHRAENKT, OHNE_EINWIRKUNG),
                    laengsschub(UNBESCHRAENKT, OHNE_EINWIRKUNG)]
        zwischen = Zwischenwerte(f"{self.id}.{fall.kennung}")
        V_Ed = zwischen.kraft("V_Ed", r"V_{z,Ed}", abs(fall.V_z))
        p.wert(V_Ed, titel="Querkraft über die ganze Breite der Decke, als Betrag")
        p.titel("Querkraft", ebene=4)
        if "V_Rd" in self.lesen:
            v = Vergleich(V_Ed, e["V_Rd"])
            v.zeile(p, dq)
            urteile = [querkraft(v, f"V_Rd nach (26) über b = {self.kennzahlen.form.breite:g} mm.")]
        else:
            text = (f"d_p über {bd.D_P_BIS:g} mm: für die Querkraft gilt SIA 262, das rechnet das "
                    f"Werkzeug für die Decke noch nicht.")
            p.hinweis(text)
            urteile = [querkraft(NICHT_FUEHRBAR, text)]
        p.titel("Längsschub", ebene=4)
        if "V_L_Rd" in self.lesen:
            v = Vergleich(V_Ed, e["V_L_Rd"])
            v.zeile(p, dl)
            urteile.append(laengsschub(v, "V_L,Rd nach der m-k-Methode (28)."))
        else:
            text = (f"Für den Längsschub fehlt noch "
                    f"{self.kennzahlen.laengsschub.fehlt_in_worten} – {KACHEL}.")
            p.hinweis(text)
            urteile.append(laengsschub(NICHT_FUEHRBAR, text))
        return urteile
