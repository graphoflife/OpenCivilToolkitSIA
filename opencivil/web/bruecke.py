"""
opencivil/web/bruecke.py -- Welche Dateien der Browser laden muss.

VERANTWORTUNG:
Fuehrt Buch darueber, aus welchen Quelldateien der Rechenkern besteht, und
schreibt diese Liste nach ``web/kern/dateien.json`` -- dazu alle Dateien in
einem Stueck nach ``web/kern/quellen.json``. Der Faden in
``web/js/kern_arbeiter.js`` holt das Paket und legt jede Datei darin ins
Dateisystem von Pyodide -- danach ist ``import opencivil`` im Browser
dasselbe wie auf dem Rechner.

EIN PAKET STATT 214 DATEIEN:
Bis 2026-11-20 holte der Browser jede Datei fuer sich, nach der Liste. Auf
GitHub Pages kostet jede Anfrage ihre Zeit, und ein paar hundert laufen
nicht alle zugleich; jetzt ist es eine. Das Paket ist ein zweites, erzeugtes
Abbild des Quellcodes im Repo -- und damit etwas, das unbemerkt veralten
kann: :func:`quellen_stimmen` prueft im Test, dass es zu den vorhandenen
Dateien passt. Veraltet es, schlaegt der Test an, nicht erst die
veroeffentlichte Seite. Es ist Text und kein Archiv, JSON von Pfad zu
Inhalt: Git speichert davon nur, was sich aendert, und GitHub komprimiert
es beim Senden. Im Diff zeigt Git es nicht (``.gitattributes``) -- was sich
darin aendert, steht schon im Diff der Quelle.

JE DATEI EINE MARKE:
Neben jedem Pfad steht in der Liste seine Marke, die ersten zwoelf Zeichen
von SHA-256 ueber den Inhalt: ihr Diff zeigt, welche Kerndatei sich
aenderte, und der Test merkt, wenn das Neuschreiben vergessen ging. Das
Paket hat seine eigene Marke, in der Importtafel der Seite (unten): ein
geaenderter Kern hat damit eine neue Adresse, und aus dem Zwischenspeicher
kommt kein alter mehr. Ein schlichter statischer Server ohne Cache-Angabe
laesst den Browser nach Gefuehl zwischenspeichern -- so kam einmal
``blatt.py`` nach einer Aenderung noch alt.

UND DAS NOTIZBUCH:
Die ganze Formelsammlung (:func:`opencivil.bericht.formelsammlung.laeufe`)
haengt an keinem Projekt -- rechnen muss man sie trotzdem: zwei Projekte, die
zusammen jeden Nachweis fuehren. Unter Pyodide dauerte das Sekunden. Darum
rechnet sie die Bruecke und legt sie fertig ab, als Seiten des Notizbuchs: je
Formel, je Thema, je Modul eine, im Ordner ``notizbuch/`` -- ohne
anzufassen, was dort von Hand steht (:mod:`opencivil.notizbuch.tresor`). Dazu das
Verzeichnis aller Seiten, ``web/kern/notizbuch.json``: GitHub Pages zeigt
keinen Ordnerinhalt, die Oberflaeche erfaehrt nur so, welche Seiten es gibt.
Die Seiten selbst holt sie ohne Marke und ohne Zwischenspeicher -- eine in
Obsidian geaenderte Notiz steht damit nach dem Hochladen gleich da; eine neue
erst, wenn die Bruecke sie ins Verzeichnis geschrieben hat.

MARKEN AUCH FUER DIE OBERFLAECHE:
Dasselbe traf die Module der Oberflaeche: nach einer Aenderung kam einmal ein
altes ``nachweise.js`` zum neuen Kern. Darum schreibt die Bruecke in
``web/index.html`` eine Importtafel (``<script type="importmap">``): je Modul
unter ``web/js/``, fuer das Paket und fuer das Verzeichnis des Notizbuchs
die Adresse mit Marke, dazu das Stilblatt mit Marke. Die Module selbst bleiben, wie sie sind
-- ``import './dom.js'`` fuehrt ueber die Tafel auf ``./dom.js?v=Marke``.
So haengt alles an der Seite: wer sie neu laedt, bekommt den Rest im selben
Stand. Ohne Marke bleiben nur die Fremdbibliotheken unter ``web/vendor/``;
die aendern sich nur, wenn jemand bewusst eine neue Fassung einlegt.

UND DIE FREMDPAKETE:
Im Manifest steht auch, welche Fremdpakete unter ``web/vendor/pyodide/``
beiliegen (:func:`mitgelieferte_pakete`): Importname -> Paketname, gelesen aus
den Dateien, die dort liegen, und aus ``pyodide-lock.json``. Die App «Python»
laedt nur diese (:mod:`opencivil.konsole.pakete`). Eine zweite, von Hand
gefuehrte Liste gibt es nicht: was ``werkzeug/pyodide_holen.py`` hinlegt,
steht nach dem naechsten Lauf der Bruecke im Manifest. Darum liegt das
Manifest auch im Paket, an seinem Platz neben ``opencivil/``: die Konsole
liest es im Browser wie auf dem Rechner.

WARUM ALLE DATEIEN UND NICHT NUR DIE GEBRAUCHTEN:
Man koennte die Liste auf das beschraenken, was :mod:`opencivil.web.dienst`
einbindet. Dann muesste die Regel aber bei jeder neuen Einbindung nachgezogen
werden, und wer das vergisst, merkt es erst im Browser. Ein paar Dutzend
Kilobyte sind der bessere Handel.

AUFRUF::

    python3 -m opencivil.web.bruecke    # schreibt web/kern/ und die Marken in web/index.html
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from opencivil.notizbuch import erzeugen, tresor

WURZEL = Path(__file__).resolve().parents[2]
PAKET = WURZEL / "opencivil"
MANIFEST = WURZEL / "web" / "kern" / "dateien.json"
QUELLEN = WURZEL / "web" / "kern" / "quellen.json"
PYODIDE = WURZEL / "web" / "vendor" / "pyodide"
NOTIZBUCH = WURZEL / "notizbuch"
VERZEICHNIS = WURZEL / "web" / "kern" / "notizbuch.json"
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
    return tresor.pruefsumme(pfad.read_text(encoding="utf-8"))


#: Was in der Liste und im Paket obenan steht.
HINWEIS = ("Erzeugt von opencivil/web/bruecke.py. Nicht von Hand ändern -- "
           "nach jeder Änderung unter opencivil/ 'python3 -m "
           "opencivil.web.bruecke' laufen lassen.")


def manifest() -> dict:
    return {"hinweis": HINWEIS, "dateien": _mit_marken(), "pakete": mitgelieferte_pakete()}


def quellen() -> dict:
    """
    Das Paket fuer den Browser: Pfad -> Inhalt, fuer jede Datei von
    :func:`kerndateien` und fuer das Manifest -- was der Faden ins
    Dateisystem von Pyodide legt, so wie es im Repo liegt.
    """
    namen = [*kerndateien(), MANIFEST.relative_to(WURZEL).as_posix()]
    return {"hinweis": HINWEIS,
            "dateien": {name: (WURZEL / name).read_text(encoding="utf-8") for name in namen}}


def mitgelieferte_pakete() -> Dict[str, str]:
    """
    Importname -> Paketname, fuer jedes Fremdpaket, dessen Datei beiliegt --
    ``dateutil`` -> ``python-dateutil``. Sortiert, damit das Manifest bei
    gleichem Stand gleich herauskommt.
    """
    try:
        pakete = json.loads((PYODIDE / "pyodide-lock.json").read_text(encoding="utf-8"))["packages"]
    except (OSError, KeyError, ValueError):
        return {}
    heraus = {}
    for name, eintrag in pakete.items():
        if (PYODIDE / eintrag["file_name"]).is_file():
            for modul in eintrag.get("imports") or [name]:
                heraus[modul] = name
    return dict(sorted(heraus.items()))


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
    return (abgelegt.get("dateien") == _mit_marken()
            and abgelegt.get("pakete") == mitgelieferte_pakete())


def schreiben(pfad: Path | None = None) -> Path:
    return _json_schreiben(Path(pfad) if pfad is not None else MANIFEST, manifest())


def quellen_stimmen() -> bool:
    """Ob das abgelegte Paket den vorhandenen Dateien entspricht, Zeichen fuer Zeichen."""
    try:
        return json.loads(QUELLEN.read_text(encoding="utf-8")) == quellen()
    except (OSError, json.JSONDecodeError):
        return False


def quellen_schreiben(pfad: Path | None = None) -> Path:
    """Schreibt das Paket -- nach dem Manifest, das darin liegt."""
    return _json_schreiben(Path(pfad) if pfad is not None else QUELLEN, quellen())


@functools.lru_cache(maxsize=1)
def notizbuch_seiten() -> Tuple[tresor.Seite, ...]:
    """Was der Code zum Notizbuch beitraegt -- einmal je Lauf gerechnet."""
    return tuple(erzeugen.seiten())


def notizbuch_plan(wurzel: Optional[Path] = None) -> tresor.Plan:
    """Was ein Lauf im Notizbuch schriebe, loeschte oder beanstandete."""
    return tresor.planen(notizbuch_seiten(), Path(wurzel) if wurzel else NOTIZBUCH)


def notizbuch_verzeichnis(wurzel: Optional[Path] = None) -> dict:
    """Das Verzeichnis aller Seiten, so wie die Oberflaeche es liest."""
    wurzel = Path(wurzel) if wurzel else NOTIZBUCH
    return {
        "hinweis": (
            "Erzeugt von opencivil/web/bruecke.py. Nicht von Hand ändern -- nach "
            "einer neuen Seite im Notizbuch 'python3 -m opencivil.web.bruecke' "
            "laufen lassen."
        ),
        "wurzel": "notizbuch/",
        "start": "Start",
        "seiten": tresor.verzeichnis(notizbuch_seiten(), wurzel),
        "anhaenge": tresor.anhaenge(wurzel),
    }


def notizbuch_schreiben(wurzel: Optional[Path] = None,
                        verzeichnis: Optional[Path] = None) -> tresor.Plan:
    """
    Schreibt die erzeugten Seiten und das Verzeichnis. Beanstandet der Plan
    etwas, bricht es ab, bevor eine Datei angefasst ist.
    """
    wurzel = Path(wurzel) if wurzel else NOTIZBUCH
    plan = notizbuch_plan(wurzel)
    tresor.ausfuehren(plan, wurzel)
    _json_schreiben(Path(verzeichnis) if verzeichnis else VERZEICHNIS,
                    notizbuch_verzeichnis(wurzel))
    return plan


def notizbuch_stimmt() -> bool:
    """Ob Seiten und Verzeichnis dem entsprechen, was der Code heute ergibt."""
    if not notizbuch_plan().nichts_zu_tun or not VERZEICHNIS.is_file():
        return False
    try:
        abgelegt = json.loads(VERZEICHNIS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return abgelegt == json.loads(json.dumps(notizbuch_verzeichnis()))


def _json_schreiben(ziel: Path, daten: dict) -> Path:
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ziel


def tafeldateien() -> List[Path]:
    """
    Was ueber die Importtafel der Seite geht: jedes Modul der Oberflaeche, das
    Paket des Kerns und das Verzeichnis des Notizbuchs.
    """
    return sorted([*(SEITE.parent / "js").glob("*.js"), QUELLEN, VERZEICHNIS])


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
    # Nach dem Manifest: es liegt im Paket.
    paket = quellen_schreiben()
    print(f"{paket.relative_to(WURZEL)}: {paket.stat().st_size / 1e6:.2f} MB")
    plan = notizbuch_schreiben()
    print(f"{NOTIZBUCH.relative_to(WURZEL)}/: {len(plan.schreiben)} geschrieben, "
          f"{len(plan.unveraendert)} unverändert, {len(plan.loeschen)} gelöscht"
          + (f", {len(plan.verwaist)} verwaist: {', '.join(plan.verwaist)}"
             if plan.verwaist else ""))
    print(f"{VERZEICHNIS.relative_to(WURZEL)}: "
          f"{len(notizbuch_verzeichnis()['seiten'])} Seiten")
    # Zuletzt: die Marken der beiden Verzeichnisse haengen an dem, was eben
    # geschrieben wurde.
    seite = versionsmarken_schreiben()
    print(f"{seite.relative_to(WURZEL)}: Marken für das Stilblatt und "
          f"{len(tafeldateien())} Dateien")
