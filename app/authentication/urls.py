from django.urls import path    
from.views import UserCreateView,UserDetailView

urlpatterns = [
    # Define your URL patterns here
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('details/', UserDetailView.as_view(), name='user-details'),
]