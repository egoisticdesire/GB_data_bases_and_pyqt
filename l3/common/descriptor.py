import logging

LOGGER = logging.getLogger('server')


class Port:
    def __set__(self, instance, value):
        # instance - <__main__.Server object at 0x000000D582740C50>
        if not 1023 < value < 65536:
            LOGGER.error('Номер порта должен быть в диапазоне от 1024 до 65635.')
            exit(1)

        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # owner - <class '__main__.Server'>
        # name - port
        self.name = name
