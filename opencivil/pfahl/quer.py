"""
opencivil/pfahl/quer.py -- der äussere Widerstand eines Pfahls quer zu seiner Achse.

VERANTWORTUNG:
Der Nachweis :class:`AeussererQuerwiderstand`, je Kombination, die den Pfahl
quer belastet (:meth:`~.pfahl.Pfahl.quer_belastet`):

* die Querkraft am Kopf gegen den Bemessungswert des äusseren Widerstands
  quer (SIA 267:2013, 9.4.4.2.2, 9.5.2.3)::

      R_tr,k   der kleinste Bruch aus dem Erdwiderstand p_E,k und dem
               Biegewiderstand M_R des Pfahls (:func:`~.erdwiderstand.brueche`)
      R_tr,d = η_a,tr · R_tr,k / γ_M,a     wie (42), mit γ_M,a = 1.4 (49)

* in jeder Tiefe die Bettungskraft der Verläufe gegen den Erdwiderstand
  (9.5.4.5)::

      q_d(z) = |p(z)| · D  ≤  p_E,d(z) = η_a,tr · p_E,k(z) / γ_M,a

Die Verläufe kommen aus der Steifigkeit (:mod:`.steifigkeit`), der
Querschnitt aus dem inneren Widerstand (:mod:`.innen`) -- beide als Befund.

DER BIEGEWIDERSTAND IM BRUCH:
η_i · M_R,k(N / η_i), mit f_ck und f_yk (:func:`~.innen.biegewiderstand`).
Längs des Pfahls liegt N zwischen dem Wert am Kopf und dem am Fuss. Die
Fläche der Widerstände ist konvex, M_R also in N konkav: sein kleinster Wert
liegt an einem der beiden Enden, und mit ihm rechnen alle Gelenke.

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
* γ_M,a = 1.4, nach (49) in der Regel der kleinste Wert; die Norm will R_tr,d
  je Objekt bestimmt haben.
* Der Biegewiderstand charakteristisch mal η_i: 9.4.4.2.2 nennt den
  charakteristischen inneren Widerstand, η_i steht bei (50).
* Die Bettungskraft gegen p_E,d, mit denselben Beiwerten wie R_tr,d.
* Ohne H_Ed kein R_tr: ein Moment allein prüft nur die Bettungskraft.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Befundbezug, Eingabebezug, Eingaben
from opencivil.core.einheiten import KN_PRO_M, M, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import Nachweis, NachweisUrteil, Vergleich, grad_def
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import WertDef
from opencivil.pfahl import buch
from opencivil.pfahl.erdwiderstand import Bruch, Erdwiderstand, Festigkeit, Linie, brueche
from opencivil.pfahl.innen import Innenbefund, biegewiderstand, querschnitt
from opencivil.pfahl.pfahl import Kombination, Kopf, Pfahl
from opencivil.pfahl.steifigkeit import Steifigkeitsbefund, Verlauf
from opencivil.querschnitt.analyse import KENNWERTE, werkstoff
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz
from opencivil.querschnitt.interaktion import Querschnitt

#: Der Widerstandsbeiwert quer zur Achse -- der kleinste, den die Norm zulässt.
GAMMA_M_QUER = 1.4
GAMMA_M_QUER_REFERENZ = "SIA 267:2013, 9.5.2.3.1, (49)"

#: Womit der Pfahl im Bruch biegt: charakteristische Werte, der Beton als Parabel.
WAHL_BRUCH = Rechenwahl(art=Rechenart.PARABEL, satz=Werkstoffsatz.CHARAKTERISTISCH)


@dataclass
class Querfall:
    """Was eine Kombination quer ergab, in SI -- R_tr nur mit H_Ed."""

    grenze: List[float]
    """In jeder Tiefe der Verläufe p_E,d / D: der Erdwiderstand als Druck, wie der Bettungsdruck."""

    R_trk: Optional[float] = None
    R_trd: Optional[float] = None
    bruch: Optional[Bruch] = None


@dataclass
class Querbefund:
    """Je Kombination, nach ihrem Namen, was sie quer ergab -- für das Bild."""

    faelle: Dict[str, Querfall] = field(default_factory=dict)


class AeussererQuerwiderstand(Nachweis):
    """Siehe Dateikopf."""

    THEMA = "Äusserer Pfahlwiderstand quer"
    ART = "R_tr"

    def __init__(self, pfahl: Pfahl, kombinationen: Sequence[Kombination], *,
                 steifigkeit: str, innen: str) -> None:
        self.pfahl = pfahl
        self.kombinationen = [k for k in kombinationen if pfahl.quer_belastet(k)]
        if not self.kombinationen:
            raise ValueError("Der äussere Widerstand quer braucht eine Kombination, die den "
                             "Pfahl quer belastet.")
        basis = f"{pfahl.id}.nachweis.quer"
        self.d_quer: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,tr,{als_text(k.name)}}}",
                             f"Erfüllungsgrad äusserer Widerstand quer – {k.name}")
            for k in self.kombinationen if k.H_Ed.si != 0.0}
        self.d_bettung: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.bettung",
                             rf"\alpha_{{eff,E,{als_text(k.name)}}}",
                             f"Erfüllungsgrad Bettungskraft – {k.name}")
            for k in self.kombinationen}
        namen = ["D", "L", "t_K", "t_w", "gamma_w", "eta_i", "eta_tr"]
        for i, s in enumerate(pfahl.schichten, start=1):
            namen += [f"d_{i}", f"gamma_{i}"] + (
                [f"phi_k_{i}", f"c_k_{i}"] if s.drainiert else [f"s_u_{i}"])
        super().__init__(basis, ausgaben=[*self.d_quer.values(), *self.d_bettung.values()],
                         bezuege=[Eingabebezug(n, pfahl.id_von(n)) for n in namen]
                         + [s.bezug(k) for s in pfahl.stoffe for k in KENNWERTE[s.art]],
                         befunde=[Befundbezug("steifigkeit", steifigkeit),
                                  Befundbezug("innen", innen)],
                         titel=f"Äusserer Widerstand quer – {pfahl.name}",
                         abschnitt=pfahl.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Äusserer Widerstand quer")
        p.erklaerung(
            "Quer zur Achse hält den Pfahl der Boden neben ihm. Gibt der Boden nach, "
            "dreht oder verschiebt sich der ganze Pfahl, oder er knickt in einem Gelenk, "
            "wo das Moment so gross wird, wie er tragen kann. Die Querkraft, bei der das "
            "zuerst geschieht, ist der charakteristische Widerstand quer; der "
            "Bemessungswert folgt wie längs mit η_a und γ_M,a. Dazu darf der Pfahl den "
            "Boden nirgends stärker drücken, als dieser hält: die Bettungskraft aus der "
            "Steifigkeit gegen den Erdwiderstand, in jeder Tiefe.")
        oben = e.g("t_K").si
        unten = oben + e.g("L").si
        erd = self._erdwiderstand(e, p, oben, unten)
        linien = erd.linien(oben, unten)
        self._tabelle(p, linien)
        self._brueche(p)
        steifigkeit: Steifigkeitsbefund = e.befund("steifigkeit")
        verlaeufe = {v.name: v for v in steifigkeit.verlaeufe}
        innen: Innenbefund = e.befund("innen")
        q = querschnitt(innen.masse, [werkstoff(s, e.si_nach_id(), WAHL_BRUCH)
                                      for s in self.pfahl.stoffe])
        befund = Querbefund()
        urteile: List[NachweisUrteil] = []
        for k in self.kombinationen:
            v = verlaeufe[k.name]
            werte = Zwischenwerte(f"{self.id}.{k.kennung}")
            p.titel(f"Äusserer Widerstand quer – {k.name}", ebene=3)
            fall = befund.faelle[k.name] = Querfall(grenze=[])
            if k.name in self.d_quer:
                urteile.append(self._querkraft(e, p, werte, k, v, linien, q, innen, fall))
            else:
                p.text("Ohne Querkraft am Kopf kein Widerstand quer: das Moment allein prüft "
                       "nur die Bettungskraft.")
            urteile.append(self._bettung(e, p, werte, k, v, erd, fall))
        return Ausfuehrung({}, urteile, befund)

    # -- Erdwiderstand ----------------------------------------------------------

    def _erdwiderstand(self, e: Eingaben, p: Protokoll, oben: float,
                       unten: float) -> Erdwiderstand:
        """p_E,k aus den Schichten -- die Erddrücke nur für die Arten, die am Pfahl vorkommen."""
        p.titel("Erdwiderstand", ebene=3)
        profil = self.pfahl.profil(e)
        arten = {self.pfahl.schichten[s.schicht].drainiert for s in profil.stuecke(oben, unten)}
        if True in arten:
            p.ansatz(r"e_p = K_p \cdot \sigma'_v + 2 \cdot c' \cdot \sqrt{K_p} \qquad "
                     r"e_a = \frac{\sigma'_v}{K_p} - \frac{2 \cdot c'}{\sqrt{K_p}} \qquad "
                     r"K_p = \frac{1 + \sin\varphi'}{1 - \sin\varphi'}",
                     titel="Erddruck drainiert, vorne passiv und hinten aktiv: wirksame "
                           "Spannungen, ohne Reibung am Pfahl",
                     referenz=buch.KAP_ERDDRUCK, name="Erddruck am Pfahl drainiert")
        if False in arten:
            p.ansatz(r"e_p = \sigma_v + 2 \cdot s_u \qquad e_a = \sigma_v - 2 \cdot s_u",
                     titel="Erddruck undrainiert, vorne passiv und hinten aktiv: totale "
                           "Spannungen", referenz=buch.KAP_ERDDRUCK_UNDRAINIERT,
                     name="Erddruck am Pfahl undrainiert")
        p.ansatz(r"p_{E,k} = b' \cdot \left(e_p - \max\left(0;\ e_a\right)\right) \qquad "
                 r"b' = 3 \cdot D",
                 titel="Erdwiderstand je Meter Pfahl: vor dem schmalen Pfahl auf der "
                       "dreifachen Breite", referenz=buch.KAP_SCHMAL,
                 name="Erdwiderstand je Meter Pfahl")
        p.annahme("Hinten drückt der Boden aktiv nach, wo e_a positiv ist, sonst klafft ein "
                  "Spalt; beide Drücke wirken auf 3 · D -- nach Vorgabe, nicht nachgeschlagen. "
                  "Das Buch nennt diese Breite für den passiven Druck vor einem schmalen "
                  "Träger. So hebt sich undrainiert σ_v vorne und hinten auf, und p_E,k "
                  "wächst nicht ohne Grenze mit der Tiefe.")
        festigkeiten = [
            Festigkeit(True, phi=e.g(f"phi_k_{i}").si, c=e.g(f"c_k_{i}").si) if s.drainiert
            else Festigkeit(False, s_u=e.g(f"s_u_{i}").si)
            for i, s in enumerate(self.pfahl.schichten, start=1)]
        return Erdwiderstand(profil, festigkeiten, e.g("D").si)

    def _tabelle(self, p: Protokoll, linien: Sequence[Linie]) -> None:
        """p_E,k am Pfahl, je Stück oben und unten."""
        p.tabelle(kopf=["Schicht", Mathe(r"z_o\ [\mathrm{m}]"), Mathe(r"z_u\ [\mathrm{m}]"),
                        Mathe(r"p_{E,k,o}\ [\mathrm{kN/m}]"),
                        Mathe(r"p_{E,k,u}\ [\mathrm{kN/m}]")],
                  zeilen=[[f"{li.schicht + 1}: {self.pfahl.schichten[li.schicht].name}",
                           Mathe(fest(li.oben, 2)), Mathe(fest(li.unten, 2)),
                           Mathe(fest(li.p_oben / 1e3, 0)), Mathe(fest(li.p_unten / 1e3, 0))]
                          for li in linien],
                  titel="Erdwiderstand am Pfahl, charakteristisch, z ab Terrain -- geteilt an "
                        "den Schichten, am Wasser und wo e_a null wird",
                  ausrichtung="lrrrr")

    def _brueche(self, p: Protokoll) -> None:
        """Die Brüche, die der Kopf zulässt."""
        p.titel("Brüche", ebene=3)
        if self.pfahl.kopf is Kopf.EINGESPANNT:
            p.ansatz(r"H \cdot s_r = M_R + \int_0^L p_{E,k} \cdot \left|s - s_r\right| ds "
                     r"\qquad H \cdot s_h = 2 \cdot M_R + \int_0^{s_h} p_{E,k} \cdot "
                     r"\left(s_h - s\right) ds",
                     titel="Eingespannter Kopf: ein Gelenk am Kopf und darunter der Pfahl um "
                           "s_r gedreht, oder ein zweites Gelenk in s_h; s ab Kopf",
                     referenz="SIA 267:2013, 9.4.4.2.2", name="Querbruch am eingespannten Kopf")
        else:
            p.ansatz(r"H \cdot \left|s_r + e\right| = \int_0^L p_{E,k} \cdot "
                     r"\left|s - s_r\right| ds \qquad H \cdot \left|s_h + e\right| = M_R + "
                     r"\int_0^{s_h} p_{E,k} \cdot \left(s_h - s\right) ds",
                     titel="Frei drehbarer Kopf: der ganze Pfahl um s_r gedreht, oder ein "
                           "Gelenk in s_h; s ab Kopf, e = M_Ed / H_Ed",
                     referenz="SIA 267:2013, 9.4.4.2.2", name="Querbruch am frei drehbaren Kopf")
        p.ansatz(r"H = \int_0^L p_{E,k}\, ds", titel="Der ganze Pfahl verschoben",
                 referenz="SIA 267:2013, 9.4.4.2.2", name="Querbruch durch Verschieben")
        p.text("Je Mechanismus leistet die Last dieselbe Arbeit, die Boden und Gelenke "
               "verzehren. s_r und s_h liegen dort, wo H am kleinsten wird, gesucht auf "
               "Knoten höchstens 1 cm auseinander; unter einem Gelenk steht der Pfahl still. "
               "Der kleinste Bruch ist R_tr,k.")
        p.annahme("Die Mechanismen, wie für kurze und lange Pfähle üblich, sind nach Vorgabe "
                  "gewählt, nicht nachgeschlagen: die Norm verlangt nur, R_tr,k aus dem "
                  "Erdwiderstand und dem inneren Widerstand zu bestimmen. Der Biegewiderstand "
                  "zählt dabei charakteristisch, mal η_i.")
        p.annahme("γ_M,a = 1.4 ist quer in der Regel der kleinste Wert; die Norm will den "
                  "Bemessungswert je Objekt bestimmt haben. Die Bettungskraft steht mit "
                  "denselben Beiwerten gegen den Erdwiderstand -- beides nach Vorgabe, nicht "
                  "nachgeschlagen.")

    # -- Die Querkraft -----------------------------------------------------------

    def _querkraft(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, k: Kombination,
                   v: Verlauf, linien: Sequence[Linie], q: Querschnitt, innen: Innenbefund,
                   fall: Querfall) -> NachweisUrteil:
        eta_i = e.g("eta_i").si
        M_kopf = biegewiderstand(q, v.N_Ed, eta_i, innen.masse.n)
        M_fuss = biegewiderstand(q, v.N_b, eta_i, innen.masse.n)
        p.tabelle(kopf=["Stelle", Mathe(r"N\ [\mathrm{kN}]"),
                        Mathe(r"\eta_i \cdot M_{R,k}(N / \eta_i)\ [\mathrm{kNm}]")],
                  zeilen=[["Kopf", Mathe(fest(v.N_Ed / 1e3, 0)), Mathe(fest(M_kopf / 1e3, 1))],
                          ["Fuss", Mathe(fest(v.N_b / 1e3, 0)), Mathe(fest(M_fuss / 1e3, 1))]],
                  titel="Biegewiderstand des Pfahls im Bruch, mit f_ck und f_yk",
                  ausrichtung="lrr")
        M_R = werte.moment("M_R", "M_R", min(M_kopf, M_fuss),
                           "Biegewiderstand des Pfahls im Bruch")
        p.wert(M_R, titel="Biegewiderstand im Bruch, der kleinere: dazwischen ist er nicht "
                          "kleiner, die Fläche der Widerstände ist konvex",
               referenz="SIA 267:2013, 9.4.4.2.2; 9.5.2.4.1, (50)")
        if M_R.groesse.si == 0.0:
            p.hinweis("Die Normalkraft allein ist mehr, als der Querschnitt trägt: der Pfahl "
                      "hat keinen Biegewiderstand mehr.")
        eingespannt = self.pfahl.kopf is Kopf.EINGESPANNT
        H_Ed = werte.kraft("H_Ed", "H_{Ed}", k.H_Ed.si, "Querkraft am Kopf")
        hebel = 0.0
        if not eingespannt and k.M_Ed.si != 0.0:
            hebel = k.M_Ed.si / k.H_Ed.si
            e_wert = werte.wert("e", "e", Groesse.aus_si(hebel, M), 2,
                                "Hebel des Moments über dem Kopf")
            p.formel(e_wert, r"\frac{@M}{@H}",
                     {"M": werte.moment("M_Ed", "M_{Ed}", k.M_Ed.si, "Moment am Kopf"),
                      "H": H_Ed},
                     titel="Hebel des Moments über dem Kopf", referenz="",
                     name="Hebel des Moments am Pfahlkopf")
        alle = brueche(linien, e.g("t_K").si, M_R.groesse.si, eingespannt=eingespannt, e=hebel)
        p.tabelle(kopf=["Bruch", Mathe(r"s\ [\mathrm{m}]"), Mathe(r"H\ [\mathrm{kN}]")],
                  zeilen=[[b.was, Mathe(fest(b.lage, 2)) if b.lage is not None else "–",
                           Mathe(fest(b.H / 1e3, 1))] for b in alle],
                  titel="Die Brüche an ihrer ungünstigsten Lage, s ab Kopf", ausrichtung="lrr")
        bruch = min(alle, key=lambda b: b.H)
        R_trk = werte.kraft("R_trk", "R_{tr,k}", bruch.H,
                            "Äusserer Widerstand quer, charakteristisch")
        p.wert(R_trk, titel=f"Der kleinste Bruch: {bruch.was}", referenz="SIA 267:2013, 9.4.4.2.2")
        gamma = werte.zahl("gamma_M", r"\gamma_{M,a}", GAMMA_M_QUER, "Widerstandsbeiwert quer",
                           stellen=1)
        R_trd = werte.kraft("R_trd", "R_{tr,d}", e.g("eta_tr").si * bruch.H / GAMMA_M_QUER,
                            "Äusserer Widerstand quer, Bemessungswert")
        p.formel(R_trd, r"\frac{@eta \cdot @R}{@gamma}",
                 {"eta": e["eta_tr"], "R": R_trk, "gamma": gamma},
                 titel="Äusserer Widerstand quer, Bemessungswert",
                 referenz="SIA 267:2013, 9.5.2.2.1, (42); 9.5.2.3.1, (49)",
                 name="Bemessungswert des äusseren Widerstands")
        fall.R_trk, fall.R_trd, fall.bruch = bruch.H, R_trd.groesse.si, bruch
        if k.H_Ed.si < 0.0:
            p.text("H_Ed ist negativ: der Widerstand quer gilt in beide Richtungen, es zählt "
                   "der Betrag.")
            H_Ed = werte.kraft("H_Ed_betrag", r"\left|H_{Ed}\right|", -k.H_Ed.si,
                               "Querkraft am Kopf, als Betrag")
        vergleich = Vergleich(H_Ed, R_trd)
        vergleich.bedingung(p, "Querkraft gegen Widerstand quer")
        vergleich.zeile(p, self.d_quer[k.name], mit_urteil=True)
        return self.urteil(self.d_quer[k.name], k.name, vergleich,
                           f"|H_Ed| = {H_Ed.formatiert()} kN "
                           f"{'≤' if vergleich.erfuellt else '>'} R_tr,d = "
                           f"{R_trd.formatiert()} kN ({bruch.was}).")

    # -- Die Bettungskraft -------------------------------------------------------

    def _bettung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, k: Kombination,
                 v: Verlauf, erd: Erdwiderstand, fall: Querfall) -> NachweisUrteil:
        """In jeder Tiefe der Verläufe die Bettungskraft gegen p_E,d -- massgebend die knappste."""
        D = e.g("D").si
        faktor = e.g("eta_tr").si / GAMMA_M_QUER
        p_Ek = [erd.bei(z) for z in v.z]
        fall.grenze = [faktor * x / D for x in p_Ek]
        kraft = [abs(x) * D for x in v.p]
        stellen = [i for i, x in enumerate(kraft) if x > 0.0]
        j = min(stellen, key=lambda i: p_Ek[i] / kraft[i]) if stellen else 0
        z = werte.wert("z_E", "z", Groesse.aus_si(v.z[j], M), 2,
                       "Tiefe unter Terrain, wo die Bettungskraft dem Erdwiderstand am nächsten "
                       "kommt")
        p.wert(z, referenz="")
        p_k = werte.wert("p_Ek", "p_{E,k}", Groesse.aus_si(p_Ek[j], KN_PRO_M), 0,
                         "Erdwiderstand dort, charakteristisch")
        p.wert(p_k, referenz=buch.KAP_SCHMAL)
        gamma = werte.zahl("gamma_E", r"\gamma_{M,a}", GAMMA_M_QUER, "Widerstandsbeiwert quer",
                           stellen=1)
        p_d = werte.wert("p_Ed", "p_{E,d}", Groesse.aus_si(faktor * p_Ek[j], KN_PRO_M), 0,
                         "Erdwiderstand dort, Bemessungswert")
        p.formel(p_d, r"\frac{@eta \cdot @p}{@gamma}",
                 {"eta": e["eta_tr"], "p": p_k, "gamma": gamma},
                 titel="Erdwiderstand dort, Bemessungswert", referenz=GAMMA_M_QUER_REFERENZ,
                 name="Bemessungswert des Erdwiderstands am Pfahl")
        q_d = werte.wert("q_d", "q_d", Groesse.aus_si(kraft[j], KN_PRO_M), 0,
                         "Bettungskraft dort, aus den Verläufen mit E_s,d")
        p.wert(q_d, referenz="SIA 267:2013, 9.5.4.5")
        vergleich = Vergleich(q_d, p_d)
        vergleich.bedingung(p, "Bettungskraft gegen Erdwiderstand")
        vergleich.zeile(p, self.d_bettung[k.name], mit_urteil=True)
        if not vergleich.erfuellt:
            p.hinweis("Der Boden gibt hier nach: die elastische Rechnung unterschätzt "
                      "Verschiebung und Moment. Bettung und Widerstand müssen über die Tiefe "
                      "zusammenpassen (SIA 267:2013, 9.5.4.5) -- etwa mit einer grösseren "
                      "Abminderung t_red nahe dem Terrain.")
        return self.urteil(self.d_bettung[k.name], k.name, vergleich,
                           f"q_d = {q_d.formatiert()} kN/m "
                           f"{'≤' if vergleich.erfuellt else '>'} p_E,d = "
                           f"{p_d.formatiert()} kN/m in z = {z.formatiert()} m.",
                           art="q_d", langname="Bettungskraft am Pfahl")
