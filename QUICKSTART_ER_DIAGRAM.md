# 🚀 Быстрый старт с ER-диаграммой

## 📁 Файлы диаграмм в проекте

```
Let-s-meet-up/
├── database_schema.sql           ← SQL скрипт для создания БД
├── database_diagram.xml          ← XML для онлайн редакторов
├── ER_DIAGRAM.md                 ← Mermaid диаграмма + документация
├── ER_DIAGRAM_VISUAL.md          ← ASCII визуализация
└── DB_DESIGNER_GUIDE.md          ← Полная инструкция
```

## ⚡ Самый быстрый способ (2 минуты)

### Вариант 1: Mermaid Live (Онлайн, без регистрации)

1. Откройте: https://mermaid.live/
2. Скопируйте код из `ER_DIAGRAM.md` (блок между ```mermaid```)
3. Вставьте в редактор
4. **Actions → Export PNG/SVG**

### Вариант 2: DBDesigner.net (Онлайн, без регистрации)

1. Откройте: https://www.dbdesigner.net/
2. **Import → From SQL**
3. Вставьте содержимое `database_schema.sql`
4. **Import** → готово!

## 🎨 Лучшие онлайн редакторы

| Редактор | URL | Регистрация | Плюсы |
|----------|-----|-------------|-------|
| **Mermaid Live** | mermaid.live | ❌ Нет | Мгновенный результат |
| **DBDesigner.net** | dbdesigner.net | ❌ Нет | Импорт SQL |
| **DrawSQL** | drawsql.app | ✅ Да | Красивый UI |
| **WWW SQL Designer** | sql.toad.cz | ❌ Нет | Импорт XML |
| **Lucidchart** | lucidchart.com | ✅ Да | Профессиональный |

## 💻 Локальные инструменты

### DBeaver (Рекомендуется)
```bash
# 1. Установить DBeaver: https://dbeaver.io/
# 2. Подключиться к PostgreSQL
# 3. Правый клик на базе → View Diagram
```

### pgAdmin
```bash
# 1. Открыть pgAdmin
# 2. Подключиться к базе
# 3. Tools → ERD Tool → Выбрать таблицы
```

## 📝 Просмотр в VS Code

1. Установите расширение: **Markdown Preview Mermaid Support**
2. Откройте `ER_DIAGRAM.md`
3. Нажмите **Ctrl+Shift+V** (Preview)
4. Диаграмма отобразится визуально

## 🔧 Создание диаграммы из БД

Если база уже существует:

```bash
# PostgreSQL
pg_dump -U postgres -d meetup_db --schema-only > exported_schema.sql

# Затем импортируйте в любой редактор
```

## 📊 Структура базы (кратко)

```
users (пользователи)
  ↓
  └─► organizes (организует) ─► events (мероприятия)
                                   ↓
users ◄─ participates ─── events_participants
         (участвует)              (связь N:M)
```

**3 таблицы, 3 связи, 11 индексов**

## 🎯 Что можно делать

- ✅ Просматривать структуру БД
- ✅ Редактировать таблицы и поля
- ✅ Экспортировать в PNG/SVG/PDF
- ✅ Генерировать SQL-скрипты
- ✅ Делиться с командой
- ✅ Распечатывать для презентаций

## 📚 Полная документация

Для подробных инструкций см. **`DB_DESIGNER_GUIDE.md`**

---

**Выберите удобный вариант и начните работу! 🚀**
