from django.contrib import admin
from mains.models import (
  Profile, Address, Job, Education, Post, Photo,
  PhotoAlbum, Like, Comment, Share
)

admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(Job)
admin.site.register(Education)
admin.site.register(Post)
admin.site.register(PhotoAlbum)
admin.site.register(Photo)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Share)