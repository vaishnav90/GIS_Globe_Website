#!/usr/bin/env python3
"""
Script to add sample projects to the database for demonstration.
"""

from main import app, db
from models import Project, User
from datetime import datetime

def add_sample_projects():
    """Add sample projects to the database."""
    with app.app_context():
        # Get the first user (admin) to assign projects to
        user = User.query.first()
        if not user:
            print("No users found in database. Please create a user first.")
            return
        
        # Sample projects data
        sample_projects = [
            {
                'title': 'Our Team',
                'description': 'National 4-H GIS Leadership Team hub page containing team information and resources.',
                'project_link': 'https://example.com/our-team',
                'project_type': 'Hub Page',
                'tags': '4-H, GIS, Leadership, Team',
                'created_at': datetime(2025, 5, 9)
            },
            {
                'title': 'Survey123 for National Urban Extension Leaders Conference',
                'description': 'This is a Survey123 that can be used to gather data from scenario cards given to attendees.',
                'project_link': 'https://survey123.arcgis.com/share/example',
                'project_type': 'Survey123',
                'tags': 'Survey123, NCExtConference2025, BrandonEstevez',
                'created_at': datetime(2024, 12, 31)
            },
            {
                'title': 'DensityFeature_NCProcessingPacking2025',
                'description': 'Output generated from Calculate Density analysis for North Carolina processing and packing facilities.',
                'project_link': 'https://services.arcgis.com/example/density',
                'project_type': 'Feature Service',
                'tags': 'Density, NC, Processing, Packing, 2025',
                'created_at': datetime(2025, 4, 21)
            },
            {
                'title': 'GroceryStoresInNC2025',
                'description': 'Comprehensive dataset of grocery store locations across North Carolina for 2025.',
                'project_link': 'https://services.arcgis.com/example/grocery-stores',
                'project_type': 'Feature Service',
                'tags': 'Estevez2025, Estevez, 2025, NOURISH, GroceryStores, Locations, NC, NorthCarolina',
                'created_at': datetime(2025, 2, 7)
            }
        ]
        
        # Check if projects already exist
        existing_projects = Project.query.count()
        if existing_projects > 0:
            print(f"Found {existing_projects} existing projects. Skipping sample data addition.")
            return
        
        # Add sample projects
        for project_data in sample_projects:
            project = Project(
                title=project_data['title'],
                description=project_data['description'],
                project_link=project_data['project_link'],
                project_type=project_data['project_type'],
                tags=project_data['tags'],
                created_by=user.id,
                created_at=project_data['created_at'],
                updated_at=project_data['created_at']
            )
            db.session.add(project)
        
        db.session.commit()
        print(f"Successfully added {len(sample_projects)} sample projects to the database!")

if __name__ == '__main__':
    add_sample_projects() 