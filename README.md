# ArtMuseum — онлайн-галерея произведений искусств

Учебный проект на Django. Каталог из 12 картин с поиском, страницами просмотра,
тёмной темой и сохранением пользовательских настроек в cookies.

## Функционал
- Каталог картин на главной странице
- Поиск по названию и автору
- Страница с подробной информацией о картине
- Тёмная/светлая тема (сохраняется в cookies)
- Последний поисковый запрос (сохраняется в cookies)
- Блок «Вы недавно смотрели» (сохраняется в cookies)

## Установка

```bash
git clone <ссылка на репозиторий>
cd artgallery_project
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
