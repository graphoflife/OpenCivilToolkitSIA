"""
Die Bewehrung suchen lassen.

Geprüft wird nicht, welcher Durchmesser herauskommt -- das hinge an den
Normsorten des Beispiels und wäre bei der ersten Änderung dort falsch.
Geprüft wird, was die Suche *zusagt*: dass das Ergebnis alle eingeschalteten
Nachweise erfüllt, dass es das kleinste ist, das sie erfüllt, und dass sie
ehrlich Nein sagt, wo es keines gibt.
"""

import copy
import unittest
from unittest import mock

from opencivil import bewehrungssuche as suche
from opencivil.projekt import KnickEintrag, Projekt
from opencivil.web import dienst


def platte(**abweichungen) -> Projekt:
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


def schlechtester(projekt) -> float:
    return suche.bewerte(projekt).grad


#: Die Stufen, die die Suche voreingestellt zur Verfügung hat -- die Null
#: vorneweg, darüber nichts unter dem Mindestdurchmesser.
STUFEN = suche.stufen(suche.DURCHMESSER, suche.MINDESTDURCHMESSER)


def ohne_duktilitaet(projekt) -> suche.Bewertung:
    """
    Bewerten wie die Suche selbst: ohne Duktilität.

    Sie sucht ohne den Nachweis, also muss auch geprüft werden, ohne ihn --
    sonst misst der Test etwas anderes als das, was das Werkzeug zusagt.
    """
    kopie = copy.deepcopy(projekt)
    q = kopie.querschnitt("q1")
    q.duktilitaet = False
    return suche.bewerte(kopie)


def _urteile(projekt):
    aufbau = projekt.aufbauen()
    return aufbau.werk.loese(*aufbau.alle_nachweisziele()).urteile


class TestSuche(unittest.TestCase):
    def test_das_ergebnis_erfuellt_alle_nachweise(self):
        """Die eine Zusage, die das Werkzeug macht."""
        projekt = platte()
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        self.assertTrue(ohne_duktilitaet(projekt).erfuellt())

    def test_ein_durchmesser_kleiner_reicht_nicht(self):
        """
        Die zweite Zusage: es ist das *kleinste* Ergebnis. Nimmt man irgendwo
        einen Durchmesser zurück, geht mindestens ein Nachweis nicht mehr auf.
        """
        projekt = platte()
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ergebnis.gefunden)

        for marke, d in ergebnis.beste.durchmesser.items():
            # Eine Stufe kleiner -- in den Stufen der Suche und nicht in der
            # rohen Durchmesserliste. Sonst prüfte man einen Zwischenwert,
            # den die Suche gar nicht anbietet.
            kleiner = [x for x in STUFEN if x < d]
            if not kleiner:
                continue
            probe = platte()
            suche.uebernehmen(probe, "q1", ergebnis.beste)
            lage, art = int(marke[:-1]), ("grund" if marke[-1] == "g" else "zulage")
            getattr(probe.querschnitt("q1").lagen[lage - 1], art).durchmesser = kleiner[-1]
            with self.subTest(posten=marke):
                self.assertFalse(ohne_duktilitaet(probe).erfuellt())

    def test_ohne_kraefte_bleibt_weniger_stahl(self):
        """
        Ohne Einwirkungen fallen M-N und Querkraft weg; übrig bleiben die
        Nachweise, die eine Platte unabhängig von der Belastung erfüllen muss.
        Weniger Anforderungen heisst nie mehr Stahl.
        """
        projekt = platte()
        ohne = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE)
        mit = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ohne.gefunden and mit.gefunden)
        self.assertLessEqual(ohne.beste.stahlflaeche, mit.beste.stahlflaeche)

    def test_das_projekt_bleibt_unberuehrt(self):
        """Gesucht wird auf einer Kopie -- sonst wäre ein Versuch eine Änderung."""
        projekt = platte()
        vorher = projekt.als_dict()
        suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertEqual(projekt.als_dict(), vorher)

    def test_grund_und_zulage_teilen_die_teilung(self):
        projekt = platte()
        ergebnis = suche.suche(
            projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE_ZULAGE_MIT)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        for lage in projekt.querschnitt("q1").lagen:
            if lage.grund.durchmesser and lage.zulage.durchmesser:
                self.assertEqual(lage.grund.abstand, lage.zulage.abstand)

    def test_nur_die_angegebenen_teilungen_kommen_heraus(self):
        ergebnis = suche.suche(platte(), "q1", teilungen=[125.0],
                               modus=suche.Suchmodus.GRUND_OHNE)
        self.assertTrue(ergebnis.gefunden)
        self.assertEqual(ergebnis.beste.teilung, 125.0)

    def test_eine_unloesbare_platte_sagt_warum(self):
        """
        Eine zu dünne Platte bekommt kein Ergebnis -- und das Werkzeug erfindet
        auch keins. Der Grund steht dabei, sonst steht dort nur ein Nein.
        """
        projekt = platte(h=80.0)
        for k in projekt.querschnitt("q1").kombinationen:
            k.M_Ed = 400.0
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertFalse(ergebnis.gefunden)
        self.assertTrue(ergebnis.begruendung)
        self.assertTrue(any(l.begruendung for l in ergebnis.loesungen))

    def test_die_y_lagen_fasst_die_suche_nicht_an(self):
        """
        Gesucht werden die x-Lagen. In y wird nichts nachgewiesen, also gäbe
        es dort auch kein Mass, an dem sich ein Durchmesser bemessen liesse --
        die Suche zöge ihn auf null, und genau das wäre falsch: die
        y-Bewehrung liegt aussen und kostet x seine statische Höhe.
        """
        projekt = platte()
        vorher = [l.grund.durchmesser for l in projekt.querschnitt("q1").lagen]
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        # Grund und Zulage der beiden x-Lagen -- und sonst nichts.
        self.assertEqual(sorted(ergebnis.beste.durchmesser),
                         ["2g", "2z", "3g", "3z"])

        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        nachher = [l.grund.durchmesser for l in projekt.querschnitt("q1").lagen]
        self.assertEqual(nachher[0], vorher[0])   # 1. Lage y
        self.assertEqual(nachher[3], vorher[3])   # 4. Lage y

    def test_eine_leere_lage_wird_bewehrt_wo_es_noetig_ist(self):
        """
        Umgekehrt: wo ein Nachweis sie braucht, legt die Suche Bewehrung an.
        Früher blieb eine leere Lage leer -- das war zu vorsichtig, denn wer
        die Bewehrung ermitteln lässt, will wissen, *wo* welche hingehört.
        """
        projekt = platte()
        for nummer in (1, 2, 3, 4):
            lage = projekt.querschnitt("q1").lagen[nummer - 1]
            lage.grund.durchmesser = lage.zulage.durchmesser = 0
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        self.assertTrue(any(d > 0 for d in ergebnis.beste.durchmesser.values()))
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        self.assertTrue(suche.bewerte(projekt).erfuellt())

    def test_kein_aktiver_stab_unter_dem_mindestdurchmesser(self):
        ergebnis = suche.suche(platte(), "q1", modus=suche.Suchmodus.GRUND_MIT,
                               mindestdurchmesser=16.0)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        for marke, d in ergebnis.beste.durchmesser.items():
            with self.subTest(posten=marke):
                self.assertTrue(d == 0.0 or d >= 16.0)

    def test_die_suche_faengt_bei_null_an(self):
        """
        Auch wenn schon etwas eingetragen ist. Das Werkzeug *ermittelt* die
        Bewehrung; es legt nicht zu dem dazu, was zufällig dasteht.
        """
        kopie = suche._arbeitskopie(platte(), "q1", kraefte=True)
        q = kopie.querschnitt("q1")
        for nummer, lage in enumerate(q.lagen, start=1):
            if q.richtung_von(nummer).value != "x":
                continue        # y bleibt stehen -- die sucht niemand
            self.assertEqual(lage.grund.durchmesser, 0)
            self.assertEqual(lage.zulage.durchmesser, 0)


class TestDieEbeneAufDerDieSucheStehenblieb(unittest.TestCase):
    """
    Der Fehler, an dem das Werkzeug zuerst scheiterte.

    Gemessen wurde der Fortschritt am *schlechtesten* Erfüllungsgrad. Halten
    zwei Nachweise ihn gleichzeitig -- sprödes Versagen in der 1. und in der
    4. Lage bei gleicher Bewehrung --, dann hebt kein einzelner Schritt ihn,
    weil der jeweils andere stehen bleibt. Die Suche sah eine Ebene und gab
    auf, obwohl der nächste Durchmesser offensichtlich geholfen hätte.

    Gemessen wird jetzt die Summe der Fehlbeträge. Die kennt keine Ebene: sie
    fällt, sobald irgendein unerfüllter Nachweis besser wird.
    """

    def gleichstand(self, durchmesser: float = 12.0) -> Projekt:
        """
        Zwei Lagen in x, gleich bewehrt, beide im Nachweis.

        Beide tragen dasselbe, also haben beide denselben Erfüllungsgrad --
        und genau das ist die Ebene. Die Zulagen sind leer, damit die Gleichheit
        nicht zufällig von einer Seite gebrochen wird.
        """
        projekt = platte(sproede = True)
        q = projekt.querschnitt("q1")
        q.richtung_lage1 = q.richtung_lage4 = "x"
        q.kombinationen = []
        for nummer in (1, 2, 3, 4):
            lage = q.lagen[nummer - 1]
            lage.zulage.durchmesser = 0
            lage.grund.durchmesser = durchmesser if nummer in (1, 4) else 0
        return projekt

    def test_zwei_gleich_schlechte_nachweise_halten_die_suche_nicht_auf(self):
        projekt = self.gleichstand()
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE,
                               teilungen=[150.0], mindestdurchmesser=8.0)
        self.assertTrue(ergebnis.gefunden, ergebnis.loesungen[0].begruendung)
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        self.assertTrue(ohne_duktilitaet(projekt).erfuellt())

    def test_der_rueckstand_faellt_auch_wenn_der_schlechteste_steht(self):
        """Die Eigenschaft, auf der das Verfahren beruht -- also geprüft."""
        projekt = suche._arbeitskopie(self.gleichstand(8.0), "q1", kraefte=False)
        q = projekt.querschnitt("q1")
        # Die Arbeitskopie fängt bei null an -- für diesen Test brauchen wir
        # aber genau den Gleichstand, also wird er eigens gesetzt.
        for nummer in (1, 4):
            q.lagen[nummer - 1].grund.durchmesser = 8
            q.lagen[nummer - 1].grund.abstand = 150
        vorher = suche.bewerte(projekt)
        self.assertFalse(vorher.erfuellt())   # sonst prüft der Rest nichts

        q.lagen[0].grund.durchmesser = 10      # nur *eine* der beiden Lagen
        nachher = suche.bewerte(projekt)
        self.assertAlmostEqual(nachher.grad, vorher.grad, places=9)   # die Ebene
        self.assertLess(nachher.rueckstand, vorher.rueckstand)        # der Ausweg


class TestDuktilitaetBleibtDraussen(unittest.TestCase):
    """
    Sie ist der einzige Nachweis, der durch mehr Bewehrung schlechter wird.
    Eine Suche, die von unten aufsteigt, hat gegen ihn kein Mittel -- also
    sucht sie ohne ihn und sagt hinterher, wie er dasteht.
    """

    #: Ausdrücklich beide Teilungen. Der Fall braucht die engere, und woran
    #: er scheitert, soll nicht an der Vorgabe hängen -- geprüft wird hier die
    #: Duktilität und nicht, welche Teilung voreingestellt ist.
    TEILUNGEN = [100.0, 150.0]

    def duenn(self) -> Projekt:
        """
        So belastet, dass die nötige Bewehrung die Druckzone zu tief macht.

        Es geht auf -- nur eben nicht duktil, und genau darauf zielt dieser
        Abschnitt: die Suche findet etwas, und der Befund sagt hinterher, dass
        die Duktilität damit nicht hinkommt.
        """
        projekt = platte(h=220.0)
        for k in projekt.querschnitt("q1").kombinationen:
            k.M_Ed, k.richtung = 150.0, "x"
        return projekt

    def test_die_suche_findet_auch_wenn_die_duktilitaet_nicht_aufgeht(self):
        ergebnis = suche.suche(self.duenn(), "q1", teilungen=self.TEILUNGEN,
                               modus=suche.Suchmodus.GRUND_MIT,
                               mindestdurchmesser=8.0)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)

    def test_sie_wird_aber_nicht_verschwiegen(self):
        projekt = self.duenn()
        ergebnis = suche.suche(projekt, "q1", teilungen=self.TEILUNGEN,
                               modus=suche.Suchmodus.GRUND_MIT,
                               mindestdurchmesser=8.0)
        self.assertIn("nicht", ergebnis.duktilitaet)
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        dukt = [u for u in _urteile(projekt) if u.art == "D"]
        self.assertTrue(dukt)
        self.assertFalse(all(u.erfuellt for u in dukt))

    def test_wo_sie_aufgeht_steht_das_auch_da(self):
        ergebnis = suche.suche(platte(), "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertIn("geht damit auf", ergebnis.duktilitaet)

    def test_die_arbeitskopie_zaehlt_keinen_duktilitaetsnachweis(self):
        """
        Gerechnet wird er auch dort -- er ist nie ganz weg. Aber er ist still,
        und die Suche zählt nur, was laut ist: sonst suchte sie gegen einen
        Nachweis, gegen den sie kein Mittel hat.
        """
        kopie = suche._arbeitskopie(platte(), "q1", kraefte=True, leeren=False)
        self.assertFalse(kopie.querschnitt("q1").duktilitaet)
        dukt = [u for u in _urteile(kopie) if u.art == "D"]
        self.assertTrue(dukt)
        self.assertTrue(all(u.still for u in dukt))


class TestEineLageWirdNichtErfunden(unittest.TestCase):
    def test_eine_zwaengung_in_y_wird_jetzt_bewehrt(self):
        """
        Früher ging das nicht auf: die y-Lagen standen auf null, und die Suche
        fasste sie nicht an. Jetzt legt sie dort Bewehrung an -- die Zwängung
        verlangt sie ja.
        """
        projekt = platte(zwaengung=True)
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        self.assertGreater(ergebnis.beste.durchmesser["2g"], 0.0)


class TestYWieX(unittest.TestCase):
    """
    «y-Grundbew. wie x»: die y-Grundbewehrung jeder Seite folgt der
    x-Grundbewehrung dieser Seite -- gleicher Durchmesser, gleiche Teilung.
    """

    @classmethod
    def setUpClass(cls):
        # y vorher leer. Folgte y erst beim Übernehmen, rechnete die Suche mit
        # zu viel statischer Höhe, und das Ergebnis ginge danach nicht auf.
        cls.projekt = platte(automatik_y_wie_x=True)
        for nummer in (1, 4):
            cls.projekt.querschnitt("q1").lagen[nummer - 1].grund.durchmesser = 0.0
        cls.ergebnis = suche.suche(cls.projekt, "q1",
                                   modus=suche.Suchmodus.GRUND_OHNE_ZULAGE_MIT)
        cls.danach = copy.deepcopy(cls.projekt)
        suche.uebernehmen(cls.danach, "q1", cls.ergebnis.beste)

    def test_y_folgt_je_seite_der_x_grundbewehrung(self):
        self.assertTrue(self.ergebnis.gefunden, self.ergebnis.begruendung)
        lagen = self.danach.querschnitt("q1").lagen
        # Im Beispiel liegt y aussen: unten die 1. unter der 2., oben die 4.
        # über der 3. Lage.
        self.assertTrue(any(lagen[x - 1].grund.durchmesser for x in (2, 3)))
        for y, x in ((1, 2), (4, 3)):
            with self.subTest(y=y):
                self.assertEqual(lagen[y - 1].grund.durchmesser,
                                 lagen[x - 1].grund.durchmesser)
                self.assertEqual(lagen[y - 1].grund.abstand,
                                 lagen[x - 1].grund.abstand)

    def test_jede_rechnung_der_suche_sieht_y_wie_x(self):
        """
        Nicht erst das Übernehmen: liegt y aussen, kostet ihr Durchmesser x
        die statische Höhe, und gesucht werden soll mit der Bewehrung, die
        hinterher dasteht.
        """
        gesehen = []
        bewerte = suche.bewerte

        def mitschreiben(projekt):
            lagen = projekt.querschnitt("q1").lagen
            gesehen.extend((lagen[y - 1].grund.durchmesser,
                            lagen[x - 1].grund.durchmesser)
                           for y, x in ((1, 2), (4, 3)))
            return bewerte(projekt)

        with mock.patch.object(suche, "bewerte", mitschreiben):
            suche.suche(self.projekt, "q1",
                        modus=suche.Suchmodus.GRUND_OHNE_ZULAGE_MIT)
        self.assertTrue(gesehen)
        self.assertTrue(all(y == x for y, x in gesehen))
        self.assertTrue(ohne_duktilitaet(self.danach).erfuellt())


class TestDieVorgabe(unittest.TestCase):
    def test_voreingestellt_wird_eine_teilung_versucht(self):
        """
        150 mm, die eine übliche. Jede weitere kostet einen vollständigen
        Suchlauf, und meistens steht die Teilung ohnehin fest.
        """
        self.assertEqual(list(suche.TEILUNGEN), [150.0])
        ergebnis = suche.suche(platte(), "q1", modus=suche.Suchmodus.GRUND_OHNE)
        self.assertEqual([l.teilung for l in ergebnis.loesungen], [150.0])


class TestNurDieEigenePlatte(unittest.TestCase):
    """
    Der Fehler, den man in der Oberfläche sah und in den Tests nie:

    Bewertet wurde das *ganze Projekt*. Stand daneben eine Platte, die aus
    eigenen Gründen nicht aufging, trug ihr Rückstand mit -- und die gesuchte
    Platte bekam die Schuld. In den Tests gab es immer nur eine Platte.

    Darum prüft diese Klasse jeden Modus zweimal: allein und mit drei
    Nachbarn, von denen jeder auf eine andere Weise scheitert.
    """

    def mit_nachbarn(self) -> Projekt:
        projekt = platte()

        zu_duenn = copy.deepcopy(projekt.querschnitte[0])
        zu_duenn.kennung, zu_duenn.name, zu_duenn.h = "q2", "zu dünn", 70.0
        for k in zu_duenn.kombinationen:
            k.M_Ed = 500.0

        ohne_y = copy.deepcopy(projekt.querschnitte[0])
        ohne_y.kennung, ohne_y.name = "q3", "ohne y"
        ohne_y.richtung_lage1 = ohne_y.richtung_lage4 = "x"
        for nummer in (2, 3):
            ohne_y.lagen[nummer - 1].grund.durchmesser = 0
        ohne_y.zwaengung = True

        knickt = copy.deepcopy(projekt.querschnitte[0])
        knickt.kennung, knickt.name = "q4", "knickt"
        knickt.knickfaelle = [KnickEintrag("Stütze", N_Ed=-2500.0, M_Ed_1=60.0,
                                           laenge=12.0, knicklaenge=12.0)]

        projekt.querschnitte += [zu_duenn, ohne_y, knickt]
        return projekt

    def test_jeder_modus_findet_dasselbe_wie_allein(self):
        for modus in suche.Suchmodus:
            allein = suche.suche(platte(), "q1", modus=modus)
            daneben = suche.suche(self.mit_nachbarn(), "q1", modus=modus)
            with self.subTest(modus=modus.value):
                self.assertTrue(allein.gefunden, allein.begruendung)
                self.assertTrue(daneben.gefunden, daneben.begruendung)
                self.assertEqual(daneben.beste.durchmesser, allein.beste.durchmesser)
                self.assertEqual(daneben.beste.teilung, allein.beste.teilung)

    def test_auch_die_buegel_sehen_nur_ihre_platte(self):
        allein, daneben = platte(), self.mit_nachbarn()
        for projekt in (allein, daneben):
            for k in projekt.querschnitt("q1").kombinationen:
                k.V_Ed = 600.0
        eine = suche.buegel_suchen(allein, "q1")
        andere = suche.buegel_suchen(daneben, "q1")
        self.assertTrue(andere.gefunden, andere.begruendung)
        self.assertEqual(andere.durchmesser, eine.durchmesser)
        self.assertEqual(andere.teilung, eine.teilung)

    def test_auch_ein_nachbar_laesst_sich_suchen(self):
        """Die kaputte Platte bleibt kaputt, die gesunde daneben nicht."""
        projekt = self.mit_nachbarn()
        self.assertFalse(
            suche.suche(projekt, "q2", modus=suche.Suchmodus.GRUND_MIT).gefunden)
        self.assertTrue(
            suche.suche(projekt, "q4", modus=suche.Suchmodus.GRUND_OHNE).gefunden)

    def test_nur_die_gesuchte_platte_kommt_geaendert_zurueck(self):
        """
        Die Antwort trägt das ganze Projekt. Käme darin eine andere Platte
        verändert zurück, überschriebe ein Klick Eingaben, die niemand
        angefasst hat.
        """
        vorher = self.mit_nachbarn().als_dict()
        for modus in suche.Suchmodus:
            antwort = dienst.bearbeite("bewehrung_suchen", {
                "projekt": vorher, "kennung": "q1", "modus": modus.value})
            nachher = antwort.daten["projekt"]
            geaendert = [neu["kennung"] for alt, neu
                         in zip(vorher["querschnitte"], nachher["querschnitte"])
                         if alt != neu]
            with self.subTest(modus=modus.value):
                self.assertEqual(geaendert, ["q1"])
                self.assertEqual(nachher["materialien"], vorher["materialien"])


class TestNurEingeschaltetes(unittest.TestCase):
    """Gesucht wird gegen das, was eingeschaltet ist -- nicht gegen mehr."""

    def test_ein_ausgeschalteter_nachweis_zaehlt_nicht(self):
        streng = platte()
        for k in streng.querschnitt("q1").kombinationen:
            k.M_Ed = 260.0
        mit = suche.suche(streng, "q1", modus=suche.Suchmodus.GRUND_MIT)

        locker = platte()
        for k in locker.querschnitt("q1").kombinationen:
            k.M_Ed, k.aktiv = 260.0, False
        ohne = suche.suche(locker, "q1", modus=suche.Suchmodus.GRUND_MIT)

        self.assertTrue(mit.gefunden and ohne.gefunden)
        self.assertLess(ohne.beste.stahlflaeche, mit.beste.stahlflaeche)


class TestBuegel(unittest.TestCase):
    def test_ohne_bedarf_keine_buegel(self):
        loesung = suche.buegel_suchen(platte(), "q1")
        self.assertTrue(loesung.gefunden)
        self.assertEqual(loesung.durchmesser, 0.0)

    def test_bei_grosser_querkraft_kommen_welche(self):
        projekt = platte()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 600.0
        loesung = suche.buegel_suchen(projekt, "q1")
        self.assertTrue(loesung.gefunden, loesung.begruendung)
        self.assertGreater(loesung.durchmesser, 0.0)

    def test_das_raster_ist_quadratisch(self):
        projekt = platte()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 600.0
        loesung = suche.buegel_suchen(projekt, "q1")
        suche.buegel_uebernehmen(projekt, "q1", loesung)
        buegel = projekt.querschnitt("q1").querkraftbewehrung
        self.assertEqual(buegel.abstand_x, buegel.abstand_y)


class TestUeberDenDienst(unittest.TestCase):
    def test_die_antwort_traegt_das_fertige_projekt(self):
        antwort = dienst.bearbeite("bewehrung_suchen", {
            "projekt": platte().als_dict(), "kennung": "q1",
            "modus": "grund_mit"})
        self.assertEqual(antwort.status, 200)
        self.assertTrue(antwort.daten["gefunden"])
        # Das Projekt kommt fertig zurück: die Oberfläche soll die gefundenen
        # Durchmesser nicht selbst einsetzen müssen.
        fertig = Projekt.aus_dict(antwort.daten["projekt"])
        self.assertGreaterEqual(schlechtester(fertig), 1.0)

    def test_eine_unbekannte_platte_ist_ein_404(self):
        antwort = dienst.bearbeite("bewehrung_suchen", {
            "projekt": platte().als_dict(), "kennung": "gibt-es-nicht"})
        self.assertEqual(antwort.status, 404)

    def test_ein_unbekannter_modus_nennt_die_moeglichen(self):
        antwort = dienst.bearbeite("bewehrung_suchen", {
            "projekt": platte().als_dict(), "kennung": "q1", "modus": "raten"})
        self.assertEqual(antwort.status, 400)
        self.assertIn("grund_ohne", antwort.daten["fehler"])


class TestSchnellerKnicknachweis(unittest.TestCase):
    """
    Die Abkürzung darf das Urteil nicht ändern.

    Ohne die Suche nach N_Rd steht eine andere Zahl da -- das Verhältnis der
    Momente statt der Kräfte. Erfüllt oder nicht muss gleich herauskommen,
    sonst suchte das Werkzeug gegen andere Nachweise als der Bericht.
    """

    def faelle(self):
        return [
            ("gedrungen", KnickEintrag("K", N_Ed=-600.0, M_Ed_1=20.0,
                                       laenge=3.0, knicklaenge=3.0)),
            ("mittel", KnickEintrag("K", N_Ed=-1800.0, M_Ed_1=40.0,
                                    laenge=5.0, knicklaenge=5.0)),
            # Instabil, ohne zwölf Meter Stab: die genaue Grenzkraftsuche
            # dauert dann eine Sekunde statt fünf.
            ("überlastet", KnickEintrag("K", N_Ed=-8000.0, M_Ed_1=30.0,
                                        laenge=3.0, knicklaenge=3.0)),
        ]

    def test_erfuellt_kommt_gleich_heraus(self):
        for name, fall in self.faelle():
            projekt = platte(knickfaelle=[fall])
            with self.subTest(fall=name):
                genau = projekt.aufbauen()
                genau.werk.loese(*genau.alle_nachweisziele())
                kurz = projekt.aufbauen(schnell=True)
                kurz.werk.loese(*kurz.alle_nachweisziele())
                self.assertEqual(
                    genau.knicken["q1"].ergebnisse[0].erfuellt,
                    kurz.knicken["q1"].ergebnisse[0].erfuellt)


if __name__ == "__main__":
    unittest.main()
