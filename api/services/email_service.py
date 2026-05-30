import logging

from django.core.mail import EmailMessage

from django.template.loader import render_to_string

from django.contrib.sites.shortcuts import (
    get_current_site
)

from django.utils.http import (
    urlsafe_base64_encode
)

from django.utils.encoding import (
    force_bytes
)

from accounts.tokens import (
    account_activation_token
)


logger = logging.getLogger(__name__)


def send_verification_email(
    request,
    user
):

    current_site = get_current_site(
        request
    )

    mail_subject = (
        'Activate your account'
    )

    message = render_to_string(

        'accounts/verify_email.html',

        {
            'user': user,

            'domain': current_site.domain,

            'uid': urlsafe_base64_encode(
                force_bytes(user.pk)
            ),

            'token': (
                account_activation_token.make_token(user)
            ),
        }
    )

    email = EmailMessage(

        mail_subject,

        message,

        to=[user.email]

    )

    email.content_subtype = "html"

    try:

        email.send()

        logger.info(
            f"Verification email sent to {user.email}"
        )

    except Exception as e:

        logger.error(
            f"Email sending failed: {str(e)}"
        )