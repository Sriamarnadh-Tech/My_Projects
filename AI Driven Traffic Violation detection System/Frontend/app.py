from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import io

APP_SECRET = "change-me-for-prod"
DB_PATH = 'sqlite:///traffic.db'

app = Flask(__name__)
app.secret_key = APP_SECRET

engine = create_engine(DB_PATH, echo=False, future=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Database Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(120))
    phone = Column(String(30))
    vehicle_type = Column(String(20))
    vehicle_number = Column(String(40))
    challans = relationship('Challan', back_populates='user')


class Challan(Base):
    __tablename__ = 'challans'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer)
    violation = Column(String(200))
    date = Column(String(50))
    location = Column(String(200))
    evidence_image = Column(Text)  # URL or path
    plate_image = Column(Text)
    status = Column(String(30), default='unpaid')
    user = relationship('User', back_populates='challans')

#Database Utility Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    db = next(get_db())
    return db.query(User).filter(User.id == uid).first()

#routes
@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        name = request.form.get('name')
        phone = request.form.get('phone')
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')

        db = next(get_db())
        if db.query(User).filter(User.username == username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        u = User(username=username,
                 password_hash=generate_password_hash(password),
                 name=name, phone=phone,
                 vehicle_type=vehicle_type,
                 vehicle_number=vehicle_number)
        db.add(u)
        db.commit()
        flash('Registration successful, please login')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = next(get_db())
        # Allow login by username OR phone number (users may enter phone in the username field)
        user = db.query(User).filter((User.username == username) | (User.phone == username)).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    try:
        user = current_user()
        if not user:
            return redirect(url_for('login'))
        db = next(get_db())
        challans = db.query(Challan).filter(Challan.user_id == user.id).all()

        # compute totals
        total_challans = len(challans)
        pending_amount = sum((c.amount or 0) for c in challans if (not c.status or c.status.lower() != 'paid'))
        paid_amount = sum((c.amount or 0) for c in challans if (c.status and c.status.lower() == 'paid'))

        return render_template('dashboard.html', user=user, challans=challans,
                               total_challans=total_challans,
                               pending_amount=pending_amount,
                               paid_amount=paid_amount)
    except Exception as exc:
        # log traceback to file for debugging and print to console
        import traceback
        tb = traceback.format_exc()
        print(tb)
        try:
            with open('error.log', 'a', encoding='utf-8') as f:
                f.write('\n--- Dashboard exception ---\n')
                f.write(tb)
        except Exception:
            pass
        flash('An internal error occurred while loading the dashboard. The error has been logged.')
        return redirect(url_for('index'))


@app.route('/challan/<int:cid>')
def view_challan(cid):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    db = next(get_db())
    ch = db.query(Challan).filter(Challan.id == cid, Challan.user_id == user.id).first()
    if not ch:
        flash('Challan not found')
        return redirect(url_for('dashboard'))
    return render_template('challan.html', challan=ch)


@app.route('/evidence/<int:cid>')
def evidence(cid):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    db = next(get_db())
    ch = db.query(Challan).filter(Challan.id == cid, Challan.user_id == user.id).first()
    if not ch:
        flash('Challan not found')
        return redirect(url_for('dashboard'))
    return render_template('evidence.html', challan=ch)


@app.route('/account')
def account():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    # Render account page with user details
    return render_template('account.html', user=user)


@app.route('/download/<int:cid>')
def download_challan(cid):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    db = next(get_db())
    ch = db.query(Challan).filter(Challan.id == cid, Challan.user_id == user.id).first()
    if not ch:
        flash('Challan not found')
        return redirect(url_for('dashboard'))

    content = f"""
    Challan ID: {ch.id}
    Name: {ch.user.name}
    Vehicle: {ch.user.vehicle_number} ({ch.user.vehicle_type})
    Violation: {ch.violation}
    Date: {ch.date}
    Amount: {ch.amount}
    Status: {ch.status}
    """
    buf = io.BytesIO()
    buf.write(content.encode('utf-8'))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"challan_{ch.id}.txt", mimetype='text/plain')


if __name__ == '__main__':
    print('Starting app on http://127.0.0.1:5000')
    app.run(debug=True)
