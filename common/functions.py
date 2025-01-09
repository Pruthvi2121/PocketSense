from django.conf import settings
from rest_framework.exceptions import APIException
from django.template.loader import render_to_string
from django.core.mail import  EmailMultiAlternatives
from secrets import token_urlsafe
from django.utils.html import strip_tags
import logging
logger = logging.getLogger(__name__)
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse

# Serializers Error Messages Modified
def serailizer_errors(e:ValidationError):
    #checking if error is in dict
    
    if(isinstance(e.detail,dict)):
        error_detail = list(e.detail.items())[0]
        field_name, error_message = error_detail[0], str(error_detail[1][0])
        return field_name, error_message
    
    #checking if error is in list
    elif(isinstance(e.detail,list) ):
        error_detail = e.detail[0]
        return  "non_field_errors", error_detail
    
    else:
        return "Invalid data provided."
        

#  handle the nested serializers errors.
def handle_nested_serilizers_errors(e:ValidationError):
    def flatten_errors(errors, prefix=''):
        flat_errors = []
        for field, error in errors.items():
            if isinstance(error, dict):
                flat_errors.extend(flatten_errors(error, f"{prefix}{field}."))
            elif isinstance(error, list):
                flat_errors.append((f"{prefix}{field}", error[0]))
            else:
                flat_errors.append((f"{prefix}{field}", error))
        return flat_errors
    
    if isinstance(e.detail, dict) and any(isinstance(v, dict) for v in e.detail.values()):
       
        flat_errors = flatten_errors(e.detail)
        if flat_errors:
            field_name, error_message = flat_errors[0]
            return field_name, error_message
        return "unknown_field", "unknown_error"

    elif(isinstance(e.detail,dict)):
 
        error_detail = list(e.detail.items())[0]
        field_name, error_message = error_detail[0], str(error_detail[1][0])
        return field_name, error_message
    
    #checking if error is in list
    elif(isinstance(e.detail,list) ):
        error_detail = e.detail[0]
        return  "non_field_errors", error_detail
    
    else:
        return "Invalid data provided."
        


# Funtion to send Email
def send_email(subject: str, context: dict, to_emails: list, template_name: str) -> bool:
    """
    Send email with provided template and context
    """
    try:
        # Render email content
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)

        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails
        )
        email.attach_alternative(html_content, "text/html")

        # Send email 
        response = email.send()
        if response == 1:
            logger.info("Email sent successfully.")
            return True
        return False

    except Exception as ex:
        logger.error("Failed to send email.", exc_info=ex)
        raise APIException(detail=str(ex))
    

