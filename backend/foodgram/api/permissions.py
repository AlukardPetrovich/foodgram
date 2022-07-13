from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Пермишенс класс предоставляющий доступ только создателю объекта
    """

    def has_object_permission(self, request, view, obj):
        return request.user and request.user == obj.author


class ReadOnly(permissions.BasePermission):
    """
    Пермишенс класс предоставляющий доступ только для чтения
    """

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
