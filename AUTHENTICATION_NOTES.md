# Authentication Notes

## Authentication

Authentication means verifying who the user is.

Example:
A user provides a username and password during login.
Django checks whether the credentials are correct.

Authentication answers:

"Who are you?"

## Authorization

Authorization means checking what an authenticated user is allowed to do.

Example:
A normal employee may be allowed to view employee information,
while an admin may be allowed to create, update, or delete records.

Authorization answers:

"What are you allowed to do?"

## Difference

| Authentication | Authorization |
|---|---|
| Verifies user identity | Checks user permissions |
| Happens during login | Happens after authentication |
| Example: username and password | Example: admin permission |
| Answers "Who are you?" | Answers "What can you do?" |

## Django User Fields

Django provides a built-in User model with fields such as:

- username
- email
- password
- first_name
- last_name
- is_active
- is_staff
- is_superuser

## Password Security

Passwords should never be stored as plain text.

Django uses a password hashing mechanism to securely store passwords.

The original password is not stored directly in the database.

When a user logs in, Django checks the entered password against
the stored password hash.