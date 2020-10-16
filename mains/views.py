from functools import wraps
import jwt

from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny

from mains.serializations import ProfileSerializer, AddressSerializer, JobSerializer
from mains.models import Profile, Address, Job, Education
from mains.permissions import IsOwnerOrReadOnly


# Validate scope


def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse(
                {'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'profiles': reverse('profile-list', request=request, format=format),
        # 'addresses': reverse('address-list', request=request, format=format),
    })


@api_view(['GET', 'POST'])
def profile_list(request):
    """
    List all users, or create a new profile.
    """
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(
            profiles, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProfileSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except ValidationError:
            raise Http404
        except Profile.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, profile)
        return profile

    def get(self, request, pk, format=None):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(
            profile, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        profile = self.get_object(pk)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def address_list(request, profile_pk):
    # Check user is ouwner of address list
    try:
        isOwner = True if request.user == User.objects.get(
            profile=profile_pk) else False
    except ValidationError:
        raise Http404

    if request.method == 'GET':
        # Allow all authenticated user can get address data
        addresses = Address.objects.filter(profile=profile_pk)
        serializer = AddressSerializer(
            addresses, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        # Only onwer can add address to their addresses list
        try:
            if isOwner:
                serializer = AddressSerializer(
                    data=request.data, context={'request': request})
                if serializer.is_valid():
                    profile = Profile.objects.get(user=request.user)
                    serializer.save(profile=profile)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            raise exceptions.PermissionDenied
        except exceptions.PermissionDenied as err:
            return Response({"detail": str(err)}, status=status.HTTP_403_FORBIDDEN)


class AddressDetail(APIView):

    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, profile_pk, address_pk):
        try:
            profile = Profile.objects.get(id=profile_pk)
            address = profile.addresses.get(id=address_pk)
        except Profile.DoesNotExist:
            raise Http404
        except Address.DoesNotExist:
            raise Http404
        except ValidationError:
            raise Http404
        self.check_object_permissions(self.request, address.profile)
        return address

    def get(self, request, *args, **kwargs):
        address = self.get_object(**kwargs)
        serializer = AddressSerializer(address, context={'request': request})
        url = request.build_absolute_uri(
            reverse('address-detail', args=(address.profile.id, address.id)))
        return Response({"url": url, **serializer.data})

    def put(self, request, *args, **kwargs):
        address = self.get_object(**kwargs)
        serializer = AddressSerializer(
            address, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        address = self.get_object(**kwargs)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobList(APIView):
    """
    List all jobs, or create a new job.
    """

    def get(self, request, profile_pk):
        try:
            jobs = Job.objects.filter(profile=profile_pk)
            serializer = JobSerializer(
                jobs, many=True, context={'request': request})
            return Response(serializer.data)
        except ValidationError as err:
            raise Http404

    def post(self, request, profile_pk):
        try:
            if request.user == User.objects.get(profile=profile_pk):
                serializer = JobSerializer(
                    data=request.data, context={'request': request})
                if serializer.is_valid():
                    profile = Profile.objects.get(user=request.user)
                    serializer.save(profile=profile)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            raise exceptions.PermissionDenied
        except ValidationError:
            raise Http404
        except exceptions.PermissionDenied as err:
            return Response({"detail": str(err)}, status=status.HTTP_403_FORBIDDEN)


class JobDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, profile_pk, job_pk):
        try:
            profile = Profile.objects.get(id=profile_pk)
            job = profile.jobs.get(id=job_pk)
        except Profile.DoesNotExist:
            raise Http404
        except Job.DoesNotExist:
            raise Http404
        # Check if the profile of this job is belong to the request user
        self.check_object_permissions(self.request, job.profile)
        return job

    def get(self, request, profile_pk, job_pk):
        job = self.get_object(profile_pk, job_pk)
        serializer = JobSerializer(job, context={'request': request})
        url = request.build_absolute_uri(
            reverse('job-detail', args=(job.profile.id, job.id)))
        return Response({'url': url, **serializer.data})

    def put(self, request, profile_pk, job_pk):
        job = self.get_object(profile_pk, job_pk)
        serializer = JobSerializer(
            job, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, profile_pk, job_pk):
        job = self.get_object(profile_pk, job_pk)
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
