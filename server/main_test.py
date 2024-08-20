from db.database import get_db
from db.models import add_user, get_users, update_user, delete_user

if __name__ == "__main__":
    db = next(get_db())
    add_user(db, "admin", "251115100")
    add_user(db, "admin1", "251115100")
    users = get_users(db)
    # error, user = update_user(db, users[0].auth_token, "251115100")
    # print("AFTER:update_user", user, error)
    delete_user(db, users[0].id)
    print("delete_user-------")
    users = get_users(db)
    print("users", users)
