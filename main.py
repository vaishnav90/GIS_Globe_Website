from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from models import db, User, ContactMessage, Project, Gallery
from forms import RegistrationForm, LoginForm, ContactForm, ProjectForm, GalleryForm

def extract_image_from_url(url):
    """
    Extract the main map image from a given URL for use as a thumbnail.
    Prioritizes map images and handles ArcGIS/Esri applications.
    Returns the image URL or None if no suitable image is found.
    """
    try:
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request with a timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Priority 1: Look for map-specific meta images
        map_meta_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'meta[itemprop="image"]',
            'meta[name="thumbnail"]',
            'meta[name="preview"]'
        ]
        
        for selector in map_meta_selectors:
            meta_img = soup.select_one(selector)
            if meta_img and meta_img.get('content'):
                return urljoin(url, meta_img['content'])
        
        # Priority 2: Look for map-specific images with map-related classes/IDs
        map_selectors = [
            'img[class*="map"]',
            'img[class*="viewer"]',
            'img[class*="canvas"]',
            'img[class*="scene"]',
            'img[class*="webmap"]',
            'img[class*="webscene"]',
            'img[id*="map"]',
            'img[id*="viewer"]',
            'img[id*="canvas"]',
            'img[id*="scene"]',
            '.map img',
            '.viewer img',
            '.canvas img',
            '.scene img',
            '.webmap img',
            '.webscene img',
            '.esri-view img',
            '.esri-map img',
            '.esri-viewer img',
            '.esri-scene img',
            '.esri-webmap img',
            '.esri-webscene img',
            '.map-container img',
            '.viewer-container img',
            '.map-view img',
            '.scene-view img',
            '.webmap-view img',
            '.webscene-view img'
        ]
        
        for selector in map_selectors:
            map_img = soup.select_one(selector)
            if map_img and map_img.get('src'):
                src = map_img.get('src')
                if not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                    return urljoin(url, src)
        
        # Priority 3: Look for canvas elements (common in map applications)
        canvas_elements = soup.find_all('canvas')
        for canvas in canvas_elements:
            # Check if canvas has map-related classes or IDs
            classes = canvas.get('class', [])
            canvas_id = canvas.get('id', '')
            class_str = ' '.join(classes).lower()
            
            if any(keyword in class_str or keyword in canvas_id.lower() for keyword in ['map', 'viewer', 'scene', 'webmap', 'webscene', 'esri']):
                # For canvas elements, we might need to take a screenshot
                # For now, look for any image that might be the map preview
                parent = canvas.parent
                if parent:
                    parent_img = parent.find('img')
                    if parent_img and parent_img.get('src'):
                        src = parent_img.get('src')
                        if not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                            return urljoin(url, src)
        
        # Priority 4: Look for iframe elements (common in embedded maps)
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            iframe_src = iframe.get('src', '')
            if any(keyword in iframe_src.lower() for keyword in ['map', 'viewer', 'scene', 'webmap', 'webscene', 'arcgis', 'esri']):
                # Try to extract image from iframe source
                try:
                    iframe_response = requests.get(iframe_src, headers=headers, timeout=5)
                    if iframe_response.status_code == 200:
                        iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                        # Look for map images in iframe
                        iframe_img = iframe_soup.select_one('img[class*="map"], img[id*="map"], .map img, .esri-view img')
                        if iframe_img and iframe_img.get('src'):
                            return urljoin(iframe_src, iframe_img['src'])
                except:
                    pass
        
        # Priority 5: Look for hero/main images with map-related keywords
        hero_selectors = [
            'img[class*="hero"]',
            'img[class*="main"]',
            'img[class*="banner"]',
            'img[class*="featured"]',
            'img[class*="primary"]',
            'img[id*="hero"]',
            'img[id*="main"]',
            'img[id*="banner"]',
            '.hero img',
            '.main-image img',
            '.banner img',
            '.featured-image img',
            '.primary-image img',
            'header img',
            '.header img',
            '.main-content img',
            '.content img'
        ]
        
        for selector in hero_selectors:
            hero_img = soup.select_one(selector)
            if hero_img and hero_img.get('src'):
                src = hero_img.get('src')
                # Skip data URLs and small images
                if not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                    return urljoin(url, src)
        
        # Priority 6: Look for the largest image on the page
        images = soup.find_all('img')
        largest_image = None
        max_area = 0
        
        for img in images:
            src = img.get('src')
            if not src or src.startswith('data:'):
                continue
                
            # Skip obvious non-main images
            if any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel', 'favicon']):
                continue
            
            # Check dimensions
            width = img.get('width')
            height = img.get('height')
            
            if width and height:
                try:
                    w, h = int(width), int(height)
                    area = w * h
                    if area > max_area and w >= 300 and h >= 200:  # Minimum size for main image
                        max_area = area
                        largest_image = src
                except ValueError:
                    pass
            
            # Check CSS classes for relevance
            classes = img.get('class', [])
            class_str = ' '.join(classes).lower()
            if any(keyword in class_str for keyword in ['hero', 'main', 'banner', 'featured', 'primary', 'map', 'dashboard', 'viewer', 'scene']):
                if not largest_image:  # If we haven't found a large image yet, use this one
                    largest_image = src
        
        if largest_image:
            return urljoin(url, largest_image)
        
        # Priority 7: Look for images with map-related alt text
        for img in images:
            src = img.get('src')
            if not src or src.startswith('data:'):
                continue
                
            alt = img.get('alt', '').lower()
            if any(keyword in alt for keyword in ['map', 'viewer', 'scene', 'webmap', 'webscene', 'project', 'dashboard', 'app', 'screenshot', 'main', 'hero', 'banner']):
                if not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                    return urljoin(url, src)
        
        # If no suitable image found, return None
        return None
        
    except Exception as e:
        print(f"Error extracting image from {url}: {str(e)}")
        return None

def get_default_image_for_type(project_type):
    """
    Return a default image URL based on project type.
    """
    default_images = {
        'Hub Page': '/static/images/hub-page-default.jpg',
        'Form': '/static/images/form-default.jpg',
        'Feature Service': '/static/images/feature-service-default.jpg',
        'Dataset': '/static/images/dataset-default.jpg',
        'Survey123': '/static/images/survey123-default.jpg',
        'Web App': '/static/images/web-app-default.jpg',
        'Dashboard': '/static/images/dashboard-default.jpg',
        'Story Map': '/static/images/story-map-default.jpg',
        'Other': '/static/images/project-default.jpg'
    }
    return default_images.get(project_type, '/static/images/project-default.jpg')

def save_uploaded_file(file):
    """
    Save an uploaded file and return the URL path.
    """
    if file and file.filename:
        # Secure the filename
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}{ext}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Return the URL path
        return f'/static/uploads/{filename}'
    return None

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Production: Use PostgreSQL on Google Cloud
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Development: Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Add cache control headers for static files
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

# Serve static files with custom headers
@app.route('/static/<path:filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    projects = Project.query.filter_by(is_active=True).order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)

@app.route('/gallery')
def gallery():
    gallery_items = Gallery.query.filter_by(is_active=True).order_by(Gallery.created_at.desc()).all()
    return render_template('gallery.html', gallery_items=gallery_items)

@app.route('/add-gallery-item', methods=['GET', 'POST'])
@login_required
def add_gallery_item():
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only users with @national4hgeospatialteam.us email addresses can add gallery items.', 'danger')
        return redirect(url_for('gallery'))
    
    form = GalleryForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image_file.data and form.image_file.data.filename:
            uploaded_image = save_uploaded_file(form.image_file.data)
            if uploaded_image:
                gallery_item = Gallery(
                    title=form.title.data,
                    description=form.description.data,
                    image_url=uploaded_image,
                    created_by=current_user.id
                )
                db.session.add(gallery_item)
                db.session.commit()
                flash('Gallery item added successfully!', 'success')
                return redirect(url_for('gallery'))
            else:
                flash('Error uploading image. Please try again.', 'error')
                return render_template('add_gallery_item.html', form=form)
        else:
            flash('Please select an image to upload.', 'error')
            return render_template('add_gallery_item.html', form=form)
    
    return render_template('add_gallery_item.html', form=form)

@app.route('/delete-gallery-item/<int:item_id>', methods=['POST'])
@login_required
def delete_gallery_item(item_id):
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only users with @national4hgeospatialteam.us email addresses can delete gallery items.', 'danger')
        return redirect(url_for('gallery'))
    
    gallery_item = Gallery.query.get_or_404(item_id)
    
    # Only allow the creator to delete
    if gallery_item.created_by != current_user.id:
        flash('You can only delete your own gallery items.', 'danger')
        return redirect(url_for('gallery'))
    
    gallery_item.is_active = False
    db.session.commit()
    flash('Gallery item deleted successfully!', 'success')
    return redirect(url_for('gallery'))

@app.route('/add-project', methods=['GET', 'POST'])
@login_required
def add_project():
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only users with @national4hgeospatialteam.us email addresses can add projects.', 'danger')
        return redirect(url_for('projects'))
    form = ProjectForm()
    if form.validate_on_submit():
        # Handle image upload or URL
        image_url = form.image_url.data
        
        # Check if file was uploaded
        if form.image_file.data and form.image_file.data.filename:
            uploaded_image = save_uploaded_file(form.image_file.data)
            if uploaded_image:
                image_url = uploaded_image
                flash('Image uploaded successfully!', 'success')
            else:
                flash('Error uploading image. Please try again.', 'error')
                return render_template('add_project.html', form=form)
        
        # If no file uploaded and no URL provided, try auto-detection
        elif not image_url:
            extracted_image = extract_image_from_url(form.project_link.data)
            if extracted_image:
                image_url = extracted_image
                flash('Main image automatically detected from your project URL!', 'success')
            else:
                # If no image found, require user to provide one
                flash('No map or main image found on the project page. Please upload an image manually.', 'warning')
                return render_template('add_project.html', form=form)
        
        project = Project(
            title=form.title.data,
            description=form.description.data,
            project_link=form.project_link.data,
            project_type=form.project_type.data,
            tags=form.tags.data,
            image_url=image_url,
            created_by=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('add_project.html', form=form)

@app.route('/edit-project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only users with @national4hgeospatialteam.us email addresses can edit projects.', 'danger')
        return redirect(url_for('projects'))
    
    project = Project.query.get_or_404(project_id)
    
    # Only allow the creator to edit
    if project.created_by != current_user.id:
        flash('You can only edit your own projects.', 'danger')
        return redirect(url_for('projects'))
    
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        # Handle image upload or URL
        image_url = form.image_url.data
        
        # Check if file was uploaded
        if form.image_file.data and form.image_file.data.filename:
            uploaded_image = save_uploaded_file(form.image_file.data)
            if uploaded_image:
                image_url = uploaded_image
                flash('Image uploaded successfully!', 'success')
            else:
                flash('Error uploading image. Please try again.', 'error')
                return render_template('edit_project.html', form=form, project=project)
        
        # If no file uploaded and no URL provided, try auto-detection
        elif not image_url:
            extracted_image = extract_image_from_url(form.project_link.data)
            if extracted_image:
                image_url = extracted_image
                flash('Main image automatically detected from your project URL!', 'success')
            else:
                # If no image found, require user to provide one
                flash('No map or main image found on the project page. Please upload an image manually.', 'warning')
                return render_template('edit_project.html', form=form, project=project)
        
        project.title = form.title.data
        project.description = form.description.data
        project.project_link = form.project_link.data
        project.project_type = form.project_type.data
        project.tags = form.tags.data
        project.image_url = image_url
        project.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('edit_project.html', form=form, project=project)

@app.route('/delete-project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only users with @national4hgeospatialteam.us email addresses can delete projects.', 'danger')
        return redirect(url_for('projects'))
    
    project = Project.query.get_or_404(project_id)
    
    # Only allow the creator to delete
    if project.created_by != current_user.id:
        flash('You can only delete your own projects.', 'danger')
        return redirect(url_for('projects'))
    
    project.is_active = False
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(message)
        db.session.commit()
        flash('Thank you for your message! I will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/music')
def music():
    return render_template('music.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Try to find user by username first, then by email
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User.query.filter_by(email=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True) 
    