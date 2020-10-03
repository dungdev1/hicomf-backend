from django.test import TestCase

# from django.contrib.auth.models import User
from mains.models import Profile, Address, CustomUser

from datetime import date


class ProfileModelTest(TestCase):

    def setUp(self):

        # Create address.
        a1 = Address.objects.create(city="Ho Chi Minh", district="5")

        # Create user.
        u1 = CustomUser.objects.create_user(
            username="dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = CustomUser(username="1712371", password="12345", first_name="Dung", last_name="Nguyen")
        u2.save()
        u2.friends.add(u1)

        # Create Profile
        p1 = Profile(
            bio="Hello World",
            birthday=date(1999, 2, 10),
            relationship="Single",
            email="dungnguyen9599@gmail.com",
            phone_number="0339561922",
            user=u1
        )
        p1.save()
        p1.address.add(a1)

        p2 = Profile(
            bio="Hello World",
            birthday=date(1999, 10, 10),
            relationship="Single",
            email="dungnguyen9599@gmail.com",
            phone_number="0339561922",
            user=u1
        )
        p2.save()
        p2.address.add(a1)    

    def test_year_old(self):
        u = CustomUser.objects.get(username="dungdev1")
        self.assertEquals(u.basic_information.all()[0].year_old, 21)
        self.assertEquals(u.basic_information.all()[1].year_old, 20)

    def test_name(self):
        u = CustomUser.objects.get(username="dungdev1")
        p = u.basic_information.all()[0]
        p.set_first_name("Dung")
        p.set_last_name("Nguyen")
        self.assertEquals(p.full_name, "Dung Nguyen")