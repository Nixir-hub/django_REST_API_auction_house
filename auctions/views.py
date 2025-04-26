# auctions/views.py
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from . import serializers
from .models import Auction, Bid
from .permissions import AuctionOwnerPermission, BidOwnerPermission
from .serializers import AuctionSerializer, BidSerializer, AuctionSummarySerializer, LoginSerializer, ProfileSerializer, \
    RegisterSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import logout

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, AuctionOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        for auction in queryset:
            auction.close_if_expired()

        # Filter by 'mine=true'
        if params.get('mine') == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)

        # Filter by auction status
        status = params.get('status')
        now = timezone.now()

        if status == 'open':
            queryset = queryset.filter(end_date__gt=now)
        elif status == 'closed':
            queryset = queryset.filter(end_date__lte=now)

        return queryset

    def perform_update(self, serializer):
        if self.get_object().owner != self.request.user:
            raise PermissionDenied("You cannot edit someone else's auction.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied("You cannot delete someone else's auction.")
        instance.delete()

    @action(detail=False, methods=['get'], url_path='my-auctions')
    def my_auctions(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to view your auctions.")

        auctions = Auction.objects.filter(owner=request.user)
        serializer = self.get_serializer(auctions, many=True)
        return Response(serializer.data)

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, BidOwnerPermission]
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        auction = serializer.validated_data['auction']

        # Zakaz licytowania własnych aukcji
        if auction.owner == self.request.user:
            raise serializers.ValidationError("You cannot bid on your own auction.")

        # Zakaz licytowania poniżej aktualnej najwyższej ceny
        if serializer.validated_data['amount'] <= auction.highest_bid:
            raise serializers.ValidationError("The bid must be higher than the current highest bid.")

        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Updating bids is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': 'Partial updating bids is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Deleting bids is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def get_queryset(self):
        if self.request.query_params.get('mine'):
            return Bid.objects.filter(user=self.request.user)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # Fetch the auction to which the bid is being placed
        auction = Auction.objects.get(id=request.data['auction'])

        # Check if the auction has ended
        if auction.ends_at < timezone.now():
            return Response({"detail": "Bidding is no longer allowed. The auction has ended."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with the normal bid creation
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my-bids')
    def my_bids(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to view your bids.")


        bids = Bid.objects.filter(user=request.user)
        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise ValidationError("You are already logged in. Cannot register again.")
        return super().create(request, *args, **kwargs)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    user = request.user
    return Response({
        'username': user.username,
        'id': user.id,
    })

class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: 'Successfully logged in', 400: 'Invalid credentials'}
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if request.user.is_authenticated:
            return Response({"detail": "User already logged in."}, status=status.HTTP_400_BAD_REQUEST)

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Sprawdzenie poprawności danych logowania
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"detail": "Successfully logged in."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Tylko zalogowani użytkownicy mogą się wylogować

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "User is not logged in."}, status=status.HTTP_400_BAD_REQUEST)

        logout(request)  # Wyczyść sesję
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

class MyProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
