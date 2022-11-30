# CoinCleave
Веб приложение на Flask. С использованием Flask-SocketIO, Celery, RabbitMQ, Binance-connector (SDK) и т.д...

Главная страница:
![image](https://user-images.githubusercontent.com/84917008/204903488-dcbd5eb2-4fe4-45e8-b933-9bded7279b8c.png)

На беке тут Flask, расширяющие модули:
1) Flask-Login для аутентификации пользователей
2) Flask-Mail для отправки почты (завёл для этого гугл почту, а там ещё старый способ подключиться к ней через приложение убрали, пришлось через спец. ключ)
3) Flask-SQLalchemy для ORM'ных SQL запросов, в общем то с алхимией давно общаюсь, удобная.
4) Flask-SocketIO в приложении есть экран с графиком и всякой другой информацией котороую нужно обнавлять в реал тайме. Стучать на сервер AJAX запросами через setInterval
накладно. (транзакционные издержки на установку соединения с сервером для http запроса)
5) Flask-Migrate как же я рад что сразу решил вкурить в миграцию на старте, не предствалю, что бы было со мной без неё. (migrate/upgrade было много)) )

База данных PostgreSQL.
Архитектура БД (схема днных):

![image](https://user-images.githubusercontent.com/84917008/204903418-ed66625a-6779-4c73-95c4-8fa4c9b48944.png)

Для I/O нагруженных задач, например, постучать на Binance за данными, использовал Celery. Такие задачи упаковывал в таски.
Так же использовал Celery для фоновых периодических задач: Цикл в котором крутяться боты (его нужно было без вариантов останавливать и запускать заново, т.к.
в Binance-connector (SDK) вебсокеты на Twisted, это значит их нельзя перезапустить в том же скрипте, при том что вебсокеты отваливаються каждые 24 часа),
апдейт торговых пар биржы на проверку новых (они используються для валидации одной формы), и обновление подписочного времени у пользователй (поминутно).
Задачи отправляются в тематические отдельные очереди: Core, Subc, Web.

В качестве брокера сообщений для Celery использовал RabbitMQ. Через него же, а точнее через новый virtual host, отправлял сообшения по румам, с сервера из таски, клиентам
по вебсокет соединению.

При необходимости асинхронно стучал на сервер с помощью AJAX (ну оно и не удивительно).

На фронте подключён Bootstrap, но чито для обших дефолтных стилей. Фронт писан на чистом HTML, CSS, JS + JQuery для AJAX, и ещё у него удобные селекторы)
Еще подключён CDN на вебсокеты с клиентской стороны. Для отрисовки графика использовал ChartJS.

Может что-то забыл, если вспомню допишу конечно...

А да, вспомнил, для работы с данными свечных графиков использовал pandas dataframe (удобно), вычисления разлиных индикаторов/осциляторов делал при помощи TA-lib.

Картиночки для понимания:

Рабочий экран с ботами:
![image](https://user-images.githubusercontent.com/84917008/204903895-67918e2e-7f23-4c32-8bbb-a16cec9675ec.png)

![image](https://user-images.githubusercontent.com/84917008/204123296-d69ab737-6314-4ce2-bc8b-2aebe29ff3f8.png)

![image](https://user-images.githubusercontent.com/84917008/204121325-51e0bece-9038-48a3-92f2-67e96e91cdab.png)
Экран настроек:
![image](https://user-images.githubusercontent.com/84917008/204904357-40f44efa-4079-44b0-afe4-6b9a45f22f2a.png)
Экран подписок:
![image](https://user-images.githubusercontent.com/84917008/204121375-355c5f34-ac44-4bf5-ba96-083a6ee05168.png)
Экран подписок (popup список покупок):
![image](https://user-images.githubusercontent.com/84917008/204904579-fa203830-e57d-4500-9d1b-c7bb8f76cb89.png)


