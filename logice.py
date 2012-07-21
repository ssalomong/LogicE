"""
Logic Engine for Python
Logice

A logic engine implementation in Python that allows a
bit of logic programming style in this language.


Sergio Salomon Garcia <sergio.salomon@alumnos.unican.es>
"""

# import inspect	
# para poder conocer en tiempo de ejecucion aridad de una funcion (regla)
#	inspect.getargspec()


class Logice():

	def __init__(self):
		"""
		Inicializa la base de conocimiento del motor.
		"""
		# Mapa de los predicados (y su aridad) definidos
		self.__predicates = {}
		# Mapa de hechos
		self.__facts = {}
		# Mapa de atomos (dominio)
		self.__atoms = set()

		# self.__rules = {} # TODO ?


	def clear(self):
		"""
		Limpia la base de datos del motor.
		"""
		self.__predicates =  {}
		self.__facts = {}
		self.__atoms = set()



	##########################
	#### LOGIC ENGINE FUNCTIONS
	##########################

	def new_pred(self, name, arity):
		"""
		Define un nuevo predicado de aridad 'arity', siempre
		que no haya sido definido ya otro predicado 'name'.
		"""
		if type(name) != str or type(arity) != int:
			raise NameError("The arguments type doesn't match.")
		elif arity < 0:
			raise NameError("Arity error.")

		if name in self.__predicates:
			raise NameError("The predicate is already defined.")
		else:
			self.__predicates[name] = arity


	def exist_pred(self, name, arity):
		"""
		Indica si existe un predicado 'name/arity' definido.
		"""
		if type(name) != str or type(arity) != int:
			raise NameError("The arguments type doesn't match.")
		elif arity < 0:
			raise NameError("Arity error.")

		result = False
		if name in self.__predicates and self.__predicates[name] == arity:
			result = True

		return result


	def del_pred(self, name, arity):
		"""
		Elimina un predicado, junto con todos los hechos de este, 
		de la base de conocimiento.
		"""
		if type(name) != str or type(arity) != int:
			raise NameError("The arguments type doesn't match.")
		elif arity < 0:
			raise NameError("Arity error.")

		result = False
		if name not in self.__predicates:
			raise NameError("The predicate hasn't been defined.") # ?
		# elif self.__predicates[name] != arity:
		# 	# Nothing... ?
		elif self.__predicates[name] == arity:
			del self.__predicates[name]
			if name in self.__facts:
				del self.__facts[name]
			result = True

		return result



	def new_fact(self, pred, *args):
		"""
		Define un nuevo hecho 'pred(args...)' que hace cierto
		al predicado 'pred'.
		"""
		if pred not in self.__predicates:
			raise NameError("The predicate hasn't been defined.")
		elif self.__predicates[pred] != len(args):
			raise NameError("Arity error.")

		# TODO tratar variables libres ?
		variables = self.__countvars(*args)

		if pred in self.__facts:
			self.__facts[pred].append(args)
		else:
			self.__facts[pred] = [args]

		for f in args:
			if f not in self.__atoms:
				self.__atoms.add(f)


	def retract_fact(self, pred, *args):
		"""
		Borra un hecho de la base de conocimiento.
		"""
		if pred not in self.__predicates:
			raise NameError("The predicate hasn't been defined.")
		elif self.__predicates[pred] != len(args):
			raise NameError("Arity error.")
		# elif args not in self.__facts[pred]:
		# 	raise NameError("The fact hasn't been asserted.")

		result = False

		# TODO tratar variables
		n = self.__countvars(*args)

		if n == 0:
			self.__facts[pred].remove(args)
			result = True

		return result


	# def new_rule(self, name, f_rule):
	# 	if type(f_rule) != function:
	# 		raise NameError("The argument must be a function.")
	# 	elif name not in self.__predicates:
	# 		raise NameError("The predicate hasn't been defined.")
	# 	self.__rules.append(f_rule)


	def eval(self, pred, *args):
		"""
		Evalua si el predicado es cierto para los atomos 'args' o, 
		en caso de que haya variables, si existen algun valor valido.
		"""
		if pred not in self.__predicates:
			raise NameError("The predicate hasn't been defined.")
		elif self.__predicates[pred] != len(args):
			raise NameError("Arity error.")

		result = False
		
		# TODO solo variables mudas ??
		free_vars = self.__countvars(*args)

		if free_vars > 0 and pred in self.__facts:
			result = self.__evl_vars(pred, free_vars, *args)
		elif pred in self.__facts:
			result = self.__evl(pred, *args)

		return result


	def solv(self, pred, *args):
		"""
		Busca valores que hagan cierto el predicado para las variables
		que se encuentren en 'args'.
		Si no hay variables en 'args', o no se encuentra, devolvera una
		lista vacia.
		"""
		if pred not in self.__predicates:
			raise NameError("The predicate hasn't been defined.")
		elif self.__predicates[pred] != len(args):
			raise NameError("Arity error.")

		free_vars = self.__count_notanon_vars(*args)
		

		if free_vars < 1:
			raise NameError("There's no variables to solve.")
		else:
			return self.__unify(pred, free_vars, *args)


	def query(self, pred, *args):
		"""
		Evalua o resuelve el objetivo lanzado, segun
		la presencia (o no) de variables o variables 
		anonimas.
		Actua como 'eval' y 'solv' al mismo tiempo.
		"""
		if pred not in self.__predicates:
			raise NameError("The predicate hasn't been defined.")
		elif self.__predicates[pred] != len(args):
			raise NameError("Arity error.")

		result = False
		free_vars = self.__countvars(*args)
		anon_vars = self.__count_anon_vars(*args)
		v = free_vars - anon_vars

		if v > 0:
			result = self.__unify(pred, v, *args)
		elif anon_vars > 0:
			result = self.__evl_vars(pred, anon_vars, *args)
		else:
			result = self.__evl(pred, *args)

		# Returns a bool or a list !!
		return result




	##########################
	#### INTERN FUNCTIONS
	##########################

	def __evl(self, pred, *args):
		return args in self.__facts[pred]


	def __evl_vars(self, pred, fvars, *args):
		"""
		* Funcion interna.
		Evalua de forma recursiva si para las constantes dadas en 'args', 
		existe algun valor (para las variables) que haga cierto el 
		predicado.
		Es decir, evalua si la combinacion de 'args' para el predicado es
		factible.
		"""
		result = False
		terms = list(args)

		domain = self.__get_domain(pred)

		# TODO mejorar backtracking
		# TODO variables mudas

		for c in range(len(terms)):
			if self.__isvar(terms[c]):
				for a in domain:
					terms[c] = a
					if fvars > 1 and self.__evl_vars(pred, fvars-1, *terms):
						# interesa si hay algun resultado cierto
						result = True
					elif fvars == 1 and self.eval(pred, *terms):
						result = True

		return result


	def __unify(self, pred, fvars, *args):
		"""
		* Funcion interna.
		Encuentra valores para las variables que hagan cierto
		el predicado.
		"""
		result = []
		terms = list(args)
		var = ""
		aux = ""

		domain = self.__get_domain(pred)

		# TODO this backtraking sucks
		# TODO trata variables mudas/anonimas !

		for c in range(len(terms)):
			if self.__isvar(terms[c]):
				var = str(terms[c])
				for a in domain: 
					terms[c] = a
					if fvars > 1 and self.__evl_vars(pred, fvars-1, *terms):
						# si hay mas variables y la decision es factible...
						aux = var + " = " + str(a)
						result.append(aux)
						r = self.__unify(pred, fvars-1, *terms)
						result = result + r
					elif fvars == 1 and self.__evl(pred, *terms):
						# si la asignacion produce exito
						aux = var + " = " + str(a)
						result.append(aux)

		return result


	def __get_domain(self, predicate):
		"""
		* Funcion interna.
		Crea el dominio de atomos que aparecen en todos los hechos
		relativos al predicado dado 'predicate'.
		pre:	predicate in __facts
		"""
		domain = []

		for a in self.__atoms:
			for fact in self.__facts[predicate]:
				if a in fact and a not in domain:
					domain.append(a)

		return domain


	def __countvars(self, *args):
		"""
		* Funcion interna.
		Cuenta las variables que aparecen en 'args'.
		"""
		result = 0

		for x in args:
			if self.__isvar(x):
				result += 1

		return result


	def __count_notanon_vars(self, *args):
		"""
		* Funcion interna.
		Cuenta las variables no anonimas (o mudas) que
		aparecen en 'args'.
		"""
		result = 0

		for x in args:
			if self.__isvar(x) and not self.__isanon(x):
				result += 1

		return result


	def __count_anon_vars(self, *args):
		"""
		* Funcion interna.
		Cuenta las variables anonimas (o mudas) que
		aparecen en 'args'.
		"""
		result = 0

		for x in args:
			if self.__isanon(x):
				result += 1

		return result




	##########################
	# DATA TYPES 
	##########################

	def __isanon(self, term):
		"""
		* Funcion interna.
		Verifica si el parametro 'term' es una variable muda (o anonima),
		representada como '_'.
		"""
		return term == '_' or term == '?'


	def __isatom(self, term):
		"""
		* Funcion interna.
		Verifica si el parametro 'term' es un atomo y retorna verdadero
		en caso de que lo sea, o falso en caso contrario.
		"""
		result = False

		if type(term) == str:
			# _Var y ?Var son variables !
			if not (term.startswith('_') or term.startswith('?')) \
			and not (term.istitle() or term.isupper()):
				result = True
			elif self.__islit(term):
				result = True

		return result


	def __islit(self, term):
		"""
		* Funcion interna.
		Verifica si el parametro 'term' es un atomo literal de la forma 
		'Nombre de Atomo', y retorna verdadero si lo es, o falso en 
		caso contrario.
		"""
		return term.startswith("'") and term.endswith("'")


	def __isvar(self, term):
		"""
		* Funcion interna.
		Verifica si el parametro 'term' es una variable (si empieza por 
		mayuscula o por _) y retorna verdadero en caso de que lo sea, o 
		falso en caso contrario.
		Retornara cierto tambien para una variable muda (anonima) '_'.
		"""
		result = False

		if type(term) == str:
			if term.startswith('_') or term.startswith('?'): # '?var' variable ?
				result = True
			elif (term.istitle() or term.isupper()) and not self.__islit(term):
				result = True

		return result




	##########################
	# TO_STRING METHODS
	##########################

	def str_preds(self):
		"""
		Retorna un string representando los predicados almacenados 
		en la base de datos del motor.
		"""
		to_st = "[ "
		for p in self.__predicates:
			to_st = to_st + p + "/" + str(self.__predicates[p]) + ", "
		return to_st.rstrip(", ") + " ]"


	def str_facts(self):
		"""
		Retorna un string representando los hechos almacenados
		en la base de datos del motor.
		"""
		to_st = "[ "
		for p in self.__facts:
			for cl in self.__facts[p]:
				to_st = to_st + p + str(cl) + ", "
		return to_st.rstrip(", ") + " ]"


	# TEMP ? for tests only
	def str_atoms(self):
		"""
		Retorna un string con todos los atomos (constantes) definidas
		en los hechos.
		"""
		to_st = "[ "
		for a in self.__atoms:
			# to_st += "'" + a + "'" + ", "
			to_st += a + ", "
		return to_st.rstrip(", ") + " ]"


	def __str__(self):
		result = ""
		result += "---------------" + "\n"
		result += "Preds:\t" + self.str_preds() + "\n"
		result += "Facts:\t" + self.str_facts() + "\n"
		# result += "Atoms:" + self.str_atoms() + "\n"
		result += "---------------"
		return result


##########################
##########################


def new():
	"""
	Retorna una instancia del motor logico 
	(con su propia base de conocimiento)
	"""
	return Logice()


##########################

# if __name__ == "__main__":


