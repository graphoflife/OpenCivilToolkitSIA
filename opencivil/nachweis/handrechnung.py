"""
opencivil/nachweis/handrechnung.py -- Eckpunkte der Resistenzlinie von Hand.

VERANTWORTUNG:
Rechnet die wenigen Punkte der M-N-Interaktion, die sich mit Papier und
Taschenrechner nachvollziehen lassen, und schreibt dabei jeden Schritt
mit -- Formel, eingesetzte Zahlen, Ergebnis. Aus den Punkten entsteht ein
Polygon, und gegen dieses Polygon wird nachgewiesen.

WARUM NICHT GEGEN DIE GENAUE LINIE:
Die punktweise aus Dehnungsebenen aufgebaute Linie in
:mod:`opencivil.nachweis.biegung_normalkraft` ist genauer, aber sie entsteht aus
einer Faserintegration ueber hunderte Stuetzstellen. Wer das Ergebnis prueft,
kann es nicht nachrechnen -- er kann es nur glauben. Genau das soll dieses
Werkzeug nicht verlangen. Die genaue Linie bleibt darum als Vergleich im
Diagramm stehen, das Urteil faellt aber ueber die Handrechnung.

ANSATZ:
* Druckzone als Spannungsblock der Hoehe ``0.85 x`` mit durchgehend ``f_cd``.
* **Gedrueckter Stahl wird durchgehend vernachlaessigt.** Das liegt auf der
  sicheren Seite und erspart die Frage, ob er ueberhaupt fliesst.
* Bewehrung je Richtung zu zwei Lagen zusammengefasst -- eine je Seite.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite
Bezugsachse fuer M ist die halbe Querschnittshoehe, wie bei der genauen Linie.

DIE VIER PUNKTE (je Momentenvorzeichen, ausser wo vermerkt):

    1  M_Rd bei N = 0      x aus dem Kraeftegleichgewicht, dann M aus dem Hebelarm
    2  groesste Zugkraft   alles fliesst auf Zug; nur ein Punkt fuer beide Vorzeichen
    3  groesste Druckkraft reiner Beton, ohne Stahl; M = 0
    4  Punkt mit x = h/2   Nulllinie auf halber Hoehe, Block bis 0.85*h/2

Punkt 4 liegt knapp unterhalb des Balancepunkts und gibt dem Polygon den Bauch,
den die genaue Linie unter Druck hat. Die Zugbewehrung traegt dort, was ihre
Dehnung hergibt: ``sigma_sd = min(E_s * eps_s; f_yd)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.material.basis import mit_index
from opencivil.querschnitt.platte import protokoll_statische_hoehe

#: Anteil der Druckzonenhoehe, ueber den der Spannungsblock wirkt.
BLOCKANTEIL = 0.85


@dataclass(frozen=True)
class Posten:
    """Ein einzelner Bewehrungsposten, so wie er in die Handrechnung eingeht."""

    a_s: float
    """Querschnittsflaeche in m^2, fuer die betrachtete Breite b."""

    z: float
    """Schwerpunkt in m, ab Oberkante."""

    f_yd: float
    """Bemessungswert der Fliessgrenze in Pa."""

    E_s: float
    """Elastizitaetsmodul in Pa."""

    text: str = ""
    index: str = ""
    """Index des Symbols, z.B. ``1,x,g``."""

    stahl_index: str = ""
    """Index der Stahlsorte -- leer, solange es nur eine gibt."""

    von_unten: bool = True

    @property
    def symbol_f_yd(self) -> str:
        """``f_{yd,\text{B500B}}`` -- die Posten einer Lage koennen sich
        unterscheiden, darum je Posten."""
        return mit_index("f_{yd}", self.stahl_index)


@dataclass(frozen=True)
class Lage:
    """Die zu einer Seite zusammengefasste Bewehrung."""

    a_s: float
    z: float
    f_yd: float
    E_s: float
    text: str = ""
    index: str = ""
    """Index der zusammengefassten Lage, z.B. ``1,x``."""

    stahl_index: str = ""
    """
    Index der massgebenden Stahlsorte -- die mit dem kleinsten ``f_yd``.

    Ohne ihn stuende bei zwei Sorten zweimal ``f_yd`` mit verschiedenen Zahlen
    im selben Bericht, und niemand koennte sagen, welche Sorte gemeint ist.
    """

    teile: Tuple[Posten, ...] = ()
    """Die Posten, aus denen sie entstanden ist -- fuer die Mitschrift."""

    @property
    def symbol_flaeche(self) -> str:
        """``A_{s,1,x}`` -- oder schlicht ``A_s``, wenn es keinen Index gibt.

        Eine unbewehrte Seite hat keine Lagennummer, also auch keinen Index.
        Ihn hier zu erzwingen ergaebe ``A_{s,}`` mit leerem Tiefstellen; darum
        bildet die Lage ihr Symbol selbst, statt es an sieben Stellen
        zusammenzusetzen.
        """
        return f"A_{{s,{self.index}}}" if self.index else "A_s"

    @property
    def symbol_f_yd(self) -> str:
        """``f_{yd,\text{B500B}}`` -- oder ``f_{yd}``, solange es nur eine Sorte gibt."""
        return mit_index("f_{yd}", self.stahl_index)

    @property
    def symbol_sigma_sd(self) -> str:
        """Die angesetzte Stahlspannung; sie gehoert zur selben Sorte wie f_yd."""
        return mit_index(r"\sigma_{sd}", self.stahl_index)

    @property
    def symbol_E_s(self) -> str:
        return mit_index("E_s", self.stahl_index)

    @property
    def symbol_d(self) -> str:
        """``d_{1,x}`` -- oder schlicht ``d``. Siehe :attr:`symbol_flaeche`."""
        return f"d_{{{self.index}}}" if self.index else "d"

    @property
    def symbol_z(self) -> str:
        """``z_{1,x}``, die Tiefe ab Oberkante -- oder ``z``. Siehe :attr:`symbol_flaeche`."""
        return f"z_{{{self.index}}}" if self.index else "z"


@dataclass(frozen=True)
class Eckpunkt:
    """Ein von Hand nachrechenbarer Punkt der Resistenzlinie."""

    kennung: str
    symbol: str
    """LaTeX -- so steht der Punkt in der Mitschrift."""

    name: str
    """Klartext -- fuer Kurzhinweise im Diagramm."""

    N: float
    """Normalkraft in N (Zug positiv)."""

    M: float
    """Moment in Nm (Zug unten positiv)."""


class Handrechnung:
    """
    Die Eckpunkte einer Richtung, samt Mitschrift.

    Rechnet und schreibt in einem Zug -- wie jede Berechnung in diesem Werkzeug.
    Was in der Mitschrift steht, ist genau das, was gerechnet wurde.
    """

    def __init__(
        self, *,
        h: float, b: float, f_cd: float, eps_c2d: float,
        unten: Lage, oben: Lage, richtung: str, basis: str,
        beton_index: str = "",
    ) -> None:
        self.h = h
        self.b = b
        self.f_cd = abs(f_cd)
        self.eps_c2d = abs(eps_c2d)
        self.unten = unten
        self.oben = oben
        self.richtung = richtung
        # Zwischenwerte der Mitschrift, unter der Kennung des Nachweises.
        self.werte = Zwischenwerte(f"{basis}.hand")

        # Symbole der Betonkennwerte: mit Sortenindex, sobald mehrere Betone
        # im Projekt sind. Sonst stuende f_cd zweimal mit anderen Zahlen da.
        self.s_f_cd = mit_index("f_{cd}", beton_index)
        self.s_eps_c2d = mit_index(r"\varepsilon_{c2d}", beton_index)
        # Eine Stelle wie in der Baustofftabelle: mit keiner stuende bei C25/30
        # «17» da, gerechnet wird mit 16.7 -- die Nachrechnung ginge daneben.
        self.w_f_cd = self.werte.spannung("f_cd", self.s_f_cd, self.f_cd, stellen=1)

    # -- Die Punkte ---------------------------------------------------------

    def rechnen(self, p: Protokoll) -> List[Eckpunkt]:
        """Rechnet alle Eckpunkte und schreibt die Herleitung."""
        self._ansatz(p)

        punkte: List[Eckpunkt] = []
        druck = self._groesste_druckkraft(p)
        zug = self._groesste_zugkraft(p)

        # Reihenfolge so, dass ein geschlossenes Polygon entsteht: vom reinen
        # Druck ueber die positive Seite zur Zugspitze und ueber die negative
        # Seite zurueck.
        rechts = self._seite(p, positiv=True)
        links = self._seite(p, positiv=False)

        # Innerhalb einer Seite nach der Normalkraft geordnet -- hinauf zum Zug,
        # wieder hinunter zum Druck.
        #
        # Welcher der beiden Punkte oben liegt, steht nicht von vornherein fest.
        # Der Punkt x = h/2 liegt gewoehnlich im Druck, bei einer duennen, stark
        # bewehrten Platte aber im Zug: sobald A_s*f_yd die Blockdruckkraft
        # uebersteigt, wird sein N positiv und er gehoert *hinter* M_Rd(N_Ed=0).
        # Fest verdrahtet kreuzte sich das Polygon dort selbst -- und ein sich
        # kreuzendes Polygon ist keine Resistenzlinie mehr: weder der
        # Punkt-in-Flaeche-Test noch die Schnittsuche liefern dann etwas
        # Brauchbares, und beide tragen jedes Urteil dieses Nachweises.
        #
        # Sortieren statt den Punkt zu verwerfen: er ist ein gerechneter
        # Widerstand, und wegzulassen hiesse, Tragfaehigkeit zu verschenken.
        punkte.append(druck)
        punkte.extend(sorted(rechts, key=lambda q: q.N))
        punkte.append(zug)
        punkte.extend(sorted(links, key=lambda q: q.N, reverse=True))

        self._uebersicht(p, punkte)
        return punkte

    def _ansatz(self, p: Protokoll) -> None:
        p.titel(f"Resistenzlinie aus Handrechnung – {self.richtung}")
        p.text(
            "Druckzone als Spannungsblock der Höhe 0.85·x mit durchgehend f_cd; "
            "gedrückter Stahl bleibt unberücksichtigt. Die Bewehrung ist je Seite "
            "zu einer Lage zusammengefasst, das Moment bezieht sich auf die halbe "
            "Querschnittshöhe."
        )

        # Wo eine Seite aus mehreren Posten besteht, muss dastehen, wie ihr
        # Schwerpunkt entsteht -- sonst faellt z aus dem Nichts.
        for lage in (self.unten, self.oben):
            if len(lage.teile) > 1:
                self._schwerpunkt(p, lage)

        # Die Stahlspalte nur, wenn es mehrere Sorten gibt -- dieselbe Regel
        # wie beim Sortenindex an den Symbolen. Ein Spaltenkopf kann keine zwei
        # Indizes tragen; welche Sorte in welcher Zeile gilt, muss aber
        # dastehen, sobald es mehr als eine gibt.
        seiten = (self.unten, self.oben)
        mit_stahl = any(lage.stahl_index for lage in seiten)

        p.tabelle(
            kopf=(["Seite"]
                  + (["Stahl"] if mit_stahl else [])
                  + [Mathe(r"A_s\ [\mathrm{mm}^2]"), Mathe(r"z\ [\mathrm{mm}]"),
                     Mathe(r"f_{yd}\ [\mathrm{N/mm^2}]")]),
            zeilen=[
                [lage.text]
                + ([lage.stahl_index or "–"] if mit_stahl else [])
                + [Mathe(f"{lage.a_s * 1e6:.0f}"), Mathe(f"{lage.z * 1e3:.1f}"),
                   Mathe(f"{lage.f_yd / 1e6:.0f}")]
                for lage in seiten
            ],
            titel="Zusammengefasste Bewehrung",
            ausrichtung="ll rrr".replace(" ", "") if mit_stahl else "lrrr",
        )

    def _schwerpunkt(self, p: Protokoll, lage: Lage) -> None:
        """
        Schreibt, wie Tiefe und Querschnitt einer Lage aus mehreren Posten
        entstehen.

        Nach Flaechen gewichtet, wie :func:`lagen_zusammenfassen` rechnet: die Lage
        traegt die Fliessgrenze ihrer schwaechsten Sorte, also stehen alle
        Posten unter derselben Spannung.
        """
        eingaben = {}
        for i, t in enumerate(lage.teile):
            eingaben[f"A{i}"] = self.werte.flaeche(f"A_s_{t.index}", f"A_{{s,{t.index}}}", t.a_s)
            eingaben[f"z{i}"] = self.werte.laenge(f"z_{t.index}", f"z_{{{t.index}}}", t.z)
        summe = " + ".join(f"@A{i}" for i in range(len(lage.teile)))
        momente = " + ".join(rf"@A{i} \cdot @z{i}" for i in range(len(lage.teile)))
        p.formel(
            self.werte.laenge(f"z_{lage.index}", lage.symbol_z, lage.z),
            rf"\frac{{{momente}}}{{{summe}}}",
            eingaben, titel=f"Schwerpunkt der zusammengefassten Lage – {lage.text}")
        p.formel(
            self.werte.flaeche(f"A_s_{lage.index}", lage.symbol_flaeche, lage.a_s),
            summe, eingaben,
            titel="Bewehrungsquerschnitt der zusammengefassten Lage")

    def _groesste_druckkraft(self, p: Protokoll) -> Eckpunkt:
        """Reiner Beton ohne Stahl -- die einfachste aller Grenzen."""
        N = -self.b * self.h * self.f_cd
        p.titel("Grösste Druckkraft", ebene=3)
        p.formel(
            self.werte.kraft("N_Rd_druck", "N_{Rd}^{-}", N,
                        "Grösste aufnehmbare Druckkraft"),
            r"-@b \cdot @h \cdot @f_cd",
            {
                "b": self.werte.laenge("b", "b", self.b),
                "h": self.werte.laenge("h", "h", self.h),
                "f_cd": self.w_f_cd,
            },
            titel="Gleichmässiger Druck, ohne Bewehrung",
        )
        p.wert(self.werte.moment("M_druck", r"M_{Rd}(N_{Rd}^{-})", 0.0),
               titel="Zugehöriges Moment")
        return Eckpunkt("druck", r"N_{Rd}^{-}", "grösste Druckkraft", N, 0.0)

    def _groesste_zugkraft(self, p: Protokoll) -> Eckpunkt:
        """
        Beide Lagen fliessen auf Zug.

        Es gibt hier nur *einen* Punkt, nicht je Momentenvorzeichen einen: der
        Dehnungszustand ist eindeutig, also auch das zugehoerige Moment.
        """
        u, o = self.unten, self.oben
        N = u.a_s * u.f_yd + o.a_s * o.f_yd
        # Jede Kraft mal ihrem Hebelarm um die halbe Hoehe. Beide sind Zug, also
        # positiv; die Hebelarme haben verschiedene Vorzeichen.
        M = u.a_s * u.f_yd * (u.z - self.h / 2) + o.a_s * o.f_yd * (o.z - self.h / 2)

        p.titel("Grösste Zugkraft", ebene=3)
        eingaben = {
            "A_s": self.werte.flaeche("As_u", u.symbol_flaeche, u.a_s),
            "A_s2": self.werte.flaeche("As_o", o.symbol_flaeche, o.a_s),
            "f_yd": self.werte.spannung("fyd_u", u.symbol_f_yd, u.f_yd),
            "f_yd2": self.werte.spannung("fyd_o", o.symbol_f_yd, o.f_yd),
        }
        p.formel(
            self.werte.kraft("N_Rd_zug", "N_{Rd}^{+}", N, "Grösste aufnehmbare Zugkraft"),
            r"@A_s \cdot @f_yd + @A_s2 \cdot @f_yd2",
            eingaben,
            titel="Beide Lagen fliessen auf Zug",
        )
        p.formel(
            self.werte.moment("M_Rd_zug", "M_{Rd}(N_{Rd}^{+})", M,
                         "Moment bei grösster Zugkraft"),
            r"@A_s \cdot @f_yd \cdot \left(@z - \tfrac{@h}{2}\right) "
            r"+ @A_s2 \cdot @f_yd2 \cdot \left(@z2 - \tfrac{@h}{2}\right)",
            {
                **eingaben,
                "z": self.werte.laenge("z_u", u.symbol_z, u.z),
                "z2": self.werte.laenge("z_o", o.symbol_z, o.z),
                "h": self.werte.laenge("h", "h", self.h),
            },
            titel="Kräfte mal Hebelarm um die halbe Höhe",
        )
        return Eckpunkt("zug", r"N_{Rd}^{+}", "grösste Zugkraft", N, M)

    def _seite(self, p: Protokoll, *, positiv: bool) -> List[Eckpunkt]:
        """Die beiden Punkte eines Momentenvorzeichens."""
        zug, gegen = (self.unten, self.oben) if positiv else (self.oben, self.unten)
        vz = 1.0 if positiv else -1.0
        marke = "pos" if positiv else "neg"

        p.titel(
            "Positives Moment (Zug unten)" if positiv
            else "Negatives Moment (Zug oben)", ebene=3)
        # d wird ab der gedrueckten Randfaser gemessen -- die wechselt mit dem
        # Vorzeichen des Moments die Seite.
        d = self.werte.laenge(f"d_{marke}", zug.symbol_d,
                              zug.z if positiv else self.h - zug.z)
        if zug.a_s > 0.0:
            protokoll_statische_hoehe(
                p, d, h=self.werte.laenge("h", "h", self.h),
                z=self.werte.laenge(f"z_{marke}", zug.symbol_z, zug.z), von_unten=positiv)

        punkte = [self._bei_n_null(p, zug, d, vz, marke)]
        halb = self._halbe_hoehe(p, zug, d, vz, marke)
        if halb is not None:
            punkte.append(halb)
        return punkte

    def _bei_n_null(self, p: Protokoll, zug: Lage, d: Wert,
                    vz: float, marke: str) -> Eckpunkt:
        """Reine Biegung: die Druckkraft im Beton haelt der Zugkraft die Waage."""
        x = zug.a_s * zug.f_yd / (BLOCKANTEIL * self.b * self.f_cd)
        M = zug.a_s * zug.f_yd * (d.groesse.si - BLOCKANTEIL * x / 2.0)

        hoch = "+" if vz > 0 else "-"
        # Bei negativem Moment traegt die Formel selbst das Minus. Sonst stuende
        # eine Gleichung da, deren rechte Seite nicht ihr eigenes Ergebnis ist.
        minus = "" if vz > 0 else "-"

        w_x = self.werte.laenge(f"x_{marke}", f"x^{{{hoch}}}", x, "Höhe der Druckzone")
        eingaben = {
            "A_s": self.werte.flaeche(f"As_{marke}", zug.symbol_flaeche, zug.a_s),
            "f_yd": self.werte.spannung(f"fyd_{marke}", zug.symbol_f_yd, zug.f_yd),
            "b": self.werte.laenge("b", "b", self.b),
            "f_cd": self.w_f_cd,
        }
        p.formel(
            w_x,
            rf"\frac{{@A_s \cdot @f_yd}}{{{BLOCKANTEIL} \cdot @b \cdot @f_cd}}",
            eingaben,
            titel="Druckzonenhöhe aus dem Kräftegleichgewicht",
        )
        p.formel(
            self.werte.moment(f"M_Rd_N0_{marke}", rf"M_{{Rd}}(N_{{Ed}}=0)^{{{hoch}}}",
                         vz * M, "Momentenwiderstand bei N_Ed = 0"),
            rf"{minus}@A_s \cdot @f_yd \cdot "
            rf"\left(@d - \frac{{{BLOCKANTEIL} \cdot @x}}{{2}}\right)",
            {**eingaben, "d": d, "x": w_x},
            titel="Momentenwiderstand bei reiner Biegung",
        )
        return Eckpunkt(f"n0_{marke}", rf"M_{{Rd}}(N_{{Ed}}=0)^{{{hoch}}}",
                        f"M_Rd(N_Ed=0) {hoch}", 0.0, vz * M)

    def _halbe_hoehe(self, p: Protokoll, zug: Lage, w_d: Wert,
                     vz: float, marke: str) -> Optional[Eckpunkt]:
        """
        Der Punkt mit der Nulllinie auf halber Hoehe: ``x = h/2``.

        Der Spannungsblock reicht damit bis ``0.85 * h/2``. Dieser Punkt liegt
        knapp unterhalb des Balancepunkts und gibt dem Polygon den Bauch, den
        die genaue Linie unter Druck hat.

        **Die Zugbewehrung traegt, was ihre Dehnung hergibt:**
        ``sigma_sd = min(E_s * eps_s; f_yd)``. Frueher galt der Punkt nur,
        solange sie fliesst -- also fuer ``d >= h/2 * (1 + eps_yd/eps_c2d)`` --,
        sonst fiel er weg und mit ihm der ganze Bauch. Bei tief liegender
        x-Bewehrung (dicke y-Lage aussen, x in der 2. Lage) lief das Polygon
        dann geradlinig vom reinen Druck zu M_Rd(N = 0): bei N = -2000 kN
        standen 81 kNm statt rund 250. Die Dehnungsebene ist dieselbe; der
        Stahl rechnet nur mit der Spannung, die zu ihr gehoert.

        Und er gilt nur, wenn es diese Zugbewehrung ueberhaupt gibt -- unter
        der Nulllinie. Ohne sie blieb der Betondruckblock allein stehen und
        schob dem Polygon ein Moment unter, das aus nichts stammte: eine
        Platte nur mit unterer Bewehrung wies so ein negatives Moment von
        220 kNm nach.
        """
        d = w_d.groesse.si
        x = self.h / 2.0
        if zug.a_s <= 0.0 or d <= x:
            p.hinweis("Keine Zugbewehrung unter x = h/2 → Eckpunkt x = h/2 "
                      "entfällt.")
            return None

        block = BLOCKANTEIL * x
        D = self.f_cd * self.b * block               # Betondruckkraft, Betrag
        # Die Dehnung aus der Ebene durch eps_c2d am gedrueckten Rand und null
        # in x, die Spannung daraus -- hoechstens bis zur Fliessgrenze.
        eps_s = (d - x) * self.eps_c2d / x
        sigma = min(zug.E_s * eps_s, zug.f_yd)
        N = -D + zug.a_s * sigma
        M = D * (self.h / 2 - block / 2) + zug.a_s * sigma * (d - self.h / 2)

        hoch = "+" if vz > 0 else "-"
        minus = "" if vz > 0 else "-"

        w_x = self.werte.laenge(f"xh_{marke}", f"x^{{{hoch}}}", x, "Druckzonenhöhe")
        p.formel(
            w_x,
            r"\frac{@h}{2}",
            {"h": self.werte.laenge("h", "h", self.h)},
            titel="Nulllinie auf halber Höhe: x = h/2",
        )
        w_eps = self.werte.dehnung(f"eps_s_{marke}", rf"\varepsilon_s^{{{hoch}}}",
                                   eps_s, "Dehnung der Zugbewehrung")
        p.formel(
            w_eps,
            r"\left(@d - @x\right) \cdot \frac{@eps_c2d}{@x}",
            {
                "d": w_d,
                "x": w_x,
                "eps_c2d": self.werte.dehnung("eps_c2d", self.s_eps_c2d,
                                              self.eps_c2d),
            },
            titel="Dehnung der Zugbewehrung",
        )
        w_sigma = self.werte.spannung(
            f"sigma_sd_{marke}", zug.symbol_sigma_sd, sigma, "Stahlspannung")
        p.formel(
            w_sigma,
            r"\min\left[@E_s \cdot @eps_s;\ @f_yd\right]",
            {
                "E_s": self.werte.spannung(f"E_s_{marke}", zug.symbol_E_s, zug.E_s),
                "eps_s": w_eps,
                "f_yd": self.werte.spannung(f"fyd_{marke}", zug.symbol_f_yd,
                                            zug.f_yd),
            },
            titel="Stahlspannung, höchstens die Fliessgrenze",
        )

        eingaben = {
            "f_cd": self.w_f_cd,
            "b": self.werte.laenge("b", "b", self.b),
            "x": w_x,
            "A_s": self.werte.flaeche(f"As_{marke}", zug.symbol_flaeche, zug.a_s),
            "sigma_sd": w_sigma,
        }
        p.formel(
            self.werte.kraft(f"N_halb_{marke}", rf"N_{{Rd}}^{{{hoch}}}", N,
                        "Normalkraft in diesem Punkt"),
            rf"-@f_cd \cdot @b \cdot {BLOCKANTEIL} \cdot @x + @A_s \cdot @sigma_sd",
            eingaben,
            titel="Kräftegleichgewicht",
        )
        p.formel(
            self.werte.moment(f"M_halb_{marke}", rf"M_{{Rd}}^{{{hoch}}}", vz * M,
                         "Moment in diesem Punkt"),
            rf"{minus}\left[@f_cd \cdot @b \cdot {BLOCKANTEIL} \cdot @x \cdot "
            rf"\left(\tfrac{{@h}}{{2}} - \tfrac{{{BLOCKANTEIL} \cdot @x}}{{2}}\right) "
            rf"+ @A_s \cdot @sigma_sd \cdot \left(@d - \tfrac{{@h}}{{2}}\right)\right]",
            {
                **eingaben,
                "h": self.werte.laenge("h", "h", self.h),
                "d": w_d,
            },
            titel="Momentengleichgewicht um die halbe Höhe",
        )
        return Eckpunkt(f"halb_{marke}", rf"M_{{Rd}}(x=\tfrac{{h}}{{2}})^{{{hoch}}}",
                        f"x = h/2 {hoch}", N, vz * M)

    def _uebersicht(self, p: Protokoll, punkte: List[Eckpunkt]) -> None:
        p.tabelle(
            kopf=["Eckpunkt", Mathe(r"N\ [\mathrm{kN}]"), Mathe(r"M\ [\mathrm{kNm}]")],
            zeilen=[
                [Mathe(q.symbol), Mathe(f"{q.N / 1e3:.1f}"), Mathe(f"{q.M / 1e3:.1f}")]
                for q in punkte
            ],
            titel="Eckpunkte der Resistenzlinie aus Handrechnung",
            ausrichtung="lrr",
        )



def gemeinsamer_index(teile: Sequence[Posten]) -> str:
    """
    Der Index der zusammengefassten Lage: das, was ihre Teile gemein haben.

    Grundbewehrung und Zulage einer Lage heissen ``1,x,g`` und ``1,x,z`` --
    zusammengefasst also ``1,x``. Gehen die Teile auseinander, bleibt der Index
    leer; eine erfundene Bezeichnung waere schlimmer als gar keine.
    """
    staemme = {t.index.rsplit(",", 1)[0] for t in teile if t.index}
    return staemme.pop() if len(staemme) == 1 else ""


def lagen_zusammenfassen(posten: Sequence[Posten]) -> Dict[str, Lage]:
    """
    Fasst die Bewehrungsposten einer Richtung zu zwei Lagen zusammen.

    Je Richtung liegen genau zwei Bewehrungslagen, jede davon aus Grund-
    bewehrung und Zulage. Fuer die Handrechnung zaehlt je Seite nur die Summe
    der Flaechen und ihr gemeinsamer Schwerpunkt.

    Gruppiert wird nach ``von_unten``, also nach der Zugehoerigkeit zur unteren
    oder oberen Lage -- **nicht** nach der Hoehenlage. Grundbewehrung und Zulage
    derselben Lage liegen naemlich auf leicht verschiedenen Hoehen, weil ihre
    Durchmesser verschieden sind. Wer nach z gruppiert, bekommt drei Gruppen
    statt zwei und verliert stillschweigend eine davon.

    Die entstandene Lage behaelt ihre Teile (:attr:`Lage.teile`) und ihren
    Index. Frueher kamen hier blanke Tupel an, in denen beides fehlte: die
    Mitschrift schrieb dann ``A_{s,}`` mit leerem Index, und die Herleitung des
    Schwerpunkts fiel still aus, weil sie ``len(teile) > 1`` verlangt.
    """
    if not posten:
        raise ValueError("Ohne Bewehrung lässt sich nichts von Hand rechnen.")

    gruppen: Dict[bool, List[Posten]] = {}
    for eintrag in posten:
        gruppen.setdefault(eintrag.von_unten, []).append(eintrag)

    def buendeln(gruppe: List[Posten]) -> Lage:
        flaeche = sum(t.a_s for t in gruppe)
        beteiligt = tuple(t for t in gruppe if t.a_s > 0.0)
        if flaeche <= 0.0:
            # Ohne Flaeche gibt es keinen Schwerpunkt -- die Hoehenlage genuegt.
            erster = gruppe[0]
            return Lage(0.0, erster.z, erster.f_yd, erster.E_s, erster.text,
                        index=erster.index, stahl_index=erster.stahl_index,
                        teile=(erster,))
        schwerpunkt = sum(t.a_s * t.z for t in gruppe) / flaeche
        # Bei verschiedenen Stahlsorten in einer Lage zaehlt die schwaechere --
        # sonst rechnete man mit einer Festigkeit, die ein Teil nicht hat. Der
        # Index gehoert derselben Sorte, sonst stuende ein fremder Name an der
        # Zahl.
        massgebend = min(gruppe, key=lambda t: t.f_yd)
        return Lage(
            flaeche,
            schwerpunkt,
            massgebend.f_yd,
            min(t.E_s for t in gruppe),
            " + ".join(t.text for t in beteiligt),
            index=gemeinsamer_index(beteiligt),
            stahl_index=massgebend.stahl_index,
            teile=beteiligt,
        )

    if True not in gruppen or False not in gruppen:
        # Nur eine Seite bewehrt -- die andere zaehlt mit null Flaeche, damit
        # die Formeln unveraendert gelten.
        vorhanden = buendeln(next(iter(gruppen.values())))
        leer = Lage(0.0, 0.0 if vorhanden.z > 0 else 0.0,
                    vorhanden.f_yd, vorhanden.E_s, "keine")
        return ({"unten": vorhanden, "oben": leer} if True in gruppen
                else {"unten": leer, "oben": vorhanden})

    return {"unten": buendeln(gruppen[True]), "oben": buendeln(gruppen[False])}
