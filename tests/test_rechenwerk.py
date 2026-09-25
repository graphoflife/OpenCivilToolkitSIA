"""
Tests fuer Werte, Berechnungen und den Loeser.

Gerechnet wird hier mit einem kleinen erfundenen Beispiel, damit die Tests die
Mechanik pruefen und nicht die Norminhalte -- die haben eigene Tests.
"""

import unittest
from typing import Mapping

from opencivil.core.berechnung import (
    Berechnung, BerechnungsFehler, Eingabebezug, Eingaben, Formel, Nachweis,
    NachweisUrteil, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, M, MM, MM2, MPA, N_PRO_MM2, DimensionsFehler, Groesse,
)
from opencivil.core.latex import (
    Formelzeile, LatexFehler, einsetzen_numerisch, einsetzen_symbolisch,
    sichtbare_breite,
)
from opencivil.core.protokoll import GleichungBlock, Protokoll, StillesProtokoll, TabellenBlock
from opencivil.core.rechenwerk import Rechenwerk, RechenwerkFehler, ZyklusFehler
from opencivil.core.wert import Quelle, Wert, WertDef

# ---------------------------------------------------------------------------
# Gemeinsame Definitionen
# ---------------------------------------------------------------------------

D_F_CK = WertDef("beton.f_ck", "f_{ck}", MPA, "Charakteristische Zylinderdruckfestigkeit", "SIA 262:2025, 3.1.2.2.7")
D_GAMMA_C = WertDef("beton.gamma_c", r"\gamma_c", EINHEITSLOS, "Teilsicherheitsbeiwert Beton", "SIA 262:2025, 2.4.2.6")
D_ETA_FC = WertDef("beton.eta_fc", r"\eta_{fc}", EINHEITSLOS, "Beiwert Festigkeitsminderung", stellen=3)
D_F_CD = WertDef("beton.f_cd", "f_{cd}", MPA, "Bemessungswert der Betondruckfestigkeit", "SIA 262:2025, 2.4.2.3", stellen=1)
D_B = WertDef("qs.b", "b", MM, "Querschnittsbreite", stellen=0)
D_H = WertDef("qs.h", "h", MM, "Querschnittshoehe", stellen=0)
D_A = WertDef("qs.A", "A", MM2, "Querschnittsflaeche", stellen=0)
D_N_RD = WertDef("qs.N_Rd", "N_{Rd}", KN, "Normalkraftwiderstand", stellen=1)


def formel_eta_fc() -> Formel:
    return Formel(
        id="b.eta_fc",
        ausgabe=D_ETA_FC,
        eingaben={"f_ck": D_F_CK.id},
        vorlage=r"\min\left[\left(\frac{40\,\mathrm{N/mm^2}}{@f_ck}\right)^{1/3};\ 1.0\right]",
        funktion=lambda f_ck: Groesse(
            min((40.0 / f_ck.in_einheit(N_PRO_MM2)) ** (1 / 3), 1.0), EINHEITSLOS
        ),
    )


def formel_f_cd() -> Formel:
    return Formel(
        id="b.f_cd",
        ausgabe=D_F_CD,
        eingaben={"eta_fc": D_ETA_FC.id, "f_ck": D_F_CK.id, "gamma_c": D_GAMMA_C.id},
        vorlage=r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}",
        funktion=lambda eta_fc, f_ck, gamma_c: eta_fc * f_ck / gamma_c,
    )


def formel_flaeche() -> Formel:
    return Formel(
        id="b.A",
        ausgabe=D_A,
        eingaben={"b": D_B.id, "h": D_H.id},
        vorlage=r"@b \cdot @h",
        funktion=lambda b, h: b * h,
    )


def formel_n_rd() -> Formel:
    return Formel(
        id="b.N_Rd",
        ausgabe=D_N_RD,
        eingaben={"A": D_A.id, "f_cd": D_F_CD.id},
        vorlage=r"@A \cdot @f_cd",
        funktion=lambda A, f_cd: A * f_cd,
    )


def standardwerk() -> Rechenwerk:
    werk = Rechenwerk()
    werk.definiere(D_F_CK, D_GAMMA_C, D_B, D_H)
    werk.registriere(formel_eta_fc(), formel_f_cd(), formel_flaeche(), formel_n_rd())
    return werk


# ---------------------------------------------------------------------------


class TestWert(unittest.TestCase):
    def test_namensraum(self):
        self.assertEqual(D_F_CD.kurzname, "f_cd")
        self.assertEqual(D_F_CD.namensraum, "beton")

    def test_praefix(self):
        mit = D_F_CK.mit_praefix("projekt1")
        self.assertEqual(mit.id, "projekt1.beton.f_ck")
        self.assertEqual(mit.symbol, D_F_CK.symbol)
        # Das Original bleibt unangetastet.
        self.assertEqual(D_F_CK.id, "beton.f_ck")

    def test_dimension_wird_geprueft(self):
        with self.assertRaises(DimensionsFehler):
            D_F_CK.belegen(Groesse(300, MM))

    def test_dimensionslose_null_erlaubt(self):
        wert = D_F_CK.belegen(Groesse(0, EINHEITSLOS))
        self.assertAlmostEqual(wert.groesse.si, 0.0)

    def test_formatierung(self):
        wert = D_F_CD.belegen(Groesse(16.6667, MPA))
        self.assertEqual(wert.formatiert(), "16.7")
        self.assertEqual(wert.zahl_latex(), r"16.7\,\mathrm{MPa}")


class TestLatexEinsetzen(unittest.TestCase):
    def setUp(self):
        self.eingaben = {
            "f_ck": D_F_CK.belegen(Groesse(30, MPA)),
            "gamma_c": D_GAMMA_C.belegen(Groesse(1.5, EINHEITSLOS)),
        }

    def test_symbolisch(self):
        ergebnis = einsetzen_symbolisch(r"\frac{@f_ck}{@gamma_c}", self.eingaben)
        self.assertEqual(ergebnis, r"\frac{f_{ck}}{\gamma_c}")

    def test_numerisch(self):
        ergebnis = einsetzen_numerisch(r"\frac{@f_ck}{@gamma_c}", self.eingaben)
        self.assertEqual(ergebnis, r"\frac{30\,\mathrm{MPa}}{1.5}")

    def test_geklammerter_platzhalter(self):
        ergebnis = einsetzen_symbolisch(r"@{f_ck}2", self.eingaben)
        self.assertEqual(ergebnis, "f_{ck}2")

    def test_unbekannter_platzhalter_wirft(self):
        with self.assertRaises(LatexFehler) as ctx:
            einsetzen_symbolisch(r"@f_yk", self.eingaben)
        self.assertIn("f_yk", str(ctx.exception))

    def test_negative_werte_werden_geklammert(self):
        eingaben = {"M": WertDef("m", "M", KNM).belegen(Groesse(-120, KNM))}
        self.assertIn(r"\left(", einsetzen_numerisch(r"@M \cdot 2", eingaben))
        # Steht der Platzhalter allein, waere die Klammer nur Unruhe.
        self.assertNotIn(r"\left(", einsetzen_numerisch(r"@M", eingaben))


class TestFormelzeile(unittest.TestCase):
    def test_vier_teile(self):
        eingaben = {
            "eta_fc": D_ETA_FC.belegen(Groesse(0.933, EINHEITSLOS)),
            "f_ck": D_F_CK.belegen(Groesse(30, MPA)),
            "gamma_c": D_GAMMA_C.belegen(Groesse(1.5, EINHEITSLOS)),
        }
        ergebnis = D_F_CD.belegen(Groesse(18.66, MPA))
        zeile = Formelzeile.bauen(ergebnis, r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}", eingaben)
        text = zeile.einzeilig()
        self.assertEqual(
            text,
            r"f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}"
            r" = \frac{0.933 \cdot 30\,\mathrm{MPa}}{1.5} = 18.7\,\mathrm{MPa}",
        )

    def test_ohne_vorlage_nur_wert(self):
        zeile = Formelzeile.bauen(D_F_CK.belegen(Groesse(30, MPA)))
        self.assertEqual(zeile.einzeilig(), r"f_{ck} = 30\,\mathrm{MPa}")

    def test_mehrzeilig(self):
        eingaben = {"b": D_B.belegen(Groesse(1000, MM)), "h": D_H.belegen(Groesse(300, MM))}
        zeile = Formelzeile.bauen(D_A.belegen(Groesse(300000, MM2)), r"@b \cdot @h", eingaben)
        mehr = zeile.mehrzeilig()
        self.assertIn(r"\begin{aligned}", mehr)
        self.assertEqual(mehr.count(r"&="), 3)

    def test_gleichheitszeichen_in_formel_bricht_nichts(self):
        """Das alte Vorgehen zerschnitt den fertigen String an ' = '."""
        eingaben = {"f_ck": D_F_CK.belegen(Groesse(30, MPA))}
        zeile = Formelzeile.bauen(
            D_ETA_FC.belegen(Groesse(1.0, EINHEITSLOS)),
            r"\left[@f_ck = 30\,\mathrm{MPa}\right]",
            eingaben,
        )
        self.assertEqual(len(zeile._teile()), 4)


class TestSichtbareBreite(unittest.TestCase):
    """Gezählt wird, was man gesetzt sieht -- nicht der Quelltext."""

    def test_formatierung_zaehlt_nicht(self):
        self.assertEqual(sichtbare_breite(r"\left(x\right)"), sichtbare_breite("(x)"))
        self.assertEqual(sichtbare_breite(r"30\,\mathrm{mm}"),
                         sichtbare_breite("30mm") + 0.2)

    def test_ein_bruch_ist_so_breit_wie_sein_breiterer_teil(self):
        self.assertAlmostEqual(sichtbare_breite(r"\frac{a}{bbbb}"),
                               sichtbare_breite("bbbb") + 0.4)

    def test_eine_umgebung_so_breit_wie_ihre_breiteste_zeile(self):
        self.assertEqual(sichtbare_breite(r"\begin{aligned} a \\ bbb \end{aligned}"), 3)

    def test_kurze_formel_bleibt_auf_einer_zeile(self):
        """Mit dem Quelltext gemessen standen solche Formeln auf drei Zeilen."""
        eingaben = {"b": D_B.belegen(Groesse(1000, MM)), "h": D_H.belegen(Groesse(300, MM))}
        zeile = Formelzeile.bauen(D_A.belegen(Groesse(300000, MM2)),
                                  r"\left(@b\right) \cdot \left(@h\right)", eingaben)
        self.assertGreater(len(zeile.einzeilig()), 90)
        self.assertEqual(zeile.darstellen(), zeile.einzeilig())


class TestFormel(unittest.TestCase):
    def test_rechnet_und_protokolliert(self):
        formel = formel_f_cd()
        eingaben = Eingaben({
            "eta_fc": D_ETA_FC.belegen(Groesse(0.933, EINHEITSLOS)),
            "f_ck": D_F_CK.belegen(Groesse(30, MPA)),
            "gamma_c": D_GAMMA_C.belegen(Groesse(1.5, EINHEITSLOS)),
        })
        p = Protokoll()
        ergebnis = formel.ausfuehren(eingaben, p)
        self.assertAlmostEqual(ergebnis[D_F_CD.id].in_einheit(MPA), 0.933 * 30 / 1.5)
        gleichungen = p.gleichungen()
        self.assertEqual(len(gleichungen), 1)
        self.assertEqual(gleichungen[0].referenz, "SIA 262:2025, 2.4.2.3")

    def test_falsche_dimension_der_ausgabe_wirft(self):
        kaputt = Formel(
            id="kaputt",
            ausgabe=D_F_CD,
            eingaben={"b": D_B.id},
            vorlage=r"@b",
            funktion=lambda b: b,  # liefert eine Laenge, deklariert ist eine Spannung
        )
        eingaben = Eingaben({"b": D_B.belegen(Groesse(1000, MM))})
        with self.assertRaises(BerechnungsFehler) as ctx:
            kaputt.ausfuehren(eingaben, Protokoll())
        self.assertIn("kaputt", str(ctx.exception))

    def test_fehler_wird_nicht_verschluckt(self):
        """Der alte Code lieferte bei einer defekten Formel einen alten Wert."""
        kaputt = Formel(
            id="teilt_durch_null",
            ausgabe=D_F_CD,
            eingaben={"f_ck": D_F_CK.id},
            vorlage=r"@f_ck",
            funktion=lambda f_ck: f_ck / 0,
        )
        eingaben = Eingaben({"f_ck": D_F_CK.belegen(Groesse(30, MPA))})
        with self.assertRaises(BerechnungsFehler) as ctx:
            kaputt.ausfuehren(eingaben, Protokoll())
        self.assertIsInstance(ctx.exception.__cause__, ZeroDivisionError)

    def test_nicht_deklarierte_ausgabe_wirft(self):
        class Schlampig(Berechnung):
            def rechne(self, e, p):
                return {D_F_CD.id: Groesse(1, MPA), "unbekannt": Groesse(1, MPA)}

        b = Schlampig("schlampig", ausgaben=[D_F_CD])
        with self.assertRaises(BerechnungsFehler) as ctx:
            b.ausfuehren(Eingaben({}), Protokoll())
        self.assertIn("unbekannt", str(ctx.exception))


class TestRechenwerkRueckwaerts(unittest.TestCase):
    def test_ziel_wird_aufgeloest(self):
        werk = standardwerk()
        werk.setze(D_F_CK.id, Groesse(30, MPA))
        werk.setze(D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS))
        loesung = werk.loese(D_F_CD.id)
        self.assertTrue(loesung.vollstaendig)
        self.assertAlmostEqual(
            loesung.groesse(D_F_CD.id).in_einheit(MPA),
            min((40 / 30) ** (1 / 3), 1.0) * 30 / 1.5,
        )

    def test_nur_noetige_berechnungen_laufen(self):
        """Die Flaeche wird fuer f_cd nicht gebraucht und darf nicht laufen."""
        werk = standardwerk()
        werk.setze(D_F_CK.id, Groesse(30, MPA))
        werk.setze(D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS))
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(D_F_CD.id)
        self.assertEqual(loesung.reihenfolge, ["b.eta_fc", "b.f_cd"])
        self.assertNotIn(D_A.id, loesung.werte)

    def test_abhaengigkeiten_vor_abhaengigen(self):
        werk = standardwerk()
        for wid, g in ((D_F_CK.id, Groesse(30, MPA)), (D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS)),
                       (D_B.id, Groesse(1000, MM)), (D_H.id, Groesse(300, MM))):
            werk.setze(wid, g)
        loesung = werk.loese(D_N_RD.id)
        self.assertEqual(loesung.reihenfolge, ["b.A", "b.eta_fc", "b.f_cd", "b.N_Rd"])

    def test_rueckverfolgung(self):
        werk = standardwerk()
        for wid, g in ((D_F_CK.id, Groesse(30, MPA)), (D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS)),
                       (D_B.id, Groesse(1000, MM)), (D_H.id, Groesse(300, MM))):
            werk.setze(wid, g)
        loesung = werk.loese(D_N_RD.id)
        self.assertEqual(loesung.kette(D_N_RD.id), ["b.A", "b.eta_fc", "b.f_cd", "b.N_Rd"])
        self.assertEqual(loesung.kette(D_F_CD.id), ["b.eta_fc", "b.f_cd"])
        self.assertIn(D_F_CK.id, loesung.benoetigte_werte(D_F_CD.id))
        self.assertNotIn(D_B.id, loesung.benoetigte_werte(D_F_CD.id))


class TestRechenwerkFehlendeEingaben(unittest.TestCase):
    def test_fehlende_eingabe_wird_benannt(self):
        werk = standardwerk()
        werk.setze(D_F_CK.id, Groesse(30, MPA))
        # gamma_c fehlt
        loesung = werk.loese(D_F_CD.id)
        self.assertFalse(loesung.vollstaendig)
        self.assertFalse(loesung.hat(D_F_CD.id))
        fehlende_ids = [f.id for f in loesung.fehlende]
        self.assertIn(D_GAMMA_C.id, fehlende_ids)

    def test_fehlende_eingabe_kennt_ihren_pfad(self):
        werk = standardwerk()
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        # f_ck und gamma_c fehlen -> N_Rd scheitert ueber f_cd
        loesung = werk.loese(D_N_RD.id)
        fehlend = {f.id: f for f in loesung.fehlende}
        self.assertIn(D_F_CK.id, fehlend)
        self.assertIn(D_F_CD.id, fehlend[D_F_CK.id].pfad)
        self.assertIn(D_N_RD.id, fehlend[D_F_CK.id].pfad)

    def test_fehlende_eingabe_kennt_ihre_beschreibung(self):
        werk = standardwerk()
        loesung = werk.loese(D_F_CD.id)
        fehlend = {f.id: f for f in loesung.fehlende}
        self.assertEqual(
            fehlend[D_F_CK.id].beschreibung, "Charakteristische Zylinderdruckfestigkeit"
        )

    def test_teilerfolg_bleibt_erhalten(self):
        """Was trotz Luecke berechenbar ist, soll berechnet werden."""
        werk = standardwerk()
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(D_N_RD.id, D_A.id)
        self.assertTrue(loesung.hat(D_A.id))
        self.assertFalse(loesung.hat(D_N_RD.id))


class TestRechenwerkVarianten(unittest.TestCase):
    """Welche Formel gilt, haengt von den vorhandenen Eingaben ab."""

    def _werk_mit_zwei_wegen(self) -> Rechenwerk:
        d_direkt = WertDef("qs.A_direkt", "A_{dir}", MM2, "Direkt angegebene Flaeche", stellen=0)
        werk = Rechenwerk()
        werk.definiere(D_B, D_H, d_direkt)
        werk.registriere(
            # Bevorzugt: direkt angegeben.
            Formel(
                id="A.direkt",
                ausgabe=D_A,
                eingaben={"A_direkt": d_direkt.id},
                vorlage=r"@A_direkt",
                funktion=lambda A_direkt: A_direkt,
                prioritaet=10,
                begruendung="Fläche wurde direkt angegeben.",
            ),
            # Rueckfall: aus den Abmessungen.
            Formel(
                id="A.aus_abmessungen",
                ausgabe=D_A,
                eingaben={"b": D_B.id, "h": D_H.id},
                vorlage=r"@b \cdot @h",
                funktion=lambda b, h: b * h,
                begruendung="Fläche aus Breite und Höhe bestimmt.",
            ),
        )
        return werk

    def test_bevorzugte_variante_wenn_eingabe_da(self):
        werk = self._werk_mit_zwei_wegen()
        werk.setze("qs.A_direkt", Groesse(250000, MM2))
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(D_A.id)
        self.assertEqual(loesung.reihenfolge, ["A.direkt"])
        self.assertAlmostEqual(loesung.groesse(D_A.id).in_einheit(MM2), 250000)

    def test_rueckfall_wenn_eingabe_fehlt(self):
        werk = self._werk_mit_zwei_wegen()
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(D_A.id)
        self.assertEqual(loesung.reihenfolge, ["A.aus_abmessungen"])
        self.assertAlmostEqual(loesung.groesse(D_A.id).in_einheit(MM2), 300000)
        self.assertTrue(loesung.vollstaendig)

    def test_wertabhaengige_anwendbarkeit(self):
        """anwendbar() darf vom Zahlenwert abhaengen, nicht nur von der Verfuegbarkeit."""
        werk = Rechenwerk()
        werk.definiere(D_F_CK, D_GAMMA_C)
        werk.registriere(
            Formel(
                id="f_cd.normalbeton",
                ausgabe=D_F_CD,
                eingaben={"f_ck": D_F_CK.id, "gamma_c": D_GAMMA_C.id},
                vorlage=r"\frac{@f_ck}{@gamma_c}",
                funktion=lambda f_ck, gamma_c: f_ck / gamma_c,
                prioritaet=10,
                bedingung=lambda e: (
                    (True, "f_ck ≤ 50 N/mm², Normalbeton")
                    if e.g("f_ck") <= Groesse(50, MPA)
                    else (False, "gilt nur bis C50/60")
                ),
            ),
            Formel(
                id="f_cd.hochfest",
                ausgabe=D_F_CD,
                eingaben={"f_ck": D_F_CK.id, "gamma_c": D_GAMMA_C.id},
                vorlage=r"\frac{0.8 \cdot @f_ck}{@gamma_c}",
                funktion=lambda f_ck, gamma_c: 0.8 * f_ck / gamma_c,
                begruendung="hochfester Beton",
            ),
        )
        werk.setze(D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS))

        werk.setze(D_F_CK.id, Groesse(30, MPA))
        self.assertEqual(werk.loese(D_F_CD.id).reihenfolge, ["f_cd.normalbeton"])

        werk.setze(D_F_CK.id, Groesse(60, MPA))
        loesung = werk.loese(D_F_CD.id)
        self.assertEqual(loesung.reihenfolge, ["f_cd.hochfest"])
        self.assertAlmostEqual(loesung.groesse(D_F_CD.id).in_einheit(MPA), 0.8 * 60 / 1.5)

    def test_begruendung_steht_im_protokoll(self):
        werk = self._werk_mit_zwei_wegen()
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(D_A.id)
        texte = [
            b.text for b in loesung.protokoll.alle_bloecke() if hasattr(b, "text")
        ]
        self.assertTrue(any("Breite und Höhe" in t for t in texte))


class TestRechenwerkUeberschreiben(unittest.TestCase):
    def test_ueberschriebener_wert_umgeht_die_berechnung(self):
        werk = standardwerk()
        werk.setze(D_F_CK.id, Groesse(30, MPA))
        werk.setze(D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS))
        werk.setze(D_F_CD.id, Groesse(20, MPA))
        loesung = werk.loese(D_F_CD.id)
        self.assertAlmostEqual(loesung.groesse(D_F_CD.id).in_einheit(MPA), 20.0)
        self.assertEqual(loesung.reihenfolge, [])
        self.assertEqual(loesung.wert(D_F_CD.id).quelle, Quelle.UEBERSCHRIEBEN)

    def test_ueberschreiben_kappt_den_zweig(self):
        """Wird f_cd gesetzt, braucht es weder f_ck noch gamma_c."""
        werk = standardwerk()
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        werk.setze(D_F_CD.id, Groesse(20, MPA))
        loesung = werk.loese(D_N_RD.id)
        self.assertTrue(loesung.vollstaendig)
        self.assertAlmostEqual(loesung.groesse(D_N_RD.id).in_einheit(KN), 300000 * 20 / 1000)

    def test_quelle_eingabe_bei_reinem_eingabewert(self):
        werk = standardwerk()
        werk.setze(D_F_CK.id, Groesse(30, MPA))
        self.assertEqual(werk.vorgegebene_werte[D_F_CK.id].quelle, Quelle.EINGABE)

    def test_ruecknahme_der_ueberschreibung(self):
        werk = standardwerk()
        werk.setze(D_F_CK.id, Groesse(30, MPA))
        werk.setze(D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS))
        werk.setze(D_F_CD.id, Groesse(20, MPA))
        werk.loesche(D_F_CD.id)
        loesung = werk.loese(D_F_CD.id)
        self.assertEqual(loesung.reihenfolge, ["b.eta_fc", "b.f_cd"])

    def test_unbekannter_wert_kann_nicht_gesetzt_werden(self):
        werk = standardwerk()
        with self.assertRaises(RechenwerkFehler):
            werk.setze("gibt.es.nicht", Groesse(1, MPA))


class TestRechenwerkZyklus(unittest.TestCase):
    def test_kreis_wird_erkannt(self):
        a = WertDef("z.a", "a", EINHEITSLOS)
        b = WertDef("z.b", "b", EINHEITSLOS)
        werk = Rechenwerk()
        werk.registriere(
            Formel(id="z.a_aus_b", ausgabe=a, eingaben={"b": b.id},
                   vorlage="@b", funktion=lambda b: b),
            Formel(id="z.b_aus_a", ausgabe=b, eingaben={"a": a.id},
                   vorlage="@a", funktion=lambda a: a),
        )
        with self.assertRaises(ZyklusFehler) as ctx:
            werk.loese("z.a")
        self.assertIn("z.a", str(ctx.exception))


class TestRechenwerkVorwaerts(unittest.TestCase):
    def test_alles_was_moeglich_ist(self):
        werk = standardwerk()
        werk.setze(D_B.id, Groesse(1000, MM))
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese_alles()
        self.assertTrue(loesung.hat(D_A.id))
        self.assertFalse(loesung.hat(D_F_CD.id))
        self.assertIn(D_F_CD.id, loesung.nicht_berechenbar)

    def test_mit_allen_eingaben_geht_alles(self):
        werk = standardwerk()
        for wid, g in ((D_F_CK.id, Groesse(30, MPA)), (D_GAMMA_C.id, Groesse(1.5, EINHEITSLOS)),
                       (D_B.id, Groesse(1000, MM)), (D_H.id, Groesse(300, MM))):
            werk.setze(wid, g)
        loesung = werk.loese_alles()
        self.assertTrue(loesung.vollstaendig)
        self.assertEqual(len(loesung.reihenfolge), 4)


class TestVorgabe(unittest.TestCase):
    def test_konstante_als_knoten(self):
        werk = Rechenwerk()
        werk.registriere(
            Vorgabe(
                id="v.gamma_c",
                ausgabe=D_GAMMA_C,
                groesse=Groesse(1.5, EINHEITSLOS),
                begruendung="Ständige Bemessungssituation.",
            )
        )
        loesung = werk.loese(D_GAMMA_C.id)
        self.assertAlmostEqual(loesung.groesse(D_GAMMA_C.id).si, 1.5)
        self.assertEqual(loesung.wert(D_GAMMA_C.id).quelle, Quelle.VORGABE)

    def test_vorgabe_ist_ueberschreibbar(self):
        werk = Rechenwerk()
        werk.registriere(
            Vorgabe(id="v.gamma_c", ausgabe=D_GAMMA_C, groesse=Groesse(1.5, EINHEITSLOS))
        )
        werk.setze(D_GAMMA_C.id, Groesse(1.2, EINHEITSLOS))
        loesung = werk.loese(D_GAMMA_C.id)
        self.assertAlmostEqual(loesung.groesse(D_GAMMA_C.id).si, 1.2)


class TestProzedur(unittest.TestCase):
    """Eine Prozedur liefert mehrere Werte und schreibt ihren Ablauf mit."""

    def _iterations_prozedur(self):
        d_x = WertDef("p.x", "x", MM, "Nulllinienlage", stellen=2)
        d_i = WertDef("p.i", "n_{iter}", EINHEITSLOS, "Anzahl Iterationsschritte", stellen=0)

        class Wurzelsuche(Prozedur):
            def rechne(self, e: Eingaben, p) -> Mapping[str, Groesse]:
                p.text("Die Nulllinienlage wird iterativ eingegabelt.")
                ziel = e.g("h")
                unten, oben = Groesse(0, MM), ziel
                zeilen = []
                schritt = 0
                for schritt in range(1, 21):
                    mitte = (unten + oben) / 2
                    if mitte * mitte < ziel * ziel / 4:
                        unten = mitte
                    else:
                        oben = mitte
                    zeilen.append([str(schritt), mitte.als_latex(2)])
                    if (oben - unten) < Groesse(0.01, MM):
                        break
                p.tabelle(["i", "x_i"], zeilen, titel="Iterationsverlauf")
                x = (unten + oben) / 2
                p.formel(d_x.belegen(x), r"\frac{@h}{2}", {"h": e["h"]})
                return {d_x.id: x, d_i.id: Groesse(schritt, EINHEITSLOS)}

        return d_x, d_i, Wurzelsuche(
            "p.wurzelsuche",
            ausgaben=[d_x, d_i],
            bezuege=[Eingabebezug("h", D_H.id)],
            titel="Nulllinienlage",
        )

    def test_mehrere_ausgaben(self):
        d_x, d_i, prozedur = self._iterations_prozedur()
        werk = Rechenwerk()
        werk.definiere(D_H)
        werk.registriere(prozedur)
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(d_x.id)
        self.assertAlmostEqual(loesung.groesse(d_x.id).in_einheit(MM), 150, places=1)
        # Die zweite Ausgabe entsteht im selben Lauf mit.
        self.assertTrue(loesung.hat(d_i.id))

    def test_ablauf_wird_mitgeschrieben(self):
        d_x, d_i, prozedur = self._iterations_prozedur()
        werk = Rechenwerk()
        werk.definiere(D_H)
        werk.registriere(prozedur)
        werk.setze(D_H.id, Groesse(300, MM))
        loesung = werk.loese(d_x.id)
        bloecke = list(loesung.protokoll.alle_bloecke())
        tabellen = [b for b in bloecke if isinstance(b, TabellenBlock)]
        self.assertEqual(len(tabellen), 1)
        self.assertGreater(len(tabellen[0].zeilen), 3)
        self.assertIn(r"\begin{tabular}", tabellen[0].als_latex())

    def test_stilles_protokoll_verwirft(self):
        d_x, d_i, prozedur = self._iterations_prozedur()
        eingaben = Eingaben({"h": D_H.belegen(Groesse(300, MM))})
        still = StillesProtokoll()
        ergebnis = prozedur.ausfuehren(eingaben, still)
        self.assertAlmostEqual(ergebnis[d_x.id].in_einheit(MM), 150, places=1)
        self.assertTrue(still.ist_leer)


class TestNachweis(unittest.TestCase):
    def test_urteil_wird_gesammelt(self):
        d_ausn = WertDef("n.grad", r"\alpha_{eff}", EINHEITSLOS, "Erfüllungsgrad", stellen=2)
        d_m_ed = WertDef("n.M_Ed", "M_{Ed}", KNM, "Bemessungsmoment", stellen=1)
        d_m_rd = WertDef("n.M_Rd", "M_{Rd}", KNM, "Momentenwiderstand", stellen=1)

        class Biegenachweis(Nachweis):
            def pruefe(self, e, p):
                m_ed, m_rd = e.g("M_Ed"), e.g("M_Rd")
                grad = m_rd / m_ed
                erfuellt = grad >= Groesse(1.0, EINHEITSLOS)
                p.formel(d_ausn.belegen(grad), r"\frac{@M_Rd}{@M_Ed}", e)
                return {d_ausn.id: grad}, [
                    NachweisUrteil(
                        name="Biegewiderstand",
                        erfuellt=erfuellt,
                        erfuellungsgrad=grad,
                        einwirkung=e["M_Ed"],
                        widerstand=e["M_Rd"],
                    )
                ]

        werk = Rechenwerk()
        werk.definiere(d_m_ed, d_m_rd)
        werk.registriere(
            Biegenachweis(
                "n.biegung",
                ausgaben=[d_ausn],
                bezuege=[Eingabebezug("M_Ed", d_m_ed.id), Eingabebezug("M_Rd", d_m_rd.id)],
            )
        )
        werk.setze(d_m_ed.id, Groesse(120, KNM))
        werk.setze(d_m_rd.id, Groesse(150, KNM))
        loesung = werk.loese(d_ausn.id)

        self.assertEqual(len(loesung.urteile), 1)
        self.assertTrue(loesung.alle_nachweise_erfuellt)
        self.assertAlmostEqual(loesung.urteile[0].erfuellungsgrad.si, 1.25)

        werk.setze(d_m_ed.id, Groesse(200, KNM))
        self.assertFalse(werk.loese(d_ausn.id).alle_nachweise_erfuellt)


class TestHinweisReihenfolge(unittest.TestCase):
    """
    Ein Hinweis gehört hinter seine eigene Gleichung, nicht davor.

    Davor stand er unmittelbar unter der vorherigen Gleichung und las sich wie
    deren Begründung. So ist der "Regelwert für übliche Gesteinskörnung" von
    k_e unter den Teilsicherheitsbeiwert für den Elastizitätsmodul geraten --
    ein Hinweis am falschen Wert ist schlimmer als gar keiner.
    """

    def bloecke(self):
        from opencivil.core.protokoll import HinweisBlock

        erst = WertDef("a.erst", "a", EINHEITSLOS, "Erster Wert")
        zweit = WertDef("a.zweit", "b", EINHEITSLOS, "Zweiter Wert")

        werk = Rechenwerk()
        werk.registriere(Vorgabe(id="a.erst", ausgabe=erst,
                                 groesse=Groesse(1, EINHEITSLOS)))
        werk.registriere(Vorgabe(id="a.zweit", ausgabe=zweit,
                                 groesse=Groesse(2, EINHEITSLOS),
                                 begruendung="Gehört zum zweiten Wert."))
        loesung = werk.loese(erst.id, zweit.id)
        return [
            b for b in loesung.protokoll.alle_bloecke()
            if isinstance(b, (GleichungBlock, HinweisBlock))
        ]

    def test_hinweis_folgt_der_eigenen_gleichung(self):
        from opencivil.core.protokoll import HinweisBlock

        bloecke = self.bloecke()
        stelle = next(i for i, b in enumerate(bloecke) if isinstance(b, HinweisBlock))
        davor = bloecke[stelle - 1]

        self.assertIsInstance(davor, GleichungBlock)
        self.assertEqual(davor.wert_id, "a.zweit",
                         "der Hinweis steht unter der falschen Gleichung")

    def test_ohne_begruendung_kein_hinweis(self):
        from opencivil.core.protokoll import HinweisBlock

        self.assertEqual(
            1, sum(1 for b in self.bloecke() if isinstance(b, HinweisBlock)))


if __name__ == "__main__":
    unittest.main()


class TestStillstellen(unittest.TestCase):
    """
    Welche Fälle nur mitrechnen -- und was passiert, wenn man sich vertippt.
    """

    def nachweis(self):
        from opencivil.core.berechnung import Nachweis
        from opencivil.core.einheiten import EINHEITSLOS
        from opencivil.core.wert import WertDef

        class Probe(Nachweis):
            def pruefe(self, e, p):
                return {}, []

        return Probe("probe", ausgaben=[WertDef(
            id="probe.wert", symbol="x", einheit=EINHEITSLOS,
            beschreibung="Probe")])

    def test_einer_laut_heisst_der_nachweis_spricht(self):
        n = self.nachweis()
        n.stillstellen([1, 2, 3, 4], [2])
        self.assertFalse(n.still)
        self.assertEqual(n.stille_faelle, {1, 3, 4})
        self.assertTrue(n.leise(1))
        self.assertFalse(n.leise(2))

    def test_keiner_laut_heisst_der_ganze_nachweis_schweigt(self):
        n = self.nachweis()
        n.stillstellen([1, 2], [])
        self.assertTrue(n.still)
        self.assertTrue(n.leise(1))
        self.assertTrue(n.leise(2))

    def test_ein_unbekannter_schluessel_wird_gemeldet(self):
        """
        Stillschweigend übergangen wäre er die unangenehmste Art von Fehler:
        der Nachweis verschwände aus Tabelle und Herleitung, ohne dass
        irgendwo etwas danebenstünde.
        """
        n = self.nachweis()
        with self.assertRaises(BerechnungsFehler) as fehler:
            n.stillstellen([1, 2, 3, 4], ["2"])      # String statt Zahl
        self.assertIn("kommen aber nicht vor", str(fehler.exception))
        self.assertIn("'2'", str(fehler.exception))
