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
einer Formel. Mit Bemessungswerten oder charakteristischen, wie die
Tragsicherheit waehlt (:mod:`opencivil.nachweis.qa_stahl_werte`).

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

from typing import Callable, Dict, Sequence

from opencivil.core.berechnung import Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import CM3, EINHEITSLOS, KN, KNM, MIO_MM4, Groesse
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis.qa_stahl_werte import (
    ELASTISCH, NORMALKRAFT, PLASTISCH, ROHR_KLASSE_4, SPANNUNG, WIDERSTANDSMOMENT, Stahlwerte,
    breiten, klassen, stoffbezuege,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.plastisch import DRUCK, Linie
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stabwerk.stabquerschnitt import keine_hauptachsen
from opencivil.stahlbau import klasse as kl
from opencivil.stahlbau import schub
from opencivil.stahlbau.querschnitt import (
    Blechzustand, Elastisch, Stahlquerschnitt, Teil, normale,
)
from opencivil.stahlprofile.bleche import Halterung

REFERENZ_38 = "SIA 263:2013, 5.1.2.1, (38)"
REFERENZ_40 = "SIA 263:2013, 5.1.3, (40)"
REFERENZ_52 = "SIA 263:2013, 5.2.3, (52)"
REFERENZ_55 = "SIA 263:2013, 5.3.2, (55); 4.5.3"
REFERENZ_56 = "SIA 263:2013, 5.3.3, (56); 4.5.3"
REFERENZ_KLASSE = "SIA 263:2013, 4.3.1.3; Tabellen 5a und 5b"


#: Was die Querschnittswerte bedeuten, nach ihrem Symbol.
_BEDEUTUNG = {"A": "Fläche aus Baustahl", "A_{eff}": "Wirksame Fläche",
              "W_{pl}": "Plastisches Widerstandsmoment", "W_{el}": "Elastisches Widerstandsmoment",
              "W_{eff}": "Wirksames Widerstandsmoment"}


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

        bezuege = ([Eingabebezug(k, analyse.id_von(k)) for k in ("A", "I_y", "I_z", "I_yz")]
                   + stoffbezuege(self.stahl))
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
        sw = Stahlwerte(self.stahl, e, self.analyse.wahl)
        self._hinweise(p, e)
        self._teile(p, sw)
        self._normalkraft(p, sw, werte, ergebnis)
        for seite in self.analyse.zugseiten:
            self._biegung(p, sw, werte, ergebnis, seite)
        if self.richtungen:
            self._schub(p, sw, ergebnis)
        return ergebnis

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

    def _teile(self, p: Protokoll, sw: Stahlwerte) -> None:
        p.titel("Teile", ebene=3)
        p.erklaerung(
            "Jedes Teil rechnet mit der Fliessgrenze seiner Dicke: ein Profil mit der seines "
            "dicksten Blechs, eine frei gezeichnete Fläche mit der ihrer kleinsten Breite. Über "
            "40 mm gilt die rechte Spalte der Tabelle 1, auch über 100 mm, wo sie endet.")
        p.annahme("Ein Profil rechnet ganz mit der Fliessgrenze seines dicksten Blechs, eine "
                  "frei gezeichnete Fläche mit der ihrer kleinsten Breite – nach Vorgabe, nicht "
                  "nachgeschlagen.")
        p.ansatz(r"\varepsilon = \sqrt{\frac{235}{f_y}}",
                 titel="Beiwert der Grenzschlankheiten, f_y in N/mm²", referenz=kl.REFERENZ_EPSILON,
                 name="Beiwert ε der Grenzschlankheiten")
        p.tabelle(
            kopf=["Teil", "Baustahl", Mathe(r"t\ [\mathrm{mm}]"), SPANNUNG,
                  Mathe(r"\tau_y\ [\mathrm{N}/\mathrm{mm}^2]"), Mathe(r"\varepsilon"),
                  Mathe(r"A\ [\mathrm{mm}^2]")],
            zeilen=[[t.name, t.flaeche.stoff.name, Mathe(fest(t.dicke, 1)),
                     Mathe(fest(sw.zahl(t.gruppe, "f_y"), 0)),
                     Mathe(fest(sw.zahl(t.gruppe, "tau_y"), 0)),
                     Mathe(fest(sw.eps[t.gruppe], 3)), Mathe(fest(t.netto, 0))]
                    for t in self.stahl.teile],
            titel="Teile aus Baustahl", ausrichtung="llrrrrr")
        ohne = [g.name for g, b in zip(self.stahl.gruppen, sw.bemessung) if not b]
        if ohne:
            p.text(f"Mit charakteristischen Werten, ohne γ_M1: {', '.join(ohne)} – so wählt es "
                   f"die Tragsicherheit.")

    # -- Summen je Gruppe -----------------------------------------------------

    def _summe(self, p: Protokoll, sw: Stahlwerte, werte: Zwischenwerte,
               ergebnis: Dict[str, Groesse], kurz: str, groessen: Sequence[float],
               symbol: str, *, vorzeichen: float = 1.0, titel: str, referenz: str) -> None:
        """
        ``Σ f_y X/γ_M1`` -- ``groessen`` je Gruppe ``X``: Flaechen in mm²,
        Widerstandsmomente in mm³, nach dem Symbol (``A`` oder ``W``). Mit
        einer Gruppe als Formel, sonst als Tabelle.
        """
        moment = symbol.startswith("W")
        si = vorzeichen * sum(f * x for f, x in zip(sw.f, groessen)) * (1e-3 if moment else 1.0)
        wert = self._belegen(ergebnis, kurz, si)
        minus = "-" if vorzeichen < 0.0 else ""
        if len(groessen) == 1:
            name = f"{kurz}_{_ohne_klammern(symbol)}"
            x = (werte.wert(name, symbol, Groesse.aus_si(groessen[0] * 1e-9, CM3),
                            beschreibung=_BEDEUTUNG[symbol]) if moment
                 else werte.flaeche(name, symbol, groessen[0] * 1e-6, _BEDEUTUNG[symbol]))
            vorlage, eingaben = sw.formel(0, "@X")
            p.formel(wert, minus + vorlage, {**eingaben, "X": x}, titel=titel, referenz=referenz,
                     name=PLASTISCH if moment else NORMALKRAFT)
            return
        einheit, x_einheit = ((r"\mathrm{kNm}", r"\mathrm{cm}^3") if moment
                              else (r"\mathrm{kN}", r"\mathrm{mm}^2"))
        p.tabelle(
            kopf=["Baustahl", SPANNUNG, Mathe(r"\gamma_{M1}"), Mathe(rf"{symbol}\ [{x_einheit}]"),
                  Mathe(sw.bruch(r"f_y\, " + symbol) + rf"\ [{einheit}]")],
            zeilen=[[gruppe.name, Mathe(fest(sw.zahl(g, "f_y"), 0)),
                     Mathe(fest(sw.gamma(g), 2)),
                     Mathe(fest(groessen[g] * (1e-3 if moment else 1.0), 1 if moment else 0)),
                     Mathe(fest(sw.f[g] * groessen[g] * (1e-6 if moment else 1e-3), 1))]
                    for g, gruppe in enumerate(self.stahl.gruppen)],
            titel=f"{titel}: je Baustahl", ausrichtung="lrrrr")
        p.wert(wert, titel=f"{titel}, zusammen", referenz=referenz)

    # -- Klassen ----------------------------------------------------------------

    def _klasse(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str,
                zustaende: Sequence[Blechzustand], freie: Sequence[Teil], titel: str) -> int:
        """Die Klasse je Blech, als Tabelle -- und die des Querschnitts: die unguenstigste."""
        klasse, wer = klassen(p, zustaende, freie, titel)
        p.wert(self._belegen(ergebnis, kurz, float(klasse)),
               titel=f"Querschnittsklasse – massgebend {wer}" if wer else "Querschnittsklasse",
               referenz=REFERENZ_KLASSE)
        return klasse

    # -- Normalkraft --------------------------------------------------------------

    def _normalkraft(self, p: Protokoll, sw: Stahlwerte, werte: Zwischenwerte,
                     ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Normalkraft", ebene=3)
        flaechen = self.stahl.flaechen()
        self._summe(p, sw, werte, ergebnis, "N_Rd_zug", flaechen, "A",
                    titel="Zugwiderstand, am gezeichneten Querschnitt", referenz=REFERENZ_38)
        zustaende = self.stahl.zustaende(DRUCK, DRUCK, sw.eps)
        klasse = self._klasse(p, ergebnis, "klasse_druck", zustaende,
                              self.stahl.freie_gedrueckt(DRUCK, DRUCK), "Bleche bei Druck")
        if klasse < 4:
            self._summe(p, sw, werte, ergebnis, "N_Rd_druck", flaechen, "A", vorzeichen=-1.0,
                        titel=f"Druckwiderstand in Klasse {klasse}", referenz=REFERENZ_38)
            return
        gefunden = self.stahl.wirksamer(zustaende, DRUCK, sw.eps)
        if gefunden is None:
            p.hinweis(ROHR_KLASSE_4)
            p.wert(self._belegen(ergebnis, "N_Rd_druck", 0.0), titel="Druckwiderstand")
            return
        wirksam, netto = gefunden
        breiten(p, wirksam, "Mitwirkende Breiten in Klasse 4")
        self._summe(p, sw, werte, ergebnis, "N_Rd_druck", netto.flaechen(), "A_{eff}",
                    vorzeichen=-1.0, titel="Druckwiderstand in Klasse 4, am wirksamen Querschnitt",
                    referenz=REFERENZ_55)

    # -- Biegung ----------------------------------------------------------------------

    def _biegung(self, p: Protokoll, sw: Stahlwerte, werte: Zwischenwerte,
                 ergebnis: Dict[str, Groesse], seite: Zugseite) -> None:
        p.titel(f"Biegung, {seite.beschriftung}", ebene=3)
        n = normale(seite)
        quer = "z" if seite.um_y else "y"
        v_pl = self.stahl.starr(sw.f).nulllinie(n)
        brutto = self.stahl.elastisch(n)
        p.wert(werte.laenge(f"{quer}_pl_{seite.value}", rf"{quer}_{{pl}}",
                            v_pl * (n[0] + n[1]) * 1e-3, "Lage der plastischen Nulllinie"),
               titel="Plastische Nulllinie bei N = 0: so viel Kraft gezogen wie gedrückt")
        pl = Linie(n, v_pl)
        zustaende = self.stahl.zustaende(pl, brutto.linie, sw.eps)
        klasse = self._klasse(p, ergebnis, f"klasse_{seite.value}", zustaende,
                              self.stahl.freie_gedrueckt(pl, brutto.linie),
                              f"Bleche bei Biegung, {seite.beschriftung}")
        kurz = f"M_Rd_{seite.value}"
        if klasse <= 2:
            self._summe(p, sw, werte, ergebnis, kurz, self.stahl.plastisch(n, v_pl), "W_{pl}",
                        vorzeichen=seite.vorzeichen,
                        titel=f"Plastischer Widerstand in Klasse {klasse}", referenz=REFERENZ_40)
            return
        if klasse == 3:
            self._elastisch(p, sw, werte, ergebnis, kurz, brutto, sw.e[f"I_{_achse(seite)}"],
                            seite, "W_{el}", "Elastischer Widerstand in Klasse 3", REFERENZ_52)
            return
        gefunden = self.stahl.wirksamer(zustaende, brutto.linie, sw.eps)
        if gefunden is None:
            p.hinweis(ROHR_KLASSE_4)
            p.wert(self._belegen(ergebnis, kurz, 0.0), titel="Momentenwiderstand")
            return
        wirksam, wirksamer = gefunden
        breiten(p, wirksam, "Mitwirkende Breiten in Klasse 4")
        netto = wirksamer.elastisch(n)
        p.wert(werte.laenge(f"e_{seite.value}", rf"e_{{{quer}}}",
                            (netto.v - brutto.v) * (n[0] + n[1]) * 1e-3,
                            "Verschiebung des Schwerpunkts im wirksamen Querschnitt"))
        I = werte.wert(f"I_eff_{seite.value}", r"I_{eff}",
                       Groesse.aus_si(netto.I * 1e-12, MIO_MM4), beschreibung="Wirksames Trägheitsmoment")
        self._elastisch(p, sw, werte, ergebnis, kurz, netto, I, seite, "W_{eff}",
                        "Widerstand in Klasse 4, am wirksamen Querschnitt", REFERENZ_56)

    def _elastisch(self, p: Protokoll, sw: Stahlwerte, werte: Zwischenwerte,
                   ergebnis: Dict[str, Groesse], kurz: str, el: Elastisch, I: Wert,
                   seite: Zugseite, symbol: str, titel: str, referenz: str) -> None:
        """
        Bis die erste Faser fliesst: je Gruppe ``W = I/z`` bis zu ihrer
        weitesten Faser, massgebend das kleinste ``f_y W/γ_M1``.
        """
        gruppen = [g for g, z in enumerate(el.abstaende) if z > 0.0]
        moment, g_min = el.moment(sw.f)
        tag = f"{seite.value}_{_ohne_klammern(symbol)}"
        z = werte.laenge(f"z_{tag}", "z", el.abstaende[g_min] * 1e-3,
                         "Weiteste Faser von der Nulllinie")
        w = werte.wert(f"W_{tag}", symbol, Groesse.aus_si(el.I / el.abstaende[g_min] * 1e-9, CM3),
                       beschreibung=_BEDEUTUNG[symbol])
        wer = f", {self.stahl.gruppen[g_min].name}" if len(gruppen) > 1 else ""
        p.formel(w, r"\frac{@I}{@z}", {"I": I, "z": z},
                 titel=f"Widerstandsmoment bis zur weitesten Faser{wer}", name=WIDERSTANDSMOMENT)
        if len(gruppen) > 1:
            p.text("Mit mehreren Stählen fliesst zuerst die Faser mit dem kleinsten f_y/z: "
                   + ", ".join(f"{self.stahl.gruppen[g].name} {fest(sw.f[g] / el.abstaende[g], 3)}"
                               for g in gruppen) + " N/mm³.")
        vorlage, eingaben = sw.formel(g_min, "@W")
        p.formel(self._belegen(ergebnis, kurz, seite.vorzeichen * moment * 1e-3),
                 ("-" if seite.vorzeichen < 0 else "") + vorlage, {**eingaben, "W": w},
                 titel=titel, referenz=referenz, name=ELASTISCH)

    # -- Querkraft ----------------------------------------------------------------------

    def _schub(self, p: Protokoll, sw: Stahlwerte, ergebnis: Dict[str, Groesse]) -> None:
        querkraft(p, sw, self.stahl, self.richtungen,
                  lambda r, V: self._belegen(ergebnis, f"V_{r}_Rd", V))


def querkraft(p: Protokoll, sw: Stahlwerte, stahl: Stahlquerschnitt, richtungen: Sequence[str],
              belegen: Callable[[str, float], Wert]) -> None:
    """
    Der Querkraftwiderstand der Profile je Richtung, mit seinen Tabellen --
    im Stahl wie im Verbund, wo der Stahl die Querkraft allein traegt.
    ``belegen`` nimmt je Richtung die Summe in N und gibt den Wert der
    Kennzahl zurueck.
    """
    p.titel("Querkraft", ebene=3)
    p.erklaerung(
        "Je Profil allein, ohne Normalkraft und Biegung: kein Blech ist gedrückt, der "
        "Querschnitt rechnet plastisch. Beim I und beim U prüft (42), ob der Steg beulen "
        "kann; tut er es, trägt er nach (13). Die Wände eines Rechteckrohrs tragen je "
        "nach (13). Zusammen tragen die Profile die Summe; frei gezeichnete Flächen "
        "tragen nichts.")
    p.ansatz("V_{Rd} = " + sw.bruch(r"\tau_y\, A_v"), titel="Querkraftwiderstand",
             referenz=schub.REFERENZ_SCHUB, name="Querkraftwiderstand eines Stahlprofils")
    p.ansatz(r"\frac{h - t_f}{t_w} \le \sqrt{\frac{4 E}{f_y}}",
             titel="Beim I und beim U beult der Steg nicht, solange", referenz=schub.REFERENZ_42,
             name="Steg ohne Schubbeulen")
    p.ansatz("V_{Rd} = " + sw.bruch(r"0.9 \sqrt{\tau_{cr}\, \tau_y}\, b\, t") + r" \le "
             + sw.bruch(r"\tau_y\, b\, t") + r" \qquad \tau_{cr} = k_\tau\, 0.9\, E "
             r"\left(\frac{t}{b}\right)^2 \qquad k_\tau = 5.34",
             titel="Schubbeulen des Blechs, ohne Quersteifen", referenz=schub.REFERENZ_BEULEN)
    for r in richtungen:
        zeilen = []
        summe = 0.0
        for t in stahl.profile:
            g = t.gruppe
            s = schub.widerstand(t.flaeche.profil, t.netto, r, f_y=sw.zahl(g, "f_y"),
                                 tau_y=sw.zahl(g, "tau_y"), E=sw.zahl(g, "E_a"))
            V = s.V_Rd(sw.gamma(g)) * 1e-3
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
        p.wert(belegen(r, summe * 1e3),
               titel=f"Querkraftwiderstand in {r}, alle Profile zusammen",
               referenz=schub.REFERENZ_SCHUB)
