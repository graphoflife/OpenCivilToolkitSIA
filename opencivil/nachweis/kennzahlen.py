"""
opencivil/nachweis/kennzahlen.py -- was eine Platte aufnimmt, ohne Einwirkung.

VERANTWORTUNG:
Die Kennzahlen der Platte in x, gerechnet immer -- ob es Lastfaelle gibt oder
nicht (Benutzer, 2026-10-16). Die Zusammenfassung zeigt sie unter jeder
Platte:

* aus der Handrechnung mit Bemessungswerten: ``M_Rd+`` und ``M_Rd-`` bei
  ``N_Ed = 0``, ``N_Rd+`` und ``N_Rd-`` bei ``M_Ed = 0``, dazu ``x/d`` bei
  ``N_Ed = 0`` je gezogene Seite;
* der Querkraftwiderstand bei ``N_Ed = 0``. Ohne Buegel ``V_Rd,max``, das
  Kleinere beider Seiten bei ``M_Ed = 0``, und ``V_Rd,min``, das Kleinere
  bei ``M_Ed = M_Rd``. Mit Buegeln der Widerstand bei der guenstigsten
  Neigung, ``V_Rd(alpha_opt)`` -- auch er das Kleinere beider Seiten.

x/d je Seite, das Kleinere beider Seiten auch mit Buegeln und die
Handrechnung mit Bemessungswerten hat der Benutzer am 2026-10-16 bestaetigt.

Die Vergroesserungsfaktoren omega_w und omega_w' rechnet
:class:`~opencivil.nachweis.verformung.Vergroesserungsfaktor`; die
Zusammenfassung stellt sie dazu.

WAS FEHLT, FEHLT:
Jede Kennzahl steht mit ihrer Beschriftung hier (:attr:`Plattenkennzahlen.kennzahlen`),
und nur, was die Platte hat: ein x/d gibt es nur fuer eine Seite mit
Zugbewehrung. Bis 2026-10-18 stand fuer die andere 0, und ein Widerstand, den
die Linie nicht traf, ebenfalls -- so hatte eine Platte nur mit oberer
Bewehrung den Druckwiderstand 0 statt -5000 kN.

NICHTS ZWEIMAL:
Rechnet die Tragsicherheit von Hand mit Bemessungswerten -- die Vorgabe --,
lesen die Kennzahlen deren Linie aus ihrem Befund und leiten nichts ein
zweites Mal her; sonst rechnen sie eine eigene, mit Herleitung (dasselbe
Muster wie das Knicken). Die Querkraft rechnet und schreibt mit den
Funktionen ihres Nachweises: :func:`~opencivil.nachweis.querkraft_ohne_buegel.beiwert_k_g`,
:func:`~opencivil.nachweis.querkraft_ohne_buegel.widerstand`,
:func:`~opencivil.nachweis.querkraft_buegel.neigungen`, dazu
:func:`~opencivil.nachweis.querkraft.protokoll_hoehen`,
:func:`~opencivil.nachweis.querkraft_ohne_buegel.protokoll_ohne_buegel` und
:func:`~opencivil.nachweis.querkraft_buegel.protokoll_mit_buegeln`. Bis 2026-10-18
standen ihre Zeilen hier ein zweites Mal.

WAS DIE GRENZEN BEDEUTEN:
Ohne Buegel ist bei ``M_Ed = 0`` die Dehnung null und ``k_d = 1``; bei
``M_Ed = M_Rd`` ist sie ``f_yd/E_s``, gleich wie gross ``M_Rd`` ist.
Dazwischen liegt jeder Widerstand ohne Normalkraft.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from opencivil.core.berechnung import BerechnungsFehler, Befundbezug, Eingaben, Prozedur
from opencivil.core.einheiten import EINHEITSLOS, KN, KN_PRO_M, KNM, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Kennzahl, Wert, WertDef
from opencivil.nachweis import linie as geo
from opencivil.nachweis.biegung_normalkraft import (
    gleiche_linie, linienbezuege, resistenzlinie,
)
from opencivil.nachweis.querkraft import lagen_von, protokoll_hoehen, zuglage
from opencivil.nachweis.querkraft_buegel import (
    buegelteilung_y, neigungen, protokoll_mit_buegeln,
)
from opencivil.nachweis.querkraft_ohne_buegel import (
    Kurvenbeiwerte, beiwert_k_g, protokoll_ohne_buegel, tau_cd_wert, widerstand,
)
from opencivil.querschnitt.fachwerk import beste_neigung
from opencivil.nachweis.rechenwahl import bezuege_vereinen, stahlname
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import UM_Y, Zugseite

#: Womit die Kennzahlen rechnen: die Handrechnung mit Bemessungswerten.
WAHL = Rechenwahl()

#: Woher die Eckwerte stammen -- ihre Erklaerung unter der Platte.
HAND = "Handrechnung mit Bemessungswerten"


class Plattenkennzahlen(Prozedur):
    """Die Kennzahlen einer Platte in x -- siehe Dateikopf."""

    THEMA = "Kennzahlen"

    def __init__(self, querschnitt, mn, querkraft) -> None:
        self.querschnitt = querschnitt
        self.posten = querschnitt.posten_in_richtung(Richtung.X)
        self.mn = mn
        self.buegel = querkraft.buegel
        self.eigene_linie = not gleiche_linie(mn.wahl, WAHL)

        basis = f"{querschnitt.id}.kennzahlen"
        #: Je Kurzname die Definition -- zum Belegen.
        self.d: Dict[str, WertDef] = {}
        #: Dieselben, wie sie unter der Platte stehen, in dieser Folge.
        self.kennzahlen: List[Kennzahl] = []

        def dazu(kurz: str, symbol: str, einheit, beschreibung: str, beschriftung: str,
                 erklaerung: str = HAND, *, stellen: int = 1, referenz: str = "") -> None:
            definition = WertDef(id=f"{basis}.{kurz}", symbol=symbol, einheit=einheit,
                                 beschreibung=beschreibung, referenz=referenz,
                                 stellen=stellen)
            self.d[kurz] = definition
            self.kennzahlen.append(Kennzahl(definition, beschriftung, erklaerung))

        dazu("M_Rd_pos", r"M_{Rd}^{+}(N_{Ed} = 0)", KNM,
             "Momentenwiderstand bei N_Ed = 0, Zug unten", "Momentenwiderstand, Zug unten")
        dazu("M_Rd_neg", r"M_{Rd}^{-}(N_{Ed} = 0)", KNM,
             "Momentenwiderstand bei N_Ed = 0, Zug oben", "Momentenwiderstand, Zug oben")
        dazu("N_Rd_zug", r"N_{Rd}^{+}(M_{Ed} = 0)", KN,
             "Zugwiderstand bei M_Ed = 0", "Zugwiderstand")
        dazu("N_Rd_druck", r"N_{Rd}^{-}(M_{Ed} = 0)", KN,
             "Druckwiderstand bei M_Ed = 0", "Druckwiderstand")
        # Ein x/d nur, wo Zug auf Bewehrung trifft: ohne sie gibt es kein d.
        gezogen = {lage.seite for lage, _, _, _, _ in self.posten}
        for seite in UM_Y:
            if seite in gezogen:
                dazu(f"x_d_{seite.marke}", rf"\left(x/d\right)^{{{seite.zeichen}}}",
                     EINHEITSLOS, f"Bezogene Druckzonenhöhe bei N_Ed = 0, Zug {seite}",
                     f"Bezogene Druckzonenhöhe, Zug {seite}", stellen=3)
        if self.buegel is None:
            dazu("V_Rd_max", r"V_{Rd,max}", KN_PRO_M,
                 "Querkraftwiderstand ohne Bügel bei M_Ed = 0 und N_Ed = 0",
                 "Querkraftwiderstand ohne Bügel, grösster",
                 "N_Ed = 0, M_Ed = 0 – das Kleinere beider Seiten",
                 referenz="SIA 262:2025, 4.3.3.2.1")
            dazu("V_Rd_min", r"V_{Rd,min}", KN_PRO_M,
                 "Querkraftwiderstand ohne Bügel bei M_Ed = M_Rd und N_Ed = 0",
                 "Querkraftwiderstand ohne Bügel, kleinster",
                 "N_Ed = 0, M_Ed = M_Rd – das Kleinere beider Seiten",
                 referenz="SIA 262:2025, 4.3.3.2.1")
        else:
            dazu("V_Rd_buegel", r"V_{Rd}(\alpha_{opt})", KN_PRO_M,
                 "Querkraftwiderstand mit Bügeln bei der günstigsten Neigung, N_Ed = 0",
                 "Querkraftwiderstand mit Bügeln",
                 "N_Ed = 0, günstigste Neigung – das Kleinere beider Seiten",
                 referenz="SIA 262:2025, 4.3.3.4")

        # Was die Querkraft braucht, unter den Namen ihres Nachweises -- ohne
        # die Momentenwiderstaende seiner Faelle.
        bezuege = [b for b in querkraft.bezuege if not b.name.startswith("m_Rd_")]
        if self.eigene_linie:
            bezuege = bezuege_vereinen(
                bezuege, linienbezuege(querschnitt, self.posten, Richtung.X, WAHL.satz))
        super().__init__(
            basis,
            ausgaben=list(self.d.values()),
            bezuege=bezuege,
            befunde=[] if self.eigene_linie else [Befundbezug("mn", mn.id)],
            titel="Kennzahlen",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was die Platte in x aufnimmt, ohne Bezug auf eine Einwirkung: die "
            "Eckwerte der Handrechnung mit Bemessungswerten und der "
            "Querkraftwiderstand ohne Normalkraft. Wo eine Seite massgebend ist, "
            "gilt das Kleinere beider Seiten."
        )
        werte = Zwischenwerte(self.id)
        ergebnis: Dict[str, Groesse] = {}

        momente = self._handrechnung(e, p, werte, ergebnis)
        if self.buegel is None:
            self._ohne_buegel(e, p, werte, ergebnis, momente)
        else:
            self._mit_buegeln(e, p, werte, ergebnis)
        return ergebnis

    def _belegen(self, ergebnis: Dict[str, Groesse], kurz: str, si: float) -> Wert:
        definition = self.d[kurz]
        wert = definition.belegen(Groesse.aus_si(si, definition.einheit))
        ergebnis[definition.id] = wert.groesse
        return wert

    def _handrechnung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                      ergebnis: Dict[str, Groesse]) -> Dict[Zugseite, float]:
        """M_Rd und x/d bei N = 0, N_Rd bei M = 0 -- aus der Linie der Handrechnung."""
        if self.eigene_linie:
            linie = resistenzlinie(
                WAHL, e, p, querschnitt=self.querschnitt, posten=self.posten,
                richtung=Richtung.X, basis=f"{self.id}.hand", vorsatz="Kennzahlen: ",
                ebene=3, wahltitel="Rechenwahl – Kennzahlen")
        else:
            linie = e.befund("mn").massgebend
            p.text("Die Eckpunkte stammen aus der Handrechnung der Tragsicherheit – "
                   "sie rechnet ebenso, von Hand mit Bemessungswerten.")

        p.titel("Biegung und Normalkraft", ebene=3)
        eckpunkt = {q.kennung: q for q in linie.punkte}
        momente: Dict[Zugseite, float] = {}
        for seite in UM_Y:
            kurz = seite.marke
            m = self._auf_der_linie(p, linie, ergebnis, geo.MOMENT, seite.positiv,
                                    f"M_Rd_{kurz}", f"Momentenwiderstand bei N_Ed = 0, Zug {seite}")
            momente[seite] = abs(m)
            if f"x_d_{kurz}" not in self.d:
                p.text(f"Zug {seite} ohne x-Bewehrung → kein d, kein x/d dieser Seite.")
                continue
            punkt = eckpunkt[f"n0_{kurz}"]
            p.formel(self._belegen(ergebnis, f"x_d_{kurz}",
                                   punkt.x.groesse.si / punkt.d.groesse.si),
                     r"\frac{@x}{@d}", {"x": punkt.x, "d": punkt.d},
                     titel=f"Bezogene Druckzonenhöhe bei N_Ed = 0, Zug {seite}",
                     name="Bezogene Druckzonenhöhe")

        for positiv, kurz, wie in ((True, "zug", "Zugwiderstand"),
                                   (False, "druck", "Druckwiderstand")):
            self._auf_der_linie(p, linie, ergebnis, geo.NORMALKRAFT, positiv,
                                f"N_Rd_{kurz}", f"{wie} bei M_Ed = 0")
        return momente

    def _auf_der_linie(self, p: Protokoll, linie, ergebnis: Dict[str, Groesse],
                       achse: geo.Achse, positiv: bool, kurz: str, titel: str) -> float:
        """
        Ein Widerstand auf der Linie, die Gegengroesse null -- hergeleitet, wie
        die Linie ihn findet: als Eckpunkt oder zwischen zweien.

        Getroffen wird sie immer: sie umschliesst den Querschnitt ohne
        Dehnung, N = M = 0, oder geht durch ihn, und jede Gerade durch ihn
        trifft sie (bei einseitiger Bewehrung als Eckpunkt,
        :func:`~opencivil.nachweis.linie.kante`).
        """
        treffer = linie.kante(achse, 0.0, positiv=positiv)
        if treffer is None:
            raise BerechnungsFehler(
                self.id, f"{titel}: die Linie trifft {achse.gegen.name} = 0 nicht.")
        wert = self._belegen(ergebnis, kurz, treffer.wert)
        linie.protokoll_treffer(p, treffer, achse=achse, fest=0.0,
                                basis=f"{self.id}.{kurz}", titel=titel, ergebnis=wert)
        return wert.groesse.si

    def _hoehen(self, e: Eingaben, werte: Zwischenwerte, p: Protokoll,
                beiwerte: Kurvenbeiwerte, seite: Zugseite, *,
                wirksam: bool) -> Optional[Tuple[Wert, Optional[Wert]]]:
        """
        ``d`` der gezogenen Seite und, ohne Buegel (``wirksam``), ``d_v`` --
        hergeleitet wie im Querkraftnachweis; ``None`` ohne Zugbewehrung.
        """
        hoehen = beiwerte.hoehen(seite.positiv)
        if hoehen is None:
            return None
        return protokoll_hoehen(p, werte, e, self.posten,
                                zuglage(beiwerte.lagen, seite.positiv),
                                hoehen[0], hoehen[1] if wirksam else None,
                                seite=seite, zeichen=seite.zeichen)

    def _ohne_buegel(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                     ergebnis: Dict[str, Groesse], momente: Dict[Zugseite, float]) -> None:
        p.titel("Querkraftwiderstand ohne Bügel bei N_Ed = 0", ebene=3)
        p.erklaerung(
            "Ohne Bügel hängt der Widerstand am Moment: am grössten bei M_Ed = 0, "
            "wo die Dehnung null ist, am kleinsten bei M_Ed = M_Rd, wo die "
            "Bewehrung zu fliessen beginnt und die Dehnung f_yd/E_s erreicht. Je "
            "Seite gilt ihre statische Höhe."
        )
        k_g = beiwert_k_g(p, self.id, e["D_max"], e["f_ck"])
        tau_cd = tau_cd_wert(werte, e)
        beiwerte = Kurvenbeiwerte(h=e.g("h").si, lagen=lagen_von(e, self.posten),
                                  einlage=e.g("einlagenhoehe").si,
                                  tau_cd=e["tau_cd"].groesse.si, zugstahl={},
                                  k_g=k_g.groesse.si)

        bei_null: List[Wert] = []
        beim_widerstand: List[Wert] = []
        for seite in UM_Y:
            hoch = seite.zeichen
            hoehen = self._hoehen(e, werte, p, beiwerte, seite, wirksam=True)
            if hoehen is None:
                p.text(f"Zug {seite} ohne x-Bewehrung → kein d, kein Widerstand dieser Seite.")
                continue
            d, d_v = hoehen
            # Der Stahl der aeussersten gezogenen Lage, wie im Querkraftnachweis.
            stahl = self.posten[zuglage(beiwerte.lagen, seite.positiv)][0].stahl
            f_yd, E_s = e[stahlname("f_yd", stahl)], e[stahlname("E_s", stahl)]

            null = widerstand(M_Ed=0.0, N_Ed=0.0, h=beiwerte.h, d=d.groesse.si,
                              d_v=d_v.groesse.si, tau_cd=beiwerte.tau_cd,
                              f_yd=f_yd.groesse.si, E_s=E_s.groesse.si, k_g=beiwerte.k_g,
                              m_Rd=momente[seite])
            v_null = werte.wert(f"V_null_{hoch}", rf"V_{{Rd}}^{{{hoch}}}(M_{{Ed}} = 0)",
                                Groesse.aus_si(null.v_Rd, KN_PRO_M), 1)
            p.formel(v_null, r"@tau_cd \cdot @d_v", {"tau_cd": tau_cd, "d_v": d_v},
                     titel=f"Zug {seite}, M_Ed = 0: ε_v = 0, k_d = 1",
                     referenz="SIA 262:2025, 4.3.3.2.1",
                     name="Querkraftwiderstand ohne Bügel bei M_Ed = 0")
            bei_null.append(v_null)

            voll = widerstand(M_Ed=momente[seite], N_Ed=0.0, h=beiwerte.h,
                              d=d.groesse.si, d_v=d_v.groesse.si, tau_cd=beiwerte.tau_cd,
                              f_yd=f_yd.groesse.si, E_s=E_s.groesse.si, k_g=beiwerte.k_g,
                              m_Rd=momente[seite])
            eps_v = werte.dehnung(f"eps_v_{hoch}", rf"\varepsilon_v^{{{hoch}}}", voll.eps_v,
                                  stellen=3)
            p.formel(eps_v, r"\frac{@f_yd}{@E_s}", {"f_yd": f_yd, "E_s": E_s},
                     titel=f"Zug {seite}, M_Ed = M_Rd: Dehnung beim Fliessbeginn",
                     name="Fliessdehnung")
            v_voll = werte.wert(f"V_voll_{hoch}",
                                rf"V_{{Rd}}^{{{hoch}}}(M_{{Ed}} = M_{{Rd}}^{{{hoch}}})",
                                Groesse.aus_si(voll.v_Rd, KN_PRO_M), 1)
            protokoll_ohne_buegel(p, werte, v_voll, k_d=voll.k_d, eps_v=eps_v, d=d, d_v=d_v,
                                  k_g=k_g, tau_cd=tau_cd, titel=f"Zug {seite}, M_Ed = M_Rd",
                                  zeichen=hoch)
            beim_widerstand.append(v_voll)

        for kurz, teile, titel in (("V_Rd_max", bei_null, "bei M_Ed = 0"),
                                   ("V_Rd_min", beim_widerstand, "bei M_Ed = M_Rd")):
            self._kleinstes(p, ergebnis, kurz, teile,
                            f"Querkraftwiderstand ohne Bügel {titel}, das Kleinere beider Seiten")

    def _mit_buegeln(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Querkraftwiderstand mit Bügeln bei N_Ed = 0", ebene=3)
        p.erklaerung(
            "Mit Bügeln trägt das Fachwerk; gesucht wird ganzgradig zwischen "
            "α_min und α_max die Neigung mit dem grössten Widerstand. Ohne "
            "Normalkraft bleiben die Grenzen, wie sie eingegeben sind."
        )
        b = e.g("b").si
        s_y = buegelteilung_y(self.buegel, b, e.g("menge_y").si)
        if self.buegel.ueber_abstand_y:
            w_sy = e["menge_y"]
        else:
            w_sy = werte.laenge("s_y", "s_{V,y}", s_y)
            p.formel(w_sy, r"\frac{@b}{@n}", {"b": e["b"], "n": e["menge_y"]},
                     titel="Teilung in y aus der Stabzahl")
        alpha_min, alpha_max = self.buegel.grenzen(False)
        beiwerte = Kurvenbeiwerte(h=e.g("h").si, lagen=lagen_von(e, self.posten),
                                  einlage=0.0, tau_cd=0.0, zugstahl={}, k_g=0.0)

        teile: List[Wert] = []
        for seite in UM_Y:
            hoch = seite.zeichen
            hoehen = self._hoehen(e, werte, p, beiwerte, seite, wirksam=False)
            if hoehen is None:
                p.text(f"Zug {seite} ohne x-Bewehrung → kein d, kein Widerstand dieser Seite.")
                continue
            d = hoehen[0]
            q = beste_neigung(neigungen(
                alpha_min=alpha_min, alpha_max=alpha_max, a_s=e.g("a_s_V").si,
                s_x=e.g("s_x").si, s_y=s_y, d=d.groesse.si, f_yd=e.g("f_yd_V").si,
                f_cd=e.g("f_cd").si, k_c=e.g("k_c").si))
            seite_wert = werte.wert(f"V_{hoch}", rf"V_{{Rd}}^{{{hoch}}}(\alpha_{{opt}})",
                                    Groesse.aus_si(q.V_Rd, KN_PRO_M), 1)
            protokoll_mit_buegeln(p, werte, seite_wert, q, e=e, s_y=w_sy, d=d,
                                  alpha_min=alpha_min, alpha_max=alpha_max, seite=seite,
                                  zeichen=hoch)
            teile.append(seite_wert)
        self._kleinstes(p, ergebnis, "V_Rd_buegel", teile,
                        "Querkraftwiderstand mit Bügeln, das Kleinere beider Seiten")

    def _kleinstes(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str,
                   teile: List[Wert], titel: str) -> None:
        """
        Das Kleinere der Seiten mit Zugbewehrung -- bei nur einer sie selbst.
        Eine hat die Platte immer: ohne x-Bewehrung gibt es keine Kennzahlen.
        """
        wert = self._belegen(ergebnis, kurz, min(t.groesse.si for t in teile))
        if len(teile) == 2:
            p.formel(wert, r"\min\left[@a;\ @b\right]", {"a": teile[0], "b": teile[1]},
                     titel=titel, name="Kleinerer Widerstand beider Seiten")
        else:
            p.formel(wert, "@a", {"a": teile[0]}, titel=titel,
                     name="Kleinerer Widerstand beider Seiten")

