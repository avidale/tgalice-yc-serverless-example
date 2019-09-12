
# tgalice + YC Serverless = <3

Этот репозиторий показывает, как можно разработать простенький stateful навык для Алисы 
на основе [serverless functions](https://cloud.yandex.ru/docs/serverless-functions/) (далее SF) 
из Яндекс.Облака и питонячьей библиотеки [tgalice](https://github.com/avidale/tgalice). 
В качестве "начинки" навыка у нас будет шуточный гороскоп - заодно покажем, как на `tgalice` можно делать
простенький form-filling.

Почему всё устроено так, как устроено:
* Для формирования среды выполнения функции в SF сейчас вручную нужно собирать все зависимости - 
это делает `Makefile` (но запускать его надо под Ubuntu)
* CLI интерфейс SF не позволяет загружать сборки более четырёх мегабайт - поэтому сборку предварительно
нужно залить в [Object Storage](https://cloud.yandex.ru/docs/storage/), и добавлять её в функции уже оттуда. 
* Object Storage нам понадобиться в любом случае - там будет храниться состояние диалога.
* Переменные окружения SF пока что можно задавать только через CLI, 
так что будем обновлять нашу функцию именно этим способом, а не через веб-интерфейс.

Что нужно сделать предварительно:
* Зарегистрироваться в Я.Облаке: https://cloud.yandex.ru
* Зарегистрироваться в [превью SF](https://cloud.yandex.ru/services/serverless-functions)
* Создать себе два бакета в [Object Storage](https://cloud.yandex.ru/docs/storage/), назвать их `{BUCKET NAME}` 
и `tgalice-test-state-storage` (вот это второе имя сейчас захардкожено в `main.py`)
* Создать [сервисный аккаунт](https://cloud.yandex.ru/docs/iam/concepts/users/service-accounts),
дать ему роль `editor`, и получить к нему статические креденшалы `{KEY ID}` и `{KEY VALUE}` - 
их будем использовать для записи состояния диалога. 
* Установить [интерфейс командной строки](https://cloud.yandex.ru/docs/cli/quickstart) `yc`

Фух, теперь можно, собственно, деплоить функцию:

```
make all
# теперь надо ручками загрузить dist.zip в бакет OBJECT STORAGE, из которого будем деплоиться 
yc serverless function version create\
    --function-name=horoscope\
    --environment=AWS_ACCESS_KEY_ID={KEY ID},AWS_SECRET_ACCESS_KEY={KEY VALUE}\
    --runtime=python37\
    --package-bucket-name={BUCKET NAME}\
    --package-object-name=dist.zip\
    --entrypoint=main.alice_handler\
    --memory=128M\
    --execution-timeout=3s
```
После того, как функция запущена, протестировать работу навыка можно подобно тому, как описано в 
[официальном примере](https://cloud.yandex.ru/docs/serverless-functions/solutions/alice-skill):
дописать к урлу функции `?integration=raw` и использовать это в качестве вебхука.

Этот пример написан по мотивам [примера от Глеба](https://github.com/monsterzz/yc-serverless-python-deps) 
(Глеб, спасибо тебе за работу в ночи!). Любые комментарии и правки принимаются.

(В частности, интересно будет попробовать разогнать Object Storage - пока что он мальца подтормаживает)
