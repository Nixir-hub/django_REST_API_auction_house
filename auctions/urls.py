# auctions/urls.py
# auctions/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet, BidViewSet, RegisterView, current_user_view, LoginView, LogoutView

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')
router.register(r'bids', BidViewSet, basename='bid')

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', current_user_view, name='current-user'),
    path('api-auth/', include('rest_framework.urls')),  # for session login/logout UI
]