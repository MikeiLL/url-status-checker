# Sample untracked-keys file
# If you get errors trying to 'import apikeys', do the following:
# 1) Copy this file to apikeys.py (keeping it in the package directory)
# 2) Replace all of the example values with real ones

# Generated like this:
# import base64, os; print(base64.b64encode(os.urandom(33)))

# These settings are used only for the sending of emails. The server will
# start with them at the defaults, but all email sending will fail.
system_email = 'server@example.com'
admin_email = 'username@example.com'

# Use https://pypi.org/project/Flask-SendGrid/ to implement SendGrid
SENDGRID_DEFAULT_FROM = "me@my.com"
SENDGRID_API_KEY = "SG.random-string-from-sendgrid"

url_list = [
  "https://infiniteglitch.net:81/status.json",
  "https://infiniteglitch.net",
  "https://app.gotagtech.com",
  "https://www.uruyoga.com",
  "https://uruyoga.com",
  "https://ellipticastudios.com",
  "https://intensity.club",
  "https://baughmanproperties.com",
  "https://jagletsproperties.com",
  "https://templeofwow.tv",
]
