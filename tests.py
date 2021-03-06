from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Poll, Option

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_polls(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four polls
        now = datetime.utcnow()
        p1 = Poll(body="poll from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Poll(body="poll from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Poll(body="poll from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Poll(body="poll from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed polls of each user
        f1 = u1.followed_polls().all()
        f2 = u2.followed_polls().all()
        f3 = u3.followed_polls().all()
        f4 = u4.followed_polls().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

    def test_vote(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        option = Option(body='1')
        db.session.add(option)
        u.vote(option)
        db.session.commit()
        test = u.has_voted_option(option)
        self.assertTrue(test)

    def test_unvote(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        option = Option(body='1')
        db.session.add(option)
        u.vote(option)
        u.unvote(option)
        db.session.commit()
        test = u.has_voted_option(option)
        self.assertFalse(test)

    def test_makeAdmin(self):
        u = User(username='susan', email='susan@example.com', is_admin=False)
        db.session.add(u)
        u.make_admin(u)
        db.session.commit()
        test = u.is_admin
        self.assertTrue(test)

    def test_removeAdmin(self):
        u = User(username='susan', email='susan@example.com', is_admin=True)
        db.session.add(u)
        u.remove_admin(u)
        db.session.commit()
        test = u.is_admin
        self.assertFalse(test)

    def test_addOption(self):
        poll = Poll(id=1, title='test', body='test')
        db.session.add(poll)
        option = Option(body='1', id_poll=poll.id)
        db.session.add(option)
        db.session.commit()
        self.assertEqual(option.id_poll, poll.id) 

    def test_deleteOption(self):
        poll = Poll(id=2, title='test', body='test')
        db.session.add(poll)
        db.session.commit()
        option = Option(body='1', id_poll=poll.id)
        db.session.add(option)
        db.session.commit()
        db.session.delete(option)
        db.session.commit()
        test=db.session.query(Option).filter(Option.id_poll==poll.id).first()==None
        self.assertTrue(test)
    
    def test_createPoll(self):
        poll = Poll(id=1, title='test', body='test')
        db.session.add(poll)
        db.session.commit()
        self.assertEqual(poll.id, 1)

    def test_deletePoll(self):
        poll = Poll(id=1, title='test', body='test')
        db.session.add(poll)
        db.session.commit()
        poll = db.session.query(Poll).filter(poll.id==1).first()
        db.session.delete(poll)
        db.session.commit()
        test=db.session.query(Poll).filter(poll.id==1).first()==None
        self.assertTrue(test)

if __name__ == '__main__':
    unittest.main(verbosity=2)