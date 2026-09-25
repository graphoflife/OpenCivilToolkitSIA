"""
opencivil/web/diagrammdaten.py -- was die Oberflaeche zeichnet, als JSON.

VERANTWORTUNG:
Die Punktfolgen der Diagramme: M-N-Interaktionslinien samt Knickpunkten,
Werkstoffgesetze, Querkraft ueber Moment und ueber Neigung, die Bilder der
Spannung-Dehnung-Analyse. Aus :mod:`opencivil.web.api` herausgeloest, das
damit nur noch Katalog, Mitschrift, Loesung und Zusammenfassung abbildet.

Wie dort wird hier nichts nachgerechnet, was der Kern schon weiss: die Kurven
kommen aus denselben Funktionen wie die Nachweise, hier werden sie in kN,
kNm und mm umgesetzt.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from opencivil import spannungsanalyse
from opencivil.core.berechnung import grad_als_text
from opencivil.core.einheiten import KN, KNM, KN_PRO_M
from opencivil.core.rechenwerk import Loesung
from opencivil.nachweis.handrechnung import BLOCKANTEIL
from opencivil.projekt import Aufbau
from opencivil.querschnitt.platte import Richtung


def linien(aufbau: Aufbau) -> dict:
    """Je M-N-Nachweis mit Linie ihre Punkte, dazu die Bemessungs- und Knickpunkte."""
    return {
        kennung: linie(nachweis, aufbau)
        for kennung, nachweis in aufbau.nachweise.items()
        if nachweis.linie
    }


def querkraftkurven(
    aufbau: Aufbau, gewaehlt: Optional[Mapping[str, float]] = None
) -> dict:
    """
    Der Querkraftwiderstand ueber dem Moment -- eine Kurve je Tragrichtung.

    Eine je Platte ohne Buegel, auch ohne Querkraft: dann rechnet der
    Nachweis still, nur fuer dieses Bild. Die Waagrechte ist vorzeichenbehaftet: rechts das positive
    Moment (Zug unten), links das negative (Zug oben). Beide Aeste im selben
    Bild, weil sie dieselbe Platte beschreiben.

    Einen Ast gibt es nur, wo auf der gezogenen Seite Bewehrung liegt. Fehlt
    sie, gibt es kein ``d`` -- und ohne ``d`` keinen Widerstand.

    ``v_Rd`` haengt ueber ``m_Rd(N_Ed)`` von der Normalkraft ab. Welche gilt,
    waehlt der Benutzer unter dem Diagramm; ``gewaehlt`` bildet die Kennung auf
    diese Normalkraft in kN ab. Ohne Angabe gilt die des ersten Falls dieser
    Richtung -- dann liegen dessen Punkte auf der Kurve.

    Einheiten wie in den anderen Diagrammen: kNm und kN/m.
    """
    gewaehlt = gewaehlt or {}
    kurven: Dict[str, Any] = {}

    for kennung, nachweis in aufbau.querkraft.items():
        if not nachweis.ergebnisse:
            continue
        # Mit Buegeln haengt der Widerstand nicht mehr am Moment, sondern an
        # der Neigung der Druckdiagonalen. Dann steht dort das andere Bild --
        # siehe neigungskurven().
        if nachweis.buegel is not None:
            continue
        querschnitt_kennung = kennung.split(".", 1)[0]
        querschnitt = aufbau.querschnitte.get(querschnitt_kennung)

        n_ed = gewaehlt.get(kennung)
        if n_ed is None:
            n_ed = nachweis.ergebnisse[0].fall.N_Ed.in_einheit(KN)
        kurve = nachweis.kurve(n_ed * 1e3)

        kurven[kennung] = {
            "querschnitt": querschnitt_kennung,
            "namensraum": querschnitt.id if querschnitt else "",
            "name": querschnitt.name if querschnitt else querschnitt_kennung,
            "richtung": nachweis.richtung.value,
            "N_Ed": n_ed,
            "aeste": [
                {
                    "moment_positiv": ast["moment_positiv"],
                    "zugseite": "unten" if ast["moment_positiv"] else "oben",
                    "m_Rd": ast["m_Rd"] / 1e3,
                    "d": ast["d"] * 1e3,
                    "punkte": [
                        {"M_Ed": M / 1e3, "v_Rd": v / 1e3, "plastisch": pl}
                        for M, v, pl in ast["punkte"]
                    ],
                }
                for ast in kurve["aeste"]
            ],
            # Moment vorzeichenbehaftet -- der Fall gehoert auf die Seite, auf
            # der er wirkt. Die Querkraft dagegen als Betrag: ihr Vorzeichen
            # spielt keine Rolle, gerechnet wird ohnehin mit |V_Ed|.
            # Ein stiller Nachweis rechnet nur fuer die Kurve: sein Nullfall
            # ist keine Einwirkung und kein Punkt im Bild.
            "faelle": [] if nachweis.still else [
                {
                    "name": erg.fall.name,
                    "M_Ed": erg.fall.M_Ed.in_einheit(KNM),
                    "N_Ed": erg.fall.N_Ed.in_einheit(KN),
                    "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                    "v_Rd": erg.v_Rd / 1e3,
                    "erfuellt": erg.erfuellt,
                    "plastisch": erg.plastisch,
                    "begruendung": erg.begruendung,
                }
                for erg in nachweis.ergebnisse
            ],
        }
    return kurven


#: Wie weit die Neigungskurve mindestens reicht, in Grad. Die beiden Grenzen
#: des Benutzers liegen normalerweise darin; gehen sie darueber hinaus, waechst
#: die Achse mit -- ein abgeschnittener Ast waere schlimmer als eine breite
#: Achse.
NEIGUNG_VON = 25
NEIGUNG_BIS = 45


def neigungskurven(aufbau: Aufbau) -> dict:
    """
    Der Querkraftwiderstand ueber der Neigung der Druckdiagonalen.

    Nur wo Buegel liegen -- sonst haengt der Widerstand am Moment und das
    andere Diagramm gilt.

    **Ein Bild je statischer Hoehe und Neigungsbereich.** Beides haengt am
    einzelnen Fall: ``d`` am Vorzeichen des Moments, der Bereich am Vorzeichen
    der Normalkraft. Faelle, die darin uebereinstimmen, liegen auf derselben
    Kurve und kommen ins selbe Bild; die anderen bekommen ihr eigenes.

    Gezeichnet wird ueber den ganzen Achsenbereich, auch ausserhalb der beiden
    Grenzen -- dort blass. Die Oberflaeche entscheidet das an ``gewaehlt``,
    gerechnet wird beides hier.
    """
    kurven: Dict[str, Any] = {}

    for kennung, nachweis in aufbau.querkraft.items():
        if nachweis.buegel is None or not nachweis.ergebnisse:
            continue
        querschnitt_kennung = kennung.split(".", 1)[0]
        querschnitt = aufbau.querschnitte.get(querschnitt_kennung)

        # Nach (statischer Hoehe, Grenzen) gruppieren -- in dieser Reihenfolge
        # gefunden, damit die Bilder in der Reihenfolge der Faelle stehen.
        gruppen: Dict[tuple, List[Any]] = {}
        for erg in nachweis.ergebnisse:
            if erg.massgebend is None:
                continue
            gruppen.setdefault(
                (round(erg.d, 9), erg.alpha_min, erg.alpha_max), []).append(erg)

        for nummer, ((d, a_min, a_max), gruppe) in enumerate(gruppen.items(), start=1):
            von = min(NEIGUNG_VON, a_min)
            bis = max(NEIGUNG_BIS, a_max)
            punkte = nachweis.neigungsverlauf(d, von, bis)
            kurven[f"{kennung}.{nummer}"] = {
                "querschnitt": querschnitt_kennung,
                "namensraum": querschnitt.id if querschnitt else "",
                "name": querschnitt.name if querschnitt else querschnitt_kennung,
                "richtung": nachweis.richtung.value,
                "d": d * 1e3,
                "alpha_min": a_min,
                "alpha_max": a_max,
                "zug": gruppe[0].zug_hebt_alpha,
                "punkte": [
                    {"alpha": q.alpha,
                     "V_Rd_s": q.V_Rd_s / 1e3,
                     "V_Rd_c": q.V_Rd_c / 1e3,
                     "V_Rd": q.V_Rd / 1e3,
                     "im_bereich": a_min <= q.alpha <= a_max}
                    for q in punkte
                ],
                "faelle": [] if nachweis.still else [
                    {
                        "name": erg.fall.name,
                        "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                        "alpha": erg.massgebend.alpha,
                        "V_Rd": erg.v_Rd / 1e3,
                        "erfuellt": erg.erfuellt,
                        "begruendung": erg.begruendung,
                    }
                    for erg in gruppe
                ],
            }
    return kurven


def _bild_dict(bild, h: float) -> dict:
    """Ein Querschnittsbild in Zeichengroessen: mm, Promille, N/mm², kN."""
    return {
        "eps_m": bild.eps_m * 1e3, "chi": bild.chi,
        "N": bild.N / 1e3, "M": bild.M / 1e3,
        "h": h * 1e3,
        "nulllinie": (bild.nulllinie * 1e3
                      if bild.nulllinie is not None else None),
        "beton": [{"z": f.z * 1e3, "eps": f.eps * 1e3, "sigma": f.sigma / 1e6}
                  for f in bild.beton],
        "stahl": [{"z": s.z * 1e3, "eps": s.eps * 1e3, "sigma": s.sigma / 1e6,
                   "nummer": s.nummer, "a_s": s.a_s * 1e6, "kraft": s.kraft / 1e3}
                  for s in bild.stahl],
        "konvergiert": bild.konvergiert, "hinweis": bild.hinweis,
    }


def spannungsanalysen(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Die Auswertungen am Querschnitt, je Platte -- fertig zum Zeichnen.

    Gerechnet wird in :func:`opencivil.spannungsanalyse.analysen`; hier wird
    nur in Zeichengroessen abgebildet.
    """
    return {kennung: [_analyse_dict(a) for a in liste]
            for kennung, liste in spannungsanalyse.analysen(aufbau, loesung).items()}


def _analyse_dict(analyse) -> dict:
    kopf = {"name": analyse.fall.name, "art": analyse.art.value,
            "richtung": analyse.richtung.value,
            "titel": analyse.art.beschriftung}
    if not analyse.moeglich:
        return {**kopf, "moeglich": False, "hinweis": analyse.hinweis}
    if analyse.kurve is not None:
        kurve = analyse.kurve
        return {**kopf, "moeglich": True, "kurve": {
            "N": kurve.N / 1e3, "M_Riss": kurve.M_Riss / 1e3,
            "M_Rd": kurve.M_Rd / 1e3, "hinweis": kurve.hinweis,
            "punkte": [{"M": p.M / 1e3, "chi": p.chi, "zeta": p.zeta,
                        "chi_I": p.chi_I, "chi_II": p.chi_II}
                       for p in kurve.punkte]}}
    return {**kopf, "moeglich": True, "bild": _bild_dict(analyse.bild, analyse.h)}


def werkstoffgesetze(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Punktfolgen der Spannungs-Dehnungs-Beziehungen, je Material.

    Gerechnet wird mit denselben Gesetzen wie im Nachweis -- die Kurve zeigt
    also genau das, was der Querschnittsintegration zugrunde liegt, und nicht
    eine zweite, nachgebaute Fassung.

    Vorzeichen wie im ganzen Werkzeug: Zug positiv. Der Beton liegt damit im
    dritten Quadranten, der Stahl spannt sich ueber beide.
    """
    ergebnis: Dict[str, dict] = {}

    for kennung, stoff in aufbau.baustoffe.items():
        def wert(kurzname: str) -> Optional[float]:
            eintrag = loesung.werte.get(stoff.definitionen[kurzname].id)
            return eintrag.groesse.si if eintrag else None

        try:
            if stoff.art.value == "beton":
                eintrag = _betonkurve(stoff, wert)
            else:
                eintrag = _stahlkurve(stoff, wert)
        except (KeyError, TypeError):
            continue  # Kennwerte noch nicht gerechnet
        if eintrag:
            eintrag["name"] = stoff.name
            eintrag["art"] = stoff.art.value
            ergebnis[kennung] = eintrag
    return ergebnis


def _betonkurve(stoff, wert, schritte: int = 80) -> Optional[dict]:
    """Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung."""
    from opencivil.querschnitt.werkstoffgesetz import Betongesetz

    f_cd, eps_c1d = wert("f_cd"), wert("eps_c1d")
    eps_c2d, k_sigma = wert("eps_c2d"), wert("k_sigma")
    if None in (f_cd, eps_c1d, eps_c2d, k_sigma):
        return None

    gesetz = Betongesetz(f_cd=abs(f_cd), eps_c1d=abs(eps_c1d),
                         eps_c2d=abs(eps_c2d), k_sigma=k_sigma)
    punkte = []
    for i in range(schritte + 1):
        eps = -abs(eps_c2d) * i / schritte
        punkte.append({"eps": eps * 1e3, "sigma": gesetz.spannung(eps) / 1e6})

    return {
        "punkte": punkte,
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Beton – Parabel-Rechteck-Beziehung",
        "referenz": "SIA 262:2025, 4.2.1.6",
        "marken": [
            {"eps": -abs(eps_c1d) * 1e3, "sigma": -abs(f_cd) / 1e6, "text": "ε_c1d"},
            {"eps": -abs(eps_c2d) * 1e3, "sigma": -abs(f_cd) / 1e6, "text": "ε_c2d"},
        ],
        "vereinfacht": _spannungsblock(abs(f_cd), abs(eps_c2d)),
    }


def _spannungsblock(f_cd: float, eps_c2d: float) -> dict:
    """
    Der vereinfachte, rechteckige Spannungsverlauf.

    Unterhalb von ``(1 - 0.85) * eps_c2d`` wird keine Spannung angesetzt,
    darueber durchgehend ``f_cd``. Das ist dieselbe Vereinfachung, die auch der
    Handrechnung zugrunde liegt -- dort als Druckzone der Hoehe ``0.85 x``.
    Beide Bilder gehoeren zusammen, und genau deshalb steht die Stufe hier neben
    der Parabel: man sieht, was man aufgibt, wenn man von Hand rechnet.
    """
    eps_knick = (1.0 - BLOCKANTEIL) * eps_c2d
    ecken = [
        (0.0, 0.0),
        (-eps_knick, 0.0),
        (-eps_knick, -f_cd),
        (-eps_c2d, -f_cd),
    ]
    return {
        "punkte": [{"eps": e * 1e3, "sigma": s / 1e6} for e, s in ecken],
        "titel": "vereinfacht (Spannungsblock)",
        "beschreibung": (
            f"σ = 0 bis {1 - BLOCKANTEIL:.2f}·ε_c2d, darüber f_cd. "
            f"Entspricht der Druckzone {BLOCKANTEIL}·x der Handrechnung."
        ),
    }


def _stahlkurve(stoff, wert) -> Optional[dict]:
    """
    Bilineare Beziehung ohne Verfestigung.

    Fuenf Eckpunkte genuegen -- dazwischen ist sie gerade, und mehr Punkte
    wuerden nur vortaeuschen, dass etwas gekruemmt waere.
    """
    E_s, f_yd = wert("E_s"), wert("f_yd")
    f_yd_druck, eps_ud = wert("f_yd_druck"), wert("eps_ud")
    if None in (E_s, f_yd, f_yd_druck, eps_ud):
        return None

    eps_yd, eps_yd_druck = f_yd / E_s, abs(f_yd_druck) / E_s
    ecken = [
        (-abs(eps_ud), -abs(f_yd_druck)),
        (-eps_yd_druck, -abs(f_yd_druck)),
        (0.0, 0.0),
        (eps_yd, f_yd),
        (abs(eps_ud), f_yd),
    ]
    return {
        "punkte": [{"eps": e * 1e3, "sigma": s / 1e6} for e, s in ecken],
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Betonstahl – bilineare Beziehung",
        "referenz": "SIA 262:2025, 4.2.2.4",
        "marken": [
            {"eps": eps_yd * 1e3, "sigma": f_yd / 1e6, "text": "ε_yd"},
            {"eps": abs(eps_ud) * 1e3, "sigma": f_yd / 1e6, "text": "ε_ud"},
        ],
    }


def _knickpunkte(aufbau, nachweis) -> list:
    """
    Die Knicknachweise als Punktepaare fuer das M-N-Diagramm.

    Zu jedem Fall zwei Punkte auf derselben Hoehe N_Ed: das Moment 1. Ordnung
    und das am verformten System. Die Strecke dazwischen ist der Zuwachs aus
    Schiefstellung und Verformung -- im Diagramm sieht man sofort, ob er den
    Punkt ueber die Linie schiebt.

    Nur in x-Richtung, denn nur dort gibt es einen Knicknachweis.
    """
    if nachweis.richtung is not Richtung.X:
        return []
    kennung = nachweis.querschnitt.id.rsplit(".", 1)[-1]
    knicken = (aufbau.knicken or {}).get(kennung)
    if knicken is None:
        return []
    punkte = []
    for erg in knicken.ergebnisse:
        if erg.fall.N_Ed.si >= 0.0:
            continue
        punkte.append({
            "name": erg.fall.name,
            "N_Ed": erg.fall.N_Ed.in_einheit(KN),
            "M_Ed_1": abs(erg.fall.M_Ed_1.in_einheit(KNM)),
            "M_Ed_II": abs(erg.M_ges) / 1e3,
            "N_Rd": erg.N_Rd / 1e3,
            "M_bei_N_Rd": erg.M_bei_N_Rd / 1e3,
            "erfuellungsgrad": erg.erfuellungsgrad,
            "grad_text": grad_als_text(erg.erfuellungsgrad, erg.erfuellt),
            "erfuellt": erg.erfuellt,
            "stabil": erg.stabil,
            "begruendung": erg.begruendung,
        })
    return punkte


def linie(nachweis, aufbau=None) -> dict:
    """
    Die M-N-Interaktionslinien zum Zeichnen -- in kN und kNm.

    Zwei Linien: die genaue aus Dehnungsebenen (``punkte``) und das Polygon aus
    der Handrechnung (``handpunkte``). Nachgewiesen wird gegen das Polygon; die
    genaue Linie steht daneben, damit man sieht, wie viel die Vereinfachung
    kostet.
    """
    return {
        "richtung": nachweis.richtung.value,
        "querschnitt": nachweis.querschnitt.name,
        "punkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "abschnitt": p.abschnitt}
            for p in nachweis.linie
        ],
        "handpunkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "name": p.name}
            for p in getattr(nachweis, "handlinie", [])
        ],
        "kombinationen": [
            {
                "name": a.schnittgroessen.name,
                "M_Ed": a.schnittgroessen.M_Ed.in_einheit(KNM),
                "N_Ed": a.schnittgroessen.N_Ed.in_einheit(KN),
                "art": a.schnittgroessen.art.value,
                "art_text": a.schnittgroessen.art.beschriftung,
                "innerhalb": a.innerhalb,
                "erfuellungsgrad": a.erfuellungsgrad,
                "grad_text": grad_als_text(a.erfuellungsgrad, a.innerhalb),
                "groesse": a.achse.name,
                "massstab": a.massstab.value,
                "massstab_text": a.massstab.beschriftung,
                "widerstand": (
                    {"N": a.widerstand[0] / 1e3, "M": a.widerstand[1] / 1e3}
                    if a.widerstand
                    else None
                ),
                "begruendung": a.begruendung,
            }
            for a in nachweis.auswertungen
        ],
        # Die Knickfaelle gehoeren in dasselbe Bild: sie tragen dieselbe
        # Normalkraft gegen dieselbe Linie, nur mit einem groesseren Moment.
        "knickfaelle": _knickpunkte(aufbau, nachweis) if aufbau else [],
    }
