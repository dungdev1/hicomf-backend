from mains.models import Profile, Address
# from django.contrib.auth.models import User
from rest_framework import serializers


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    addresses = serializers.HyperlinkedRelatedField(view_name='address-detail', read_only=True, many=True)

    class Meta:
        model = Profile
        fields = ['url', 'id', 'first_name', 'last_name', 'bio', 'gender',
                  'birthday', 'relationship', 'email', 'phone_number', 'addresses']
            

class AddressSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name='profile-detail', read_only=True)

    class Meta:
        model = Address
        fields = ['url', 'id', 'city', 'district', 'street', 'house_number', 'profile']