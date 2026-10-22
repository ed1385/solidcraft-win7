import json,re,sys
R='/home/claude/src/solidcraft-0.18.2/assets/locales/'
en=json.load(open(R+'en.json')); ru=json.load(open('/home/claude/l10n/ru_orig.json'))
def sub_case(pat, rep, s):
    def f(m):
        r=rep(m) if callable(rep) else m.expand(rep)
        return r
    return re.sub(pat,f,s)
END={'':'', 'а':'а','у':'у','ом':'ом','е':'е','ы':'ы','ов':'ов','ам':'ам','ами':'ами','ах':'ах'}
for k,v in list(ru.items()):
    e=en.get(k,'')
    # design -> проект
    v=re.sub(r'(Д|д)изайн(ами|ам|ах|ов|ом|а|у|е|ы)?\b', lambda m:('Д' if m.group(1)=='Д' else 'д')+'окумент'+(m.group(2) or ''), v)
    # joint -> соединение (only where English talks about joints)
    if re.search(r'joint',e,re.I):
        v=v.replace('сопряжени','соединени').replace('Сопряжени','Соединени').replace('СОПРЯЖЕНИ','СОЕДИНЕНИ')
    v=v.replace('«Взгляд на»','«Вид по нормали»').replace('«Главная»','«Исходный вид»').replace('«Вписать»','«Показать всё»')
    v=re.sub(r'(И|и)нтерференци(я|и|ю|ей)', lambda m:('К' if m.group(1)=='И' else 'к')+'оллизи'+{'я':'и','и':'й','ю':'и','ей':'ями'}[m.group(2)], v)
    v=re.sub(r'\bмеша\b','сетки',v); v=re.sub(r'\bмеш\b','сетку',v)
    v=v.replace('рендеринга','визуализации').replace('Рендеринг','Визуализация').replace('рендеринг','визуализацию')
    v=v.replace('скриншот','снимок экрана')
    ru[k]=v
O={
# --- ribbon / views / core terms
'ui.extrude':'Выдавливание','ui.revolve':'Вращение','ui.sweep':'По траектории','ui.loft':'По сечениям',
'ui.home':'Исходный вид','ui.fit':'Показать всё','ui.look_at':'Вид по нормали','ui.orbit':'Поворот','ui.pan':'Сдвиг','ui.zoom':'Масштаб',
'ui.browser_title':'Дерево модели','ui.joints':'Соединения','cmd.joint_create':'Соединение','ui.render':'Визуализация','ui.renderer':'Визуализатор',
'ui.pan_zoom_orbit':'Сдвиг, масштаб, поворот','render.fit':'Показать модель',
'ui.rectangular_pattern':'Массив по сетке','cmd.config_table':'Таблица конфигураций',
'cmd.mesh_convert':'Сетка в тело','cmd.component_from_bodies':'Компоненты из тел','cmd.component_capture_position':'Фиксировать положение',
'cmd.contact_enable_sets':'Включить контакты','cmd.component_properties':'МЦХ компонента','cmd.inspect_interference':'Коллизии',
'cmd.inspect_curvature_comb':'Гребёнка кривизны','cmd.sheet_manage_rules':'Правила листа','cmd.plastic_manage_rules':'Правила пластика',
'cmd.plastic_assign_rule':'Назначить правило','cmd.document_units':'Единицы документа','cmd.view_apply':'Восстановить вид','cmd.view_save':'Сохранить вид',
'cmd.sketch_rectangle_two_point':'Прямоугольник','cmd.sketch_circle_center':'Окружность','cmd.sheet_export_dxf':'Развёртка в DXF',
'cmd.sheet_export_bend_table':'Таблица гибов','cmd.render_scene':'Сцена визуализации','cmd.surface_loft':'Пов-ть по сечениям','cmd.surface_sweep':'Пов-ть по траектории',
'cmd.surface_extrude':'Выдавливание пов-ти','cmd.surface_revolve':'Вращение пов-ти',
'cmd.file_insert_mesh':'Вставить сетку','cmd.file_save_mesh':'Сохранить как сетку','cmd.sketch_fit_curves_to_section':'Кривые по сечению сетки',
'cmd.render_backends':'Модули визуализации','cmd.render_cancel':'Прервать визуализацию','cmd.render_export':'Экспорт изображения','cmd.render_preflight':'Проверка визуализации',
'cmd.render_settings_apply':'Применить камеру визуализации','cmd.render_settings_get':'Параметры визуализации','cmd.render_settings_set':'Сохранить параметры визуализации',
'cmd.render_start':'Визуализировать','cmd.render_status':'Ход визуализации','render.image_cancelled':'Визуализация прервана','render.image_failed':'Ошибка визуализации',
'render.image_queued':'Ожидание визуализации','render.image_running':'Визуализация…','render.image_start':'Начать визуализацию','render.image_title':'Визуализация',
'render.image_unknown':'Состояние визуализации неизвестно','ui.workspace_render_description':'Предпросмотр изделия, параметры сцены, готовые изображения',
'no interference':'коллизий нет','needs two joints':'нужны два соединения',
# --- ribbon captions
'ui.heading_construct':'Построения','REFERENCE':'Справочные','toolbar.image':'Снимок','ui.heading_finish_sketch':'Завершить эскиз',
# --- dialog row labels (≤125 px)
'Add Mid Radius':'Добавить ср. радиус','Add or edit rule':'Добавить/изменить правило','All open designs':'Все открытые документы','Apply to selection':'Применить к выбранному',
'Bend Line Position':'Положение линии сгиба','Catch Direction':'Направл. защёлки','Check collisions':'Проверять коллизии','Close draft':'Закрыть анализ уклона',
'Configuration rules':'Правила конфигураций','Copy all licences':'Копировать лицензии','Copy screenshot':'Копировать снимок','Customize Toolbar':'Настроить ленту',
'Edit Profile Sketch':'Изменить эскиз профиля','End continuity':'Гладкость в конце','Start continuity':'Гладкость в начале','Export Animation…':'Экспорт анимации…',
'Extend to meet':'Продлить до пересеч.','In place (surfaces)':'На месте (пов-ти)','Keep (points on it)':'Оставить (с точками)','Keep Tools':'Оставить инструм. тела',
'Remove Tools':'Удалить инструм. тела','Letter Spacing':'Межбукв. интервал','Line Spacing':'Межстроч. интервал','Local library':'Локальная библ.','Move / Copy':'Перемест./копир.',
'Open GitHub draft':'Черновик на GitHub','Plastic Rules':'Правила пластика','Position (0 to 1)':'Положение (0…1)','Preview Row':'Строка предпросм.','Remove override':'Снять переопредел.',
'Reset Toolbar':'Сбросить ленту','Resize Part':'Изменить типоразмер','Retake screenshot':'Переснять снимок','Reverse Direction':'Обратное направл.','Scale factor':'Коэфф. масштаба',
'Search this library':'Поиск в библиотеке','Sheet Rules':'Правила листа','Show Agent Cursor':'Курсор агента','Stand it up':'Поставить вертикально','Stand this part up?':'Поставить деталь вертикально?',
'Tangent Chain':'Цепочка касательных','Thin Extrude':'Тонкостенное выдавл.','Use fixed plane':'Фикс. плоскость','User Parameters':'Параметры польз.','Wall Location':'Положение стенки',
'Will fail':'Будет ошибка','appearance.dielectric_ior':'Коэфф. преломления','appearance.surface_response':'Отклик поверхности','cam.roller_pick':'Ролик (необяз.)',
'cam.tip_pick':'Острие (необяз.)','color.edit':'Изменить цвет','coupling.gear_1_pick':'Колесо 1 (необяз.)','coupling.gear_2_pick':'Колесо 2 (необяз.)','coupling.internal':'Внутр. зацепление',
'coupling.pinion_pick':'Шестерня (необяз.)','crash.copy_folder':'Копировать путь','file_load.recovering':'Восстановление…','motion.delete_key':'Удалить ключ. кадр',
'motion.key_here':'Ключ. кадр здесь','pattern.flip_direction':'Обратить направл.','render.image_preparing':'Подготовка…','render.preview':'Встр. предпросмотр',
'render.return_design':'К проектированию','render.setup_name':'Имя настройки','sample.vents.name':'Вентиляц. пластина','Applied Radius':'Факт. радиус','BLEND SURFACE':'СОПРЯГАЮЩАЯ ПОВ-ТЬ',
'RULED SURFACE':'ЛИНЕЙЧАТАЯ ПОВ-ТЬ','Don\u0027t ask again':'Не спрашивать',
}
ru.update(O)
O2={'ui.angle_decimals':'Знаков (углы)','ui.length_decimals':'Знаков (длины)','ui.bodies_all_if_none':'Тела (пусто — все)','ui.hole_tap_type':'Тип резьбы',
'ui.pull_direction':'Направл. извлечения','ui.rail_fit':'Подгонка по направл.','ui.second_rail':'2-я направляющая','ui.tool_direction':'Направл. инструмента',
'ui.display_quality':'Качество отображ.','ui.graphics_preset':'Профиль графики','ui.ui_scale':'Масштаб интерф.','ui.autosave_every':'Автосохр. каждые',
'thread.automatic_size':'Авто размер','ui.equivalent_radius':'Эквив. радиус','ui.material_review.shear_strength':'Предел прочн. (сдвиг)',
'ui.material_review.specific_heat':'Уд. теплоёмкость','ui.material_review.tensile_strength':'Предел прочн. (растяж.)','ui.material_review.thermal_expansion':'КТЛР',
'ui.agent_chat_side':'Сторона чата','ui.sweep_follow_direction':'По направлению','ui.sweep_turn_with_path':'Поворот по траект.','Tangent Chain':'Цепочка касат.',
'Bend Line Position':'Положение линии сгиба','Extend to meet':'Продлить до пересеч.','Thin Extrude':'Тонкостенная','Keep Tools':'Сохр. инструм. тела','Remove Tools':'Удал. инструм. тела',
'appearance.dielectric_ior':'Коэфф. преломл.','ui.fully_constrained':'Полностью опред.','ui.heading_save_mesh':'СОХРАНИТЬ КАК СЕТКУ','ui.mesh_format_3mf_tagged':'3MF с метками граней',
'ui.ambient_occlusion':'Затенение (AO)','ui.visual_shaded_with_edges':'Тонир. с рёбрами','ui.feature_options':'Параметры операции','ui.active_component':'Активный компонент',
'ui.horizontal_vertical':'Гориз./верт.','ui.perpendicular':'Перпендикулярность','ui.fix_unfix':'Фиксировать/освободить','ui.hideOrigin':'Скрыть начало коорд.',
'ui.showOrigin':'Показать начало коорд.','ui.pinToShortcuts':'В быстрые команды','cmd.sketch_rectangle_two_point':'Прямоуг. по 2 точкам','ui.heading_construct':'Вспомог.',
'ui.editJointLimits':'Пределы соединения','cmd.joint_limits':'Пределы соединения','ui.unsuppress':'Включить операцию','Stand it up':'Поставить верт.',
}
ru.update(O2)
BYEN={'Box':'Параллелепипед','Press Pull':'Тянуть/толкать','Hem':'Подгибка','Thicken':'Придать толщину','Patch':'Заплата','Ground':'Закрепить'}
for k in en:
    if en[k] in BYEN: ru[k]=BYEN[en[k]]
# missing help entries
ru.update({
'help.solid.chamfer':'Срезает выбранные рёбра плоской фаской заданного размера. Применяется для притупления острых кромок и для заходных фасок под штифт или винт.',
'help.solid.extrude':'Выдавливает профиль эскиза на заданное расстояние, добавляя или удаляя материал. Превращает плоский контур в блок, бобышку или карман.',
'help.solid.fillet':'Скругляет выбранные рёбра дугой заданного радиуса. Применяется, чтобы убрать острые кромки — для прочности, удобства или внешнего вида.',
'help.solid.hole':'Сверлит круглое отверстие заданного диаметра в выбранной точке грани. Применяется для отверстий под крепёж, штифты и других простых круглых проёмов.',
'help.solid.revolve':'Вращает профиль эскиза вокруг оси, создавая тело вращения. Применяется для валов, ручек, чаш и любых деталей, симметричных относительно оси.',
'help.solid.shell':'Делает тело полым с заданной толщиной стенки; выбранные грани можно вскрыть. Применяется для корпусов, крышек и других тонкостенных деталей.',
})
assert set(ru)>=set(en), set(en)-set(ru)
json.dump({k:ru[k] for k in en}|{k:v for k,v in ru.items() if k not in en},open(sys.argv[1],'w'),ensure_ascii=False,indent=2)
print('ok',len(ru))
