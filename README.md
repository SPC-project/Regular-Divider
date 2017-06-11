Regular-Divider
===============
##### (проект разрабатывается студентами кафедры [КМПС](http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/) [НТУ "ХПИ"](http://www.kpi.kharkov.ua/ru/))

Для запуска необходимы (в скобках - версии ПО, которые используются при отладке):
- Интерпретатор для Python 3 (3.5)
- Qt 5 (5.6)
- PyQt 5 (5.6)

Все ошибки записываются в файл errors.log (последние внизу; в начале записи - дата и время).

Будьте бдительны при модификации логики ввода\отображения треугольников: в интерфейсе используется интуитивное для человека представление в узлах, внутри самой программы - прямоугольниках, что разбиваются диагональю на два элемента. Во втором случае число на единицу меньше (N узлов образуют N-1 отрезок).

Если вы используете среду рабочего стола KDE, то у вас возможен баг, когда кнопкам автоматически выставляется shortcut вида alt+<первая буква надписи> - что выражается в подчеркивании соответствующей буквы. Чтобы исправить это, добавить в конец файла ~/.config/kdeglobals следующие строчки:
```
[Development]
AutoCheckAccelerators=false
```

Структура выходного файла
----------
**n_nodes** - количество узлов в фигуре. Координаты узлов перечислены в секции *[koor]* (индексация начинается с 1)

**n_elements** - количество элементов (треугольников) в фигуре. Задаются перечислением индексов узлов-вершин в секции *[inds]* (число указывает на соответствующую строку в секции *[koor]*)

	[settings]
	n_nodes=M
	n_elements=N
	n_forces=K
	n_contacts=L
	[inds]
	<индекс1 индекс2 индекс3 — всего N строк>
	[coor]
	<x-координата у-координата — всего M строк>
	[contact]
	<всего L строк>
	[force]
	<всего K строк>
	[material]
	<0 (для воздуха) или 1 (для фигуры) — всего M строк>
	[element's material]
	<0 (для воздуха) или 1 (для фигуры) — всего N строк>

[.pmd](https://github.com/SPC-project/Transformer/blob/master/README.md#Структура-входного-файла) используются для сообщения с программой Transformer


Экспорт фигур
----------
Вы можете сохранить созданные фигуры в файл формата .d42do чтобы в дальнейшем продолжить над ними работу. Формат имеет следующую структуру:
```
type: "<type>" | [<Вспомогательные данные>: <data>] | x y width height | NAT NAR NAB NAL NFX NFY
```
NA* - количество воздушных узлов, соответственно, сверху/справа/снизу/слева; NF* - количество узлов для фигуры, по x/y
