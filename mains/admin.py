from django.contrib import admin
from mains.models import (
  Profile, Address, Job, Education, Post, Photo,
  PhotoAlbum
)

admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(Job)
admin.site.register(Education)
admin.site.register(Post)
admin.site.register(PhotoAlbum)
admin.site.register(Photo)