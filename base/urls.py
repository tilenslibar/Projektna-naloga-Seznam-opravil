from modulefinder import LOAD_CONST
from django.urls import path
from .views import Odjava, PosameznoOpravilo, Prijava, Ustvarjanje, SeznamOpravil, Urejanje, Brisanje, Registracija, ModifikacijaPrijave


urlpatterns = [
    path('prijava/', Prijava.as_view(authentication_form=ModifikacijaPrijave), name='prijava'),
    path('odjava/', Odjava.as_view(), name='odjava'),
    path('registracija/', Registracija.as_view(), name='registracija'),
    path('opravilo/<int:pk>/', PosameznoOpravilo.as_view(), name = 'opravilo'),
    path('', SeznamOpravil.as_view(), name = 'opravila'),
    path('ustvari-opravilo/', Ustvarjanje.as_view(), name = 'ustvari-opravilo'),
    path('posodobi-opravilo/<int:pk>/', Urejanje.as_view(), name='posodobi-opravilo'),
    path('izbrisi-opravilo/<int:pk>/', Brisanje.as_view(), name='izbrisi-opravilo'),
]