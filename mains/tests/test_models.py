from django.test import TestCase

from django.contrib.auth.models import User
from mains.models import (
    Profile,
    Address,
    Friendship,
    FriendshipRequest,
    Job,
    Education
)

from datetime import date


class ProfileModelTest(TestCase):

    def setUp(self):

        # Create user.
        u1 = User.objects.create_user(
            username="dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = User.objects.create_user(
            username="1712371", password="12345", first_name="Dung", last_name="Nguyen")

        # Creaet Profile manually.
        p1 = Profile.objects.create(user=u1)
        p2 = Profile.objects.create(user=u2)

        # Update profile
        p1.bio = "Hello World"
        p1.birthday = date(1999, 2, 10)
        p1.relationship = "Single"
        p1.save()

        p2.bio = "Hello World"
        p2.birthday = date(1999, 12, 20)
        p2.relationship = "Single"
        p2.save()

    # def test_year_old(self):
    #     u1 = User.objects.get(username="dungdev1")
    #     u2 = User.objects.get(username="1712371")
    #     self.assertEquals(u1.profile.year_old, 21)
    #     self.assertEquals(u2.profile.year_old, 20)

    def test_name(self):
        u = User.objects.get(username="dungdev1")
        p = u.profile
        p.set_first_name("Dung")
        p.set_last_name("Nguyen")
        self.assertEquals(p.full_name, "Dung Nguyen")


class FriendshipModelTest(TestCase):

    # Setup
    def setUp(self):
        u1 = User.objects.create_user(
            "dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = User.objects.create_user(
            "1712371", password="12345", first_name="Dung", last_name="Nguyen")
        u3 = User.objects.create_user(
            "1234", password="12345", first_name="Dung", last_name="Nguyen")

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
        u1 = User.objects.create_user(
            "dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        u2 = User.objects.create_user(
            "1712371", password="12345", first_name="Dung", last_name="Nguyen")
        u3 = User.objects.create_user(
            "1234", password="12345", first_name="Dung", last_name="Nguyen")

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


# class JobModelTest(TestCase):

#     # Setup
#     def setUp(self):
#         u = User.objects.create_user(
#             "dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
#         p = Profile.objects.create(user=u)
#         j1 = Job.objects.create(
#             profile=u.profile, starting_month=2, starting_year=2008, ending_month=10, ending_year=2020)
#         j2 = Job.objects.create(
#             profile=u.profile, starting_month=12, starting_year=2008, ending_month=10, ending_year=2020)
#         j3 = Job(profile=u.profile, starting_month=2, starting_year=2019,
#                  position="Software developer", company="NET", city="HCMC")
#         j3.save()
#         # j4 = Job.objects.create(starting_month=2, starting_year=2008, ending_month=10, ending_year=2007)

#     def test_get_working_time(self):
#         j1 = Job.objects.all()[0]
#         j2 = Job.objects.all()[1]
#         j3 = Job.objects.all()[2]

#         print(j3)

#         self.assertEqual(j1.get_working_time(), (12, 8))
#         self.assertEqual(j2.get_working_time(), (11, 10))
#         self.assertEqual(j3.get_working_time(), (1, 9))


class EducationModelTest(TestCase):

    # setUp
    def setUp(self):
        u = User.objects.create_user(
            "dungdev1", password="12345", first_name="Dung", last_name="Nguyen")
        Profile.objects.create(user=u)
        e1 = Education(
            school_name="University of Science",
            starting_year=2017,
            ending_year=2021,
            description="Senior Student",
            concentration="Computer science",
            degree="Barchelor",
            profile=u.profile
        )
        e1.save()

    def test_validated_data(self):
        u = User.objects.get(username="dungdev1")
        print(u.profile.educations.all()[0])
