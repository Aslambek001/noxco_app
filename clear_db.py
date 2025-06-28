from dotenv import load_dotenv
from app import create_app
from app.extensions import db
load_dotenv()
app = create_app()

with app.app_context():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f'Leegmaken: {table}')
        db.session.execute(table.delete())
    db.session.commit()
    print('Database succesvol geleegd!')
