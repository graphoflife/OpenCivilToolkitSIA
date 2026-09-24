"""Tests fuer die Berichtsausgabe (Konsole und LaTeX)."""

import re
import tempfile
import unittest
from pathlib import Path

from opencivil.bericht.konsole import als_text, protokoll_zeilen
from opencivil.bericht.latex_dokument import (
    als_tex, finde_tex_maschine, formeln_sammeln, schreibe,
)
from opencivil.core.einheiten import EINHEITSLOS, KNM, MM, N_PRO_MM2, Groesse
from opencivil.core.protokoll import Protokoll, TextBlock, TitelBlock
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.core.wert import WertDef
from opencivil.material.beton import beton


def beispiel_loesung(vollstaendig: bool = True):
    werk = Rechenwerk()
    c30 = beton("C30/37").ins_rechenwerk(werk)
    if not vollstaendig:
        werk._nach_ausgabe.pop(c30.id_von("f_ck"))
    return werk.loese(c30.id_von("f_cd")), c30


class TestKonsole(unittest.TestCase):
    def test_bericht_enthaelt_die_abschnitte(self):
        loesung, c30 = beispiel_loesung()
        text = als_text(loesung, titel="Prüfbericht")
        self.assertIn("Prüfbericht", text)
        self.assertIn("Herleitung", text)
        self.assertIn("Werte", text)
        self.assertIn(c30.id_von("f_cd"), text)

    def test_latex_wird_roh_ausgegeben(self):
        """Auf der Konsole soll der LaTeX-Quelltext lesbar dastehen."""
        loesung, _ = beispiel_loesung()
        text = als_text(loesung)
        self.assertIn(r"\frac", text)
        self.assertIn(r"\mathrm{N}/\mathrm{mm}^{2}", text)

    def test_fehlende_eingaben_werden_aufgefuehrt(self):
        loesung, c30 = beispiel_loesung(vollstaendig=False)
        text = als_text(loesung)
        self.assertIn("Fehlende Eingaben", text)
        self.assertIn(c30.id_von("f_ck"), text)

    def test_ueberschriebene_werte_sind_gekennzeichnet(self):
        werk = Rechenwerk()
        c30 = beton("C30/37").ins_rechenwerk(werk)
        werk.setze(c30.id_von("f_cd"), Groesse(15, N_PRO_MM2))
        text = als_text(werk.loese(c30.id_von("f_cd")))
        self.assertIn("ÜBERSCHRIEBEN", text)

    def test_tabelle_wird_ausgerichtet(self):
        p = Protokoll()
        p.tabelle(["i", "x"], [["1", "150.00"], ["2", "75.0"]], titel="Verlauf")
        zeilen = protokoll_zeilen(p)
        self.assertTrue(any("Verlauf" in z for z in zeilen))
        self.assertTrue(any("150.00" in z for z in zeilen))

    def test_leere_loesung_stuerzt_nicht_ab(self):
        als_text(Rechenwerk().loese())


class TestLatexDokument(unittest.TestCase):
    def test_dokument_ist_vollstaendig(self):
        loesung, _ = beispiel_loesung()
        tex = als_tex(loesung, titel="Prüfbericht")
        self.assertIn(r"\documentclass", tex)
        self.assertIn(r"\begin{document}", tex)
        self.assertIn(r"\end{document}", tex)
        # Die Praeambel muss vor jedem eigenen Befehl stehen.
        self.assertLess(tex.index(r"\documentclass"), tex.index(r"\newcommand"))

    def test_umlaute_bleiben_erhalten(self):
        loesung, _ = beispiel_loesung()
        tex = als_tex(loesung, titel="Decke über EG")
        self.assertIn("über", tex)
        self.assertIn(r"\usepackage[utf8]{inputenc}", tex)

    def test_sonderzeichen_im_text_werden_maskiert(self):
        d = WertDef("x.a", "a", EINHEITSLOS, "Anteil in % & mehr")
        werk = Rechenwerk()
        werk.definiere(d)
        werk.setze(d.id, Groesse(1, EINHEITSLOS))
        tex = als_tex(werk.loese(d.id))
        self.assertIn(r"\%", tex)
        self.assertIn(r"\&", tex)

    def test_werteuebersicht(self):
        loesung, c30 = beispiel_loesung()
        tex = als_tex(loesung)
        self.assertIn("Werteübersicht", tex)
        self.assertIn(r"\begin{longtable}", tex)

    def test_fehlende_eingaben_im_dokument(self):
        loesung, c30 = beispiel_loesung(vollstaendig=False)
        tex = als_tex(loesung)
        self.assertIn("Fehlende Eingaben", tex)

    def test_schreiben_erzeugt_datei(self):
        loesung, _ = beispiel_loesung()
        with tempfile.TemporaryDirectory() as ordner:
            ziel = Path(ordner) / "unterordner" / "bericht"
            ergebnis = schreibe(loesung, ziel, titel="Test", pdf=False)
            self.assertTrue(ergebnis.tex_pfad.exists())
            self.assertIn(r"\documentclass", ergebnis.tex_pfad.read_text(encoding="utf-8"))

    def test_ohne_tex_maschine_kein_fehler(self):
        """Fehlt eine TeX-Maschine, bleibt es beim .tex -- ohne Absturz."""
        loesung, _ = beispiel_loesung()
        with tempfile.TemporaryDirectory() as ordner:
            ergebnis = schreibe(loesung, Path(ordner) / "b", titel="Test", pdf=True)
            self.assertTrue(ergebnis.tex_pfad.exists())
            if finde_tex_maschine() is None:
                self.assertFalse(ergebnis.hat_pdf)
                self.assertIn("keine TeX-Maschine", ergebnis.meldung)


class TestFormelnSammeln(unittest.TestCase):
    def test_jede_formel_einzeln(self):
        loesung, c30 = beispiel_loesung()
        formeln = formeln_sammeln(loesung)
        self.assertGreaterEqual(len(formeln), 4)
        ids = [f.wert_id for f in formeln]
        self.assertIn(c30.id_von("f_cd"), ids)

    def test_referenz_wird_mitgeliefert(self):
        loesung, c30 = beispiel_loesung()
        f_cd = next(f for f in formeln_sammeln(loesung) if f.wert_id == c30.id_von("f_cd"))
        self.assertEqual(f_cd.referenz, "SIA 262:2025, 2.4.2.3")
        self.assertIn(r"\frac", f_cd.latex)


class TestTextMaskierung(unittest.TestCase):
    r"""
    Nichts Unmaskiertes in ``\text{...}``.

    Namen kommen aus dem Projekt oder aus einer Berechnung: ``C12/15_1``,
    ``M_Rd(N=0) +``. Der Unterstrich ist auch im Textmodus ein
    Tiefstellungsbefehl -- KaTeX bricht ab, und die Oberfläche zeigt dann den
    rohen Quelltext statt der Beschriftung. Genau das ist zweimal passiert,
    darum dieser Wächter über der ganzen Mitschrift.
    """

    #: Zeichen, die in \text{...} maskiert sein müssen.
    HEIKEL = "_^&%$#"

    def unmaskierte_stellen(self, latex: str):
        """Alle \\text{...}-Inhalte mit unmaskierten Sonderzeichen."""
        treffer = []
        for inhalt in re.findall(r"\\text\{([^{}]*)\}", latex):
            # Ein Zeichen gilt als maskiert, wenn unmittelbar davor ein
            # Rückwärtsstrich steht.
            for i, zeichen in enumerate(inhalt):
                if zeichen in self.HEIKEL and (i == 0 or inhalt[i - 1] != "\\"):
                    treffer.append(inhalt)
                    break
        return treffer

    def test_erkennt_den_fehler_ueberhaupt(self):
        """Der Wächter muss anschlagen, sonst prüft er nichts."""
        self.assertTrue(self.unmaskierte_stellen(r"\text{M_Rd(N=0)}"))
        self.assertFalse(self.unmaskierte_stellen(r"\text{M\_Rd(N=0)}"))
        self.assertFalse(self.unmaskierte_stellen(r"\text{grösste Zugkraft}"))

    def test_die_ganze_mitschrift_ist_sauber(self):
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock
        from opencivil.projekt import Projekt

        aufbau = Projekt.beispiel().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())

        for block in loesung.protokoll.alle_bloecke():
            if isinstance(block, GleichungBlock):
                stuecke = [block.latex]
            elif isinstance(block, TabellenBlock):
                stuecke = list(block.kopf) + [z for zeile in block.zeilen for z in zeile]
            else:
                continue
            for stueck in stuecke:
                schlecht = self.unmaskierte_stellen(stueck)
                self.assertEqual(
                    [], schlecht,
                    f"unmaskiert in \\text{{...}}: {schlecht} – bitte als_text() "
                    f"verwenden statt \\text{{}} von Hand")

    def test_als_text_maskiert(self):
        from opencivil.core.latex import als_text

        self.assertEqual(als_text("M_Rd(N=0) +"), r"\text{M\_Rd(N=0) +}")
        self.assertEqual(als_text("C12/15_1"), r"\text{C12/15\_1}")
        # Umlaute bleiben stehen -- der Bericht ist UTF-8.
        self.assertEqual(als_text("grösste Zugkraft"), r"\text{grösste Zugkraft}")

    def test_text_maskieren_ist_dieselbe_funktion(self):
        """Zwei Maskierungen nebeneinander wären zwei Stellen zum Auseinanderlaufen."""
        from opencivil.core.latex import text_latex
        from opencivil.material.basis import text_maskieren

        self.assertIs(text_maskieren, text_latex)


if __name__ == "__main__":
    unittest.main()


class TestAbschnittsordnung(unittest.TestCase):
    """
    Gerechnet wird in Abhängigkeitsreihenfolge, gelesen wird nach Bauteilen.

    Der Querkraftnachweis einer Platte braucht ihren Momentenwiderstand und
    kommt darum erst, wenn alle M-N-Nachweise durch sind. Im Protokoll stand
    die Überschrift einer Platte deshalb zweimal, mit der anderen Platte
    dazwischen.
    """

    def protokoll(self) -> Protokoll:
        p = Protokoll()
        p.titel("Beton: C30/37", raum="beton.b1")
        p.text("f_cd")
        p.titel("Platte A", raum="querschnitt.q1")
        p.text("A: Biegung")
        p.titel("Platte B", raum="querschnitt.q2")
        p.text("B: Biegung")
        p.titel("Platte A", raum="querschnitt.q1")
        p.titel("Querkraft", ebene=3)          # ohne Raum: eröffnet nichts
        p.text("A: Querkraft")
        p.titel("Platte B", raum="querschnitt.q2")
        p.text("B: Querkraft")
        return p

    def test_jede_ueberschrift_steht_genau_einmal(self):
        titel = [b.text for b in self.protokoll().nach_abschnitten()
                 if isinstance(b, TitelBlock) and b.raum]
        self.assertEqual(titel, ["Beton: C30/37", "Platte A", "Platte B"])

    def test_der_inhalt_folgt_seinem_abschnitt(self):
        texte = [b.text for b in self.protokoll().nach_abschnitten()
                 if isinstance(b, TextBlock)]
        self.assertEqual(texte, ["f_cd", "A: Biegung", "A: Querkraft",
                                 "B: Biegung", "B: Querkraft"])

    def test_untertitel_ohne_raum_bleiben_bei_ihrem_abschnitt(self):
        bloecke = self.protokoll().nach_abschnitten()
        namen = [getattr(b, "text", "") for b in bloecke]
        self.assertEqual(namen.index("Querkraft"), namen.index("A: Querkraft") - 1)

    def test_kein_block_geht_verloren(self):
        p = self.protokoll()
        self.assertEqual(len(p.nach_abschnitten()), len(p.bloecke) - 2)  # 2 Dubletten

    def test_ohne_abschnitte_bleibt_alles_wie_es_ist(self):
        p = Protokoll()
        p.text("eins")
        p.titel("Zwischentitel", ebene=3)
        p.text("zwei")
        self.assertEqual(p.nach_abschnitten(), p.bloecke)


class TestStilleNachweiseImBericht(unittest.TestCase):
    """
    Ein ausgeschalteter Nachweis darf nicht als geführter dastehen.

    Beide Berichte zählten früher jedes Urteil auf, der Schlusssatz darunter
    aber nur die geführten -- das Dokument widersprach sich selbst: vier
    Zeilen «nicht erfüllt» und darunter «Sämtliche Nachweise sind erfüllt».
    """

    def loesung(self):
        """Eine Platte, an der nur *stille* Nachweise durchfallen."""
        from opencivil.projekt import Projekt

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.h = 600.0
        for k in q.kombinationen:
            k.M_Ed, k.N_Ed, k.V_Ed = 10.0, 0.0, 0.0
        lage = q.lagen[0]
        lage.grund.durchmesser, lage.grund.abstand = 6.0, 300.0
        lage.zulage.durchmesser = 0.0
        aufbau = projekt.aufbauen()
        return aufbau.werk.loese(*aufbau.alle_nachweisziele())

    def test_die_probe_faellt_wirklich_nur_still_durch(self):
        """Sonst prüfte der Rest nichts."""
        loesung = self.loesung()
        self.assertTrue(loesung.stille_maengel)
        self.assertTrue(loesung.alle_nachweise_erfuellt)

    def test_die_konsole_zaehlt_nur_gefuehrte_auf(self):
        text = als_text(self.loesung())
        abschnitt = text[text.index("Nachweise"):]
        kopf = abschnitt[:abschnitt.index("Nicht geführt")]
        self.assertNotIn("Rissnormalkraft", kopf)
        self.assertIn("M-N-Nachweis", kopf)

    def test_die_konsole_verschweigt_sie_aber_nicht(self):
        text = als_text(self.loesung())
        self.assertIn("Nicht geführt, geht aber nicht auf:", text)
        self.assertIn("Rissnormalkraft x –", text)

    def test_das_latex_dokument_widerspricht_sich_nicht(self):
        tex = als_tex(self.loesung())
        tabelle = tex[tex.index("Zusammenstellung der Nachweise"):]
        tabelle = tabelle[:tabelle.index(r"\end{longtable}")]
        self.assertNotIn("Rissnormalkraft", tabelle)
        self.assertNotIn("nicht erfüllt", tabelle)
        self.assertIn("Sämtliche geführten Nachweise sind erfüllt.", tex)

    def test_das_latex_dokument_meldet_sie_darunter(self):
        tex = als_tex(self.loesung())
        hinweis = tex[tex.index("Nicht geführte Nachweise"):]
        self.assertIn("Rissnormalkraft", hinweis)
