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


class Region:
    def __init__(self):
        self.wynik = Wynik({})
        self.podregiony = {}

    def process_csv_row(self, row):
        self.wynik.add({x: row[x] for x in list(row.keys())[7:]})
        self.push_down(row)

    def push_down(self):
        pass

    def generate(self, linki_do_rodzicow):
        template.stream(wyniki=self.wynik.wyniki_kandydatow(), statystyki=self.wynik.statystyki(),
                        linki=linki_do_rodzicow, gdzie_jesteśmy=self.__str__(),
                        dzieci={podregion.__str__(): '../' + podregion.get_html() for podregion in self.podregiony.values()}).dump(
            './webpages/' + self.get_html())
        if self.__str__() != "Polska":
            linki_do_rodzicow[self.__str__()] = '../' + self.get_html()
        for podregion in self.podregiony.values():
            podregion.generate(linki_do_rodzicow)
            del linki_do_rodzicow[podregion.__str__()]

    def get_html(self):
        pass


class Kraj(Region):
    def __init__(self):
        super().__init__()

    def push_down(self, row):
        for k, wojewodztwo in self.podregiony.items():
            if row['Nr okr.'] in wojewodztwo.podregiony:
                wojewodztwo.process_csv_row(row)
                break

    def dodaj_info_o_okręgach(self, row):
        wojewodztwo = row['wojewodztwo']
        if wojewodztwo not in self.podregiony:
            self.podregiony[wojewodztwo] = Wojewodztwo(wojewodztwo)
        self.podregiony[wojewodztwo].podregiony[row['nr']] = Okrag(row['nr'], row['siedziba'])

    def get_html(self):
        return 'kraj/polska.html'

    def __str__(self):
        return "Polska"


class Wojewodztwo(Region):
    def __init__(self, nazwa):
        super().__init__()
        self.nazwa = nazwa

    def push_down(self, row):
        self.podregiony[row['Nr okr.']].process_csv_row(row)

    def get_html(self):
        return 'wojewodztwa/' + self.nazwa + '.html'

    def __str__(self):
        return self.nazwa


class Okrag(Region):
    def __init__(self, nr, siedziba):
        super().__init__()
        self.nr = nr
        self.siedziba = siedziba

    def push_down(self, row):
        if row['Kod gminy'] not in self.podregiony:
            self.podregiony[row['Kod gminy']] = Gmina(row['Kod gminy'], row['Gmina'])
        self.podregiony[row['Kod gminy']].process_csv_row(row)

    def get_html(self):
        return 'okregi/' + self.nr + '.html'

    def __str__(self):
        return 'okrag nr ' + self.nr + ' (' + self.siedziba + ')'


class Gmina(Region):
    def __init__(self, kod_gminy, nazwa):
        super().__init__()
        self.kod_gminy = kod_gminy
        self.nazwa = nazwa

    def push_down(self, row):
        self.podregiony[Obwod.max_id] = Obwod(Obwod.max_id, row['Adres'])
        self.podregiony[Obwod.max_id].process_csv_row(row)
        Obwod.max_id += 1

    def get_html(self):
        return 'gminy/' + self.kod_gminy + '.html'

    def __str__(self):
        return self.nazwa


class Obwod(Region):
    max_id = 0

    def __init__(self, id, adres):
        super().__init__()
        self.id = id
        self.adres = adres

    def push_down(self, row):
        pass

    def get_html(self):
        return 'obwody/' + str(self.id) + '.html'

    def __str__(self):
        return self.adres


class Wynik:
    def __init__(self, wyniki):
        self.wyniki = wyniki

    def add(self, wynik_podregionu):
        for k, v in wynik_podregionu.items():
            if k in self.wyniki:
                self.wyniki[k] += int(v)
            else:
                self.wyniki[k] = int(v)

    def wyniki_kandydatow(self):
        return {x: self.wyniki[x] for x in list(self.wyniki.keys())[5:]}

    def statystyki(self):
        return {x: self.wyniki[x] for x in list(self.wyniki.keys())[:5]}


def process_csv(file, row_function):
    with open(file, 'r') as csvfile:
        read = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in read:
            row_function(row)


create_directories_for_html()
polska = Kraj()
process_csv('data/districts.csv', polska.dodaj_info_o_okręgach)
process_csv('data/data.csv', polska.process_csv_row)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
template_file = 'base.html'
template = templateEnv.get_template(template_file)
polska.generate({})
