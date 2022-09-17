import datetime
from pprint import pprint
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ServerDB:
    """
    A wrapper class for working with the server database.
    It uses a SQLite database, implemented with SQLAlchemy ORM and uses a declarative approach.
    """

    Base = declarative_base()

    class AllUsers(Base):
        """Displaying a table of all users."""

        __tablename__ = 'all_users'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        last_login = Column(DateTime)
        pswd_hash = Column(String)
        public_key = Column(Text)

        def __init__(self, name, pswd_hash):
            self.name = name
            self.last_login = datetime.datetime.now()
            self.pswd_hash = pswd_hash
            self.public_key = None

    class ActiveUsers(Base):
        """Displaying a table of active users."""
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        login_time = Column(DateTime)

        def __init__(self, user, ip, port, login_time):
            self.user = user
            self.ip = ip
            self.port = port
            self.login_time = login_time

    class LoginHistory(Base):
        """Displaying the login history table."""
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        login_time = Column(DateTime)
        ip = Column(String)
        port = Column(Integer)

        def __init__(self, user, login_time, ip, port):
            self.user = user
            self.login_time = login_time
            self.ip = ip
            self.port = port

    class UsersContacts(Base):
        """Displaying the table of user contacts."""
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        contact = Column(String, ForeignKey('all_users.id'))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

    class UsersHistory(Base):
        """Displaying the activity history table."""
        __tablename__ = 'users_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):

        self.engine = create_engine(
            f'sqlite:///{path}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        # Когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port, key):
        """
        The method that executed when the user logs in, writes the login fact to the database.
        Updates the user's public key when it changes.
        """

        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        # Проверяем корректность ключа. Если пришел новый ключ - сохраняем
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            if user.public_key != key:
                user.public_key = key
        # Если нет, то создаём нового пользователя
        else:
            raise ValueError('User not registered')

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        # Создаем экземпляр класса self.ActiveUsers, через который передаем данные в таблицу
        new_active_user = self.ActiveUsers(user.id, ip, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # и сохранить в историю входов
        # Создаем экземпляр класса self.LoginHistory, через который передаем данные в таблицу
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip, port)
        self.session.add(history)

        # Сохраняем изменения
        self.session.commit()

    def add_user(self, name, pswd_hash):
        """
        User registration method. Accepts a name and password hash, creates an entry in the statistics table.
        """

        user_row = self.AllUsers(name, pswd_hash)
        self.session.add(user_row)
        self.session.commit()

        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        """A method that removes a user from the database."""

        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        """A method to get the hash of the user's password."""

        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pswd_hash

    def get_public_key(self, name):
        """A method for getting the user's public key."""

        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.public_key

    def check_user(self, name):
        """A method that checks for the existence of a user."""

        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        return False

    def user_logout(self, username):
        """A method fixing user disconnections."""

        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы AllUsers
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        # Удаляем его из таблицы активных пользователей
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        # Применяем изменения
        self.session.commit()

    def process_message(self, sender, recipient):
        """A method that writes the fact of message transmission to the statistics table."""

        # Получаем ID отправителя и получателя
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def add_contact(self, user, contact):
        """A method for adding a contact for the user."""

        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        """A method for deleting a user's contact."""

        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return

        # Удаляем требуемое
        self.session.query(self.UsersContacts) \
            .filter(self.UsersContacts.user == user.id, self.UsersContacts.contact == contact.id).delete()

        self.session.commit()

    def users_list(self):
        """A method that returns a list of known users with last login time."""

        # Запрос строк таблицы пользователей.
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login)
        # Возвращаем список кортежей
        return query.all()

    def active_users_list(self):
        """A method returning a list of active users."""

        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.session \
            .query(self.AllUsers.name, self.ActiveUsers.ip, self.ActiveUsers.port, self.ActiveUsers.login_time) \
            .join(self.AllUsers)
        # Возвращаем список тюплов
        return query.all()

    def login_history(self, username=None):
        """A method that returns the login history."""

        # Запрашиваем историю входа
        query = self.session \
            .query(self.AllUsers.name, self.LoginHistory.login_time, self.LoginHistory.ip, self.LoginHistory.port) \
            .join(self.AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def get_contacts(self, username):
        """A method that returns a list of the user's contacts."""

        # Запрашиваем указанного пользователя
        user = self.session.query(self.AllUsers).filter_by(name=username).one()

        # Запрашиваем его список контактов
        query = self.session.query(self.UsersContacts, self.AllUsers.name) \
            .filter_by(user=user.id).join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    def message_history(self):
        """A method that returns message statistics."""

        query = self.session \
            .query(self.AllUsers.name, self.AllUsers.last_login, self.UsersHistory.sent, self.UsersHistory.accepted) \
            .join(self.AllUsers)
        # Возвращаем список кортежей
        return query.all()
