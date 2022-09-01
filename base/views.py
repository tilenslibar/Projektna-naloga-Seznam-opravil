from django.contrib.auth.models import User
import django.forms
import django.forms.utils
import django.forms.widgets
from django.utils.translation import ngettext 
from django.core.exceptions import ValidationError
from difflib import SequenceMatcher
import re
from django.core.exceptions import FieldDoesNotExist
import os
import gzip

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

from .models import Opravilo


class SeznamOpravil(LoginRequiredMixin, ListView):
    model = Opravilo
    context_object_name = 'opravila'
    template_name = 'base/seznam_opravil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opravila'] = context['opravila'].filter(uporabnik=self.request.user)
        return context


class PosameznoOpravilo(LoginRequiredMixin, DetailView):
    model = Opravilo
    context_object_name = 'opravilo'


class Ustvarjanje(LoginRequiredMixin, CreateView):
    model = Opravilo
    fields = ['naslov', 'opis', 'opravljeno']
    template_name = 'base/ustvarjanje.html'
    success_url = reverse_lazy('opravila')

    def form_valid(self, form):
        form.instance.uporabnik = self.request.user
        return super(Ustvarjanje, self).form_valid(form)


class Urejanje(LoginRequiredMixin, UpdateView):
    model = Opravilo
    fields = ['naslov', 'opis', 'opravljeno']
    success_url = reverse_lazy('opravila')
    template_name = 'base/ustvarjanje.html'


class Brisanje(LoginRequiredMixin, DeleteView):
    model = Opravilo
    fields = '__all__'
    template_name = 'base/brisanje.html'
    success_url = reverse_lazy('opravila')

# UPORABNIŠKE NASTAVITVE ----------------------------------------------------------------------------------------------------------

class ModifikacijaPrijave(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Napačno uporabniško ime ali geslo."
        ),
        'inactive': ("Račun ni v uporabi"),
    }

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['username'].widget.attrs.update(
                {'class':'my-username-class'}
            )
            self.fields['password'].widget.attrs.update(
            {'class':'my-password-class'}
            )
            self.fields['username'].label = 'Uporabniško ime'
            self.fields['password'].label = 'Geslo'


class Prijava(LoginView):
    template_name = 'base/prijava.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('opravila')


class Odjava(LogoutView):
    next_page = 'prijava'


class ModifikacijaRegistracije(UserCreationForm):
    error_messages = {'password_mismatch':("Gesli nista enaki!"),
                        'username_exists':("Uporabniško ime je že v uporabi")}

    def clean_username(self):
        username = self.cleaned_data.get('username')

        try:
            User._default_manager.get(username=username)

            raise django.forms.ValidationError(
                self.error_messages['username_exists'],
                code = 'username_exist',)
        except User.DoesNotExist:
            return username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Geslo'
        self.fields['password2'].label = 'Potrditev gesla'
        self.fields['username'].label = 'Uporabniško ime'
        self.fields['password1'].help_text = '*geslo naj ima vsaj 8 znakov, naj ne vsebuje samo števk in naj bo čim bolj izvirno*'
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None


class Registracija(FormView):
    template_name = 'base/registracija.html'
    form_class = ModifikacijaRegistracije
    success_url = reverse_lazy('opravila')

    def form_valid(self, form):
        uporabnik = form.save()
        if uporabnik is not None:
            login(self.request, uporabnik)
        return super(Registracija, self).form_valid(form)

# CUSTOM VALIDATORJI ------------------------------------------------------------------------------------------------------------

class CustomMinimumLengthValidator():
  
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Geslo je prekratko. Imeti mora vsaj  %(min_length)d znakov.",
                    "Geslo je prekratko. Imeti mora vsaj %(min_length)d znakov.",
                    self.min_length
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Geslo je prekratko. Imeti mora vsaj  %(min_length)d znakov.",
                    "Geslo je prekratko. Imeti mora vsaj %(min_length)d znakov.",
            self.min_length
        ) % {'min_length': self.min_length}



class CustomUserAttributeSimilarityValidator():
    DEFAULT_USER_ATTRIBUTES = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=1):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        ("Geslo je preveč podobno uporabniškemu imenu."),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )

    def get_help_text(self):
        return ("Geslo ne sme biti preveč podobno ostalim uporabniškim podatkom")



class CustomCommonPasswordValidator():
    DEFAULT_PASSWORD_LIST_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'common-passwords.txt.gz'
    )

    def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        try:
            with gzip.open(password_list_path) as f:
                common_passwords_lines = f.read().decode().splitlines()
        except IOError:
            with open(password_list_path) as f:
                common_passwords_lines = f.readlines()

        self.passwords = {p.strip() for p in common_passwords_lines}

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                ("Prepogosto geslo."),
                code='password_too_common',
            )

    def get_help_text(self):
        return ("Geslo ne sme biti pogosto uporabljeno.")



class CustomNumericPasswordValidator():

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                ("Geslo vsebuje samo števke."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return ("Geslo ne sme biti v celoti numerično.")