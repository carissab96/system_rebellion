"""
This type stub file was generated by pyright.
"""

"""Exceptions used with SQLAlchemy.

The base exception class is :exc:`.SQLAlchemyError`.  Exceptions which are
raised as a result of DBAPI exceptions are all subclasses of
:exc:`.DBAPIError`.

"""
_version_token = ...
class HasDescriptionCode:
    """helper which adds 'code' as an attribute and '_code_str' as a method"""
    code = ...
    def __init__(self, *arg, **kw) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


class SQLAlchemyError(HasDescriptionCode, Exception):
    """Generic error class."""
    def __str__(self) -> str:
        ...
    
    def __unicode__(self): # -> str:
        ...
    


class ArgumentError(SQLAlchemyError):
    """Raised when an invalid or conflicting function argument is supplied.

    This error generally corresponds to construction time state errors.

    """
    ...


class ObjectNotExecutableError(ArgumentError):
    """Raised when an object is passed to .execute() that can't be
    executed as SQL.

    .. versionadded:: 1.1

    """
    def __init__(self, target) -> None:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[Any]]:
        ...
    


class NoSuchModuleError(ArgumentError):
    """Raised when a dynamically-loaded module (usually a database dialect)
    of a particular name cannot be located."""
    ...


class NoForeignKeysError(ArgumentError):
    """Raised when no foreign keys can be located between two selectables
    during a join."""
    ...


class AmbiguousForeignKeysError(ArgumentError):
    """Raised when more than one foreign key matching can be located
    between two selectables during a join."""
    ...


class CircularDependencyError(SQLAlchemyError):
    """Raised by topological sorts when a circular dependency is detected.

    There are two scenarios where this error occurs:

    * In a Session flush operation, if two objects are mutually dependent
      on each other, they can not be inserted or deleted via INSERT or
      DELETE statements alone; an UPDATE will be needed to post-associate
      or pre-deassociate one of the foreign key constrained values.
      The ``post_update`` flag described at :ref:`post_update` can resolve
      this cycle.
    * In a :attr:`_schema.MetaData.sorted_tables` operation, two
      :class:`_schema.ForeignKey`
      or :class:`_schema.ForeignKeyConstraint` objects mutually refer to each
      other.  Apply the ``use_alter=True`` flag to one or both,
      see :ref:`use_alter`.

    """
    def __init__(self, message, cycles, edges, msg=..., code=...) -> None:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[None, Any, Any, Any], dict[str, Any]]:
        ...
    


class CompileError(SQLAlchemyError):
    """Raised when an error occurs during SQL compilation"""
    ...


class UnsupportedCompilationError(CompileError):
    """Raised when an operation is not supported by the given compiler.

    .. seealso::

        :ref:`faq_sql_expression_string`

        :ref:`error_l7de`
    """
    code = ...
    def __init__(self, compiler, element_type, message=...) -> None:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[Any, Any, Any | None]]:
        ...
    


class IdentifierError(SQLAlchemyError):
    """Raised when a schema name is beyond the max character limit"""
    ...


class DisconnectionError(SQLAlchemyError):
    """A disconnect is detected on a raw DB-API connection.

    This error is raised and consumed internally by a connection pool.  It can
    be raised by the :meth:`_events.PoolEvents.checkout`
    event so that the host pool
    forces a retry; the exception will be caught three times in a row before
    the pool gives up and raises :class:`~sqlalchemy.exc.InvalidRequestError`
    regarding the connection attempt.

    """
    invalidate_pool = ...


class InvalidatePoolError(DisconnectionError):
    """Raised when the connection pool should invalidate all stale connections.

    A subclass of :class:`_exc.DisconnectionError` that indicates that the
    disconnect situation encountered on the connection probably means the
    entire pool should be invalidated, as the database has been restarted.

    This exception will be handled otherwise the same way as
    :class:`_exc.DisconnectionError`, allowing three attempts to reconnect
    before giving up.

    .. versionadded:: 1.2

    """
    invalidate_pool = ...


class TimeoutError(SQLAlchemyError):
    """Raised when a connection pool times out on getting a connection."""
    ...


class InvalidRequestError(SQLAlchemyError):
    """SQLAlchemy was asked to do something it can't do.

    This error generally corresponds to runtime state errors.

    """
    ...


class NoInspectionAvailable(InvalidRequestError):
    """A subject passed to :func:`sqlalchemy.inspection.inspect` produced
    no context for inspection."""
    ...


class PendingRollbackError(InvalidRequestError):
    """A transaction has failed and needs to be rolled back before
    continuing.

    .. versionadded:: 1.4

    """
    ...


class ResourceClosedError(InvalidRequestError):
    """An operation was requested from a connection, cursor, or other
    object that's in a closed state."""
    ...


class NoSuchColumnError(InvalidRequestError, KeyError):
    """A nonexistent column is requested from a ``Row``."""
    ...


class NoResultFound(InvalidRequestError):
    """A database result was required but none was found.


    .. versionchanged:: 1.4  This exception is now part of the
       ``sqlalchemy.exc`` module in Core, moved from the ORM.  The symbol
       remains importable from ``sqlalchemy.orm.exc``.


    """
    ...


class MultipleResultsFound(InvalidRequestError):
    """A single database result was required but more than one were found.

    .. versionchanged:: 1.4  This exception is now part of the
       ``sqlalchemy.exc`` module in Core, moved from the ORM.  The symbol
       remains importable from ``sqlalchemy.orm.exc``.


    """
    ...


class NoReferenceError(InvalidRequestError):
    """Raised by ``ForeignKey`` to indicate a reference cannot be resolved."""
    ...


class AwaitRequired(InvalidRequestError):
    """Error raised by the async greenlet spawn if no async operation
    was awaited when it required one.

    """
    code = ...


class MissingGreenlet(InvalidRequestError):
    r"""Error raised by the async greenlet await\_ if called while not inside
    the greenlet spawn context.

    """
    code = ...


class NoReferencedTableError(NoReferenceError):
    """Raised by ``ForeignKey`` when the referred ``Table`` cannot be
    located.

    """
    def __init__(self, message, tname) -> None:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[Any, Any]]:
        ...
    


class NoReferencedColumnError(NoReferenceError):
    """Raised by ``ForeignKey`` when the referred ``Column`` cannot be
    located.

    """
    def __init__(self, message, tname, cname) -> None:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[Any, Any, Any]]:
        ...
    


class NoSuchTableError(InvalidRequestError):
    """Table does not exist or is not visible to a connection."""
    ...


class UnreflectableTableError(InvalidRequestError):
    """Table exists but can't be reflected for some reason.

    .. versionadded:: 1.2

    """
    ...


class UnboundExecutionError(InvalidRequestError):
    """SQL was attempted without a database connection to execute it on."""
    ...


class DontWrapMixin:
    """A mixin class which, when applied to a user-defined Exception class,
    will not be wrapped inside of :exc:`.StatementError` if the error is
    emitted within the process of executing a statement.

    E.g.::

        from sqlalchemy.exc import DontWrapMixin

        class MyCustomException(Exception, DontWrapMixin):
            pass

        class MySpecialType(TypeDecorator):
            impl = String

            def process_bind_param(self, value, dialect):
                if value == 'invalid':
                    raise MyCustomException("invalid!")

    """
    ...


class StatementError(SQLAlchemyError):
    """An error occurred during execution of a SQL statement.

    :class:`StatementError` wraps the exception raised
    during execution, and features :attr:`.statement`
    and :attr:`.params` attributes which supply context regarding
    the specifics of the statement which had an issue.

    The wrapped exception object is available in
    the :attr:`.orig` attribute.

    """
    statement = ...
    params = ...
    orig = ...
    ismulti = ...
    def __init__(self, message, statement, params, orig, hide_parameters=..., code=..., ismulti=...) -> None:
        ...
    
    def add_detail(self, msg): # -> None:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[Any, Any | None, Any | None, Any | None, bool, Any | None, Any | None], dict[str, list[Any]]]:
        ...
    


class DBAPIError(StatementError):
    """Raised when the execution of a database operation fails.

    Wraps exceptions raised by the DB-API underlying the
    database operation.  Driver-specific implementations of the standard
    DB-API exception types are wrapped by matching sub-types of SQLAlchemy's
    :class:`DBAPIError` when possible.  DB-API's ``Error`` type maps to
    :class:`DBAPIError` in SQLAlchemy, otherwise the names are identical.  Note
    that there is no guarantee that different DB-API implementations will
    raise the same exception type for any given error condition.

    :class:`DBAPIError` features :attr:`~.StatementError.statement`
    and :attr:`~.StatementError.params` attributes which supply context
    regarding the specifics of the statement which had an issue, for the
    typical case when the error was raised within the context of
    emitting a SQL statement.

    The wrapped exception object is available in the
    :attr:`~.StatementError.orig` attribute. Its type and properties are
    DB-API implementation specific.

    """
    code = ...
    @classmethod
    def instance(cls, statement, params, orig, dbapi_base_err, hide_parameters=..., connection_invalidated=..., dialect=..., ismulti=...): # -> BaseException | DontWrapMixin | StatementError | Self | Any:
        ...
    
    def __reduce__(self): # -> tuple[type[Self], tuple[Any | None, Any | None, Any | None, bool, bool, Any | None, Any | None], dict[str, list[Any]]]:
        ...
    
    def __init__(self, statement, params, orig, hide_parameters=..., connection_invalidated=..., code=..., ismulti=...) -> None:
        ...
    


class InterfaceError(DBAPIError):
    """Wraps a DB-API InterfaceError."""
    code = ...


class DatabaseError(DBAPIError):
    """Wraps a DB-API DatabaseError."""
    code = ...


class DataError(DatabaseError):
    """Wraps a DB-API DataError."""
    code = ...


class OperationalError(DatabaseError):
    """Wraps a DB-API OperationalError."""
    code = ...


class IntegrityError(DatabaseError):
    """Wraps a DB-API IntegrityError."""
    code = ...


class InternalError(DatabaseError):
    """Wraps a DB-API InternalError."""
    code = ...


class ProgrammingError(DatabaseError):
    """Wraps a DB-API ProgrammingError."""
    code = ...


class NotSupportedError(DatabaseError):
    """Wraps a DB-API NotSupportedError."""
    code = ...


class SADeprecationWarning(HasDescriptionCode, DeprecationWarning):
    """Issued for usage of deprecated APIs."""
    deprecated_since = ...


class Base20DeprecationWarning(SADeprecationWarning):
    """Issued for usage of APIs specifically deprecated or legacy in
    SQLAlchemy 2.0.

    .. seealso::

        :ref:`error_b8d9`.

        :ref:`deprecation_20_mode`

    """
    deprecated_since = ...
    def __str__(self) -> str:
        ...
    


class LegacyAPIWarning(Base20DeprecationWarning):
    """indicates an API that is in 'legacy' status, a long term deprecation."""
    ...


class RemovedIn20Warning(Base20DeprecationWarning):
    """indicates an API that will be fully removed in SQLAlchemy 2.0."""
    ...


class MovedIn20Warning(RemovedIn20Warning):
    """Subtype of RemovedIn20Warning to indicate an API that moved only."""
    ...


class SAPendingDeprecationWarning(PendingDeprecationWarning):
    """A similar warning as :class:`_exc.SADeprecationWarning`, this warning
    is not used in modern versions of SQLAlchemy.

    """
    deprecated_since = ...


class SAWarning(HasDescriptionCode, RuntimeWarning):
    """Issued at runtime."""
    ...


