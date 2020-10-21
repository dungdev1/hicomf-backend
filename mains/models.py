from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError

from .signals import (
    friendship_request_created,
    friendship_request_declined,
    friendship_request_accepted,
    friendship_request_cancelled
)

class Profile(models.Model):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.CharField(max_length=100, blank=True)
    gender = models.CharField(
        max_length=6,
        choices=[
            ('FEMALE', 'Female'),
            ('MALE', 'Male')
        ]
    )
    birthday = models.DateField(null=True)
    relationship = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", to_field='username')

    @property
    def year_old(self):
        "Returns the year old of user, if birthday is undefined, return 0."
        if self.birthday:
            today = timezone.now().date()
            return today.year - self.birthday.year - \
                ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        return 0

    @property
    def full_name(self):
        "Returns the user's full name."
        return self.first_name + ' ' + self.last_name

    def set_first_name(self, first_name):
        if first_name == '':
            raise "Invalid name"
        self.first_name = first_name

    def set_last_name(self, last_name):
        if last_name == '':
            raise "Invalid name"
        self.last_name = last_name

    def __str__(self):
        return self.full_name


class Address(models.Model):
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=50, blank=True)
    house_number = models.CharField(max_length=15, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses')

    def __str__(self):
        return f"{self.house_number}, {self.street}, {self.district}, {self.city}."


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_from", on_delete=models.CASCADE, to_field='username')
    to_user = models.ForeignKey(User, related_name="invitations_to", on_delete=models.CASCADE, to_field='username')
    message = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.from_user} wants to be friends with {self.to_user}"

    def clean(self):
        "Raise error if request is sent to its owner"
        if not self.from_user != self.to_user:
            raise ValidationError("Request must be sent to another user.")
    
    # Call this method before trying to add data, overriding the default behavior of built-in `save`
    def save(self, *args, **kwargs):
        # catch exception before save instance
        self.clean()

        # This syntax now calls Django's own 'save' function, add data to DB if data is safe
        super().save(*args, **kwargs)

    def accept(self):
        "Accept friend request, add friendship between two user"
        Friendship.objects.befriend(self.from_user, self.to_user)

        friendship_request_accepted.send(sender=self.__class__)
        
        self.delete() # delete request when successful accepting

    def decline(self):
        "Delete when request is declined by to_user"
        friendship_request_declined.send(sender=self.__class__)

        self.delete() # delete request when request is declined

    def cancel(self):
        "Delete when request is cancelled by from_user"
        friendship_request_cancelled.send(sender=self.__class__)

        self.delete()



# Use this manager to add extra methods for Friendship model ("table-level")
class FriendshipManager(models.Manager):
    def friends_of(self, user, shuffle=False):
        query_set = User.objects.filter(friendship__friends__user=user)
        if shuffle:
            query_set = query_set.order_by('?')
        return query_set

    def are_friends(self, user1, user2):
        return bool(Friendship.objects.get(user=user1).friends.filter(user=user2).exists())

    def befriend(self, user1, user2):
        Friendship.objects.get(user=user1).friends.add(Friendship.objects.get(user=user2))

        # FriendshipRequest.objects.filter(from_user=user1, to_user=user2).delete()

    def unfriend(self, user1, user2):
        Friendship.objects.get(user=user1).friends.remove(Friendship.objects.get(user=user2))

        # FriendshipRequest.objects.filter(from_user=user1, to_user=user2).delete()
        # FriendshipRequest.objects.filter(from_user=user2, to_user=user1).delete()


class Friendship(models.Model):
    user = models.OneToOneField(User, related_name='friendship', on_delete=models.CASCADE, to_field='username')
    friends = models.ManyToManyField('self')

    objects = FriendshipManager()

    def friend_count(self):
        return self.friends.count()


class Job(models.Model):
    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    starting_month = models.IntegerField()
    starting_year = models.IntegerField()
    ending_month = models.IntegerField(null=True, blank=True)
    ending_year = models.IntegerField(null=True, blank=True)
    still_working = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="jobs")
    
    def __str__(self):
        if self.still_working:
            return f"{self.position} at {self.company} ({self.starting_month}/{self.starting_year} - now)"
        return f"{self.position} at {self.company} ({self.starting_month}/{self.starting_year} - {self.ending_month}/{self.ending_year})"

    def clean(self):
        if self.ending_month and self.ending_year:
            if self.ending_year < self.starting_year:
                raise ValidationError("The starting year must be less than the ending year")
            if self.ending_year == self.starting_year and self.ending_month < self.starting_month:
                raise ValidationError("Value error")

    def save(self, *args, **kwargs):
        self.clean()

        if self.ending_month is None and self.ending_year is None:
            self.still_working = True

        super().save(*args, **kwargs)

    def get_working_time(self):
        ending_month, ending_year = None, None
        if self.still_working:
            ending_month = timezone.now().month
            ending_year = timezone.now().year
        else:
            ending_month = self.ending_month
            ending_year = self.ending_year

        if ending_month < self.starting_month:
            num_years = ending_year - self.starting_year - 1
            num_months = ending_month + (12 - self.starting_month)
            return (num_years, num_months)
        return (ending_year - self.starting_year, ending_month - self.starting_month)

    
class Education(models.Model):
    school_name = models.CharField(max_length=100)
    starting_year = models.IntegerField(null=True)
    ending_year = models.IntegerField(null=True)
    graduated = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    concentration = models.CharField(max_length=100)
    degree = models.CharField(max_length=150, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="educations")
    

    class Privacy(models.TextChoices):
        PUBLIC = 'P', _('Public')
        FRIENDS = 'F', _('Friends')
        ONLY_ME = 'O', _('Only me')

    privacy = models.CharField(
        max_length=2,
        choices=Privacy.choices,
        default=Privacy.PUBLIC,
    )

    def __str__(self):
        import string
        if self.graduated:
            if self.degree:
                return f"{self.degree.capitalize()} of {string.capwords(self.concentration)}"
            else:
                return f"Studied {string.capwords(self.concentration)} at {string.capwords(self.school_name)}"
        else:
            return f"Studies {string.capwords(self.concentration)} at {string.capwords(self.school_name)}"

    def clean(self):
        if self.ending_year and self.ending_year < self.starting_year:
            raise ValidationError("The starting year must be greater than the ending year")

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)


class PhotoAlbum(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='albums')

    def __str__(self):
        return f"{self.name} album - with {self.num_photos} photos."
    
    @property
    def num_photos(self):
        return len(Photo.objects.filter(album=self))


class Post(models.Model):
    caption = models.TextField(blank=True)
    time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    
    @property
    def num_likes(self):
        return len(Like.objects.filter(post=self))

    @property
    def num_comments(self):
        return len(Comment.objects.filter(post=self))

    @property
    def num_shares(self):
        return len(Share.objects.filter(post=self))


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name="by user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f"This like is created by {self.user.profile.full_name} in post (id: {self.post.id})"


class Comment(models.Model):
    text = models.TextField()
    time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="by user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"This comment is created by {self.user.profile.full_name} in post (id: {self.post.id})"


class Share(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares', verbose_name="by user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')

    def __str__(self):
        return f"This share is created by {self.user.profile.full_name} in post (id: {self.post.id}"


class Photo(models.Model):
    photo_url = models.TextField()
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name="photos")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="photos")
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="photos")

    def __str__(self):
        return f"Photo {self.id} belong to {self.album.name}"