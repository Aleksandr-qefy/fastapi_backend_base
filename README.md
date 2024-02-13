# Заготовка бэкенда на fastapi
Пример базовой структуры бэкенда на fastapi с PostgreSQL в качестве БД. 

Для регистрации используется письмо с сылкой, для подтверждения почты пользователя. Авторизация возможна через ник или почту. Пароль шифруется библиотекой bcrypt,
т.о. в БД сохраняется хешированный пароль, и нет возможности восстановить пароль из хеша. Для взаимодействия клиента с api используется технология JWT. Это позволяет 
пользователю с помощью токена производить доступные для него действия с бэкенда.
 
