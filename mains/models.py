from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import date


class Address(models.Model):
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    house_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.house_number}, {self.street}, {self.district}, {self.city}."

class CustomUser(AbstractUser):
    friends = models.ManyToManyField("self")

    def __str__(self):
        return self.username


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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="basic_information")

    @property
    def year_old(self):
        "Returns the year old of user, if birthday is undefined, return 0."
        if self.birthday:
            today = date.today()
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

