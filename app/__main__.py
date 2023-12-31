from doctest import master
from instagrapi.exceptions import LoginRequired
from typing import Dict, List
import schedule
from instagrapi import Client
import logging

logger = logging.getLogger()

master = {
  "username": "",
  "password": ""
}

children = [{
    "username": "",
    "password": ""
  },
  {
    "username": "",
    "password": ""
  },
  {
    "username": "",
    "password": ""
  }
]

def get_interset(masters: List[str], children: List[str]):
  l: List[str] = []
  
  for child in children:
    if child not in masters:
      l.append(child)
  return l;

class User:
  cl: Client
  def user_login(self, username, password):
    self.cl = Client()
    session = self.cl.load_settings(f"sessions/{username}.json")

    login_via_session = False
    login_via_pw = False

    if session:
      try:
        self.cl.set_settings(session)
        self.cl.login(username, password)

        try:
          self.cl.get_timeline_feed()
        except LoginRequired:
          logger.info("Session is invalid, need to login via username and password")

          old_session = self.cl.get_settings()

          # use the same device uuids across logins
          self.cl.set_settings({})
          self.cl.set_uuids(old_session["uuids"])

          self.cl.login(username, password)
          login_via_session = True
      except Exception as e:
        logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
      try:
        logger.info("Attempting to login via username and password. username: %s" % username)
        if self.cl.login(username, password):
          login_via_pw = True
      except Exception as e:
        logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")
      
  def follow_users_with_tag(self, key: str):
    self.cl.user_follow(key)
    return print(f'followed user {key}')
    
  def check_users_following(self):
    return self.cl.user_following(self.cl.user_id);
  
  def check_users_followers(self):
    return self.cl.user_followers(self.cl.user_id);
  
  def user_unfollow(self, user_ids: Dict):
    for user_id in user_ids:
      self.cl.user_unfollow(user_id)
    


class App :
    master_account: User;
    children = List[User];
    
    def __init__(self):
      self.master_account = User();
      for i in range(children):
        self.children[i] = User();
        
    def users_login(self):
      self.master_account.user_login(master.get('username'), master.get('password'))
      for i in range(children):
        self.children[i].user_login(children[i].get('username'), children[i].get('password'))
        
    def follow_users_by_tag(self, hash_tag):
      users_with_tag = self.master_account.cl.hashtag_medias_recent(hash_tag, 7)
      
      for i, user in enumerate(users_with_tag):
        self.children[0].follow_users_with_tag(user.user.pk)
        self.children[1].follow_users_with_tag(user.user.pk)
        self.children[2].follow_users_with_tag(user.user.pk)
        
        
    def check_users_followers(self):
      master_list: List[str] = self.master_account[0].check_users_following()
      user_list: Dict = self.children[0].check_users_followers()
      
      filtered = get_interset(user_list, master_list);
      
      self.children[0].user_unfollow(filtered)
      self.children[1].user_unfollow(filtered)
      self.children[2].user_unfollow(filtered)
      

def initialize():       
  app = App();

  app.users_login();
  app.check_users_followers();
  
  schedule.every(12).hour.do(app.follow_users_by_tag)
  schedule.every(24).hour.do(app.unfollow_user)
        