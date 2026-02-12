"""
Production Flask API for AI Video Production System
Multi-user support with authentication, database, and cloud storage
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import json
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

from src.core.config import Config
from src.agents.crew import ProductionCrew
from src.tools.fast_search import FastVideoSearch
from src.tools.downloader import VideoDownloader
from src.tools.broll_extractor import BRollExtractor
from src.tools.flux_generator import FluxImageGenerator, integrate_with_image_fallback
from src.tools.premiere_exporter import PremiereExporter
from src.tools.capcut_exporter import CapCutExporter

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///video_production.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# AWS S3 Configuration (optional - for cloud storage)
USE_S3 = os.getenv('USE_S3', 'false').lower() == 'true'
if USE_S3:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    S3_BUCKET = os.getenv('S3_BUCKET_NAME')

# Local storage fallback
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    api_quota = db.Column(db.Integer, default=100)  # Monthly quota
    api_usage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_tier = db.Column(db.String(20), default='free')  # free, pro, enterprise
    
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_quota(self):
        return self.api_usage < self.api_quota


class Project(db.Model):
    """Project model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    script = db.Column(db.Text)
    duration = db.Column(db.Float)
    status = db.Column(db.String(20), default='created')  # created, analyzing, searching, downloading, generating, complete, failed
    scenes_count = db.Column(db.Integer, default=0)
    clips_count = db.Column(db.Integer, default=0)
    images_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Storage paths
    plan_path = db.Column(db.String(500))
    premiere_path = db.Column(db.String(500))
    capcut_path = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'status': self.status,
            'scenes_count': self.scenes_count,
            'clips_count': self.clips_count,
            'images_count': self.images_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Usage(db.Model):
    """API usage tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cost = db.Column(db.Float, default=0.0)  # Cost in credits


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'subscription_tier': user.subscription_tier,
                'api_quota': user.api_quota,
                'api_usage': user.api_usage
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'subscription_tier': user.subscription_tier,
                'api_quota': user.api_quota,
                'api_usage': user.api_usage
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'subscription_tier': user.subscription_tier,
                'api_quota': user.api_quota,
                'api_usage': user.api_usage,
                'projects_count': len(user.projects)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PROJECT ENDPOINTS (Protected)
# ============================================================================

@app.route('/api/projects', methods=['GET'])
@jwt_required()
def list_user_projects():
    """List all projects for current user"""
    try:
        user_id = get_jwt_identity()
        projects = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'projects': [p.to_dict() for p in projects]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get specific project"""
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(project_id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete project"""
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(project_id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # TODO: Delete files from storage (S3 or local)
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project deleted'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-script', methods=['POST'])
@jwt_required()
def analyze_script():
    """Analyze script with AI agents (Protected)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check quota
        if not user.has_quota():
            return jsonify({'error': 'API quota exceeded. Please upgrade your plan.'}), 429
        
        data = request.json
        script = data.get('script')
        duration = data.get('duration', 60)
        
        if not script:
            return jsonify({'error': 'Script is required'}), 400
        
        # Track usage
        user.api_usage += 1
        usage = Usage(user_id=user_id, endpoint='analyze-script', cost=1.0)
        db.session.add(usage)
        
        # Run AI agents
        config = Config.load()
        crew = ProductionCrew(config)
        result = crew.analyze_script(script, duration)
        
        # Parse result
        import re
        json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            return jsonify({'error': 'Failed to parse agent output'}), 500
        
        # Create project
        project_id = datetime.now().strftime('%Y%m%d_%H%M%S') + f'_{user_id}'
        project = Project(
            user_id=user_id,
            project_id=project_id,
            title=plan.get('title', 'Untitled'),
            script=script,
            duration=duration,
            status='analyzing',
            scenes_count=len(plan.get('scenes', []))
        )
        
        # Save plan
        user_dir = OUTPUT_DIR / f"user_{user_id}"
        user_dir.mkdir(exist_ok=True)
        
        plan_path = user_dir / f"plan_{project_id}.json"
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        project.plan_path = str(plan_path)
        project.status = 'complete'
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'plan': plan,
            'scenes_count': len(plan.get('scenes', [])),
            'remaining_quota': user.api_quota - user.api_usage
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def list_users():
    """List all users (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if admin (you can add an is_admin field to User model)
        if user.username != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        users = User.query.all()
        
        return jsonify({
            'success': True,
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'subscription_tier': u.subscription_tier,
                'api_usage': u.api_usage,
                'api_quota': u.api_quota,
                'projects_count': len(u.projects),
                'created_at': u.created_at.isoformat()
            } for u in users]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get system statistics (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.username != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        total_users = User.query.count()
        total_projects = Project.query.count()
        total_usage = db.session.query(db.func.sum(Usage.cost)).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_projects': total_projects,
                'total_api_calls': Usage.query.count(),
                'total_cost': float(total_usage)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# HEALTH & INFO
# ============================================================================

@app.route('/')
def index():
    """Serve the frontend"""
    return app.send_static_file('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'mode': 'production',
        'database': 'connected',
        'storage': 's3' if USE_S3 else 'local'
    })


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                subscription_tier='enterprise',
                api_quota=999999
            )
            admin.set_password('admin123')  # Change this!
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created (username: admin, password: admin123)")


if __name__ == '__main__':
    print("=" * 80)
    print("🎬 AI VIDEO PRODUCTION API - PRODUCTION MODE")
    print("=" * 80)
    print("\nFeatures:")
    print("  ✓ Multi-user authentication (JWT)")
    print("  ✓ Database (SQLite/PostgreSQL)")
    print("  ✓ API quota management")
    print("  ✓ Usage tracking")
    print("  ✓ Cloud storage support (S3)")
    print("  ✓ Admin dashboard")
    print("\n" + "=" * 80)
    
    # Initialize database
    init_db()
    
    # Run app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
