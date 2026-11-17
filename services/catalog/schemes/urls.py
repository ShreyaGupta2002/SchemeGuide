from django.urls import path
from .views import SchemeListView, SchemeDetailView

urlpatterns = [
    path('schemes/', SchemeListView.as_view(), name='scheme-list'),
    path('schemes/<int:scheme_id>/', SchemeDetailView.as_view(), name='scheme-detail'),
]
