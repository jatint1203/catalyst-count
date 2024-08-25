from django.urls import path
from .views import *

urlpatterns = [
    path('welcome/', WelcomeView.as_view(), name='welcome'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('filter/', CompanyFilterView.as_view(), name='company-filter'),
    path('selection_data/', SelectionDataView.as_view(), name='selection-data'),

]
