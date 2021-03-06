import sys
from datetime import datetime
from collections import defaultdict
from twisted.internet.defer import Deferred
from twisted.internet import reactor

TIME_FORMATS = (
  '%Y-%m-%dT%H:%M:%S',
)

def merge(a, b):
  a = a.copy()
  a.update(b)
  return a

def groups_of(n, x):
  if n > len(x) or n < 1:
    raise ValueError(n)

  ys = []
  while True:
    if len(x) < n:
      if len(x): ys.append(x)
      return ys
    y, x = x[:n], x[n:]
    ys.append(y)

def n_groups(n, x):
  if n > len(x) or n < 1:
    raise ValueError(n)

  z = (len(x) + n - 1) / n

  ys = []
  while True:
    if len(x) < z:
      if len(x): ys.append(x)
      assert len(ys) == n, ys
      return ys
    y, x = x[:z], x[z:]
    ys.append(y)

    rest = n - len(ys)
    if rest: z = (len(x) + rest - 1) / rest

def flatten(x):
  x = list(x)
  i = 0
  while i < len(x):
    while isinstance(x[i], (list, tuple)):
      if not x[i]:
        x.pop(i)
        i -= 1
        break
      else:
        x[i:i + 1] = x[i]
    i += 1
  return x

def mix_one(f, a, b):
  ap = (1 - f) * 1000
  bp = f * 1000
  return (a * ap + b * bp) / (ap + bp)

def mix(f, a, b):
  f = (f,) * len(a)
  return tuple((mix_one(*fab) for fab in zip(f, a, b)))

def leading(line_height, item_height):
  return line_height - item_height

class EventEmitter(Deferred):
  # The special event name "*" will register a listener for all events.
  def addListener(self, name, listener):
    assert callable(listener)
    self.init_listeners()
    self.listeners[name].append(listener)
    return self

  def chainEvents(self, other):
    self.addListener('*', other.emit)

  def emit(self, name, *args, **kw):
    self.init_listeners()
    for listener in self.listeners[name] + self.listeners['*']:
      reactor.callLater(0, listener, name, *args, **kw)

  def init_listeners(self):
    self.listeners = getattr(self, 'listeners', defaultdict(list))
