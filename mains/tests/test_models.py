from django.test import TestCase

from django.contrib.auth.models import User
from mains.models import Profile, Address, Friendship, FriendshipRequest

from datetime import date


class ProfileModelTest(TestCase):

    def setUp(self):

        # Create address.
        a1 = Address.objects.create(city="Ho Chi Minh", district="5")

        # Create user.
        u1 = User.objects.create_user(
            username="dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = User(username="1712371", password="12345", first_name="Dung", last_name="Nguyen")
        u2.save()

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
            user=u2
        )
        p2.save()
        p2.address.add(a1)    

    def test_year_old(self):
        u1 = User.objects.get(username="dungdev1")
        u2 = User.objects.get(username="1712371")
        self.assertEquals(u1.basic_information.year_old, 21)
        self.assertEquals(u2.basic_information.year_old, 20)

    def test_name(self):
        u = User.objects.get(username="dungdev1")
        p = u.basic_information
        p.set_first_name("Dung")
        p.set_last_name("Nguyen")
        self.assertEquals(p.full_name, "Dung Nguyen")


class FriendshipModelTest(TestCase):
    
    # Setup
    def setUp(self):
        u1 = User.objects.create_user("dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = User.objects.create_user("1712371", password="12345", first_name="Dung", last_name="Nguyen")
        u3 = User.objects.create_user("1234", password="12345", first_name="Dung", last_name="Nguyen")

        f1 = Friendship(user=u1)
        f2 = Friendship(user=u2)
        f3 = Friendship(user=u3)
        f1.save()
        f2.save()
        f3.save()
        f1.friends.add(f2, f3)

    def test_friend_count(self):
        u1 = User.objects.get(username='dungdev1')
        u2 = User.objects.get(username='1712371')
        self.assertEqual(u1.friendship.friend_count(), 2)
        self.assertEqual(u2.friendship.friend_count(), 1)

    def test_check_friends_of_user(self):
        u1 = User.objects.get(username='dungdev1')
        u2 = User.objects.get(username='1712371')
        u3 = User.objects.get(username='1234')
        self.assertEqual(Friendship.objects.friends_of(u1).count(), 2)
        self.assertEqual(Friendship.objects.friends_of(u2).count(), 1)
        self.assertEqual(Friendship.objects.friends_of(u3).count(), 1)

    def test_check_are_friend_of_user(self):
        u1 = User.objects.get(username='dungdev1')
        u2 = User.objects.get(username='1712371')
        u3 = User.objects.get(username='1234')
        self.assertTrue(Friendship.objects.are_friends(u1, u2))
        self.assertTrue(Friendship.objects.are_friends(u1, u3))
        self.assertFalse(Friendship.objects.are_friends(u3, u2))

    def test_unfriend(self):
        u1 = User.objects.get(username='dungdev1')
        u2 = User.objects.get(username='1712371')
        Friendship.objects.befriend(u1, u2)
        self.assertTrue(Friendship.objects.are_friends(u1, u2))
        Friendship.objects.unfriend(u1, u2)
        self.assertFalse(Friendship.objects.are_friends(u1, u2))


class FriendshipRequestModelTest(TestCase):

    # Setup
    def setUp(self):
        u1 = User.objects.create_user("dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = User.objects.create_user("1712371", password="12345", first_name="Dung", last_name="Nguyen")
        u3 = User.objects.create_user("1234", password="12345", first_name="Dung", last_name="Nguyen")

        f1 = Friendship.objects.create(user=u1)
        f2 = Friendship.objects.create(user=u2)
        f3 = Friendship.objects.create(user=u3)

        f_request = FriendshipRequest.objects.create(from_user=u1, to_user=u2)

    def test_accept_request(self):
        u1 = User.objects.get(username='dungdev1')
        u2 = User.objects.get(username='1712371')
        u3 = User.objects.get(username='1234')
        f_request = FriendshipRequest.objects.get(from_user=u1, to_user=u2)
        f_request.accept()
        self.assertTrue(Friendship.objects.are_friends(u1, u2))
        self.assertFalse(Friendship.objects.are_friends(u1, u3))
        self.assertFalse(Friendship.objects.are_friends(u2, u3))

    def test_decline_request(self):
        u1 = User.objects.get(username='dungdev1')
        u2 = User.objects.get(username='1712371')
        f_request = FriendshipRequest.objects.get(from_user=u1, to_user=u2)
        f_request.decline()
        self.assertFalse(Friendship.objects.are_friends(u1, u2))