"""
opencivil/web/bruecke.py -- Welche Dateien der Browser laden muss.

VERANTWORTUNG:
Fuehrt Buch darueber, aus welchen Quelldateien der Rechenkern besteht, und
schreibt diese Liste nach ``web/kern/dateien.json``. Der Faden in
``web/js/kern_arbeiter.js`` liest sie, holt die Dateien uebers Netz und legt
sie ins Dateisystem von Pyodide -- danach ist ``import opencivil`` im Browser
dasselbe wie auf dem Rechner.

WARUM EINE LISTE UND KEIN ARCHIV:
Ein Archiv waere ein zweites, erzeugtes Abbild des Quellcodes im Repo -- und
damit etwas, das unbemerkt veralten kann. Die Liste ist reiner Text, im Diff
lesbar, und :func:`stimmt_ueberein` prueft im Test, dass sie zu den
tatsaechlich vorhandenen Dateien passt. Veraltet sie, schlaegt der Test an,
nicht erst die veroeffentlichte Seite.

JE DATEI EINE MARKE:
Neben jedem Pfad steht eine Marke, die ersten zwoelf Zeichen von SHA-256 ueber
den Inhalt. Der Browser holt die Datei als ``...py?v=Marke``: eine geaenderte
Datei hat damit eine neue Adresse, und aus dem Zwischenspeicher kommt keine
alte Fassung mehr, waehrend die uebrigen schon neu sind. Ein schlichter
statischer Server ohne Cache-Angabe laesst den Browser nach Gefuehl
zwischenspeichern -- so kam einmal ``blatt.py`` nach einer Aenderung noch alt.
Das Manifest aendert sich darum mit jeder Aenderung am Kern; der Test merkt,
wenn das Neuschreiben vergessen ging.

UND DIE FORMELSAMMLUNG:
Die ganze Formelsammlung (:func:`opencivil.bericht.formelsammlung.vollstaendig`)
haengt an keinem Projekt -- rechnen muss man sie trotzdem: zwei Projekte, die
zusammen jeden Nachweis fuehren. Unter Pyodide dauerte das Sekunden, jedesmal
beim ersten Blick in den Reiter. Darum legt die Bruecke sie fertig ab,
``web/kern/formelsammlung.json``, und die Oberflaeche liest sie nur noch. Ein
Test merkt, wenn sie nicht mehr zum Kern passt.

MARKEN AUCH FUER DIE OBERFLAECHE:
Dasselbe traf die Module der Oberflaeche: nach einer Aenderung kam einmal ein
altes ``nachweise.js`` zum neuen Kern. Darum schreibt die Bruecke in
``web/index.html`` eine Importtafel (``<script type="importmap">``): je Modul
unter ``web/js/`` und je Verzeichnis unter ``web/kern/`` die Adresse mit
Marke, dazu das Stilblatt mit Marke. Die Module selbst bleiben, wie sie sind
-- ``import './dom.js'`` fuehrt ueber die Tafel auf ``./dom.js?v=Marke``.
So haengt alles an der Seite: wer sie neu laedt, bekommt den Rest im selben
Stand. Ohne Marke bleiben nur die Fremdbibliotheken unter ``web/vendor/``;
die aendern sich nur, wenn jemand bewusst eine neue Fassung einlegt.

WARUM ALLE DATEIEN UND NICHT NUR DIE GEBRAUCHTEN:
Man koennte die Liste auf das beschraenken, was :mod:`opencivil.web.dienst`
einbindet. Dann muesste die Regel aber bei jeder neuen Einbindung nachgezogen
werden, und wer das vergisst, merkt es erst im Browser. Ein paar Dutzend
Kilobyte sind der bessere Handel.

AUFRUF::

    python3 -m opencivil.web.bruecke    # schreibt web/kern/ und die Marken in web/index.html
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

from opencivil.bericht.formelsammlung import vollstaendig
from opencivil.web.api import formelsammlung_liste

WURZEL = Path(__file__).resolve().parents[2]
PAKET = WURZEL / "opencivil"
MANIFEST = WURZEL / "web" / "kern" / "dateien.json"
FORMELSAMMLUNG = WURZEL / "web" / "kern" / "formelsammlung.json"
SEITE = WURZEL / "web" / "index.html"
STILBLATT = WURZEL / "web" / "css" / "stil.css"

# Zwischen diesen beiden Kommentaren in der Seite schreibt die Bruecke.
ANFANG = ("<!-- Versionsmarken: geschrieben von «python3 -m opencivil.web.bruecke», "
          "nicht von Hand ändern -->")
ENDE = "<!-- Ende der Versionsmarken -->"


def kerndateien() -> List[str]:
    """
    Alle Quelldateien des Kerns, als Pfade vom Projektverzeichnis aus.

    Sortiert, damit das Manifest bei gleichem Stand Zeichen fuer Zeichen gleich
    herauskommt und im Diff nur echte Aenderungen auftauchen.
    """
    return sorted(
        pfad.relative_to(WURZEL).as_posix()
        for pfad in PAKET.rglob("*.py")
        if "__pycache__" not in pfad.parts
    )


def marke(pfad: Path) -> str:
    """
    Die Versionsmarke einer Datei: die ersten zwoelf Zeichen von SHA-256 ueber
    ihren Inhalt. Windows-Zeilenenden zaehlen nicht -- sonst stimmte das
    Manifest nach einem Auschecken mit CRLF nicht mehr.
    """
    return hashlib.sha256(pfad.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]


def manifest() -> dict:
    return {
        "hinweis": (
            "Erzeugt von opencivil/web/bruecke.py. Nicht von Hand ändern -- "
            "nach jeder Änderung unter opencivil/ 'python3 -m "
            "opencivil.web.bruecke' laufen lassen."
        ),
        "dateien": _mit_marken(),
    }


def _mit_marken() -> Dict[str, str]:
    """Pfad -> Marke, in der Reihenfolge von :func:`kerndateien`."""
    return {name: marke(WURZEL / name) for name in kerndateien()}


def stimmt_ueberein() -> bool:
    """Ob das abgelegte Manifest den vorhandenen Dateien entspricht -- samt Marken."""
    if not MANIFEST.is_file():
        return False
    try:
        abgelegt = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return abgelegt.get("dateien") == _mit_marken()


def schreiben(pfad: Path | None = None) -> Path:
    return _json_schreiben(Path(pfad) if pfad is not None else MANIFEST, manifest())


def formelsammlung() -> dict:
    """Die ganze Formelsammlung, so wie die Oberflaeche sie liest."""
    return {
        "hinweis": (
            "Erzeugt von opencivil/web/bruecke.py aus Projekt.beispiel und "
            "Projekt.jeder_nachweis. Nicht von Hand ändern."
        ),
        "themen": formelsammlung_liste(vollstaendig()),
    }


def formelsammlung_stimmt() -> bool:
    """Ob die abgelegte Formelsammlung der entspricht, die der Kern heute ergibt."""
    if not FORMELSAMMLUNG.is_file():
        return False
    try:
        abgelegt = json.loads(FORMELSAMMLUNG.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    # Durch JSON hin und zurueck, damit beide Seiten dieselben Typen haben.
    return abgelegt.get("themen") == json.loads(json.dumps(formelsammlung()["themen"]))


def formelsammlung_schreiben(pfad: Path | None = None) -> Path:
    return _json_schreiben(Path(pfad) if pfad is not None else FORMELSAMMLUNG,
                           formelsammlung())


def _json_schreiben(ziel: Path, daten: dict) -> Path:
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ziel


def tafeldateien() -> List[Path]:
    """
    Was ueber die Importtafel der Seite geht: jedes Modul der Oberflaeche und
    die beiden Verzeichnisse unter ``web/kern/``.
    """
    return sorted([*(SEITE.parent / "js").glob("*.js"), MANIFEST, FORMELSAMMLUNG])


def versionsmarken() -> str:
    """
    Was in der Seite zwischen :data:`ANFANG` und :data:`ENDE` steht: das
    Stilblatt und die Importtafel, jede Adresse mit der Marke ihrer Datei.
    """
    tafel = {"imports": {_adresse(pfad): _adresse(pfad, mit_marke=True)
                         for pfad in tafeldateien()}}
    zeilen = [
        f'<link rel="stylesheet" href="{_adresse(STILBLATT, mit_marke=True)}">',
        '<script type="importmap">',
        *json.dumps(tafel, indent=2).splitlines(),
        "</script>",
    ]
    return "".join(f"  {zeile}\n" for zeile in zeilen)


def _adresse(pfad: Path, *, mit_marke: bool = False) -> str:
    """Die Adresse einer Datei von der Seite aus, auf Wunsch mit ihrer Marke."""
    adresse = f"./{pfad.relative_to(SEITE.parent).as_posix()}"
    return f"{adresse}?v={marke(pfad)}" if mit_marke else adresse


def versionsmarken_stimmen() -> bool:
    """Ob die Marken in der Seite zu den Dateien passen, auf die sie zeigen."""
    _, block, _ = _zerlegen(SEITE)
    return block == versionsmarken()


def versionsmarken_schreiben(seite: Path | None = None) -> Path:
    """Ersetzt die Marken in der Seite; alles ausserhalb der beiden Kommentare bleibt."""
    seite = Path(seite) if seite is not None else SEITE
    kopf, _, fuss = _zerlegen(seite)
    seite.write_text(kopf + versionsmarken() + fuss, encoding="utf-8")
    return seite


def _zerlegen(seite: Path) -> Tuple[str, str, str]:
    """
    Die Seite in drei Stuecke: bis und mit dem Anfangskommentar, die Marken,
    ab dem Endkommentar. Fehlt ein Kommentar, bricht es ab -- still nichts zu
    schreiben hiesse, die alten Marken blieben stehen.
    """
    zeilen = seite.read_text(encoding="utf-8").splitlines(keepends=True)
    try:
        anfang = next(i for i, zeile in enumerate(zeilen) if zeile.strip() == ANFANG)
        ende = next(i for i, zeile in enumerate(zeilen)
                    if zeile.strip() == ENDE and i > anfang)
    except StopIteration:
        raise ValueError(f"{seite}: Anfang oder Ende der Versionsmarken fehlt.") from None
    return ("".join(zeilen[:anfang + 1]), "".join(zeilen[anfang + 1:ende]),
            "".join(zeilen[ende:]))


if __name__ == "__main__":
    geschrieben = schreiben()
    print(f"{geschrieben.relative_to(WURZEL)}: {len(kerndateien())} Dateien")
    sammlung = formelsammlung_schreiben()
    themen = json.loads(sammlung.read_text(encoding="utf-8"))["themen"]
    print(f"{sammlung.relative_to(WURZEL)}: {len(themen)} Themen, "
          f"{sum(len(t['bloecke']) for t in themen)} Einträge")
    # Zuletzt: die Marken der beiden Verzeichnisse haengen an dem, was eben
    # geschrieben wurde.
    seite = versionsmarken_schreiben()
    print(f"{seite.relative_to(WURZEL)}: Marken für das Stilblatt und "
          f"{len(tafeldateien())} Dateien")
