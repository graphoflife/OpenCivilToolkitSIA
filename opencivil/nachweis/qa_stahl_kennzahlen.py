"""
opencivil/nachweis/qa_stahl_kennzahlen.py -- was ein gezeichneter Stahlquerschnitt aufnimmt, ohne Einwirkung.

VERANTWORTUNG:
Die Kennzahlen eines Querschnitts aus Baustahl nach SIA 263:2013, wie die des
Stahlbetons (:mod:`opencivil.nachweis.qa_kennzahlen`) -- gerechnet immer, ob
es Lastfaelle gibt oder nicht:

* die Querschnittsklasse bei Druck und je Zugseite bei Biegung: je Blech
  jedes Profils nach den Tabellen 5a und 5b, massgebend das unguenstigste
  (4.3.1.3);
* der Zug- und der Druckwiderstand nach (38), in Klasse 4 nach (55) mit der
  wirksamen Flaeche;
* je Zugseite der Momentenwiderstand: plastisch nach (40) in den Klassen 1
  und 2, elastisch nach (52) in Klasse 3, nach (56) mit dem wirksamen
  Querschnitt in Klasse 4;
* mit Profilen der Querkraftwiderstand in z und, wo auch um z gebogen wird,
  in y -- je Profil allein (:mod:`opencivil.stahlbau.schub`), zusammen.

Knicken und Kippen gehoeren dem Stab: hier stehen die Widerstaende des
Querschnitts. Die Rechnung selbst steht in :mod:`opencivil.stahlbau`; hier
nur, was sie in die Herleitung schreibt. Mit mehreren Staehlen oder Dicken
rechnet jede Gruppe mit ihrer Fliessgrenze; eine Tabelle zeigt sie, statt
einer Formel.

WAS FEHLT -- GRAU IN DER HERLEITUNG:
* Frei gezeichnete Flaechen: ihr Beulen ist nicht geprueft, Querkraft tragen
  sie nicht (:mod:`opencivil.stahlbau.querschnitt`). Ohne Profil gibt es
  darum keinen Querkraftwiderstand.
* Ein Rundrohr der Klasse 4: SIA 263 nennt dafuer keine mitwirkende Breite;
  der Widerstand dieser Beanspruchung steht auf null, und ein Satz sagt,
  warum.
* Der Nettoquerschnitt (39): gerechnet wird der gezeichnete Querschnitt nach
  (38). Ein Loch zeichnet man als Aussparung; dass dort die Zugfestigkeit
  nach (39) massgebend werden kann, prueft das Werkzeug nicht (nach Vorgabe,
  nicht nachgeschlagen).
* Sind y und z keine Hauptachsen, sagt es der Satz des Balkensystems
  (:func:`~opencivil.stabwerk.stabquerschnitt.keine_hauptachsen`).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import CM3, EINHEITSLOS, KN, KNM, MIO_MM4, Groesse
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stabwerk.stabquerschnitt import keine_hauptachsen
from opencivil.stahlbau import klasse as kl
from opencivil.stahlbau import schub
from opencivil.stahlbau.querschnitt import Blechzustand, Elastisch, Stahlquerschnitt, Wirksam
from opencivil.stahlprofile.bleche import Halterung

#: Was die Kennzahlen je Baustahl lesen.
KENNWERTE = ("f_y", "f_y_dick", "tau_y", "tau_y_dick", "gamma_M1", "E_a")

REFERENZ_38 = "SIA 263:2013, 5.1.2.1, (38)"
REFERENZ_40 = "SIA 263:2013, 5.1.3, (40)"
REFERENZ_52 = "SIA 263:2013, 5.2.3, (52)"
REFERENZ_55 = "SIA 263:2013, 5.3.2, (55); 4.5.3"
REFERENZ_56 = "SIA 263:2013, 5.3.3, (56); 4.5.3"
REFERENZ_KLASSE = "SIA 263:2013, 4.3.1.3; Tabellen 5a und 5b"

#: Warum ein Rundrohr der Klasse 4 nichts traegt -- siehe Dateikopf.
ROHR_KLASSE_4 = ("Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht – SIA 263 nennt dafür "
                 "keine mitwirkende Breite. Der Widerstand steht darum auf null.")

_SPANNUNG = Mathe(r"f_y\ [\mathrm{N}/\mathrm{mm}^2]")


def _normale(seite: Zugseite) -> Tuple[float, float]:
    """Die Richtung zur gezogenen Seite -- genau 0 oder ±1."""
    return float(round(math.cos(seite.psi))), float(round(math.sin(seite.psi)))


def _ohne_klammern(symbol: str) -> str:
    """Ein Symbol als Teil einer Kennung: «W_{pl}» wird «W_pl»."""
    return symbol.replace("{", "").replace("}", "")


def _achse(seite: Zugseite) -> str:
    """Um welche Achse ein Moment diese Seite zieht."""
    return "y" if seite.um_y else "z"


class KennzahlenStahlQA(Kennzahlprozedur):
    """Die Kennzahlen eines Stahlquerschnitts -- siehe Dateikopf."""

    THEMA = "Kennzahlen"

    def __init__(self, analyse: Querschnittsanalyse) -> None:
        self.analyse = analyse
        self.stahl = Stahlquerschnitt(analyse.flaechen, analyse.eltern)
        basis = f"{analyse.id}.kennzahlen"
        dazu = self.anlegen(basis)
        dazu("klasse_druck", r"\mathrm{QK}^{-}", EINHEITSLOS, "Querschnittsklasse bei Druck",
             "Querschnittsklasse, Druck", "das ungünstigste gedrückte Blech",
             stellen=0, referenz=REFERENZ_KLASSE)
        for seite in analyse.zugseiten:
            dazu(f"klasse_{seite.value}", rf"\mathrm{{QK}}_{{{_achse(seite)}}}^{{{seite.zeichen}}}",
                 EINHEITSLOS, f"Querschnittsklasse bei Biegung, {seite.beschriftung}",
                 f"Querschnittsklasse, {seite.beschriftung}", "das ungünstigste gedrückte Blech",
                 stellen=0, referenz=REFERENZ_KLASSE)
        rohr = any(b.halterung is Halterung.ROHR for t in self.stahl.profile for b in t.bleche)
        nachsatz = " – ein Rundrohr der Klasse 4: null" if rohr else ""
        dazu("N_Rd_zug", r"N_{Rd}^{+}", KN, "Zugwiderstand des Querschnitts", "Zugwiderstand",
             "am gezeichneten Querschnitt", referenz=REFERENZ_38)
        dazu("N_Rd_druck", r"N_{Rd}^{-}", KN, "Druckwiderstand des Querschnitts, ohne Knicken",
             "Druckwiderstand", f"ohne Knicken, in Klasse 4 am wirksamen Querschnitt{nachsatz}")
        for seite in analyse.zugseiten:
            dazu(f"M_Rd_{seite.value}", rf"M_{{{_achse(seite)},Rd}}^{{{seite.zeichen}}}", KNM,
                 f"Momentenwiderstand bei N = 0, {seite.beschriftung}",
                 f"Momentenwiderstand, {seite.beschriftung}",
                 f"ohne Kippen – plastisch, elastisch oder wirksam nach der Klasse{nachsatz}")
        # Querkraft tragen nur Profile; in y nur, wo auch um z gebogen wird.
        self.richtungen = ([] if not self.stahl.profile
                           else ["z", "y"] if Zugseite.LINKS in analyse.zugseiten else ["z"])
        for r in self.richtungen:
            dazu(f"V_{r}_Rd", rf"V_{{{r},Rd}}", KN, f"Querkraftwiderstand in {r}, allein",
                 f"Querkraftwiderstand in {r}", "je Profil allein, zusammen – ohne freie Flächen",
                 referenz=schub.REFERENZ_SCHUB)

        stoffe = {g.stoff.id: g.stoff for g in self.stahl.gruppen}.values()
        bezuege = ([Eingabebezug(k, analyse.id_von(k)) for k in ("A", "I_y", "I_z", "I_yz")]
                   + [stoff.bezug(k) for stoff in stoffe for k in KENNWERTE])
        super().__init__(basis, bezuege=bezuege, titel=f"Kennzahlen – {analyse.name}",
                         abschnitt=analyse.abschnitt)

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was der Stahlquerschnitt aufnimmt, ohne Bezug auf einen Lastfall: die "
            "Querschnittsklasse bei Druck und bei Biegung, die Widerstände des Querschnitts "
            "gegen Zug, Druck und Biegung und, mit Profilen, gegen Querkraft. Knicken und "
            "Kippen gehören dem Stab und sind hier nicht dabei.")
        werte = Zwischenwerte(self.id)
        ergebnis: Dict[str, Groesse] = {}
        self._hinweise(p, e)
        self._teile(p, e)
        self._normalkraft(p, e, werte, ergebnis)
        for seite in self.analyse.zugseiten:
            self._biegung(p, e, werte, ergebnis, seite)
        if self.richtungen:
            self._schub(p, e, ergebnis)
        return ergebnis

    # -- Kennwerte je Gruppe --------------------------------------------------

    def _wert(self, e: Eingaben, g: int, kurz: str) -> Wert:
        """Ein Kennwert der Gruppe ``g``, in ihrer Dicke -- ``gamma_M1`` und ``E_a`` in jeder."""
        gruppe = self.stahl.gruppen[g]
        name = kurz if kurz in ("gamma_M1", "E_a") else gruppe.kennwert(kurz)
        return e[gruppe.stoff.eingabename(name)]

    def _zahl(self, e: Eingaben, g: int, kurz: str) -> float:
        """Derselbe als Zahl, Spannungen in N/mm²."""
        return self._wert(e, g, kurz).groesse.si / (1.0 if kurz == "gamma_M1" else 1e6)

    def _f_yd(self, e: Eingaben) -> List[float]:
        return [self._zahl(e, g, "f_y") / self._zahl(e, g, "gamma_M1")
                for g in range(len(self.stahl.gruppen))]

    def _eps(self, e: Eingaben) -> List[float]:
        return [kl.epsilon(self._zahl(e, g, "f_y")) for g in range(len(self.stahl.gruppen))]

    # -- Was fehlt, die Teile -------------------------------------------------

    def _hinweise(self, p: Protokoll, e: Eingaben) -> None:
        freie = self.stahl.freie
        if freie:
            namen = ", ".join(f"«{t.flaeche.name}»" for t in freie)
            schub_satz = ("Querkraft tragen nur die Profile." if self.stahl.profile else
                          "Querkraft tragen nur Profile – ohne Profil steht kein "
                          "Querkraftwiderstand da.")
            p.hinweis(f"Frei gezeichnet: {namen}. Wie diese Flächen gehalten sind, weiss das "
                      f"Werkzeug nicht: wo sie gedrückt sind, rechnet der Querschnitt höchstens "
                      f"elastisch, in Klasse 3, und ihr Beulen ist nicht geprüft. {schub_satz}")
        text = keine_hauptachsen(
            f"Querschnittsanalyse «{self.analyse.name}»",
            *(e.g(k).si for k in ("I_y", "I_z", "I_yz")), was="den Querschnitt",
            folge="Die Widerstände gelten mit der Nulllinie parallel zu y oder z und sind "
                  "darum nur genähert.")
        if text:
            p.hinweis(text)
        p.annahme("Den Nettoquerschnitt nach (39) prüft das Werkzeug nicht: gerechnet wird der "
                  "gezeichnete Querschnitt nach (38) – nach Vorgabe, nicht nachgeschlagen.")

    def _teile(self, p: Protokoll, e: Eingaben) -> None:
        p.titel("Teile", ebene=3)
        p.erklaerung(
            "Jedes Teil rechnet mit der Fliessgrenze seiner Dicke: ein Profil mit der seines "
            "dicksten Blechs, eine frei gezeichnete Fläche mit der ihrer kleinsten Breite. Über "
            "40 mm gilt die rechte Spalte der Tabelle 1, auch über 100 mm, wo sie endet.")
        p.annahme("Ein Profil rechnet ganz mit der Fliessgrenze seines dicksten Blechs, eine "
                  "frei gezeichnete Fläche mit der ihrer kleinsten Breite – nach Vorgabe, nicht "
                  "nachgeschlagen.")
        eps = self._eps(e)
        p.ansatz(r"\varepsilon = \sqrt{\frac{235}{f_y}}",
                 titel="Beiwert der Grenzschlankheiten, f_y in N/mm²", referenz=kl.REFERENZ_EPSILON)
        p.tabelle(
            kopf=["Teil", "Baustahl", Mathe(r"t\ [\mathrm{mm}]"), _SPANNUNG,
                  Mathe(r"\tau_y\ [\mathrm{N}/\mathrm{mm}^2]"), Mathe(r"\varepsilon"),
                  Mathe(r"A\ [\mathrm{mm}^2]")],
            zeilen=[[t.name, t.flaeche.stoff.name, Mathe(fest(t.dicke, 1)),
                     Mathe(fest(self._zahl(e, t.gruppe, "f_y"), 0)),
                     Mathe(fest(self._zahl(e, t.gruppe, "tau_y"), 0)),
                     Mathe(fest(eps[t.gruppe], 3)), Mathe(fest(t.netto, 0))]
                    for t in self.stahl.teile],
            titel="Teile aus Baustahl", ausrichtung="llrrrrr")

    # -- Summen je Gruppe -----------------------------------------------------

    def _summe(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
               ergebnis: Dict[str, Groesse], kurz: str, groessen: Sequence[float],
               symbol: str, *, vorzeichen: float = 1.0, titel: str, referenz: str) -> None:
        """
        ``Σ f_y X/γ_M1`` -- ``groessen`` je Gruppe ``X``: Flaechen in mm²,
        Widerstandsmomente in mm³, nach dem Symbol (``A`` oder ``W``). Mit
        einer Gruppe als Formel, sonst als Tabelle.
        """
        moment = symbol.startswith("W")
        f_yd = self._f_yd(e)
        si = vorzeichen * sum(f * x for f, x in zip(f_yd, groessen)) * (1e-3 if moment else 1.0)
        wert = self._belegen(ergebnis, kurz, si)
        minus = "-" if vorzeichen < 0.0 else ""
        if len(groessen) == 1:
            name = f"{kurz}_{_ohne_klammern(symbol)}"
            x = (werte.wert(name, symbol, Groesse.aus_si(groessen[0] * 1e-9, CM3)) if moment
                 else werte.flaeche(name, symbol, groessen[0] * 1e-6))
            p.formel(wert, rf"{minus}\frac{{@f_y \cdot @X}}{{@gamma_M1}}",
                     {"f_y": self._wert(e, 0, "f_y"), "X": x,
                      "gamma_M1": self._wert(e, 0, "gamma_M1")}, titel=titel, referenz=referenz)
            return
        einheit, x_einheit = ((r"\mathrm{kNm}", r"\mathrm{cm}^3") if moment
                              else (r"\mathrm{kN}", r"\mathrm{mm}^2"))
        p.tabelle(
            kopf=["Baustahl", _SPANNUNG, Mathe(r"\gamma_{M1}"), Mathe(rf"{symbol}\ [{x_einheit}]"),
                  Mathe(rf"f_y\, {symbol}/\gamma_{{M1}}\ [{einheit}]")],
            zeilen=[[gruppe.name, Mathe(fest(self._zahl(e, g, "f_y"), 0)),
                     Mathe(fest(self._zahl(e, g, "gamma_M1"), 2)),
                     Mathe(fest(groessen[g] * (1e-3 if moment else 1.0), 1 if moment else 0)),
                     Mathe(fest(f_yd[g] * groessen[g] * (1e-6 if moment else 1e-3), 1))]
                    for g, gruppe in enumerate(self.stahl.gruppen)],
            titel=f"{titel}: je Baustahl", ausrichtung="lrrrr")
        p.wert(wert, titel=f"{titel}, zusammen", referenz=referenz)

    # -- Klassen ----------------------------------------------------------------

    def _klasse(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str,
                zustaende: Sequence[Blechzustand], freie: Sequence, titel: str) -> int:
        """Die Klasse je Blech, als Tabelle -- und die des Querschnitts: die unguenstigste."""
        if zustaende:
            p.tabelle(
                kopf=["Blech", "Tabelle", Mathe(r"c/t"), Mathe(r"\alpha"), Mathe(r"\psi"),
                      Mathe(r"\text{Grenzen}\ 1 / 2 / 3"), "Klasse"],
                zeilen=[self._zeile(z) for z in zustaende], titel=titel,
                ausrichtung="llrrrrr")
        kandidaten = ([(z.klasse, z.name) for z in zustaende]
                      + [(3, f"«{f.flaeche.name}»") for f in freie])
        klasse = max((k for k, _ in kandidaten), default=1)
        wer = next((name for k, name in kandidaten if k == klasse), "") if klasse > 1 else ""
        if freie:
            p.text("Gedrückt und frei gezeichnet: "
                   + ", ".join(f"«{f.flaeche.name}»" for f in freie) + " – höchstens Klasse 3.")
        p.wert(self._belegen(ergebnis, kurz, float(klasse)),
               titel=f"Querschnittsklasse – massgebend {wer}" if wer else "Querschnittsklasse",
               referenz=REFERENZ_KLASSE)
        return klasse

    @staticmethod
    def _zeile(z: Blechzustand) -> List:
        rohr = z.blech.halterung is Halterung.ROHR
        tabelle = z.blech.halterung.tabelle.replace("Tabelle ", "")
        if z.frei and z.psi is not None and z.psi < 1.0:
            tabelle += ", freier Rand gedrückt"
        return [z.name, f"{tabelle}, D/t" if rohr else tabelle,
                Mathe(rf"{fest(z.blech.c, 1)}/{fest(z.blech.t, 1)} = {fest(z.schlankheit, 1)}"),
                Mathe("–" if rohr else fest(z.alpha, 2)),
                Mathe("–" if rohr or z.psi is None else fest(z.psi, 2)),
                Mathe(" / ".join("–" if math.isinf(g) else fest(g, 1) for g in z.grenzen.werte)),
                Mathe(f"{z.klasse}")]

    def _wirksam(self, p: Protokoll, e: Eingaben, zustaende: Sequence[Blechzustand],
                 n: Optional[Tuple[float, float]], v_el: float = 0.0) -> Optional[List[Wirksam]]:
        """
        Die mitwirkenden Breiten der Bleche in Klasse 4 -- ``None`` mit einem
        Rundrohr darunter (siehe Dateikopf).
        """
        vierte = [z for z in zustaende if z.klasse == 4]
        if any(z.blech.halterung is Halterung.ROHR for z in vierte):
            return None
        eps = self._eps(e)
        wirksam = [self.stahl.wirksam(z, n, eps[z.teil.gruppe], v_el) for z in vierte]
        p.ansatz(r"\bar{\lambda}_p = \frac{b/t}{28.4\, \varepsilon \sqrt{k}} \qquad "
                 r"\rho = \frac{0.9}{\bar{\lambda}_p} \le 1 \qquad b_{eff} = \rho\, b_c",
                 titel="Mitwirkende Breite, b zwischen den theoretischen Scheibenschnittlinien",
                 referenz=kl.REFERENZ_BREITE)
        if any(w.zustand.blech.kasten for w in wirksam):
            p.ansatz(r"\rho = \frac{\bar{\lambda}_p - 0.055\,(3 + \psi)}{\bar{\lambda}_p^2} \le 1",
                     titel="Im Kasten, hier im Rechteckrohr", referenz=kl.REFERENZ_KASTEN)
        p.tabelle(
            kopf=["Blech", Mathe(r"b\ [\mathrm{mm}]"), Mathe(r"\psi"), Mathe("k"),
                  Mathe(r"\bar{\lambda}_p"), Mathe(r"\rho"), Mathe(r"b_c\ [\mathrm{mm}]"),
                  Mathe(r"b_{eff}\ [\mathrm{mm}]")],
            zeilen=[[w.zustand.name, Mathe(fest(w.zustand.blech.b, 1)), Mathe(fest(w.psi, 2)),
                     Mathe(fest(w.k, 3)), Mathe(fest(w.lambda_p, 3)), Mathe(fest(w.rho, 3)),
                     Mathe(fest(w.b_c, 1)), Mathe(fest(w.b_eff, 1))] for w in wirksam],
            titel="Mitwirkende Breiten in Klasse 4", ausrichtung="lrrrrrrr")
        p.annahme("Der wirksame Querschnitt entsteht in einem Schritt aus den Spannungen des "
                  "Bruttoquerschnitts; je Blech fällt ein Streifen der gedrückten Zone weg, beim "
                  "einseitig gehaltenen am freien Ende – nach Vorgabe, nicht nachgeschlagen.")
        return wirksam

    # -- Normalkraft --------------------------------------------------------------

    def _normalkraft(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Normalkraft", ebene=3)
        flaechen = self.stahl.flaechen()
        self._summe(p, e, werte, ergebnis, "N_Rd_zug", flaechen, "A",
                    titel="Zugwiderstand, am gezeichneten Querschnitt", referenz=REFERENZ_38)
        zustaende = self.stahl.zustaende(None, self._eps(e))
        klasse = self._klasse(p, ergebnis, "klasse_druck", zustaende,
                              self.stahl.freie_gedrueckt(None), "Bleche bei Druck")
        if klasse < 4:
            self._summe(p, e, werte, ergebnis, "N_Rd_druck", flaechen, "A", vorzeichen=-1.0,
                        titel=f"Druckwiderstand in Klasse {klasse}", referenz=REFERENZ_38)
            return
        wirksam = self._wirksam(p, e, zustaende, None)
        if wirksam is None:
            p.hinweis(ROHR_KLASSE_4)
            p.wert(self._belegen(ergebnis, "N_Rd_druck", 0.0), titel="Druckwiderstand")
            return
        weg = [0.0] * len(flaechen)
        for w in wirksam:
            if w.streifen:
                weg[w.zustand.teil.gruppe] += (w.b_c - w.b_eff) * w.zustand.blech.t
        self._summe(p, e, werte, ergebnis, "N_Rd_druck",
                    [a - d for a, d in zip(flaechen, weg)], "A_{eff}", vorzeichen=-1.0,
                    titel="Druckwiderstand in Klasse 4, am wirksamen Querschnitt",
                    referenz=REFERENZ_55)

    # -- Biegung ----------------------------------------------------------------------

    def _biegung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                 ergebnis: Dict[str, Groesse], seite: Zugseite) -> None:
        p.titel(f"Biegung, {seite.beschriftung}", ebene=3)
        n = _normale(seite)
        quer = "z" if seite.um_y else "y"
        v_pl = self.stahl.nulllinie(n, self._f_yd(e))
        brutto = self.stahl.elastisch(n)
        p.wert(werte.laenge(f"{quer}_pl_{seite.value}", rf"{quer}_{{pl}}",
                            v_pl * (n[0] + n[1]) * 1e-3, "Lage der plastischen Nulllinie"),
               titel="Plastische Nulllinie bei N = 0: so viel Kraft gezogen wie gedrückt")
        zustaende = self.stahl.zustaende(n, self._eps(e), v_pl, brutto.v)
        klasse = self._klasse(p, ergebnis, f"klasse_{seite.value}", zustaende,
                              self.stahl.freie_gedrueckt(n, v_pl, brutto.v),
                              f"Bleche bei Biegung, {seite.beschriftung}")
        kurz = f"M_Rd_{seite.value}"
        if klasse <= 2:
            self._summe(p, e, werte, ergebnis, kurz, self.stahl.plastisch(n, v_pl), "W_{pl}",
                        vorzeichen=seite.vorzeichen,
                        titel=f"Plastischer Widerstand in Klasse {klasse}", referenz=REFERENZ_40)
            return
        if klasse == 3:
            self._elastisch(p, e, werte, ergebnis, kurz, brutto, e[f"I_{_achse(seite)}"],
                            seite, "W_{el}", "Elastischer Widerstand in Klasse 3", REFERENZ_52)
            return
        wirksam = self._wirksam(p, e, zustaende, n, brutto.v)
        if wirksam is None:
            p.hinweis(ROHR_KLASSE_4)
            p.wert(self._belegen(ergebnis, kurz, 0.0), titel="Momentenwiderstand")
            return
        netto = self.stahl.elastisch(n, [(w.zustand.teil.gruppe, w.streifen)
                                         for w in wirksam if w.streifen])
        p.wert(werte.laenge(f"e_{seite.value}", rf"e_{{{quer}}}",
                            (netto.v - brutto.v) * (n[0] + n[1]) * 1e-3,
                            "Verschiebung des Schwerpunkts im wirksamen Querschnitt"))
        I = werte.wert(f"I_eff_{seite.value}", r"I_{eff}",
                       Groesse.aus_si(netto.I * 1e-12, MIO_MM4))
        self._elastisch(p, e, werte, ergebnis, kurz, netto, I, seite, "W_{eff}",
                        "Widerstand in Klasse 4, am wirksamen Querschnitt", REFERENZ_56)

    def _elastisch(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                   ergebnis: Dict[str, Groesse], kurz: str, el: Elastisch, I: Wert,
                   seite: Zugseite, symbol: str, titel: str, referenz: str) -> None:
        """
        Bis die erste Faser fliesst: je Gruppe ``W = I/z`` bis zu ihrer
        weitesten Faser, massgebend das kleinste ``f_y W/γ_M1``.
        """
        gruppen = [g for g, z in enumerate(el.abstaende) if z > 0.0]
        f_yd = self._f_yd(e)
        moment, g_min = el.moment(f_yd)
        tag = f"{seite.value}_{_ohne_klammern(symbol)}"
        z = werte.laenge(f"z_{tag}", "z", el.abstaende[g_min] * 1e-3,
                         "Weiteste Faser von der Nulllinie")
        w = werte.wert(f"W_{tag}", symbol, Groesse.aus_si(el.I / el.abstaende[g_min] * 1e-9, CM3))
        wer = f", {self.stahl.gruppen[g_min].name}" if len(gruppen) > 1 else ""
        p.formel(w, r"\frac{@I}{@z}", {"I": I, "z": z},
                 titel=f"Widerstandsmoment bis zur weitesten Faser{wer}")
        if len(gruppen) > 1:
            p.text("Mit mehreren Stählen fliesst zuerst die Faser mit dem kleinsten f_y/z: "
                   + ", ".join(f"{self.stahl.gruppen[g].name} {fest(f_yd[g] / el.abstaende[g], 3)}"
                               for g in gruppen) + " N/mm³.")
        p.formel(self._belegen(ergebnis, kurz, seite.vorzeichen * moment * 1e-3),
                 rf"{'-' if seite.vorzeichen < 0 else ''}\frac{{@f_y \cdot @W}}{{@gamma_M1}}",
                 {"f_y": self._wert(e, g_min, "f_y"), "W": w,
                  "gamma_M1": self._wert(e, g_min, "gamma_M1")}, titel=titel, referenz=referenz)

    # -- Querkraft ----------------------------------------------------------------------

    def _schub(self, p: Protokoll, e: Eingaben, ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Querkraft", ebene=3)
        p.erklaerung(
            "Je Profil allein, ohne Normalkraft und Biegung: kein Blech ist gedrückt, der "
            "Querschnitt rechnet plastisch. Beim I und beim U prüft (42), ob der Steg beulen "
            "kann; tut er es, trägt er nach (13). Die Wände eines Rechteckrohrs tragen je "
            "nach (13). Zusammen tragen die Profile die Summe; frei gezeichnete Flächen "
            "tragen nichts.")
        p.ansatz(r"V_{Rd} = \frac{\tau_y\, A_v}{\gamma_{M1}}", titel="Querkraftwiderstand",
                 referenz=schub.REFERENZ_SCHUB)
        p.ansatz(r"\frac{h - t_f}{t_w} \le \sqrt{\frac{4 E}{f_y}}",
                 titel="Beim I und beim U beult der Steg nicht, solange", referenz=schub.REFERENZ_42)
        p.ansatz(r"V_{Rd} = \frac{0.9 \sqrt{\tau_{cr}\, \tau_y}\, b\, t}{\gamma_{M1}} \le "
                 r"\frac{\tau_y\, b\, t}{\gamma_{M1}} \qquad \tau_{cr} = k_\tau\, 0.9\, E "
                 r"\left(\frac{t}{b}\right)^2 \qquad k_\tau = 5.34",
                 titel="Schubbeulen des Blechs, ohne Quersteifen", referenz=schub.REFERENZ_BEULEN)
        for r in self.richtungen:
            zeilen = []
            summe = 0.0
            for t in self.stahl.profile:
                g = t.gruppe
                s = schub.widerstand(t.flaeche.profil, t.netto, r, f_y=self._zahl(e, g, "f_y"),
                                     tau_y=self._zahl(e, g, "tau_y"), E=self._zahl(e, g, "E_a"))
                V = s.V_Rd(self._zahl(e, g, "gamma_M1")) * 1e-3
                summe += V
                teile = []
                if s.steg is not None:
                    zeichen = r"\le" if s.steg[0] <= s.steg[1] else ">"
                    teile.append(rf"{fest(s.steg[0], 1)} {zeichen} {fest(s.steg[1], 1)}")
                if s.beulen is not None:
                    teile.append(rf"\tau_{{cr}} = {fest(s.beulen.tau_cr, 0)}")
                pruefung = r"\quad ".join(teile) or "–"
                zeilen.append([t.name, Mathe(s.formel), Mathe(fest(s.flaeche, 0)),
                               Mathe(pruefung), Mathe(fest(s.tau, 0)), s.herkunft,
                               Mathe(fest(V, 1))])
            p.tabelle(
                kopf=["Profil", Mathe(r"A_v\ \text{oder}\ b\, t"), Mathe(r"[\mathrm{mm}^2]"),
                      Mathe(r"\text{Beulen}"), Mathe(r"\tau\ [\mathrm{N}/\mathrm{mm}^2]"),
                      "Stelle", Mathe(r"V_{Rd}\ [\mathrm{kN}]")],
                zeilen=zeilen, titel=f"Querkraft in {r}: je Profil", ausrichtung="llrrrlr")
            p.wert(self._belegen(ergebnis, f"V_{r}_Rd", summe * 1e3),
                   titel=f"Querkraftwiderstand in {r}, alle Profile zusammen",
                   referenz=schub.REFERENZ_SCHUB)
