from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Auction, Bid
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class AuctionViewSetTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.auction = Auction.objects.create(
            owner=self.user,
            title='Test Auction',
            description='Test Description',
            starting_price=100.00,
            ends_at=timezone.now() + timedelta(days=1),
        )

    def test_list_auctions(self):
        response = self.client.get(reverse('auction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_auction(self):
        self.client.force_login(self.user)
        data = {
            'title': 'New Auction',
            'description': 'New Description',
            'starting_price': 200.00,
            'ends_at': timezone.now() + timedelta(days=1)
        }
        response = self.client.post(reverse('auction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_auction_unauthorized(self):
        data = {
            'title': 'Unauthorized Auction',
            'description': 'Test Description',
            'starting_price': 100.00,
            'ends_at': timezone.now() + timedelta(days=1)
        }
        response = self.client.post(reverse('auction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_closed_auction(self):
        self.client.force_login(self.user)
        self.auction.ends_at = timezone.now() - timedelta(days=1)
        self.auction.save()
        data = {'title': 'Updated Title'}
        response = self.client.patch(reverse('auction-detail', args=[self.auction.id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_my_auctions(self):
        self.client.force_login(self.user)
        response = self.client.get(f"{reverse('auction-list')}?mine=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class BidViewSetTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.bidder = User.objects.create_user(username='bidder', password='bidderpass')
        self.auction = Auction.objects.create(
            owner=self.user,
            title='Test Auction',
            description='Test Description',
            starting_price=100.00,
            ends_at=timezone.now() + timedelta(days=1),
        )

    def test_create_bid(self):
        self.client.force_login(self.bidder)
        data = {
            'auction': self.auction.id,
            'amount': 150.00
        }
        response = self.client.post(reverse('bid-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_bid_on_closed_auction(self):
        self.client.force_login(self.bidder)
        self.auction.ends_at = timezone.now() - timedelta(days=1)
        self.auction.save()
        data = {
            'auction': self.auction.id,
            'amount': 150.00
        }
        response = self.client.post(reverse('bid-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_bid_lower_than_current(self):
    #     self.client.force_login(self.bidder)
    #     data = {
    #         'auction': self.auction.id,
    #         'amount': 50.00
    #     }
    #     response = self.client.post(reverse('bid-list'), data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_owner_cannot_bid(self):
    #     self.client.force_login(self.user)
    #     data = {
    #         'auction': self.auction.id,
    #         'amount': 150.00
    #     }
    #     response = self.client.post(reverse('bid-list'), data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterViewTests(APITestCase):
    def test_register_user(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CurrentUserViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_get_current_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('current-user'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        

        

