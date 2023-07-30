"""
Add users to database who are added as SYSTEM_ADMIN_EMAIL_LIST
"""
import logging
import time

from app.models import User, UserRoleEnum
from app.settings import settings


def load_system_admins():
    logging.info(f"Creating system admins...")
    repo = settings.get_repo()
    admin_emails = settings.system_admin_email_list.split(',')
    for email in admin_emails:
        user = repo.get_user_by_email(email)
        if user is None:
            user = User(
                first_name="System",
                last_name="Admin",
                email=email,
                raw_password=settings.system_admin_default_password,
                verified=True,
                verified_on=int(time.time()),
                role=UserRoleEnum.SUPER_ADMIN
            )
            repo.register_user(user=user)

    super_admin_users = repo.get_user_by_role(role=UserRoleEnum.SUPER_ADMIN)
    for user in super_admin_users:
        if user.email not in admin_emails:
            repo.delete_user(user)
            logging.warning(f"Removed user {user.email} from system admin")


def run(retires: int = 5):
    try:
        load_system_admins()
    except Exception as ex:
        logging.exception(ex)
        logging.warning("Retrying creating system admins")
        retires -= 1
        time.sleep(0.1)
        run(retires=retires)


if __name__ == "__main__":
    run()
