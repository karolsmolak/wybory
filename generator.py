# this script takes fetched data and generates html
import csv
import jinja2
import os


def create_directories_for_html():
    if not os.path.exists('./webpages/kraj'):
        os.mkdir('./webpages/kraj')
    if not os.path.exists('./webpages/wojewodztwa'):
        os.mkdir('./webpages/wojewodztwa')
    if not os.path.exists('./webpages/okregi'):
        os.mkdir('./webpages/okregi')
    if not os.path.exists('./webpages/gminy'):
        os.mkdir('./webpages/gminy')
    if not os.path.exists('./webpages/obwody'):
        os.mkdir('./webpages/obwody')


class Kraj:
    def __init__(self):
        self.wojewodztwa = {}
        self.wynik = Wynik({})

    def propaguj(self, row):
        self.wynik.add({x: row[x] for x in list(row.keys())[7:]})
        for k, wojewodztwo in self.wojewodztwa.items():
            if row['Nr okr.'] in wojewodztwo.okregi:
                wojewodztwo.propaguj(row)
                break

    def generuj(self):
        template.stream(wyniki=self.wynik.wyniki_kandydatow(), statystyki=self.wynik.statystyki(),
                        dzieci={wojewodztwo.nazwa: wojewodztwo.get_html() for wojewodztwo in self.wojewodztwa.values()},
                        gdzie_jesteśmy='Polska').dump('./webpages/kraj/polska.html')
        linki = {}
        for wojewodztwo in self.wojewodztwa.values():
            wojewodztwo.generuj(linki)
            del linki[wojewodztwo.nazwa]


class Wojewodztwo:
    def __init__(self, nazwa):
        self.okregi = {}
        self.wynik = Wynik({})
        self.nazwa = nazwa

    def propaguj(self, row):
        self.wynik.add({x: row[x] for x in list(row.keys())[7:]})
        self.okregi[row['Nr okr.']].propaguj(row)

    def generuj(self, linki_do_rodziców):
        template.stream(wyniki=self.wynik.wyniki_kandydatow(), statystyki=self.wynik.statystyki(),
                        linki=linki_do_rodziców,
                        dzieci={okrag.to_string(): okrag.get_html() for okrag in self.okregi.values()},
                        gdzie_jesteśmy=self.nazwa).dump(
            './webpages/wojewodztwa/' + self.nazwa + '.html')
        linki_do_rodziców[self.nazwa] = self.get_html()
        for okrag in self.okregi.values():
            okrag.generuj(linki_do_rodziców)
            del linki_do_rodziców[okrag.to_string()]

    def get_html(self):
        return '../wojewodztwa/' + self.nazwa + '.html'


class Okrag:
    def __init__(self, nr, siedziba, wojewodztwo):
        self.nr = nr
        self.siedziba = siedziba
        self.wojewodztwo = wojewodztwo
        self.wynik = Wynik({})
        self.gminy = {}

    def propaguj(self, row):
        self.wynik.add({x: row[x] for x in list(row.keys())[7:]})
        if row['Kod gminy'] not in self.gminy:
            self.gminy[row['Kod gminy']] = Gmina(row['Kod gminy'], self.nr, row['Gmina'])
        self.gminy[row['Kod gminy']].propaguj(row)

    def generuj(self, linki_do_rodziców):
        template.stream(wyniki=self.wynik.wyniki_kandydatow(), statystyki=self.wynik.statystyki(),
                        linki=linki_do_rodziców, gdzie_jesteśmy=self.to_string(),
                        dzieci={gmina.nazwa: gmina.get_html() for gmina in self.gminy.values()}).dump(
            './webpages/okregi/' + self.nr + '.html'
        )
        linki_do_rodziców[self.to_string()] = self.get_html()
        for gmina in self.gminy.values():
            gmina.generuj(linki_do_rodziców)
            del linki_do_rodziców[gmina.nazwa]

    def get_html(self):
        return '../okregi/' + self.nr + '.html'

    def to_string(self):
        return 'okrag nr ' + self.nr + ' (' + self.siedziba + ')'


class Gmina:
    def __init__(self, kod_gminy, nr_okregu, nazwa):
        self.nr_okregu = nr_okregu
        self.kod_gminy = kod_gminy
        self.nazwa = nazwa
        self.obwody = {}
        self.wynik = Wynik({})

    def propaguj(self, row):
        self.wynik.add({x: row[x] for x in list(row.keys())[7:]})
        self.obwody[Obwod.max_id] = Obwod(Obwod.max_id, row['Kod gminy'], row['Adres'])
        self.obwody[Obwod.max_id].propaguj(row)
        Obwod.max_id += 1

    def generuj(self, linki_do_rodziców):
        template.stream(wyniki=self.wynik.wyniki_kandydatow(), statystyki=self.wynik.statystyki(),
                        linki=linki_do_rodziców,
                        gdzie_jesteśmy=self.nazwa,
                        dzieci={obwod.adres: obwod.get_html() for obwod in self.obwody.values()}).dump(
            './webpages/gminy/' + self.kod_gminy + '.html')
        linki_do_rodziców[self.nazwa] = self.get_html()
        for obwod in self.obwody.values():
            obwod.generuj(linki_do_rodziców)

    def get_html(self):
        return '../gminy/' + self.kod_gminy + '.html'


class Obwod:
    max_id = 0

    def __init__(self, id, kod_gminy, adres):
        self.id = id
        self.kod_gminy = kod_gminy
        self.adres = adres
        self.wynik = Wynik({})

    def propaguj(self, row):
        self.wynik.add({x: row[x] for x in list(row.keys())[7:]})

    def generuj(self, linki_do_rodziców):
        template.stream(wyniki=self.wynik.wyniki_kandydatow(), statystyki=self.wynik.statystyki(),
                        linki=linki_do_rodziców, gdzie_jesteśmy=self.adres).dump(
            './webpages/obwody/' + str(self.id) + '.html')

    def get_html(self):
        return '../obwody/' + str(self.id) + '.html'


class Wynik:
    def __init__(self, wyniki):
        self.wyniki = wyniki

    def add(self, podwynik):
        for k, v in podwynik.items():
            if k in self.wyniki:
                self.wyniki[k] += int(v)
            else:
                self.wyniki[k] = int(v)

    def wyniki_kandydatow(self):
        return {x: self.wyniki[x] for x in list(self.wyniki.keys())[5:]}

    def statystyki(self):
        return {x: self.wyniki[x] for x in list(self.wyniki.keys())[:5]}


polska = Kraj()

with open('data/districts.csv', 'r') as csvfile:
    read = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in read:
        wojewodztwo = row['wojewodztwo']
        if wojewodztwo not in polska.wojewodztwa:
            polska.wojewodztwa[wojewodztwo] = Wojewodztwo(wojewodztwo)
        polska.wojewodztwa[wojewodztwo].okregi[row['nr']] = Okrag(
            row['nr'], row['siedziba'], wojewodztwo)

with open('data/data.csv', 'r') as csvfile:
    read = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in read:
        polska.propaguj(row)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = 'base.html'
template = templateEnv.get_template(TEMPLATE_FILE)

create_directories_for_html()
polska.generuj()
