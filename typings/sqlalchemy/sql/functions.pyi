"""
This type stub file was generated by pyright.
"""

from . import sqltypes
from .base import Executable, Generative, HasMemoized
from .elements import BinaryExpression, ColumnElement, NamedColumn
from .selectable import FromClause
from .visitors import TraversibleType
from .. import util

"""SQL function API, factories, and built-in functions.

"""
_registry = ...
def register_function(identifier, fn, package=...): # -> None:
    """Associate a callable with a particular func. name.

    This is normally called by _GenericMeta, but is also
    available by itself so that a non-Function construct
    can be associated with the :data:`.func` accessor (i.e.
    CAST, EXTRACT).

    """
    ...

class FunctionElement(Executable, ColumnElement, FromClause, Generative):
    """Base for SQL function-oriented constructs.

    .. seealso::

        :ref:`tutorial_functions` - in the :ref:`unified_tutorial`

        :class:`.Function` - named SQL function.

        :data:`.func` - namespace which produces registered or ad-hoc
        :class:`.Function` instances.

        :class:`.GenericFunction` - allows creation of registered function
        types.

    """
    _traverse_internals = ...
    packagenames = ...
    _has_args = ...
    _with_ordinality = ...
    _table_value_type = ...
    def __init__(self, *clauses, **kwargs) -> None:
        r"""Construct a :class:`.FunctionElement`.

        :param \*clauses: list of column expressions that form the arguments
         of the SQL function call.

        :param \**kwargs:  additional kwargs are typically consumed by
         subclasses.

        .. seealso::

            :data:`.func`

            :class:`.Function`

        """
        ...
    
    _non_anon_label = ...
    def scalar_table_valued(self, name, type_=...): # -> ScalarFunctionColumn:
        """Return a column expression that's against this
        :class:`_functions.FunctionElement` as a scalar
        table-valued expression.

        The returned expression is similar to that returned by a single column
        accessed off of a :meth:`_functions.FunctionElement.table_valued`
        construct, except no FROM clause is generated; the function is rendered
        in the similar way as a scalar subquery.

        E.g.::

            >>> from sqlalchemy import func, select
            >>> fn = func.jsonb_each("{'k', 'v'}").scalar_table_valued("key")
            >>> print(select(fn))
            SELECT (jsonb_each(:jsonb_each_1)).key

        .. versionadded:: 1.4.0b2

        .. seealso::

            :meth:`_functions.FunctionElement.table_valued`

            :meth:`_functions.FunctionElement.alias`

            :meth:`_functions.FunctionElement.column_valued`

        """
        ...
    
    def table_valued(self, *expr, **kw): # -> TableValuedAlias:
        r"""Return a :class:`_sql.TableValuedAlias` representation of this
        :class:`_functions.FunctionElement` with table-valued expressions added.

        e.g.::

            >>> fn = (
            ...     func.generate_series(1, 5).
            ...     table_valued("value", "start", "stop", "step")
            ... )

            >>> print(select(fn))
            SELECT anon_1.value, anon_1.start, anon_1.stop, anon_1.step
            FROM generate_series(:generate_series_1, :generate_series_2) AS anon_1

            >>> print(select(fn.c.value, fn.c.stop).where(fn.c.value > 2))
            SELECT anon_1.value, anon_1.stop
            FROM generate_series(:generate_series_1, :generate_series_2) AS anon_1
            WHERE anon_1.value > :value_1

        A WITH ORDINALITY expression may be generated by passing the keyword
        argument "with_ordinality"::

            >>> fn = func.generate_series(4, 1, -1).table_valued("gen", with_ordinality="ordinality")
            >>> print(select(fn))
            SELECT anon_1.gen, anon_1.ordinality
            FROM generate_series(:generate_series_1, :generate_series_2, :generate_series_3) WITH ORDINALITY AS anon_1

        :param \*expr: A series of string column names that will be added to the
         ``.c`` collection of the resulting :class:`_sql.TableValuedAlias`
         construct as columns.  :func:`_sql.column` objects with or without
         datatypes may also be used.

        :param name: optional name to assign to the alias name that's generated.
         If omitted, a unique anonymizing name is used.

        :param with_ordinality: string name that when present results in the
         ``WITH ORDINALITY`` clause being added to the alias, and the given
         string name will be added as a column to the .c collection
         of the resulting :class:`_sql.TableValuedAlias`.

        :param joins_implicitly: when True, the table valued function may be
         used in the FROM clause without any explicit JOIN to other tables
         in the SQL query, and no "cartesian product" warning will be generated.
         May be useful for SQL functions such as ``func.json_each()``.

         .. versionadded:: 1.4.33

        .. versionadded:: 1.4.0b2


        .. seealso::

            :ref:`tutorial_functions_table_valued` - in the :ref:`unified_tutorial`

            :ref:`postgresql_table_valued` - in the :ref:`postgresql_toplevel` documentation

            :meth:`_functions.FunctionElement.scalar_table_valued` - variant of
            :meth:`_functions.FunctionElement.table_valued` which delivers the
            complete table valued expression as a scalar column expression

            :meth:`_functions.FunctionElement.column_valued`

            :meth:`_sql.TableValuedAlias.render_derived` - renders the alias
            using a derived column clause, e.g. ``AS name(col1, col2, ...)``

        """
        ...
    
    def column_valued(self, name=..., joins_implicitly=...): # -> memoized_attribute:
        """Return this :class:`_functions.FunctionElement` as a column expression that
        selects from itself as a FROM clause.

        E.g.::

            >>> from sqlalchemy import select, func
            >>> gs = func.generate_series(1, 5, -1).column_valued()
            >>> print(select(gs))
            SELECT anon_1
            FROM generate_series(:generate_series_1, :generate_series_2, :generate_series_3) AS anon_1

        This is shorthand for::

            gs = func.generate_series(1, 5, -1).alias().column

        :param name: optional name to assign to the alias name that's generated.
         If omitted, a unique anonymizing name is used.

        :param joins_implicitly: when True, the "table" portion of the column
         valued function may be a member of the FROM clause without any
         explicit JOIN to other tables in the SQL query, and no "cartesian
         product" warning will be generated. May be useful for SQL functions
         such as ``func.json_array_elements()``.

         .. versionadded:: 1.4.46

        .. seealso::

            :ref:`tutorial_functions_column_valued` - in the :ref:`unified_tutorial`

            :ref:`postgresql_column_valued` - in the :ref:`postgresql_toplevel` documentation

            :meth:`_functions.FunctionElement.table_valued`

        """
        ...
    
    @property
    def columns(self): # -> ColumnCollection:
        r"""The set of columns exported by this :class:`.FunctionElement`.

        This is a placeholder collection that allows the function to be
        placed in the FROM clause of a statement::

            >>> from sqlalchemy import column, select, func
            >>> stmt = select(column('x'), column('y')).select_from(func.myfunction())
            >>> print(stmt)
            SELECT x, y FROM myfunction()

        The above form is a legacy feature that is now superseded by the
        fully capable :meth:`_functions.FunctionElement.table_valued`
        method; see that method for details.

        .. seealso::

            :meth:`_functions.FunctionElement.table_valued` - generates table-valued
            SQL function expressions.

        """
        ...
    
    @property
    def exported_columns(self): # -> ColumnCollection:
        ...
    
    @HasMemoized.memoized_attribute
    def clauses(self): # -> ClauseList:
        """Return the underlying :class:`.ClauseList` which contains
        the arguments for this :class:`.FunctionElement`.

        """
        ...
    
    def over(self, partition_by=..., order_by=..., rows=..., range_=...): # -> Over:
        """Produce an OVER clause against this function.

        Used against aggregate or so-called "window" functions,
        for database backends that support window functions.

        The expression::

            func.row_number().over(order_by='x')

        is shorthand for::

            from sqlalchemy import over
            over(func.row_number(), order_by='x')

        See :func:`_expression.over` for a full description.

        .. seealso::

            :func:`_expression.over`

            :ref:`tutorial_window_functions` - in the :ref:`unified_tutorial`

        """
        ...
    
    def within_group(self, *order_by): # -> WithinGroup:
        """Produce a WITHIN GROUP (ORDER BY expr) clause against this function.

        Used against so-called "ordered set aggregate" and "hypothetical
        set aggregate" functions, including :class:`.percentile_cont`,
        :class:`.rank`, :class:`.dense_rank`, etc.

        See :func:`_expression.within_group` for a full description.

        .. versionadded:: 1.1


        .. seealso::

            :ref:`tutorial_functions_within_group` -
            in the :ref:`unified_tutorial`


        """
        ...
    
    def filter(self, *criterion): # -> Self | FunctionFilter:
        """Produce a FILTER clause against this function.

        Used against aggregate and window functions,
        for database backends that support the "FILTER" clause.

        The expression::

            func.count(1).filter(True)

        is shorthand for::

            from sqlalchemy import funcfilter
            funcfilter(func.count(1), True)

        .. versionadded:: 1.0.0

        .. seealso::

            :ref:`tutorial_functions_within_group` -
            in the :ref:`unified_tutorial`

            :class:`.FunctionFilter`

            :func:`.funcfilter`


        """
        ...
    
    def as_comparison(self, left_index, right_index): # -> FunctionAsBinary:
        """Interpret this expression as a boolean comparison between two
        values.

        This method is used for an ORM use case described at
        :ref:`relationship_custom_operator_sql_function`.

        A hypothetical SQL function "is_equal()" which compares to values
        for equality would be written in the Core expression language as::

            expr = func.is_equal("a", "b")

        If "is_equal()" above is comparing "a" and "b" for equality, the
        :meth:`.FunctionElement.as_comparison` method would be invoked as::

            expr = func.is_equal("a", "b").as_comparison(1, 2)

        Where above, the integer value "1" refers to the first argument of the
        "is_equal()" function and the integer value "2" refers to the second.

        This would create a :class:`.BinaryExpression` that is equivalent to::

            BinaryExpression("a", "b", operator=op.eq)

        However, at the SQL level it would still render as
        "is_equal('a', 'b')".

        The ORM, when it loads a related object or collection, needs to be able
        to manipulate the "left" and "right" sides of the ON clause of a JOIN
        expression. The purpose of this method is to provide a SQL function
        construct that can also supply this information to the ORM, when used
        with the :paramref:`_orm.relationship.primaryjoin` parameter. The
        return value is a containment object called :class:`.FunctionAsBinary`.

        An ORM example is as follows::

            class Venue(Base):
                __tablename__ = 'venue'
                id = Column(Integer, primary_key=True)
                name = Column(String)

                descendants = relationship(
                    "Venue",
                    primaryjoin=func.instr(
                        remote(foreign(name)), name + "/"
                    ).as_comparison(1, 2) == 1,
                    viewonly=True,
                    order_by=name
                )

        Above, the "Venue" class can load descendant "Venue" objects by
        determining if the name of the parent Venue is contained within the
        start of the hypothetical descendant value's name, e.g. "parent1" would
        match up to "parent1/child1", but not to "parent2/child1".

        Possible use cases include the "materialized path" example given above,
        as well as making use of special SQL functions such as geometric
        functions to create join conditions.

        :param left_index: the integer 1-based index of the function argument
         that serves as the "left" side of the expression.
        :param right_index: the integer 1-based index of the function argument
         that serves as the "right" side of the expression.

        .. versionadded:: 1.3

        .. seealso::

            :ref:`relationship_custom_operator_sql_function` -
            example use within the ORM

        """
        ...
    
    def within_group_type(self, within_group): # -> None:
        """For types that define their return type as based on the criteria
        within a WITHIN GROUP (ORDER BY) expression, called by the
        :class:`.WithinGroup` construct.

        Returns None by default, in which case the function's normal ``.type``
        is used.

        """
        ...
    
    def alias(self, name=..., joins_implicitly=...): # -> TableValuedAlias:
        r"""Produce a :class:`_expression.Alias` construct against this
        :class:`.FunctionElement`.

        .. tip::

            The :meth:`_functions.FunctionElement.alias` method is part of the
            mechanism by which "table valued" SQL functions are created.
            However, most use cases are covered by higher level methods on
            :class:`_functions.FunctionElement` including
            :meth:`_functions.FunctionElement.table_valued`, and
            :meth:`_functions.FunctionElement.column_valued`.

        This construct wraps the function in a named alias which
        is suitable for the FROM clause, in the style accepted for example
        by PostgreSQL.  A column expression is also provided using the
        special ``.column`` attribute, which may
        be used to refer to the output of the function as a scalar value
        in the columns or where clause, for a backend such as PostgreSQL.

        For a full table-valued expression, use the
        :meth:`_functions.FunctionElement.table_valued` method first to
        establish named columns.

        e.g.::

            >>> from sqlalchemy import func, select, column
            >>> data_view = func.unnest([1, 2, 3]).alias("data_view")
            >>> print(select(data_view.column))
            SELECT data_view
            FROM unnest(:unnest_1) AS data_view

        The :meth:`_functions.FunctionElement.column_valued` method provides
        a shortcut for the above pattern::

            >>> data_view = func.unnest([1, 2, 3]).column_valued("data_view")
            >>> print(select(data_view))
            SELECT data_view
            FROM unnest(:unnest_1) AS data_view

        .. versionadded:: 1.4.0b2  Added the ``.column`` accessor

        :param name: alias name, will be rendered as ``AS <name>`` in the
         FROM clause

        :param joins_implicitly: when True, the table valued function may be
         used in the FROM clause without any explicit JOIN to other tables
         in the SQL query, and no "cartesian product" warning will be
         generated.  May be useful for SQL functions such as
         ``func.json_each()``.

         .. versionadded:: 1.4.33

        .. seealso::

            :ref:`tutorial_functions_table_valued` -
            in the :ref:`unified_tutorial`

            :meth:`_functions.FunctionElement.table_valued`

            :meth:`_functions.FunctionElement.scalar_table_valued`

            :meth:`_functions.FunctionElement.column_valued`


        """
        ...
    
    def select(self): # -> Select | None:
        """Produce a :func:`_expression.select` construct
        against this :class:`.FunctionElement`.

        This is shorthand for::

            s = select(function_element)

        """
        ...
    
    @util.deprecated_20(":meth:`.FunctionElement.scalar`", alternative="Scalar execution in SQLAlchemy 2.0 is performed " "by the :meth:`_engine.Connection.scalar` method of " ":class:`_engine.Connection`, " "or in the ORM by the :meth:`.Session.scalar` method of " ":class:`.Session`.")
    def scalar(self):
        """Execute this :class:`.FunctionElement` against an embedded
        'bind' and return a scalar value.

        This first calls :meth:`~.FunctionElement.select` to
        produce a SELECT construct.

        Note that :class:`.FunctionElement` can be passed to
        the :meth:`.Connectable.scalar` method of :class:`_engine.Connection`
        or :class:`_engine.Engine`.

        """
        ...
    
    @util.deprecated_20(":meth:`.FunctionElement.execute`", alternative="All statement execution in SQLAlchemy 2.0 is performed " "by the :meth:`_engine.Connection.execute` method of " ":class:`_engine.Connection`, " "or in the ORM by the :meth:`.Session.execute` method of " ":class:`.Session`.")
    def execute(self):
        """Execute this :class:`.FunctionElement` against an embedded
        'bind'.

        This first calls :meth:`~.FunctionElement.select` to
        produce a SELECT construct.

        Note that :class:`.FunctionElement` can be passed to
        the :meth:`.Connectable.execute` method of :class:`_engine.Connection`
        or :class:`_engine.Engine`.

        """
        ...
    
    def self_group(self, against=...): # -> Grouping | AsBoolean | Self:
        ...
    
    @property
    def entity_namespace(self):
        """overrides FromClause.entity_namespace as functions are generally
        column expressions and not FromClauses.

        """
        ...
    


class FunctionAsBinary(BinaryExpression):
    _traverse_internals = ...
    def __init__(self, fn, left_index, right_index) -> None:
        ...
    
    @property
    def left(self):
        ...
    
    @left.setter
    def left(self, value): # -> None:
        ...
    
    @property
    def right(self):
        ...
    
    @right.setter
    def right(self, value): # -> None:
        ...
    


class ScalarFunctionColumn(NamedColumn):
    __visit_name__ = ...
    _traverse_internals = ...
    is_literal = ...
    table = ...
    def __init__(self, fn, name, type_=...) -> None:
        ...
    


class _FunctionGenerator:
    """Generate SQL function expressions.

    :data:`.func` is a special object instance which generates SQL
    functions based on name-based attributes, e.g.::

        >>> print(func.count(1))
        count(:param_1)

    The returned object is an instance of :class:`.Function`, and  is a
    column-oriented SQL element like any other, and is used in that way::

        >>> print(select(func.count(table.c.id)))
        SELECT count(sometable.id) FROM sometable

    Any name can be given to :data:`.func`. If the function name is unknown to
    SQLAlchemy, it will be rendered exactly as is. For common SQL functions
    which SQLAlchemy is aware of, the name may be interpreted as a *generic
    function* which will be compiled appropriately to the target database::

        >>> print(func.current_timestamp())
        CURRENT_TIMESTAMP

    To call functions which are present in dot-separated packages,
    specify them in the same manner::

        >>> print(func.stats.yield_curve(5, 10))
        stats.yield_curve(:yield_curve_1, :yield_curve_2)

    SQLAlchemy can be made aware of the return type of functions to enable
    type-specific lexical and result-based behavior. For example, to ensure
    that a string-based function returns a Unicode value and is similarly
    treated as a string in expressions, specify
    :class:`~sqlalchemy.types.Unicode` as the type:

        >>> print(func.my_string(u'hi', type_=Unicode) + ' ' +
        ...       func.my_string(u'there', type_=Unicode))
        my_string(:my_string_1) || :my_string_2 || my_string(:my_string_3)

    The object returned by a :data:`.func` call is usually an instance of
    :class:`.Function`.
    This object meets the "column" interface, including comparison and labeling
    functions.  The object can also be passed the :meth:`~.Connectable.execute`
    method of a :class:`_engine.Connection` or :class:`_engine.Engine`,
    where it will be
    wrapped inside of a SELECT statement first::

        print(connection.execute(func.current_timestamp()).scalar())

    In a few exception cases, the :data:`.func` accessor
    will redirect a name to a built-in expression such as :func:`.cast`
    or :func:`.extract`, as these names have well-known meaning
    but are not exactly the same as "functions" from a SQLAlchemy
    perspective.

    Functions which are interpreted as "generic" functions know how to
    calculate their return type automatically. For a listing of known generic
    functions, see :ref:`generic_functions`.

    .. note::

        The :data:`.func` construct has only limited support for calling
        standalone "stored procedures", especially those with special
        parameterization concerns.

        See the section :ref:`stored_procedures` for details on how to use
        the DBAPI-level ``callproc()`` method for fully traditional stored
        procedures.

    .. seealso::

        :ref:`tutorial_functions` - in the :ref:`unified_tutorial`

        :class:`.Function`

    """
    def __init__(self, **opts) -> None:
        ...
    
    def __getattr__(self, name): # -> Any | _FunctionGenerator:
        ...
    
    def __call__(self, *c, **kwargs): # -> Function:
        ...
    


func = ...
modifier = ...
class Function(FunctionElement):
    r"""Describe a named SQL function.

    The :class:`.Function` object is typically generated from the
    :data:`.func` generation object.


    :param \*clauses: list of column expressions that form the arguments
     of the SQL function call.

    :param type\_: optional :class:`.TypeEngine` datatype object that will be
     used as the return value of the column expression generated by this
     function call.

    :param packagenames: a string which indicates package prefix names
     to be prepended to the function name when the SQL is generated.
     The :data:`.func` generator creates these when it is called using
     dotted format, e.g.::

        func.mypackage.some_function(col1, col2)

    .. seealso::

        :ref:`tutorial_functions` - in the :ref:`unified_tutorial`

        :data:`.func` - namespace which produces registered or ad-hoc
        :class:`.Function` instances.

        :class:`.GenericFunction` - allows creation of registered function
        types.

    """
    __visit_name__ = ...
    _traverse_internals = ...
    type = ...
    @util.deprecated_params(bind=("2.0", "The :paramref:`_sql.text.bind` argument is deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, name, *clauses, **kw) -> None:
        """Construct a :class:`.Function`.

        The :data:`.func` construct is normally used to construct
        new :class:`.Function` instances.

        """
        ...
    


class _GenericMeta(TraversibleType):
    def __init__(cls, clsname, bases, clsdict) -> None:
        ...
    


class GenericFunction(util.with_metaclass(_GenericMeta, Function)):
    """Define a 'generic' function.

    A generic function is a pre-established :class:`.Function`
    class that is instantiated automatically when called
    by name from the :data:`.func` attribute.    Note that
    calling any name from :data:`.func` has the effect that
    a new :class:`.Function` instance is created automatically,
    given that name.  The primary use case for defining
    a :class:`.GenericFunction` class is so that a function
    of a particular name may be given a fixed return type.
    It can also include custom argument parsing schemes as well
    as additional methods.

    Subclasses of :class:`.GenericFunction` are automatically
    registered under the name of the class.  For
    example, a user-defined function ``as_utc()`` would
    be available immediately::

        from sqlalchemy.sql.functions import GenericFunction
        from sqlalchemy.types import DateTime

        class as_utc(GenericFunction):
            type = DateTime
            inherit_cache = True

        print(select(func.as_utc()))

    User-defined generic functions can be organized into
    packages by specifying the "package" attribute when defining
    :class:`.GenericFunction`.   Third party libraries
    containing many functions may want to use this in order
    to avoid name conflicts with other systems.   For example,
    if our ``as_utc()`` function were part of a package
    "time"::

        class as_utc(GenericFunction):
            type = DateTime
            package = "time"
            inherit_cache = True

    The above function would be available from :data:`.func`
    using the package name ``time``::

        print(select(func.time.as_utc()))

    A final option is to allow the function to be accessed
    from one name in :data:`.func` but to render as a different name.
    The ``identifier`` attribute will override the name used to
    access the function as loaded from :data:`.func`, but will retain
    the usage of ``name`` as the rendered name::

        class GeoBuffer(GenericFunction):
            type = Geometry
            package = "geo"
            name = "ST_Buffer"
            identifier = "buffer"
            inherit_cache = True

    The above function will render as follows::

        >>> print(func.geo.buffer())
        ST_Buffer()

    The name will be rendered as is, however without quoting unless the name
    contains special characters that require quoting.  To force quoting
    on or off for the name, use the :class:`.sqlalchemy.sql.quoted_name`
    construct::

        from sqlalchemy.sql import quoted_name

        class GeoBuffer(GenericFunction):
            type = Geometry
            package = "geo"
            name = quoted_name("ST_Buffer", True)
            identifier = "buffer"
            inherit_cache = True

    The above function will render as::

        >>> print(func.geo.buffer())
        "ST_Buffer"()

    .. versionadded:: 1.3.13  The :class:`.quoted_name` construct is now
       recognized for quoting when used with the "name" attribute of the
       object, so that quoting can be forced on or off for the function
       name.


    """
    coerce_arguments = ...
    _register = ...
    inherit_cache = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class next_value(GenericFunction):
    """Represent the 'next value', given a :class:`.Sequence`
    as its single argument.

    Compiles into the appropriate function on each backend,
    or will raise NotImplementedError if used on a backend
    that does not provide support for sequences.

    """
    type = ...
    name = ...
    _traverse_internals = ...
    def __init__(self, seq, **kw) -> None:
        ...
    
    def compare(self, other, **kw): # -> bool:
        ...
    


class AnsiFunction(GenericFunction):
    """Define a function in "ansi" format, which doesn't render parenthesis."""
    inherit_cache = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class ReturnTypeFromArgs(GenericFunction):
    """Define a function whose return type is the same as its arguments."""
    inherit_cache = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class coalesce(ReturnTypeFromArgs):
    _has_args = ...
    inherit_cache = ...


class max(ReturnTypeFromArgs):
    """The SQL MAX() aggregate function."""
    inherit_cache = ...


class min(ReturnTypeFromArgs):
    """The SQL MIN() aggregate function."""
    inherit_cache = ...


class sum(ReturnTypeFromArgs):
    """The SQL SUM() aggregate function."""
    inherit_cache = ...


class now(GenericFunction):
    """The SQL now() datetime function.

    SQLAlchemy dialects will usually render this particular function
    in a backend-specific way, such as rendering it as ``CURRENT_TIMESTAMP``.

    """
    type = sqltypes.DateTime
    inherit_cache = ...


class concat(GenericFunction):
    """The SQL CONCAT() function, which concatenates strings.

    E.g.::

        >>> print(select(func.concat('a', 'b')))
        SELECT concat(:concat_2, :concat_3) AS concat_1

    String concatenation in SQLAlchemy is more commonly available using the
    Python ``+`` operator with string datatypes, which will render a
    backend-specific concatenation operator, such as ::

        >>> print(select(literal("a") + "b"))
        SELECT :param_1 || :param_2 AS anon_1


    """
    type = sqltypes.String
    inherit_cache = ...


class char_length(GenericFunction):
    """The CHAR_LENGTH() SQL function."""
    type = sqltypes.Integer
    inherit_cache = ...
    def __init__(self, arg, **kwargs) -> None:
        ...
    


class random(GenericFunction):
    """The RANDOM() SQL function."""
    _has_args = ...
    inherit_cache = ...


class count(GenericFunction):
    r"""The ANSI COUNT aggregate function.  With no arguments,
    emits COUNT \*.

    E.g.::

        from sqlalchemy import func
        from sqlalchemy import select
        from sqlalchemy import table, column

        my_table = table('some_table', column('id'))

        stmt = select(func.count()).select_from(my_table)

    Executing ``stmt`` would emit::

        SELECT count(*) AS count_1
        FROM some_table


    """
    type = sqltypes.Integer
    inherit_cache = ...
    def __init__(self, expression=..., **kwargs) -> None:
        ...
    


class current_date(AnsiFunction):
    """The CURRENT_DATE() SQL function."""
    type = sqltypes.Date
    inherit_cache = ...


class current_time(AnsiFunction):
    """The CURRENT_TIME() SQL function."""
    type = sqltypes.Time
    inherit_cache = ...


class current_timestamp(AnsiFunction):
    """The CURRENT_TIMESTAMP() SQL function."""
    type = sqltypes.DateTime
    inherit_cache = ...


class current_user(AnsiFunction):
    """The CURRENT_USER() SQL function."""
    type = sqltypes.String
    inherit_cache = ...


class localtime(AnsiFunction):
    """The localtime() SQL function."""
    type = sqltypes.DateTime
    inherit_cache = ...


class localtimestamp(AnsiFunction):
    """The localtimestamp() SQL function."""
    type = sqltypes.DateTime
    inherit_cache = ...


class session_user(AnsiFunction):
    """The SESSION_USER() SQL function."""
    type = sqltypes.String
    inherit_cache = ...


class sysdate(AnsiFunction):
    """The SYSDATE() SQL function."""
    type = sqltypes.DateTime
    inherit_cache = ...


class user(AnsiFunction):
    """The USER() SQL function."""
    type = sqltypes.String
    inherit_cache = ...


class array_agg(GenericFunction):
    """Support for the ARRAY_AGG function.

    The ``func.array_agg(expr)`` construct returns an expression of
    type :class:`_types.ARRAY`.

    e.g.::

        stmt = select(func.array_agg(table.c.values)[2:5])

    .. versionadded:: 1.1

    .. seealso::

        :func:`_postgresql.array_agg` - PostgreSQL-specific version that
        returns :class:`_postgresql.ARRAY`, which has PG-specific operators
        added.

    """
    type = sqltypes.ARRAY
    inherit_cache = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class OrderedSetAgg(GenericFunction):
    """Define a function where the return type is based on the sort
    expression type as defined by the expression passed to the
    :meth:`.FunctionElement.within_group` method."""
    array_for_multi_clause = ...
    inherit_cache = ...
    def within_group_type(self, within_group): # -> ARRAY:
        ...
    


class mode(OrderedSetAgg):
    """Implement the ``mode`` ordered-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is the same as the sort expression.

    .. versionadded:: 1.1

    """
    inherit_cache = ...


class percentile_cont(OrderedSetAgg):
    """Implement the ``percentile_cont`` ordered-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is the same as the sort expression,
    or if the arguments are an array, an :class:`_types.ARRAY` of the sort
    expression's type.

    .. versionadded:: 1.1

    """
    array_for_multi_clause = ...
    inherit_cache = ...


class percentile_disc(OrderedSetAgg):
    """Implement the ``percentile_disc`` ordered-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is the same as the sort expression,
    or if the arguments are an array, an :class:`_types.ARRAY` of the sort
    expression's type.

    .. versionadded:: 1.1

    """
    array_for_multi_clause = ...
    inherit_cache = ...


class rank(GenericFunction):
    """Implement the ``rank`` hypothetical-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is :class:`.Integer`.

    .. versionadded:: 1.1

    """
    type = ...
    inherit_cache = ...


class dense_rank(GenericFunction):
    """Implement the ``dense_rank`` hypothetical-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is :class:`.Integer`.

    .. versionadded:: 1.1

    """
    type = ...
    inherit_cache = ...


class percent_rank(GenericFunction):
    """Implement the ``percent_rank`` hypothetical-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is :class:`.Numeric`.

    .. versionadded:: 1.1

    """
    type = ...
    inherit_cache = ...


class cume_dist(GenericFunction):
    """Implement the ``cume_dist`` hypothetical-set aggregate function.

    This function must be used with the :meth:`.FunctionElement.within_group`
    modifier to supply a sort expression to operate upon.

    The return type of this function is :class:`.Numeric`.

    .. versionadded:: 1.1

    """
    type = ...
    inherit_cache = ...


class cube(GenericFunction):
    r"""Implement the ``CUBE`` grouping operation.

    This function is used as part of the GROUP BY of a statement,
    e.g. :meth:`_expression.Select.group_by`::

        stmt = select(
            func.sum(table.c.value), table.c.col_1, table.c.col_2
        ).group_by(func.cube(table.c.col_1, table.c.col_2))

    .. versionadded:: 1.2

    """
    _has_args = ...
    inherit_cache = ...


class rollup(GenericFunction):
    r"""Implement the ``ROLLUP`` grouping operation.

    This function is used as part of the GROUP BY of a statement,
    e.g. :meth:`_expression.Select.group_by`::

        stmt = select(
            func.sum(table.c.value), table.c.col_1, table.c.col_2
        ).group_by(func.rollup(table.c.col_1, table.c.col_2))

    .. versionadded:: 1.2

    """
    _has_args = ...
    inherit_cache = ...


class grouping_sets(GenericFunction):
    r"""Implement the ``GROUPING SETS`` grouping operation.

    This function is used as part of the GROUP BY of a statement,
    e.g. :meth:`_expression.Select.group_by`::

        stmt = select(
            func.sum(table.c.value), table.c.col_1, table.c.col_2
        ).group_by(func.grouping_sets(table.c.col_1, table.c.col_2))

    In order to group by multiple sets, use the :func:`.tuple_` construct::

        from sqlalchemy import tuple_

        stmt = select(
            func.sum(table.c.value),
            table.c.col_1, table.c.col_2,
            table.c.col_3
        ).group_by(
            func.grouping_sets(
                tuple_(table.c.col_1, table.c.col_2),
                tuple_(table.c.value, table.c.col_3),
            )
        )


    .. versionadded:: 1.2

    """
    _has_args = ...
    inherit_cache = ...


