# this script takes fetched data and generates html
import csv
import jinja2
import os
from collections import Counter


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


districts = {}
boroughs = {}


class Region:
    def __init__(self):
        self.results = Counter()
        self.statistics = Counter()
        self.subregions = {}

    def process_csv_row(self, row):
        self.results += Counter({x: int(row[x]) for x in list(row.keys())[12:]})
        self.statistics += Counter({x: int(row[x]) for x in list(row.keys())[7:12]})
        self.push_down(row)

    def push_down(self, row):
        pass

    def generate(self):
        template.stream(results=self.results, statistics=self.statistics,
                        links=self.get_parent_links(), me=self.__str__(),
                        children=[subregion.get_hyperlink() for subregion in
                                  self.subregions.values()]).dump(
            './webpages/' + self.get_link())
        for subregion in self.subregions.values():
            subregion.generate()

    def get_hyperlink(self):
        return self.__str__(), '../' + self.get_link()

    def get_link(self):
        pass


class Country(Region):
    def __init__(self):
        super().__init__()

    def push_down(self, row):
        for k, state in self.subregions.items():
            if row['Nr okr.'] in state.subregions:
                state.process_csv_row(row)
                break

    def add_district_info(self, row):
        state = row['wojewodztwo']
        if state not in self.subregions:
            self.subregions[state] = State(state)
        districts[row['nr']] = District(row['nr'], row['siedziba'])
        self.subregions[state].subregions[row['nr']] = districts[row['nr']]

    def get_link(self):
        return 'kraj/polska.html'

    def get_parent_links(self):
        return []

    def __str__(self):
        return "Polska"


class State(Region):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def push_down(self, row):
        self.subregions[row['Nr okr.']].state = self
        self.subregions[row['Nr okr.']].process_csv_row(row)

    def get_link(self):
        return 'wojewodztwa/' + self.name + '.html'

    def get_parent_links(self):
        return []

    def __str__(self):
        return self.name


class District(Region):
    def __init__(self, nr, headquarters):
        super().__init__()
        self.nr = nr
        self.headquarters = headquarters

    def push_down(self, row):
        if row['Kod gminy'] not in self.subregions:
            if row['Kod gminy'] not in boroughs:
                boroughs[row['Kod gminy']] = Borough(row['Kod gminy'], row['Gmina'])
            borough = boroughs[row['Kod gminy']]
            self.subregions[row['Kod gminy']] = borough
            borough.districts.append(self)
        self.subregions[row['Kod gminy']].process_csv_row(row)

    def get_link(self):
        return 'okregi/' + self.nr + '.html'

    def get_parent_links(self):
        return [self.state.get_hyperlink()]

    def __str__(self):
        return 'okrąg nr ' + self.nr + ' (' + self.headquarters + ')'


class Borough(Region):
    def __init__(self, nr, name):
        super().__init__()
        self.districts = []
        self.nr = nr
        self.name = name

    def push_down(self, row):
        ambit = Ambit(Ambit.max_id, row['Adres'])
        self.subregions[Ambit.max_id] = ambit
        ambit.borough = self
        ambit.district = districts[row['Nr okr.']]
        Ambit.max_id += 1
        ambit.process_csv_row(row)

    def get_link(self):
        return 'gminy/' + self.nr + '.html'

    def get_parent_links(self):
        links = self.districts[0].get_parent_links()
        for district in self.districts:
            links += [district.get_hyperlink()]
        return links

    def __str__(self):
        return self.name


class Ambit(Region):
    max_id = 0

    def __init__(self, id, adres):
        super().__init__()
        self.id = id
        self.adres = adres

    def push_down(self, row):
        pass

    def get_link(self):
        return 'obwody/' + str(self.id) + '.html'

    def get_parent_links(self):
        return self.district.get_parent_links() + [self.district.get_hyperlink()] + \
               [self.borough.get_hyperlink()]

    def __str__(self):
        return self.adres


def process_csv(file, row_function):
    with open(file, 'r') as csvfile:
        read = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in read:
            row_function(row)


create_directories_for_html()
poland = Country()
process_csv('data/districts.csv', poland.add_district_info)
process_csv('data/data.csv', poland.process_csv_row)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
template_file = 'base.html'
template = templateEnv.get_template(template_file)
poland.generate()
