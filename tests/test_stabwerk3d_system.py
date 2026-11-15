"""
Das raeumliche Stabwerk als Ganzes -- gegen Handrechnungen und gegen die Ebene.

Kragarm in alle Richtungen, Kragarm um die Ecke, Traegerrost, Dreibein aus
Gelenkstaeben, Balken mit und ohne Gabel, Bettung, feste Linienlager,
Federn, T-Stoss, Kombinationen -- und ein ebener Rahmen, der im Raum genau
das ergibt, was das 2D-Balkensystem rechnet.

Vorzeichen des Systems: x und y waagrecht, z nach oben, Drehungen im
Rechtssinn; eine Lagerkraft nach oben ist positiv.
"""

import math
import unittest

from opencivil.stabwerk import modell as m2
from opencivil.stabwerk import system as kern
from opencivil.stabwerk.art import EBENE, RAUM
from opencivil.stabwerk.modell import FEST, FREI, Kombination, Lastart, Lastfall, feder
from opencivil.stabwerk.verlauf import verlaeufe
from opencivil.stabwerk3d.modell import (
    Knoten, Knotenlast, Lager, Richtung, Stab, Stablast, System,
)

EA, EI_y, EI_z, GI_T = 5e9, 50e6, 20e6, 10e6
q, P = 10e3, 20e3


def stab(name, a, b, **felder):
    werte = dict(EA=EA, EI_y=EI_y, EI_z=EI_z, GI_T=GI_T)
    werte.update(felder)
    return Stab(name, a, b, **werte)


def eingespannt(name, knoten):
    return Lager(name, knoten, FEST, FEST, FEST, FEST, FEST, FEST)


def gelenkig(name, knoten, **drehungen):
    return Lager(name, knoten, x=FEST, y=FEST, z=FEST, **drehungen)


def linienlast(stab_, wert=q, **felder):
    return Stablast(stab_, Lastart.LINIENLAST, wert, **felder)


def system(knoten, staebe, lager, *lastfaelle, kombinationen=()):
    return System(knoten=[Knoten(*k) for k in knoten], staebe=staebe, lager=lager,
                  lastfaelle=list(lastfaelle), kombinationen=list(kombinationen))


def rechnen(s, art=RAUM):
    """Im Raum -- oder, mit :data:`~opencivil.stabwerk.art.EBENE`, ein ebenes System."""
    return kern.rechnen(s, art)


class Rechnung(unittest.TestCase):
    def gerechnet(self, s):
        e = rechnen(s)
        self.assertTrue(e.gueltig, [m.text for m in e.meldungen])
        for f in e.faelle:
            groesse = max(abs(v) for v in f.lastsumme) or 1.0
            for rest in f.gleichgewicht:
                self.assertLess(abs(rest), 1e-9 * groesse, f"Gleichgewicht in {f.name}")
        return e

    def nahe(self, a, b, relativ=1e-9):
        self.assertAlmostEqual(a, b, delta=relativ * max(abs(b), 1e-12) + 1e-12)


class TestKragarm(Rechnung):
    """Eingespannt bei K1, frei bei K2, laengs x; die Last am freien Ende."""

    L = 4.0

    def rechne(self, F=(0.0, 0.0, 0.0), M=(0.0, 0.0, 0.0), drehung=0.0):
        e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", self.L, 0, 0)], [stab("L1", "K1", "K2", drehung=drehung)],
            [eingespannt("A", "K1")], Lastfall("F", [Knotenlast("K2", F, M)])))
        f = e.faelle[0]
        return f, verlaeufe(f)["L1"]

    def test_nach_unten(self):
        """w = PL³/3EI_y, φ = PL²/2EI_y; M_y zieht oben, also negativ."""
        f, v = self.rechne(F=(0, 0, -P))
        L = self.L
        self.nahe(f.verschiebungen["K2"][2], -P * L ** 3 / (3 * EI_y))
        self.nahe(f.verschiebungen["K2"][4], P * L ** 2 / (2 * EI_y))
        self.nahe(f.lagerkraefte["K1"][2], P)
        self.nahe(f.lagerkraefte["K1"][4], -P * L)
        self.nahe(v.bei(0.0)["M_y"], -P * L)
        self.nahe(v.bei(1.0)["V_z"], P)
        self.nahe(v.bei(L)["uz"], -P * L ** 3 / (3 * EI_y))

    def test_seitlich(self):
        """In +y des Systems -- -y des Stabs: M_z zieht an +y des Stabs."""
        f, v = self.rechne(F=(0, P, 0))
        L = self.L
        self.nahe(f.verschiebungen["K2"][1], P * L ** 3 / (3 * EI_z))
        self.nahe(f.lagerkraefte["K1"][5], -P * L)
        self.nahe(v.bei(0.0)["M_z"], P * L)
        self.nahe(v.bei(1.0)["V_y"], -P)

    def test_torsion(self):
        T = 5e3
        f, v = self.rechne(M=(T, 0, 0))
        self.nahe(f.verschiebungen["K2"][3], T * self.L / GI_T)
        self.nahe(f.lagerkraefte["K1"][3], -T)
        self.nahe(v.bei(1.0)["T"], T)
        self.nahe(v.bei(self.L)["theta_x"], T * self.L / GI_T)

    def test_laengs(self):
        f, v = self.rechne(F=(P, 0, 0))
        self.nahe(f.verschiebungen["K2"][0], P * self.L / EA)
        self.nahe(v.bei(2.0)["N"], P)

    def test_gedreht(self):
        """β = 90°: der Steg liegt waagrecht, die Last biegt um z."""
        f, v = self.rechne(F=(0, 0, -P), drehung=math.pi / 2)
        self.nahe(f.verschiebungen["K2"][2], -P * self.L ** 3 / (3 * EI_z))
        self.nahe(v.bei(0.0)["M_z"], -P * self.L)
        self.assertAlmostEqual(v.bei(0.0)["M_y"], 0.0, places=6)


class TestUmDieEcke(Rechnung):
    """Ein Kragarm um die Ecke: L1 laengs x, L2 laengs y, die Last am Ende."""

    a, b = 3.0, 2.0

    def setUp(self):
        self.e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", self.a, 0, 0), ("K3", self.a, self.b, 0)],
            [stab("L1", "K1", "K2"), stab("L2", "K2", "K3")], [eingespannt("A", "K1")],
            Lastfall("P", [Knotenlast("K3", F=(0, 0, -P))])))
        self.f = self.e.faelle[0]

    def test_durchbiegung(self):
        """Biegung beider Arme und die Verdrillung von L1 mit dem Moment P·b."""
        a, b = self.a, self.b
        erwartet = P * a ** 3 / (3 * EI_y) + P * b * b * a / GI_T + P * b ** 3 / (3 * EI_y)
        self.nahe(self.f.verschiebungen["K3"][2], -erwartet)

    def test_torsion_und_einspannung(self):
        v = verlaeufe(self.f)["L1"]
        self.nahe(v.bei(1.0)["T"], -P * self.b)
        self.nahe(self.f.lagerkraefte["K1"][3], P * self.b)
        self.nahe(self.f.lagerkraefte["K1"][4], -P * self.a)


class TestTraegerrost(Rechnung):
    """Zwei gleiche Traeger kreuzen sich in der Mitte, starr verbunden; P dort."""

    L = 6.0

    def test_jeder_traegt_die_haelfte(self):
        h = self.L / 2
        e = self.gerechnet(system(
            [("K0", 0, 0, 0), ("K1", -h, 0, 0), ("K2", h, 0, 0), ("K3", 0, -h, 0), ("K4", 0, h, 0)],
            [stab("L1", "K1", "K0"), stab("L2", "K0", "K2"),
             stab("L3", "K3", "K0"), stab("L4", "K0", "K4")],
            [Lager("A1", "K1", x=FEST, y=FEST, z=FEST), Lager("A2", "K2", y=FEST, z=FEST),
             Lager("A3", "K3", z=FEST), Lager("A4", "K4", z=FEST)],
            Lastfall("P", [Knotenlast("K0", F=(0, 0, -P))])))
        f = e.faelle[0]
        for k in ("K1", "K2", "K3", "K4"):
            self.nahe(f.lagerkraefte[k][2], P / 4)
        self.nahe(f.verschiebungen["K0"][2], -(P / 2) * self.L ** 3 / (48 * EI_y))
        self.assertAlmostEqual(verlaeufe(f)["L1"].bei(1.0)["T"], 0.0, places=6)


class TestEbenerRahmen(Rechnung):
    """
    Ein Rahmen in der x-z-Ebene, im Raum gerechnet: dieselben Zahlen wie das
    2D-Balkensystem. Der Riegel L2 laeuft nach links -- dort haben V_z und
    M_y das andere Vorzeichen als V und M der Ebene.
    """

    knoten = [("K1", 0, 0), ("K2", 0, 4), ("K3", 6, 4), ("K4", 6, 0), ("K5", 8, 5)]
    staebe = [("L1", "K1", "K2", {}), ("L2", "K3", "K2", {"gelenk_b": True}),
              ("L3", "K4", "K3", {}), ("L4", "K3", "K5", {})]
    nach_links = {"L2"}
    lager = [("A1", "K1", (FEST, FEST, FEST)), ("A2", "K4", (FEST, FEST, FREI))]

    def setUp(self):
        lasten = [
            m2.Stablast("L2", Lastart.LINIENLAST, 10e3, 14e3, m2.Lastrichtung.SENKRECHT, 1.0, 5.0),
            m2.Stablast("L1", Lastart.EINZELLAST, 5e3, None, m2.Lastrichtung.WAAGRECHT, 2.0),
            m2.Stablast("L4", Lastart.LINIENLAST, 3e3, None, m2.Lastrichtung.QUER),
            m2.Stablast("L4", Lastart.LINIENLAST, 2e3, None, m2.Lastrichtung.SENKRECHT,
                        projiziert=True),
            m2.Stablast("L3", Lastart.MOMENT, 7e3, None, von=1.5),
            m2.Stablast("L2", Lastart.LINIENMOMENT, 1e3, None),
            m2.Knotenlast("K5", Fx=2e3, Fz=-1e3, M=3e3),
        ]
        eben = m2.System([m2.Knoten(n, x, z) for n, x, z in self.knoten],
                         [m2.Stab(n, a, b, EA=EA, EI=EI_y, **f) for n, a, b, f in self.staebe],
                         [m2.Lager(n, k, *h) for n, k, h in self.lager], [Lastfall("F", lasten)])
        self.e2 = rechnen(eben, EBENE)
        self.assertTrue(self.e2.gueltig)
        # Aus der Ebene heraus gehalten: in y und um x und z.
        raeumlich = System(
            [Knoten(n, x, 0.0, z) for n, x, z in self.knoten],
            [stab(n, a, b, **f) for n, a, b, f in self.staebe],
            [Lager(n, k, x=h[0], y=FEST, z=h[1], phi_x=FEST, phi_y=h[2], phi_z=FEST)
             for n, k, h in self.lager],
            [Lastfall("F", [self.raeumlich(l) for l in lasten])])
        self.e3 = self.gerechnet(raeumlich)
        self.f2, self.f3 = self.e2.faelle[0], self.e3.faelle[0]

    def raeumlich(self, last):
        """Die Last der Ebene im Raum -- ein Moment im Gegenuhrzeigersinn dreht um -y."""
        if isinstance(last, m2.Knotenlast):
            return Knotenlast(last.knoten, F=(last.Fx, 0.0, last.Fz), M=(0.0, -last.M, 0.0))
        richtung = {m2.Lastrichtung.SENKRECHT: Richtung.SENKRECHT,
                    m2.Lastrichtung.WAAGRECHT: Richtung.X,
                    m2.Lastrichtung.QUER: Richtung.QUER_Z,
                    m2.Lastrichtung.LAENGS: Richtung.LAENGS}[last.richtung]
        faktor = 1.0
        if not last.art.kraft:
            richtung, faktor = Richtung.Y, -1.0
        elif last.richtung is m2.Lastrichtung.QUER and last.stab in self.nach_links:
            faktor = -1.0
        return Stablast(last.stab, last.art, faktor * last.wert_a,
                        None if last.wert_b is None else faktor * last.wert_b,
                        richtung, last.von, last.bis, last.projiziert)

    def test_verschiebungen(self):
        for k, (ux, uz, phi) in self.f2.verschiebungen.items():
            if k not in self.f3.verschiebungen:
                continue
            w = self.f3.verschiebungen[k]
            self.nahe(w[0], ux, 1e-8)
            self.nahe(w[2], uz, 1e-8)
            self.nahe(-w[4], phi, 1e-8)
            for i in (1, 3, 5):
                self.assertAlmostEqual(w[i], 0.0, places=12)

    def test_lagerkraefte(self):
        for k, (rx, rz, rm) in self.f2.lagerkraefte.items():
            r = self.f3.lagerkraefte[k]
            self.nahe(r[0], rx, 1e-8)
            self.nahe(r[2], rz, 1e-8)
            self.assertAlmostEqual(-r[4], rm, delta=1e-8 * P)

    def test_verlaeufe(self):
        eben, raeumlich = verlaeufe(self.f2), verlaeufe(self.f3)
        for name, verlauf in eben.items():
            vz = -1.0 if name in self.nach_links else 1.0
            for x in (0.0, 0.3, 1.0, 1.5, 2.0, 2.9, verlauf.L):
                a, b = verlauf.bei(x), raeumlich[name].bei(x)
                for g, s in (("N", 1), ("V_z", vz), ("M_y", vz), ("ux", 1), ("uz", 1)):
                    self.assertAlmostEqual(a[g], s * b[g], delta=1e-6 * (1 + abs(a[g])),
                                           msg=(name, x, g))
                for g3 in ("V_y", "M_z", "T", "uy"):
                    self.assertAlmostEqual(b[g3], 0.0, places=6, msg=(name, x, g3))


class TestRaeumlicherRahmen(Rechnung):
    """
    Schief im Raum, mit Drehwinkeln, Gelenk, Federn, Bettung und Lasten in
    allen Richtungen. Die Verlaeufe, vom Anfang jedes Stuecks aus gerechnet,
    muessen an seinem Ende treffen, was die Loesung dort hat -- je Teil mit
    seinen Vorzeichen.
    """

    def setUp(self):
        self.e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", 0, 0, 3), ("K3", 4, 1, 3.5), ("K4", 4, 1, 0),
             ("K5", 6, 3, 3.5), ("K6", 4, 6, 0)],
            [stab("S1", "K1", "K2", drehung=0.3), stab("R", "K2", "K3", gelenk_b=True),
             stab("S2", "K4", "K3"), stab("K", "K3", "K5", drehung=0.5),
             stab("G", "K4", "K6", quer_z=feder(5e6), quer_y=feder(1e6), laengs=feder(2e5))],
            [eingespannt("A1", "K1"),
             Lager("A4", "K4", x=FEST, y=FEST, z=FEST, phi_x=feder(1e7), phi_y=FEST)],
            Lastfall("F", [
                linienlast("R", 8e3, wert_b=3e3, von=0.5, bis=3.0),
                Stablast("K", Lastart.EINZELLAST, 4e3, richtung=Richtung.QUER_Y, von=1.0),
                Stablast("S1", Lastart.LINIENMOMENT, 2e3, richtung=Richtung.LAENGS),
                Stablast("S2", Lastart.MOMENT, 6e3, richtung=Richtung.Z, von=2.0),
                Stablast("G", Lastart.LINIENLAST, 3e3, richtung=Richtung.Y),
                Knotenlast("K5", F=(1e3, -2e3, -5e3), M=(1e3, 2e3, -3e3)),
            ])))
        self.f = self.e.faelle[0]
        self.verlaeufe = verlaeufe(self.f)

    def test_biegelinie_trifft_das_ende(self):
        namen = ("u", "v", "w", "theta_x", "theta_y", "theta_z")
        for teil in self.f.teile:
            t = teil.teil
            werte = self.verlaeufe[t.stab.name].bei(t.x1, links=True)
            for i, name in enumerate(namen):
                self.assertAlmostEqual(werte[name], teil.d[6 + i],
                                       delta=1e-7 * (1e-3 + abs(teil.d[6 + i])),
                                       msg=(t.stab.name, t.nummer, name))

    def test_schnittgroessen_am_ende(self):
        for teil in self.f.teile:
            t, s = teil.teil, teil.s
            werte = self.verlaeufe[t.stab.name].bei(t.x1, links=True)
            for name, wert in (("N", s[6]), ("V_y", s[7]), ("V_z", s[8]), ("T", s[9]),
                               ("M_y", s[10]), ("M_z", -s[11])):
                self.assertAlmostEqual(werte[name], wert, delta=1e-6 * (1 + abs(wert)),
                                       msg=(t.stab.name, t.nummer, name))

    def test_gebettet_geteilt(self):
        self.assertGreater(len([t for t in self.e.teilstaebe if t.stab.name == "G"]), 1)


class TestGelenke(Rechnung):
    """Ein Gelenk loest alle drei Momente; mit zweien traegt der Stab keine Torsion."""

    def dreibein(self, *lasten):
        h, r = 4.0, 2.0
        fuesse = [(f"K{i + 1}", r * math.cos(2 * math.pi * i / 3), r * math.sin(2 * math.pi * i / 3), 0.0)
                  for i in range(3)]
        return rechnen(system(
            [("K0", 0.0, 0.0, h), *fuesse],
            [stab(f"L{i + 1}", "K0", k[0], gelenk_a=True, gelenk_b=True) for i, k in enumerate(fuesse)],
            [gelenkig(f"A{i + 1}", k[0]) for i, k in enumerate(fuesse)],
            Lastfall("F", list(lasten))))

    def test_dreibein(self):
        """Drei Gelenkstaebe tragen wie ein Fachwerk: nur Normalkraft."""
        e = self.dreibein(Knotenlast("K0", F=(0, 0, -P)))
        self.assertTrue(e.gueltig, [m.text for m in e.meldungen])
        laenge = math.hypot(2.0, 4.0)
        verlauf = verlaeufe(e.faelle[0])
        for name in ("L1", "L2", "L3"):
            werte = verlauf[name].bei(1.0)
            self.nahe(werte["N"], -P * laenge / (3 * 4.0))
            for g in ("M_y", "M_z", "V_y", "V_z", "T"):
                self.assertAlmostEqual(werte[g], 0.0, places=6, msg=(name, g))
        self.assertEqual(sorted(e.unbestimmt()), ["K0", "K1", "K2", "K3"])
        self.assertIn("θ_y(L1, Anfang)", e.unbekannte)
        self.assertNotIn("θ_x(L1, Anfang)", e.unbekannte)

    def test_moment_ohne_halt(self):
        e = self.dreibein(Knotenlast("K0", M=(0, 1e3, 0)))
        self.assertFalse(e.gueltig)
        self.assertIn("gelenkig angeschlossen", e.meldungen[0].text)

    def test_torsion_ohne_halt(self):
        e = self.dreibein(Stablast("L1", Lastart.LINIENMOMENT, 1e3, richtung=Richtung.LAENGS))
        self.assertFalse(e.gueltig)
        self.assertIn("trägt der Stab keine Torsion", e.meldungen[0].text)

    def test_gelenkig_zwischen_stuetzen(self):
        """Ein Riegel mit Gelenken zwischen zwei eingespannten Stuetzen: wie ein Einfeldtraeger."""
        L = 5.0
        e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", 0, 0, 3), ("K3", L, 0, 3), ("K4", L, 0, 0)],
            [stab("S1", "K1", "K2"), stab("R", "K2", "K3", gelenk_a=True, gelenk_b=True),
             stab("S2", "K4", "K3")],
            [eingespannt("A1", "K1"), eingespannt("A2", "K4")],
            Lastfall("q", [linienlast("R"), linienlast("R", 2e3, richtung=Richtung.Y)])))
        v = verlaeufe(e.faelle[0])["R"]
        for x in (0.0, L):
            for g in ("M_y", "M_z", "T"):
                self.assertAlmostEqual(v.bei(x)[g], 0.0, places=6, msg=(x, g))
        self.nahe(v.extrem("M_y").groesst[1], q * L * L / 8, 1e-8)
        # In +y des Systems ist -y des Stabs: Zug auf der Seite -y, M_z negativ.
        self.nahe(v.extrem("M_z").kleinst[1], -2e3 * L * L / 8, 1e-8)

    def test_ein_gelenk_traegt_torsion(self):
        """Mit einem Gelenk traegt der Stab Torsion zum anderen Ende -- wie ein Kragarm."""
        L, m = 4.0, 1e3
        e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", L, 0, 0)], [stab("L1", "K1", "K2", gelenk_b=True)],
            [eingespannt("A1", "K1"), gelenkig("A2", "K2")],
            Lastfall("m", [Stablast("L1", Lastart.LINIENMOMENT, m, richtung=Richtung.LAENGS)])))
        f = e.faelle[0]
        self.nahe(f.lagerkraefte["K1"][3], -m * L)
        self.nahe(verlaeufe(f)["L1"].bei(0.0)["T"], m * L)
        self.assertIn("θ_x(L1, Ende)", e.unbekannte)


class TestGabel(Rechnung):
    """Ein Einfeldtraeger auf zwei gelenkigen Lagern dreht sich ohne Gabel um seine Achse."""

    L = 6.0

    def rechne(self, lager_a, **gelenke):
        return rechnen(system(
            [("K1", 0, 0, 0), ("K2", self.L, 0, 0)], [stab("L1", "K1", "K2", **gelenke)],
            [lager_a, Lager("A2", "K2", y=FEST, z=FEST)], Lastfall("q", [linienlast("L1")])))

    def test_ohne_gabel_beweglich(self):
        e = self.rechne(gelenkig("A1", "K1"))
        self.assertFalse(e.gueltig)
        self.assertIn("beweglich", e.meldungen[0].text)
        self.assertIn("Dabei verschiebt sich nichts", e.meldungen[0].text)

    def pruefe_einfeldtraeger(self, e):
        self.assertTrue(e.gueltig, [m.text for m in e.meldungen])
        f = e.faelle[0]
        v = verlaeufe(f)["L1"]
        L = self.L
        self.nahe(f.lagerkraefte["K1"][2], q * L / 2)
        self.nahe(v.extrem("M_y").groesst[1], q * L * L / 8, 1e-8)
        self.nahe(v.extrem("M_y").groesst[0], L / 2, 1e-6)
        self.nahe(v.extrem("f_z").groesst[1], 5 * q * L ** 4 / (384 * EI_y), 1e-8)
        self.nahe(v.bei(0.0)["V_z"], q * L / 2)

    def test_mit_gabel(self):
        self.pruefe_einfeldtraeger(self.rechne(gelenkig("A1", "K1", phi_x=FEST)))

    def test_mit_gelenken(self):
        e = self.rechne(gelenkig("A1", "K1"), gelenk_a=True, gelenk_b=True)
        self.pruefe_einfeldtraeger(e)
        self.assertEqual(sorted(e.unbestimmt()), ["K1", "K2"])


class TestBeweglich(unittest.TestCase):
    def test_ein_lager_zu_wenig(self):
        e = rechnen(system(
            [("K1", 0, 0, 0), ("K2", 4, 0, 0)], [stab("L1", "K1", "K2")],
            [gelenkig("A1", "K1", phi_x=FEST)], Lastfall("q", [linienlast("L1")])))
        self.assertFalse(e.gueltig)
        self.assertIn("Es fehlt ein Lager", e.meldungen[0].text)
        self.assertIn("K2", e.beweglich)


class TestBettung(Rechnung):
    """Ein gebetteter Balken im Raum wie in der Ebene -- quer in z und laengs."""

    def test_wie_in_der_ebene(self):
        L, k, k_x = 8.0, 2e6, 5e5
        lasten2 = [m2.Stablast("L1", Lastart.LINIENLAST, q),
                   m2.Stablast("L1", Lastart.EINZELLAST, P, von=3.0),
                   m2.Stablast("L1", Lastart.EINZELLAST, P, richtung=m2.Lastrichtung.LAENGS,
                               von=L)]
        eben = rechnen(m2.System(
            [m2.Knoten("K1", 0, 0), m2.Knoten("K2", L, 0)],
            [m2.Stab("L1", "K1", "K2", EA=EA, EI=EI_y, quer=feder(k), laengs=feder(k_x))],
            [], [Lastfall("F", lasten2)]), EBENE)
        self.assertTrue(eben.gueltig, [m.text for m in eben.meldungen])
        lasten3 = [linienlast("L1"), Stablast("L1", Lastart.EINZELLAST, P, von=3.0),
                   Stablast("L1", Lastart.EINZELLAST, P, richtung=Richtung.LAENGS, von=L)]
        raeumlich = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", L, 0, 0)],
            [stab("L1", "K1", "K2", quer_z=feder(k), laengs=feder(k_x))],
            [Lager("A1", "K1", y=FEST, phi_x=FEST), Lager("A2", "K2", y=FEST)],
            Lastfall("F", lasten3)))
        a = verlaeufe(eben.faelle[0])["L1"]
        b = verlaeufe(raeumlich.faelle[0])["L1"]
        for x in (0.0, 1.0, 3.0, 5.5, L):
            for g in ("uz", "ux", "M_y", "N"):
                self.assertAlmostEqual(a.bei(x)[g], b.bei(x)[g],
                                       delta=1e-6 * (1 + abs(a.bei(x)[g])), msg=(x, g))
        bettung = raeumlich.faelle[0].bettung["L1"]
        self.nahe(bettung[2], q * L + P, 1e-8)
        self.nahe(bettung[0], -P, 1e-8)


class TestLinienlager(Rechnung):
    def test_auf_der_mauer(self):
        """Quer in z fest aufgelegt: die senkrechte Last geht geradewegs ins Lager."""
        L = 5.0
        e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", L, 0, 0)], [stab("L1", "K1", "K2", quer_z=FEST)],
            [Lager("A1", "K1", x=FEST, y=FEST, phi_x=FEST), Lager("A2", "K2", y=FEST)],
            Lastfall("q", [linienlast("L1")])))
        f = e.faelle[0]
        self.nahe(f.linienlast["L1"][2], q * L)
        v = verlaeufe(f)["L1"]
        for g in ("M_y", "V_z", "uz"):
            self.assertAlmostEqual(v.bei(2.0)[g], 0.0, places=9)


class TestFedern(Rechnung):
    def test_drehfeder(self):
        """Kragarm auf einer Drehfeder: PL³/3EI und dazu L·PL/k."""
        L, k = 3.0, 4e7
        e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", L, 0, 0)], [stab("L1", "K1", "K2")],
            [Lager("A", "K1", FEST, FEST, FEST, FEST, feder(k), FEST)],
            Lastfall("P", [Knotenlast("K2", F=(0, 0, -P))])))
        f = e.faelle[0]
        self.nahe(f.verschiebungen["K2"][2], -(P * L ** 3 / (3 * EI_y) + L * P * L / k))
        self.nahe(f.lagerkraefte["K1"][4], -P * L)


class TestTStoss(Rechnung):
    def test_knoten_im_stab(self):
        """K3 liegt auf L1: dort ist L1 geteilt, und die Stuetze L2 haengt daran."""
        e = self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", 6, 0, 0), ("K3", 2, 0, 0), ("K4", 2, 0, -3)],
            [stab("L1", "K1", "K2"), stab("L2", "K4", "K3")],
            [eingespannt("A1", "K1"), eingespannt("A4", "K4")],
            Lastfall("q", [linienlast("L1")])))
        self.assertEqual(len([t for t in e.teilstaebe if t.stab.name == "L1"]), 2)
        v = verlaeufe(e.faelle[0])["L1"]
        self.assertAlmostEqual(v.bei(2.0, links=True)["uz"], v.bei(2.0)["uz"], places=12)
        self.assertAlmostEqual(v.bei(2.0)["uz"], e.faelle[0].verschiebungen["K3"][2], places=12)

    def test_kreuzen_ohne_knoten(self):
        e = rechnen(system(
            [("K1", 0, 0, 0), ("K2", 4, 0, 0), ("K3", 2, -2, 0), ("K4", 2, 2, 0)],
            [stab("L1", "K1", "K2"), stab("L2", "K3", "K4")],
            [eingespannt(f"A{i}", f"K{i}") for i in range(1, 5)], Lastfall("leer")))
        self.assertTrue(e.gueltig)
        self.assertIn("kreuzen sich ohne Knoten", e.meldungen[0].text)


class TestLasten(Rechnung):
    def kragarm(self, *faelle, kombinationen=()):
        return self.gerechnet(system(
            [("K1", 0, 0, 0), ("K2", 4, 0, 3)], [stab("L1", "K1", "K2")],
            [eingespannt("A", "K1")], *faelle, kombinationen=kombinationen))

    def test_projiziert(self):
        e = self.kragarm(Lastfall("je Stab", [linienlast("L1")]),
                         Lastfall("je Grundriss", [linienlast("L1", projiziert=True)]))
        self.nahe(e.fall("je Stab").lastsumme[2], -q * 5.0)
        self.nahe(e.fall("je Grundriss").lastsumme[2], -q * 4.0)

    def test_kombination(self):
        e = self.kragarm(Lastfall("G", [linienlast("L1")]),
                         Lastfall("Q", [Knotenlast("K2", F=(P, 0, 0))]),
                         kombinationen=[Kombination("ULS", {"G": 1.35, "Q": 1.5})])
        g, q_, uls = e.fall("G"), e.fall("Q"), e.fall("ULS")
        self.assertTrue(uls.kombination)
        for i in range(6):
            self.nahe(uls.verschiebungen["K2"][i],
                      1.35 * g.verschiebungen["K2"][i] + 1.5 * q_.verschiebungen["K2"][i], 1e-8)

    def test_ausserhalb(self):
        e = rechnen(system(
            [("K1", 0, 0, 0), ("K2", 4, 0, 0)], [stab("L1", "K1", "K2")],
            [eingespannt("A", "K1")],
            Lastfall("F", [Stablast("L1", Lastart.EINZELLAST, P, von=5.0)])))
        self.assertFalse(e.gueltig)
        self.assertIn("der Stab ist aber 4.000 m lang", e.meldungen[0].text)


class TestPruefen(unittest.TestCase):
    def test_ohne_torsionssteifigkeit(self):
        e = rechnen(system([("K1", 0, 0, 0), ("K2", 4, 0, 0)],
                           [stab("L1", "K1", "K2", GI_T=0.0)], [eingespannt("A", "K1")]))
        self.assertFalse(e.gueltig)
        self.assertIn("Torsionssteifigkeit", e.meldungen[0].text)

    def test_lager_ohne_stab(self):
        e = rechnen(system([("K1", 0, 0, 0), ("K2", 4, 0, 0), ("K3", 9, 9, 9)],
                           [stab("L1", "K1", "K2")],
                           [eingespannt("A", "K1"), eingespannt("B", "K3")]))
        self.assertTrue(e.gueltig)
        self.assertIn("das Lager hält nichts", e.meldungen[0].text)


if __name__ == "__main__":
    unittest.main()
