"""
Ein Punkt mit Flaeche im Zeichenfenster (``web/js/cad_auswahl.js``) -- ein
Stahlprofil an seiner Mitte: den Umriss sagt der Adapter (``punktUmriss``).
Ein Klick trifft es in seinem Stahl, nicht in seinem Loch und nicht daneben;
ein Rahmen nach links waehlt es, wenn er seinen Umriss schneidet, einer nach
rechts, wenn er seine Mitte enthaelt -- wie die Ecke eines Polygons.

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
const w = await import('./cad_auswahl.js');
const PROFIL = { liste: 'profile', vorsilbe: 'R', form: 'punkt', rang: 5 };
const modell = m.cadModell({ arten: [PROFIL], achsen: ['y', 'z'] });
const z = { knoten: [], profile: [] };
z.profile.push({ kennung: 'R1', knoten: modell.knotenAn(z, [0, 0]) });
// Ein Rohr 200 × 200 mit einem Loch 160 × 160, um seine Mitte.
const quadrat = (h) => [[-h, -h], [h, -h], [h, h], [-h, h]];
const a = {
  v: { ...v.ansichtNeu(), massstab: 1, ursprung: [300, 300], breite: 600, hoehe: 600 },
  modell, auswahl: new Set(), einstellung: {},
  adapter: {
    zeichnung: () => z,
    punktUmriss: (_, art, e) => {
      const p = modell.lagen(z).get(e.knoten);
      return [quadrat(100), quadrat(80)].map((t) => t.map(([y, zz]) => [y + p[0], zz + p[1]]));
    },
  },
};
const bild = (p) => v.nachBild(a.v, p);
const rahmen = (von, bis) => { w.rahmenWaehlen(a, bild(von), bild(bis), false); return [...a.auswahl]; };
const erg = {
  imStahl: w.treffer(a, bild([90, 0])),
  imLoch: w.treffer(a, bild([40, 40])),
  daneben: w.treffer(a, bild([150, 0])),
  teile: w.teileVon(a, PROFIL, z.profile[0]).length,
  rechtsUmDieMitte: rahmen([-20, -20], [20, 20]),
  rechtsDaneben: rahmen([110, -20], [150, 20]),
  linksSchneidet: rahmen([95, 20], [60, -20]),
  linksImLoch: rahmen([40, 20], [-40, -20]),
};
process.stdout.write(JSON.stringify(erg));
"""


@unittest.skipUnless(NODE, "ohne node")
class TestPunktMitFlaeche(unittest.TestCase):
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

    def test_ein_klick_trifft_den_stahl(self):
        self.assertEqual((self.erg["imStahl"], self.erg["imLoch"], self.erg["daneben"]), (["R1"], [], []))
        self.assertEqual(self.erg["teile"], 2)

    def test_ein_rahmen(self):
        self.assertEqual(self.erg["rechtsUmDieMitte"], ["R1"])
        self.assertEqual(self.erg["rechtsDaneben"], [])
        self.assertEqual(self.erg["linksSchneidet"], ["R1"])
        self.assertEqual(self.erg["linksImLoch"], [])


if __name__ == "__main__":
    unittest.main()
