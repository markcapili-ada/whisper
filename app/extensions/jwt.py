# import jwt
# from flask import current_app, request


# def get_user_from_header():
#     header_token = request.headers.get('Authorization').split()[1] if 'Authorization' in request.headers else None
#     param_token = request.args.get('token')
#     token = header_token or param_token

#     try:
#         data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
#         current_user = data
#     except Exception as e:
#         print(e)

#     return current_user
