from mains.models import Profile, Address, Job
# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.reverse import reverse


class AddressHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'address-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'profile_pk': obj.profile.id,
            'address_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class JobHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'job-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'profile_pk': obj.profile.id,
            'job_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    # addresses = serializers.HyperlinkedRelatedField(view_name='address-detail', read_only=True, many=True)
    addresses = AddressHyperlink(read_only=True, many=True)
    jobs = JobHyperlink(read_only=True, many=True)

    class Meta:
        model = Profile
        fields = ['url', 'id', 'first_name', 'last_name', 'bio', 'gender',
                  'birthday', 'relationship', 'email', 'phone_number', 'addresses', 'jobs']


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
        view_name='profile-detail', read_only=True)
    url = AddressHyperlink(read_only=True)

    class Meta:
        model = Address
        fields = ['url', 'id', 'city', 'district',
                  'street', 'house_number', 'profile']


class JobSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
        view_name='profile-detail', read_only=True)
    url = JobHyperlink(read_only=True)
    working_time = serializers.ListField(source='get_working_time', read_only=True)

    class Meta:
        model = Job
        fields = ['url', 'id', 'position', 'company', 'description', 'city', 'starting_month',
                  'starting_year', 'ending_month', 'ending_year', 'profile', 'working_time']

