"""
Logic Engine for Python
Logice

TEST creating a knowledge base about the Middle-Earth.
... A really simple one.


Sergio Salomon Garcia <sergio.salomon@alumnos.unican.es>
"""
import logice


engine = logice.new()


# Definition of some predicates
engine.new_pred("parent", 2)
engine.new_pred("gender", 2)
engine.new_pred("race", 2)

p_race = lambda who,r: engine.new_fact("race", who, r)
p_sex = lambda who, s: engine.new_fact("gender", who, s)
p_parnt = lambda x, y: engine.new_fact("parent", x, y)


# Assert some facts in the knowledge base
p_race("frodo", "hobbit")
p_race("bilbo", "hobbit")
p_race("primula", "hobbit")
p_race("legolas", "elf")
p_race("aragorn", "human")
p_race("arathorn", "human")
p_race("gandalf", "ainur")
p_race("treebeard", "ent")
p_race("boromir", "human")
p_race("denethor", "human")
p_race("faramir", "human")

p_sex("frodo", "male")
p_sex("primula", "female")
p_sex("legolas", "male")
p_sex("aragorn", "male")
p_sex("arathorn", "male")
p_sex("boromir", "male")
p_sex("denethor", "male")
p_sex("faramir", "male")

p_parnt("arathorn", "aragorn")
p_parnt("denethor", "faramir")
p_parnt("denethor", "boromir")
p_parnt("primula", "frodo")


# Show the actual state of the engine
print engine
print


# Define the rule is_child
def is_child(eng, child, parent):
	return eng.query("parent", parent, child)

child = lambda x, y: is_child(engine, x, y)

print "child(aragorn, arathorn):", child("aragorn", "arathorn")
print "child(frodo, primula):", child("frodo", "primula")
print "child(C, P):", child('C', 'P')
print


# Define the rule is_mother
def is_mother(eng, mother, child):
	# this has a tricky syntax...
	m = eng.query("gender", mother, "female")

	if m == True:
		# mother already has a valid value
		return eng.query("parent", mother, child)
	elif m == False:
		return False
	else:
		# The first result has to be processed
		result = []
		for x in m:
			aux_m = x.lstrip(mother + " = ")
			aux_c = eng.query("parent", aux_m, child)
			result.append((x, aux_c,))
		return result

mother = lambda x, y: is_mother(engine, x, y)

print "mother(primula, frodo):", mother("primula", "frodo")
print "mother(M, frodo):", mother('X', "frodo")
print "mother(denethor, faramir):", mother("denethor", "faramir")
print "mother(M, C):", mother('M', 'C')
print


# Clears the knowledge base
engine.clear()

print engine


