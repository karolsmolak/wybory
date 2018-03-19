from django.db import models
from django.db.models import Sum


class Wynik(models.Model):
    podmiot = models.CharField(max_length=30)
    wynik = models.IntegerField()
    obwod = models.ForeignKey('Obwod', on_delete=models.CASCADE, related_name='wyniki')
    available_types = (
        ('k', 'kandydat'),
        ('s', 'statystyka')
    )
    rodzaj = models.CharField(max_length=1, choices=available_types)

    class Meta:
        unique_together = ('podmiot', 'obwod')

    def __str__(self):
        return self.podmiot + " " + str(self.wynik)


class Region:
    def get_results_by_type(self, type):
        pass

    def get_candidate_results(self):
        return self.get_results_by_type('kandydat')

    def get_statistics(self):
        return self.get_results_by_type('statystyka')


class Kraj(Region):

    def dodaj_info_o_okregach(self, row):
        wojewodztwo, created = Wojewodztwo.objects.get_or_create(nazwa=row['wojewodztwo'])
        Okrag.objects.create(nr=row['nr'], siedziba=row['siedziba'], wojewodztwo=wojewodztwo)

    def get_html(self):
        return '/wyniki/kraj'

    def get_results_by_type(self, type):
        return {wynik['podmiot']: wynik['val'] for wynik in
                Wynik.objects.all().filter(rodzaj=type).values(
                    'podmiot').annotate(val=Sum('wynik'))}

    def get_links(self):
        return []

    def get_child_links(self):
        return {wojewodztwo.__str__(): wojewodztwo.get_html() for wojewodztwo in
                Wojewodztwo.objects.all()}

    def __str__(self):
        return "Polska"


class Wojewodztwo(models.Model, Region):
    nazwa = models.CharField(max_length=25, primary_key=True)

    def get_html(self):
        return '/wyniki/wojewodztwo/' + self.nazwa

    def get_results_by_type(self, type):
        return {wynik['podmiot']: wynik['val'] for wynik in
                Wynik.objects.filter(rodzaj=type, obwod__in=[obwod for okrag in self.okregi.all() for obwod in
                                                             okrag.obwody.all()]).values(
                    'podmiot').annotate(val=Sum('wynik'))}

    def get_links(self):
        return []

    def get_child_links(self):
        return {okrag.__str__(): okrag.get_html() for okrag in self.okregi.all()}

    def __str__(self):
        return self.nazwa


class Okrag(models.Model, Region):
    wojewodztwo = models.ForeignKey(Wojewodztwo, on_delete=models.CASCADE, related_name='okregi')
    nr = models.IntegerField(primary_key=True)
    siedziba = models.CharField(max_length=25)

    def get_html(self):
        return '/wyniki/okrag/' + str(self.nr)

    def get_results_by_type(self, type):
        return {wynik['podmiot']: wynik['val'] for wynik in
                Wynik.objects.filter(rodzaj=type).filter(
                    obwod__in=self.obwody.all()).values('podmiot').annotate(val=Sum('wynik'))}

    def get_links(self):
        return [(self.wojewodztwo.nazwa, self.wojewodztwo.get_html())]

    def get_child_links(self):
        return {gmina.__str__(): gmina.get_html() for gmina in self.gminy.all()}

    def __str__(self):
        return 'okrag nr ' + str(self.nr) + ' (' + self.siedziba + ')'


class Gmina(models.Model, Region):
    okrag = models.ManyToManyField(Okrag, related_name='gminy')
    kod_gminy = models.CharField(max_length=7, primary_key=True)
    nazwa = models.CharField(max_length=30)

    def get_results_by_type(self, type):
        return {wynik['podmiot']: wynik['val'] for wynik in
                Wynik.objects.filter(obwod__in=self.obwody.all(), rodzaj=type).values('podmiot').annotate(
                    val=Sum('wynik'))}

    def get_html(self):
        return '/wyniki/gmina/' + self.kod_gminy

    def get_links(self):
        wojewodztwo = self.okrag.all()[0].wojewodztwo
        links = [(wojewodztwo.__str__(), wojewodztwo.get_html())]
        links = links + [(okrag.__str__(), okrag.get_html()) for okrag in self.okrag.all()]
        return links

    def get_child_links(self):
        return {obwod.__str__(): obwod.get_html() for obwod in self.obwody.all()}

    def __str__(self):
        return self.nazwa


class Obwod(models.Model, Region):
    adres = models.CharField(max_length=100)
    gmina = models.ForeignKey(Gmina, on_delete=models.CASCADE, related_name='obwody')
    okrag = models.ForeignKey(Okrag, on_delete=models.CASCADE, related_name='obwody')

    def get_html(self):
        return '/wyniki/obwod/' + str(self.pk)

    def __str__(self):
        return self.adres

    def get_links(self):
        links = self.gmina.get_links()
        links.append((self.gmina.__str__(), self.gmina.get_html()))
        return links

    def get_child_links(self):
        return {}

    def get_results_by_type(self, rodzaj):
        return {wynik['podmiot']: wynik['wynik'] for wynik in self.wyniki.all().filter(rodzaj=rodzaj).values()}

    def modify_result(self, subject, result):
        previous_result = self.wyniki.get(podmiot=subject)
        previous_result.wynik = result
        previous_result.save(update_fields=['wynik'])
