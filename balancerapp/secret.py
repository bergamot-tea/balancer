MY_HOSTS = [
        '127.0.0.1',
        'localhost'
        ]
MY_SECRET_KEY = 'django-insecure-95m-luefus0*bnmkcx*n$wlfh$is*o=1_!%74_92qc$a8j7*v^'
MY_DEBUG = True
DB_NAME = 'postgres'
DB_HOST = 'db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
MY_TIME_ZONE = 'Europe/Moscow'


#исправляем ворнинги которые нам показывает python3 manage.py check --deploy
#все что ниже раскоментить только для прода

#SECURE_CONTENT_TYPE_NOSNIFF = True
#SECURE_BROWSER_XSS_FILTER = True
#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#X_FRAME_OPTIONS = 'DENY'

