import unittest
from mega_money_millions.utils import safe


class Level3:
  def __init__(self):
    self.c: int = 1
    self.d: int = 2


class Level2:
  def __init__(self):
    self.b: Level3 = Level3()


class Level1:
  def __init__(self):
    self.a: Level2 = Level2()


class TestPortfolio(unittest.TestCase):
  def test_safe(self):
    obj = Level1()

    self.assertEqual(safe(obj, 'a.b.c'), 1)
    self.assertEqual(safe(obj, ['a', 'b', 'c']), 1)
    self.assertEqual(safe(obj, 'a.b.d'), 2)
    self.assertEqual(safe(obj, ['a', 'b', 'd']), 2)
    self.assertEqual(safe(obj, 'a'), obj.a)
    self.assertEqual(safe(obj, 'a.b'), obj.a.b)
    self.assertEqual(safe(obj, 'a.b.e'), None)
    self.assertEqual(safe(obj, 'x'), None)
