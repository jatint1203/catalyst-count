from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Company, Industry, YearFounded, City, State, Country

class CompanyFilter(filters.FilterSet):
    year_founded = filters.ModelChoiceFilter(
        field_name='year_founded',
        queryset=YearFounded.objects.all()
    )
    industry = filters.ModelChoiceFilter(
        field_name='industry',
        queryset=Industry.objects.all()
    )
    size_range = filters.CharFilter(field_name='size_range', lookup_expr='icontains')
    city = filters.ModelChoiceFilter(
        field_name='city',
        queryset=City.objects.all()
    )
    state = filters.ModelChoiceFilter(
        field_name='state',
        queryset=State.objects.all()
    )
    country = filters.ModelChoiceFilter(
        field_name='country',
        queryset=Country.objects.all()
    )

    search = filters.CharFilter(method='filter_by_all_fields')
    employee_size = filters.CharFilter(method='filter_by_employee_size')

    class Meta:
        model = Company
        fields = [
            'name', 'domain', 'year_founded', 'industry',
            'size_range', 'city', 'state', 'country', 'linkedin_url'
        ]

    def filter_by_all_fields(self, queryset, name, value):
        """Filter queryset by search value across multiple fields."""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(domain__icontains=value) |
            Q(linkedin_url__icontains=value)
        )
    
    def filter_by_employee_size(self, queryset, name, value):
   
        if value:
            print(value)
            # Handle size range with '+' sign (e.g., '10001+')
            if value.endswith('+'):
                size_from = value.rstrip('+')
                queryset = queryset.filter(size__gte=size_from)
            else:
                # Handle size range in the format 'min-max' (e.g., '50-5000')
                try:
                    size_range = list(map(int, value.split('-')))
                    print(size_range)
                    if len(size_range) == 2:
                        size_from, size_to = size_range
                        queryset = queryset.filter(size_range__gte=size_from, size_range__lte=size_to)
                except ValueError:
                    # If value is invalid, return the unfiltered queryset
                    pass
        return queryset
