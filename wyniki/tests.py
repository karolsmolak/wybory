from django.test import TestCase
import wyniki.models as models

wojewodztwa = [
    'woj1',
    'woj2'
]

okregi = {
    1: 'woj1',
    2: 'woj1',
    3: 'woj2'
}

gminy = {
    1: [1],
    2: [1, 2],
    3: [3]
}

obwody = {
    'obw1': (1, 1, [('a', 'kandydat', 6), ('b', 'kandydat', 3), ('c', 'statystyka', 4)]),
    'obw2': (2, 2, [('a', 'kandydat', 4), ('b', 'kandydat', 1), ('c', 'statystyka', 1)]),
    'obw3': (2, 1, [('a', 'kandydat', 3), ('b', 'kandydat', 9), ('c', 'statystyka', 8)]),
    'obw4': (3, 3, [('a', 'kandydat', 2), ('b', 'kandydat', 0), ('c', 'statystyka', 2)])
}

wynik = {
    'kraj': {
        'a': 15,
        'b': 13
    },
    'woj1': {
        'a': 13,
        'b': 13
    },
    'woj2': {
        'a': 2,
        'b': 0
    },
    'okr1': {
        'a': 9,
        'b': 12
    },
    'gm2': {
        'a': 7,
        'b': 10
    },
    'obw3': {
        'a': 3,
        'b': 9
    }
}

statystyki = {
    'kraj': {
        'c': 15
    },
    'woj1': {
        'c': 13
    },
    'okr1': {
        'c': 12
    }
}


class ZliczanieWynikow(TestCase):
    def setUp(self):
        self.kraj = models.Kraj()
        for nazwa in wojewodztwa:
            models.Wojewodztwo.objects.create(nazwa=nazwa)
        for key, value in okregi.items():
            wojewodztwo = models.Wojewodztwo.objects.get(nazwa=value)
            models.Okrag.objects.create(wojewodztwo=wojewodztwo, nr=key)
        for key, value in gminy.items():
            gmina = models.Gmina.objects.create(kod_gminy=key)
            for nr_okragu in value:
                okrag = models.Okrag.objects.get(nr=nr_okragu)
                okrag.gminy.add(gmina)
        for key, (nr_gminy, nr_okragu, wyniki) in obwody.items():
            gmina = models.Gmina.objects.get(kod_gminy=nr_gminy)
            okrag = models.Okrag.objects.get(nr=nr_okragu)
            obwod = models.Obwod.objects.create(gmina=gmina, okrag=okrag, adres=key)
            for wynik in wyniki:
                models.Wynik.objects.create(podmiot=wynik[0], wynik=wynik[2], rodzaj=wynik[1], obwod=obwod)

    def test_wyniki_w_kraju(self):
        wyniki_w_kraju = self.kraj.get_candidate_results()
        self.assertEqual(wyniki_w_kraju, wynik['kraj'])

    def test_statystyki_w_kraju(self):
        statystyki_w_kraju = self.kraj.get_statistics()
        self.assertEqual(statystyki_w_kraju, statystyki['kraj'])

    def test_wyniki_w_wojewodztwie(self):
        woj1 = models.Wojewodztwo.objects.get(nazwa='woj1')
        self.assertEqual(woj1.get_candidate_results(), wynik['woj1'])

        woj2 = models.Wojewodztwo.objects.get(nazwa='woj2')
        self.assertEqual(woj2.get_candidate_results(), wynik['woj2'])

    def test_statystyki_w_wojewodztwie(self):
        woj1 = models.Wojewodztwo.objects.get(nazwa='woj1')
        self.assertEqual(woj1.get_statistics(), statystyki['woj1'])

    def test_wyniki_w_okregu(self):
        okr1 = models.Okrag.objects.get(nr=1)
        self.assertEqual(okr1.get_candidate_results(), wynik['okr1'])

    def test_statystyki_w_okregu(self):
        okr1 = models.Okrag.objects.get(nr=1)
        self.assertEqual(okr1.get_statistics(), statystyki['okr1'])

    def test_wyniki_w_gminie(self):
        gm2 = models.Gmina.objects.get(kod_gminy=2)
        self.assertEqual(gm2.get_candidate_results(), wynik['gm2'])

    def test_wyniki_w_obwodzie(self):
        obw3 = models.Obwod.objects.get(adres='obw3')
        wyniki_w_obwodzie = obw3.get_candidate_results()
        self.assertEqual(wyniki_w_obwodzie, wynik['obw3'])

    def test_modyfikacja_wyniku_w_obwodzie(self):
        obw3 = models.Obwod.objects.get(adres='obw3')
        obw3.modify_result('a', wynik['obw3']['a'] - 1)
        gmina = obw3.gmina
        self.assertEqual(gmina.get_candidate_results()['a'], wynik['gm2']['a'] - 1)
        okrag = gmina.okrag.get(nr=1)
        self.assertEqual(okrag.get_candidate_results()['a'], wynik['okr1']['a'] - 1)
        wojewodztwo = okrag.wojewodztwo
        self.assertEqual(wojewodztwo.get_candidate_results()['a'], wynik['woj1']['a'] - 1)
        wyniki_w_kraju = self.kraj.get_candidate_results()
        self.assertEqual(wyniki_w_kraju['a'], wynik['kraj']['a'] - 1)
