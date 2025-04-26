from datetime import timedelta
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from .models import Auction, Bid




class BidSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Bid
        fields = '__all__'

    def validate(self, attrs):
        auction = attrs['auction']
        user = self.context['request'].user
        amount = attrs['amount']

        # Nie możesz licytować własnej aukcji
        if auction.owner == user:
            raise ValidationError("You cannot bid on your own auction.")

        # Kwota musi być większa od aktualnej najwyższej
        if amount <= auction.highest_bid:
            raise ValidationError("The bid must be higher than the current highest bid.")

        # Aukcja nie może być zamknięta
        if auction.is_closed:
            raise ValidationError("This auction is closed. You can't place a bid.")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AuctionSerializer(serializers.ModelSerializer):
    winner = serializers.StringRelatedField()
    owner = serializers.ReadOnlyField(source='owner.username')
    highest_bid = serializers.SerializerMethodField()
    bids = BidSerializer(many=True, read_only=True)  # Historia ofert
    ends_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model = Auction
        fields = '__all__'
        exeption = ["highest_bid"]
        read_only_fields = ["is_closed"]

    def get_status(self, obj):
        return "closed" if obj.end_date < timezone.now() else "open"

    def get_highest_bid(self, obj):
        highest = obj.bids.order_by('-amount').first()
        return highest.amount if highest else obj.starting_price

    def validate(self, data):
        end_date = data.get('ends_at')
        if end_date:
            min_end_time = timezone.now() + timedelta(minutes=5)
            if end_date <= min_end_time:
                raise serializers.ValidationError({
                    'ends_at': "End date must be at least 5 minutes in the future."
                })
        return data


class AuctionSummarySerializer(serializers.ModelSerializer):
    highest_bid = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    winner = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = ['id', 'title', 'starting_price', 'highest_bid', 'total_bids', 'winner']

    def get_highest_bid(self, obj):
        highest_bid = obj.bids.order_by('-amount').first()
        return highest_bid.amount if highest_bid else obj.starting_price

    def get_total_bids(self, obj):
        return obj.bids.count()


    def get_winner(self, obj):
        if obj.status == "closed":
            highest_bid = obj.bids.order_by('-amount').first()
            return highest_bid.user.username if highest_bid else None
        return None

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        fields = '__all__'