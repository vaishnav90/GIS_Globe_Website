#!/usr/bin/env python3
"""
Main Flask application for National 4-H GIS Leadership Team Website
Cloud Storage Version - Uses Google Cloud Storage for data persistence
"""

from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from cloud_storage import CloudStorageManager
from cloud_user import CloudUser
from forms import RegistrationForm, LoginForm, ContactForm, ProjectForm, GalleryForm

# Load environment variables
load_dotenv()

# Simple object wrapper to convert dictionaries to objects with attributes
class DictToObject:
    def __init__(self, data_dict):
        for key, value in data_dict.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize cloud storage
cloud_storage = CloudStorageManager()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return CloudUser.get(user_id)

@app.after_request
def add_header(response):
    """Add headers to prevent caching issues."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = '0'
    return response

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@app.route('/')
def home():
    """Home page."""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@app.route('/projects')
def projects():
    """Projects page."""
    projects_data = cloud_storage.get_all_projects()
    print(f"Loaded {len(projects_data)} projects from database")
    
    # Convert dictionaries to objects with attributes
    projects_objects = []
    for project_dict in projects_data:
        print(f"Project: {project_dict.get('title', 'Unknown')} - Image URL: {project_dict.get('image_url', 'None')}")
        
        # Convert to object
        project_obj = DictToObject(project_dict)
        projects_objects.append(project_obj)
    
    return render_template('projects.html', projects=projects_objects)

@app.route('/gallery')
def gallery():
    """Gallery page."""
    gallery_items = cloud_storage.get_all_gallery_items()
    
    # Convert dictionaries to objects with attributes
    gallery_objects = []
    for item_dict in gallery_items:
        # Add creator information to each gallery item
        creator = cloud_storage.get_user_by_id(item_dict['created_by'])
        item_dict['creator'] = creator
        
        # Convert to object
        item_obj = DictToObject(item_dict)
        gallery_objects.append(item_obj)
    
    return render_template('gallery.html', gallery_items=gallery_objects)

@app.route('/add-gallery-item', methods=['GET', 'POST'])
@login_required
def add_gallery_item():
    """Add gallery item."""
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        if request.headers.get('Content-Type') == 'application/json' or request.is_xhr:
            return jsonify({'success': False, 'message': 'Only users with @national4hgeospatialteam.us email addresses can add gallery items.'})
        flash('Only users with @national4hgeospatialteam.us email addresses can add gallery items.', 'danger')
        return redirect(url_for('gallery'))
    
    # Handle AJAX request from modal
    if request.method == 'POST' and request.headers.get('Content-Type') != 'application/json':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            image_file = request.files.get('image_file')
            
            if not title or not description or not image_file:
                return jsonify({'success': False, 'message': 'All fields are required.'})
            
            # Handle image upload
            uploaded_image = cloud_storage.upload_file(image_file, image_file.filename, 'uploads')
            if uploaded_image:
                cloud_storage.create_gallery_item(
                    title=title,
                    description=description,
                    image_url=uploaded_image,
                    created_by=current_user.id
                )
                return jsonify({'success': True, 'message': 'Gallery item added successfully!'})
            else:
                return jsonify({'success': False, 'message': 'Error uploading image. Please try again.'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    
    # Handle regular form submission
    form = GalleryForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image_file.data and form.image_file.data.filename:
            uploaded_image = cloud_storage.upload_file(form.image_file.data, form.image_file.data.filename, 'uploads')
            if uploaded_image:
                cloud_storage.create_gallery_item(
                    title=form.title.data,
                    description=form.description.data,
                    image_url=uploaded_image,
                    created_by=current_user.id
                )
                flash('Gallery item added successfully!', 'success')
                return redirect(url_for('gallery'))
            else:
                flash('Error uploading image. Please try again.', 'error')
                return render_template('add_gallery_item.html', form=form)
        else:
            flash('Please select an image to upload.', 'error')
            return render_template('add_gallery_item.html', form=form)
    
    return render_template('add_gallery_item.html', form=form)

@app.route('/delete-gallery-item/<item_id>', methods=['POST'])
@login_required
def delete_gallery_item(item_id):
    """Delete gallery item."""
    print(f"Delete request received for item_id: {item_id}")
    print(f"Current user: {current_user.email}")
    
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        print("Unauthorized user attempted to delete gallery item")
        return jsonify({'success': False, 'message': 'Only users with @national4hgeospatialteam.us email addresses can delete gallery items.'})
    
    gallery_item = cloud_storage.get_gallery_item_by_id(item_id)
    print(f"Gallery item found: {gallery_item is not None}")
    
    # Allow any geospatial user to delete any gallery item
    if gallery_item:
        try:
            delete_result = cloud_storage.delete_gallery_item(item_id)
            if delete_result:
                print(f"Successfully deleted gallery item: {item_id}")
                return jsonify({'success': True, 'message': 'Gallery item deleted successfully!'})
            else:
                print(f"Failed to delete gallery item: {item_id}")
                return jsonify({'success': False, 'message': 'Failed to delete gallery item from storage.'})
        except Exception as e:
            print(f"Error deleting gallery item: {str(e)}")
            return jsonify({'success': False, 'message': f'Error deleting gallery item: {str(e)}'})
    else:
        print(f"Gallery item not found: {item_id}")
        return jsonify({'success': False, 'message': 'Gallery item not found.'})

@app.route('/edit-gallery-item/<item_id>', methods=['POST'])
@login_required
def edit_gallery_item(item_id):
    """Edit gallery item."""
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        return jsonify({'success': False, 'message': 'Only users with @national4hgeospatialteam.us email addresses can edit gallery items.'})
    
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        image_file = request.files.get('image_file')
        
        if not title or not description:
            return jsonify({'success': False, 'message': 'Title and description are required.'})
        
        # Get the existing gallery item
        gallery_item = cloud_storage.get_gallery_item_by_id(item_id)
        if not gallery_item:
            return jsonify({'success': False, 'message': 'Gallery item not found.'})
        
        # Allow any geospatial user to edit any gallery item
        # No creator restriction needed
        
        # Handle image upload if provided
        image_url = gallery_item['image_url']  # Keep existing image by default
        if image_file and image_file.filename:
            uploaded_image = cloud_storage.upload_file(image_file, image_file.filename, 'uploads')
            if uploaded_image:
                image_url = uploaded_image
            else:
                return jsonify({'success': False, 'message': 'Error uploading new image. Please try again.'})
        
        # Update the gallery item
        cloud_storage.update_gallery_item(
            item_id=item_id,
            title=title,
            description=description,
            image_url=image_url
        )
        
        return jsonify({'success': True, 'message': 'Gallery item updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/add-project', methods=['GET', 'POST'])
@login_required
def add_project():
    """Add project."""
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
            print(f"Processing uploaded file: {form.image_file.data.filename}")
            uploaded_image = cloud_storage.upload_file(form.image_file.data, form.image_file.data.filename, 'uploads')
            if uploaded_image:
                image_url = uploaded_image
                print(f"Image uploaded successfully. URL: {image_url}")
                flash('Image uploaded successfully!', 'success')
            else:
                print("Failed to upload image")
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
        
        # Create project
        cloud_storage.create_project(
            title=form.title.data,
            creator_name=form.creator_name.data,
            description=form.description.data,
            project_link=form.project_link.data,
            project_type=form.project_type.data,
            tags=form.tags.data,
            image_url=image_url,
            created_by=current_user.id
        )
        
        flash('Project added successfully!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('add_project.html', form=form)

@app.route('/edit-project/<project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit project."""
    print(f"Edit project request for project_id: {project_id}")
    print(f"Current user: {current_user.email}")
    
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        print("Unauthorized user attempted to edit project")
        flash('Only users with @national4hgeospatialteam.us email addresses can edit projects.', 'danger')
        return redirect(url_for('projects'))
    
    project_dict = cloud_storage.get_project_by_id(project_id)
    print(f"Project found: {project_dict is not None}")
    if project_dict:
        print(f"Project data: {project_dict}")
    
    if not project_dict:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    # Convert to object for template compatibility
    project = DictToObject(project_dict)
    
    # Only allow the creator to edit
    if project_dict['created_by'] != current_user.id:
        print(f"User {current_user.id} tried to edit project created by {project_dict['created_by']}")
        flash('You can only edit your own projects.', 'danger')
        return redirect(url_for('projects'))
    
    form = ProjectForm()
    print(f"Form validation result: {form.validate_on_submit()}")
    if form.errors:
        print(f"Form errors: {form.errors}")
    if form.validate_on_submit():
        # Handle image upload or URL
        image_url = form.image_url.data
        
        # Check if file was uploaded
        if form.image_file.data and form.image_file.data.filename:
            uploaded_image = cloud_storage.upload_file(form.image_file.data, form.image_file.data.filename, 'uploads')
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
        
        print("Processing POST request for project edit")
        print(f"Form data received:")
        print(f"  title: {form.title.data}")
        print(f"  description: {form.description.data}")
        print(f"  project_link: {form.project_link.data}")
        print(f"  project_type: {form.project_type.data}")
        print(f"  tags: {form.tags.data}")
        print(f"  image_url: {image_url}")
        
        # Update project
        try:
            print("Attempting to update project in cloud storage")
            updated_project = cloud_storage.update_project(
                project_id,
                title=form.title.data,
                creator_name=form.creator_name.data,
                description=form.description.data,
                project_link=form.project_link.data,
                project_type=form.project_type.data,
                tags=form.tags.data,
                image_url=image_url
            )
            if updated_project:
                print(f"Successfully updated project: {project_id}")
                flash('Project updated successfully!', 'success')
            else:
                print(f"Failed to update project: {project_id}")
                flash('Failed to update project.', 'error')
            return redirect(url_for('projects'))
        except Exception as e:
            print(f"Error updating project: {str(e)}")
            flash(f'Error updating project: {str(e)}', 'error')
            return render_template('edit_project.html', form=form, project=project)
    
    elif request.method == 'GET':
        # Populate form with existing data
        form.title.data = project_dict['title']
        form.creator_name.data = project_dict.get('creator_name', '')
        form.description.data = project_dict['description']
        form.project_link.data = project_dict['project_link']
        form.project_type.data = project_dict['project_type']
        form.tags.data = project_dict['tags']
        form.image_url.data = project_dict['image_url']
    
    return render_template('edit_project.html', form=form, project=project)

@app.route('/delete-project/<project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete project."""
    print(f"Delete project request for project_id: {project_id}")
    print(f"Current user: {current_user.email}")
    
    # Check if user has authorized email domain
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        print("Unauthorized user attempted to delete project")
        flash('Only users with @national4hgeospatialteam.us email addresses can delete projects.', 'danger')
        return redirect(url_for('projects'))
    
    project = cloud_storage.get_project_by_id(project_id)
    print(f"Project found: {project is not None}")
    if project:
        print(f"Project data: {project}")
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    # Only allow the creator to delete
    if project['created_by'] != current_user.id:
        print(f"User {current_user.id} tried to delete project created by {project['created_by']}")
        flash('You can only delete your own projects.', 'danger')
        return redirect(url_for('projects'))
    
    try:
        print("Attempting to delete project from cloud storage")
        delete_result = cloud_storage.delete_project(project_id)
        if delete_result:
            print(f"Successfully deleted project: {project_id}")
            flash('Project deleted successfully!', 'success')
        else:
            print(f"Failed to delete project: {project_id}")
            flash('Failed to delete project from storage.', 'error')
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
        flash(f'Error deleting project: {str(e)}', 'error')
    
    return redirect(url_for('projects'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page."""
    return render_template('contact.html')

@app.route('/youth-map-lab')
def youth_map_lab():
    """Youth Map Lab page."""
    return render_template('youth_map_lab.html')

@app.route('/music')
def music():
    """Music page - redirects to National 4-H GIS Team Pictures."""
    return redirect(url_for('national_4h_gis_team'))

@app.route('/national-4h-gis-team')
def national_4h_gis_team():
    """National 4-H GIS Team Pictures page."""
    # Get all gallery items from the database
    gallery_items = cloud_storage.get_all_gallery_items()
    return render_template('national_4h_gis_team.html', gallery_items=gallery_items)

@app.route('/team')
def team():
    """Team page."""
    # Force a complete refresh by clearing any potential cache
    import time
    time.sleep(0.1)  # Small delay to ensure any caching is cleared
    
    # Get all team members from the database
    team_members = cloud_storage.get_all_team_members()
    print(f"Loaded {len(team_members)} team members from database")
    
    # Convert dictionaries to objects with attributes
    team_objects = []
    for member_dict in team_members:
        print(f"Team member: {member_dict.get('name', 'Unknown')} (ID: {member_dict.get('id', 'No ID')}) - Description: {member_dict.get('description', 'No description')[:100]}...")
        
        # Convert to object
        member_obj = DictToObject(member_dict)
        team_objects.append(member_obj)
    
    # Add cache-busting parameter to force browser refresh
    cache_buster = int(time.time())
    return render_template('team.html', team_members=team_objects, cache_buster=cache_buster)

@app.route('/add-team-member', methods=['GET', 'POST'])
@login_required
def add_team_member():
    """Add a new team member."""
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only team members can add new team members.', 'error')
        return redirect(url_for('team'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        description = request.form.get('description')
        linkedin_url = request.form.get('linkedin_url')
        member_type = request.form.get('member_type', 'board')  # 'board' or 'alumni'
        year = request.form.get('year', '')  # For alumni
        
        if not all([name, title, description]):
            flash('Name, title, and description are required.', 'error')
            return redirect(url_for('add_team_member'))
        
        try:
            cloud_storage.create_team_member(
                name=name,
                title=title,
                description=description,
                linkedin_url=linkedin_url,
                member_type=member_type,
                year=year,
                created_by=current_user.id
            )
            flash('Team member added successfully!', 'success')
            return redirect(url_for('team'))
        except Exception as e:
            flash(f'Error adding team member: {str(e)}', 'error')
    
    return render_template('add_team_member.html')

@app.route('/edit-team-member/<member_id>', methods=['GET', 'POST'])
@login_required
def edit_team_member(member_id):
    """Edit a team member."""
    print(f"Edit team member request for member_id: {member_id}")
    print(f"Current user: {current_user.email}")
    
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        print("Unauthorized user attempted to edit team member")
        flash('Only team members can edit team members.', 'error')
        return redirect(url_for('team'))
    
    if request.method == 'POST':
        print("Processing POST request for team member edit")
        name = request.form.get('name')
        title = request.form.get('title')
        description = request.form.get('description')
        linkedin_url = request.form.get('linkedin_url')
        member_type = request.form.get('member_type', 'board')
        year = request.form.get('year', '')
        
        print(f"Form data received:")
        print(f"  name: {name}")
        print(f"  title: {title}")
        print(f"  description: {description}")
        print(f"  linkedin_url: {linkedin_url}")
        print(f"  member_type: {member_type}")
        print(f"  year: {year}")
        
        if not all([name, title, description]):
            print("Missing required fields")
            flash('Name, title, and description are required.', 'error')
            return redirect(url_for('edit_team_member', member_id=member_id))
        
        try:
            print("Attempting to update team member in cloud storage")
            updated_member = cloud_storage.update_team_member(
                member_id=member_id,
                name=name,
                title=title,
                description=description,
                linkedin_url=linkedin_url,
                member_type=member_type,
                year=year
            )
            if updated_member:
                print(f"Successfully updated team member: {member_id}")
                flash('Team member updated successfully!', 'success')
            else:
                print(f"Failed to update team member: {member_id}")
                flash('Failed to update team member.', 'error')
            return redirect(url_for('team'))
        except Exception as e:
            print(f"Error updating team member: {str(e)}")
            flash(f'Error updating team member: {str(e)}', 'error')
    
    # Force a complete refresh by clearing any potential cache and reloading
    import time
    time.sleep(2)  # Increased delay to ensure any caching is cleared
    
    fresh_team_member_dict = cloud_storage.get_team_member(member_id)
    print(f"Rendering edit form with fresh data: {fresh_team_member_dict.get('updated_at', 'No updated_at') if fresh_team_member_dict else 'No data'}")
    
    if not fresh_team_member_dict:
        flash('Team member not found.', 'error')
        return redirect(url_for('team'))
    
    # Convert to object for template compatibility
    fresh_team_member = DictToObject(fresh_team_member_dict)
    
    # Add cache-busting parameter to force browser refresh
    cache_buster = int(time.time())
    return render_template('edit_team_member.html', team_member=fresh_team_member, cache_buster=cache_buster)

@app.route('/delete-team-member/<member_id>', methods=['POST'])
@login_required
def delete_team_member(member_id):
    """Delete a team member."""
    if not current_user.email.endswith('@national4hgeospatialteam.us'):
        flash('Only team members can delete team members.', 'error')
        return redirect(url_for('team'))
    
    team_member = cloud_storage.get_team_member(member_id)
    if not team_member:
        flash('Team member not found.', 'error')
        return redirect(url_for('team'))
    
    try:
        delete_result = cloud_storage.delete_team_member(member_id)
        if delete_result:
            flash('Team member deleted successfully!', 'success')
        else:
            flash('Failed to delete team member from storage.', 'error')
    except Exception as e:
        flash(f'Error deleting team member: {str(e)}', 'error')
    
    return redirect(url_for('team'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            cloud_storage.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = cloud_storage.authenticate_user(form.username.data, form.password.data)
        if user_data:
            user = CloudUser(user_data)
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    """User profile."""
    return render_template('profile.html')

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
        
        # Priority 4: Look for iframe elements (embedded maps)
        iframe_elements = soup.find_all('iframe')
        for iframe in iframe_elements:
            iframe_src = iframe.get('src')
            if iframe_src and any(keyword in iframe_src.lower() for keyword in ['map', 'viewer', 'scene', 'arcgis', 'esri']):
                # Try to scrape the iframe source for map images
                try:
                    iframe_response = requests.get(iframe_src, headers=headers, timeout=5)
                    iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                    
                    # Look for images in the iframe
                    iframe_imgs = iframe_soup.find_all('img')
                    for img in iframe_imgs:
                        src = img.get('src')
                        if src and not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                            return urljoin(iframe_src, src)
                except:
                    pass
        
        # Priority 5: Look for hero/main image selectors
        hero_selectors = [
            'img[class*="hero"]',
            'img[class*="main"]',
            'img[class*="primary"]',
            'img[class*="featured"]',
            'img[class*="banner"]',
            'img[class*="header"]',
            '.hero img',
            '.main img',
            '.primary img',
            '.featured img',
            '.banner img',
            '.header img',
            '.jumbotron img',
            '.hero-image img',
            '.main-image img'
        ]
        
        for selector in hero_selectors:
            hero_img = soup.select_one(selector)
            if hero_img and hero_img.get('src'):
                src = hero_img.get('src')
                if not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                    return urljoin(url, src)
        
        # Priority 6: Find the largest image (likely the main content)
        all_images = soup.find_all('img')
        largest_image = None
        max_area = 0
        
        for img in all_images:
            src = img.get('src')
            if src and not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel', 'thumb']):
                width = img.get('width')
                height = img.get('height')
                
                # Try to get dimensions from style attribute
                if not width or not height:
                    style = img.get('style', '')
                    width_match = re.search(r'width:\s*(\d+)px', style)
                    height_match = re.search(r'height:\s*(\d+)px', style)
                    if width_match:
                        width = int(width_match.group(1))
                    if height_match:
                        height = int(height_match.group(1))
                
                # If we have dimensions, calculate area
                if width and height:
                    try:
                        area = int(width) * int(height)
                        if area > max_area:
                            max_area = area
                            largest_image = src
                    except (ValueError, TypeError):
                        pass
        
        if largest_image:
            return urljoin(url, largest_image)
        
        # Priority 7: Look for images with map-related alt text
        for img in all_images:
            src = img.get('src')
            alt = img.get('alt', '').lower()
            
            if src and not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel']):
                if any(keyword in alt for keyword in ['map', 'viewer', 'scene', 'webmap', 'webscene', 'arcgis', 'esri', 'geographic', 'spatial']):
                    return urljoin(url, src)
        
        # Priority 8: Return the first non-icon image
        for img in all_images:
            src = img.get('src')
            if src and not src.startswith('data:') and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'pixel', 'thumb']):
                return urljoin(url, src)
        
        return None
        
    except Exception as e:
        print(f"Error extracting image from {url}: {e}")
        return None

def save_uploaded_file(file):
    """
    Save an uploaded file to cloud storage and return the URL.
    """
    if file and file.filename:
        # Secure the filename
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        
        # Upload to cloud storage
        try:
            file_url = cloud_storage.upload_file(file, filename, 'uploads')
            return file_url
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    return None

if __name__ == '__main__':
    app.run(debug=True, port=5001) 