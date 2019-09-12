# -*- coding: utf-8 -*-
import abc

from functools import reduce

from django.apps import apps

from django.utils.translation import ugettext as _
from rest_framework.permissions import BasePermission
import inspect


######################################################################
# Base permissiones definition
######################################################################

class ResourcePermission(BasePermission):
    """
    Base class for define resource permissions.
    """
    metadata_perms = None
    None_perms = None
    enought_perms = None
    global_perms = None
    retrieve_perms = None
    create_perms = None
    update_perms = None
    destroy_perms = None
    list_perms = None

    def has_permission(self, request, view):
        permset = getattr(self, "{}_perms".format(view.action))

        if isinstance(permset, (list, tuple)):
            permset = reduce(lambda acc, v: acc & v, permset)
        elif permset is None:
            # Use empty operator that always return true with
            # empty components.
            permset = And()
        elif isinstance(permset, PermissionComponent):
            # Do nothing
            pass
        elif inspect.isclass(permset) and issubclass(permset, PermissionComponent):
            permset = permset()
        else:
            raise RuntimeError(_("Invalid permission definition."))

        if self.global_perms:
            permset = (self.global_perms & permset)

        if self.enought_perms:
            permset = (self.enought_perms | permset)

        return permset.has_permission(request,view)

    def has_object_permission(self, request, view, obj:object=None):
        permset = getattr(self, "{}_perms".format(view.action))

        if isinstance(permset, (list, tuple)):
            permset = reduce(lambda acc, v: acc & v, permset)
        elif permset is None:
            # Use empty operator that always return true with
            # empty components.
            permset = And()
        elif isinstance(permset, PermissionComponent):
            # Do nothing
            pass
        elif inspect.isclass(permset) and issubclass(permset, PermissionComponent):
            permset = permset()
        else:
            raise RuntimeError(_("Invalid permission definition."))

        if self.global_perms:
            permset = (self.global_perms & permset)

        if self.enought_perms:
            permset = (self.enought_perms | permset)

        return permset.has_object_permission(request,view,obj)


class PermissionComponent(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def has_object_permission(self, request, view, obj=None):
        pass

    def __invert__(self):
        return Not(self)

    def __and__(self, component):
        return And(self, component)

    def __or__(self, component):
        return Or(self, component)


class PermissionOperator(PermissionComponent):
    """
    Base class for all logical operators for compose
    components.
    """

    def __init__(self, *components):
        self.components = tuple(components)


class Not(PermissionOperator):
    """
    Negation operator as permission composable component.
    """

    # Overwrites the default constructor for fix
    # to one parameter instead of variable list of them.
    def __init__(self, component):
        super().__init__(component)

    def has_object_permission(self, *args, **kwargs):
        component = self.components[0]
        return (not component.has_object_permission(*args, **kwargs))

    def has_permission(self, *args, **kwargs):
        component = self.components[0]
        return (not component.has_permission(*args, **kwargs))


class Or(PermissionOperator):
    """
    Or logical operator as permission component.
    """

    def has_object_permission(self, *args, **kwargs):
        valid = False

        for component in self.components:
            if component.has_object_permission(*args, **kwargs):
                valid = True
                break

        return valid


    def has_permission(self, *args, **kwargs):
        valid = False

        for component in self.components:
            if component.has_permission(*args, **kwargs):
                valid = True
                break

        return valid

class And(PermissionOperator):
    """
    And logical operator as permission component.
    """

    def has_object_permission(self, *args, **kwargs):
        valid = True

        for component in self.components:
            if not component.has_object_permission(*args, **kwargs):
                valid = False
                break

        return valid

    def has_permission(self, *args, **kwargs):
        valid = True

        for component in self.components:
            if component.has_permission(*args, **kwargs):
                valid = True
                break

        return valid


######################################################################
# Generic components.
######################################################################

class AllowAny(PermissionComponent):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj=None):
        return True


class DenyAll(PermissionComponent):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj=None):
        return False


class IsAuthenticated(PermissionComponent):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj=None):
        return request.user and request.user.is_authenticated


class IsSuperUser(PermissionComponent):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj=None):
        return request.user.is_authenticated and request.user.is_superuser

class IsObjectOwner(IsAuthenticated):

    def has_object_permission(self, request, view, obj=None):
        if obj.owner is None:
            return False

        return obj.owner == request.user

class IsAnonymous(PermissionComponent):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        else:
            return True

    def has_object_permission(self, request, view, obj=None):
        if request.user.is_authenticated:
            return False
        else:
            return True

######################################################################
# Generic permissions.
######################################################################

class AllowAnyPermission(ResourcePermission):
    enought_perms = AllowAny()


class IsAuthenticatedPermission(ResourcePermission):
    enought_perms = IsAuthenticated()


class AppResourcePermission(ResourcePermission):
    enought_perms = IsSuperUser()


######################################################################
# Common perms
######################################################################

class IsTheSameUser(PermissionComponent):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj=None):
        return obj and request.user.is_authenticated and request.user.pk == obj.pk

