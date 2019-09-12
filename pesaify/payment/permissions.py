from pesaify.base.permissions import (AppResourcePermission,IsSuperUser,AllowAny,IsAuthenticated,PermissionComponent, IsAnonymous, IsTheSameUser, IsObjectOwner)

class EmailItemPermission(AppResourcePermission):
    enought_perms = IsSuperUser()
    global_perms = None
    retrieve_perms = IsObjectOwner()
    destroy_perms = IsObjectOwner()
    list_perms = IsObjectOwner()

class EmailBillPermission(AppResourcePermission):
    enought_perms = IsSuperUser()
    global_perms = None
    create_perms = IsAuthenticated()
    retrieve_perms = IsObjectOwner()
    destroy_perms = IsObjectOwner()
    list_perms = IsObjectOwner()
    resend_perms = IsObjectOwner()
    update_perms = AllowAny()
    partial_update_perms = AllowAny()

class ButtonPermission(AppResourcePermission):
    enought_perms = IsSuperUser()
    global_perms = None
    retrieve_perms = IsObjectOwner()
    list_perms = IsObjectOwner()
    update_perms = IsObjectOwner()
    partial_update_perms = IsObjectOwner()

class CheckoutPermission(AppResourcePermission):
    enought_perms = IsSuperUser()
    global_perms = None
    retrieve_perms = IsObjectOwner()
    list_perms = IsObjectOwner()
    update_perms = IsObjectOwner()
    partial_update_perms = IsObjectOwner()

class InvoicePermission(AppResourcePermission):
    enought_perms = IsSuperUser()
    global_perms = None
    retrieve_perms = IsObjectOwner()
    list_perms = IsObjectOwner()
    notify_perms = AllowAny()
