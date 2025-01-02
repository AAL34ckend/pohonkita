from datetime import datetime
import os
import uuid
from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
from numpy import ceil
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from models import db, User, Tree, Status, ActivityLog, get_leaderboard, get_dashboard_summary, Submission, get_user_activity_logs, get_admin_activity_logs

# Initialize Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/pohonkita'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# HOMEPAGE AND LOGIN
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400

        new_user = User(
            name=name, 
            email=email, 
            password=hashed_password,
            role='user',
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            return redirect(url_for('dashboard' if user.role == 'user' else 'adminHome'))

        return jsonify({'message': 'Invalid email or password'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

# USER DASHBOARD
from flask import render_template, request, session, redirect, url_for
from datetime import datetime
from math import ceil
from models import db, Submission, Tree

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))

    # Ambil filter dari query string
    selected_jenis = request.args.get('jenis', 'Semua Jenis')

    # Query untuk katalog pohon dengan filter jenis
    tree_query = Tree.query
    if selected_jenis != 'Semua Jenis':
        tree_query = tree_query.filter(Tree.jenis == selected_jenis)
    
    # Pagination
    per_page = 3
    page = request.args.get('page', 1, type=int)
    tree_catalog = tree_query.paginate(page=page, per_page=per_page)

    # Total pohon dan target
    total_trees = db.session.query(db.func.sum(Submission.required_seeds)).filter(Submission.status == 'approved').scalar() or 0
    target_trees = 100000

    # Pohon bulan ini
    this_month = datetime.now().month
    this_year = datetime.now().year
    trees_this_month = db.session.query(db.func.sum(Submission.required_seeds)).filter(
        db.extract('month', Submission.created_at) == this_month,
        db.extract('year', Submission.created_at) == this_year,
        Submission.status == 'approved'
    ).scalar() or 0

    # Ambil daftar jenis pohon untuk filter dropdown
    jenis_options = db.session.query(Tree.jenis).distinct().all()

    return render_template(
        'dashboardpage.html',
        page=page,
        total_pages=tree_catalog.pages,
        tree_catalog=tree_catalog.items,
        total_trees=total_trees,
        target_trees=target_trees,
        trees_this_month=trees_this_month,
        selected_jenis=selected_jenis,
        jenis_options=[j[0] for j in jenis_options]  # Flatten hasil query
    )



@app.route('/dashboard/plant', methods=['GET'])
def plant():
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))

    trees = Tree.query.all()
    return render_template('plant.html', trees=trees)

@app.route('/dashboard/plant/details/<int:tree_id>', methods=['GET'])
def plantDetails(tree_id):
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))  # Arahkan ke login jika tidak terautentikasi
    # Ambil data pohon berdasarkan tree_id
    tree = Tree.query.get(tree_id)  # Pastikan tree_id valid di database
    print(tree)
    if tree is None:
        return redirect(url_for('plant'))  # Redirect ke halaman tanaman jika pohon tidak ditemukan
    return render_template('plant-details.html', tree=tree)

@app.route('/dashboard/plant/details/<int:tree_id>/form', methods=['GET', 'POST'])
def formPlant(tree_id):
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))
    
    tree = Tree.query.get(tree_id)  # Ambil pohon berdasarkan ID yang diberikan
    if tree is None:
        return redirect(url_for('plant'))  # Redirect jika pohon tidak ditemukan

    if request.method == 'POST':
        # Ambil data dari form
        full_name = request.form.get('full_name')
        city = request.form.get('city')
        planned_planting_date = request.form.get('planned_planting_date')
        required_seeds = request.form.get('required_seeds')  # Gunakan get() agar tidak error jika tidak ada
        notes = request.form.get('notes')
        supporting_image = request.files.get('supporting_image')  # Foto bukti pendukung
        
        # Tentukan folder tempat menyimpan gambar
        upload_folder = os.path.join('static', 'uploads')

        # Cek jika folder tidak ada, buat folder baru
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Gunakan secure_filename untuk memastikan nama file aman
        if supporting_image:
            supporting_image_filename = secure_filename(supporting_image.filename)
            # Simpan file di folder uploads
            supporting_image.save(os.path.join(upload_folder, supporting_image_filename))


        # Simpan data pengajuan ke database
        new_submission = Submission(
            user_id=session['user_id'],
            tree_id=tree_id,
            full_name=full_name,
            city=city,
            planned_planting_date=planned_planting_date,
            required_seeds=required_seeds,
            supporting_image=supporting_image_filename,
            notes=notes,
            status='pending'  # Status default pengajuan adalah pending
        )
        
        db.session.add(new_submission)
        db.session.commit()

        return redirect(url_for('plant'))  # Redirect setelah pengajuan disubmit

    return render_template('form-plant.html', tree=tree)

@app.route('/dashboard/mysubmission',methods=['GET'])
def mySubmission():
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))
    user_id = session['user_id']
    submissions = Submission.query.filter_by(user_id=user_id).all()
    for submission in submissions:
        print('submission result :',submission.supporting_image)
    return render_template(
        'mysubmission.html',
        submissions=submissions)


@app.route('/dashboard/leaderboard', methods=['GET'])
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Ambil data leaderboard dari database atau sumber lainnya
    leaderboard_data = get_leaderboard(user_id)
    print('leaderboard data : ', leaderboard_data)
    # Ambil data pengguna teratas dari leaderboard_data
    top_users = leaderboard_data.get('top_users', [])
    # Ambil data peringkat pengguna saat ini dari leaderboard_data
    user_rank_data = leaderboard_data.get('user_rank', {
        'rank': len(top_users) + 1,
        'name': 'Anda',
        'total_trees': 0
    })
    # Menyusun daftar leaderboard
    leaderboard = [
        {
            'rank': idx + 1,
            'name': user['name'],
            'trees_planted': user['total_trees']
        }
        for idx, user in enumerate(top_users)
    ]

    # Data pengguna saat ini yang akan ditampilkan di atas leaderboard
    current_user = {
        'rank': user_rank_data['rank'],
        'name': user_rank_data['name'],
        'trees_planted': user_rank_data['total_trees']
    }

    # Render template leaderboard
    return render_template(
        'leaderboard.html',
        leaderboard=leaderboard,
        current_user=current_user
    )

def get_leaderboard(user_id):
    # Ambil data leaderboard berdasarkan jumlah pohon yang di-approve
    top_users = db.session.query(
        User.name, 
        db.func.count(Submission.id).label('approved_trees')
    ) \
    .join(Submission, User.id == Submission.user_id) \
    .filter(Submission.status == 'approved') \
    .group_by(User.id) \
    .having(db.func.count(Submission.id) > 0) \
    .order_by(db.func.count(Submission.id).desc()) \
    .limit(10).all()

    # Ambil data pengguna saat ini berdasarkan user_id
    current_user = db.session.query(
        User.name, 
        db.func.count(Submission.id).label('approved_trees')
    ) \
    .join(Submission, User.id == Submission.user_id) \
    .filter(Submission.status == 'approved') \
    .filter(User.id == user_id) \
    .first()

    user_rank = {}
    if current_user:
        # Hitung peringkat pengguna saat ini berdasarkan jumlah pohon yang di-approve
        rank = db.session.query(User) \
                         .join(Submission, User.id == Submission.user_id) \
                         .filter(Submission.status == 'approved') \
                         .group_by(User.id) \
                         .having(db.func.count(Submission.id) > current_user.approved_trees) \
                         .count() + 1
        user_rank = {
            'rank': rank,
            'name': current_user.name,
            'total_trees': current_user.approved_trees
        }

    leaderboard_data = {
        'top_users': [{'name': user[0], 'total_trees': user[1]} for user in top_users],
        'user_rank': user_rank
    }

    return leaderboard_data




@app.route('/dashboard/about', methods=['GET'])
def about():
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))

    return render_template('about.html')


@app.route('/dashboard/activity', methods=['GET'])
def user_activity():
    if 'user_id' not in session or session['user_role'] != 'user':
        return redirect(url_for('login'))

    user_id = session['user_id']
    activities = get_user_activity_logs(user_id)
    return render_template('user-activity.html', activities=activities)

# ADMIN DASHBOARD
@app.route('/admin/dashboard', methods=['GET'])
def adminHome():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Total pohon (dari semua submission yang statusnya 'approved')
    total_trees = db.session.query(db.func.sum(Submission.required_seeds)).filter(Submission.status == 'approved').scalar() or 0
    target_trees = 100000

    # Total user (jumlah semua pengguna dengan role 'user')
    total_users = User.query.filter_by(role='user').count()

    # Pending submissions
    pending_count = Submission.query.filter_by(status='pending').count()

    # Top contributors (urutan berdasarkan jumlah pohon yang ditanam)
    top_contributors = (
        db.session.query(User.name, db.func.sum(Submission.required_seeds).label('total_trees'))
        .join(Submission, User.id == Submission.user_id)
        .filter(Submission.status == 'approved')
        .group_by(User.id)
        .order_by(db.desc('total_trees'))
        .limit(3)
        .all()
    )

    return render_template(
        'adminHome.html',
        total_trees=total_trees,
        target_trees=target_trees,
        total_users=total_users,
        pending_count=pending_count,
        top_contributors=top_contributors
    )



@app.route('/admin/userSubmission', methods=['GET', 'POST'])
def userSubmission():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    # Ambil semua pengguna dengan role 'user'
    users = User.query.filter(User.role == 'user').all()
    # Ambil semua submission
    submissions = (
        Submission.query
        .join(User, Submission.user_id == User.id)
        .add_columns(
            Submission.id,
            Submission.full_name,
            Submission.city,
            Submission.planned_planting_date,
            Submission.required_seeds,
            Submission.status,
            Submission.supporting_image
        )
        .all()
    )
    
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        # Menangani update status user
        if action_type == 'users_action':
            user_id = request.form.get('user_id', type=int)
            action = request.form.get('action')
            # Validasi action (contoh: hanya 'active' atau 'inactive' yang valid)
            if action not in ['active', 'deactive']:
                flash('Invalid action.', 'error')
                return redirect(url_for('userSubmission'))
            # Update status pengguna
            user = User.query.get(user_id)
            if user:
                user.status = action
                db.session.commit()
                flash(f"User {user.name}'s status updated to {action}.", 'success')
            else:
                flash('User not found.', 'error')

        # Menangani update status submission
        if action_type == 'submission_action':
            submission_id = request.form.get('submission_id', type=int)
            action = request.form.get('action')

            if action not in ['approved', 'rejected']:
                flash('Invalid action.', 'error')
                return redirect(url_for('userSubmission'))

            # Update submission status
            submission = Submission.query.get(submission_id)
            if submission:
                submission.status = action
                db.session.commit()
                flash(f"Submission status updated to {action}.", 'success')
            else:
                flash('Submission not found.', 'error')

        return redirect(url_for('userSubmission'))

    return render_template(
        'admin-user-manager.html',
        users=users,
        submissions=submissions
    )
    
@app.route('/admin/manage-user', methods=['GET', 'POST'])
def adminManageUser():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    users = User.query.filter(User.role == 'user').all()
    return render_template(
        'admin-manage-user.html',
        users=users,
    )

@app.route('/admin/manage-user/<int:user_id>', methods=['GET', 'POST'])
def deleteUser(user_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        flash('Tree not found!', 'error')
        return redirect(url_for('adminManageUser'))
    db.session.delete(user)
    db.session.commit()
    flash('Tree deleted successfully!', 'success')
    return redirect(url_for('adminManageUser'))

@app.route('/admin/treeManagements', methods=['GET', 'POST'])
def treeManagements():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        jenis = request.form.get('jenis')
        rata_rata_tumbuh = request.form.get('rata_rata_tumbuh')
        waktu_tumbuh = request.form.get('waktu_tumbuh')
        manfaat = request.form.get('manfaat')

        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('static/uploads', filename)
                image_file.save(image_path)
            else:
                image_path = None
        else:
            image_path = None

        # Add tree to database
        new_tree = Tree(
            user_id=session['user_id'], 
            name=name, 
            jenis=jenis, 
            image=image_path, 
            jumlah_bibit=0, 
            rata_rata_tumbuh=rata_rata_tumbuh, 
            waktu_tumbuh=waktu_tumbuh, 
            manfaat=manfaat
        )
        db.session.add(new_tree)
        db.session.commit()
        flash('Tree added successfully!', 'success')
        return redirect(url_for('treeManagements'))

    # Fetch all trees for display
    trees = Tree.query.all()
    return render_template('admin-tree-managements.html', trees=trees)

@app.route('/admin/treeManagements/add', methods=['GET', 'POST'])
def addTree():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    print(request)
    if request.method == 'POST':
        name = request.form.get('name')
        jenis = request.form.get('jenis')
        rata_rata_tumbuh = request.form.get('rata_rata_tumbuh')
        waktu_tumbuh = request.form.get('waktu_tumbuh')
        manfaat = request.form.get('manfaat')
        jumlah_bibit = request.form.get('jumlah_bibit')
        image_path = None
        # Cek jika gambar ada dalam request
        if 'image' in request.files:
            image_file = request.files['image']
            print(f"File uploaded: {image_file.filename}")  # Log untuk mengecek nama file yang di-upload
        else:
            print("No file uploaded.")
        if 'image' not in request.files or request.files['image'].filename == '':
            flash('Gambar wajib di-upload!', 'danger')
            return render_template('admin-tree-managements-add.html')  # Tampilkan form kembali dengan pesan error

        image_file = request.files['image']
        filename = secure_filename(image_file.filename)
        upload_folder = 'static/uploads'
        os.makedirs(upload_folder, exist_ok=True)  # Pastikan folder ada
        unique_filename = f"{uuid.uuid4().hex}_{filename}"  # Bikin nama file unik
        image_path = os.path.join(upload_folder, unique_filename)
        image_file.save(image_path)  # Simpan file ke folder upload

        new_tree = Tree(
            user_id=session['user_id'], 
            name=name, 
            jenis=jenis, 
            image=unique_filename,
            jumlah_bibit=jumlah_bibit, 
            rata_rata_tumbuh=rata_rata_tumbuh, 
            waktu_tumbuh=waktu_tumbuh, 
            manfaat=manfaat
        )
        db.session.add(new_tree)
        db.session.commit()
        flash('Tree added successfully!', 'success')
        return redirect(url_for('treeManagements'))
    return render_template('admin-tree-managements-add.html')

@app.route('/admin/treeManagements/<int:tree_id>', methods=['GET'])
def treeDetails(tree_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    # Ambil data pohon berdasarkan tree_id
    tree = Tree.query.get(tree_id)  # Pastikan tree_id valid di database
    print(tree)
    if tree is None:
        return redirect(url_for('treeManagements'))  
    return render_template('admin-tree-managements-detail.html',tree=tree)

@app.route('/admin/treeManagements/<int:tree_id>/edit', methods=['POST', 'GET'])
def treeEdits(tree_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    tree = Tree.query.get(tree_id)
    if not tree:
        flash('Tree not found!', 'error')
        return redirect(url_for('treeManagements'))
    
    if request.method == 'POST':
        # Ambil data dari form
        tree.name = request.form.get('name', tree.name)
        tree.jenis = request.form.get('jenis', tree.jenis)
        tree.rata_rata_tumbuh = request.form.get('rata_rata_tumbuh', tree.rata_rata_tumbuh)
        tree.waktu_tumbuh = request.form.get('waktu_tumbuh', tree.waktu_tumbuh)
        tree.manfaat = request.form.get('manfaat', tree.manfaat)
        tree.jumlah_bibit = request.form.get('jumlah_bibit', tree.jumlah_bibit)
        
        # Update image jika ada upload baru
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename != '':
                if tree.image and os.path.exists(tree.image):
                    os.remove(tree.image)
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('static/uploads', filename)
                image_file.save(image_path)
                tree.image = filename
        
        # Commit perubahan ke database
        db.session.commit()
        flash('Tree updated successfully!', 'success')
        return redirect(url_for('treeManagements'))
    
    return render_template('admin-tree-managements-edit.html', tree=tree)


@app.route('/admin/treeManagements/delete/<int:tree_id>', methods=['POST'])
def deleteTree(tree_id):
    tree = Tree.query.get(tree_id)
    if not tree:
        flash('Tree not found!', 'error')
        return redirect(url_for('treeManagements'))
    
    # Remove image file if exists
    if tree.image and os.path.exists(tree.image):
        os.remove(tree.image)

    db.session.delete(tree)
    db.session.commit()
    flash('Tree deleted successfully!', 'success')
    return redirect(url_for('treeManagements'))

@app.route('/admin/activity', methods=['GET'])
def admin_activity():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))

    activities = get_admin_activity_logs()
    return render_template('admin-activity.html', activities=activities)

if __name__ == '__main__':
    app.run(debug=True)
