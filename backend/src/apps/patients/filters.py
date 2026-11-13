import django_filters

from .models import Patient


class PatientFilter(django_filters.FilterSet):
    gender = django_filters.ChoiceFilter(field_name="sex", choices=Patient.Sex.choices)

    class Meta:
        model = Patient
        fields = ("facility", "gender", "village", "is_active")
