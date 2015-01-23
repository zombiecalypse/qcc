# Purpose

Tests can either check specific examples, or general properties. The former is
what you typically get from testing frameworks, the latter is what you get
here. The inspiration is obviously the excellent
[QuickCheck](https://github.com/nick8325/quickcheck) library, and this library
is compatible to the [qc](https://github.com/dbravender/qc) library, but
offers a bit more customization.

# Usage

Let's say we want to check a property, for example `a+b == b+a` for integers,
but instead of testing specific examples, we want to say that it holds for all
of them. We can decorate the test function with the `@forall` for this:

```python
    # tests1.py
    from qcc import forall, floats

    @forall(tries=1000, a=floats(), b=floats())
    def test_commutativity(a, b):
        assert a+b == b+a
```

The `tries` defines how many random generated examples are tested, all
arguments are passed as keyword arguments.

As a counterexample, let's see 

```python
    # tests2.py
    from qcc import forall, floats

    @forall(tries=1000, a=floats(), b=floats(), c=floats())
    def test_associativity(a, b, c):
        assert (a+b)+c == a+(b+c)
```

Now when we run the test, we find the following:

```
    $ nose2 test2

    Counter example:
    {'a': 2.29560875082814e+17,
     'b': 762573.8629461317,
     'c': -36504139162.02817}
```

There are more complex data structures, for example lists:

```python
    # tests3.py
    from qcc import forall, lists, non_negative

    @forall(tries=1000, l=lists(non_negative()))
    def test_monotonicity(l):
        assert not l or sum(l) >= max(l)
```

If you want to have more reliable results, you can set the seed either with
the environment variable `QC_SEED` or by directly instanciating an
`Arbitrary` instance:

```python
    # tests4.py
    from qcc import Arbitrary

    test = Arbitrary(seed=1)

    @test.forall(tries=1000, a=test.floats(), b=test.floats(), c=test.floats())
    def test_associativity(a, b, c):
        assert (a+b)+c == a+(b+c)
```

```
    $ nose2 test4
    Counter example:
    {'a': -6.047492685383753e+65,
     'b': 3.596506239937929e+58,
     'c': 2.137023042150319e+75}
```

```
    $ nose2 test4
    Counter example:
    {'a': -6.047492685383753e+65,
     'b': 3.596506239937929e+58,
     'c': 2.137023042150319e+75}
```


Currently the seed isn't printed on a failing example, but this is planned
feature.

The functions generating samples available are at the moment:

* `integers`
  takes no arguments and gives `int` or `long`
* `non_negative`
  takes no arguments and gives `int` or `long` >= 0
* `floats`
  takes no arguments and gives `float`
* `lists`
  takes argument `items` that gives the generator for the elements and
  returns a list with random elements.
* `tuples`
  takes argument `items` that gives the generator for the elements and
  returns a tuple with random elements of varying size.
* `dicts`
  takes argument `key_values` (or `keys` and `values` separately) that
  gives the generator for the elements and returns a dicts with random
  elements of varying size. If the `keys` and `values` are given, they are
  sampled independently.
* `unicodes`
  takes argument `min` and `max` (defaulting to 0 and 512) that gives the
  generator for the elements and returns a unicode string with random elements
  between the min and max ord number.
* `chars`
  takes argument `min` and `max` (defaulting to 0 and 255) that gives the
  generator for the elements and returns a string with random elements
  between the min and max ord number.
* `objects`
  takes argument `_object_class`, `_fields`, and other arguments. The
  additional arguments are used as generators into the `_object_class`
  constructor. The `_fields` are set afterwards.

# Installation

Until the package is uploaded to `PyPI`, the following procedure will install
it.

    sudo pip install -e git://github.com/zombiecalypse/qcc.git#egg=qcc
