# CSRF Security Notes

## What is CSRF?

Cross-Site Request Forgery (CSRF) is an attack where a malicious website
tries to make a user's browser send an unwanted request to an application
where the user is already authenticated.

## Why CSRF matters

CSRF is particularly important when authentication uses browser cookies,
because browsers automatically send cookies with matching requests.

## Authentication used in this project

This API uses JWT Bearer authentication.

Clients send the access token using:

Authorization: Bearer <access_token>

The JWT is not automatically attached to requests by the browser in the
same way as a session cookie.

Therefore, CSRF protection is not the primary security control for the
JWT-authenticated API endpoints.

## Django CSRF middleware

Django's CSRF middleware remains enabled:

django.middleware.csrf.CsrfViewMiddleware

This protects Django's cookie/session-based browser requests where CSRF
protection applies.

## Security conclusion

The API should continue using JWT authentication with protected endpoints
and appropriate authorization/permissions.

If the application later uses cookie-based authentication for API requests,
CSRF protection must be reviewed and configured accordingly.