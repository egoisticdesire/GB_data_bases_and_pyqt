"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
(Внимание! Аргументом сабпроцеса должен быть список, а не строка!!! Для уменьшения времени работы скрипта при проверке
нескольких ip-адресов, решение необходимо выполнить с помощью потоков)

2. Написать функцию host_range_ping() (возможности которой основаны на функции из примера 1) для перебора ip-адресов
из заданного диапазона. Меняться должен только последний октет каждого адреса. По результатам проверки должно выводиться
соответствующее сообщение.

3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном случае
результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль tabulate).
Таблица должна состоять из двух колонок и выглядеть примерно так:

    Reachable | Unreachable
    ----------|------------
    10.0.0.1  | 10.0.0.3
    10.0.0.2  | 10.0.0.4
"""