# Поисковый робот #
 
Напишите многопоточный поисковый робот (crawler), реализующий обход Web-графа в ширину и сохраняющий на диск все посещенные страницы.
 
При запуске роботу передаются адрес начальной страницы, максимальная глубина обхода, максимальное количество загружаемых страниц и путь к директории, в которую сохраняются посещенные страницы.
 
Робот не должен посещать одну и ту же страницу более одного раза.
 
Попытайтесь добиться максимальной скорости работы робота и обоснуйте используемый подход.
 
Программа должна быть реализована на C++ или Java. Другие языки программирования — по согласованию с преподавателем.
 
Программа должна поддерживать следующие аргументы командной строки:
 - Адрес начальной страницы;
 - Максимальная глубина обхода;
 - Максимальное количество загружаемых страниц;
 - Путь к директории, в который сохраняются посещенные страницы;
 
Все перечисленные аргументы являются обязательными и передаются в указанном порядке.
 
Программа может поддерживать дополнительные аргументы (например, количество потоков), следующие после описанных выше. При этом программа должна работать при отсутствии этих дополнительных аргументов, используя значения по-умолчанию или вычисляя их динамически.

Пример запуска программы:
    
    crawler http://www.yandex.ru/ 2 100 /home/sol/crawl/
 
Программа должна завершать работу при достижении максимальной глубины обхода или максимального количества загруженных страниц (что наступит раньше).

# Пример работы #
    
    > python crawler.py http://yandex.ru/ 2 10 down --debug --thread 3
    
    1414095768.23219 [0] start
    1414095768.23219 [0] want get work
    1414095768.23219 [1] start
    1414095768.23219 [0] get work and start working
    1414095768.23219 [1] want get work
    1414095768.23317 [0] START. URL http://yandex.ru/
    1414095768.23219 [2] start
    1414095768.23512 [2] want get work
    1414095768.60367 [0] STOP. WORKING 371ms [REQUEST: 249ms SAVE: 74ms PARSE: 46ms] WITH URL http://yandex.ru/
    1414095768.60367 [0] work completed (done); start do_something_with_work_result()
    1414095768.60367 [0] do_something_with_work_result completed
    1414095768.60465 [1] get work and start working
    1414095768.60465 [2] get work and start working
    1414095768.60465 [0] want get work
    1414095768.60465 [1] START. URL http://home.yandex.ru/?from=prov_main
    1414095768.60465 [2] work completed (done); start do_something_with_work_result()
    1414095768.60465 [0] get work and start working
    1414095768.60562 [2] do_something_with_work_result completed
    1414095768.60660 [0] START. URL https://disk.yandex.ru/?auth&source=main-nonlogin
    1414095768.60660 [2] want get work
    1414095768.60660 [2] get work and start working
    1414095768.60856 [2] START. URL http://tune.yandex.ru
    1414095768.82265 [2] STOP. WORKING 214ms [REQUEST: 168ms SAVE: 17ms PARSE: 29ms] WITH URL http://tune.yandex.ru
    1414095768.82460 [2] work completed (done); start do_something_with_work_result()
    1414095768.82460 [2] do_something_with_work_result completed
    1414095768.82460 [2] want get work
    1414095768.82460 [2] get work and start working
    1414095768.82460 [2] START. URL http://www.yandex.ru/themes
    1414095769.04651 [1] STOP. WORKING 442ms [REQUEST: 435ms SAVE: 4ms PARSE: 3ms] WITH URL http://home.yandex.ru/?from=prov_main
    1414095769.04847 [1] work completed (done); start do_something_with_work_result()
    1414095769.04945 [1] do_something_with_work_result completed
    1414095769.04945 [1] want get work
    1414095769.04945 [1] get work and start working
    1414095769.04945 [1] START. URL http://www.yandex.ru/?edit=1
    1414095769.20586 [2] STOP. WORKING 381ms [REQUEST: 247ms SAVE: 64ms PARSE: 70ms] WITH URL http://www.yandex.ru/themes
    1414095769.20586 [2] work completed (done); start do_something_with_work_result()
    1414095769.20684 [2] do_something_with_work_result completed
    1414095769.20684 [2] want get work
    1414095769.20684 [2] get work and start working
    1414095769.20684 [2] START. URL http://widgets.yandex.ru
    1414095769.29970 [0] STOP. WORKING 693ms [REQUEST: 660ms SAVE: 12ms PARSE: 22ms] WITH URL https://disk.yandex.ru/?auth&source=main-nonlogin
    1414095769.30068 [0] work completed (done); start do_something_with_work_result()
    1414095769.30068 [0] do_something_with_work_result completed
    1414095769.30068 [0] want get work
    1414095769.30068 [0] get work and start working
    1414095769.30068 [0] START. URL http://tune.yandex.ru/region/?retpath=http%3A%2F%2Fwww.yandex.ru%2F%3Fdomredir%3D1
    1414095769.45416 [1] STOP. WORKING 405ms [REQUEST: 282ms SAVE: 83ms PARSE: 40ms] WITH URL http://www.yandex.ru/?edit=1
    1414095769.45416 [1] work completed (done); start do_something_with_work_result()
    1414095769.45416 [1] do_something_with_work_result completed
    1414095769.45416 [1] want get work
    1414095769.45416 [1] get work and start working
    1414095769.45514 [1] START. URL http://tune.yandex.ru/?retpath=http%3A%2F%2Fwww.yandex.ru%2F%3Fdomredir%3D1
    1414095769.51966 [0] STOP. WORKING 219ms [REQUEST: 188ms SAVE: 13ms PARSE: 19ms] WITH URL http://tune.yandex.ru/region/?retpath=http%3A%2F%2Fwww.yandex.ru%2F%3Fdomredir%3D1
    1414095769.51966 [0] work completed (done); start do_something_with_work_result()
    1414095769.51966 [0] do_something_with_work_result completed
    1414095769.51966 [0] want get work
    1414095769.51966 [0] max pop queue
    1414095769.51966 [0] stop
    1414095769.56560 [2] STOP. WORKING 359ms [REQUEST: 317ms SAVE: 16ms PARSE: 26ms] WITH URL http://widgets.yandex.ru
    1414095769.56854 [2] work completed (done); start do_something_with_work_result()
    1414095769.56854 [2] do_something_with_work_result completed
    1414095769.56854 [2] want get work
    1414095769.56854 [2] max pop queue
    1414095769.56854 [2] stop
    1414095769.64870 [1] STOP. WORKING 194ms [REQUEST: 169ms SAVE: 13ms PARSE: 12ms] WITH URL http://tune.yandex.ru/?retpath=http%3A%2F%2Fwww.yandex.ru%2F%3Fdomredir%3D1
    1414095769.64870 [1] work completed (done); start do_something_with_work_result()
    1414095769.64870 [1] do_something_with_work_result completed
    1414095769.64870 [1] want get work
    1414095769.64870 [1] max pop queue
    1414095769.64870 [1] stop
    WORK FINISHED!
    TasksQueue: size(0) 0/0
    <Downloader(worker-0, stopped daemon 9832)>
    <Downloader(worker-1, stopped daemon 10788)>
    <Downloader(worker-2, stopped daemon 9192)>
    [0] downloads: 3 pop:0.00000 put:0.00000 work:1.28649 = 1.28747
    [1] downloads: 3 pop:0.37246 put:0.00098 work:1.04307 = 1.41651
    [2] downloads: 4 pop:0.36953 put:0.00195 work:0.96096 = 1.33635

Видим, что скорость может быть улучше за счет обработки полученных данных в отдельном потоке.

# Обновление #

Парсинг и сохранение в потоке воркера.

    > python crawler1.py http://yandex.ru/ 2 100 down --debug --thread 10
    
    [0] downloads: 8 pop:0.22680 put:0.04888 work:4.97196 = 5.36103
    [1] downloads: 17 pop:0.72341 put:0.14957 work:6.22520 = 7.22625
    [2] downloads: 11 pop:0.51225 put:0.05670 work:5.68754 = 6.39140
    [3] downloads: 10 pop:0.39592 put:0.20920 work:5.74522 = 6.38455
    [4] downloads: 10 pop:0.48293 put:0.05866 work:4.69627 = 5.36592
    [5] downloads: 6 pop:0.52203 put:0.18867 work:4.75004 = 5.61324
    [6] downloads: 6 pop:0.47021 put:0.23657 work:5.76966 = 6.54585
    [7] downloads: 14 pop:0.51323 put:0.23462 work:4.42744 = 5.35516
    [8] downloads: 11 pop:0.60317 put:0.06452 work:4.57897 = 5.35419
    [9] downloads: 7 pop:0.38126 put:0.03617 work:4.80283 = 5.35517

Парсинг и сохранение в отдельном потоке.

    > python crawler2.py http://yandex.ru/ 2 100 down --debug --thread 10
    
    [0] downloads: 6 pop:0.11829 put:0.00293 work:3.82676 = 3.95286
    [1] downloads: 6 pop:0.84658 put:0.00000 work:2.85602 = 3.70652
    [2] downloads: 9 pop:0.84658 put:0.00880 work:4.07408 = 4.93435
    [3] downloads: 4 pop:0.83046 put:0.00148 work:3.49729 = 4.33119
    [4] downloads: 9 pop:0.83681 put:0.00880 work:3.39271 = 4.24321
    [5] downloads: 11 pop:0.82996 put:0.00293 work:3.02710 = 3.86586
    [6] downloads: 31 pop:0.83249 put:0.01473 work:4.15451 = 5.02136
    [7] downloads: 12 pop:0.82321 put:0.01132 work:2.95889 = 3.80427
    [8] downloads: 6 pop:0.81432 put:0.00587 work:3.42302 = 4.25200
    [9] downloads: 6 pop:0.81334 put:0.00391 work:3.48754 = 4.30870

Видим, что время работы уменьшелось.
