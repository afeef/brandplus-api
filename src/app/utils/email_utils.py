from typing import Dict
from urllib.parse import urlparse, urljoin

from app.settings import settings
from app.tasks import send_message
from app.utils.token_utils import generate_confirmation_token, generate_reset_password_token


def get_user_domain(user):
    subdomain = user.get('subdomain')
    url = settings.frontend_url

    if not subdomain:
        return url

    # Get the hostname from the URL
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    # Check if the hostname is the local IP address or a reserved keyword
    is_local_url = hostname.startswith('127.') or hostname.startswith('192.168.') or hostname == '::1' or \
                   hostname in ('localhost', 'localhost.localdomain')

    if is_local_url:
        return url
    else:
        domain = hostname.split('.', 1)[1]
        new_hostname = f"{subdomain}.{domain}"
        parsed_url = parsed_url._replace(netloc=parsed_url.netloc.replace(hostname, new_hostname))
        return parsed_url.geturl()


def send_verification_email(user: Dict):
    email = user.get('email')
    first_name = user.get('first_name')
    last_name = user.get('last_name')
    token = generate_confirmation_token(email)
    confirmation_link = urljoin(get_user_domain(user), '/login/' + token)

    send_message(queue_name='email-transmitter', data={
        "event": "WELCOME_EMAIL",
        "to_users": [{
            'email': email,
            'username': f'{first_name} {last_name}'
        }],
        "data": {
            "recipient_name": f"{first_name} {last_name}",
            "confirmation_link": confirmation_link
        }
    })


def send_password_reset_email(user: Dict):
    email = user.get('email')
    token = generate_reset_password_token(email)
    password_reset_url = urljoin(get_user_domain(user), '/reset-password/' + token)
    send_message(queue_name='email-transmitter', data={
        "event": "RESET_PASSWORD",
        "to_users": [{
            'email': user.get('email'),
            'username': f'{user.get("first_name")} {user.get("last_name")}'
        }],
        "data": {
            'password_reset_url': password_reset_url,
            "recipient_name": f'{user.get("first_name")} {user.get("last_name")}'
        }
    })
