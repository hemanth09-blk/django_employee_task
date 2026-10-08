from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from employees.models import Notification


class NotificationService:
    """
    Service layer responsible for creating notifications
    and sending notification emails.
    """

    @staticmethod
    def create_notification(
        *,
        title,
        message,
        recipient=None,
        employee=None,
        notification_type="SYSTEM",
        recipient_email=None,
    ):
        """
        Create and persist a notification.
        """

        notification = Notification.objects.create(
            recipient=recipient,
            employee=employee,
            notification_type=notification_type,
            title=title,
            message=message,
            recipient_email=recipient_email,
            status="PENDING",
        )

        return notification

    @staticmethod
    def send_email(
        *,
        notification,
        subject,
        template_name,
        context,
        recipient_email,
    ):
        """
        Send an HTML email for an existing notification.

        The notification status is updated to SENT or FAILED.
        """

        if not recipient_email:
            notification.status = "FAILED"
            notification.error_message = "Recipient email is missing."
            notification.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )
            return False

        try:
            html_content = render_to_string(
                template_name,
                context,
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=notification.message,
                to=[recipient_email],
            )

            email.attach_alternative(
                html_content,
                "text/html",
            )

            email.send()

            notification.status = "SENT"
            notification.error_message = None

            notification.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return True

        except Exception as exc:
            notification.status = "FAILED"
            notification.error_message = str(exc)

            notification.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return False

    @staticmethod
    def send_welcome_notification(employee, recipient=None):
        """
        Create and send a welcome notification for an employee.
        """

        recipient_email = employee.email

        notification = NotificationService.create_notification(
            recipient=recipient,
            employee=employee,
            notification_type="WELCOME",
            title="Welcome to the Employee Management System",
            message=(
                f"Welcome {employee.first_name} "
                f"{employee.last_name}!"
            ),
            recipient_email=recipient_email,
        )

        NotificationService.send_email(
            notification=notification,
            subject="Welcome to the Employee Management System",
            template_name="emails/welcome_email.html",
            context={
                "employee": employee,
                "notification": notification,
            },
            recipient_email=recipient_email,
        )

        return notification

    @staticmethod
    def mark_as_read(notification):
        """
        Mark a notification as read.
        """

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()

            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                ]
            )

        return notification