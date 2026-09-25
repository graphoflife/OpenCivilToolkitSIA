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
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import (
    Block, Protokoll, TextBlock, TitelBlock, UnterprotokollBlock, darstellen,
)
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
        # Die Werteuebersicht nennt jeden Wert mit Bezeichnung und Symbol.
        self.assertIn("Bemessungswert der Betondruckfestigkeit", text)
        self.assertIn(c30.definition("f_cd").symbol, text)

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
        self.assertIn("vom Benutzer überschrieben", text)

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
        self.assertIn(r"\section{Werte}", tex)
        # Lang genug fuer mehrere Seiten: der Kopf wiederholt sich dort.
        werte = tex[tex.index(r"\section{Werte}"):]
        self.assertIn(r"\begin{xltabular}", werte)
        self.assertIn(r"\endhead", werte)

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
        from opencivil.core.latex import Mathe
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock
        from opencivil.projekt import Projekt

        aufbau = Projekt.beispiel().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())

        for block in loesung.protokoll.alle_bloecke():
            if isinstance(block, GleichungBlock):
                stuecke = [block.latex]
            elif isinstance(block, TabellenBlock):
                # Nur die Mathe-Zellen sind LaTeX; Text wird beim Setzen
                # maskiert und steht hier roh.
                zellen = list(block.kopf) + [z for zeile in block.zeilen for z in zeile]
                stuecke = [z.latex for z in zellen if isinstance(z, Mathe)]
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

    def aufbau_und_loesung(self):
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
        return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())

    def text(self) -> str:
        aufbau, loesung = self.aufbau_und_loesung()
        return als_text(loesung, aufbau=aufbau)

    def tex(self) -> str:
        aufbau, loesung = self.aufbau_und_loesung()
        return als_tex(loesung, aufbau=aufbau)

    def test_die_probe_faellt_wirklich_nur_still_durch(self):
        """Sonst prüfte der Rest nichts."""
        _, loesung = self.aufbau_und_loesung()
        self.assertTrue(loesung.stille_maengel)
        self.assertTrue(loesung.alle_nachweise_erfuellt)
        self.assertTrue(any(u.name.startswith("Rissnormalkraft")
                            for u in loesung.stille_maengel))

    def test_die_konsole_zaehlt_nur_gefuehrte_auf(self):
        text = self.text()
        abschnitt = text[text.index("\nNachweise\n"):]
        tabelle = abschnitt[:abschnitt.index("[i] Hinweis")]
        self.assertNotIn("Zwängung auf Normalkraft", tabelle)
        self.assertIn("Biegung und Normalkraft", tabelle)
        self.assertIn("Alle geführten Nachweise sind erfüllt.", abschnitt)

    def test_die_konsole_verschweigt_sie_aber_nicht(self):
        text = self.text()
        self.assertRegex(text, r"\[i\] Hinweis: Zwängung auf Normalkraft – \d\. Lage: "
                               r"nicht erfüllt")
        # Die Konsole bricht den Satz um; verglichen wird der Wortlaut.
        self.assertIn("Dieser Nachweis ist ausgeschaltet", " ".join(text.split()))

    def test_das_latex_dokument_widerspricht_sich_nicht(self):
        tex = self.tex()
        abschnitt = tex[tex.index(r"\section{Nachweise}"):]
        tabelle = abschnitt[abschnitt.index("Nachweis & Bezeichnung"):]
        tabelle = tabelle[:tabelle.index(r"\end{xltabular}")]
        self.assertNotIn("Zwängung auf Normalkraft", tabelle)
        self.assertNotIn("nicht erfüllt", tabelle)
        self.assertIn("Alle geführten Nachweise sind erfüllt.", abschnitt)

    def test_das_latex_dokument_meldet_sie_darunter(self):
        tex = self.tex()
        abschnitt = tex[tex.index(r"\section{Nachweise}"):]
        hinweis = abschnitt[abschnitt.index(r"\end{xltabular}"):]
        self.assertRegex(hinweis, r"\\hinweis\{Hinweis\}\{Zwängung auf Normalkraft – "
                                  r"\d\. Lage: nicht erfüllt")


class TestKnappVerfehlterGrad(unittest.TestCase):
    """
    0.9966 ist nicht erfüllt, und so darf es auch nicht aussehen.

    Das Beispielprojekt trägt genau einen solchen Fall: die Rissnormalkraft
    der 3. Lage, still, mit α = 0.9966. Auf zwei Stellen gerundet stand in
    beiden Berichten «1» -- neben der Überschrift «geht aber nicht auf».
    """

    @classmethod
    def setUpClass(cls):
        from opencivil.projekt import Projekt

        cls.aufbau = Projekt.beispiel().aufbauen()
        cls.loesung = cls.aufbau.werk.loese(*cls.aufbau.alle_nachweisziele())
        cls.urteil = next(u for u in cls.loesung.stille_maengel
                          if u.name == "Rissnormalkraft x – 3. Lage")

    def test_die_probe_ist_knapp_verfehlt(self):
        """Sonst prüfte der Rest nichts."""
        self.assertFalse(self.urteil.erfuellt)
        self.assertEqual(f"{self.urteil.erfuellungsgrad.si:.2f}", "1.00")

    def test_die_konsole_schreibt_ihn_kleiner_als_eins(self):
        text = als_text(self.loesung, aufbau=self.aufbau)
        self.assertIn("Zwängung auf Normalkraft – 3. Lage: nicht erfüllt "
                      "(α_eff = 0.996)", text)
        self.assertNotIn("(α_eff = 1)", text)

    def test_das_latex_dokument_auch(self):
        tex = als_tex(self.loesung, aufbau=self.aufbau)
        self.assertIn(r"(α\_eff = 0.996)", tex)
        self.assertNotIn(r"(α\_eff = 1)", tex)

    def test_die_herleitung_auch(self):
        """
        Eingeschaltet steht der Nachweis in der Herleitung. Dort rundete jeder
        Nachweis seinen Grad selbst -- «= 1.00» neben «nicht erfüllt».
        """
        from opencivil.core.protokoll import GleichungBlock
        from opencivil.projekt import Projekt

        projekt = Projekt.beispiel()
        projekt.querschnitt("q1").zwaengung = True
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        urteil = next(u for u in loesung.gefuehrte_urteile
                      if u.name == "Rissnormalkraft x – 3. Lage")
        self.assertFalse(urteil.erfuellt)
        grade = [b.latex for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock) and b.titel == "Erfüllungsgrad"
                 and r"\alpha_{eff,NR,3" in b.latex]
        self.assertEqual(len(grade), 1)
        self.assertIn("0.996", grade[0])
        self.assertNotIn("1.00", grade[0])

    def test_die_diagrammpunkte_bringen_den_grad_fertig_mit(self):
        """
        Die Tooltips rundeten in JavaScript selbst -- ``toFixed(2)`` neben
        «NICHT erfüllt». Jetzt kommt der Text aus derselben Regel.
        """
        from opencivil.projekt import KnickEintrag, Projekt
        from opencivil.web import api

        projekt = Projekt.beispiel()
        projekt.querschnitte[0].knickfaelle = [KnickEintrag(
            "schlank", N_Ed=-1500.0, M_Ed_1=30.0, laenge=12.0, knicklaenge=12.0)]
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        linie = api.loesung_dict(loesung, aufbau=aufbau)["linien"]["q1.x"]
        self.assertEqual([k["grad_text"] for k in linie["kombinationen"]],
                         ["2.36", "2.54", "1.60"])
        knick = linie["knickfaelle"][0]
        self.assertFalse(knick["erfuellt"])
        from opencivil.core.berechnung import grad_als_text

        self.assertEqual(knick["grad_text"],
                         grad_als_text(knick["erfuellungsgrad"], False))


class TestMarkdown(unittest.TestCase):
    """Der Bericht als Markdown: Text ist Markdown, Formeln sind LaTeX-Mathe."""

    def test_text_wird_maskiert(self):
        from opencivil.bericht.markdown import absatz_markdown, text_markdown

        self.assertEqual(text_markdown("N_Ed = 5 * 3 $ | ü"),
                         r"N\_Ed = 5 \* 3 \$ \| ü")
        # Nur am Anfang eines Absatzes wird aus «2.» eine Liste.
        self.assertEqual(text_markdown("2. Lage"), "2. Lage")
        self.assertEqual(absatz_markdown("2. Lage"), r"2\. Lage")
        self.assertEqual(absatz_markdown("- minus"), r"\- minus")

    def test_ein_betrag_in_der_tabelle_teilt_die_zelle_nicht(self):
        from opencivil.bericht.markdown import protokoll_zeilen

        p = Protokoll()
        p.tabelle([Mathe("N"), "Art"], [[Mathe(r"\left|N_{Ed}\right|"), "Druck"]],
                  ausrichtung="rl")
        kopf, trenner, zeile = [z for z in protokoll_zeilen(p) if z]
        self.assertEqual(trenner, "| ---: | :--- |")
        self.assertEqual(zeile, r"| $\left\vert N_{Ed}\right\vert $ | Druck |")

    def test_jede_formel_steht_als_formelblock_da(self):
        from opencivil.bericht.markdown import als_markdown

        loesung, _ = beispiel_loesung()
        text = als_markdown(loesung, titel="Probe")
        self.assertTrue(text.startswith("# Probe\n"))
        for gleichung in loesung.protokoll.gleichungen():
            self.assertIn(f"$$\n{gleichung.latex}\n$$", text)


class TestKopierknoepfe(unittest.TestCase):
    """
    Der MD-Knopf an einem Block liefert, was im Markdown-Bericht steht --
    aus derselben Tafel, nicht aus einer zweiten Regel in der Oberfläche.
    """

    @classmethod
    def setUpClass(cls):
        from opencivil.bericht.markdown import als_markdown
        from opencivil.projekt import Projekt
        from opencivil.web import api

        cls.aufbau = Projekt.beispiel().aufbauen()
        cls.loesung = cls.aufbau.werk.loese(*cls.aufbau.alle_nachweisziele())
        cls.bloecke = api.protokoll_liste(cls.loesung.protokoll)
        cls.zusammenfassung = api.zusammenfassungen(cls.loesung, cls.aufbau)["q1"]
        cls.dokument = als_markdown(cls.loesung, aufbau=cls.aufbau)

    def test_jede_formel_und_tabelle_der_herleitung(self):
        mit = [b for b in self.bloecke if b["art"] in ("gleichung", "tabelle")]
        self.assertTrue(any(b["art"] == "tabelle" for b in mit))
        for block in mit:
            self.assertIn(block["markdown"], self.dokument)

    def test_die_zusammenfassung_auch(self):
        for teil in (self.zusammenfassung, self.zusammenfassung["angaben"],
                     self.zusammenfassung["bewehrung"]):
            self.assertIn(teil["markdown"], self.dokument)


class TestBerichtWieBildschirm(unittest.TestCase):
    """
    Der Bericht zeigt je Platte, was der Bildschirm zeigt -- aus denselben
    Stücken. Vorher fasste er die Nachweise flach zusammen, ohne Platten, und
    zwei Kombinationen «Feld» zweier Platten sahen gleich aus.
    """

    @classmethod
    def setUpClass(cls):
        from opencivil.projekt import Projekt
        from opencivil.web import api

        projekt = Projekt.beispiel()
        dach = projekt.platte("Dach", h=200, x=[10, 10])
        dach.einwirkung("Feld", M_Ed=300)
        ohne = projekt.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
        ohne.einwirkung("Feld", M_Ed=30, V_Ed=20)
        cls.aufbau = projekt.aufbauen()
        cls.loesung = cls.aufbau.werk.loese(*cls.aufbau.alle_nachweisziele())
        cls.web = api.zusammenfassungen(cls.loesung, cls.aufbau)
        # Die Konsole bricht lange Saetze um; verglichen wird der Wortlaut.
        cls.text = " ".join(als_text(cls.loesung, aufbau=cls.aufbau).split())

    def test_jede_platte_hat_ihren_abschnitt(self):
        self.assertEqual(len(self.web), 3)
        for kennung in self.web:
            name = self.aufbau.querschnitte[kennung].name
            self.assertIn(f"{name} {'-' * len(name)} Angaben zur Platte", self.text)

    def test_die_zellen_der_tabelle_stehen_im_bericht(self):
        for tabelle in self.web.values():
            for zeile in tabelle["zeilen"]:
                for zelle in zeile["zellen"]:
                    self.assertIn(zelle.get("mathe", zelle.get("text")), self.text)

    def test_hinweise_und_stille_saetze_stehen_wortgleich_da(self):
        saetze = [satz for tabelle in self.web.values()
                  for satz in tabelle["hinweise"] + [s["text"] for s in tabelle["stille"]]]
        self.assertTrue(any(t["hinweise"] for t in self.web.values()),
                        "die Probe braucht einen Hinweis")
        self.assertTrue(any(t["stille"] for t in self.web.values()),
                        "und einen stillen Mangel")
        for satz in saetze:
            self.assertIn(satz, self.text)

    def test_was_nicht_aufgeht_steht_mit_begruendung_darunter(self):
        """Auf Papier gibt es weder rote Zeilen noch Tooltips."""
        self.assertIn("[!] Warnung: Biegung und Normalkraft – Feld: nicht erfüllt. "
                      "Bei festgehaltenem N_Ed = 0 kN", self.text)
        # Die Platte ohne Bewehrung erklaert schon der gebuendelte Hinweis.
        self.assertNotIn("Querkraft – Feld: nicht erfüllt.", self.text)


class TestTafeln(unittest.TestCase):
    """
    Jede Darstellung setzt die Blöcke über eine Tafel {Blockart: Funktion}.

    Vorher unterschied jede die Blockarten mit einer eigenen if/elif-Kette,
    und die der Oberfläche liess eine unbekannte Art still weg.
    """

    def tafeln(self):
        from opencivil.bericht import konsole, latex_dokument, markdown
        from opencivil.web import api

        return {"Konsole": konsole.TAFEL, "LaTeX": latex_dokument.TAFEL,
                "Markdown": markdown.TAFEL, "Oberfläche": api.TAFEL}

    def test_jede_tafel_kennt_jede_blockart(self):
        def unterklassen(art):
            for unter in art.__subclasses__():
                yield unter
                yield from unterklassen(unter)

        arten = set(unterklassen(Block))
        self.assertIn(UnterprotokollBlock, arten)
        for name, tafel in self.tafeln().items():
            with self.subTest(darstellung=name):
                self.assertEqual(set(tafel), arten)

    def test_eine_unbekannte_blockart_wirft(self):
        p = Protokoll()
        p.titel("Titel")
        p.text("Text")
        with self.assertRaisesRegex(TypeError, "TextBlock"):
            darstellen(p, {TitelBlock: lambda block, tiefe: block.text})

    def test_die_tiefe_zaehlt_die_unterprotokolle(self):
        p = Protokoll()
        p.text("aussen")
        p.unterprotokoll("Durchlauf").text("innen")
        tafel = {
            TextBlock: lambda block, tiefe: (block.text, tiefe),
            UnterprotokollBlock:
                lambda block, tiefe: darstellen(block.protokoll, tafel, tiefe + 1),
        }
        self.assertEqual(darstellen(p, tafel), [("aussen", 0), [("innen", 1)]])


if __name__ == "__main__":
    unittest.main()
