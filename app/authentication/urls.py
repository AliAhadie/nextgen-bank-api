from django.urls import path    
from.views import UserCreateView,UserDetailView,ActivationAccountView,ActivatedView

urlpatterns = [
    # Define your URL patterns here
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('details/', UserDetailView.as_view(), name='user-details'),
    path('resend_activation/',ActivationAccountView.as_view(),name='active'),
    path('active/<str:uuid>/',ActivatedView.as_view(),name='active_acc')
]