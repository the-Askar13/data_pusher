from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView,
    AccountListCreateView,
    AccountRetrieveUpdateDestroyView,
    DestinationListCreateView,
    DestinationRetrieveUpdateDestroyView,
    AccountDestinationsView,
    IncomingDataView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<uuid:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='account-detail'),
    path('accounts/<uuid:account_id>/destinations/', DestinationListCreateView.as_view(), name='destination-list-create'),
    path('destinations/<int:pk>/', DestinationRetrieveUpdateDestroyView.as_view(), name='destination-detail'),
    path('accounts/<uuid:account_id>/destinations-list/', AccountDestinationsView.as_view(), name='account-destinations'),
    path('server/incoming_data/', IncomingDataView.as_view(), name='incoming-data'),
]
