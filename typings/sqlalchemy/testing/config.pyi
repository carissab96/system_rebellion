"""
This type stub file was generated by pyright.
"""

requirements = ...
db = ...
db_url = ...
db_opts = ...
file_config = ...
test_schema = ...
test_schema_2 = ...
any_async = ...
_current = ...
ident = ...
_fixture_functions = ...
def combinations(*comb, **kw):
    r"""Deliver multiple versions of a test based on positional combinations.

    This is a facade over pytest.mark.parametrize.


    :param \*comb: argument combinations.  These are tuples that will be passed
     positionally to the decorated function.

    :param argnames: optional list of argument names.   These are the names
     of the arguments in the test function that correspond to the entries
     in each argument tuple.   pytest.mark.parametrize requires this, however
     the combinations function will derive it automatically if not present
     by using ``inspect.getfullargspec(fn).args[1:]``.  Note this assumes the
     first argument is "self" which is discarded.

    :param id\_: optional id template.  This is a string template that
     describes how the "id" for each parameter set should be defined, if any.
     The number of characters in the template should match the number of
     entries in each argument tuple.   Each character describes how the
     corresponding entry in the argument tuple should be handled, as far as
     whether or not it is included in the arguments passed to the function, as
     well as if it is included in the tokens used to create the id of the
     parameter set.

     If omitted, the argument combinations are passed to parametrize as is.  If
     passed, each argument combination is turned into a pytest.param() object,
     mapping the elements of the argument tuple to produce an id based on a
     character value in the same position within the string template using the
     following scheme::

        i - the given argument is a string that is part of the id only, don't
            pass it as an argument

        n - the given argument should be passed and it should be added to the
            id by calling the .__name__ attribute

        r - the given argument should be passed and it should be added to the
            id by calling repr()

        s - the given argument should be passed and it should be added to the
            id by calling str()

        a - (argument) the given argument should be passed and it should not
            be used to generated the id

     e.g.::

        @testing.combinations(
            (operator.eq, "eq"),
            (operator.ne, "ne"),
            (operator.gt, "gt"),
            (operator.lt, "lt"),
            id_="na"
        )
        def test_operator(self, opfunc, name):
            pass

    The above combination will call ``.__name__`` on the first member of
    each tuple and use that as the "id" to pytest.param().


    """
    ...

def combinations_list(arg_iterable, **kw):
    "As combination, but takes a single iterable"
    ...

class _variation_base:
    __slots__ = ...
    def __init__(self, case, argname, case_names) -> None:
        ...
    
    def __bool__(self):
        ...
    
    def __nonzero__(self): # -> bool:
        ...
    


def variation(argname, cases):
    """a helper around testing.combinations that provides a single namespace
    that can be used as a switch.

    e.g.::

        @testing.variation("querytyp", ["select", "subquery", "legacy_query"])
        @testing.variation("lazy", ["select", "raise", "raise_on_sql"])
        def test_thing(
            self,
            querytyp,
            lazy,
            decl_base
        ):
            class Thing(decl_base):
                __tablename__ = 'thing'

                # use name directly
                rel = relationship("Rel", lazy=lazy.name)

            # use as a switch
            if querytyp.select:
                stmt = select(Thing)
            elif querytyp.subquery:
                stmt = select(Thing).subquery()
            elif querytyp.legacy_query:
                stmt = Session.query(Thing)
            else:
                assert False


    The variable provided is a slots object of boolean variables, as well
    as the name of the case itself under the attribute ".name"

    """
    ...

def fixture(*arg, **kw):
    ...

def get_current_test_name():
    ...

def mark_base_test_class():
    ...

class Config:
    def __init__(self, db, db_opts, options, file_config) -> None:
        ...
    
    _stack = ...
    _configs = ...
    @classmethod
    def register(cls, db, db_opts, options, file_config): # -> Config:
        """add a config as one of the global configs.

        If there are no configs set up yet, this config also
        gets set as the "_current".
        """
        ...
    
    @classmethod
    def set_as_current(cls, config, namespace): # -> None:
        ...
    
    @classmethod
    def push_engine(cls, db, namespace): # -> None:
        ...
    
    @classmethod
    def push(cls, config, namespace): # -> None:
        ...
    
    @classmethod
    def pop(cls, namespace): # -> None:
        ...
    
    @classmethod
    def reset(cls, namespace): # -> None:
        ...
    
    @classmethod
    def all_configs(cls): # -> set[Any]:
        ...
    
    @classmethod
    def all_dbs(cls): # -> Generator[Any, Any, None]:
        ...
    
    def skip_test(self, msg): # -> None:
        ...
    


def skip_test(msg):
    ...

def async_test(fn):
    ...

