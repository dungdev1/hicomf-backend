from django.db.models import fields
from mains.models import (
    Profile, Address, Job, Education,
    PhotoAlbum, Photo,
    Post, Like, Share, Comment
)
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


class EducationHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'education-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'profile_pk': obj.profile.id,
            'edu_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class AlbumHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'album-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'profile_pk': obj.profile.id,
            'album_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class LikeHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'like-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'post_pk': obj.post.id,
            'like_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class CommentHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'comment-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'post_pk': obj.post.id,
            'comment_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class ShareHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'share-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'post_pk': obj.post.id,
            'share_pk': obj.id
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    # addresses = serializers.HyperlinkedRelatedField(view_name='address-detail', read_only=True, many=True)
    addresses = AddressHyperlink(read_only=True, many=True)
    jobs = JobHyperlink(read_only=True, many=True)
    educations = EducationHyperlink(read_only=True, many=True)
    albums = AlbumHyperlink(read_only=True, many=True)

    class Meta:
        model = Profile
        fields = ['url', 'id', 'first_name', 'last_name', 'full_name', 'bio', 'gender', 'birthday', 'relationship',
                  'email', 'phone_number', 'addresses', 'jobs', 'educations', 'albums']


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
    working_time = serializers.ListField(
        source='get_working_time', read_only=True)

    class Meta:
        model = Job
        fields = ['url', 'id', 'position', 'company', 'description', 'city', 'starting_month',
                  'starting_year', 'ending_month', 'ending_year', 'profile', 'working_time']


class EducationSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
        view_name='profile-detail', read_only=True)
    url = EducationHyperlink(read_only=True)

    class Meta:
        model = Education
        fields = ['url', 'id', 'privacy', 'school_name', 'starting_year', 'ending_year',
                  'graduated', 'description', 'concentration', 'degree', 'profile']


class PostSerializer(serializers.HyperlinkedModelSerializer):
    photos = serializers.HyperlinkedRelatedField(
        view_name='photo-detail', many=True, read_only=True)
    likes = LikeHyperlink(read_only=True, many=True)
    comments = CommentHyperlink(read_only=True, many=True)
    shares = ShareHyperlink(read_only=True, many=True)

    class Meta:
        model = Post
        fields = ['url', 'id', 'caption', 'time', 'photos', 'num_likes',
                  'num_comments', 'num_shares', 'likes', 'comments', 'shares']


class AlbumSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
        view_name='profile-detail', read_only=True)
    photos = serializers.HyperlinkedRelatedField(
        view_name='photo-detail', read_only=True, many=True)
    url = AlbumHyperlink(read_only=True)

    class Meta:
        model = PhotoAlbum
        fields = ['url', 'id', 'name', 'num_photos', 'photos', 'profile']


class PhotoSerializer(serializers.HyperlinkedModelSerializer):
    post = serializers.HyperlinkedRelatedField(
        view_name='post-detail', read_only=True)

    class Meta:
        model = Photo
        fields = ['url', 'id', 'photo_url', 'post']


class LikeSerializer(serializers.HyperlinkedModelSerializer):
    post = serializers.HyperlinkedRelatedField(
        view_name='post-detail', read_only=True)
    url = LikeHyperlink(read_only=True)

    class Meta:
        model = Like
        fields = ['url', 'id', 'post']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    post = serializers.HyperlinkedRelatedField(
        view_name='post-detail', read_only=True)
        
    class Meta:
        model = Comment
        fields = ['id', 'text', 'time', 'post']


class ShareSerializer(serializers.HyperlinkedModelSerializer):
    post = serializers.HyperlinkedRelatedField(
        view_name='post-detail', read_only=True)
    url = ShareHyperlink(read_only=True)

    class Meta:
        model = Share
        fields = ['url', 'id', 'post']
