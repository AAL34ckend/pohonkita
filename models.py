from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask import jsonify

# Initialize extensions
db = SQLAlchemy()

# Define Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    total_trees = db.Column(db.Integer, default=0)
    role = db.Column(db.Enum('admin', 'user'), default='user')
    status = db.Column(db.Enum('active', 'deactive'), default='user')

class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    jenis = db.Column(db.String(100))
    image = db.Column(db.String(255))
    jumlah_bibit = db.Column(db.Integer, nullable=False)
    rata_rata_tumbuh = db.Column(db.String(50))  # Example: '10-15 meter'
    waktu_tumbuh = db.Column(db.String(50))  # Example: '3-5 tahun hingga berbuah'
    manfaat = db.Column(db.Text)  # Example: 'Menghasilkan buah, Peneduh alami, etc.'

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Mengacu pada user yang mengajukan
    tree_id = db.Column(db.Integer, db.ForeignKey('tree.id'), nullable=False)  # Mengacu pada pohon yang dipilih
    full_name = db.Column(db.String(255), nullable=False)  # Nama lengkap pengaju
    city = db.Column(db.String(255), nullable=False)  # Kota tempat penanaman
    planned_planting_date = db.Column(db.Date, nullable=False)  # Tanggal rencana penanaman
    required_seeds = db.Column(db.Integer, nullable=False)  # Jumlah bibit yang dibutuhkan
    supporting_image = db.Column(db.String(255))  # Foto bukti pendukung
    notes = db.Column(db.Text)  # Catatan tambahan
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'banned', name='submission_status'), default='pending')  # Status pengajuan
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Waktu pengajuan
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # Waktu update pengajuan

    # Relasi ke tabel `user` dan `tree`
    user = db.relationship('User', backref='submissions')  # Relasi dengan tabel User
    tree = db.relationship('Tree', backref='submissions')  # Relasi dengan tabel Tree

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trees_id = db.Column(db.Integer, db.ForeignKey('tree.id'), nullable=False)
    name = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_trees = db.Column(db.Integer, default=0)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trees_id = db.Column(db.Integer, db.ForeignKey('tree.id'), nullable=False)
    goal_name = db.Column(db.String(255), nullable=False)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)  # Example: 'Planted a tree', 'Approved a request'
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

# Additional query for leaderboard
def get_leaderboard(user_id):
    top_users = db.session.query(
        User.id,
        User.name,
        User.total_trees
    ).order_by(User.total_trees.desc()).limit(10).all()

    user_rank_query = db.session.query(
        func.rank().over(order_by=User.total_trees.desc()).label('rank'),
        User.id,
        User.name,
        User.total_trees
    ).filter(User.id == user_id).first()

    return {
        'top_users': [{'id': u.id, 'name': u.name, 'total_trees': u.total_trees} for u in top_users],
        'user_rank': {
            'rank': user_rank_query.rank if user_rank_query else None,
            'id': user_rank_query.id if user_rank_query else None,
            'name': user_rank_query.name if user_rank_query else None,
            'total_trees': user_rank_query.total_trees if user_rank_query else None
        }
    }

# Dashboard Queries
def get_dashboard_summary():
    total_users = db.session.query(func.count(User.id)).scalar()
    total_trees = db.session.query(func.sum(User.total_trees)).scalar()
    top_contributor = db.session.query(
        User.name,
        User.total_trees
    ).order_by(User.total_trees.desc()).first()

    return {
        'total_users': total_users,
        'total_trees': total_trees,
        'top_contributor': {
            'name': top_contributor.name if top_contributor else None,
            'total_trees': top_contributor.total_trees if top_contributor else None
        }
    }

# Admin Management
def approve_reject_user_tree_request(status_id, action):
    status = Status.query.get(status_id)
    if not status:
        return jsonify({'message': 'Status not found'}), 404

    if action not in ['approved', 'rejected']:
        return jsonify({'message': 'Invalid action'}), 400

    status.name = action
    db.session.commit()

    # Log activity
    activity = ActivityLog(user_id=status.user_id, action=f'Request {action}')
    db.session.add(activity)
    db.session.commit()

    return jsonify({'message': f'Status {action} successfully!'}), 200

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Log activity
    activity = ActivityLog(user_id=user_id, action='Deleted user')
    db.session.add(activity)

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully!'}), 200

def add_tree_type(jenis, notes=None):
    new_tree = Tree(
        user_id=None,  # Admin adding tree types does not associate with a user
        name='Admin added tree',
        notes=notes,
        jenis=jenis,
        jumlah_bibit=0
    )
    db.session.add(new_tree)

    # Log activity
    activity = ActivityLog(user_id=None, action=f'Added tree type: {jenis}')
    db.session.add(activity)

    db.session.commit()
    return jsonify({'message': 'Tree type added successfully!'}), 201

# Activity Log Queries
def get_user_activity_logs(user_id):
    logs = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.timestamp.desc()).all()
    return [{'action': log.action, 'timestamp': log.timestamp} for log in logs]

def get_admin_activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    return [{'user_id': log.user_id, 'action': log.action, 'timestamp': log.timestamp} for log in logs]
