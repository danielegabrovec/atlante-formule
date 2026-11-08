"""Esempi Python autonomi e verificabili per i concetti di programmazione."""
EXAMPLES=[
'''class Counter:
    def __init__(self, value=0):
        self.value = value
a, b = Counter(2), Counter(7)
assert a.value == 2 and b.value == 7
''',
'''class Counter:
    def __init__(self):
        self.value = 0
    def increment(self):
        self.value += 1
c = Counter()
c.increment()
assert c.value == 1
''',
'''class Interval:
    def __init__(self, start, end):
        if start > end:
            raise ValueError("Intervallo non valido")
        self.start, self.end = start, end
assert Interval(1, 3).end == 3
''',
'''class Account:
    def __init__(self):
        self._balance = 0  # convenzione interna di Python
    def deposit(self, amount):
        if amount < 0:
            raise ValueError("Importo negativo")
        self._balance += amount
    @property
    def balance(self):
        return self._balance
a = Account()
a.deposit(5)
assert a.balance == 5
''',
'''class MemoryStore:
    def __init__(self):
        self.items = []
    def save(self, value):
        self.items.append(value)
class Service:
    def __init__(self, store):
        self.store = store
    def add(self, value):
        self.store.save(value)
s = MemoryStore()
Service(s).add("dato")
assert s.items == ["dato"]
''',
'''class Shape:
    def area(self):
        raise NotImplementedError
class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2
assert Square(3).area() == 9
''',
'''class Square:
    def area(self):
        return 9
class Rectangle:
    def area(self):
        return 8
assert [s.area() for s in (Square(), Rectangle())] == [9, 8]
''',
'''def withdraw(balance, amount):
    if not 0 <= amount <= balance:
        raise ValueError("Precondizione non rispettata")
    result = balance - amount
    assert result >= 0
    return result
assert withdraw(10, 3) == 7
''',
'''class NumberStore:
    def save(self, number):
        return number
class LoggedStore(NumberStore):
    def save(self, number):
        # Mantiene gli ingressi ammessi dal contratto base.
        return super().save(number)
assert LoggedStore().save(-2) == -2
''',
'''def total(prices):
    return sum(prices)
def present(value):
    return f"Totale: {value}"
assert present(total([2, 3])) == "Totale: 5"
''',
'''class Service:
    def __init__(self, repository):
        self.repository = repository
    def read(self):
        return self.repository.load()
class FakeRepository:
    def load(self):
        return 42
assert Service(FakeRepository()).read() == 42
''',
'''a = [1, 2]
b = [1, 2]
assert a == b
assert a is not b
''',
'''a = [1]
b = a
b.append(2)
assert a == [1, 2] and a is b
''',
'''from copy import deepcopy
a = [[1]]
shallow = a.copy()
deep = deepcopy(a)
a[0].append(2)
assert shallow == [[1, 2]]
assert deep == [[1]]
''',
'''def parse_integer(text):
    try:
        return int(text)
    except ValueError:
        return None  # esito esplicito del contratto
assert parse_integer("12") == 12
assert parse_integer("abc") is None
''',
'''from io import StringIO
stream = StringIO("dato")
with stream as resource:
    assert resource.read() == "dato"
assert stream.closed
''',
'''iterator = iter([2, 4])
assert next(iterator) == 2
assert list(iterator) == [4]
assert list(iterator) == []
''',
'''from typing import Protocol
class HasArea(Protocol):
    def area(self) -> float: ...
class Tile:
    def area(self):
        return 4.0
def measured(value: HasArea):
    return value.area()
assert measured(Tile()) == 4.0
''',
'''def apply_price(value, strategy):
    return strategy(value)
assert apply_price(100, lambda x: x * 0.9) == 90
''',
'''class Signal:
    def __init__(self):
        self.listeners = []
    def emit(self, value):
        for listener in tuple(self.listeners):
            listener(value)
received = []
signal = Signal()
signal.listeners.append(received.append)
signal.emit(7)
assert received == [7]
''',
'''class Model:
    def __init__(self):
        self.value = 4
def view_text(model):
    return str(model.value)
assert view_text(Model()) == "4"
''',
'''def divide(a, b):
    if b == 0:
        raise ValueError("Denominatore nullo")
    return a / b
assert divide(6, 3) == 2
try:
    divide(1, 0)
except ValueError:
    pass
else:
    raise AssertionError("Errore atteso")
''',
'''values = [3, 7, 9]
lookup = set(values)
assert 7 in values and 7 in lookup
# L'esito coincide; i modelli di costo sono differenti.
''',
'''def factorial(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("Intero non negativo richiesto")
    return 1 if n == 0 else n * factorial(n - 1)
assert factorial(0) == 1 and factorial(5) == 120
''',
]

def attach_code(cards):
    for c in cards:
        if c['id'].startswith('programmazione-'):
            c['code_example']={'language':'Python 3','source':EXAMPLES[int(c['id'].split('-')[1])-1]}
