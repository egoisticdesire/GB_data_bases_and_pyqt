from setuptools import setup, find_packages

setup(name="first-ego-mess-client",
      version="0.1.2",
      description="Messenger Client",
      author="Ivan Ivanov",
      author_email="iv.iv@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
