from functools import wraps
import jwt

from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.utils import serializer_helpers

from rest_framework.views import APIView
from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny

from mains.serializations import (
    CommentSerializer, ProfileSerializer,
    AddressSerializer,
    JobSerializer,
    EducationSerializer,
    AlbumSerializer,
    PhotoSerializer,
    PostSerializer,
    LikeSerializer, ShareSerializer
)
from mains.models import (
    Profile, Address, Job, Education,
    PhotoAlbum, Photo, Post, Like, Comment, Share
)
from mains.permissions import IsOwnerOrReadOnly, AllowPostOwnerDelete


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
        queryset = []
        post_id = request.query_params.get('postId', None)
        content = request.query_params.get('content', None)
        if post_id and content:
            if content == 'like':
                likes = Post.objects.get(pk=post_id).likes.all()
                for like in likes:
                    profile = like.user.profile
                    queryset.append(profile)
            elif content == 'comment':
                comments = Post.objects.get(pk=post_id).comments.all()
                for comment in comments:
                    profile = comment.user.profile
                    queryset.append(profile)
            elif content == 'share':
                shares = Post.objects.get(pk=post_id).shares.all()
                for share in shares:
                    profile = share.user.profile
                    queryset.append(profile)
        else:
            queryset = Profile.objects.all()

        serializer = ProfileSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        user_avatar = request.data.pop('user_avatar')
        serializer = ProfileSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            # Has Profile, create Album, Post and Photo
            profile = Profile.objects.get(user=request.user)
            album = PhotoAlbum.objects.create(name='avatar', profile=profile)
            post = Post.objects.create(
                caption=f"{profile.full_name} has updated his avatar",
                user=profile.user
            )
            Photo.objects.create(
                photo_url=user_avatar, album=album, post=post, is_active=True)
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
            address = Address.objects.filter(
                profile=profile_pk).get(id=address_pk)
        except ValidationError:
            raise Http404
        except Address.DoesNotExist:
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
            job = Job.objects.filter(profile=profile_pk).get(id=job_pk)
        except ValidationError:
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


class EducationList(APIView):
    """
    List all educations, or create a new education instance.
    """

    def get(self, request, profile_pk):
        try:
            educations = Education.objects.filter(profile=profile_pk)
            serializer = EducationSerializer(
                educations, many=True, context={'request': request})
            return Response(serializer.data)
        except ValidationError:
            raise Http404

    def post(self, request, profile_pk):
        try:
            if request.user == User.objects.get(profile=profile_pk):
                serializer = EducationSerializer(
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


class EducationDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, profile_pk, edu_pk):
        try:
            edu = Education.objects.filter(profile=profile_pk).get(id=edu_pk)
        except ValidationError:
            raise Http404
        except Education.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, edu.profile)
        return edu

    def get(self, request, *args, **kwargs):
        edu = self.get_object(**kwargs)
        serializer = EducationSerializer(edu, context={'request': request})
        url = request.build_absolute_uri(
            reverse('education-detail', args=(edu.profile.id, edu.id)))
        return Response({'url': url, **serializer.data})

    def put(self, request, *args, **kwargs):
        edu = self.get_object(**kwargs)
        serializer = EducationSerializer(
            edu, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        edu = self.get_object(**kwargs)
        edu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlbumList(APIView):

    def get(self, request, profile_pk):
        try:
            albums = PhotoAlbum.objects.filter(profile=profile_pk)
            serializer = AlbumSerializer(
                albums, many=True, context={'request': request})
            return Response(serializer.data)
        except ValidationError:
            raise Http404

    def post(self, request, profile_pk):
        try:
            if request.user == User.objects.get(profile=profile_pk):
                serializer = AlbumSerializer(
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


class AlbumDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, profile_pk, album_pk):
        try:
            album = PhotoAlbum.objects.filter(
                profile=profile_pk).get(id=album_pk)
        except ValidationError:
            raise Http404
        except PhotoAlbum.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, album.profile)
        return album

    def get(self, request, *args, **kwargs):
        album = self.get_object(**kwargs)
        serializer = AlbumSerializer(album, context={'request': request})
        url = request.build_absolute_uri(
            reverse('album-detail', args=(album.profile.id, album.id)))
        return Response({'url': url, **serializer.data})

    def put(self, request, *args, **kwargs):
        album = self.get_object(**kwargs)
        serializer = AlbumSerializer(
            album, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        album = self.get_object(**kwargs)
        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostList(APIView):

    def get(self, request):
        queryset = Post.objects.all()
        profile_id = request.query_params.get('profile', None)
        if profile_id is not None:
            user = Profile.objects.get(pk=profile_id).user
            queryset = queryset.filter(user=user)
        serializer = PostSerializer(
            queryset, many=True, context={'request': request})
        for i, post in enumerate(queryset):
            profile = request.build_absolute_uri(
                reverse('profile-detail', args=(post.user.profile.id,)))
            serializer.data[i]['profile'] = profile
            serializer.data[i]['owner_name'] = post.user.profile.full_name
            for album in post.user.profile.albums.all():
                if album.name == 'avatar':
                    for photo in album.photos.all():
                        if photo.is_active:
                            serializer.data[i]['owner_pic'] = photo.photo_url
        return Response(serializer.data)

    def post(self, request):
        photos_url = request.data.pop('imageUrl', None)
        serializer = PostSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            post = Post.objects.latest('time')
            if photos_url is not None:
                for photo_url in photos_url:
                    try:
                        photo_album = PhotoAlbum.objects.get(name='postPhoto')
                    except PhotoAlbum.DoesNotExist:
                        photo_album = PhotoAlbum.objects.create(
                            name="postPhoto", profile=request.user.profile)                                
                    Photo.objects.create(photo_url=photo_url, album=photo_album, post=post)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            post = Post.objects.get(pk=pk)
        except ValidationError:
            raise Http404
        except Post.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, post)
        return post

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post, context={'request': request})
        profile = request.build_absolute_uri(
            reverse('profile-detail', args=(post.user.profile.id,)))
        return Response({**serializer.data, 'profile': profile})

    def put(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(
            post, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhotoList(APIView):

    def get(self, request):
        queryset = Photo.objects.all()
        profile_param = request.query_params.get('profile_id', None)
        album_param = request.query_params.get('album', None)
        if profile_param is not None:
            queryset = queryset.filter(post__user__profile=profile_param)
            if album_param is not None:
                try:
                    album = PhotoAlbum.objects.get(pk=album_param)
                    queryset = queryset.filter(album=album)
                    if album.name == 'avatar':
                        serializer = PhotoSerializer(queryset.get(
                            is_active=True), context={'request': request})
                        return Response(serializer.data)
                except PhotoAlbum.DoesNotExist:
                    raise Http404

            serializer = PhotoSerializer(
                queryset, many=True, context={'request': request})
            return Response(serializer.data)

    def post(self, request):
        try:
            album = PhotoAlbum.objects.get(pk=request.data.pop('album'))
            post = Post.objects.get(pk=request.data.pop('post'))
            if album.profile.user != request.user or post.user != request.user:
                raise exceptions.PermissionDenied
        except exceptions.PermissionDenied as err:
            return Response({"detail": str(err)}, status=status.HTTP_403_FORBIDDEN)
        except PhotoAlbum.DoesNotExist:
            raise Http404
        except Post.DoesNotExist:
            raise Http404
        serializer = PhotoSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(album=album, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            photo = Photo.objects.get(pk=pk)
        except ValidationError:
            raise Http404
        except Photo.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, photo.post)
        return photo

    def get(self, request, pk):
        photo = self.get_object(pk)
        album = request.build_absolute_uri(
            reverse('album-detail', args=(photo.album.profile.id, photo.album.id)))
        serializer = PhotoSerializer(photo, context={'request': request})
        return Response({**serializer.data, 'album': album})

    def put(self, request, pk):
        photo = self.get_object(pk)
        serializer = PhotoSerializer(
            photo, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        photo = self.get_object(pk)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeList(APIView):

    def get(self, request, post_pk):
        try:
            likes = Like.objects.filter(post=post_pk)
            serializer = LikeSerializer(
                likes, many=True, context={'request': request})
            return Response(serializer.data)
        except ValidationError:
            raise Http404

    def post(self, request, post_pk):
        try:
            serializer = LikeSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    post = Post.objects.get(pk=post_pk)
                    serializer.save(post=post, user=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Post.DoesNotExist:
                    raise Http404
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            raise Http404


class LikeDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, post_pk, like_pk):
        try:
            like = Like.objects.filter(post=post_pk).get(id=like_pk)
        except ValidationError:
            raise Http404
        except Like.DoesNotExist:
            raise Http404

        self.check_object_permissions(self.request, like)
        return like

    def get(self, request, *args, **kwargs):
        like = self.get_object(**kwargs)
        serializer = LikeSerializer(like, context={'request': request})
        url = request.build_absolute_uri(
            reverse('like-detail', args=(like.post.id, like.id)))
        profile = request.build_absolute_uri(
            reverse('profile-detail', args=(like.user.profile.id,)))
        return Response({'url': url, **serializer.data, 'profile': profile})

    def delete(self, request, *args, **kwargs):
        like = self.get_object(**kwargs)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentList(APIView):

    def get(self, request, post_pk):
        try:
            comments = Comment.objects.filter(post=post_pk)
            serializer = CommentSerializer(
                comments, many=True, context={'request': request})
            return Response(serializer.data)
        except ValidationError:
            raise Http404

    def post(self, request, post_pk):
        try:
            serializer = CommentSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    post = Post.objects.get(pk=post_pk)
                    serializer.save(post=post, user=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Post.DoesNotExist:
                    raise Http404
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            raise Http404


class CommentDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly | AllowPostOwnerDelete]

    def get_object(self, post_pk, comment_pk):
        try:
            comment = Comment.objects.filter(post=post_pk).get(id=comment_pk)
        except ValidationError:
            raise Http404
        except Comment.DoesNotExist:
            raise Http404

        self.check_object_permissions(self.request, comment)
        return comment

    def get(self, request, *args, **kwargs):
        comment = self.get_object(**kwargs)
        serializer = CommentSerializer(comment, context={'request': request})
        url = request.build_absolute_uri(
            reverse('comment-detail', args=(comment.post.id, comment.id)))
        profile = request.build_absolute_uri(
            reverse('profile-detail', args=(comment.user.profile.id,)))
        return Response({'url': url, **serializer.data, 'profile': profile})

    def put(self, request, *args, **kwargs):
        comment = self.get_object(**kwargs)
        serializer = CommentSerializer(
            comment, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        comment = self.get_object(**kwargs)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShareList(APIView):

    def get(self, request, post_pk):
        try:
            shares = Share.objects.filter(post=post_pk)
            serializer = ShareSerializer(
                shares, many=True, context={'request': request})
            return Response(serializer.data)
        except ValidationError:
            raise Http404

    def post(self, request, post_pk):
        try:
            serializer = ShareSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    post = Post.objects.get(pk=post_pk)
                    serializer.save(post=post, user=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Post.DoesNotExist:
                    raise Http404
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            raise Http404


class ShareDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, post_pk, share_pk):
        try:
            share = Share.objects.filter(post=post_pk).get(id=share_pk)
        except ValidationError:
            raise Http404
        except Share.DoesNotExist:
            raise Http404

        self.check_object_permissions(self.request, share)
        return share

    def get(self, request, *args, **kwargs):
        share = self.get_object(**kwargs)
        serializer = ShareSerializer(share, context={'request': request})
        url = request.build_absolute_uri(
            reverse('share-detail', args=(share.post.id, share.id)))
        profile = request.build_absolute_uri(
            reverse('profile-detail', args=(share.user.profile.id,)))
        return Response({'url': url, **serializer.data, 'profile': profile})

    def delete(self, request, *args, **kwargs):
        share = self.get_object(**kwargs)
        share.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetail(APIView):
    
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        likes = Like.objects.filter(user=request.user)
        postsId = []
        for like in likes:
            postsId.append({
                "post_id": like.post.id,
                "like_id": like.id
            })
        data = {**serializer.data, "liked_postsId": postsId}
        for album in profile.albums.all():
            if album.name == 'avatar':
                for photo in album.photos.all():
                    if photo.is_active:
                        return Response({**data, 'avatar': photo.photo_url})
        return Response(data)