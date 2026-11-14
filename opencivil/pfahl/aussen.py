"""
opencivil/pfahl/aussen.py -- der äussere Widerstand eines Pfahls längs seiner Achse.

VERANTWORTUNG:
Der Nachweis :class:`AeussererWiderstand`: je Kombination die Normalkraft am
Kopf gegen den Bemessungswert des äusseren Widerstands, auf Druck oder auf
Zug (SIA 267:2013, 9.5.2.2, 9.5.3.1)::

    R_a,k   = R_b,k + R_s,k         (41)   Druck: Fuss und Mantel
    R_a,k,Z = R_s,k                        Zug: nur der Mantel
    R_a,d   = η_a · R_a,k / γ_M,a   (42)   γ_M,a = 1.3 auf Druck (43), 1.6 auf Zug (44)

R_a,k kommt aus einem Versuch oder aus den Schichten (:class:`~.pfahl.Grundlage`).

DER MANTEL (Kap. 12.5):
Je Stück des Mantels (:meth:`~.boden.Profil.stuecke`) die Mantelreibung
q_s,k -- drainiert K · σ'_v · tan δ mit δ = k_δ · φ'_k, undrainiert
α · s_u,k, oder eingegeben -- und R_s,k = U · Σ h · q_s,k.

DER FUSS (Kap. 12.5):
Drainiert q_b,k = (c* · N_c + σ'_v · N_q) · X: N_q und N_c wie beim
Grundbruch (Kap. 9.2.6), beim örtlichen Abscheren mit φ* = 2/3 · φ'_k und
c* = 2/3 · c'_k, sonst mit φ'_k und c'_k; X aus Bild 12.4 nach φ'_k und
der Einbindung h in die Schicht am Fuss. Undrainiert q_b,k = s_u,k · N_c
mit N_c aus Bild 12.5 nach L/D. R_b,k = A_b · q_b,k.

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
* Die Faktoren des örtlichen Abscherens und dazu η_a und γ_M,a: das Buch
  rechnet mit einer globalen Sicherheit und führt nach dem Abmindern keine
  weitere ein. Hier gilt die Norm, und sie verlangt R_a,d.
* X mit φ'_k, nicht mit φ*.
* Undrainiert ohne die Überlagerung am Fuss: sie hebt sich etwa mit dem
  Gewicht des Pfahls auf, das auch nicht in der Einwirkung steht.
* Auf Zug dieselbe Mantelreibung wie auf Druck.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.einheiten import GRAD, KN_PRO_M, KPA, M, M2, Groesse
from opencivil.core.latex import Mathe, Zelle, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.geotechnik.grundbruch import tragfaehigkeitsfaktoren
from opencivil.pfahl import buch
from opencivil.pfahl.achse import Achsnachweis
from opencivil.pfahl.boden import Mantel, Profil, Stueck
from opencivil.pfahl.pfahl import Abscheren, Kombination, Pfahl, Spitze

#: Die Widerstandsbeiwerte des äusseren axialen Widerstands, auf Druck und
#: auf Zug, mit ihrer Stelle (SIA 267:2013, 9.5.2.2.4).
GAMMA_M = {True: (1.3, "SIA 267:2013, 9.5.2.2.4, (43)"),
           False: (1.6, "SIA 267:2013, 9.5.2.2.4, (44)")}

#: Was beide Richtungen annehmen -- siehe Dateikopf.
ZUG_WIE_DRUCK = ("Auf Zug trägt nur der Mantel, mit derselben Mantelreibung wie auf Druck "
                 "-- nach Vorgabe, nicht nachgeschlagen. Ein Zugpfahl muss die Zugkraft "
                 "über seine ganze Länge tragen (SIA 267:2013, 9.5.3.4.2).")


@dataclass(frozen=True)
class Mantelstueck:
    """Was ein Stück des Mantels trägt -- Spannungen in Pa."""

    stueck: Stueck
    q_s: float
    sigma: Optional[float] = None
    """σ'_v in seiner Mitte -- nur, wo die Mantelreibung daraus gerechnet ist."""


@dataclass
class Aussenbefund:
    """Was ausser den Erfüllungsgraden bleibt -- für Zusammenfassung und Bild, in SI."""

    aus_versuch: bool
    stuecke: List[Mantelstueck] = field(default_factory=list)
    R_s: float = 0.0
    q_b: Optional[float] = None
    """Der Spitzendruck -- ``None``, wo der Fuss nicht trägt."""

    R_b: float = 0.0
    R_ak: float = 0.0
    R_ak_zug: float = 0.0
    R_ad: float = 0.0
    R_ad_zug: float = 0.0


class AeussererWiderstand(Achsnachweis):
    """Siehe Dateikopf."""

    THEMA = "Äusserer Pfahlwiderstand"
    ART = "R_a"
    INDEX = "a"
    TITEL = "Äusserer Widerstand"
    WORT = "äusserer Widerstand"

    def __init__(self, pfahl: Pfahl, kombinationen: Sequence[Kombination]) -> None:
        gruppen = (("Äusserer Widerstand",) if pfahl.grundlage.aus_versuch else
                   ("Pfahl", "Grundwasser", "Äusserer Widerstand", "Schicht"))
        super().__init__(pfahl, kombinationen, basis=f"{pfahl.id}.nachweis.aussen",
                         bezuege=[Eingabebezug(n, pfahl.id_von(n))
                                  for n in pfahl.kurznamen(*gruppen)])

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Äusserer Widerstand")
        p.erklaerung(
            "Der Pfahl gibt seine Last über den Mantel und den Fuss an den Boden ab. "
            "Am Mantel reibt er an jeder Schicht, durch die er geht; am Fuss drückt er "
            "auf die Schicht, in der er steht. Die Summe ist der charakteristische "
            "äussere Widerstand. Auf Zug trägt nur der Mantel. Der Bemessungswert "
            "folgt mit zwei Faktoren der Norm: der Umrechnungsfaktor η_a sagt, wie "
            "verlässlich der Widerstand bestimmt ist -- aus einer Berechnung am "
            "wenigsten, aus einem statischen Versuch am meisten --, der "
            "Widerstandsbeiwert γ_M,a deckt die Streuung des Bodens und der "
            "Ausführung.")
        werte = Zwischenwerte(self.id)
        if self.pfahl.grundlage.aus_versuch:
            befund = Aussenbefund(aus_versuch=True)
            p.text(f"R_a,k ist eingegeben, Grundlage: {self.pfahl.grundlage.beschriftung}. "
                   f"Er ist der kleinste gemessene Wert (SIA 267:2013, 9.4.4.1.6).")
            R_ak, R_ak_zug = e["R_ak"], e["R_ak_zug"]
        else:
            befund = Aussenbefund(aus_versuch=False)
            R_ak, R_ak_zug = self._aus_schichten(e, p, werte, befund)
        befund.R_ak, befund.R_ak_zug = R_ak.groesse.si, R_ak_zug.groesse.si
        R_ad = self._bemessung(e, p, werte, R_ak, druck=True)
        R_ad_zug = self._bemessung(e, p, werte, R_ak_zug, druck=False)
        befund.R_ad, befund.R_ad_zug = R_ad.groesse.si, R_ad_zug.groesse.si
        return Ausfuehrung({}, self.faelle(p, R_ad, R_ad_zug), befund)

    # -- R_a,k aus den Schichten -------------------------------------------

    def _profil(self, e: Eingaben) -> Profil:
        n = len(self.pfahl.schichten)
        return Profil([e.g(f"d_{i}").si for i in range(1, n + 1)],
                      [e.g(f"gamma_{i}").si for i in range(1, n + 1)],
                      e.g("t_w").si, e.g("gamma_w").si)

    def _aus_schichten(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                       befund: Aussenbefund) -> Tuple[Wert, Wert]:
        profil = self._profil(e)
        R_s = self._mantel(e, p, werte, profil, befund)
        R_b = self._fuss(e, p, werte, profil, befund)
        p.titel("Charakteristischer äusserer Widerstand", ebene=3)
        R_ak = werte.kraft("R_ak", "R_{a,k}", R_b.groesse.si + R_s.groesse.si,
                           "Äusserer Widerstand auf Druck", stellen=0)
        p.formel(R_ak, "@R_b + @R_s", {"R_b": R_b, "R_s": R_s},
                 titel="Äusserer Widerstand auf Druck, charakteristisch",
                 referenz="SIA 267:2013, 9.4.4.1.1, (41); 9.4.4.1.6",
                 name="Äusserer Widerstand auf Druck")
        R_ak_zug = werte.kraft("R_ak_zug", "R_{a,k,Z}", R_s.groesse.si,
                               "Äusserer Widerstand auf Zug", stellen=0)
        p.formel(R_ak_zug, "@R_s", {"R_s": R_s},
                 titel="Äusserer Widerstand auf Zug, charakteristisch: nur der Mantel",
                 referenz="SIA 267:2013, 9.4.4.1.1", name="Äusserer Widerstand auf Zug")
        p.annahme(ZUG_WIE_DRUCK)
        return R_ak, R_ak_zug

    def _mantel(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, profil: Profil,
                befund: Aussenbefund) -> Wert:
        """Je Stück die Mantelreibung, als Tabelle -- und daraus R_s,k."""
        f = self.pfahl
        p.titel("Mantel", ebene=3)
        D, t_K, L = e["D"], e["t_K"], e["L"]
        U = werte.wert("U", "U", Groesse.aus_si(math.pi * D.groesse.si, M), 3,
                       "Umfang des Pfahls")
        p.formel(U, r"\pi \cdot @D", {"D": D}, titel="Umfang des Pfahls", referenz="",
                 name="Umfang des Pfahls")
        oben, unten = t_K.groesse.si, t_K.groesse.si + L.groesse.si
        stuecke = profil.stuecke(oben, unten)
        arten = {(f.schichten[s.schicht].mantel, f.schichten[s.schicht].drainiert)
                 for s in stuecke}
        if any(m is Mantel.RECHNEN and d for m, d in arten):
            p.ansatz(r"\sigma'_v(z) = \sum \gamma_i \, t_i - u(z) \qquad"
                     r" u(z) = \gamma_w \cdot \max\left(0;\ z - t_w\right)",
                     titel="Wirksame Spannung aus dem Gewicht des Bodens darüber",
                     referenz=buch.KAP_MANTEL, name="Wirksame Überlagerungsspannung")
            p.ansatz(r"q_{s,k} = K \cdot \sigma'_v \cdot \tan\delta \qquad"
                     r" \delta = k_{\delta} \cdot \varphi'_k",
                     titel="Mantelreibung drainiert, σ'_v in der Mitte des Stücks",
                     referenz=buch.KAP_MANTEL, name="Mantelreibung drainiert")
        if any(m is Mantel.RECHNEN and not d for m, d in arten):
            p.ansatz(r"q_{s,k} = \alpha \cdot s_{u,k}", titel="Mantelreibung undrainiert",
                     referenz=buch.KAP_MANTEL, name="Mantelreibung undrainiert")
        p.text(f"Der Mantel reicht vom Kopf in {fest(oben, 2)} m bis zum Fuss in "
               f"{fest(unten, 2)} m unter Terrain; je Schicht ein Stück, am "
               f"Grundwasserspiegel geteilt. Über dem Kopf trägt der Boden nur als Auflast.")
        zeilen: List[List[Zelle]] = []
        for s in stuecke:
            stueck = self._stueck(e, s, profil)
            befund.stuecke.append(stueck)
            schicht = f.schichten[s.schicht]
            zeilen.append([
                f"{s.schicht + 1}: {schicht.name}", Mathe(fest(s.z_o, 2)), Mathe(fest(s.z_u, 2)),
                Mathe(fest(s.h, 2)),
                Mathe(fest(stueck.sigma / 1e3, 1)) if stueck.sigma is not None else "–",
                Mathe(fest(stueck.q_s / 1e3, 1)), Mathe(fest(s.h * stueck.q_s / 1e3, 1))])
        p.tabelle(kopf=["Schicht", Mathe(r"z_o\ [\mathrm{m}]"), Mathe(r"z_u\ [\mathrm{m}]"),
                        Mathe(r"h\ [\mathrm{m}]"), Mathe(r"\sigma'_v\ [\mathrm{kPa}]"),
                        Mathe(r"q_{s,k}\ [\mathrm{kPa}]"),
                        Mathe(r"h \cdot q_{s,k}\ [\mathrm{kN/m}]")],
                  zeilen=zeilen, titel="Mantelreibung je Stück", ausrichtung="lrrrrrr")
        self._erddruck_pruefen(e, p, stuecke)
        summe = sum(s.stueck.h * s.q_s for s in befund.stuecke)
        Q = werte.wert("summe_q_s", r"\sum h \, q_{s,k}", Groesse.aus_si(summe, KN_PRO_M), 1,
                       "Mantelreibung über die Länge")
        R_s = werte.kraft("R_sk", "R_{s,k}", U.groesse.si * summe, "Mantelwiderstand",
                          stellen=0)
        p.formel(R_s, "@U \\cdot @Q", {"U": U, "Q": Q}, titel="Mantelwiderstand",
                 referenz=f"{buch.KAP_MANTEL}; SIA 267:2013, 9.4.4.1.1",
                 name="Mantelwiderstand")
        befund.R_s = R_s.groesse.si
        return R_s

    def _stueck(self, e: Eingaben, s: Stueck, profil: Profil) -> Mantelstueck:
        schicht = self.pfahl.schichten[s.schicht]
        i = s.schicht + 1
        if schicht.mantel is Mantel.EINGEBEN:
            return Mantelstueck(s, e.g(f"q_s_{i}").si)
        if not schicht.drainiert:
            return Mantelstueck(s, e.g(f"alpha_{i}").si * e.g(f"s_u_{i}").si)
        sigma = profil.sigma_v_wirksam(s.mitte)
        delta = e.g(f"delta_faktor_{i}").si * e.g(f"phi_k_{i}").si
        return Mantelstueck(s, e.g(f"K_{i}").si * sigma * math.tan(delta), sigma)

    def _erddruck_pruefen(self, e: Eingaben, p: Protokoll, stuecke: Sequence[Stueck]) -> None:
        """K über K_0: das Buch sieht für Bohrpfähle höchstens etwa K_0 (Kap. 12.5)."""
        for i in sorted({s.schicht + 1 for s in stuecke}):
            schicht = self.pfahl.schichten[i - 1]
            if schicht.mantel is not Mantel.RECHNEN or not schicht.drainiert:
                continue
            K, K_0 = e.g(f"K_{i}").si, buch.ruhedruckbeiwert(e.g(f"phi_k_{i}").si)
            if K > K_0:
                p.hinweis(f"Schicht {i}: K = {K:.2f} liegt über K_0 ≈ 1 − sin φ'_k = {K_0:.2f} "
                          f"({buch.KAP_RUHEDRUCK}). An einem Bohrpfahl erreicht K nach dem Buch "
                          f"höchstens etwa K_0, und K_0 wächst mit der Vorbelastung "
                          f"({buch.KAP_MANTEL}).")

    # -- Der Fuss -------------------------------------------------------------

    def _fuss(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, profil: Profil,
              befund: Aussenbefund) -> Wert:
        f = self.pfahl
        p.titel("Fuss", ebene=3)
        if f.spitze is Spitze.KEINE:
            p.text("Der Fuss trägt nicht: nur der Mantel.")
            return werte.kraft("R_bk", "R_{b,k}", 0.0, "Spitzenwiderstand", stellen=0)
        D = e["D"]
        A_b = werte.wert("A_b", "A_b", Groesse.aus_si(math.pi * D.groesse.si ** 2 / 4.0, M2), 3,
                         "Fläche des Fusses")
        p.formel(A_b, r"\frac{\pi \cdot @D^{2}}{4}", {"D": D}, titel="Fläche des Fusses",
                 referenz="", name="Fläche des Pfahlquerschnitts")
        if f.spitze is Spitze.EINGEBEN:
            q_b = e["q_b"]
        else:
            z_F = e.g("t_K").si + e.g("L").si
            j = profil.schicht_bei(z_F)
            schicht = f.schichten[j]
            p.text(f"Der Fuss steht in {fest(z_F, 2)} m unter Terrain in Schicht {j + 1}, "
                   f"{schicht.name}; sie reicht noch {fest(profil.grenzen[j][1] - z_F, 2)} m "
                   f"tiefer.")
            p.annahme("Die Schicht unter dem Fuss ist mächtig genug, dass der Fuss sie nicht "
                      f"durchstanzt -- die Voraussetzung des Spitzendrucks ({buch.KAP_MANTEL}).")
            q_b = (self._fuss_drainiert(e, p, werte, profil, j, z_F) if schicht.drainiert
                   else self._fuss_undrainiert(e, p, werte, j))
        R_b = werte.kraft("R_bk", "R_{b,k}", A_b.groesse.si * q_b.groesse.si,
                          "Spitzenwiderstand", stellen=0)
        p.formel(R_b, r"@A_b \cdot @q_b", {"A_b": A_b, "q_b": q_b}, titel="Spitzenwiderstand",
                 referenz=f"{buch.KAP_SPITZE}; SIA 267:2013, 9.4.4.1.1",
                 name="Spitzenwiderstand")
        befund.q_b, befund.R_b = q_b.groesse.si, R_b.groesse.si
        return R_b

    def _fuss_drainiert(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                        profil: Profil, j: int, z_F: float) -> Wert:
        i = j + 1
        phi, c = e[f"phi_k_{i}"], e[f"c_k_{i}"]
        if self.pfahl.abscheren is Abscheren.OERTLICH:
            p.text("Örtliches Abscheren: bis der Boden am Fuss ganz bricht, müsste sich der "
                   "Pfahl stark setzen. Darum zählen nur 2/3 von φ'_k und c'_k "
                   f"({buch.KAP_ABSCHEREN}).")
            p.annahme("Das Buch sieht danach keine weitere Sicherheit am Spitzendruck vor; hier "
                      "gelten η_a und γ_M,a der Norm trotzdem. X wird mit φ'_k abgelesen, nicht "
                      "mit 2/3 davon -- beides nach Vorgabe, nicht nachgeschlagen.")
            phi = werte.wert("phi_stern", r"\varphi^{*}", Groesse.aus_si(
                buch.ABSCHEREN * phi.groesse.si, GRAD), 2, "Reibungswinkel am Fuss")
            p.formel(phi, r"\tfrac{2}{3} \cdot @phi", {"phi": e[f"phi_k_{i}"]},
                     titel="Reibungswinkel für örtliches Abscheren", referenz=buch.KAP_ABSCHEREN,
                     name="Reibungswinkel für örtliches Abscheren")
            c = werte.wert("c_stern", "c^{*}", Groesse.aus_si(buch.ABSCHEREN * c.groesse.si,
                                                              KPA), 1, "Kohäsion am Fuss")
            p.formel(c, r"\tfrac{2}{3} \cdot @c", {"c": e[f"c_k_{i}"]},
                     titel="Kohäsion für örtliches Abscheren", referenz=buch.KAP_ABSCHEREN,
                     name="Kohäsion für örtliches Abscheren")
        else:
            p.text("Allgemeines Abscheren: mit φ'_k und c'_k.")
        N_q, N_c = tragfaehigkeitsfaktoren(p, werte, phi)
        h = werte.wert("h", "h", Groesse.aus_si(z_F - profil.grenzen[j][0], M), 2,
                       "Einbindung in die Schicht am Fuss")
        p.formel(h, "@z_F - @z_o", {
            "z_F": werte.wert("z_F", "z_F", Groesse.aus_si(z_F, M), 2, "Tiefe des Fusses"),
            "z_o": werte.wert("z_o", f"z_{{o,{i}}}", Groesse.aus_si(profil.grenzen[j][0], M), 2,
                              f"Oberkante der Schicht {i}")},
            titel="Einbindung in die Schicht am Fuss", referenz=buch.KAP_LASTTRANSPORT,
            name="Einbindung in die tragende Schicht")
        phi_k, D = e[f"phi_k_{i}"], e["D"]
        h_d = h.groesse.si / D.groesse.si
        X = werte.zahl("X", "X", buch.faktor_x(math.degrees(phi_k.groesse.si), h_d),
                       "Form- und Tiefenfaktor", stellen=2)
        p.formel(X, r"X\left(@phi, \tfrac{@h}{@D}\right)", {"phi": phi_k, "h": h, "D": D},
                 titel="Form- und Tiefenfaktor, abgelesen nach φ'_k und h/D",
                 referenz=buch.KAP_SPITZE, name="Form- und Tiefenfaktor des Pfahlfusses")
        for satz in buch.ausserhalb(math.degrees(phi_k.groesse.si), h_d):
            p.warnung(satz)
        sigma = werte.wert("sigma_vF", r"\sigma'_{v,F}", Groesse.aus_si(
            profil.sigma_v_wirksam(z_F), KPA), 1, "Wirksame Spannung am Fuss")
        p.formel(sigma, r"\sum \gamma_i \, t_i - u", {}, titel="Wirksame Spannung am Fuss",
                 referenz=buch.KAP_MANTEL, name="Wirksame Spannung am Pfahlfuss")
        q_b = werte.wert("q_b", "q_{b,k}", Groesse.aus_si(
            (c.groesse.si * N_c.groesse.si + sigma.groesse.si * N_q.groesse.si)
            * X.groesse.si, KPA), 0, "Spitzendruck")
        p.formel(q_b, r"\left(@c \cdot @N_c + @sigma \cdot @N_q\right) \cdot @X",
                 {"c": c, "N_c": N_c, "sigma": sigma, "N_q": N_q, "X": X},
                 titel="Spitzendruck, drainiert", referenz=buch.KAP_SPITZE,
                 name="Spitzendruck drainiert")
        return q_b

    def _fuss_undrainiert(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                          j: int) -> Wert:
        L, D, s_u = e["L"], e["D"], e[f"s_u_{j + 1}"]
        N_c = werte.zahl("N_c", "N_c", buch.faktor_n_c_undrainiert(
            L.groesse.si / D.groesse.si), "Tragfähigkeitsfaktor, undrainiert", stellen=2)
        p.formel(N_c, r"N_c\left(\tfrac{@L}{@D}\right)", {"L": L, "D": D},
                 titel="Tragfähigkeitsfaktor undrainiert, abgelesen nach L/D, höchstens 9",
                 referenz=buch.KAP_SPITZE_UNDRAINIERT,
                 name="Tragfähigkeitsfaktor des Pfahlfusses undrainiert")
        p.annahme("Undrainiert ohne die Überlagerung am Fuss: sie hebt sich etwa mit dem "
                  "Gewicht des Pfahls auf, das auch nicht in der Einwirkung steht -- nach "
                  "Vorgabe, nicht nachgeschlagen.")
        q_b = werte.wert("q_b", "q_{b,k}", Groesse.aus_si(s_u.groesse.si * N_c.groesse.si, KPA),
                         0, "Spitzendruck")
        p.formel(q_b, r"@s_u \cdot @N_c", {"s_u": s_u, "N_c": N_c},
                 titel="Spitzendruck, undrainiert", referenz=buch.KAP_SPITZE_UNDRAINIERT,
                 name="Spitzendruck undrainiert")
        return q_b

    # -- Bemessung und Vergleich ----------------------------------------------

    def _bemessung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, R_ak: Wert, *,
                   druck: bool) -> Wert:
        """R_a,d = η_a · R_a,k / γ_M,a (42) -- auf Druck oder auf Zug."""
        p.titel(f"Bemessungswert auf {'Druck' if druck else 'Zug'}", ebene=3)
        zahl, referenz = GAMMA_M[druck]
        z = "" if druck else "_zug"
        gamma = werte.zahl(f"gamma_M{z}", r"\gamma_{M,a}", zahl,
                           f"Widerstandsbeiwert auf {'Druck' if druck else 'Zug'}", stellen=1)
        p.wert(gamma, referenz=referenz)
        R_ad = werte.kraft(f"R_ad{z}", "R_{a,d}" if druck else "R_{a,d,Z}",
                           e.g("eta_a").si * R_ak.groesse.si / zahl,
                           f"Äusserer Widerstand auf {'Druck' if druck else 'Zug'}", stellen=0)
        p.formel(R_ad, r"\frac{@eta \cdot @R}{@gamma}",
                 {"eta": e["eta_a"], "R": R_ak, "gamma": gamma},
                 titel=f"Äusserer Widerstand auf {'Druck' if druck else 'Zug'}, Bemessungswert",
                 referenz="SIA 267:2013, 9.5.2.2.1, (42)",
                 name="Bemessungswert des äusseren Widerstands")
        return R_ad
