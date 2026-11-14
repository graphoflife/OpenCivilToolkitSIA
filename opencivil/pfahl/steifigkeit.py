"""
opencivil/pfahl/steifigkeit.py -- wie steif ein Pfahl im Boden steht, und wie er sich verformt.

VERANTWORTUNG:
Die Prozedur :class:`Pfahlsteifigkeit`: der Pfahl als Stab auf Federn
(:mod:`.bettung`), längs und quer. Sie liefert

* die Federn am Kopf mit dem charakteristischen Verformungsmodul E_s,k
  (SIA 267:2013, 5.3.2.8): längs auf Druck k_v und auf Zug k_v,Z, quer bei
  frei drehbarem Kopf k_h, dazu die Steifigkeitsmatrix des Kopfs -- K_HH,
  K_HM, K_MM -- für ein Modell des Tragwerks darüber. Sie hängen an keiner
  Kombination und stehen als Kennzahlen unter dem Pfahl;
* je Kombination die Verläufe über die Tiefe, mit E_s,d = E_s,k / γ_E
  (5.3.2.5): Setzung und Normalkraft, Verschiebung, Verdrehung, Moment,
  Querkraft und Bettungsdruck -- im Befund (:class:`Steifigkeitsbefund`).

DIE FEDERN DES BODENS:
* am Mantel je Meter Pfahl k_l = B · π · D mit B ≈ 0.42 · E_s (Cassan,
  Kap. 12.8) -- null in einer Schicht, deren Mantelreibung als null
  eingegeben ist: Cassan zählt nur die Schicht, in der der Pfahl trägt;
* am Fuss K_b = A_b · R / D = π · D · R / 4 mit R ≈ 4.5 · E_s der Schicht am
  Fuss: Cassan setzt dort σ_F = R · s / D -- nur auf Druck, und nur, wo der
  Fuss trägt (:attr:`~.pfahl.Pfahl.fuss_traegt`);
* quer k_s = E_s / D (SIA 267:2013, 9.5.4.5, (53)), je Meter Pfahl also
  k_s · D = E_s, vom Terrain bis in die Tiefe t_red von null an linear
  wachsend.

DIE FEDERN AM KOPF:
Das System ist linear; abgelesen wird an einer Probelast von 1 MN. Quer
zweimal: mit frei drehbarem Kopf (k_h = H / y_0) und mit eingespanntem
(K_HH = H / y_0, K_HM = M_0 / y_0, M_0 die Reaktion). Weil k_h = K_HH −
K_HM² / K_MM, folgt daraus die Drehfeder K_MM ohne dritte Rechnung.

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
* Die Abminderung nahe dem Terrain, linear von null bis t_red: die Norm
  verlangt nur, k_s dort abzumindern, das Buch sagt, die Stützkraft an der
  Oberfläche sei null (Kap. 12.10).
* Der Mikropfahl mit Cassans Werten für Bohrpfähle.
* Der Querschnitt ungerissen und ohne Bewehrung: beim Bohrpfahl der Beton
  mit E_cm, beim Mikropfahl das Tragglied allein, ohne den Mörtel.
* γ_E = 1.5, der kleinste Wert, den 5.3.2.5 zulässt.
* Längs und quer getrennt: keine Rechnung nach Theorie zweiter Ordnung
  (9.5.3.4.3 verlangt dafür eine eigene Untersuchung).
* Keine Feder am Mantel, wo q_s,k null eingegeben ist; eine Feder am Fuss,
  wo R_a,k aus einem Versuch kommt.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import M, MM, MN, MN_PRO_M, MNM, MNM2, MNM_PRO_RAD, Groesse
from opencivil.core.latex import Mathe, Zelle, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Kennzahl, Wert, WertDef
from opencivil.pfahl import bettung, buch
from opencivil.pfahl.bettung import Strecke
from opencivil.pfahl.boden import Mantel
from opencivil.pfahl.pfahl import Kombination, Kopf, Pfahl, Tragglied

#: Der Widerstandsbeiwert des Verformungsmoduls, wo eine zu kleine
#: Steifigkeit zum Versagen führt -- der kleinste, den die Norm zulässt.
GAMMA_E = 1.5
GAMMA_E_REFERENZ = "SIA 267:2013, 5.3.2.5"

#: Die Probelast am Kopf, an der die Federn abgelesen werden, in N und Nm.
PROBE = 1e6

#: So lang ist ein Element höchstens, gemessen an der elastischen Länge 1/λ.
SCHRITT_LAMBDA = 0.2

#: Die Federn am Kopf, als Kennzahlen: Kurzname, Zeichen, Einheit, Stellen,
#: Beschriftung, Erklärung. Quer zwei Stellen: ein Mikropfahl ist dort rund
#: tausendmal weicher als ein Bohrpfahl, seine Drehfeder etwa 0.15 MNm/rad.
FEDERN = (
    ("k_v", "k_v", MN_PRO_M, 0, "Längsfeder auf Druck",
     "N/w am Kopf, mit E_s,k; der Fuss trägt mit, wo er trägt"),
    ("k_v_zug", "k_{v,Z}", MN_PRO_M, 0, "Längsfeder auf Zug",
     "Z/w am Kopf, mit E_s,k; nur der Mantel"),
    ("k_h", "k_h", MN_PRO_M, 2, "Querfeder, Kopf frei drehbar",
     "H/y am Kopf, der sich frei dreht, mit E_s,k"),
    ("K_HH", "K_{HH}", MN_PRO_M, 2, "Querfeder, Kopf eingespannt",
     "H/y am Kopf, der sich nicht dreht – Steifigkeitsmatrix des Kopfs, mit E_s,k"),
    ("K_HM", "K_{HM}", MN, 2, "Kopplung am Kopf",
     "M/y am eingespannten Kopf – Steifigkeitsmatrix; negativ: das Moment hält gegen "
     "die Drehung"),
    ("K_MM", "K_{MM}", MNM_PRO_RAD, 2, "Drehfeder, Kopf nicht verschoben",
     "M/θ am Kopf, der sich nicht verschiebt – Steifigkeitsmatrix, mit E_s,k"),
)


@dataclass(frozen=True)
class Baugrund:
    """Was die Bettung aus den Eingaben braucht, in SI -- z ab Terrain."""

    grenzen: Tuple[Tuple[float, float], ...]
    E_s: Tuple[float, ...]
    mantel: Tuple[bool, ...]
    """Je Schicht, ob der Mantel in ihr trägt -- sonst hat er längs keine Feder."""

    t_K: float
    L: float
    D: float
    t_red: float

    @property
    def z_F(self) -> float:
        return self.t_K + self.L

    def stuecke(self) -> List[Tuple[int, float, float]]:
        """Je Schicht das Stück des Pfahls in ihr: Schicht, Ober- und Unterkante."""
        return [(i, max(oben, self.t_K), min(unten, self.z_F))
                for i, (oben, unten) in enumerate(self.grenzen)
                if min(unten, self.z_F) > max(oben, self.t_K)]

    def schicht_am_fuss(self) -> int:
        """Die Schicht, auf der der Fuss steht -- an einer Grenze die untere."""
        return next(i for i, (_, unten) in enumerate(self.grenzen) if self.z_F < unten)

    def abminderung(self, z: float) -> float:
        """Wie viel der Bettung quer in der Tiefe z wirkt: bis t_red linear von null an."""
        return min(1.0, z / self.t_red) if self.t_red > 0.0 else 1.0

    def strecken(self, gamma: float) -> List[Strecke]:
        """
        Die Strecken des Pfahls, z ab Kopf, mit E_s / ``gamma``: je Schicht
        eine, an t_red geteilt -- darüber wächst die Bettung quer linear.
        """
        heraus = []
        for i, oben, unten in self.stuecke():
            E = self.E_s[i] / gamma
            laengs = buch.CASSAN_MANTEL * E * math.pi * self.D if self.mantel[i] else 0.0
            punkte = [oben, *([self.t_red] if oben < self.t_red < unten else []), unten]
            heraus += [Strecke(a - self.t_K, b - self.t_K, laengs=laengs,
                               quer=(E * self.abminderung(a), E * self.abminderung(b)))
                       for a, b in zip(punkte, punkte[1:])]
        return heraus

    def fussfeder(self, gamma: float) -> float:
        """K_b = π · D · R / 4 mit R = 4.5 · E_s / ``gamma`` der Schicht am Fuss."""
        return math.pi * self.D * buch.CASSAN_FUSS * self.E_s[self.schicht_am_fuss()] / gamma / 4.0


@dataclass(frozen=True)
class Verlauf:
    """
    Was eine Kombination mit dem Pfahl macht, über die Tiefe ab Terrain, in
    SI. Quer nur, wo eine Querkraft oder ein Moment am Kopf wirkt.
    """

    name: str
    N_Ed: float
    H_Ed: float
    M_Ed: float
    z: List[float]
    w: List[float]
    N: List[float]
    N_b: float
    """Die Kraft der Feder am Fuss."""

    y: Optional[List[float]] = None
    theta: Optional[List[float]] = None
    M: Optional[List[float]] = None
    V: Optional[List[float]] = None
    p: Optional[List[float]] = None
    """Der Bettungsdruck: die Bettungskraft je Meter durch D, in Pa."""

    @property
    def quer(self) -> bool:
        return self.y is not None


@dataclass
class Steifigkeitsbefund:
    """Die Verläufe je Kombination, für Bild und Zusammenfassung."""

    eingespannt: bool
    verlaeufe: List[Verlauf] = field(default_factory=list)


def _extrem(z: Sequence[float], werte: Sequence[float]) -> Tuple[float, float]:
    """Der Wert mit dem grössten Betrag und seine Tiefe."""
    i = max(range(len(werte)), key=lambda k: abs(werte[k]))
    return werte[i], z[i]


class Pfahlsteifigkeit(Prozedur):
    """Siehe Dateikopf."""

    THEMA = "Pfahlsteifigkeit"

    @staticmethod
    def kennung(pfahl: Pfahl) -> str:
        """Unter welcher Kennung die Steifigkeit eines Pfahls rechnet -- und ihr Befund steht."""
        return f"{pfahl.id}.steifigkeit"

    def __init__(self, pfahl: Pfahl, kombinationen: Sequence[Kombination]) -> None:
        self.pfahl = pfahl
        self.kombinationen = list(kombinationen)
        basis = self.kennung(pfahl)
        #: Je Kurzname die Definition einer Feder -- zum Belegen.
        self.d: Dict[str, WertDef] = {}
        #: Dieselben, wie sie unter dem Pfahl stehen.
        self.kennzahlen: List[Kennzahl] = []
        for kurz, symbol, einheit, stellen, beschriftung, erklaerung in FEDERN:
            definition = WertDef(id=f"{basis}.{kurz}", symbol=symbol, einheit=einheit,
                                 beschreibung=beschriftung, stellen=stellen)
            self.d[kurz] = definition
            self.kennzahlen.append(Kennzahl(definition, beschriftung, erklaerung))
        self.stoff = pfahl.beton if pfahl.bohrpfahl else pfahl.stahl
        self.modul = "E_cm" if pfahl.bohrpfahl else "E_s"
        namen = ["D", "L", "t_K", "t_red"]
        if not pfahl.bohrpfahl:
            namen += ["d_a", "dt"] + (["t_r"] if pfahl.tragglied is Tragglied.ROHR else [])
        for i, s in enumerate(pfahl.schichten, start=1):
            namen += [f"d_{i}", f"E_s_{i}"] + ([f"q_s_{i}"] if s.mantel is Mantel.EINGEBEN else [])
        super().__init__(basis, ausgaben=list(self.d.values()),
                         bezuege=[Eingabebezug(n, pfahl.id_von(n)) for n in namen]
                         + [self.stoff.bezug(self.modul)],
                         titel=f"Steifigkeit – {pfahl.name}", abschnitt=pfahl.abschnitt)

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Steifigkeit")
        p.erklaerung(
            "Der Pfahl steht im Boden wie ein Stab auf Federn. Längs halten ihn die "
            "Reibung am Mantel und der Druck am Fuss, quer drückt er gegen den Boden "
            "neben sich. Wie stark die Federn sind, folgt aus dem Verformungsmodul der "
            "Schichten: am Mantel und am Fuss nach Cassan, quer nach der Norm. Die Federn "
            "am Kopf -- wie weit er sich unter einer Last setzt, verschiebt und dreht -- "
            "braucht das Modell des Tragwerks darüber; sie gelten mit dem "
            "charakteristischen Modul. Für die Schnittkräfte rechnet die Norm mit einem "
            "kleineren: in weicherem Boden weicht der Pfahl weiter aus und biegt sich "
            "stärker.")
        werte = Zwischenwerte(self.id)
        EA, EI = self._querschnitt(e, p, werte)
        n = len(self.pfahl.schichten)
        grenzen, oben = [], 0.0
        for i in range(1, n + 1):
            grenzen.append((oben, oben + e.g(f"d_{i}").si))
            oben = grenzen[-1][1]
        # Die Mantelreibung null eingegeben: der Mantel trägt dort nicht, auch elastisch nicht.
        mantel = tuple(s.mantel is not Mantel.EINGEBEN or e.g(f"q_s_{i}").si > 0.0
                       for i, s in enumerate(self.pfahl.schichten, start=1))
        grund = Baugrund(tuple(grenzen), tuple(e.g(f"E_s_{i}").si for i in range(1, n + 1)),
                         mantel, e.g("t_K").si, e.g("L").si, e.g("D").si, e.g("t_red").si)
        self._bettung(e, p, werte, grund)
        lam = (max(grund.E_s) / (4.0 * EI.groesse.si)) ** 0.25
        schritt = min(bettung.SCHRITT, SCHRITT_LAMBDA / lam)
        ergebnis: Dict[str, Groesse] = {}
        self._federn(p, werte, grund, EA.groesse.si, EI.groesse.si, schritt, ergebnis)
        befund = Steifigkeitsbefund(eingespannt=self.pfahl.kopf is Kopf.EINGESPANNT)
        if self.kombinationen:
            self._kombinationen(p, grund, EA.groesse.si, EI.groesse.si, schritt, befund)
        return Ausfuehrung(ergebnis, (), befund)

    def _belegen(self, ergebnis: Dict[str, Groesse], kurz: str, si: float) -> Wert:
        definition = self.d[kurz]
        wert = definition.belegen(Groesse.aus_si(si, definition.einheit))
        ergebnis[definition.id] = wert.groesse
        return wert

    # -- Querschnitt ------------------------------------------------------------

    def _querschnitt(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte) -> Tuple[Wert, Wert]:
        """EA und EI: der Beton des Bohrpfahls, das Tragglied des Mikropfahls."""
        p.titel("Querschnitt", ebene=3)
        E = e[self.stoff.eingabename(self.modul)]
        if self.pfahl.bohrpfahl:
            D = e["D"]
            a, i = math.pi * D.groesse.si ** 2 / 4.0, math.pi * D.groesse.si ** 4 / 64.0
            vorlagen = (r"@E \cdot \frac{\pi \cdot @D^{2}}{4}",
                        r"@E \cdot \frac{\pi \cdot @D^{4}}{64}")
            eingaben = {"E": E, "D": D}
            p.annahme("Der Beton ungerissen und ohne die Bewehrung, mit E_cm -- nach Vorgabe, "
                      "nicht nachgeschlagen. Gerissen ist der Pfahl weicher: die "
                      "Verschiebungen werden grösser, die Momente etwas kleiner.")
        else:
            d_a, dt = e["d_a"], e["dt"]
            aussen = d_a.groesse.si - 2.0 * dt.groesse.si
            eingaben = {"E": E, "d_a": d_a, "dt": dt}
            if self.pfahl.tragglied is Tragglied.ROHR:
                t = e["t_r"]
                innen = d_a.groesse.si - 2.0 * t.groesse.si
                eingaben["t"] = t
                vorlagen = tuple(
                    rf"@E \cdot \frac{{\pi \cdot \left(\left(@d_a - 2 \cdot @dt\right)^{{{k}}}"
                    rf" - \left(@d_a - 2 \cdot @t\right)^{{{k}}}\right)}}{{{nenner}}}"
                    for k, nenner in ((2, 4), (4, 64)))
            else:
                innen = 0.0
                vorlagen = tuple(rf"@E \cdot \frac{{\pi \cdot \left(@d_a - 2 \cdot @dt\right)"
                                 rf"^{{{k}}}}}{{{nenner}}}" for k, nenner in ((2, 4), (4, 64)))
            a = math.pi * (aussen ** 2 - innen ** 2) / 4.0
            i = math.pi * (aussen ** 4 - innen ** 4) / 64.0
            p.annahme("Es trägt nur das Tragglied, nach der Abrostung; der Mörtel zählt nicht "
                      "-- nach Vorgabe, nicht nachgeschlagen, wie beim inneren Widerstand.")
        EA = werte.wert("EA", "EA", Groesse.aus_si(E.groesse.si * a, MN), 0,
                        "Dehnsteifigkeit des Pfahls")
        p.formel(EA, vorlagen[0], eingaben, titel="Dehnsteifigkeit des Pfahls", referenz="",
                 name="Dehnsteifigkeit des Pfahls")
        EI = werte.wert("EI", "EI", Groesse.aus_si(E.groesse.si * i, MNM2), 1,
                        "Biegesteifigkeit des Pfahls")
        p.formel(EI, vorlagen[1], eingaben, titel="Biegesteifigkeit des Pfahls", referenz="",
                 name="Biegesteifigkeit des Pfahls")
        return EA, EI

    # -- Bettung --------------------------------------------------------------

    def _bettung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, grund: Baugrund) -> None:
        """Die Federn des Bodens, charakteristisch: je Schicht als Tabelle, dazu der Fuss."""
        p.titel("Bettung", ebene=3)
        p.ansatz(r"k_l = B \cdot \pi \cdot D \qquad B = 0.42 \cdot E_{s,k}",
                 titel="Feder am Mantel je Meter Pfahl, für Bohrpfähle",
                 referenz=buch.KAP_FEDERN, name="Feder am Pfahlmantel")
        p.ansatz(r"k_s = \frac{E_{s,k}}{D} \qquad k_s \cdot D = E_{s,k}",
                 titel="Bettung quer, je Meter Pfahl", referenz="SIA 267:2013, 9.5.4.5, (53)",
                 name="Bettungsmodul quer zum Pfahl")
        p.ansatz(r"k_s(z) = k_s \cdot \min\left(1;\ \frac{z}{t_{red}}\right)",
                 titel="Bettung quer nahe dem Terrain abgemindert, z ab Terrain",
                 referenz="SIA 267:2013, 9.5.4.5", name="Abgeminderte Bettung am Terrain")
        p.annahme("Wie die Bettung nahe dem Terrain abnimmt, sagt die Norm nicht; hier linear "
                  "von null am Terrain bis zum vollen Wert in t_red -- nach Vorgabe, nicht "
                  f"nachgeschlagen. An der Oberfläche stützt der Boden nicht ({buch.KAP_QUER}).")
        if not self.pfahl.bohrpfahl:
            p.annahme("Cassans Federn gelten für Bohrpfähle; der Mikropfahl rechnet mit "
                      "denselben -- nach Vorgabe, nicht nachgeschlagen.")
        zeilen: List[List[Zelle]] = []
        stuecke = grund.stuecke()
        for i, oben, unten in stuecke:
            E = grund.E_s[i]
            k_l = buch.CASSAN_MANTEL * E * math.pi * grund.D if grund.mantel[i] else 0.0
            zeilen.append([f"{i + 1}: {self.pfahl.schichten[i].name}", Mathe(fest(oben, 2)),
                           Mathe(fest(unten, 2)), Mathe(fest(E / 1e6, 0)),
                           Mathe(fest(k_l / 1e6, 1)), Mathe(fest(E / grund.D / 1e6, 1))])
        p.tabelle(kopf=["Schicht", Mathe(r"z_o\ [\mathrm{m}]"), Mathe(r"z_u\ [\mathrm{m}]"),
                        Mathe(r"E_{s,k}\ [\mathrm{MN/m^2}]"), Mathe(r"k_l\ [\mathrm{MN/m^2}]"),
                        Mathe(r"k_s\ [\mathrm{MN/m^3}]")],
                  zeilen=zeilen, titel="Federn je Schicht, charakteristisch, ohne Abminderung",
                  ausrichtung="lrrrrr")
        ohne = [str(i + 1) for i, _, _ in stuecke if not grund.mantel[i]]
        if ohne:
            p.text(f"Schicht {', '.join(ohne)}: die Mantelreibung ist null eingegeben, der "
                   f"Mantel trägt dort nicht -- auch längs keine Feder. Cassan zählt nur die "
                   f"Schicht, in der der Pfahl trägt ({buch.KAP_FEDERN}).")
        if not self.pfahl.fuss_traegt:
            p.text("Der Fuss trägt nicht: er hat keine Feder.")
            return
        j = grund.schicht_am_fuss()
        K_b = werte.wert("K_b", "K_b", Groesse.aus_si(grund.fussfeder(1.0), MN_PRO_M), 1,
                         "Feder am Fuss")
        p.formel(K_b, r"\frac{\pi \cdot @D \cdot 4.5 \cdot @E}{4}",
                 {"D": e["D"], "E": e[f"E_s_{j + 1}"]},
                 titel=f"Feder am Fuss, in Schicht {j + 1}: A_b · R / D mit R = 4.5 · E_s,k",
                 referenz=buch.KAP_FEDERN, name="Feder am Pfahlfuss")
        if self.pfahl.grundlage.aus_versuch:
            p.annahme("R_a,k kommt aus einem Versuch: der Fuss zählt mit seiner Feder mit -- "
                      "nach Vorgabe, nicht nachgeschlagen.")
        p.text("Der Fuss drückt nur: auf Zug hat er keine Feder.")

    # -- Die Federn am Kopf -------------------------------------------------------

    def _federn(self, p: Protokoll, werte: Zwischenwerte, grund: Baugrund, EA: float, EI: float,
                schritt: float, ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Federn am Kopf", ebene=3)
        p.ansatz(r"EA \cdot w'' = k_l \cdot w \qquad EI \cdot y'''' = -k_s \cdot D \cdot y",
                 titel="Gebetteter Stab: längs die Setzung w, quer die Verschiebung y",
                 referenz=f"{buch.KAP_FEDERN}; {buch.KAP_QUER}", name="Gebetteter Pfahl")
        p.text("Gelöst mit finiten Elementen: Knoten an jeder Grenze einer Schicht und bei "
               "t_red, dazwischen gleich weit, längs mit linearem, quer mit kubischem Ansatz; "
               "die abgeminderte Bettung wächst in jedem Element linear. Mit dem "
               "charakteristischen Verformungsmodul (SIA 267:2013, 5.3.2.8), unter einer "
               "Probelast von 1 MN am Kopf -- das System ist linear, jede Last gibt dieselbe "
               "Feder.")
        p.wert(werte.wert("dz", r"\Delta z", Groesse.aus_si(schritt, M), 3,
                          "Länge der Elemente, höchstens"), referenz="")
        strecken = grund.strecken(1.0)
        K_b = grund.fussfeder(1.0) if self.pfahl.fuss_traegt else 0.0
        eins = r"\frac{1\,\mathrm{MN}}{@w}"
        for kurz, mit_fuss, zeichen, was in (("k_v", True, "w_0", "Druck"),
                                             ("k_v_zug", False, "w_{0,Z}", "Zug")):
            w = bettung.laengs(strecken, EA, K_b if mit_fuss else 0.0, PROBE, schritt).w[0]
            w0 = werte.wert(f"w_{kurz}", zeichen, Groesse.aus_si(w, MM), 3,
                            f"Setzung des Kopfs unter 1 MN {was}")
            p.wert(w0, referenz="")
            p.formel(self._belegen(ergebnis, kurz, PROBE / w), eins, {"w": w0},
                     titel=f"Längsfeder auf {was}", referenz=buch.KAP_FEDERN,
                     name="Längsfeder des Pfahlkopfs")
        frei = bettung.quer(strecken, EI, PROBE, 0.0, eingespannt=False, schritt=schritt)
        starr = bettung.quer(strecken, EI, PROBE, 0.0, eingespannt=True, schritt=schritt)
        y_frei = werte.wert("y_frei", "y_0", Groesse.aus_si(frei.y[0], MM), 3,
                            "Verschiebung des frei drehbaren Kopfs unter H = 1 MN")
        p.wert(y_frei, referenz="")
        k_h = self._belegen(ergebnis, "k_h", PROBE / frei.y[0])
        p.formel(k_h, r"\frac{1\,\mathrm{MN}}{@y}", {"y": y_frei},
                 titel="Querfeder, Kopf frei drehbar", referenz=buch.KAP_QUER,
                 name="Querfeder des frei drehbaren Pfahlkopfs")
        y_fest = werte.wert("y_fest", "y_{0,E}", Groesse.aus_si(starr.y[0], MM), 3,
                            "Verschiebung des eingespannten Kopfs unter H = 1 MN")
        M_fest = werte.wert("M_fest", "M_{0,E}", Groesse.aus_si(starr.M[0], MNM), 3,
                            "Moment am eingespannten Kopf unter H = 1 MN")
        p.wert(y_fest, referenz="")
        p.wert(M_fest, referenz="")
        K_HH = self._belegen(ergebnis, "K_HH", PROBE / starr.y[0])
        p.formel(K_HH, r"\frac{1\,\mathrm{MN}}{@y}", {"y": y_fest},
                 titel="Querfeder, Kopf eingespannt", referenz=buch.KAP_QUER,
                 name="Querfeder des eingespannten Pfahlkopfs")
        K_HM = self._belegen(ergebnis, "K_HM", starr.M[0] / starr.y[0])
        p.formel(K_HM, r"\frac{@M}{@y}", {"M": M_fest, "y": y_fest},
                 titel="Kopplung: das Moment am eingespannten Kopf je Verschiebung",
                 referenz=buch.KAP_QUER, name="Kopplung am Pfahlkopf")
        K_MM = self._belegen(ergebnis, "K_MM", K_HM.groesse.si ** 2
                             / (K_HH.groesse.si - k_h.groesse.si))
        p.formel(K_MM, r"\frac{@K_HM^{2}}{@K_HH - @k_h}",
                 {"K_HM": K_HM, "K_HH": K_HH, "k_h": k_h},
                 titel="Drehfeder, Kopf nicht verschoben: aus k_h = K_HH − K_HM² / K_MM",
                 referenz="", name="Drehfeder des Pfahlkopfs")
        p.text("K_HH, K_HM und K_MM bilden die Steifigkeitsmatrix des Kopfs: H = K_HH · y + "
               "K_HM · θ, M = K_HM · y + K_MM · θ. Das Moment dreht wie H, wenn es über dem "
               "Kopf angreift; K_HM ist darum negativ.")

    # -- Je Kombination -----------------------------------------------------------

    def _kombinationen(self, p: Protokoll, grund: Baugrund, EA: float, EI: float,
                       schritt: float, befund: Steifigkeitsbefund) -> None:
        """Die Verläufe mit E_s,d = E_s,k / γ_E: längs immer, quer, wo eine Last quer wirkt."""
        p.titel("Verformungen und Schnittkräfte je Kombination", ebene=3)
        p.ansatz(r"E_{s,d} = \frac{E_{s,k}}{\gamma_E} \qquad \gamma_E = 1.5",
                 titel="Verformungsmodul der Tragsicherheit: hier führt zu wenig Steifigkeit "
                       "zum Versagen", referenz=GAMMA_E_REFERENZ,
                 name="Bemessungswert des Verformungsmoduls")
        p.annahme("γ_E = 1.5 ist der kleinste Wert, den die Norm zulässt; sie verlangt ihn "
                  "objektbezogen -- nach Vorgabe, nicht nachgeschlagen.")
        p.annahme("Längs und quer getrennt: die Normalkraft verstärkt die Biegung nicht. Wächst "
                  "die Wirkung nicht im Mass der Last, etwa durch Effekte zweiter Ordnung, "
                  "verlangt die Norm eine eigene Untersuchung (SIA 267:2013, 9.5.3.4.3) -- "
                  "hier nach Vorgabe, nicht nachgeschlagen, ohne sie.")
        strecken = grund.strecken(GAMMA_E)
        K_b = grund.fussfeder(GAMMA_E) if self.pfahl.fuss_traegt else 0.0
        eingespannt = befund.eingespannt
        for k in self.kombinationen:
            N, H, M = k.N_Ed.si, k.H_Ed.si, k.M_Ed.si
            laengs = bettung.laengs(strecken, EA, K_b if N >= 0.0 else 0.0, N, schritt)
            z = [grund.t_K + zi for zi in laengs.z]
            felder = {}
            if self.pfahl.quer_belastet(k):
                quer = bettung.quer(strecken, EI, H, M, eingespannt=eingespannt,
                                    schritt=schritt)
                felder = {"y": quer.y, "theta": quer.theta, "M": quer.M, "V": quer.V,
                          "p": [q / grund.D for q in quer.q]}
            befund.verlaeufe.append(Verlauf(k.name, N, H, M, z, laengs.w, laengs.N,
                                            laengs.fusskraft, **felder))
            if eingespannt and M != 0.0:
                p.hinweis(f"{k.name}: der Kopf ist eingespannt -- M_Ed = {M / 1e3:.1f} kNm "
                          f"zählt nicht, das Moment am Kopf ist die Reaktion.")
        self._tabellen(p, befund)

    def _tabellen(self, p: Protokoll, befund: Steifigkeitsbefund) -> None:
        """Je Kombination die Werte am Kopf und die grössten über die Tiefe."""
        p.tabelle(kopf=["Kombination", Mathe(r"N_{Ed}\ [\mathrm{kN}]"),
                        Mathe(r"w_0\ [\mathrm{mm}]"), Mathe(r"N_b\ [\mathrm{kN}]")],
                  zeilen=[[v.name, Mathe(fest(v.N_Ed / 1e3, 0)), Mathe(fest(v.w[0] * 1e3, 2)),
                           Mathe(fest(v.N_b / 1e3, 0))] for v in befund.verlaeufe],
                  titel="Längs: Setzung des Kopfs und Kraft am Fuss", ausrichtung="lrrr")
        quer = [v for v in befund.verlaeufe if v.quer]
        if not quer:
            p.text("Keine Kombination belastet den Pfahl quer.")
            return
        zeilen: List[List[Zelle]] = []
        for v in quer:
            M, z_M = _extrem(v.z, v.M)
            q, _ = _extrem(v.z, v.p)
            V, _ = _extrem(v.z, v.V)
            zeilen.append([v.name, Mathe(fest(v.H_Ed / 1e3, 1)),
                           Mathe(fest(v.M_Ed / 1e3, 1)) if not befund.eingespannt else "–",
                           Mathe(fest(v.y[0] * 1e3, 2)), Mathe(fest(v.theta[0] * 1e3, 2)),
                           Mathe(fest(M / 1e3, 1)), Mathe(fest(z_M, 2)),
                           Mathe(fest(abs(V) / 1e3, 1)), Mathe(fest(abs(q) / 1e3, 0))])
        p.tabelle(kopf=["Kombination", Mathe(r"H_{Ed}\ [\mathrm{kN}]"),
                        Mathe(r"M_{Ed}\ [\mathrm{kNm}]"), Mathe(r"y_0\ [\mathrm{mm}]"),
                        Mathe(r"\theta_0\ [\mathrm{mrad}]"), Mathe(r"M_{max}\ [\mathrm{kNm}]"),
                        Mathe(r"z\ [\mathrm{m}]"), Mathe(r"|V|_{max}\ [\mathrm{kN}]"),
                        Mathe(r"|p|_{max}\ [\mathrm{kN/m^2}]")],
                  zeilen=zeilen, titel="Quer: am Kopf und die grössten Werte über die Tiefe, "
                                       "z ab Terrain", ausrichtung="lrrrrrrrr")
