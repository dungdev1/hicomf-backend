from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone

from django.core.exceptions import ValidationError


class Address(models.Model):
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    house_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.house_number}, {self.street}, {self.district}, {self.city}."


class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    bio = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=6,
        choices=[
            ('FEMALE', 'Female'),
            ('MALE', 'Male')
        ]
    )
    birthday = models.DateField(null=True)
    relationship = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=12)
    address = models.ManyToManyField(Address)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="basic_information")

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


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_from", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="invitations_to", on_delete=models.CASCADE)
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

        self.delete() # delete request when successful accepting

    def decline(self):
        self.delete() # delete request when request is declined


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
    user = models.OneToOneField(User, related_name='friendship', on_delete=models.CASCADE)
    friends = models.ManyToManyField('self')

    objects = FriendshipManager()

    def friend_count(self):
        return self.friends.count()