"""
opencivil/projekt/beispiele.py -- die Prüfprojekte: das Beispiel und «Jeder Nachweis».

VERANTWORTUNG:
Das Beispiel, mit dem die Oberflaeche startet (:func:`beispiel`), und das
Pruefprojekt, das jeden Nachweis einmal laut fuehrt (:func:`jeder_nachweis`).
Beide sind ueber die Fassade des Projekts gebaut, wie ein Benutzer es in
Python taete; aus ihnen stammen der Schnappschuss des Berichts und die
Formelsammlung. :meth:`Projekt.beispiel <opencivil.projekt.projekt.Projekt.beispiel>`
und :meth:`Projekt.jeder_nachweis <opencivil.projekt.projekt.Projekt.jeder_nachweis>`
fuehren hierher. Bis 2026-11-10 standen sie in der Klasse des Projekts, die
damit fast neunhundert Zeilen hatte.
"""

from __future__ import annotations

import math

from opencivil.decke.schnitt import BALKENGROESSEN
from opencivil.projekt.balkensystem import DIAGRAMMGROESSEN
from opencivil.projekt.balkensystem3d import DIAGRAMMGROESSEN as DIAGRAMMGROESSEN3D
from opencivil.projekt.decke import PLATTENGROESSEN
from opencivil.projekt.eintraege import (
    Gebrauchswahl, KnickVerformungswahl, KnickWiderstandswahl, RechenwahlEintrag,
)
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.projekt import Projekt
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.projekt.skript import VORLAGE
from opencivil.projekt.staebe import MATERIAL_DES_QUERSCHNITTS
from opencivil.querschnitt.geometrie import Linienart
from opencivil.querschnitt.gesetzwahl import Rechenart, Werkstoffsatz


def beispiel() -> Projekt:
    """
    Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet.

    Gebaut über dieselben Methoden, die man ohne Oberfläche benutzt. So
    steht die Fassade an einer Stelle vorgeführt -- und der
    Schnappschuss-Test prüft sie mit: baute sie etwas anderes als die
    Einträge von Hand, die hier vorher standen, änderte sich der Bericht.
    """
    projekt = Projekt(name="OCT Projekt")
    projekt.beton("C30/37")
    projekt.stahl("B500B")
    # Aussen y, innen x -- der übliche Fall: die Querrichtung läuft unten
    # und oben durch, die Tragrichtung liegt dazwischen und verliert
    # dadurch statische Höhe. Die 2. Lage trägt eine Zulage.
    platte = projekt.platte("Decke über EG", h=300,
                            x=[18, 12], x_zulage=[12, 0], y=[12, 12])
    # Die Werte sind so gewählt, dass das Beispiel grün startet.
    platte.einwirkung("Feld", M_Ed=100.0)
    platte.einwirkung("Feld mit Druck", M_Ed=100.0, N_Ed=-300.0)
    platte.einwirkung("Stütze", M_Ed=-50.0)
    # Die Durchbiegung im Feld, mit E_cm gerechnet -- der
    # Vergrösserungsfaktor macht sie gut viermal grösser.
    platte.verformungsfall("Feld", w=3.5, laenge=6.0)
    # Ein gezeichneter Querschnitt: der Unterzug, 300 × 600 mm. Vier
    # Schubwände auf der Bügelachse umschliessen eine Zelle -- so trägt
    # er auch Torsion; jede Wand kreuzt ein Schenkel des Bügels.
    unterzug = projekt.analyse("Unterzug")
    stahl = unterzug.stablinien[0].stahl
    for von, bis in (([50.0, 50.0], [250.0, 50.0]), ([250.0, 50.0], [250.0, 550.0]),
                     ([250.0, 550.0], [50.0, 550.0]), ([50.0, 550.0], [50.0, 50.0])):
        unterzug.schubwand(von, bis, dicke=100.0, durchmesser=10.0, teilung=150.0,
                           schnitte=1, stahl=stahl)
    unterzug.lastfall("Feld", M_y_Ed=150.0, V_z_Ed=150.0, T_Ed=15.0)
    # Ein Rahmen: zwei Stützen von 4 m und ein Riegel von 6 m mit dem
    # Querschnitt des Unterzugs. Links eingespannt, rechts eine
    # Pendelstütze; das Eigengewicht von selbst, eine Auflast auf dem
    # Riegel, Wind auf der linken Stütze -- kombiniert in GZT und GZG,
    # dazu die Diagramme eines neuen Systems und die Lagerkräfte.
    rahmen = projekt.balkensystem("Rahmen")
    beton = rahmen.beton("b1")
    stuetze = rahmen.querschnitt("Stütze 300×300", "rechteck", b=300.0, h=300.0)
    riegel = rahmen.querschnitt_aus("Unterzug", "analyse", unterzug)
    links = rahmen.linie((0, 0), (0, 4), querschnitt=stuetze, material=beton)
    balken = rahmen.linie((0, 4), (6, 4), querschnitt=riegel, material=beton)
    rahmen.linie((6, 4), (6, 0), querschnitt=stuetze, material=beton, gelenk_anfang=True)
    rahmen.lager_an((0, 0), "eingespannt")
    rahmen.lager_an((6, 0), "gelenkig")
    eigengewicht = rahmen.lastfall("Eigengewicht", eigengewicht=True)
    auflast = rahmen.lastfall("Auflast")
    wind = rahmen.lastfall("Wind")
    rahmen.stablast(auflast, balken, wert=20.0)
    rahmen.stablast(wind, links, wert=3.0, richtung="waagrecht")
    gzt = rahmen.kombination("GZT", (eigengewicht, 1.35), (auflast, 1.35), (wind, 1.5))
    gzg = rahmen.kombination("GZG", (eigengewicht, 1.0), (auflast, 1.0), (wind, 1.0))
    for groesse in ("M", "V", "N", "lagerkraefte"):
        rahmen.diagramm(gzt, groesse)
    rahmen.diagramm(gzg, "verschiebung")
    # Ein Einzelfundament 2.0 × 2.5 m, 1.2 m tief, das Grundwasser tiefer
    # als der Gleitkörper -- grün, wie der Rest.
    fundament = projekt.grundbruch("Fundament Stütze", phi_k=32.0, b=2.0, L=2.5,
                                   t=1.2, t1=5.0)
    fundament.kombination("Tragsicherheit", N_Ed=1500.0, T_Ed=150.0)
    # Und seine Setzung: bis zur Sohle 1.2 m Aushub, das ist die
    # Wiederbelastung; der Rest der Pressung belastet den Boden zum
    # ersten Mal. Unter dem Kies ein weicher Silt, darunter Moräne.
    setzung = projekt.setzung("Fundament Stütze", B=2.0, L=2.5, q_W=24.0, q_E=196.0,
                              s_zul=25.0)
    setzung.schicht("Kies, sandig", d=2.0, M_E=60.0, M_E_strich=180.0)
    setzung.schicht("Silt, tonig", d=3.0, M_E=15.0, M_E_strich=45.0)
    setzung.schicht("Moräne", d=4.0, M_E=100.0, M_E_strich=250.0)
    # Und als Pfahl gegründet: ein Bohrpfahl ⌀ 900 durch die Auffüllung, die
    # nicht trägt, und den Kies bis in die Moräne, am Kopf auch quer belastet
    # -- grün, wie der Rest.
    pfahl = projekt.pfahl("Pfahl Stütze", stahl=_erstes(projekt, "betonstahl"),
                          beton=_erstes(projekt, "beton"), D=900.0, L=12.0, t_K=1.5,
                          t_w=3.0)
    pfahl.schicht("Auffüllung", d=2.0, gamma=19.0, mantel="eingeben", q_s=0.0, E_s=10.0)
    pfahl.schicht("Kies, sandig", d=6.0, gamma=21.0, phi_k=34.0, K=0.44, E_s=60.0)
    pfahl.schicht("Moräne", d=15.0, gamma=22.0, phi_k=36.0, c_k=5.0, K=0.41, E_s=120.0)
    pfahl.kombination("Tragsicherheit", N_Ed=2000.0, H_Ed=100.0)
    # Und das Haus im Erdbeben: vier Geschosse auf je zwei Wänden in x und
    # in y, alle aus einer Querschnittsanalyse 5000 × 250 mm, an beiden
    # Seiten ⌀ 12 alle 150 mm -- die in y um 90° gedreht. Grund- und Aufriss
    # regelmässig, T₁ weit unter 4·T_C -- grün, wie der Rest.
    wand = _tragwand(projekt.freie_kennung("a"), "Tragwand 5000 × 250",
                     [[0, 0], [5000, 0], [5000, 250], [0, 250]], _erstes(projekt, "beton"))
    for z in (50.0, 200.0):
        wand.stablinie([50.0, z], [4950.0, z], art="teilung", durchmesser=12, teilung=150,
                       stahl=_erstes(projekt, "betonstahl"))
    projekt.querschnittsanalysen.append(wand)
    haus = projekt.gebaeude("Wohnhaus")
    for name in ("EG", "1. OG", "2. OG"):
        haus.geschoss(name, h=3.0, G_k=2500.0, Q_k=800.0)
    haus.geschoss("Dach", h=3.0, G_k=2000.0)
    haus.wand("Wände in x", wand.kennung, n=2)
    haus.wand("Wände in y", wand.kennung, lage="90", n=2)

    # Ein Skript für die App «Python», mit einem Diagramm -- ohne Download.
    projekt.skript("Skript 1", VORLAGE)
    return projekt


def jeder_nachweis() -> Projekt:
    """
    Jeder Nachweis einmal laut -- und die Fälle, die das Beispiel nie zeigt.

    Zusammen mit :func:`beispiel` führt es jeden Nachweis einmal laut; ein
    Test wacht darüber. Aus den beiden stammen der Schnappschuss des
    Berichts und die Formelsammlung der Oberfläche -- darum steht es hier
    und nicht bei den Tests.

    Erhöhte Anforderung mit allen Schaltern und begrenzter rissaktiver
    Dicke, häufige und quasi-ständige Lastfälle abgeleitet und eigene, Bügel
    mit Stabzahl in y, ein Knickfall, die Verformung im Feld und am
    Kragarm; eine zweite Platte mit x aussen und b = 500 mm, die im Feld
    nicht aufgeht, auch nicht in der Durchbiegung, und deren Stahl unter
    Dauerlast fliesst, dazu Querkraft ohne Bügel -- einmal über m_Rd,
    einmal darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
    Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
    gemessen wird, und ⌀40 in y unter der x-Bewehrung -- die fliesst bei
    x = h/2 nicht. Gebaut über die Fassade, wie ein Benutzer es in Python
    täte.
    """
    p = Projekt(name="Jeder Nachweis einmal")
    p.beton("C30/37")
    p.stahl("B500B")
    p.baustahl("S355")
    p.spannstahl("Y1860")
    p.holz("GL24h")
    decke = p.platte("Decke", h=300, x=[18, 12], x_zulage=[12, 0], y=[12, 12],
                     rissanforderung="erhoeht", duktilitaet=True, sproede=True,
                     zwaengung=True, zwaengung_begrenzt=True,
                     zwaengung_biegung=True)
    decke.querkraftbewehrung.durchmesser = 8.0
    decke.querkraftbewehrung.art_y = Linienart.ANZAHL
    decke.querkraftbewehrung.anzahl_y = 5.0
    decke.einwirkung("Feld", M_Ed=150, V_Ed=80)
    decke.einwirkung("Feld mit Druck", M_Ed=120, N_Ed=-300)
    decke.einwirkung("Stütze", M_Ed=-60, V_Ed=60)
    decke.haeufig.aus_tragsicherheit = True
    decke.haeufig.lastfall("Gebrauch", M_Ed=90)
    decke.quasistaendig.aus_tragsicherheit = True
    decke.quasistaendig.lastfall("Dauerlast", M_Ed=70)
    decke.knickfall("Wand", N_Ed=-800, M_Ed_1=20, laenge=3.0)
    # Die Verformung im Feld und am Kragarm -- einmal je gezogene Seite.
    decke.verformungsfall("Feld", w=3.0, laenge=6.0)
    decke.verformungsfall("Kragarm", w=0.8, laenge=2.5, zugseite="oben")
    # Die Kapitel der Decke rechnen mit φ = 2, wie bis 2026-10-09 die
    # Platte.
    decke.zwaengung_biegung_kriechzahl = 2.0
    decke.haeufig.wahl.kriechzahl = decke.quasistaendig.wahl.kriechzahl = 2.0
    decke.knicken_wahl_verformung.kriechzahl = 2.0
    # Zwei Linien der Spannung-Dehnung-Analyse -- sie schreiben ihre
    # Herleitung für die Formelsammlung: präzise, und mit der
    # 0.85·x-Vereinfachung und charakteristischen Werten. Eine
    # Handrechnung gibt es dort nicht mehr (2026-10-12).
    decke.spannungsfall("Biegung mit Druck", art="moment_kruemmung", N_Ed=-300,
                        kriechzahl=2.0)
    decke.spannungsfall("Zug mit Moment", art="normalkraft_dehnung", M_Ed=30,
                        kriechzahl=1.0, werkstoffsaetze=charakteristisch(decke),
                        rechenarten={decke.beton: Rechenart.BLOCK})
    # Der äquivalente E-Modul, einmal über dem Moment und einmal über der
    # Normalkraft bei festem Moment -- dort zählt er ab dem Zustand ohne N.
    decke.spannungsfall("Biegesteifigkeit", art="moment_emodul",
                        werkstoffsaetze=charakteristisch(decke))
    decke.spannungsfall("Dehnsteifigkeit", art="normalkraft_emodul", M_Ed=30,
                        werkstoffsaetze=charakteristisch(decke))

    # Ein Streifen von 500 mm: M und N je b, V je Meter. Mit halben
    # Momenten sind es dieselben Grade wie bei 1000 mm -- nur die
    # Lagentabelle zeigt, dass x je b und y je Laufmeter gilt.
    dach = p.platte("Dach", h=200, x=[10, 10], y=[8, 8], x_innen=False,
                    einlagenhoehe=40, b=500)
    dach.einwirkung("Feld", M_Ed=40, V_Ed=40)
    dach.einwirkung("Rand", M_Ed=10, V_Ed=30)
    dach.quasistaendig.lastfall("Dauerlast", M_Ed=20)
    # Mit φ = 2 fliesst hier der Stahl -- der Fall soll laut bleiben.
    dach.quasistaendig.wahl.kriechzahl = 2.0
    # Die Durchbiegung geht nicht auf, mit einem eigenen φ.
    dach.verformung.kriechzahl = 1.5
    dach.verformungsfall("Feld", w=2.0, laenge=5.0)

    # Jede Rechenwahl einmal laut. Die Platte «Parabel» haelt die
    # Tragsicherheit praezise mit charakteristischen Werten -- M_Rk,
    # m_Rk in der Querkraft, sproedes Versagen --, rechnet die
    # Stahlspannungen mit 0.85·x und praezise und knickt mit eigener
    # Linie: Verformung mit charakteristischen Werten, Widerstand praezise
    # mit Bemessungswerten. Die «Decke» knickt mit der Vorgabe 0.85·x
    # gegen ihre Handrechnung, also ebenfalls mit eigener Linie.
    genau = p.platte("Parabel", h=250, x=[12, 10], y=[10, 10],
                     rissanforderung="erhoeht", sproede=True)
    genau.tragsicherheit_wahl = RechenwahlEintrag(
        kriechzahl=1.0, werkstoffsaetze=charakteristisch(genau),
        rechenarten={genau.beton: Rechenart.PARABEL})
    genau.einwirkung("Feld", M_Ed=60, N_Ed=-200, V_Ed=50)
    genau.quasistaendig.lastfall("Dauerlast", M_Ed=30)
    genau.quasistaendig.wahl = Gebrauchswahl(kriechzahl=1.0,
                                             rechenarten={genau.beton: Rechenart.BLOCK})
    genau.haeufig.lastfall("Gebrauch", M_Ed=45)
    genau.haeufig.wahl = Gebrauchswahl(kriechzahl=2.0)
    genau.knickfall("Stütze", N_Ed=-600, M_Ed_1=10, laenge=3.0)
    genau.knicken_wahl_verformung = KnickVerformungswahl(
        werkstoffsaetze=charakteristisch(genau))
    genau.knicken_wahl_widerstand = KnickWiderstandswahl(
        rechenarten={genau.beton: Rechenart.PARABEL})

    # Die Platte «Block» haelt die Tragsicherheit mit der 0.85·x-Vereinfachung,
    # einmal bei festem Moment -- dort zeigt die Probe die Normalkraft --,
    # rechnet die Stahlspannung von Hand und knickt gegen dieselbe Linie.
    block = p.platte("Block", h=220, x=[10, 10], y=[8, 8])
    block.tragsicherheit_wahl = RechenwahlEintrag(rechenarten={block.beton: Rechenart.BLOCK})
    block.einwirkung("Feld", M_Ed=25, V_Ed=30)
    block.einwirkung("Rand", M_Ed=-15, N_Ed=-100).art = "M_konstant"
    block.quasistaendig.lastfall("Dauerlast", M_Ed=12)
    block.quasistaendig.wahl = Gebrauchswahl(
        rechenarten={block.beton: Rechenart.HANDRECHNUNG})
    block.knickfall("Wand", N_Ed=-400, M_Ed_1=5, laenge=2.5)
    block.knicken_wahl_widerstand = KnickWiderstandswahl()

    ohne = p.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
    ohne.einwirkung("Feld", M_Ed=30, V_Ed=20)
    ohne.verformungsfall("Feld", w=2.0, laenge=4.0)

    konsole = p.platte("Konsole", h=250, x=[12, 12], y=[40, 10])
    konsole.einwirkung("Feld", M_Ed=40, V_Ed=50)
    konsole.einwirkung("Schräg", M_Ed=30, N_Ed=-500).art = "naechster_Punkt"

    # Gemischte Werte, je Material gewählt (2026-11-20): in der Tragsicherheit
    # der Beton charakteristisch und der Stahl mit Bemessungswerten, von
    # Hand -- ein Widerstand heisst dann R --, in der Stahlspannung umgekehrt,
    # dazu eine Spannung-Dehnung-Analyse.
    gemischt = p.platte("Gemischt", h=250, x=[12, 10], y=[10, 10])
    gemischt.tragsicherheit_wahl = RechenwahlEintrag(
        werkstoffsaetze={gemischt.beton: Werkstoffsatz.CHARAKTERISTISCH})
    gemischt.einwirkung("Feld", M_Ed=50, V_Ed=40)
    gemischt.quasistaendig.lastfall("Dauerlast", M_Ed=25)
    gemischt.quasistaendig.wahl = Gebrauchswahl(
        werkstoffsaetze={gemischt.beton: Werkstoffsatz.BEMESSUNG})
    gemischt.spannungsfall("Gemischt", art="moment_kruemmung",
                           werkstoffsaetze={gemischt.beton: Werkstoffsatz.CHARAKTERISTISCH})

    # Vier gezeichnete Querschnitte. Ein Kastenträger mit Aussparung,
    # Bewehrung in allen drei Arten, vier Schubwänden als Zelle, Torsion,
    # schiefer Biegung und Längszugkraft, gerechnet mit dem
    # Spannungsblock, dazu jeder Gebrauchsnachweis bei erhöhter
    # Anforderung; eine Stütze, einachsig, mit charakteristischen Werten,
    # normaler Anforderung und Knicken -- so steht jede Wahl einmal da.
    # Dazu ein Träger mit Spanngliedern, je eines in jedem Gesetz, und
    # einer aus Stahl.
    p.querschnittsanalysen.append(_kastentraeger(p.freie_kennung("a")))
    p.querschnittsanalysen.append(_stuetze(p.freie_kennung("a")))
    p.querschnittsanalysen.append(_spannbeton(p.freie_kennung("a")))
    p.querschnittsanalysen.append(_stahltraeger(p.freie_kennung("a")))

    # Zwei Balkensysteme: eines, das alles einmal braucht, und eines, das
    # sich nicht rechnen lässt -- dazu ein Rahmen im Raum. Dazu jede Lage
    # beim Durchstanzen und jede Spielart von Grundbruch, Setzung und Pfahl.
    _alles_einmal(p, decke, p.querschnittsanalysen[0])
    _beweglich(p)
    _raumrahmen(p, decke, p.querschnittsanalysen[0])
    _decken(p)
    _durchstanzstellen(p)
    _grundbrueche(p)
    _setzungen(p)
    _pfaehle(p)
    _gebaeude(p)
    return p


def _decken(p: Projekt) -> None:
    """
    Zwei Decken. Die des Kolloquiums 4 (Stahlbeton II): eine Platte auf
    einer Wand und drei Stützen, versteckte Unterzüge in zwei Stufen, fest
    30 % in x, und als einziger Lastfall q_d = 18.6 kN/m² auf der ganzen
    Platte, das Eigengewicht darin. Und eine, die jede Wahl einmal braucht:
    zwei Platten verschiedener Dicke in einem L, automatisch aufgeteilt, mit
    einer Zone, einer eingespannten Wand, einem Rand an einer Symmetrieachse
    und einer Stütze mit Stützenbereich von Hand -- daneben eine schiefe
    Platte, deren Streifen ihren Rändern folgen. Sie hat die Lastfälle und
    Kombinationen einer frischen Decke und jede Art Last: auf einer ganzen
    Platte, gezeichnet, längs einer Linie und an einem Punkt. Die erste
    zeigt m_x, m_y, die Lager und M und V des Unterzugs U4, der auf den drei
    anderen liegt; die zweite jedes Bild der Platte einmal.
    """
    beton = _erstes(p, "beton")
    k4 = p.decke("Kolloquium 4", aufteilung="fest", anteil=30.0)
    k4.platte([(0, 0), (9, 0), (9, 5.5), (0, 5.5)], beton=beton, h=240)
    k4.lager((0, 0), (9, 0))
    for x in (0.5, 4.5, 8.5):
        k4.stuetze((x, 5.0))
        k4.unterzug((x, 0), (x, 5.5), stufe=2)
    k4.unterzug((0, 5.0), (9, 5.0))
    q_d = k4.lastfall("q_d")
    k4.plattenlast(q_d, "P1", 18.6)
    for groesse in ("m_x", "m_y", "lager"):
        k4.diagramm(q_d, groesse)
    for groesse in BALKENGROESSEN:
        k4.diagramm(q_d, groesse, "U4")

    el = p.decke("Jede Wahl", streifenbreite=0.5)
    el.platte([(0, 0), (6, 0), (6, 4), (0, 4)], beton=beton, h=220)
    el.platte([(0, 4), (6, 4), (6, 7), (3, 7), (0, 7)], beton=beton, h=280)
    el.lager((0, 0), (6, 0))
    el.lager((6, 0), (6, 4), eingespannt=True)
    el.lager((0, 0), (0, 7))
    el.lager((0, 7), (3, 7))
    el.lager((3, 7), (6, 7), vertikal=False, eingespannt=True)
    el.stuetze((6, 7), b_x=400, b_y=250, bereich_von_hand=True, l_x=1.2, l_y=0.8)
    el.zone([(0, 0), (2, 0), (2, 4), (0, 4)], anteil=100.0)
    schief = [(9.0, 0.0), (13.0, 0.0), (14.0, 3.0), (10.0, 3.0)]
    el.platte(schief, beton=beton, h=200, richtungen_von_hand=True, richtung_1=0.0,
              richtung_2=math.degrees(math.atan2(3.0, 1.0)))
    for a, b in zip(schief, schief[1:] + schief[:1]):
        el.lager(a, b)
    gzt = el.standardfaelle()
    for groesse in PLATTENGROESSEN:
        el.diagramm(gzt, groesse)
    _, auflast, nutzlast = el.lastfaelle
    el.plattenlast(auflast, "P2", 1.5)
    el.linienlast(auflast, (1, 6.5), (5, 6.5), wert=8.0)
    el.flaechenlast(nutzlast, [(3, 1), (5, 1), (5, 3), (3, 3)], wert=5.0)
    el.punktlast(nutzlast, (12.5, 2.0), wert=30.0)


def _durchstanzstellen(p: Projekt) -> None:
    """
    Jede Lage der gestützten Fläche, jede Form der Stütze, jede
    Näherungsstufe und beide Wege zu k_e: eine Innenstütze mit Flächenlast;
    eine Rundstütze am Rand, k_e aus der Exzentrizität; eine Eckstütze, die
    ohne Durchstanzbewehrung aufgeht, mit den Randstreifen bis zum zweiten
    Rand (Figur 25); eine Randstütze in Stufe 3, deren r_s senkrecht zum Rand
    auf 2/3 · b_sr steigt; eine lange Ovalstütze in einer Bodenplatte, mit
    Momenten von Hand und einer Aussparung neben der Ecke; ein Wandende und
    eine Wandecke, an denen Stufe 2 wie Stufe 1 rechnet und für die es noch
    keinen Vorschlag gibt. Innen-, Rand- und Ovalstütze brauchen
    Durchstanzbewehrung; eine zweite Innenstütze trägt so viel, dass es einen
    Stahlpilz braucht.
    """
    beton, stahl = _erstes(p, "beton"), _erstes(p, "betonstahl")
    p.durchstanzen("Innenstütze", beton, stahl, b_x=400, b_y=400, V_d=900.0, q_d=14.0)
    p.durchstanzen("Mit Stahlpilz", beton, stahl, b_x=400, b_y=400, V_d=1000.0)
    p.durchstanzen("Randstütze", beton, stahl, lage="rand", form="rund", D=450, a_y=100,
                   h=300, ke="exzentrizitaet", e_y=80, V_d=500.0, q_d=12.0)
    p.durchstanzen("Eckstütze", beton, stahl, lage="ecke", V_d=80.0)
    p.durchstanzen("Randstütze in Stufe 3", beton, stahl, lage="rand", stufe="3", r_sx=0.8,
                   r_sy=0.4, m_sdx=40.0, m_sdy=60.0, V_d=150.0)
    oval = p.durchstanzen("Ovalstütze", beton, stahl, plattenart="bodenplatte", form="oval",
                          b_x=1200, b_y=300, h=400, c=40, phi_x=20, phi_y=20, stufe="3",
                          r_sx=2.0, r_sy=1.6, m_sdx=180.0, m_sdy=150.0, V_d=1400.0,
                          q_d=150.0)
    oval.aussparung([[700, 300], [1000, 300], [1000, 600], [700, 600]])
    p.durchstanzen("Wandende", beton, stahl, lage="wandende", t=250, V_d=400.0)
    p.durchstanzen("Wandecke", beton, stahl, lage="wandecke", t=250, V_d=300.0)


def _grundbrueche(p: Projekt) -> None:
    """
    Jede Lage des Grundwassers und beide Arten des Bodens: drainiert mit
    Kohäsion, geneigter Sohle, geneigtem Gelände, Auflast und dem
    Wasser im Gleitkörper, dazu eine Last, so schräg, dass die Klammer
    eines Lastneigungsfaktors unter null fällt; das Wasser über der Sohle
    und auf ihrer Höhe, dort ein langer Streifen; undrainiert flach und
    tief eingebunden, einmal so schräg belastet, dass es keinen
    Widerstand gibt.
    """
    hang = p.grundbruch("Hang", phi_k=33.0, c_k=6.0, b=1.6, L=4.0, t=0.8, t1=2.0,
                        alpha=5.0, beta=15.0, q_Ed=10.0, delta_faktor=0.67)
    hang.kombination("Normal", N_Ed=900.0, T_Ed=120.0)
    hang.kombination("Steil", N_Ed=150.0, T_Ed=300.0)
    p.grundbruch("Ufer", phi_k=30.0, b=1.5, L=1.5, t=1.0, t1=0.4).kombination(
        "Tragsicherheit", N_Ed=1200.0, T_Ed=100.0)
    p.grundbruch("Kai", phi_k=28.0, c_k=3.0, b=2.0, L=20.0, t=1.5, t1=1.5).kombination(
        "Tragsicherheit", N_Ed=2000.0, T_Ed=80.0)
    seeton = p.grundbruch("Seeton", verhalten="undrainiert", s_u=40.0, b=1.5, L=2.0,
                          t=0.8, alpha=4.0, beta=10.0)
    seeton.kombination("Normal", N_Ed=300.0, T_Ed=40.0)
    seeton.kombination("Zu schräg", N_Ed=300.0, T_Ed=200.0)
    p.grundbruch("Schacht", verhalten="undrainiert", s_u=60.0, b=1.2, L=1.2,
                 t=2.0).kombination(
        "Tragsicherheit", N_Ed=900.0, T_Ed=30.0)


def _setzungen(p: Projekt) -> None:
    """
    Das Beispiel der Tabelle 8.4 des Kapitels -- ein Bauwerk 15 × 8 m, starr,
    auf Kiessand über Ton; der Kiessand setzt sich dort nicht, hier fast
    nicht --, das mit 20 mm nicht aufgeht; dazu ein schlaffer Damm mit
    Wiederbelastung, und eine Berechnung ohne Schicht.
    """
    bauwerk = p.setzung("Bauwerk", B=8.0, L=15.0, q_E=60.0, s_zul=20.0, dz=1.0)
    bauwerk.schicht("Kiessand", d=5.0, M_E=1000.0, M_E_strich=3000.0)
    bauwerk.schicht("Ton", d=4.0, M_E=4.0, M_E_strich=24.0)
    damm = p.setzung("Damm", B=6.0, L=40.0, steifigkeit="schlaff", q_W=20.0, q_E=80.0,
                     s_zul=120.0)
    damm.schicht("Auffüllung", d=1.5, M_E=8.0, M_E_strich=30.0)
    damm.schicht("Seeton", d=6.0, M_E=5.0, M_E_strich=25.0)
    damm.schicht("Ton", d=4.0, M_E=7.0, M_E_strich=35.0)
    p.setzung("Ohne Schicht")


def _pfaehle(p: Projekt) -> None:
    """
    Jede Spielart des Pfahls. Ein Bohrpfahl im Kies, das Grundwasser teilt
    eine Schicht, die oberste trägt nicht; sein Fuss schert örtlich ab, in
    der Moräne liegt K über K_0, und er wird auch gezogen, quer mit einem
    Moment am frei drehbaren Kopf. Ein Bohrpfahl im Ton, undrainiert an
    Mantel und Fuss, der auf Druck nicht aufgeht, der Kopf eingespannt --
    sein Moment zählt dann nicht. Ein Mikropfahl mit Rohr aus einem
    statischen Versuch, ohne Schichten und darum ohne Steifigkeit, mit
    Abrostung und η_i über dem Regelwert; einer mit Vollstab aus Erfahrung,
    die Mantelreibung aus dem geotechnischen Bericht, der Spitzendruck
    eingegeben, quer leicht belastet -- und schon das trägt er nicht: ein
    gezogener Stab hält quer wenig, und am Terrain drückt er den Kies
    stärker, als dieser hält.
    """
    stahl, beton = _erstes(p, "betonstahl"), _erstes(p, "beton")
    kies = p.pfahl("Kies, örtlich", stahl=stahl, beton=beton, D=900.0, L=12.0, t_K=1.0,
                   t_w=4.0)
    kies.schicht("Auffüllung", d=2.5, gamma=19.0, mantel="eingeben", q_s=0.0, E_s=8.0)
    kies.schicht("Kies, sandig", d=7.0, gamma=21.0, phi_k=34.0, K=0.44, E_s=50.0)
    kies.schicht("Moräne", d=20.0, gamma=22.0, phi_k=36.0, c_k=5.0, K=0.6, delta_faktor=0.8,
                 E_s=100.0)
    kies.kombination("Druck", N_Ed=2000.0, H_Ed=150.0, M_Ed=80.0)
    kies.kombination("Zug", N_Ed=-300.0)

    ton = p.pfahl("Ton, undrainiert", stahl=stahl, beton=beton, D=1200.0, L=15.0, t_K=0.5,
                  t_w=1.0, abscheren="allgemein", n=16, phi_l=26.0, kopf="eingespannt")
    ton.schicht("Seeton", d=8.0, gamma=18.0, verhalten="undrainiert", s_u=25.0, alpha=0.6,
                E_s=6.0)
    ton.schicht("Ton, steif", d=20.0, gamma=20.0, verhalten="undrainiert", s_u=110.0,
                alpha=0.9, E_s=40.0)
    ton.kombination("Druck", N_Ed=6000.0, H_Ed=300.0, M_Ed=200.0)

    rohr = p.pfahl("Mikropfahl, Versuch", stahl=stahl, art="mikropfahl", D=200.0, L=8.0,
                   t_K=0.5, grundlage="statisch", eta_a=1.0, R_ak=900.0, R_ak_zug=700.0,
                   d_a=88.9, t_r=8.0, dt=1.0, eta_i=0.9)
    rohr.kombination("Druck", N_Ed=450.0)
    rohr.kombination("Zug", N_Ed=-380.0)

    stab = p.pfahl("Mikropfahl, Stab", stahl=stahl, art="mikropfahl", D=150.0, L=6.0,
                   t_K=0.0, t_w=10.0, grundlage="erfahrung", eta_a=0.9, tragglied="stab",
                   d_a=40.0, dt=2.0, spitze="eingeben", q_b=2500.0)
    stab.schicht("Kies", d=12.0, gamma=21.0, phi_k=35.0, mantel="eingeben", q_s=120.0,
                 E_s=80.0)
    stab.kombination("Zug", N_Ed=-150.0, H_Ed=5.0)


def _gebaeude(p: Projekt) -> None:
    """
    Was das Wohnhaus des Beispiels nie zeigt. Ein Lager mit T_1 von Hand und
    ohne Wand -- die Kraefte je Geschoss bleiben ohne Verteilung --, in
    Zone Z3b auf Baugrund E, Bauwerksklasse III: in x liegt T_1 unter T_B
    (31), in y zwischen T_C und T_D (33) und ueber 4 T_C, (39) geht dort
    nicht auf. Sein Grundriss ist nicht regelmaessig und das Dach schwerer
    als das Erdgeschoss: das Verfahren gilt nicht. Ein schlanker Turm auf
    einer Winkelwand, deren y und z keine Hauptachsen sind -- in y schwingt
    er langsamer als T_D (34) --, duktil bemessen mit q = 3.0: dafuer steht
    der graue Satz zu den Waenden. Und ein Gebaeude, dessen Wand noch keinen
    Querschnitt hat: es rechnet nicht.
    """
    lager = p.gebaeude("Lager, von Hand", zone="Z3b", baugrund="E", bauwerksklasse="III",
                       q_x=2.0, schwingzeit="hand", T1_x=0.05, T1_y=1.2,
                       grundriss_regelmaessig=False)
    lager.geschoss("Halle", h=5.0, G_k=1200.0, Q_k=2000.0, psi_2=0.8)
    lager.geschoss("Dach", h=4.0, G_k=3000.0)
    winkel = _tragwand(p.freie_kennung("a"), "Winkelwand",
                       [[0, 0], [4000, 0], [4000, 250], [250, 250], [250, 2000], [0, 2000]],
                       _erstes(p, "beton"))
    p.querschnittsanalysen.append(winkel)
    turm = p.gebaeude("Turm", zone="Z2", baugrund="D", q_x=3.0, q_y=3.0)
    for i in range(1, 9):
        turm.geschoss(f"{i}. OG", h=3.0, G_k=600.0, Q_k=200.0)
    turm.wand("Kern", winkel.kennung, eta_EI=0.4)
    ohne = p.gebaeude("Wand ohne Querschnitt")
    ohne.geschoss("EG", h=3.0, G_k=1000.0)
    ohne.wand("Wand 1", "")


def _tragwand(kennung: str, name: str, ecken: list, beton: str) -> QuerschnittsanalyseEintrag:
    """Eine Wand fuer das Erdbeben: ein Polygon aus Beton, ohne Lastfall."""
    a = QuerschnittsanalyseEintrag.neu(kennung=kennung, name=name)
    a.polygon(ecken, material=beton)
    return a


def _erstes(p: Projekt, art: str) -> str:
    """Die Kennung des ersten Materials dieser Art im Projekt."""
    return next(m.kennung for m in p.materialien if m.art == art)


def charakteristisch(eintrag) -> dict:
    """Charakteristische Werte fuer jedes Material, auf das der Eintrag zeigt."""
    return {kennung: Werkstoffsatz.CHARAKTERISTISCH for kennung in eintrag.materialien()}


def _alles_einmal(p: Projekt, decke: QuerschnittEintrag,
                  analyse: QuerschnittsanalyseEintrag) -> None:
    """
    Jede Vorlage, Kennwerte von Hand, Platte und Analyse als
    Querschnitt, beide mit E_eq; jede Form der Stahlprofile um beide
    Achsen -- ohne Stab, ausser dem HEB --, das Doppel-T ohne Stab; ein
    Beton und ein Baustahl des Projekts
    und ein eigenes Material, ein weicherer Beton; ein Stab mit dem
    Material gemäss Querschnitt; Gelenke und ein Knoten, dessen Drehung
    keine Steifigkeit hat; Federn am Lager, Bettung, feste Linienlager mit
    und ohne Stab; jede Lastart, auch projiziert.
    """
    s = p.balkensystem("Alles einmal")
    beton = s.beton("b1")
    baustahl = s.baustahl(_erstes(p, "baustahl"))
    weich = s.eigenes_material("Fundamentbeton", E=15000.0, rho=2500.0)
    q = {
        "rechteck": s.querschnitt("Balken 300×500", "rechteck", b=300.0, h=500.0),
        "kreis": s.querschnitt("Rundstütze", "kreis", d=400.0),
        "kreisring": s.querschnitt("Rohr", "kreisring", D=168.3, t=10.0),
        "rechteckrohr": s.querschnitt("Hohlprofil", "rechteckrohr", b=200.0, h=300.0, t=12.5),
        "t": s.querschnitt("Plattenbalken", "t", b=1200.0, h=600.0, b_w=300.0, h_f=200.0),
        "doppel_t": s.querschnitt("Walzprofil", "doppel_t", b=300.0, h=300.0,
                                  t_f=19.0, t_w=11.0),
        "trapez": s.querschnitt("Fundamentbalken", "trapez", b_o=600.0, b_u=400.0, h=500.0),
    }
    s.querschnitt_mit_kennwerten("Von Hand", A=15000.0, I=120.0)
    # E_eq der Platte -- in x, Zug unten --, auch ohne Stab gesucht und hergeleitet.
    s.querschnitt_aus("Deckenstreifen", "platte", decke, E_eq={"M": 20.0})
    kasten = s.querschnitt_aus("Kasten", "analyse", analyse, E_eq={"N": -100.0, "M": 200.0})
    heb = s.stahlprofil("Träger", "HEB 300")
    for profil in ("HEA 200", "UPE 200", "UNP 200", "RRK 200 x 100 x 8"):
        for achse in ("y", "z"):
            s.stahlprofil(f"{profil} um {achse}", profil, achse)
    s.stahlprofil("Rundrohr", "ROR 219.1 x 8", "z")
    gebettet = s.linie((0, 0), (8, 0), querschnitt=q["rechteck"], material=beton,
                       quer="feder", k_quer=20000.0)
    stuetze = s.linie((8, 0), (8, 3), querschnitt=q["kreis"], material=beton)
    sparren = s.linie((8, 3), (12, 5), querschnitt=q["t"], material=beton)
    s.linie((12, 5), (12, 0), querschnitt=q["kreisring"], material=baustahl,
            gelenk_anfang=True, gelenk_ende=True)
    stahl = s.linie((12, 0), (15, 0), querschnitt=heb, material=baustahl,
                    gelenk_anfang=True)
    aufgelegt = s.linie((15, 0), (17, 0), querschnitt=q["trapez"], material=weich,
                        quer="fest")
    s.linie((17, 0), (17, -1), quer="fest")
    s.linie((15, 0), (15, 2), querschnitt=q["rechteckrohr"], material=baustahl)
    s.linie((15, 2), (17, 2), querschnitt=kasten, material=MATERIAL_DES_QUERSCHNITTS)
    s.lager_an((0, 0), "gelenkig", z="feder", k_z=50000.0, phi="feder", k_phi=10000.0)
    s.lager_an((12, 0), "gelenkig")
    g = s.lastfall("Eigengewicht", eigengewicht=True)
    w = s.lastfall("Schnee und Wind")
    s.stablast(g, gebettet, wert=5.0, wert_b=15.0)
    s.stablast(g, gebettet, art="linienmoment", wert=2.0)
    s.stablast(g, sparren, wert=4.0)
    s.stablast(g, aufgelegt, wert=10.0)
    s.knotenlast(g, (8, 3), 5.0, art="moment")
    s.stablast(w, sparren, wert=3.0, projiziert=True)
    s.stablast(w, stuetze, art="einzellast", wert=8.0, stelle=50.0, richtung="quer")
    s.stablast(w, stahl, art="moment", wert=4.0, stelle=50.0)
    s.knotenlast(w, (8, 3), 10.0, richtung="waagrecht")
    tragsicherheit = s.kombination("Tragsicherheit", (g, 1.35), (w, 1.5))
    # Jede Grösse einmal, eine auch für einen Lastfall allein.
    for groesse in DIAGRAMMGROESSEN:
        s.diagramm(tragsicherheit, groesse)
    s.diagramm(w, "M")


def _beweglich(p: Projekt) -> None:
    """Ein Träger auf zwei Rollen: nichts hält ihn waagrecht -- eine Meldung statt einer Zahl."""
    s = p.balkensystem("Beweglich")
    traeger = s.linie((0, 0), (5, 0), querschnitt=s.querschnitt("Rechteck", "rechteck"),
                      material=s.beton("b1"))
    s.lager_an((0, 0), "verschieblich")
    s.lager_an((5, 0), "verschieblich")
    s.stablast(s.lastfall("Last"), traeger, wert=10.0)


def _raumrahmen(p: Projekt, decke: QuerschnittEintrag,
                analyse: QuerschnittsanalyseEintrag) -> None:
    """
    Ein Rahmen im Raum, der alles einmal braucht: Stützen aus Beton, Stahl
    und Holz, je mit anderem Lager -- eingespannt, gelenkig mit Drehfeder,
    verschieblich und in y gehalten --, Riegel in x und y, einer gedreht und
    einer mit Gelenk, ein geneigter Kragarm, ein gebetteter Fundamentbalken;
    Querschnitte nach Vorlage, als Profil, von Hand, aus einer Platte mit
    E_eq und aus einer Querschnittsanalyse, deren I_T sie dafür rechnet --
    beide mit dem Material gemäss Querschnitt --, ein eigenes Material mit
    G; Lasten in jeder Richtung, Torsion, projiziert, an Knoten.
    """
    s = p.balkensystem3d("Raumrahmen")
    beton = s.beton("b1")
    stahl = s.baustahl(_erstes(p, "baustahl"))
    holz = s.eigenes_material("Brettschichtholz", E=11500.0, rho=480.0, G=650.0)
    balken = s.querschnitt("Balken 300×500", "rechteck", b=300.0, h=500.0)
    heb = s.stahlprofil("Stütze", "HEB 300")
    hand = s.querschnitt_mit_kennwerten("Holzstütze", A=40000.0, I_y=133.3, I_z=133.3,
                                        I_T=225.0)
    streifen = s.querschnitt_aus("Deckenstreifen", "platte", decke, E_eq={"M": 20.0})
    kasten = s.querschnitt_aus("Kasten", "analyse", analyse)
    s.linie((0, 0, 0), (0, 0, 3), querschnitt=balken, material=beton)
    s.linie((6, 0, 0), (6, 0, 3), querschnitt=heb, material=stahl, drehung=90.0)
    s.linie((0, 4, 0), (0, 4, 3), querschnitt=hand, material=holz)
    riegel_x = s.linie((0, 0, 3), (6, 0, 3), querschnitt=heb, material=stahl, gelenk_ende=True)
    riegel_y = s.linie((0, 0, 3), (0, 4, 3), querschnitt=balken, material=beton, drehung=30.0)
    kragarm = s.linie((6, 0, 3), (6, 2, 4), querschnitt=heb, material=stahl)
    s.linie((0, 4, 3), (6, 0, 3), querschnitt=kasten, material=MATERIAL_DES_QUERSCHNITTS)
    s.linie((0, 4, 3), (-2, 4, 3), querschnitt=streifen, material=MATERIAL_DES_QUERSCHNITTS)
    fundament = s.linie((0, 0, 0), (6, 0, 0), querschnitt=balken, material=beton,
                        quer_z="feder", k_quer_z=20000.0, laengs="feder", k_laengs=5000.0)
    s.lager_an((0, 0, 0), "eingespannt")
    s.lager_an((6, 0, 0), "gelenkig", phi_z="feder", k_phi_z=5000.0)
    s.lager_an((0, 4, 0), "verschieblich", y="fest", x="feder", k_x=10000.0)
    g = s.lastfall("Eigengewicht", eigengewicht=True)
    q = s.lastfall("Nutzlast und Wind")
    s.stablast(g, riegel_x, wert=8.0)
    s.stablast(q, riegel_x, wert=5.0, wert_b=10.0, richtung="z")
    s.stablast(q, riegel_y, wert=3.0, richtung="quer_y")
    s.stablast(q, kragarm, wert=4.0, projiziert=True)
    s.stablast(q, kragarm, art="einzellast", wert=6.0, stelle=100.0, richtung="quer_z")
    s.stablast(q, riegel_x, art="moment", wert=2.0, stelle=50.0, richtung="laengs")
    s.stablast(q, riegel_y, art="linienmoment", wert=1.0, richtung="x")
    s.stablast(q, fundament, art="einzellast", wert=12.0, stelle=50.0, richtung="laengs")
    s.knotenlast(q, (0, 4, 3), 5.0, richtung="x")
    s.knotenlast(q, (6, 0, 3), 3.0, richtung="y")
    s.knotenlast(g, (0, 0, 3), 4.0, art="moment", richtung="z")
    tragsicherheit = s.kombination("Tragsicherheit", (g, 1.35), (q, 1.5))
    # Jede Grösse einmal, eine auch für einen Lastfall allein.
    for groesse in DIAGRAMMGROESSEN3D:
        s.diagramm(tragsicherheit, groesse)
    s.diagramm(q, "T")


def _kastentraeger(kennung: str) -> QuerschnittsanalyseEintrag:
    a = QuerschnittsanalyseEintrag(
        kennung=kennung, name="Kastenträger",
        rechenarten={"b1": "block"},
        laengszugkraft=True, duktilitaet=True, sproede=True,
        rissanforderung="erhoeht", zwaengung=True, zwaengung_begrenzt=True,
        zwaengung_biegung=True, zwaengung_biegung_kriechzahl=1.0)
    a.polygon([[0, 0], [800, 0], [800, 600], [0, 600]], material="b1")
    a.polygon([[150, 150], [650, 150], [650, 450], [150, 450]])
    a.stablinie([50, 50], [750, 50], art="teilung", durchmesser=16, teilung=150,
                stahl="s1")
    a.stablinie([60, 550], [740, 550], art="anzahl", durchmesser=12, anzahl=4,
                starteisen=False, endeisen=False, stahl="s1")
    a.stablinie([40, 150], [40, 450], art="flaeche", flaeche=400, stahl="s1")
    a.stablinie([110, 150], [110, 450], art="flaeche", verschmiert="staebe",
                durchmesser=10, teilung=200, stahl="s1")
    a.stab(760, 300, durchmesser=20, stahl="s1")
    for e, f in (([75, 75], [725, 75]), ([725, 75], [725, 525]),
                 ([725, 525], [75, 525]), ([75, 525], [75, 75])):
        a.schubwand(e, f, dicke=150, durchmesser=10, teilung=150, schnitte=1, stahl="s1")
    a.lastfall("Feld", M_y_Ed=300.0, V_z_Ed=250.0, T_Ed=60.0)
    a.lastfall("Schief", N_Ed=-1500.0, M_y_Ed=250.0, M_z_Ed=150.0, V_y_Ed=100.0)
    # Spannung-Dehnung-Analysen, je Zugseite: ein Bild und eine Linie mit
    # ihrer Herleitung -- um z unter Druck, und der Modul unter Zug bei
    # negativem Moment, wo der gedrückte Rand reisst.
    a.spannungsfall("Schnitt", art="schnittgroessen", N_Ed=-500.0, M_Ed=200.0)
    a.spannungsfall("Seitlich", art="moment_kruemmung", N_Ed=-500.0, richtung="links",
                    kriechzahl=1.0)
    a.spannungsfall("Zugsteifigkeit", art="normalkraft_emodul", M_Ed=-50.0,
                    werkstoffsaetze=charakteristisch(a), rechenarten={"b1": "block"})
    # Die Stahlspannungen: quasi-ständig aus der Tragsicherheit und ein
    # eigener Fall, häufig ein schiefer -- die Nulllinie dreht.
    a.quasistaendig.aus_tragsicherheit = True
    a.quasistaendig.lastfall("Dauer", N_Ed=-300.0, M_y_Ed=120.0, M_z_Ed=60.0)
    a.haeufig.lastfall("Häufig schief", N_Ed=-500.0, M_y_Ed=200.0, M_z_Ed=100.0)
    return a


def _stuetze(kennung: str) -> QuerschnittsanalyseEintrag:
    a = QuerschnittsanalyseEintrag(
        kennung=kennung, name="Stütze",
        werkstoffsaetze={"b1": "charakteristisch", "s1": "charakteristisch"},
        einachsig=True, zwaengung=True)
    a.polygon([[0, 0], [400, 0], [400, 400], [0, 400]], material="b1")
    for z in (50, 350):
        a.stablinie([50, z], [350, z], art="anzahl", durchmesser=20, anzahl=3, stahl="s1")
    a.lastfall("Druck", N_Ed=-2500.0, M_y_Ed=120.0)
    a.lastfall("Zug", N_Ed=400.0)
    a.spannungsfall("Randdehnungen", art="dehnungen", eps_oben=-2.0, eps_unten=5.0,
                    richtung="oben")
    a.spannungsfall("Biegesteifigkeit", art="moment_emodul", N_Ed=-800.0,
                    richtung="oben", werkstoffsaetze=charakteristisch(a))
    # Quasi-ständig präzise, wie vorgegeben: σ_s,adm ist bei normaler
    # Anforderung f_yk.
    a.quasistaendig.lastfall("Dauer", N_Ed=-600.0, M_y_Ed=80.0)
    # Knicken unten und seitlich, die Verformung mit Kriechen.
    a.knicken_wahl_verformung.kriechzahl = 1.5
    a.knickfall("Stütze", N_Ed=-1500.0, M_Ed_1=30.0, laenge=4.0)
    a.knickfall("Seitlich", N_Ed=-1200.0, M_Ed_1=10.0, laenge=5.0, knicklaenge=3.5,
                richtung="links")
    return a


def _spannbeton(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Ein Träger 400 × 800 mm mit Betonstahl oben und unten und drei
    Spanngliedern aus Y1860, je eines in jedem Gesetz: vier Litzen mit
    Vordehnung und Verbund, die Spannungen nach Vorgabe; zwei ohne Verbund,
    die Spannungen eingegeben; zwei schlaff mit Restfestigkeit. Die
    Duktilität sieht Spannstahl in der Zugzone, sprödes Versagen und
    Zwängung messen am Rissmoment mit Vorspannung, die Stahlspannung gilt
    dem Betonstahl, und die Linie beginnt bei der Krümmung, die die
    Vorspannung allein weckt. Am Auflager trägt das erste Glied, um 5°
    geneigt, die Querkraft mit; das zweite, um -4° geneigt und neben dem
    Schwerpunkt, wirkt ihr entgegen und dreht den Kasten der Schubwände; das
    schlaffe zählt seine Neigung nicht.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Spannbeton", duktilitaet=True,
                                   sproede=True, zwaengung_biegung=True)
    a.polygon([[0, 0], [400, 0], [400, 800], [0, 800]], material="b1")
    a.stablinie([50, 50], [350, 50], art="anzahl", durchmesser=14, anzahl=4, stahl="s1")
    a.stablinie([50, 750], [350, 750], art="anzahl", durchmesser=12, anzahl=3, stahl="s1")
    a.spannglied(200, 120, stahl="sp1", durchmesser=15.7, anzahl=4, neigung=5.0)
    a.spannglied(120, 160, stahl="sp1", durchmesser=15.3, anzahl=2, verbund="ohne",
                 sigma_p0=1350.0, sigma_pinf=1100.0, neigung=-4.0)
    a.spannglied(280, 160, stahl="sp1", durchmesser=12.9, anzahl=2, wirkung="restfestigkeit",
                 neigung=3.0)
    ecken = [[50, 50], [350, 50], [350, 750], [50, 750]]
    for von, bis in zip(ecken, ecken[1:] + ecken[:1]):
        a.schubwand(von, bis, dicke=100.0, durchmesser=10.0, teilung=150.0, schnitte=1,
                    stahl="s1")
    a.lastfall("Feld", M_y_Ed=600.0)
    a.lastfall("Auflager", M_y_Ed=150.0, V_z_Ed=450.0)
    a.quasistaendig.lastfall("Dauer", M_y_Ed=550.0)
    a.spannungsfall("Biegung", art="moment_kruemmung")
    return a


def _stahltraeger(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Ein IPE 600 aus S355, zweiachsig, jede Klasse einmal (SIA 263:2013):
    im Feld plastisch, schief, mit einer Querkraft über der Hälfte von V_Rd,
    die dem Steg nimmt, und mit Torsion, die nur ein Hinweis ist; mit mehr
    Druck nach (54), mit noch mehr am wirksamen Querschnitt nach (60), und
    reiner Druck nach (55).

    Dazu Knicken und Kippen, wieder jede Klasse: im Feld nach (50) und (51),
    mit Kippen unter einem dreieckigen Moment; mit Druck in Klasse 3; am
    wirksamen Querschnitt nach (62) und (63); reiner Druck nach 5.3.8; und
    seitlich gehalten nur (50).
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Stahlträger")
    a.profil(0, 0, "IPE 600", stahl="st1")
    a.lastfall("Feld", N_Ed=-1000.0, M_y_Ed=300.0, M_z_Ed=20.0, V_z_Ed=900.0, T_Ed=2.0)
    a.lastfall("Druck mit Biegung", N_Ed=-3000.0, M_y_Ed=100.0)
    a.lastfall("Beulen", N_Ed=-4000.0, M_y_Ed=50.0)
    a.lastfall("Druck", N_Ed=-4000.0)
    kurz = {"L_K_y": 6.0, "L_K_z": 1.5, "L_D": 1.5}
    a.stabilitaetsfall("Feld", N_Ed=-1000.0, M_y_Ed=300.0, M_z_Ed=20.0, psi_y=0.0,
                       L_K_y=6.0, L_K_z=3.0, L_D=3.0)
    a.stabilitaetsfall("Druck mit Biegung", N_Ed=-3000.0, M_y_Ed=100.0, **kurz)
    a.stabilitaetsfall("Beulen", N_Ed=-3500.0, M_y_Ed=30.0, **{**kurz, "L_K_y": 3.0})
    a.stabilitaetsfall("Druck", N_Ed=-3000.0, **kurz)
    a.stabilitaetsfall("Gehalten", N_Ed=-1000.0, M_y_Ed=300.0, L_K_y=6.0, L_K_z=0.0, L_D=0.0)
    return a
