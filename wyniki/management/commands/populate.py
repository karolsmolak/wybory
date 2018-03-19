# this script takes fetched data and generates html
import csv
import wyniki.models as modele
from django.db import transaction
from django.core.management.base import BaseCommand


def process_csv_row(row):
    okrag = modele.Okrag.objects.get(nr=int(row['Nr okr.']))
    gmina, created = modele.Gmina.objects.get_or_create(kod_gminy=row['Kod gminy'], nazwa=row['Gmina'])
    if not okrag.gminy.filter(kod_gminy=row['Kod gminy']).exists():
        okrag.gminy.add(gmina)
    obwod = modele.Obwod.objects.create(adres=row['Adres'], gmina=gmina, okrag=okrag)
    modele.Wynik.objects.bulk_create([
        modele.Wynik(podmiot=key, wynik=int(value), obwod=obwod,
                     rodzaj='statystyka' if i < 6 else 'kandydat') for i, (key, value) in
        enumerate(list(row.items())[7:])
    ])


@transaction.atomic
def process_csv(file, row_function):
    with open(file, 'r') as csvfile:
        read = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in read:
            row_function(row)


class Command(BaseCommand):
    def handle(self, *args, **options):
        polska = modele.Kraj()
        process_csv('data/districts.csv', polska.dodaj_info_o_okregach)
        process_csv('data/data.csv', process_csv_row)
