"""Cliente y colecciones Mongo proporcionados por pcrenergy."""

from pcrenergy import client_local

mongo_client = client_local()
db_products = mongo_client.PRODUCTOS.Productos
db_user = mongo_client.USERS.Users
db_token = mongo_client.USERS.Token
db_otp = mongo_client.USERS.OtpChallenges
db_reset = mongo_client.USERS.PasswordResetGrants
db_oauth_state = mongo_client.USERS.OAuthStates
db_login_grant = mongo_client.USERS.LoginGrants
