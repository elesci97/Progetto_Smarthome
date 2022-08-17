from dataclasses import dataclass


@dataclass
class user:
    ip: str


userlist = []


def login(ip):
    print(f"{ip} ha effettuato il login.")
    userlist.append(user(ip))


def is_logged_in(ip):
    for user in userlist:
        if user.ip == ip:
            return True
    return False
