# import os

from setuptools import setup, find_packages

# path = os.path.join(os.getcwd(), '../client_dist/client/common/img')
# images = os.listdir(path)

setup(
    name="first-ego-mess-client",
    version="0.1.3",
    description="Messenger Client",
    author="Ivan Ivanov",
    author_email="iv.iv@yandex.ru",
    packages=find_packages(),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
    # data_files=[(path, images)]
)
