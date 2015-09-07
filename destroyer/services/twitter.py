"""twitter.py - Module for Twitter service functionality"""

import time

import click
import tweepy
from tabulate import tabulate

from ..settings import consumer_key, consumer_secret
from ..settings import access_token, access_token_secret
from ..utils import get_random_prompt


class TwitterDestroyer():
    """Destroyer class for Twitter integration.
    """
    def __init__(self, unfollow_non_followers=False):
        """Initializer method"""
        self.auth = tweepy.auth.OAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth_handler=self.auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=True)

        self.unfollow_non_followers = unfollow_non_followers
        self.logger = None

    def _unfollow(self, user):
        """Private method that takes a Tweepy user object and unfollows the user.
        The user that is unfollowing the user passed into this function is the user
        authenticated with the current Tweepy API class instance."""
        try:
            user.unfollow()
        except:
            time.sleep(5)
            user.unfollow()

    def _unfollow_non_friends(self, non_friends):
        """Private method that takes a list of non_friends and calls _unfollow on them"""
        for non_friend in non_friends:
            self._unfollow(non_friend)

    def _unfollow_friends(self, friends):
        """Private method that takes a list of friends and calls _unfollow on them"""
        for friend_id, friend in friends.items():
            friend_is_following = False
            if friend.following:
                friend_is_following = True
            friend_data = [[friend.name, friend.screen_name, friend.description, friend_is_following, friend.followers_count, friend.location]]
            friend_headers = ['Name', 'Handle', 'Bio', 'Follows you?', 'Followers', 'Location']

            print('You are following {friend}.'.format(friend=friend.name))
            print(tabulate(friend_data, friend_headers, tablefmt='fancy_grid'))

            answer = click.confirm('{prompt}'.format(prompt=get_random_prompt(friend.screen_name, 'question')))
            if not answer:
                print('Not unfollowing {friend}.'.format(friend=friend.screen_name))
                continue
            self._unfollow(friend)
            print('{prompt}'.format(prompt=get_random_prompt(friend.screen_name, 'insult')))

    def destroy(self):
        """Public method that implements the abstracted functionality of unfollowing users"""
        if self.unfollow_non_followers:
            followers = dict()
            print('Getting followers')
            for follower in tweepy.Cursor(self.api.followers, skip_status=True, include_user_entities=False, count=1000).pages():
                print(follower.screen_name)
                followers[follower.id] = follower
            print('Finished getting followers')

        friends = dict()
        print('Getting friends')
        for friend in tweepy.Cursor(self.api.friends, skip_status=True, include_user_entities=False, count=200).items():
            print(friend.screen_name)
            friends[friend.id] = friend
        print('Finished getting friends')

        if self.unfollow_non_followers:
            non_friends = [friend for friend in friend_objects if friend.id not in followers]

        if self.unfollow_non_followers:
            answer = click.confirm('Are you sure you want to unfollow all the people you are following that are not following you?', abort=True)
            self._unfollow_non_friends(non_friends)
        else:
            self._unfollow_friends(friends)
