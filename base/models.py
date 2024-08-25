from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'country')

class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'state')

class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class YearFounded(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.year)

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    sr = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    year_founded = models.ForeignKey(YearFounded, on_delete=models.SET_NULL, null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    size_range = models.CharField(max_length=50, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    linkedin_url = models.URLField(max_length=500, null=True, blank=True)
    current_employee_estimate = models.IntegerField(null=True, blank=True)
    total_employee_estimate = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Company"
