from rest_framework import permissions

class AuctionOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow auction owners to modify the auction.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the auction
        return obj.owner == request.user

class BidOwnerPermission(permissions.BasePermission):
    """
    Custom permission to only allow bid owners to modify the bid.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the bid
        return obj.user == request.user
