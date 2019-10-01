
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

Что нужно сделать предварительно:
* Зарегистрироваться в Я.Облаке: https://cloud.yandex.ru
* Создать себе два бакета в [Object Storage](https://cloud.yandex.ru/docs/storage/), назвать их `{BUCKET NAME}` 
и `tgalice-test-cold-storage` (вот это второе имя сейчас захардкожено в `main.py`)
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
сделать функцию публичной и выбрать её из выпадающего списка в консоли разработчика диалогов.

Все последующие редактирования функции можно выполнять прямо из веб-интерфейса, т.к. скорее всего 
большая часть работы затронет только два файла - `main.py` и `form.yaml`. 
Но, конечно, лучше всё-таки пользоваться системой контроля версий и прочими современными инструментами.

Этот пример написан по мотивам [примера от Глеба](https://github.com/monsterzz/yc-serverless-python-deps) 
(Глеб, спасибо тебе за работу в ночи!). Любые комментарии и правки принимаются.

(В частности, интересно будет попробовать разогнать Object Storage - пока что он иногда подтормаживает)
