import datetime
import pathlib
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class ClientDB:
    """
    A wrapper class for working with the client database.
    Uses SQLite database, implemented with SQLAlchemy ORM and uses declarative approach.
    """

    Base = declarative_base()

    class KnownUsers(Base):
        """Display for the table of all users."""

        __tablename__ = 'known_users'
        id = Column(Integer, primary_key=True)
        username = Column(String)

        def __init__(self, username):
            self.username = username

    class MessageHistory(Base):
        """Display for the transmitted message statistics table."""

        __tablename__ = 'messages_history'
        id = Column(Integer, primary_key=True)
        contact = Column(String)
        direction = Column(String)
        message = Column(Text)
        date = Column(DateTime)

        def __init__(self, contact, direction, message):
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts(Base):
        """Display for the table of all contacts."""
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

        def __init__(self, contact):
            self.name = contact

    def __init__(self, name):
        path_to_db = pathlib.Path(__file__).absolute().joinpath(f'../client_{name}.db3')

        self.engine = create_engine(
            f'sqlite:///{path_to_db}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """A method that adds a contact to the database."""
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        """A method that clears a table with a list of contacts."""
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def del_contact(self, contact):
        """A method that removes a specific contact."""
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def add_users(self, users_list):
        """A method that populates the table of known users."""
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """A method that saves the message to the database."""
        message_row = self.MessageHistory(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """A method that returns a list of all contacts."""
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """A method that returns a list of all known users."""
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """A method that checks if the user exists."""
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        return False

    def check_contact(self, contact):
        """A method that checks if a contact exists."""
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        return False

    def get_history(self, contact):
        """A method that returns the history of messages with a specific user."""
        query = self.session.query(self.MessageHistory).filter_by(contact=contact)

        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    test_db = ClientDB('test1')
    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message(
        'test1', 'test2',
        f'Привет! я тестовое сообщение от {datetime.datetime.now()}!'
    )
    test_db.save_message(
        'test2', 'test1',
        f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!'
    )
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(test_db.get_history('test2'))
    print(sorted(test_db.get_history('t2'), key=lambda item: item[3]))
    print(test_db.get_history('test3'))
    test_db.del_contact('test4')
    print(test_db.get_contacts())
