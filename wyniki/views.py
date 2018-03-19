from django.http import HttpResponse
import wyniki.jinja2
import wyniki.models
from jinja2 import PackageLoader, select_autoescape

env = wyniki.jinja2.environment(
    loader=PackageLoader('wyniki', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def get_region_response(region):
    template = env.get_template('wyniki/base.html')
    return HttpResponse(template.render(
        wyniki=region.get_candidate_results(),
        statystyki=region.get_statistics(),
        linki=region.get_links(),
        gdzie_jesteśmy=region.__str__(),
        dzieci=region.get_child_links()))


def index(request):
    template = env.get_template('index.html')
    return HttpResponse(template.render())


def kraj(request):
    polska = wyniki.models.Kraj()
    return get_region_response(polska)


def wojewodztwo(request, nazwa):
    wojewodztwo = wyniki.models.Wojewodztwo.objects.get(nazwa=nazwa)
    return get_region_response(wojewodztwo)


def okrag(request, nr):
    okrag = wyniki.models.Okrag.objects.get(nr=nr)
    return get_region_response(okrag)


def obwod(request, id):
    obwod = wyniki.models.Obwod.objects.get(pk=id)
    return get_region_response(obwod)


def gmina(request, kod):
    gmina = wyniki.models.Gmina.objects.get(kod_gminy=kod)
    return get_region_response(gmina)
