"""
Das Zeichenfenster mit jeder Zahl von Achsen (``web/js/cad_modell.js``,
``web/js/cad_ansicht.js``): ein Knoten hat so viele Koordinaten, wie die App
Achsen nennt, und Verschieben, Kopieren und Zusammenfuehren rechnen mit
allen. Zwei Strecken im Raum kreuzen sich nur, wo sie sich wirklich treffen.
Die Ansicht bildet die Zeichnung ins Bild ab -- in der Ebene wie bisher, im
Raum ueber zwei Richtungen --, und ein Punkt im Bild zeigt auf die
Arbeitsebene. Im Raum (``web/js/cad_raum.js``) liegen die vier Ansichten,
wie ihre Knoepfe sagen, Drehen haelt den Punkt, um den es dreht, im Bild,
und die Arbeitsebene merkt sich je Richtung ihre Lage.

Die Module werden mit ihren Nachbarn in ein leeres Verzeichnis kopiert, das
node als Module liest. Ohne node wird uebersprungen.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

PROGRAMM = r"""
const m = await import('./cad_modell.js');
const v = await import('./cad_ansicht.js');
const r = (p) => p.map((x) => Math.round(x * 1e6) / 1e6);
const erg = {};

// Ein Modell mit drei Achsen: Knoten, Verschieben, Kopieren, Zusammenführen.
const arten = [{ liste: 'staebe', vorsilbe: 'S', form: 'linie' }];
const modell = m.cadModell({ arten, achsen: ['x', 'y', 'z'], verbunden: true });
const z = { knoten: [], staebe: [] };
const k1 = modell.knotenAn(z, [0, 0, 0]);
const k2 = modell.knotenAn(z, [0, 0, 4]);
const k3 = modell.knotenAn(z, [0, 0, 4]);
z.staebe.push({ kennung: 'S1', von: k1, bis: k2 });
erg.knoten = [z.knoten.map((k) => [k.x, k.y, k.z]), k2 === k3];
modell.verschieben(z, new Set(['S1']), [1, 2, 3]);
erg.verschoben = z.knoten.map((k) => modell.lage(k));
const kopien = modell.kopieren(z, new Set(['S1']), [0, 5, 0], 2);
erg.kopiert = [kopien.length, z.staebe.map((s) => [modell.lage(z.knoten.find((k) => k.kennung === s.von)),
  modell.lage(z.knoten.find((k) => k.kennung === s.bis))])];
const zwei = { knoten: [{ kennung: 'K1', x: 1, y: 2, z: 3 }, { kennung: 'K2', x: 1, y: 2, z: 3 }], staebe: [] };
modell.zusammenfuehren(zwei);
erg.zusammen = zwei.knoten.length;

// Strecken im Raum: kreuzend, windschief, parallel -- und in der Ebene wie bisher.
erg.kreuzung = [
  m.kreuzung([[0, 0, 0], [2, 2, 2]], [[2, 0, 0], [0, 2, 2]]),
  m.kreuzung([[0, 0, 0], [2, 0, 0]], [[1, -1, 1], [1, 1, 1]]),
  m.kreuzung([[0, 0, 0], [2, 0, 0]], [[0, 1, 0], [2, 1, 0]]),
  m.kreuzung([[0, 0], [2, 2]], [[2, 0], [0, 2]]),
  m.kreuzung([[0, 0], [1, 1]], [[2, 0], [3, 1]]),
];
erg.strecke = [m.aufStrecke([1, 5, 0], [0, 0, 0], [0, 4, 0]), m.mitte([0, 0, 0], [2, 4, 6])];

// Die Ansicht: in der Ebene wie bisher.
const eben = v.ansichtNeu();
Object.assign(eben, { massstab: 20, ursprung: [100, 300], breite: 400, hoehe: 400 });
erg.eben = [v.nachBild(eben, [2, 3]), r(v.nachWelt(eben, v.nachBild(eben, [2, 3])))];

// Im Raum, von oben auf den Grundriss in z = 3: x nach rechts, y nach oben.
const oben = v.ansichtNeu();
Object.assign(oben, { massstab: 20, ursprung: [100, 300], breite: 400, hoehe: 400,
  basis: [[1, 0, 0], [0, 1, 0]], ebene: { achse: 2, lage: 3 } });
erg.oben = [v.nachBild(oben, [2, 3, 7]), r(v.nachWelt(oben, [140, 240])), r(v.blickrichtung(oben))];

// Schräg: ein Punkt der Arbeitsebene, ins Bild und zurück, liegt wieder dort.
const c = Math.cos(Math.PI / 6);
const schraeg = v.ansichtNeu();
Object.assign(schraeg, { massstab: 30, ursprung: [200, 200], breite: 400, hoehe: 400,
  basis: [[Math.SQRT1_2, Math.SQRT1_2, 0], [-0.5 * Math.SQRT1_2, 0.5 * Math.SQRT1_2, c]],
  ebene: { achse: 2, lage: 2 } });
erg.schraeg = [r(v.nachWelt(schraeg, v.nachBild(schraeg, [1.5, -2, 2]))),
  r(v.richtungImBild(schraeg, [0, 0, 1]))];
// Von der Seite gesehen trifft der Blick die Ebene nicht: der Punkt senkrecht auf sie.
const seitlich = { ...schraeg, basis: [[1, 0, 0], [0, 0, 1]], ebene: { achse: 1, lage: 0 } };
seitlich.ebene = { achse: 2, lage: 5 };
erg.seitlich = r(v.nachWelt(seitlich, v.nachBild(seitlich, [2, 0, 1])));

// Alles zeigen im Raum: jede Ecke des Umrisses liegt danach im Bild.
v.einpassen(schraeg, [[0, 0, 0], [10, 6, 4]], { rand: 20 });
const ecken = [];
for (const x of [0, 10]) for (const y of [0, 6]) for (const zz of [0, 4]) ecken.push(v.nachBild(schraeg, [x, y, zz]));
erg.eingepasst = ecken.every(([x, h]) => x >= 19.99 && x <= 380.01 && h >= 19.99 && h <= 380.01);
erg.raster = [v.rasterschritt(1, 30), v.rasterschritt(1, 3), v.rasterschritt(0.5, 2)];

// Die Ansicht im Raum: die vier Ansichten, Drehen um einen Punkt, die Arbeitsebene.
const raum = await import('./cad_raum.js');
erg.basen = Object.fromEntries(raum.ANSICHTEN.map((x) => [x.name, raum.basisAus(x).map(r)]));
const a = { v: v.ansichtNeu(), adapter: { umriss: () => [[0, 0, 0], [6, 4, 2]] } };
raum.raumEinrichten(a);
Object.assign(a.v, { massstab: 20, ursprung: [200, 200], breite: 400, hoehe: 400 });
const um = raum.drehpunkt(a);
const vorher = v.nachBild(a.v, um);
raum.drehen(a, 25, -10, um);
erg.drehen = [um, r(vorher), r(v.nachBild(a.v, um)), { ...a.raum.drehung }];
raum.drehen(a, 0, 1000, um);
erg.scheitel = a.raum.drehung.hoehe;
erg.ebenen = [];
for (const [achse, lage] of [[1, 4], [2], [1]]) {
  raum.ebeneSetzen(a, achse, lage);
  erg.ebenen.push({ ...a.v.ebene });
}
raum.ebeneDurch(a, [1, 2, 3]);
erg.ebenen.push({ ...a.v.ebene });
process.stdout.write(JSON.stringify(erg));
"""


@unittest.skipUnless(NODE, "ohne node")
class TestZeichenfensterMitAchsen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as ort:
            ort = Path(ort)
            for datei in (WURZEL / "web" / "js").glob("*.js"):
                shutil.copy(datei, ort / datei.name)
            (ort / "package.json").write_text('{"type": "module"}')
            (ort / "probe.js").write_text(PROGRAMM)
            lauf = subprocess.run([NODE, str(ort / "probe.js")], capture_output=True, text=True,
                                  timeout=60, cwd=ort)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.erg = json.loads(lauf.stdout)

    def test_knoten_mit_drei_koordinaten(self):
        lagen, gleich = self.erg["knoten"]
        self.assertEqual(lagen, [[0, 0, 0], [0, 0, 4]])
        self.assertTrue(gleich, "genau gleiche Koordinaten sind ein Knoten")

    def test_verschieben_in_allen_achsen(self):
        self.assertEqual(self.erg["verschoben"], [[1, 2, 3], [1, 2, 7]])

    def test_kopieren_in_allen_achsen(self):
        anzahl, staebe = self.erg["kopiert"]
        self.assertEqual(anzahl, 2)
        self.assertEqual(staebe, [[[1, 2, 3], [1, 2, 7]], [[1, 7, 3], [1, 7, 7]],
                                  [[1, 12, 3], [1, 12, 7]]])

    def test_zusammenfuehren_vergleicht_alle_achsen(self):
        self.assertEqual(self.erg["zusammen"], 1)

    def test_kreuzung_im_raum_und_in_der_ebene(self):
        kreuzend, windschief, parallel, eben, daneben = self.erg["kreuzung"]
        self.assertEqual(kreuzend, [1, 1, 1])
        self.assertIsNone(windschief, "im Raum gehen zwei Strecken meist aneinander vorbei")
        self.assertIsNone(parallel)
        self.assertEqual(eben, [1, 1])
        self.assertIsNone(daneben)

    def test_strecke_und_mitte(self):
        naechster, mitte = self.erg["strecke"]
        self.assertEqual(naechster, {"q": [0, 4, 0], "t": 1})
        self.assertEqual(mitte, [1, 2, 3])

    def test_in_der_ebene_wie_bisher(self):
        bild, zurueck = self.erg["eben"]
        self.assertEqual(bild, [140, 240])
        self.assertEqual(zurueck, [2, 3])

    def test_von_oben_auf_den_grundriss(self):
        bild, welt, blick = self.erg["oben"]
        self.assertEqual(bild, [140, 240], "die Höhe z zeigt sich von oben nicht")
        self.assertEqual(welt, [2, 3, 3], "ein Klick zeigt auf die Arbeitsebene z = 3")
        self.assertEqual(blick, [0, 0, 1])

    def test_schraeg_auf_die_arbeitsebene(self):
        zurueck, z_im_bild = self.erg["schraeg"]
        self.assertEqual(zurueck, [1.5, -2, 2])
        self.assertAlmostEqual(z_im_bild[0], 0)
        self.assertLess(z_im_bild[1], 0, "z zeigt im Bild nach oben")

    def test_ebene_von_der_seite(self):
        self.assertEqual(self.erg["seitlich"], [2, 0, 5])

    def test_alles_zeigen_im_raum(self):
        self.assertTrue(self.erg["eingepasst"])

    def test_rasterschritt(self):
        self.assertEqual(self.erg["raster"], [1, 5, 10])

    def test_die_vier_ansichten(self):
        basen = self.erg["basen"]
        self.assertEqual(basen["oben"], [[1, 0, 0], [0, 1, 0]], "Grundriss: x nach rechts, y nach oben")
        self.assertEqual(basen["vorne"], [[1, 0, 0], [0, 0, 1]], "Ansicht x-z: z nach oben")
        self.assertEqual(basen["seite"], [[0, 1, 0], [0, 0, 1]], "Ansicht y-z: y nach rechts")
        (rechts, oben) = basen["3d"]
        self.assertGreater(rechts[0], 0, "schräg von oben liegt x rechts unten")
        self.assertLess(oben[0], 0)
        self.assertGreater(rechts[1], 0, "und y rechts oben")
        self.assertGreater(oben[1], 0)
        self.assertEqual(rechts[2], 0, "rechts liegt immer waagrecht")
        self.assertGreater(oben[2], 0, "z zeigt nach oben")

    def test_drehen_haelt_den_punkt(self):
        um, vorher, nachher, drehung = self.erg["drehen"]
        self.assertEqual(um, [3, 2, 1], "gedreht wird um die Mitte der Zeichnung")
        self.assertEqual(nachher, vorher)
        self.assertEqual(drehung, {"azimut": -60, "hoehe": 26})

    def test_hoehe_haelt_am_scheitel(self):
        self.assertEqual(self.erg["scheitel"], 90)

    def test_arbeitsebene_merkt_ihre_lage(self):
        self.assertEqual(self.erg["ebenen"], [
            {"achse": 1, "lage": 4}, {"achse": 2, "lage": 0}, {"achse": 1, "lage": 4},
            {"achse": 1, "lage": 2}])


if __name__ == "__main__":
    unittest.main()
