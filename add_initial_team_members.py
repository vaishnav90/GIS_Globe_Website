#!/usr/bin/env python3
"""
Script to add initial team members to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloud_storage import cloud_storage

def add_initial_team_members():
    """Add the original team members to the database."""
    
    # Board of Directors
    board_members = [
        {
            "name": "Thomas Tate",
            "title": "Founder",
            "description": "Retired National Program Leader at USDA with extensive experience in developing adult and youth learning programs and systems.",
            "linkedin_url": None,
            "member_type": "board",
            "year": None
        },
        {
            "name": "Esther Worker",
            "title": "Former Education Account Manager at Esri",
            "description": "Retired from Esri in 2020 after nearly 29 years, where she served as an Education Account Manager. She also served on the Advisory Council for Broomfield 4-H from 2005 to 2015.",
            "linkedin_url": None,
            "member_type": "board",
            "year": None
        },
        {
            "name": "Dr. Thomas Ray",
            "title": "Associate Executive Director, Poe Center for Health Education",
            "description": "Dr. Ray has championed youth-led STEM programs across North Carolina through his leadership in 4-H and now supports statewide education and outreach at the Poe Center. He remains a driving force in GIS competition and STEM access for students grades 4–12.",
            "linkedin_url": None,
            "member_type": "board",
            "year": None
        },
        {
            "name": "Barbaree Duke",
            "title": "GIS Curriculum & Training Consultant",
            "description": "Veteran classroom teacher and consultant in GIS in Education. Former Editor-in-Chief at Directions Magazine and curriculum lead at GISetc.",
            "linkedin_url": None,
            "member_type": "board",
            "year": None
        },
        {
            "name": "Dr. Gerardo López",
            "title": "STEM Extension Specialist, University of Arizona",
            "description": "A national leader in agricultural and STEM education, Dr. López has expanded 4-H STEM programs across Arizona — establishing the state as a top contender in national youth STEM efforts. His work connects underserved youth to science, agriculture, and water quality solutions.",
            "linkedin_url": None,
            "member_type": "board",
            "year": None
        },
        {
            "name": "Austin Ramsey",
            "title": "Founder & Chief Box Crusher, Pointech",
            "description": "A former Roan Scholar and East Tennessee State University graduate, Austin leads Pointech, LLC — a startup focused on applied GIS and youth tech engagement. He previously led National 4-H GIS workshops and national mapping projects.",
            "linkedin_url": None,
            "member_type": "board",
            "year": None
        }
    ]
    
    # Alumni
    alumni_members = [
        {
            "name": "Geovanny Solera",
            "title": "Now at Esri",
            "description": "Now at Esri, Geovanny supports digital transformation for utilities and telecoms. He started in youth-led mapping initiatives and has since built a career helping cities and utility clients build high-performing GIS platforms with impact across sectors.",
            "linkedin_url": None,
            "member_type": "alumni",
            "year": "Field Mapping Lead, 2009"
        },
        {
            "name": "Arjun Kuncha",
            "title": "Mechanical Engineering Student and Franklin Scholar at NC State",
            "description": "Arjun, a Mechanical Engineering student and Franklin Scholar at NC State, created advanced ArcGIS Web Apps that visualized local health, equity, and sustainability data. He bridged geospatial thinking with engineering to elevate youth storytelling through tech and civic design.",
            "linkedin_url": None,
            "member_type": "alumni",
            "year": "GIS 3D Imagery Operator, 2024"
        },
        {
            "name": "Austin Ramsey",
            "title": "Founder & Chief Box Crusher, Pointech",
            "description": "Austin spearheaded youth communications and digital storytelling during his time on the team. His award-winning StoryMaps helped set a national tone for youth GIS. Today, he leads Pointech, LLC and serves on our Board of Directors.",
            "linkedin_url": None,
            "member_type": "alumni",
            "year": "Youth Outreach & StoryMap Design, 2017"
        }
    ]
    
    # Add all members
    all_members = board_members + alumni_members
    
    print("Adding initial team members to database...")
    
    for member in all_members:
        try:
            cloud_storage.create_team_member(
                name=member["name"],
                title=member["title"],
                description=member["description"],
                linkedin_url=member["linkedin_url"],
                member_type=member["member_type"],
                year=member["year"],
                created_by=None  # System created
            )
            print(f"✓ Added: {member['name']} ({member['member_type']})")
        except Exception as e:
            print(f"✗ Error adding {member['name']}: {e}")
    
    print("\nInitial team members added successfully!")

if __name__ == "__main__":
    add_initial_team_members() 