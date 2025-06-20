"""
This type stub file was generated by pyright.
"""

from . import roles
from .base import Executable, SchemaVisitor, _generative
from .elements import ClauseElement
from .. import util

"""
Provides the hierarchy of DDL-defining schema items as well as routines
to invoke them for a create/drop call.

"""
class _DDLCompiles(ClauseElement):
    _hierarchy_supports_caching = ...


class DDLElement(roles.DDLRole, Executable, _DDLCompiles):
    """Base class for DDL expression constructs.

    This class is the base for the general purpose :class:`.DDL` class,
    as well as the various create/drop clause constructs such as
    :class:`.CreateTable`, :class:`.DropTable`, :class:`.AddConstraint`,
    etc.

    :class:`.DDLElement` integrates closely with SQLAlchemy events,
    introduced in :ref:`event_toplevel`.  An instance of one is
    itself an event receiving callable::

        event.listen(
            users,
            'after_create',
            AddConstraint(constraint).execute_if(dialect='postgresql')
        )

    .. seealso::

        :class:`.DDL`

        :class:`.DDLEvents`

        :ref:`event_toplevel`

        :ref:`schema_ddl_sequences`

    """
    _execution_options = ...
    target = ...
    on = ...
    dialect = ...
    callable_ = ...
    @util.deprecated_20(":meth:`.DDLElement.execute`", alternative="All statement execution in SQLAlchemy 2.0 is performed " "by the :meth:`_engine.Connection.execute` method of " ":class:`_engine.Connection`, " "or in the ORM by the :meth:`.Session.execute` method of " ":class:`.Session`.")
    def execute(self, bind=..., target=...): # -> Any | None:
        """Execute this DDL immediately.

        Executes the DDL statement in isolation using the supplied
        :class:`.Connectable` or
        :class:`.Connectable` assigned to the ``.bind``
        property, if not supplied. If the DDL has a conditional ``on``
        criteria, it will be invoked with None as the event.

        :param bind:
          Optional, an ``Engine`` or ``Connection``. If not supplied, a valid
          :class:`.Connectable` must be present in the
          ``.bind`` property.

        :param target:
          Optional, defaults to None.  The target :class:`_schema.SchemaItem`
          for the execute call.   This is equivalent to passing the
          :class:`_schema.SchemaItem` to the :meth:`.DDLElement.against`
          method and then invoking :meth:`_schema.DDLElement.execute`
          upon the resulting :class:`_schema.DDLElement` object.  See
          :meth:`.DDLElement.against` for further detail.

        """
        ...
    
    @_generative
    def against(self, target): # -> None:
        """Return a copy of this :class:`_schema.DDLElement` which will include
        the given target.

        This essentially applies the given item to the ``.target`` attribute
        of the returned :class:`_schema.DDLElement` object.  This target
        is then usable by event handlers and compilation routines in order to
        provide services such as tokenization of a DDL string in terms of a
        particular :class:`_schema.Table`.

        When a :class:`_schema.DDLElement` object is established as an event
        handler for the :meth:`_events.DDLEvents.before_create` or
        :meth:`_events.DDLEvents.after_create` events, and the event
        then occurs for a given target such as a :class:`_schema.Constraint`
        or :class:`_schema.Table`, that target is established with a copy
        of the :class:`_schema.DDLElement` object using this method, which
        then proceeds to the :meth:`_schema.DDLElement.execute` method
        in order to invoke the actual DDL instruction.

        :param target: a :class:`_schema.SchemaItem` that will be the subject
         of a DDL operation.

        :return: a copy of this :class:`_schema.DDLElement` with the
         ``.target`` attribute assigned to the given
         :class:`_schema.SchemaItem`.

        .. seealso::

            :class:`_schema.DDL` - uses tokenization against the "target" when
            processing the DDL string.

        """
        ...
    
    @_generative
    def execute_if(self, dialect=..., callable_=..., state=...): # -> None:
        r"""Return a callable that will execute this
        :class:`_ddl.DDLElement` conditionally within an event handler.

        Used to provide a wrapper for event listening::

            event.listen(
                        metadata,
                        'before_create',
                        DDL("my_ddl").execute_if(dialect='postgresql')
                    )

        :param dialect: May be a string or tuple of strings.
          If a string, it will be compared to the name of the
          executing database dialect::

            DDL('something').execute_if(dialect='postgresql')

          If a tuple, specifies multiple dialect names::

            DDL('something').execute_if(dialect=('postgresql', 'mysql'))

        :param callable\_: A callable, which will be invoked with
          four positional arguments as well as optional keyword
          arguments:

            :ddl:
              This DDL element.

            :target:
              The :class:`_schema.Table` or :class:`_schema.MetaData`
              object which is the
              target of this event. May be None if the DDL is executed
              explicitly.

            :bind:
              The :class:`_engine.Connection` being used for DDL execution

            :tables:
              Optional keyword argument - a list of Table objects which are to
              be created/ dropped within a MetaData.create_all() or drop_all()
              method call.

            :state:
              Optional keyword argument - will be the ``state`` argument
              passed to this function.

            :checkfirst:
             Keyword argument, will be True if the 'checkfirst' flag was
             set during the call to ``create()``, ``create_all()``,
             ``drop()``, ``drop_all()``.

          If the callable returns a True value, the DDL statement will be
          executed.

        :param state: any value which will be passed to the callable\_
          as the ``state`` keyword argument.

        .. seealso::

            :class:`.DDLEvents`

            :ref:`event_toplevel`

        """
        ...
    
    def __call__(self, target, bind, **kw): # -> None:
        """Execute the DDL as a ddl_listener."""
        ...
    
    def bind(self): # -> None:
        ...
    
    bind = ...


class DDL(DDLElement):
    """A literal DDL statement.

    Specifies literal SQL DDL to be executed by the database.  DDL objects
    function as DDL event listeners, and can be subscribed to those events
    listed in :class:`.DDLEvents`, using either :class:`_schema.Table` or
    :class:`_schema.MetaData` objects as targets.
    Basic templating support allows
    a single DDL instance to handle repetitive tasks for multiple tables.

    Examples::

      from sqlalchemy import event, DDL

      tbl = Table('users', metadata, Column('uid', Integer))
      event.listen(tbl, 'before_create', DDL('DROP TRIGGER users_trigger'))

      spow = DDL('ALTER TABLE %(table)s SET secretpowers TRUE')
      event.listen(tbl, 'after_create', spow.execute_if(dialect='somedb'))

      drop_spow = DDL('ALTER TABLE users SET secretpowers FALSE')
      connection.execute(drop_spow)

    When operating on Table events, the following ``statement``
    string substitutions are available::

      %(table)s  - the Table name, with any required quoting applied
      %(schema)s - the schema name, with any required quoting applied
      %(fullname)s - the Table name including schema, quoted if needed

    The DDL's "context", if any, will be combined with the standard
    substitutions noted above.  Keys present in the context will override
    the standard substitutions.

    """
    __visit_name__ = ...
    @util.deprecated_params(bind=("2.0", "The :paramref:`_ddl.DDL.bind` argument is deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, statement, context=..., bind=...) -> None:
        """Create a DDL statement.

        :param statement:
          A string or unicode string to be executed.  Statements will be
          processed with Python's string formatting operator using
          a fixed set of string substitutions, as well as additional
          substitutions provided by the optional :paramref:`.DDL.context`
          parameter.

          A literal '%' in a statement must be escaped as '%%'.

          SQL bind parameters are not available in DDL statements.

        :param context:
          Optional dictionary, defaults to None.  These values will be
          available for use in string substitutions on the DDL statement.

        :param bind:
          Optional. A :class:`.Connectable`, used by
          default when ``execute()`` is invoked without a bind argument.


        .. seealso::

            :class:`.DDLEvents`

            :ref:`event_toplevel`

        """
        ...
    
    def __repr__(self): # -> str:
        ...
    


class _CreateDropBase(DDLElement):
    """Base class for DDL constructs that represent CREATE and DROP or
    equivalents.

    The common theme of _CreateDropBase is a single
    ``element`` attribute which refers to the element
    to be created or dropped.

    """
    @util.deprecated_params(bind=("2.0", "The :paramref:`_ddl.DDLElement.bind` argument is " "deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, element, bind=..., if_exists=..., if_not_exists=..., _legacy_bind=...) -> None:
        ...
    
    @property
    def stringify_dialect(self):
        ...
    


class CreateSchema(_CreateDropBase):
    """Represent a CREATE SCHEMA statement.

    The argument here is the string name of the schema.

    """
    __visit_name__ = ...
    def __init__(self, name, quote=..., **kw) -> None:
        """Create a new :class:`.CreateSchema` construct."""
        ...
    


class DropSchema(_CreateDropBase):
    """Represent a DROP SCHEMA statement.

    The argument here is the string name of the schema.

    """
    __visit_name__ = ...
    def __init__(self, name, quote=..., cascade=..., **kw) -> None:
        """Create a new :class:`.DropSchema` construct."""
        ...
    


class CreateTable(_CreateDropBase):
    """Represent a CREATE TABLE statement."""
    __visit_name__ = ...
    @util.deprecated_params(bind=("2.0", "The :paramref:`_ddl.CreateTable.bind` argument is deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, element, bind=..., include_foreign_key_constraints=..., if_not_exists=...) -> None:
        """Create a :class:`.CreateTable` construct.

        :param element: a :class:`_schema.Table` that's the subject
         of the CREATE
        :param on: See the description for 'on' in :class:`.DDL`.
        :param bind: See the description for 'bind' in :class:`.DDL`.
        :param include_foreign_key_constraints: optional sequence of
         :class:`_schema.ForeignKeyConstraint` objects that will be included
         inline within the CREATE construct; if omitted, all foreign key
         constraints that do not specify use_alter=True are included.

         .. versionadded:: 1.0.0

        :param if_not_exists: if True, an IF NOT EXISTS operator will be
         applied to the construct.

         .. versionadded:: 1.4.0b2

        """
        ...
    


class _DropView(_CreateDropBase):
    """Semi-public 'DROP VIEW' construct.

    Used by the test suite for dialect-agnostic drops of views.
    This object will eventually be part of a public "view" API.

    """
    __visit_name__ = ...


class CreateColumn(_DDLCompiles):
    """Represent a :class:`_schema.Column`
    as rendered in a CREATE TABLE statement,
    via the :class:`.CreateTable` construct.

    This is provided to support custom column DDL within the generation
    of CREATE TABLE statements, by using the
    compiler extension documented in :ref:`sqlalchemy.ext.compiler_toplevel`
    to extend :class:`.CreateColumn`.

    Typical integration is to examine the incoming :class:`_schema.Column`
    object, and to redirect compilation if a particular flag or condition
    is found::

        from sqlalchemy import schema
        from sqlalchemy.ext.compiler import compiles

        @compiles(schema.CreateColumn)
        def compile(element, compiler, **kw):
            column = element.element

            if "special" not in column.info:
                return compiler.visit_create_column(element, **kw)

            text = "%s SPECIAL DIRECTIVE %s" % (
                    column.name,
                    compiler.type_compiler.process(column.type)
                )
            default = compiler.get_column_default_string(column)
            if default is not None:
                text += " DEFAULT " + default

            if not column.nullable:
                text += " NOT NULL"

            if column.constraints:
                text += " ".join(
                            compiler.process(const)
                            for const in column.constraints)
            return text

    The above construct can be applied to a :class:`_schema.Table`
    as follows::

        from sqlalchemy import Table, Metadata, Column, Integer, String
        from sqlalchemy import schema

        metadata = MetaData()

        table = Table('mytable', MetaData(),
                Column('x', Integer, info={"special":True}, primary_key=True),
                Column('y', String(50)),
                Column('z', String(20), info={"special":True})
            )

        metadata.create_all(conn)

    Above, the directives we've added to the :attr:`_schema.Column.info`
    collection
    will be detected by our custom compilation scheme::

        CREATE TABLE mytable (
                x SPECIAL DIRECTIVE INTEGER NOT NULL,
                y VARCHAR(50),
                z SPECIAL DIRECTIVE VARCHAR(20),
            PRIMARY KEY (x)
        )

    The :class:`.CreateColumn` construct can also be used to skip certain
    columns when producing a ``CREATE TABLE``.  This is accomplished by
    creating a compilation rule that conditionally returns ``None``.
    This is essentially how to produce the same effect as using the
    ``system=True`` argument on :class:`_schema.Column`, which marks a column
    as an implicitly-present "system" column.

    For example, suppose we wish to produce a :class:`_schema.Table`
    which skips
    rendering of the PostgreSQL ``xmin`` column against the PostgreSQL
    backend, but on other backends does render it, in anticipation of a
    triggered rule.  A conditional compilation rule could skip this name only
    on PostgreSQL::

        from sqlalchemy.schema import CreateColumn

        @compiles(CreateColumn, "postgresql")
        def skip_xmin(element, compiler, **kw):
            if element.element.name == 'xmin':
                return None
            else:
                return compiler.visit_create_column(element, **kw)


        my_table = Table('mytable', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('xmin', Integer)
                )

    Above, a :class:`.CreateTable` construct will generate a ``CREATE TABLE``
    which only includes the ``id`` column in the string; the ``xmin`` column
    will be omitted, but only against the PostgreSQL backend.

    """
    __visit_name__ = ...
    def __init__(self, element) -> None:
        ...
    


class DropTable(_CreateDropBase):
    """Represent a DROP TABLE statement."""
    __visit_name__ = ...
    @util.deprecated_params(bind=("2.0", "The :paramref:`_ddl.DropTable.bind` argument is " "deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, element, bind=..., if_exists=...) -> None:
        """Create a :class:`.DropTable` construct.

        :param element: a :class:`_schema.Table` that's the subject
         of the DROP.
        :param on: See the description for 'on' in :class:`.DDL`.
        :param bind: See the description for 'bind' in :class:`.DDL`.
        :param if_exists: if True, an IF EXISTS operator will be applied to the
         construct.

         .. versionadded:: 1.4.0b2

        """
        ...
    


class CreateSequence(_CreateDropBase):
    """Represent a CREATE SEQUENCE statement."""
    __visit_name__ = ...


class DropSequence(_CreateDropBase):
    """Represent a DROP SEQUENCE statement."""
    __visit_name__ = ...


class CreateIndex(_CreateDropBase):
    """Represent a CREATE INDEX statement."""
    __visit_name__ = ...
    @util.deprecated_params(bind=("2.0", "The :paramref:`_ddl.CreateIndex.bind` argument is " "deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, element, bind=..., if_not_exists=...) -> None:
        """Create a :class:`.Createindex` construct.

        :param element: a :class:`_schema.Index` that's the subject
         of the CREATE.
        :param on: See the description for 'on' in :class:`.DDL`.
        :param bind: See the description for 'bind' in :class:`.DDL`.
        :param if_not_exists: if True, an IF NOT EXISTS operator will be
         applied to the construct.

         .. versionadded:: 1.4.0b2

        """
        ...
    


class DropIndex(_CreateDropBase):
    """Represent a DROP INDEX statement."""
    __visit_name__ = ...
    @util.deprecated_params(bind=("2.0", "The :paramref:`_ddl.DropIndex.bind` argument is " "deprecated and " "will be removed in SQLAlchemy 2.0."))
    def __init__(self, element, bind=..., if_exists=...) -> None:
        """Create a :class:`.DropIndex` construct.

        :param element: a :class:`_schema.Index` that's the subject
         of the DROP.
        :param on: See the description for 'on' in :class:`.DDL`.
        :param bind: See the description for 'bind' in :class:`.DDL`.
        :param if_exists: if True, an IF EXISTS operator will be applied to the
         construct.

         .. versionadded:: 1.4.0b2

        """
        ...
    


class AddConstraint(_CreateDropBase):
    """Represent an ALTER TABLE ADD CONSTRAINT statement."""
    __visit_name__ = ...
    def __init__(self, element, *args, **kw) -> None:
        ...
    


class DropConstraint(_CreateDropBase):
    """Represent an ALTER TABLE DROP CONSTRAINT statement."""
    __visit_name__ = ...
    def __init__(self, element, cascade=..., **kw) -> None:
        ...
    


class SetTableComment(_CreateDropBase):
    """Represent a COMMENT ON TABLE IS statement."""
    __visit_name__ = ...


class DropTableComment(_CreateDropBase):
    """Represent a COMMENT ON TABLE '' statement.

    Note this varies a lot across database backends.

    """
    __visit_name__ = ...


class SetColumnComment(_CreateDropBase):
    """Represent a COMMENT ON COLUMN IS statement."""
    __visit_name__ = ...


class DropColumnComment(_CreateDropBase):
    """Represent a COMMENT ON COLUMN IS NULL statement."""
    __visit_name__ = ...


class DDLBase(SchemaVisitor):
    def __init__(self, connection) -> None:
        ...
    


class SchemaGenerator(DDLBase):
    def __init__(self, dialect, connection, checkfirst=..., tables=..., **kwargs) -> None:
        ...
    
    def visit_metadata(self, metadata): # -> None:
        ...
    
    def visit_table(self, table, create_ok=..., include_foreign_key_constraints=..., _is_metadata_operation=...): # -> None:
        ...
    
    def visit_foreign_key_constraint(self, constraint): # -> None:
        ...
    
    def visit_sequence(self, sequence, create_ok=...): # -> None:
        ...
    
    def visit_index(self, index, create_ok=...): # -> None:
        ...
    


class SchemaDropper(DDLBase):
    def __init__(self, dialect, connection, checkfirst=..., tables=..., **kwargs) -> None:
        ...
    
    def visit_metadata(self, metadata): # -> None:
        ...
    
    def visit_index(self, index, drop_ok=...): # -> None:
        ...
    
    def visit_table(self, table, drop_ok=..., _is_metadata_operation=..., _ignore_sequences=...): # -> None:
        ...
    
    def visit_foreign_key_constraint(self, constraint): # -> None:
        ...
    
    def visit_sequence(self, sequence, drop_ok=...): # -> None:
        ...
    


def sort_tables(tables, skip_fn=..., extra_dependencies=...): # -> list[Any]:
    """Sort a collection of :class:`_schema.Table` objects based on
    dependency.

    This is a dependency-ordered sort which will emit :class:`_schema.Table`
    objects such that they will follow their dependent :class:`_schema.Table`
    objects.
    Tables are dependent on another based on the presence of
    :class:`_schema.ForeignKeyConstraint`
    objects as well as explicit dependencies
    added by :meth:`_schema.Table.add_is_dependent_on`.

    .. warning::

        The :func:`._schema.sort_tables` function cannot by itself
        accommodate automatic resolution of dependency cycles between
        tables, which are usually caused by mutually dependent foreign key
        constraints. When these cycles are detected, the foreign keys
        of these tables are omitted from consideration in the sort.
        A warning is emitted when this condition occurs, which will be an
        exception raise in a future release.   Tables which are not part
        of the cycle will still be returned in dependency order.

        To resolve these cycles, the
        :paramref:`_schema.ForeignKeyConstraint.use_alter` parameter may be
        applied to those constraints which create a cycle.  Alternatively,
        the :func:`_schema.sort_tables_and_constraints` function will
        automatically return foreign key constraints in a separate
        collection when cycles are detected so that they may be applied
        to a schema separately.

        .. versionchanged:: 1.3.17 - a warning is emitted when
           :func:`_schema.sort_tables` cannot perform a proper sort due to
           cyclical dependencies.  This will be an exception in a future
           release.  Additionally, the sort will continue to return
           other tables not involved in the cycle in dependency order
           which was not the case previously.

    :param tables: a sequence of :class:`_schema.Table` objects.

    :param skip_fn: optional callable which will be passed a
     :class:`_schema.ForeignKey` object; if it returns True, this
     constraint will not be considered as a dependency.  Note this is
     **different** from the same parameter in
     :func:`.sort_tables_and_constraints`, which is
     instead passed the owning :class:`_schema.ForeignKeyConstraint` object.

    :param extra_dependencies: a sequence of 2-tuples of tables which will
     also be considered as dependent on each other.

    .. seealso::

        :func:`.sort_tables_and_constraints`

        :attr:`_schema.MetaData.sorted_tables` - uses this function to sort


    """
    ...

def sort_tables_and_constraints(tables, filter_fn=..., extra_dependencies=..., _warn_for_cycles=...): # -> list[tuple[Any, Any]]:
    """Sort a collection of :class:`_schema.Table`  /
    :class:`_schema.ForeignKeyConstraint`
    objects.

    This is a dependency-ordered sort which will emit tuples of
    ``(Table, [ForeignKeyConstraint, ...])`` such that each
    :class:`_schema.Table` follows its dependent :class:`_schema.Table`
    objects.
    Remaining :class:`_schema.ForeignKeyConstraint`
    objects that are separate due to
    dependency rules not satisfied by the sort are emitted afterwards
    as ``(None, [ForeignKeyConstraint ...])``.

    Tables are dependent on another based on the presence of
    :class:`_schema.ForeignKeyConstraint` objects, explicit dependencies
    added by :meth:`_schema.Table.add_is_dependent_on`,
    as well as dependencies
    stated here using the :paramref:`~.sort_tables_and_constraints.skip_fn`
    and/or :paramref:`~.sort_tables_and_constraints.extra_dependencies`
    parameters.

    :param tables: a sequence of :class:`_schema.Table` objects.

    :param filter_fn: optional callable which will be passed a
     :class:`_schema.ForeignKeyConstraint` object,
     and returns a value based on
     whether this constraint should definitely be included or excluded as
     an inline constraint, or neither.   If it returns False, the constraint
     will definitely be included as a dependency that cannot be subject
     to ALTER; if True, it will **only** be included as an ALTER result at
     the end.   Returning None means the constraint is included in the
     table-based result unless it is detected as part of a dependency cycle.

    :param extra_dependencies: a sequence of 2-tuples of tables which will
     also be considered as dependent on each other.

    .. versionadded:: 1.0.0

    .. seealso::

        :func:`.sort_tables`


    """
    ...

