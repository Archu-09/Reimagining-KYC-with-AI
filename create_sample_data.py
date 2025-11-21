#!/usr/bin/env python3
"""
Sample data generator for KYC admin panel
Creates sample verification jobs and records for testing
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
import json
import random

# Add the backend directory to path
sys.path.append('/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend')

# Database connection
DB_PATH = '/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend/kyc_database.db'

def create_sample_data():
    """Create sample KYC records and verification jobs"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kyc_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            document_type TEXT,
            document_number TEXT,
            score REAL,
            risk_level TEXT,
            meta TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT DEFAULT 'pending',
            callback_url TEXT,
            result TEXT,
            created_at TEXT,
            updated_at TEXT,
            manual_review TEXT,
            reviewer TEXT,
            review_comments TEXT
        )
    ''')
    
    # Sample data
    sample_records = [
        {
            'name': 'John Smith',
            'document_type': 'passport',
            'document_number': 'P123456789',
            'score': 0.95,
            'risk_level': 'LOW',
            'meta': json.dumps({
                'face_match_score': 0.97,
                'document_quality': 'HIGH',
                'liveness_passed': True,
                'biometric_confidence': 0.95
            })
        },
        {
            'name': 'Sarah Johnson',
            'document_type': 'drivers_license',
            'document_number': 'DL987654321',
            'score': 0.88,
            'risk_level': 'MEDIUM',
            'meta': json.dumps({
                'face_match_score': 0.82,
                'document_quality': 'MEDIUM',
                'liveness_passed': True,
                'biometric_confidence': 0.88
            })
        },
        {
            'name': 'Michael Chen',
            'document_type': 'aadhaar',
            'document_number': 'AADR123456789012',
            'score': 0.72,
            'risk_level': 'HIGH',
            'meta': json.dumps({
                'face_match_score': 0.65,
                'document_quality': 'LOW',
                'liveness_passed': False,
                'biometric_confidence': 0.72
            })
        },
        {
            'name': 'Emily Davis',
            'document_type': 'passport',
            'document_number': 'P987654321',
            'score': 0.93,
            'risk_level': 'LOW',
            'meta': json.dumps({
                'face_match_score': 0.94,
                'document_quality': 'HIGH',
                'liveness_passed': True,
                'biometric_confidence': 0.93
            })
        },
        {
            'name': 'Robert Wilson',
            'document_type': 'pan_card',
            'document_number': 'PANR123456C',
            'score': 0.79,
            'risk_level': 'MEDIUM',
            'meta': json.dumps({
                'face_match_score': 0.81,
                'document_quality': 'MEDIUM',
                'liveness_passed': True,
                'biometric_confidence': 0.79
            })
        }
    ]
    
    # Clear existing data
    cursor.execute('DELETE FROM kyc_records')
    cursor.execute('DELETE FROM verification_jobs')
    
    # Insert KYC records
    for record in sample_records:
        cursor.execute('''
            INSERT INTO kyc_records (name, document_type, document_number, score, risk_level, meta)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (record['name'], record['document_type'], record['document_number'], 
              record['score'], record['risk_level'], record['meta']))
    
    # Create verification jobs based on the records
    statuses = ['pending', 'processing', 'completed', 'failed', 'approved', 'rejected']
    
    for i, record in enumerate(sample_records):
        base_time = datetime.now() - timedelta(days=random.randint(1, 30))
        status = random.choice(statuses)
        
        result_data = {
            'kyc_record_id': i + 1,
            'verification_status': status,
            'confidence_score': record['score'],
            'risk_assessment': record['risk_level'],
            'document_analysis': json.loads(record['meta']),
            'processing_time': random.randint(5, 45),
            'flags': []
        }
        
        if record['score'] < 0.8:
            result_data['flags'].append('LOW_CONFIDENCE')
        if json.loads(record['meta'])['liveness_passed'] == False:
            result_data['flags'].append('LIVENESS_FAILED')
        
        cursor.execute('''
            INSERT INTO verification_jobs 
            (status, result, created_at, updated_at, manual_review, reviewer, review_comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            status,
            json.dumps(result_data),
            base_time.isoformat(),
            (base_time + timedelta(minutes=random.randint(5, 120))).isoformat(),
            'true' if status in ['approved', 'rejected'] else 'false',
            'admin' if status in ['approved', 'rejected'] else None,
            f'Reviewed and {status}' if status in ['approved', 'rejected'] else None
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data created successfully!")
    print(f"📊 Created {len(sample_records)} KYC records")
    print(f"📋 Created {len(sample_records)} verification jobs")
    print("🎯 Admin panel is now populated with test data")

if __name__ == "__main__":
    create_sample_data()
