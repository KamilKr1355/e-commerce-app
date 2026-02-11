from src.auth.authenticate import RoleChecker
from src.users.constants import Role

user_required = RoleChecker([Role.user, Role.admin, Role.superadmin]) 
admin_required = RoleChecker([Role.admin, Role.superadmin]) 
superadmin_required = RoleChecker([Role.superadmin]) 
allow_any = RoleChecker([])
