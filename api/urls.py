from django.urls import path
from .views import GenerateTextView,home,generate
urlpatterns = [
    path('',home,name="home"),
    path('gen/',generate,name="gen"),
    path('generate/',GenerateTextView.as_view(),name="generate")
]