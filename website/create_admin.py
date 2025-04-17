from  .import db, create_app
from models import Customer
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_email = 'admin@example.com'
    admin_username = 'admin'
    admin_password = 'jojoy'

    hashed_password = generate_password_hash(admin_password, method='sha256')

    new_admin = Customer(
        email='rubelgado@gmail.com',
        username='admin',
        password_hash=hashed_password,
        is_admin=True
    )

    db.session.add(new_admin)
    db.session.commit()
