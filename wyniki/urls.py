from django.urls import path

from . import views

urlpatterns = [
    path('kraj', views.kraj, name='kraj'),
    path('wojewodztwo/<str:nazwa>', views.wojewodztwo),
    path('okrag/<int:nr>', views.okrag),
    path('gmina/<int:kod>', views.gmina),
    path('obwod/<int:id>', views.obwod)
]
