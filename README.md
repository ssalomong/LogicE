LogicE
=================

**A Logic Engine for Python**

Sergio Salomon Garcia, *sergio.salomon at alumnos.unican.es*


Notice: a better version in a more object-oriented style is in progress.
The actual handling with strings is evil!


Introduction
-----------

Logice is a logic engine implementation in Python that allows a
bit of logic programming style in this language.

In a *Prolog-like way*, **LogicE** allows to define logical predicates, 
facts and rules.


Quick Start
-----------

First, you import the module and get a new instance of the engine:

```python
import logice

logic_engine = logice.new()
```

Then, you can define new logical predicates and assert some facts:

```python
logic_engine.new_pred("is_man", 1)
#	is_man/1
#	is_man(?Something)

logic_engine.new_fact("is_man", "socrates")
logic_engine.new_fact("is_man", "plato")
```

You can define rules too:

```python
def is_mortal(someone):
	return logic_engine.eval("is_man", someone)
```


Finally, you should take a look to the file <code>midearth.py</code> for
an example of how the work is done with the engine.


