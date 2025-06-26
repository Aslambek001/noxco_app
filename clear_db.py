# clear_db.py
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # Отключаем внешние ключи (только для PostgreSQL!)
    db.session.execute('TRUNCATE TABLE {} RESTART IDENTITY CASCADE;'.format(
        ', '.join(table.name for table in db.metadata.sorted_tables)
    ))
    db.session.commit()
    print("✅ Все данные из базы данных удалены.")
