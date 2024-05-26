from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Account, Destination
from .serializers import UserRegistrationSerializer, AccountSerializer, DestinationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import requests

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationListCreateView(generics.ListCreateAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

    def perform_create(self, serializer):
        account_id = self.kwargs.get('account_id')
        account = Account.objects.get(id=account_id)
        serializer.save(account=account)

class DestinationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

class AccountDestinationsView(APIView):
    def get(self, request, account_id):
        destinations = Destination.objects.filter(account_id=account_id)
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)

class IncomingDataView(APIView):
    def post(self, request):
        token = request.headers.get('CL-X-TOKEN')
        if not token:
            return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            account = Account.objects.get(app_secret_token=token)
        except Account.DoesNotExist:
            return Response({"error": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        if request.method == 'GET' and not isinstance(data, dict):
            return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

        destinations = account.destinations.all()
        for destination in destinations:
            headers = destination.headers
            if destination.http_method.lower() == 'get':
                response = requests.get(destination.url, headers=headers, params=data)
            elif destination.http_method.lower() in ['post', 'put']:
                response = requests.request(destination.http_method, destination.url, headers=headers, json=data)
            else:
                continue

            if response.status_code != 200:
                return Response({"error": "Failed to push data to destination"}, status=response.status_code)

        return Response({"success": "Data pushed to all destinations"}, status=status.HTTP_200_OK)
