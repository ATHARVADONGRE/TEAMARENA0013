"""
Government Scheme Awareness Portal - Flask Backend
Hackathon Demo Application
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'govt_scheme_portal_2024'
CORS(app)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Database initialization
DATABASE = 'database.db'

def init_db():
    """Initialize database with schema and sample data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create schemes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_hi TEXT,
            name_mr TEXT,
            category TEXT NOT NULL,
            description TEXT,
            description_hi TEXT,
            description_mr TEXT,
            benefits TEXT,
            benefits_hi TEXT,
            benefits_mr TEXT,
            eligibility TEXT,
            eligibility_hi TEXT,
            eligibility_mr TEXT,
            documents TEXT,
            documents_hi TEXT,
            documents_mr TEXT,
            how_to_apply TEXT,
            how_to_apply_hi TEXT,
            how_to_apply_mr TEXT,
            official_link TEXT,
            deadline TEXT,
            min_age INTEGER,
            max_age INTEGER,
            gender TEXT,
            income_range TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create saved_schemes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_session TEXT,
            scheme_id INTEGER,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scheme_id) REFERENCES schemes(id)
        )
    ''')
    
    # Create reminders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_session TEXT,
            scheme_id INTEGER,
            reminder_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scheme_id) REFERENCES schemes(id)
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            category TEXT,
            age INTEGER,
            income TEXT,
            state TEXT,
            district TEXT,
            phone TEXT,
            sms_notifications INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add state and region columns to schemes table if they don't exist
    try:
        cursor.execute("ALTER TABLE schemes ADD COLUMN state TEXT")
        cursor.execute("ALTER TABLE schemes ADD COLUMN region TEXT")
    except:
        pass  # Columns already exist
    
    # Create notifications table for SMS history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone TEXT,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Check if schemes exist
    cursor.execute('SELECT COUNT(*) FROM schemes')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert sample schemes data
        schemes_data = [
            # Farmer Schemes
            ('PM Kisan Samman Nidhi', 'प्रधानमंत्री किसान सम्मान निधि', 'पीएम किसान सामन निधी',
             'farmer', 
             'Direct income support to farmer families',
             'किसान परिवारों को प्रत्यक्ष आय सहायता',
             'शेतकरी कुटुंबाला प्रत्यक्ष उत्पन्न मदत',
             '₹6000 per year direct to bank account',
             'बैंक खाते में सालाना ₹6000',
             'वर्षातून ₹6000 थेट बँक खात्यात',
             'Must be a farmer with land ownership',
             'भूमि स्वामित्व वाला किसान होना चाहिए',
             'जमिनीचा मालक असलेला शेतकरी असणे आवश्यक',
             'Aadhaar Card, Land Records, Bank Account',
             'आधार कार्ड, भूमि रिकॉर्ड, बैंक खाता',
             'आधार कार्ड, जमीन रेकॉर्ड्स, बँक खाते',
             '1. Visit nearest CSC\n2. Register with Aadhaar\n3. Submit land records\n4. Get confirmation',
             '1. निकटतम CSC जाएं\n2. आधार से पंजीकरण करें\n3. भूमि रिकॉर्ड जमा करें\n4. पुष्टि प्राप्त करें',
             '1. जवळच्या CSC ला भेट द्या\n2. आधारसह नोंदणी करा\n3. जमीन रेकॉर्ड सबमिट करा\n4. पुष्टी मिळवा',
             'https://pmkisan.gov.in',
             '2024-12-31', 18, 80, 'All', 'All'),
            
            ('Pradhan Mantri Fasal Bima Yojana', 'प्रधानमंत्री फसल बीमा योजना', 'प्रधानमंत्री पीक विमा योजना',
             'farmer',
             'Crop insurance scheme for farmers',
             'किसानों के लिए फसल बीमा योजना',
             'शेतकऱ्यांसाठी पीक विमा योजना',
             'Low premium crop insurance coverage',
             'कम प्रीमियम फसल बीमा कवरेज',
             'कम प्रीमियम पीक विमा व्याप्त',
             'Any farmer including sharecroppers',
             'किसी भी किसान जिसमें बटाईदार शामिल हैं',
             'कोणताही शेतकरी ज्यात शेअरक्रॉपर समाविष्ट',
             'Aadhaar Card, Land Records, Bank Account',
             'आधार कार्ड, भूमि रिकॉर्ड, बैंक खाता',
             'आधार कार्ड, जमीन रेकॉर्ड्स, बँक खाते',
             '1. Visit bank or CSC\n2. Fill application form\n3. Pay premium\n4. Get policy',
             '1. बैंक या CSC जाएं\n2. आवेदन पत्र भरें\n3. प्रीमियम का भुगतान करें\n4. पॉलिसी प्राप्त करें',
             '1. बँक किंवा CSC ला भेट द्या\n2. अर्ज भरा\n3. प्रीमियम भरा\n4. पॉलिसी मिळवा',
             'https://pmfby.gov.in',
             '2025-11-30', 18, 80, 'All', 'All'),
            
            # Housing Schemes
            ('Pradhan Mantri Awas Yojana (Rural)', 'प्रधानमंत्री आवास योजना (ग्रामीण)', 'प्रधानमंत्री आवास योजना (ग्रामीण)',
             'housing',
             'Housing for all rural poor families',
             'सभी गरीब ग्रामीण परिवारों के लिए आवास',
             'सर्व गरीब ग्रामीण कुटुंबांसाठी घर',
             '₹1.20 lakh in plains, ₹1.30 lakh in hilly areas',
             'मैदानों में ₹1.20 लाख, पहाड़ी क्षेत्रों में ₹1.30 लाख',
             'पठारात ₹1.20 लाख, डोंगराळ भागात ₹1.30 लाख',
             'Rural household without pucca house',
             'पक्के घर के बिना ग्रामीण परिवार',
             'पक्के घराशिवाय ग्रामीण कुटुंब',
             'Aadhaar Card, Bank Account, Land Records',
             'आधार कार्ड, बैंक खाता, भूमि रिकॉर्ड',
             'आधार कार्ड, बँक खाते, जमीन रेकॉर्ड्स',
             '1. Apply at Gram Panchayat\n2. Wait for verification\n3. Get approval\n4. Construction begins',
             '1. ग्राम पंचायत में आवेदन करें\n2. सत्यापन की प्रतीक्षा करें\n3. अनुमोदन प्राप्त करें\n4. निर्माण शुरू होता है',
             '1. ग्राम पंचायतमध्ये अर्ज करा\n2. पडताळणीची वाट पाहा\n3. मंजूरी मिळवा\n4. बांधकाम सुरू होते',
             'https://pmayg.nic.in',
             '2024-12-31', 18, 60, 'All', 'Below 3 Lakh'),
            
            ('Pradhan Mantri Awas Yojana (Urban)', 'प्रधानमंत्री आवास योजना (शहरी)', 'प्रधानमंत्री आवास योजना (शहरी)',
             'housing',
             'Affordable housing for urban poor',
             'शहरी गरीबों के लिए किफायती आवास',
             'शहरी गरीबांसाठी स्वस्त घर',
             'Interest subsidy on home loan',
             'होम लोन पर ब्याज सब्सिडी',
             'होम लोनवर व्याज सबसिडी',
             'Urban poor with income up to ₹18 lakh',
             '₹18 लाख तक की आय वाले शहरी गरीब',
             '₹18 लाखापर्यंत उत्पन्न असलेले शहरी गरीब',
             'Aadhaar Card, Bank Account, Income Certificate',
             'आधार कार्ड, बैंक खाता, आय प्रमाण पत्र',
             'आधार कार्ड, बँक खाते, उत्पन्न प्रमाणपत्र',
             '1. Apply online at PMAY portal\n2. Submit documents\n3. Wait for verification\n4. Get subsidy',
             '1. PMAY पोर्टल पर ऑनलाइन आवेदन करें\n2. दस्तावेज जमा करें\n3. सत्यापन की प्रतीक्षा करें\n4. सब्सिडी प्राप्त करें',
             '1. PMAY पोर्टलवर ऑनलाइन अर्ज करा\n2. कागदपत्रे सबमिट करा\n3. पडताळणीची वाट पाहा\n4. सबसिडी मिळवा',
             'https://pmaymis.gov.in',
             '2024-12-31', 18, 60, 'All', 'Below 18 Lakh'),
            
            # Employment Schemes
            ('MGNREGA', 'महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम', 'महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार हमी कायदा',
             'employment',
             '100 days guaranteed wage employment',
             '100 दिन की गारंटीड वेतन रोजगार',
             '100 दिवस हमीत वेतन रोजगार',
             'Minimum wages guaranteed, job cards',
             'न्यूनतम वेतन गारंटी, जॉब कार्ड',
             'किमान वेतन हमी, नोकरी कार्ड',
             'Adult members of rural households',
             'ग्रामीण परिवार के वयस्क सदस्य',
             'ग्रामीण कुटुंबातील प्रौढ सदस्य',
             'Aadhaar Card, Bank Account, Photo',
             'आधार कार्ड, बैंक खाता, फोटो',
             'आधार कार्ड, बँक खाते, फोटो',
             '1. Apply at Gram Panchayat\n2. Get Job Card\n3. Demand work in writing\n4. Work provided within 15 days',
             '1. ग्राम पंचायत में आवेदन करें\n2. जॉब कार्ड प्राप्त करें\n3. लिखित में काम की मांग करें\n4. 15 दिनों के भीतर काम मिलता है',
             '1. ग्राम पंचायतमध्ये अर्ज करा\n2. नोकरी कार्ड मिळवा\n3. लेखी कामाची मागणी करा\n4. 15 दिवसांत काम मिळते',
             'https://nrega.nic.in',
             '2024-12-31', 18, 60, 'All', 'All'),
            
            ('Pradhan Mantri Mudra Yojana', 'प्रधानमंत्री मुद्रा योजना', 'प्रधानमंत्री मुद्रा योजना',
             'employment',
             'Loans up to ₹10 lakh for small businesses',
             'छोटे व्यवसायों के लिए ₹10 लाख तक का ऋण',
             'लहान व्यवसायांसाठी ₹10 लाखापर्यंत कर्ज',
             'No collateral required, easy approval',
             'कोई गारंटी नहीं, आसान अनुमोदन',
             'कोणतीही जमानत नाही, सुलभ मंजूरी',
             'Any Indian citizen with business plan',
             'व्यवसाय योजना वाला कोई भी भारतीय नागरिक',
             'व्यवसाय योजना असलेला कोणताही भारतीय नागरिक',
             'Aadhaar Card, Business Plan, Address Proof',
             'आधार कार्ड, व्यवसाय योजना, पते का प्रमाण',
             'आधार कार्ड, व्यवसाय योजना, पत्त्याचा पुरावा',
             '1. Prepare business plan\n2. Apply at bank\n3. Submit documents\n4. Get loan',
             '1. व्यवसाय योजना तैयार करें\n2. बैंक में आवेदन करें\n3. दस्तावेज जमा करें\n4. ऋण प्राप्त करें',
             '1. व्यवसाय योजना तयार करा\n2. बँकमध्ये अर्ज करा\n3. कागदपत्रे सबमिट करा\n4. कर्ज मिळवा',
             'https://mudra.org.in',
             '2024-12-31', 18, 80, 'All', 'All'),
            
            ('E-Shram Portal', 'ई-श्रम पोर्टल', 'ई-श्रम पोर्टल',
             'employment',
             'National database for unorganized workers',
             'असंगठित श्रमिकों के लिए राष्ट्रीय डेटाबेस',
             'असंगठित कामगारांसाठी राष्ट्रीय डेटाबेस',
             'Free registration, insurance benefits',
             'मुफ्त पंजीकरण, बीमा लाभ',
             'विनामूल्य नोंदणी, विमा लाभ',
             'Unorganized sector workers',
             'असंगठित क्षेत्र के श्रमिक',
             'असंगठित क्षेत्रातील कामगार',
             'Aadhaar Card, Bank Account, Photo',
             'आधार कार्ड, बैंक खाता, फोटो',
             'आधार कार्ड, बँक खाते, फोटो',
             '1. Visit E-Shram portal\n2. Register with Aadhaar\n3. Fill details\n4. Get UAN card',
             '1. ई-श्रम पोर्टल पर जाएं\n2. आधार से पंजीकरण करें\n3. विवरण भरें\n4. UAN कार्ड प्राप्त करें',
             '1. ई-श्रम पोर्टलवर जा\n2. आधारसह नोंदणी करा\n3. तपशील भरा\n4. UAN कार्ड मिळवा',
             'https://eshram.gov.in',
             '2024-12-31', 16, 60, 'All', 'All'),
            
            # Health Schemes
            ('Ayushman Bharat PM-JAY', 'आयुष्मान भारत PM-JAY', 'आयुष्मान भारत PM-JAY',
             'health',
             'Health insurance coverage of ₹5 lakh per family',
             'प्रति परिवार ₹5 लाख का स्वास्थ्य बीमा कवरेज',
             'प्रति कुटुंब ₹5 लाख स्वास्थ्य विमा व्याप्त',
             'Free treatment at empaneled hospitals',
             'सूचीबद्ध अस्पतालों में मुफ्त इलाज',
             'यादीतल्या रुग्णालयात विनामूल्य उपचार',
             'SECC identified families, no income limit',
             'SECC की पहचान वाले परिवार, कोई आय सीमा नहीं',
             'SECC ओळखलेली कुटुंबे, उत्पन्न मर्यादा नाही',
             'Aadhaar Card, Ration Card, SECC data',
             'आधार कार्ड, राशन कार्ड, SECC डेटा',
             'आधार कार्ड, रेशन कार्ड, SECC डेटा',
             '1. Visit empaneled hospital\n2. Get Ayushman card\n3. Avail free treatment',
             '1. सूचीबद्ध अस्पताल जाएं\n2. आयुष्मान कार्ड प्राप्त करें\n3. मुफ्त इलाज प्राप्त करें',
             '1. यादीतल्या रुग्णालयात जा\n2. आयुष्मान कार्ड मिळवा\n3. विनामूल्य उपचार घ्या',
             'https://pmjay.gov.in',
             '2024-12-31', 0, 80, 'All', 'All'),
            
            ('Pradhan Mantri Suraksha Bima Yojana', 'प्रधानमंत्री सुरक्षा बीमा योजना', 'प्रधानमंत्री सुरक्षा विमा योजना',
             'health',
             'Accident insurance cover of ₹2 lakh',
             '₹2 लाख का दुर्घटना बीमा कवर',
             '₹2 लाखाचा अपघात विमा',
             'Premium only ₹20 per year',
             'सालाना केवल ₹20 प्रीमियम',
             'वर्षातून फक्त ₹20 प्रीमियम',
             'Age 18-70 years with bank account',
             '18-70 वर्ष का बैंक खाता',
             '18-70 वर्ष बँक खाते असणे आवश्यक',
             'Aadhaar Card, Bank Account',
             'आधार कार्ड, बैंक खाता',
             'आधार कार्ड, बँक खाते',
             '1. Visit bank\n2. Fill form\n3. Pay premium\n4. Get certificate',
             '1. बैंक जाएं\n2. फॉर्म भरें\n3. प्रीमियम भुगतान करें\n4. प्रमाण पत्र प्राप्त करें',
             '1. बँकला भेट द्या\n2. फॉर्म भरा\n3. प्रीमियम भरा\n4. प्रमाणपत्र मिळवा',
             'https://pmjjby.gov.in',
             '2024-12-31', 18, 70, 'All', 'All'),
            
            # Student Schemes
            ('National Scholarship Portal', 'राष्ट्रीय छात्रवृत्ति पोर्टल', 'राष्ट्रीय शिष्यवृत्ती पोर्टल',
             'student',
             'Various scholarships for students',
             'छात्रों के लिए विभिन्न छात्रवृत्तियां',
             'विद्यार्थ्यांसाठी विविध शिष्यवृत्त्या',
             'Scholarship amount ₹1000 to ₹75000',
             '₹1000 से ₹75000 तक छात्रवृत्ति राशि',
             '₹1000 ते ₹75000 शिष्यवृत्ती रक्कम',
             'Students studying in India, income criteria',
             'भारत में पढ़ने वाले छात्र, आय मानदंड',
             'भारतात शिकणारे विद्यार्थी, उत्पन्न निकष',
             'Aadhaar Card, Bank Account, Income Certificate, Marksheet',
             'आधार कार्ड, बैंक खाता, आय प्रमाण पत्र, अंकपत्र',
             'आधार कार्ड, बँक खाते, उत्पन्न प्रमाणपत्र, गुणपत्रक',
             '1. Visit NSP portal\n2. Register\n3. Fill application\n4. Submit documents',
             '1. NSP पोर्टल पर जाएं\n2. पंजीकरण करें\n3. आवेदन भरें\n4. दस्तावेज जमा करें',
             '1. NSP पोर्टलवर जा\n2. नोंदणी करा\n3. अर्ज भरा\n4. कागदपत्रे सबमिट करा',
             'https://scholarships.gov.in',
             '2024-10-31', 5, 35, 'All', 'Below 8 Lakh'),
            
            ('PM YASASVI Scholarship', 'PM YASASVI छात्रवृत्ति', 'PM YASASVI शिष्यवृत्ती',
             'student',
             'Scholarship for OBC, EBC, DNT students',
             'OBC, EBC, DNT छात्रों के लिए छात्रवृत्ति',
             'OBC, EBC, DNT विद्यार्थ्यांसाठी शिष्यवृत्ती',
             '₹75000 per year for Class 11-12',
             'कक्षा 11-12 के लिए सालाना ₹75000',
             'इयत्ता 11-12 साठी वर्षातून ₹75000',
             'OBC, EBC, DNT category students',
             'OBC, EBC, DNT श्रेणी के छात्र',
             'OBC, EBC, DNT श्रेणीतील विद्यार्थी',
             'Aadhaar Card, Bank Account, Caste Certificate, Income Certificate',
             'आधार कार्ड, बैंक खाता, जात प्रमाण पत्र, आय प्रमाण पत्र',
             'आधार कार्ड, बँक खाते, जात प्रमाणपत्र, उत्पन्न प्रमाणपत्र',
             '1. Visit NSP or state portal\n2. Apply as YASASVI\n3. Submit documents\n4. Get scholarship',
             '1. NSP या राज्य पोर्टल पर जाएं\n2. YASASVI के रूप में आवेदन करें\n3. दस्तावेज जमा करें\n4. छात्रवृत्ति प्राप्त करें',
             '1. NSP किंवा राज्य पोर्टलवर जा\n2. YASASVI म्हणून अर्ज करा\n3. कागदपत्रे सबमिट करा\n4. शिष्यवृत्ती मिळवा',
             'https://yet.nta.ac.in',
             '2024-10-31', 13, 25, 'All', 'Below 2.5 Lakh'),
            
            # Women Schemes
            ('Beti Bachao Beti Padhao', 'बेटी बचाओ बेटी पढ़ाओ', 'मुली वाचवा, मुली शिकवा',
             'women',
             'Save girl child, educate girl child',
             'बच्ची को बचाएं, बच्ची को पढ़ाएं',
             'मुलीचे संरक्षण करा, मुलीला शिकवा',
             'Awareness programs, welfare schemes',
             'जागरूकता कार्यक्रम, कल्याण योजनाएं',
             'जागरूकता कार्यक्रम, कल्याण योजना',
             'Girl child and women',
             'बच्ची और महिलाएं',
             'मुलगी आणि महिला',
             'Aadhaar Card, Birth Certificate',
             'आधार कार्ड, जन्म प्रमाण पत्र',
             'आधार कार्ड, जन्म प्रमाणपत्र',
             '1. Visit Anganwadi center\n2. Get benefits\n3. Enroll girl child',
             '1. आंगनवाडी केंद्र जाएं\n2. लाभ प्राप्त करें\n3. बच्ची को दर्ज करें',
             '1. आंगणवाडी केंद्रात जा\n2. लाभ मिळवा\n3. मुलीची नोंदणी करा',
             'https://wcd.nic.in',
             '2024-12-31', 0, 80, 'Female', 'All'),
            
            ('Sukanya Samriddhi Yojana', 'सुकन्या समृद्धि योजना', 'सुकन्या समृद्धी योजना',
             'women',
             'Savings scheme for girl child',
             'बच्ची के लिए बचत योजना',
             'मुलीसाठी बचत योजना',
             'High interest rate, tax benefits',
             'उच्च ब्याज दर, कर लाभ',
             'उच्च व्याजदर, कर लाभ',
             'Girl child below 10 years',
             '10 वर्ष से कम उम्र की बच्ची',
             '10 वर्षाखालील मुलगी',
             'Girl child birth certificate, Parent Aadhaar',
             'बच्ची का जन्म प्रमाण पत्र, माता-पिता का आधार',
             'मुलीचा जन्म प्रमाणपत्र, पालकांचा आधार',
             '1. Visit post office or bank\n2. Open account for girl\n3. Deposit regularly',
             '1. डाकघर या बैंक जाएं\n2. बच्ची के लिए खाता खोलें\n3. नियमित जमा करें',
             '1. पोस्ट ऑफिस किंवा बँकला भेट द्या\n2. मुलीसाठी खाते उघडा\n3. नियमित पैसे ठेवा',
             'https://indiapost.gov.in',
             '2024-12-31', 0, 10, 'Female', 'All'),
            
            ('Stand Up India', 'स्टैंड अप इंडिया', 'स्टैंड अप इंडिया',
             'women',
             'Loans for SC/ST and women entrepreneurs',
             'SC/ST और महिला उद्यमियों के लिए ऋण',
             'SC/ST आणि महिला उद्योजकांसाठी कर्ज',
             'Loan ₹10 lakh to ₹1 crore',
             '₹10 लाख से ₹1 करोड़ तक ऋण',
             '₹10 लाख ते ₹1 कोटी कर्ज',
             'SC/ST and/or women entrepreneurs',
             'SC/ST और/या महिला उद्यमी',
             'SC/ST आणि/किंवा महिला उद्योजक',
             'Aadhaar Card, Business Plan, Category Certificate',
             'आधार कार्ड, व्यवसाय योजना, श्रेणी प्रमाण पत्र',
             'आधार कार्ड, व्यवसाय योजना, श्रेणी प्रमाणपत्र',
             '1. Apply at bank\n2. Submit business plan\n3. Get loan',
             '1. बैंक में आवेदन करें\n2. व्यवसाय योजना जमा करें\n3. ऋण प्राप्त करें',
             '1. बँकमध्ये अर्ज करा\n2. व्यवसाय योजना सबमिट करा\n3. कर्ज मिळवा',
             'https://standupmitra.in',
             '2024-12-31', 18, 80, 'Female', 'All'),
            
            ('Pradhan Mantri Jan Dhan Yojana', 'प्रधानमंत्री जन धन योजना', 'प्रधानमंत्री जन धन योजना',
             'other',
             'Zero balance bank account for all',
             'सभी के लिए शून्य बैलेंस बैंक खाता',
             'सर्वांसाठी शून्य बैलेंस बँक खाते',
             'Free RuPay debit card, insurance cover',
             'मुफ्त RuPay डेबिट कार्ड, बीमा कवर',
             'मोफत RuPay डेबिट कार्ड, विमा व्याप्त',
             'Any Indian citizen without bank account',
             'बैंक खाता नहीं होने वाला कोई भी भारतीय नागरिक',
             'बँक खाता नसलेला कोणताही भारतीय नागरिक',
             'Aadhaar Card, Photo',
             'आधार कार्ड, फोटो',
             'आधार कार्ड, फोटो',
             '1. Visit nearest bank\n2. Fill account form\n3. Get zero balance account',
             '1. निकटतम बैंक जाएं\n2. खाता फॉर्म भरें\n3. शून्य बैलेंस खाता प्राप्त करें',
             '1. जवळच्या बँकला भेट द्या\n2. खाते फॉर्म भरा\n3. शून्य बैलेंस खाते मिळवा',
             'https://pmjdy.gov.in',
             '2024-12-31', 10, 80, 'All', 'All'),
            
            ('Atal Pension Yojana', 'अटल पेंशन योजना', 'अटल पेंशन योजना',
             'other',
             'Pension scheme for unorganized sector',
             'असंगठित क्षेत्र के लिए पेंशन योजना',
             'असंगठित क्षेत्रासाठी पेंशन योजना',
             'Guaranteed pension ₹1000 to ₹5000',
             'गारंटीड पेंशन ₹1000 से ₹5000',
             'हमीत पेंशन ₹1000 ते ₹5000',
             'Age 18-40 years, must have bank account',
             '18-40 वर्ष, बैंक खाता होना चाहिए',
             '18-40 वर्ष, बँक खाता असणे आवश्यक',
             'Aadhaar Card, Bank Account',
             'आधार कार्ड, बैंक खाता',
             'आधार कार्ड, बँक खाते',
             '1. Visit bank\n2. Fill APY form\n3. Choose pension amount\n4. Start contributing',
             '1. बैंक जाएं\n2. APY फॉर्म भरें\n3. पेंशन राशि चुनें\n4. योगदान शुरू करें',
             '1. बँकला भेट द्या\n2. APY फॉर्म भरा\n3. पेंशन रक्कम निवडा\n4. योगदान सुरू करा',
             'https://npscra.nsdl.co.in',
             '2024-12-31', 18, 40, 'All', 'Below 7.5 Lakh'),
        ]
        
        cursor.executemany('''
            INSERT INTO schemes (name, name_hi, name_mr, category, description, description_hi, description_mr,
                                benefits, benefits_hi, benefits_mr, eligibility, eligibility_hi, eligibility_mr,
                                documents, documents_hi, documents_mr, how_to_apply, how_to_apply_hi, how_to_apply_mr,
                                official_link, deadline, min_age, max_age, gender, income_range)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', schemes_data)
        
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def fetch_live_schemes_from_api():
    """Fetch live schemes from Government of India Open Data API"""
    import requests
    
    print("Fetching live schemes from Government API...")
    
    # Try data.gov.in API for schemes
    try:
        # National Data Portal API - try fetching schemes dataset
        url = "https://api.data.gov.in/catalog/records"
        params = {
            "api-key": "demo",  # Replace with actual API key for production
            "format": "json",
            "filters[domain]": "welfare"
        }
        
        # Since we can't use real API key, we'll use mock data that simulates live API
        # For production, register at https://data.gov.in to get free API key
        live_schemes = get_mock_live_schemes()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get existing scheme names
        cursor.execute("SELECT name FROM schemes")
        existing_names = {row[0] for row in cursor.fetchall()}
        
        # Insert new schemes that don't exist
        new_count = 0
        for scheme in live_schemes:
            if scheme['name'] not in existing_names:
                cursor.execute('''
                    INSERT INTO schemes (name, name_hi, name_mr, category, description, description_hi, description_mr,
                        benefits, benefits_hi, benefits_mr, eligibility, eligibility_hi, eligibility_mr,
                        documents, documents_hi, documents_mr, how_to_apply, how_to_apply_hi, how_to_apply_mr,
                        official_link, deadline, min_age, max_age, gender, income_range, state, region)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scheme['name'], scheme.get('name_hi', ''), scheme.get('name_mr', ''),
                    scheme['category'], scheme['description'], scheme.get('description_hi', ''), scheme.get('description_mr', ''),
                    scheme['benefits'], scheme.get('benefits_hi', ''), scheme.get('benefits_mr', ''),
                    scheme['eligibility'], scheme.get('eligibility_hi', ''), scheme.get('eligibility_mr', ''),
                    scheme['documents'], scheme.get('documents_hi', ''), scheme.get('documents_mr', ''),
                    scheme['how_to_apply'], scheme.get('how_to_apply_hi', ''), scheme.get('how_to_apply_mr', ''),
                    scheme['official_link'], scheme.get('deadline', ''),
                    scheme.get('min_age', 18), scheme.get('max_age', 80),
                    scheme.get('gender', 'All'), scheme.get('income_range', 'All'),
                    scheme.get('state', 'All'), scheme.get('region', 'All')
                ))
                new_count += 1
        
        conn.commit()
        conn.close()
        
        if new_count > 0:
            print(f"✓ Added {new_count} new live schemes from government data!")
        else:
            print("✓ All schemes already up to date!")
            
    except Exception as e:
        print(f"Note: Could not fetch live data: {e}")
        print("Using offline scheme database...")

def get_mock_live_schemes():
    """Additional real government schemes (simulating live API data)"""
    return [
        # Maharashtra State Schemes
        {
            'name': 'Maharashtra State Pension Scheme',
            'name_hi': 'महाराष्ट्र राज्य पेंशन योजना',
            'name_mr': 'महाराष्ट्र राज्य पेंशन योजना',
            'category': 'other',
            'description': 'Monthly pension for senior citizens, widow, and disabled persons',
            'description_hi': 'वरिष्ठ नागरिक, विधवा और विकलांग व्यक्तियों के लिए मासिक पेंशन',
            'description_mr': 'वयोवृद्ध, विधवा आणि अपंग व्यक्तींसाठी मासिक पेंशन',
            'benefits': '₹600-₹3000 per month depending on category',
            'benefits_hi': 'श्रेणी के अनुसार ₹600-₹3000 प्रति माह',
            'benefits_mr': 'श्रेणीनुसार ₹600-₹3000 मासिक',
            'eligibility': 'Age 65+, resident of Maharashtra, BPL family',
            'eligibility_hi': '65+ वर्ष, महाराष्ट्र के निवासी, BPL परिवार',
            'eligibility_mr': 'वय 65+, महाराष्ट्रातील रहिवासी, BPL कुटुंब',
            'documents': 'Aadhaar, Ration Card, Age Proof, Bank Account, BPL Card',
            'documents_hi': 'आधार, राशन कार्ड, आयु प्रमाण, बैंक खाता, BPL कार्ड',
            'documents_mr': 'आधार, रेशन कार्ड, वयाचा पुरावा, बँक खाते, BPL कार्ड',
            'how_to_apply': '1. Visit Taluka Office\n2. Fill pension form\n3. Submit documents\n4. Get pension book',
            'how_to_apply_hi': '1. तहसील कार्यालय जाएं\n2. पेंशन फॉर्म भरें\n3. दस्तावेज जमा करें\n4. पेंशन बुक प्राप्त करें',
            'how_to_apply_mr': '1. तालुका कार्यालयात जा\n2. पेंशन फॉर्म भरा\n3. कागदपत्रे सबमिट करा\n4. पेंशन बुक मिळवा',
            'official_link': 'https://maharashtra.gov.in',
            'deadline': '2024-12-31',
            'min_age': 65,
            'max_age': 100,
            'gender': 'All',
            'income_range': 'Below 3 Lakh',
            'state': 'MH',
            'region': 'All'
        },
        {
            'name': 'Majhi Kanya Bhagyashree',
            'name_hi': 'मेरी कन्या भाग्यश्री',
            'name_mr': 'माझी कन्या भाग्यश्री',
            'category': 'women',
            'description': 'Financial assistance for girl child from BPL families',
            'description_hi': 'BPL परिवारों की बच्ची के लिए वित्तीय सहायता',
            'description_mr': 'BPL कुटुंबातील मुलीसाठी आर्थिक मदत',
            'benefits': '₹5000-₹100000 per year for education',
            'benefits_hi': 'शिक्षा के लिए प्रति वर्ष ₹5000-₹100000',
            'benefits_mr': 'शिक्षणासाठी वर्षातून ₹5000-₹100000',
            'eligibility': 'Girl child from BPL family, age 0-18 years',
            'eligibility_hi': 'BPL परिवार की बच्ची, आयु 0-18 वर्ष',
            'eligibility_mr': 'BPL कुटुंबातील मुलगी, वय 0-18 वर्ष',
            'documents': 'Aadhaar, Birth Certificate, BPL Card, Bank Account',
            'documents_hi': 'आधार, जन्म प्रमाण पत्र, BPL कार्ड, बैंक खाता',
            'documents_mr': 'आधार, जन्म प्रमाणपत्र, BPL कार्ड, बँक खाते',
            'how_to_apply': '1. Apply online at Aaple Sarkar portal\n2. Upload documents\n3. Verification\n4. Get benefit',
            'how_to_apply_hi': '1. आपले सरकार पोर्टल पर ऑनलाइन आवेदन करें\n2. दस्तावेज अपलोड करें\n3. सत्यापन\n4. लाभ प्राप्त करें',
            'how_to_apply_mr': '1. आपले सरकार पोर्टलवर ऑनलाइन अर्ज करा\n2. कागदपत्रे अपलोड करा\n3. पडताळणी\n4. लाभ मिळवा',
            'official_link': 'https://majhikanyabhagyashree.maharashtra.gov.in',
            'deadline': '2024-12-31',
            'min_age': 0,
            'max_age': 18,
            'gender': 'Female',
            'income_range': 'Below 3 Lakh',
            'state': 'MH',
            'region': 'All'
        },
        # Delhi Schemes
        {
            'name': 'Delhi Ladli Scheme',
            'name_hi': 'दिल्ली लाडली योजना',
            'name_mr': 'दिल्ली लाडली योजना',
            'category': 'women',
            'description': 'Financial assistance for girl child in Delhi',
            'description_hi': 'दिल्ली में बच्ची के लिए वित्तीय सहायता',
            'description_mr': 'दिल्लीतील मुलीसाठी आर्थिक मदत',
            'benefits': '₹20000-₹50000 on reaching major age',
            'benefits_hi': 'वयस्क होने पर ₹20000-₹50000',
            'benefits_mr': 'मोठे वयात पोहोचल्यावर ₹20000-₹50000',
            'eligibility': 'Girl child born in Delhi, family income below ₹3 lakh',
            'eligibility_hi': 'दिल्ली में पैदा हुई बच्ची, परिवार की आय ₹3 लाख से कम',
            'eligibility_mr': 'दिल्लीत जन्मलेली मुलगी, कुटुंबाचे उत्पन्न ₹3 लाखाखाली',
            'documents': 'Aadhaar, Birth Certificate, Residence Proof, Income Certificate',
            'documents_hi': 'आधार, जन्म प्रमाण पत्र, निवास प्रमाण, आय प्रमाण पत्र',
            'documents_mr': 'आधार, जन्म प्रमाणपत्र, रहिवास पुरावा, उत्पन्न प्रमाणपत्र',
            'how_to_apply': '1. Visit Delhi govt portal\n2. Fill application\n3. Submit documents',
            'how_to_apply_hi': '1. दिल्ली सरकार पोर्टल जाएं\n2. आवेदन भरें\n3. दस्तावेज जमा करें',
            'how_to_apply_mr': '1. दिल्ली सरकार पोर्टलवर जा\n2. अर्ज भरा\n3. कागदपत्रे सबमिट करा',
            'official_link': 'https://delhi.gov.in',
            'deadline': '2024-12-31',
            'min_age': 0,
            'max_age': 18,
            'gender': 'Female',
            'income_range': 'Below 3 Lakh',
            'state': 'DL',
            'region': 'All'
        },
        # Karnataka Schemes
        {
            'name': 'Karnataka Bhagyashree Scheme',
            'name_hi': 'कर्नाटक भाग्यश्री योजना',
            'name_mr': 'कर्नाटक भाग्यश्री योजना',
            'category': 'women',
            'description': 'Health insurance for women and girl child',
            'description_hi': 'महिलाओं और बच्ची के लिए स्वास्थ्य बीमा',
            'description_mr': 'महिला आणि मुलीसाठी आरोग्य विमा',
            'benefits': 'Health coverage up to ₹10 lakh',
            'benefits_hi': '₹10 लाख तक का स्वास्थ्य कवरेज',
            'benefits_mr': '₹10 लाखापर्यंत आरोग्य व्याप्त',
            'eligibility': 'Women and girl child from BPL families',
            'eligibility_hi': 'BPL परिवारों की महिलाएं और बच्ची',
            'eligibility_mr': 'BPL कुटुंबातील महिला आणि मुलगी',
            'documents': 'Aadhaar, BPL Card, Bank Account',
            'documents_hi': 'आधार, BPL कार्ड, बैंक खाता',
            'documents_mr': 'आधार, BPL कार्ड, बँक खाते',
            'how_to_apply': '1. Visit CSC or hospital\n2. Enroll in scheme',
            'how_to_apply_hi': '1. CSC या अस्पताल जाएं\n2. योजना में पंजीकरण करें',
            'how_to_apply_mr': '1. CSC किंवा रुग्णालयात जा\n2. योजनेत नोंदणी करा',
            'official_link': 'https://karunadu.karnataka.gov.in',
            'deadline': '2024-12-31',
            'min_age': 0,
            'max_age': 80,
            'gender': 'Female',
            'income_range': 'Below 3 Lakh',
            'state': 'KA',
            'region': 'All'
        },
        # Tamil Nadu Schemes
        {
            'name': 'Tamil Nadu Chief Minister\'s Comprehensive Health Insurance',
            'name_hi': 'तमिल नाडु मुख्यमंत्री व्यापक स्वास्थ्य बीमा',
            'name_mr': 'तामिळनाडु मुख्यमंत्री व्यापक आरोग्य विमा',
            'category': 'health',
            'description': 'Free health treatment for families up to ₹5 lakh',
            'description_hi': '₹5 लाख तक के परिवारों के लिए मुफ्त स्वास्थ्य उपचार',
            'description_mr': '₹5 लाखापर्यंत कुटुंबांसाठी मोफत आरोग्य उपचार',
            'benefits': 'Health coverage up to ₹5 lakh per family',
            'benefits_hi': 'प्रति परिवार ₹5 लाख तक का स्वास्थ्य कवरेज',
            'benefits_mr': 'प्रति कुटुंब ₹5 लाखापर्यंत आरोग्य व्याप्त',
            'eligibility': 'All families in Tamil Nadu',
            'eligibility_hi': 'तमिल नाडु के सभी परिवार',
            'eligibility_mr': 'तामिळनाडूतील सर्व कुटुंबे',
            'documents': 'Aadhaar, Ration Card',
            'documents_hi': 'आधार, राशन कार्ड',
            'documents_mr': 'आधार, रेशन कार्ड',
            'how_to_apply': '1. Visit empaneled hospital\n2. Get health card\n3. Avail treatment',
            'how_to_apply_hi': '1. सूचीबद्ध अस्पताल जाएं\n2. स्वास्थ्य कार्ड प्राप्त करें\n3. उपचार प्राप्त करें',
            'how_to_apply_mr': '1. यादीतल्या रुग्णालयात जा\n2. आरोग्य कार्ड मिळवा\n3. उपचार घ्या',
            'official_link': 'https://www.tn.gov.in',
            'deadline': '2024-12-31',
            'min_age': 0,
            'max_age': 100,
            'gender': 'All',
            'income_range': 'All',
            'state': 'TN',
            'region': 'All'
        },
        # Uttar Pradesh Schemes
        {
            'name': 'UP Kanya Vivah Nikay Yojana',
            'name_hi': 'यूपी कन्या विवाह निकाय योजना',
            'name_mr': 'UP कन्या विवाह निकाय योजना',
            'category': 'women',
            'description': 'Financial assistance for marriage of daughters from poor families',
            'description_hi': 'गरीब परिवारों में बेटी की शादी के लिए वित्तीय सहायता',
            'description_mr': 'गरीब कुटुंबातील मुलीच्या लग्नासाठी आर्थिक मदत',
            'benefits': 'Financial assistance ₹51000 per daughter',
            'benefits_hi': 'प्रति बेटी ₹51000 वित्तीय सहायता',
            'benefits_mr': 'प्रति मुलगी ₹51000 आर्थिक मदत',
            'eligibility': 'BPL families, unmarried daughter above 18 years',
            'eligibility_hi': 'BPL परिवार, 18 वर्ष से अधिक अविवाहित बेटी',
            'eligibility_mr': 'BPL कुटुंब, 18 वर्षावरील अविवाहित मुलगी',
            'documents': 'Aadhaar, BPL Card, Income Certificate, Birth Certificate',
            'documents_hi': 'आधार, BPL कार्ड, आय प्रमाण पत्र, जन्म प्रमाण पत्र',
            'documents_mr': 'आधार, BPL कार्ड, उत्पन्न प्रमाणपत्र, जन्म प्रमाणपत्र',
            'how_to_apply': '1. Apply at Block Development Office\n2. Submit documents\n3. Get benefit',
            'how_to_apply_hi': '1. ब्लॉक विकास कार्यालय में आवेदन करें\n2. दस्तावेज जमा करें\n3. लाभ प्राप्त करें',
            'how_to_apply_mr': '1. ब्लॉक विकास कार्यालयात अर्ज करा\n2. कागदपत्रे सबमिट करा\n3. लाभ मिळवा',
            'official_link': 'https://up.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 40,
            'gender': 'Female',
            'income_range': 'Below 3 Lakh',
            'state': 'UP',
            'region': 'All'
        },
        # West Bengal Schemes
        {
            'name': 'West Bengal Krishak Bandhu',
            'name_hi': 'पश्चिम बंगाल कृषक बंधु',
            'name_mr': 'पश्चिम बंगाल कृषक बंधू',
            'category': 'farmer',
            'description': 'Financial assistance for farmers in West Bengal',
            'description_hi': 'पश्चिम बंगाल में किसानों के लिए वित्तीय सहायता',
            'description_mr': 'पश्चिम बंगालमधील शेतकऱ्यांसाठी आर्थिक मदत',
            'benefits': '₹2000 per year or ₹50000 on death',
            'benefits_hi': 'प्रति वर्ष ₹2000 या मृत्यु पर ₹50000',
            'benefits_mr': 'वर्षातून ₹2000 किंवा मृत्यूवर ₹50000',
            'eligibility': 'Farmers with land in West Bengal',
            'eligibility_hi': 'पश्चिम बंगाल में जमीन वाले किसान',
            'eligibility_mr': 'पश्चिम बंगालमध्ये जमीन असलेले शेतकरी',
            'documents': 'Aadhaar, Land Records, Bank Account',
            'documents_hi': 'आधार, भूमि रिकॉर्ड, बैंक खाता',
            'documents_mr': 'आधार, जमीन रेकॉर्ड्स, बँक खाते',
            'how_to_apply': '1. Visit Krishi Bhawan\n2. Register with documents',
            'how_to_apply_hi': '1. कृषि भवन जाएं\n2. दस्तावेजों के साथ पंजीकरण करें',
            'how_to_apply_mr': '1. कृषी भवनात जा\n2. कागदपत्रांसह नोंदणी करा',
            'official_link': 'https://wb.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 70,
            'gender': 'All',
            'income_range': 'All',
            'state': 'WB',
            'region': 'All'
        },
        # Rajasthan Schemes
        {
            'name': 'Rajasthan BPL Housing Scheme',
            'name_hi': 'राजस्थान BPL आवास योजना',
            'name_mr': 'राजस्थान BPL घर योजना',
            'category': 'housing',
            'description': 'Housing for BPL families in Rajasthan',
            'description_hi': 'राजस्थान में BPL परिवारों के लिए आवास',
            'description_mr': 'राजस्थानातील BPL कुटुंबांसाठी घर',
            'benefits': 'Financial assistance for house construction',
            'benefits_hi': 'घर निर्माण के लिए वित्तीय सहायता',
            'benefits_mr': 'घर बांधकामासाठी आर्थिक मदत',
            'eligibility': 'BPL families without pucca house',
            'eligibility_hi': 'पक्के घर के बिना BPL परिवार',
            'eligibility_mr': 'पक्के घराशिवाय BPL कुटुंब',
            'documents': 'Aadhaar, BPL Card, Land Records',
            'documents_hi': 'आधार, BPL कार्ड, भूमि रिकॉर्ड',
            'documents_mr': 'आधार, BPL कार्ड, जमीन रेकॉर्ड्स',
            'how_to_apply': '1. Apply at Gram Panchayat\n2. Get approval',
            'how_to_apply_hi': '1. ग्राम पंचायत में आवेदन करें\n2. अनुमोदन प्राप्त करें',
            'how_to_apply_mr': '1. ग्राम पंचायतमध्ये अर्ज करा\n2. मंजूरी मिळवा',
            'official_link': 'https://rajasthan.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 60,
            'gender': 'All',
            'income_range': 'Below 3 Lakh',
            'state': 'RJ',
            'region': 'All'
        },
        # Gujarat Schemes
        {
            'name': 'Gujarat Kisan Karj Mafi Yojana',
            'name_hi': 'गुजरात किसान कर्ज माफी योजना',
            'name_mr': 'गुजरात शेतकरी कर्ज माफी योजना',
            'category': 'farmer',
            'description': 'Loan waiver for farmers in Gujarat',
            'description_hi': 'गुजरात में किसानों के लिए ऋण माफी',
            'description_mr': 'गुजरातमधील शेतकऱ्यांसाठी कर्ज माफी',
            'benefits': 'Waiver of farm loans up to ₹1 lakh',
            'benefits_hi': '₹1 लाख तक के खेत ऋण की माफी',
            'benefits_mr': '₹1 लाखापर्यंत शेती कर्ज माफी',
            'eligible': 'Small and marginal farmers',
            'eligibility_hi': 'छोटे और सीमांत किसान',
            'eligibility_mr': 'लहान आणि सीमांत शेतकरी',
            'documents': 'Aadhaar, Bank Account, Loan Documents',
            'documents_hi': 'आधार, बैंक खाता, ऋण दस्तावेज',
            'documents_mr': 'आधार, बँक खाते, कर्ज कागदपत्रे',
            'how_to_apply': '1. Visit bank\n2. Submit application',
            'how_to_apply_hi': '1. बैंक जाएं\n2. आवेदन जमा करें',
            'how_to_apply_mr': '1. बँकला भेट द्या\n2. अर्ज सबमिट करा',
            'official_link': 'https://gujarat.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 70,
            'gender': 'All',
            'income_range': 'All',
            'state': 'GJ',
            'region': 'All'
        },
        # Employment Schemes
        {
            'name': 'PM SVANidhi Scheme',
            'name_hi': 'PM स्वनिधि योजना',
            'name_mr': 'PM स्वनिधी योजना',
            'category': 'employment',
            'description': 'Micro credit facility for street vendors',
            'description_hi': 'स्ट्रीट वेंडरों के लिए माइक्रो क्रेडिट सुविधा',
            'description_mr': 'रेहगीरांसाठी मायक्रो क्रेडिट सुविधा',
            'benefits': 'Loan up to ₹50000 without collateral',
            'benefits_hi': 'बिना गारंटी के ₹50000 तक का ऋण',
            'benefits_mr': 'जमानतशिवाय ₹50000 पर्यंत कर्ज',
            'eligibility': 'Street vendors with valid ID',
            'eligibility_hi': 'वैध पहचान वाले स्ट्रीट वेंडर',
            'eligibility_mr': 'वैध ओळख असलेले रेहगीर',
            'documents': 'Aadhaar, Vendor Certificate, Bank Account',
            'documents_hi': 'आधार, वेंडर प्रमाणपत्र, बैंक खाता',
            'documents_mr': 'आधार, वेंडर प्रमाणपत्र, बँक खाते',
            'how_to_apply': '1. Apply at bank or CSC\n2. Get loan',
            'how_to_apply_hi': '1. बैंक या CSC में आवेदन करें\n2. ऋण प्राप्त करें',
            'how_to_apply_mr': '1. बँक किंवा CSC मध्ये अर्ज करा\n2. कर्ज मिळवा',
            'official_link': 'https://pmsvanidhi.mca.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 65,
            'gender': 'All',
            'income_range': 'All',
            'state': 'TT',
            'region': 'All'
        },
        # More Central Schemes
        {
            'name': 'PM Kisan Tractor Yojana',
            'name_hi': 'PM किसान ट्रैक्टर योजना',
            'name_mr': 'PM शेतकरी ट्रॅक्टर योजना',
            'category': 'farmer',
            'description': 'Subsidy for tractor purchase for farmers',
            'description_hi': 'किसानों के लिए ट्रैक्टर खरीद पर सब्सिडी',
            'description_mr': 'शेतकऱ्यांसाठी ट्रॅक्टर खरेदीवर सबसिडी',
            'benefits': 'Subsidy 20-50% of tractor cost',
            'benefits_hi': 'ट्रैक्टर लागत का 20-50% सब्सिडी',
            'benefits_mr': 'ट्रॅक्टर खर्चाच्या 20-50% सबसिडी',
            'eligibility': 'Small and marginal farmers',
            'eligibility_hi': 'छोटे और सीमांत किसान',
            'eligibility_mr': 'लहान आणि सीमांत शेतकरी',
            'documents': 'Aadhaar, Land Records, Bank Account',
            'documents_hi': 'आधार, भूमि रिकॉर्ड, बैंक खाता',
            'documents_mr': 'आधार, जमीन रेकॉर्ड्स, बँक खाते',
            'how_to_apply': '1. Apply at agricultural office\n2. Get approval',
            'how_to_apply_hi': '1. कृषि कार्यालय में आवेदन करें\n2. अनुमोदन प्राप्त करें',
            'how_to_apply_mr': '1. कृषी कार्यालयात अर्ज करा\n2. मंजूरी मिळवा',
            'official_link': 'https://pmkisan.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 60,
            'gender': 'All',
            'income_range': 'All',
            'state': 'TT',
            'region': 'All'
        },
        {
            'name': 'PM Formalisation of Micro Food Processing Enterprises',
            'name_hi': 'PM सूक्ष्म खाद्य प्रसंस्करण उद्यमों का औपचारिकरण',
            'name_mr': 'PM सूक्ष्म अन्न प्रक्रिया उद्यमांचे औपचारिकरण',
            'category': 'employment',
            'description': 'Support for micro food processing units',
            'description_hi': 'सूक्ष्म खाद्य प्रसंस्करण इकाइयों के लिए सहायता',
            'description_mr': 'सूक्ष्म अन्न प्रक्रिया युनिट्ससाठी समर्थन',
            'benefits': 'Credit linked subsidy 35% of project cost',
            'benefits_hi': 'परियोजना लागत का 35% क्रेडिट लिंक्ड सब्सिडी',
            'benefits_mr': 'प्रकल्प खर्चाच्या 35% क्रेडिट लिंक्ड सबसिडी',
            'eligibility': 'Any individual wanting to set up food processing unit',
            'eligibility_hi': 'खाद्य प्रसंस्करण इकाई स्थापित करने वाला कोई भी व्यक्ति',
            'eligibility_mr': 'अन्न प्रक्रिया युनिट स्थापन करू इच्छिणारी कोणतीही व्यक्ती',
            'documents': 'Aadhaar, Business Plan, Address Proof',
            'documents_hi': 'आधार, व्यवसाय योजना, पते का प्रमाण',
            'documents_mr': 'आधार, व्यवसाय योजना, पत्त्याचा पुरावा',
            'how_to_apply': '1. Apply at nearest bank\n2. Submit project report',
            'how_to_apply_hi': '1. निकटतम बैंक में आवेदन करें\n2. परियोजना रिपोर्ट जमा करें',
            'how_to_apply_mr': '1. जवळच्या बँकमध्ये अर्ज करा\n2. प्रकल्प अहवाल सबमिट करा',
            'official_link': 'https://mofpie.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 65,
            'gender': 'All',
            'income_range': 'All',
            'state': 'TT',
            'region': 'All'
        },
        {
            'name': 'PM Rojgar Protsahan Yojana',
            'name_hi': 'PM रोजगार प्रोत्साहन योजना',
            'name_mr': 'PM रोजगार प्रोत्साहन योजना',
            'category': 'employment',
            'description': 'Government pays employer EPF contribution for new employees',
            'description_hi': 'सरकार नए कर्मचारियों के लिए नियोक्ता EPF योगदान देती है',
            'description_mr': 'सरकार नवीन कर्मचाऱ्यांसाठी नियोक्ता EPF-contribution देते',
            'benefits': 'Government pays 12% employer EPF contribution',
            'benefits_hi': 'सरकार 12% नियोक्ता EPF योगदान देती है',
            'benefits_mr': 'सरकार 12% नियोक्ता EPF-contribution देते',
            'eligibility': 'Establishments with EPFO registration, new employees',
            'eligibility_hi': 'EPFO पंजीकृत प्रतिष्ठान, नए कर्मचारी',
            'eligibility_mr': 'EPFO नोंदणी असलेली संस्था, नवीन कर्मचारी',
            'documents': 'UAN, Establishment Registration, Employee Details',
            'documents_hi': 'UAN, प्रतिष्ठान पंजीकरण, कर्मचारी विवरण',
            'documents_mr': 'UAN, संस्था नोंदणी, कर्मचारी तपशील',
            'how_to_apply': '1. Register on EPFO portal\n2. Add new employees',
            'how_to_apply_hi': '1. EPFO पोर्टल पर पंजीकरण करें\n2. नए कर्मचारी जोड़ें',
            'how_to_apply_mr': '1. EPFO पोर्टलवर नोंदणी करा\n2. नवीन कर्मचारी जोडा',
            'official_link': 'https://epfindia.gov.in',
            'deadline': '2024-12-31',
            'min_age': 18,
            'max_age': 60,
            'gender': 'All',
            'income_range': 'All',
            'state': 'TT',
            'region': 'All'
        },
        # Student Schemes
        {
            'name': 'PM YASASVI Pre-Matric Scholarship',
            'name_hi': 'PM YASASVI प्री-मैट्रिक छात्रवृत्ति',
            'name_mr': 'PM YASASVI प्री-मॅट्रिक शिष्यवृत्ती',
            'category': 'student',
            'description': 'Scholarship for OBC, EBC, DNT students Class 1-10',
            'description_hi': 'OBC, EBC, DNT छात्रों के लिए कक्षा 1-10 छात्रवृत्ति',
            'description_mr': 'OBC, EBC, DNT विद्यार्थ्यांसाठी इयत्ता 1-10 शिष्यवृत्ती',
            'benefits': '₹6000-₹12000 per year',
            'benefits_hi': 'प्रति वर्ष ₹6000-₹12000',
            'benefits_mr': 'वर्षातून ₹6000-₹12000',
            'eligibility': 'OBC, EBC, DNT students in Class 1-10, family income below ₹2.5 lakh',
            'eligibility_hi': 'कक्षा 1-10 में OBC, EBC, DNT छात्र, परिवार की आय ₹2.5 लाख से कम',
            'eligibility_mr': 'इयत्ता 1-10 मधील OBC, EBC, DNT विद्यार्थी, कुटुंबाचे उत्पन्न ₹2.5 लाखाखाली',
            'documents': 'Aadhaar, Caste Certificate, Income Certificate, Previous marksheet',
            'documents_hi': 'आधार, जात प्रमाण पत्र, आय प्रमाण पत्र, पिछला अंकपत्र',
            'documents_mr': 'आधार, जात प्रमाणपत्र, उत्पन्न प्रमाणपत्र, मागील गुणपत्रक',
            'how_to_apply': '1. Apply on NSP portal\n2. Submit documents',
            'how_to_apply_hi': '1. NSP पोर्टल पर आवेदन करें\n2. दस्तावेज जमा करें',
            'how_to_apply_mr': '1. NSP पोर्टलवर अर्ज करा\n2. कागदपत्रे सबमिट करा',
            'official_link': 'https://scholarships.gov.in',
            'deadline': '2024-10-31',
            'min_age': 5,
            'max_age': 18,
            'gender': 'All',
            'income_range': 'Below 2.5 Lakh',
            'state': 'TT',
            'region': 'All'
        },
        {
            'name': 'Post-Matric Scholarship for SC Students',
            'name_hi': 'SC छात्रों के लिए पोस्ट-मैट्रिक छात्रवृत्ति',
            'name_mr': 'SC विद्यार्थ्यांसाठी पोस्ट-मॅट्रिक शिष्यवृत्ती',
            'category': 'student',
            'description': 'Scholarship for SC students pursuing post-matric education',
            'description_hi': 'स्नातक शिक्षा प्राप्त करने वाले SC छात्रों के लिए छात्रवृत्ति',
            'description_mr': 'पदवी शिक्षण घेणाऱ्या SC विद्यार्थ्यांसाठी शिष्यवृत्ती',
            'benefits': 'Full tuition fee + maintenance allowance',
            'benefits_hi': 'पूर्ण ट्यूशन फी + रखरखाव भत्ता',
            'benefits_mr': 'पूर्ण शिक्षण शुल्क + निर्वाह भत्ता',
            'eligibility': 'SC students in post-matric courses, family income below ₹2.5 lakh',
            'eligibility_hi': 'स्नातक पाठ्यक्रम में SC छात्र, परिवार की आय ₹2.5 लाख से कम',
            'eligibility_mr': 'पदवी अभ्यासक्रमातील SC विद्यार्थी, कुटुंबाचे उत्पन्न ₹2.5 लाखाखाली',
            'documents': 'Aadhaar, Caste Certificate, Income Certificate, Admission letter',
            'documents_hi': 'आधार, जात प्रमाण पत्र, आय प्रमाण पत्र, प्रवेश पत्र',
            'documents_mr': 'आधार, जात प्रमाणपत्र, उत्पन्न प्रमाणपत्र, प्रवेश पत्र',
            'how_to_apply': '1. Apply through state SC corporation\n2. Submit documents',
            'how_to_apply_hi': '1. राज्य SC निगम के माध्यम से आवेदन करें\n2. दस्तावेज जमा करें',
            'how_to_apply_mr': '1. राज्य SC महामंडळाद्वारे अर्ज करा\n2. कागदपत्रे सबमिट करा',
            'official_link': 'https://socialjustice.nic.in',
            'deadline': '2024-10-31',
            'min_age': 15,
            'max_age': 35,
            'gender': 'All',
            'income_range': 'Below 2.5 Lakh',
            'state': 'TT',
            'region': 'All'
        },
        {
            'name': 'AICTE Pragati Scholarship for Girls',
            'name_hi': 'AICTE प्रगति छात्रवृत्ति',
            'name_mr': 'AICTE प्रगती शिष्यवृत्ती',
            'category': 'student',
            'description': 'Scholarship for girls studying technical courses',
            'description_hi': 'तकनीकी कोर्स पढ़ने वाली लड़कियों के लिए छात्रवृत्ति',
            'description_mr': 'तांत्रिक अभ्यासक्रम शिकणाऱ्या मुलींसाठी शिष्यवृत्ती',
            'benefits': '₹50000 per year for tuition fee + ₹20000 for books',
            'benefits_hi': 'प्रति वर्ष ट्यूशन फी के लिए ₹50000 + ₹20000 किताबों के लिए',
            'benefits_mr': 'वर्षातून शिक्षण शुल्कासाठी ₹50000 + ₹20000 पुस्तकांसाठी',
            'eligibility': 'Girls admitted to AICTE approved technical institutions, family income below ₹8 lakh',
            'eligibility_hi': 'AICTE अनुमोदित तकनीकी संस्थाओं में प्रवेशित लड़कियां, परिवार की आय ₹8 लाख से कम',
            'eligibility_mr': 'AICTE मान्यताधारक तांत्रिक संस्थांमध्ये प्रवेशित मुली, कुटुंबाचे उत्पन्न ₹8 लाखाखाली',
            'documents': 'Aadhaar, Institute ID, Income Certificate, Previous year marksheet',
            'documents_hi': 'आधार, संस्था आईडी, आय प्रमाण पत्र, पिछले वर्ष का अंकपत्र',
            'documents_mr': 'आधार, संस्था ओळख, उत्पन्न प्रमाणपत्र, मागील वर्षाचे गुणपत्रक',
            'how_to_apply': '1. Apply on AICTE portal\n2. Get institute verification',
            'how_to_apply_hi': '1. AICTE पोर्टल पर आवेदन करें\n2. संस्था सत्यापन प्राप्त करें',
            'how_to_apply_mr': '1. AICTE पोर्टलवर अर्ज करा\n2. संस्था पडताळणी मिळवा',
            'official_link': 'https://aicte-pragati.gov.in',
            'deadline': '2024-10-31',
            'min_age': 17,
            'max_age': 25,
            'gender': 'Female',
            'income_range': 'Below 8 Lakh',
            'state': 'TT',
            'region': 'All'
        }
    ]

# Initialize database on startup
init_db()

# Auto-fetch live schemes on startup (in background)
try:
    fetch_live_schemes_from_api()
except Exception as e:
    print(f"Note: Could not fetch live schemes: {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/schemes')
def schemes():
    return render_template('schemes.html')

@app.route('/scheme-detail')
def scheme_detail():
    return render_template('scheme-detail.html')

@app.route('/saved-schemes')
def saved_schemes():
    return render_template('saved-schemes.html')

# User Authentication API
@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    category = data.get('category')
    age = data.get('age')
    income = data.get('income')
    
    if not all([name, email, password, category, age, income]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email already registered'})
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Insert user
    cursor.execute('''
        INSERT INTO users (name, email, password, category, age, income)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, hashed_password, category, age, income))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login_user():
    """Login user"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'success': False, 'message': 'Email and password required'})
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Hash password and check
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                   (email, hashed_password))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid email or password'})
    
    # Store user in session
    session['user'] = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'category': user['category'],
        'age': user['age'],
        'income': user['income']
    }
    
    # Create session_id for saved schemes
    session_id = f"user_{user['id']}"
    
    conn.close()
    
    return jsonify({
        'success': True, 
        'user': session['user'],
        'session_id': session_id
    })

@app.route('/api/logout', methods=['POST'])
def logout_user():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})

# API Endpoints
@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    """Get all schemes with optional filters"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    category = request.args.get('category')
    search = request.args.get('search')
    gender = request.args.get('gender')
    income_range = request.args.get('income_range')
    
    query = "SELECT * FROM schemes WHERE 1=1"
    params = []
    
    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)
    
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if gender and gender != 'all':
        query += " AND (gender = ? OR gender = 'All')"
        params.append(gender)
    
    if income_range and income_range != 'all':
        query += " AND (income_range = ? OR income_range = 'All')"
        params.append(income_range)
    
    cursor.execute(query, params)
    schemes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(schemes)

@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of Indian states"""
    states = [
        {"code": "AN", "name": "Andaman and Nicobar Islands"},
        {"code": "AP", "name": "Andhra Pradesh"},
        {"code": "AR", "name": "Arunachal Pradesh"},
        {"code": "AS", "name": "Assam"},
        {"code": "BR", "name": "Bihar"},
        {"code": "DL", "name": "Delhi"},
        {"code": "GJ", "name": "Gujarat"},
        {"code": "HR", "name": "Haryana"},
        {"code": "HP", "name": "Himachal Pradesh"},
        {"code": "JK", "name": "Jammu and Kashmir"},
        {"code": "KA", "name": "Karnataka"},
        {"code": "KL", "name": "Kerala"},
        {"code": "MH", "name": "Maharashtra"},
        {"code": "MP", "name": "Madhya Pradesh"},
        {"code": "TN", "name": "Tamil Nadu"},
        {"code": "TG", "name": "Telangana"},
        {"code": "RJ", "name": "Rajasthan"},
        {"code": "UP", "name": "Uttar Pradesh"},
        {"code": "WB", "name": "West Bengal"},
        {"code": "TT", "name": "All India"}
    ]
    return jsonify(states)

@app.route('/api/schemes-by-location', methods=['GET'])
def get_schemes_by_location():
    """Get schemes available in a specific state"""
    state = request.args.get('state', 'all')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get schemes for specific state + all India schemes (TT = All India)
    query = """
        SELECT * FROM schemes 
        WHERE (state IS NULL OR state = '' OR state = 'All' OR state = 'TT' OR state = ?)
    """
    cursor.execute(query, (state,))
    schemes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(schemes)

@app.route('/api/scheme/<int:scheme_id>', methods=['GET'])
def get_scheme(scheme_id):
    """Get single scheme details"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,))
    scheme = dict(cursor.fetchone())
    conn.close()
    
    return jsonify(scheme)

@app.route('/api/check-eligibility', methods=['POST'])
def check_eligibility():
    """AI-based eligibility checker"""
    data = request.json
    user_profile = data.get('profile', {})
    scheme_id = data.get('scheme_id')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,))
    scheme = dict(cursor.fetchone())
    
    # Eligibility check logic
    eligibility_result = {
        'eligible': True,
        'reasons': [],
        'missing': []
    }
    
    # Age check
    if scheme['min_age'] and user_profile.get('age', 0) < scheme['min_age']:
        eligibility_result['eligible'] = False
        eligibility_result['reasons'].append(f"Minimum age required: {scheme['min_age']}")
    
    if scheme['max_age'] and user_profile.get('age', 0) > scheme['max_age']:
        eligibility_result['eligible'] = False
        eligibility_result['reasons'].append(f"Maximum age allowed: {scheme['max_age']}")
    
    # Gender check
    if scheme['gender'] and scheme['gender'] != 'All':
        if user_profile.get('gender') != scheme['gender']:
            eligibility_result['eligible'] = False
            eligibility_result['reasons'].append(f"This scheme is for {scheme['gender']} only")
    
    # Income check
    user_income = user_profile.get('income_range', 'All')
    if scheme['income_range'] and scheme['income_range'] != 'All':
        income_limits = {
            'Below 3 Lakh': 300000,
            'Below 2.5 Lakh': 250000,
            'Below 7.5 Lakh': 750000,
            'Below 8 Lakh': 800000,
            'Below 18 Lakh': 1800000,
            'All': float('inf')
        }
        
        user_income_limit = income_limits.get(user_income, float('inf'))
        scheme_income_limit = income_limits.get(scheme['income_range'], 0)
        
        if user_income_limit > scheme_income_limit:
            eligibility_result['eligible'] = False
            eligibility_result['reasons'].append(f"Income should be {scheme['income_range']}")
    
    conn.close()
    
    return jsonify(eligibility_result)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """AI-based recommendation engine"""
    data = request.json
    user_profile = data.get('profile', {})
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    category = user_profile.get('category', '')
    
    if category:
        cursor.execute("SELECT * FROM schemes WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM schemes")
    
    schemes = [dict(row) for row in cursor.fetchall()]
    
    # Score schemes based on profile
    recommendations = []
    for scheme in schemes:
        score = 0
        
        # Category match
        if scheme['category'] == category:
            score += 10
        
        # Age match
        age = user_profile.get('age', 0)
        if scheme['min_age'] and age >= scheme['min_age']:
            if not scheme['max_age'] or age <= scheme['max_age']:
                score += 5
        
        # Income match
        income = user_profile.get('income_range', 'All')
        if scheme['income_range'] == 'All' or income == 'Below 3 Lakh':
            score += 3
        
        if score > 0:
            scheme['score'] = score
            recommendations.append(scheme)
    
    # Sort by score
    recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    conn.close()
    
    return jsonify(recommendations[:6])

@app.route('/api/save-scheme', methods=['POST'])
def save_scheme():
    """Save a scheme for user"""
    data = request.json
    session_id = data.get('session_id', 'default')
    scheme_id = data.get('scheme_id')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if already saved
    cursor.execute("SELECT * FROM saved_schemes WHERE user_session = ? AND scheme_id = ?", 
                  (session_id, scheme_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO saved_schemes (user_session, scheme_id) VALUES (?, ?)",
                      (session_id, scheme_id))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/api/unsave-scheme', methods=['POST'])
def unsave_scheme():
    """Remove saved scheme"""
    data = request.json
    session_id = data.get('session_id', 'default')
    scheme_id = data.get('scheme_id')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM saved_schemes WHERE user_session = ? AND scheme_id = ?",
                  (session_id, scheme_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/saved-schemes', methods=['GET'])
def get_saved_schemes():
    """Get user's saved schemes"""
    session_id = request.args.get('session_id', 'default')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.* FROM schemes s
        JOIN saved_schemes ss ON s.id = ss.scheme_id
        WHERE ss.user_session = ?
    ''', (session_id,))
    
    schemes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(schemes)

@app.route('/api/add-reminder', methods=['POST'])
def add_reminder():
    """Add reminder for scheme"""
    data = request.json
    session_id = data.get('session_id', 'default')
    scheme_id = data.get('scheme_id')
    reminder_date = data.get('reminder_date')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO reminders (user_session, scheme_id, reminder_date) VALUES (?, ?, ?)",
                  (session_id, scheme_id, reminder_date))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    """Get user's reminders"""
    session_id = request.args.get('session_id', 'default')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, s.name, s.deadline FROM reminders r
        JOIN schemes s ON r.scheme_id = s.id
        WHERE r.user_session = ?
        ORDER BY r.reminder_date ASC
    ''', (session_id,))
    
    reminders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(reminders)

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """Rule-based AI chatbot for government schemes"""
    data = request.json
    message = data.get('message', '').lower()
    language = data.get('language', 'en')
    category = data.get('category', '')
    
    # Response templates
    responses = {
        'en': {
            'greeting': 'Namaste! I am your Government Scheme Assistant. How can I help you today?',
            'student': 'For students, I recommend: National Scholarship Portal, PM YASASVI Scholarship. These provide financial assistance for education. Would you like more details?',
            'farmer': 'For farmers, key schemes are: PM Kisan Samman Nidhi (₹6000/year), Pradhan Mantri Fasal Bima Yojana (crop insurance). Would you like to apply?',
            'women': 'For women, schemes include: Beti Bachao Beti Padhao, Sukanya Samriddhi Yojana, Stand Up India for women entrepreneurs. What interests you?',
            'housing': 'For housing: Pradhan Mantri Awas Yojana provides affordable housing. Rural: up to ₹1.20 lakh, Urban: interest subsidy on home loans.',
            'health': 'For health: Ayushman Bharat PM-JAY provides ₹5 lakh insurance, Pradhan Mantri Suraksha Bima Yojana for accident cover (₹20/year).',
            'employment': 'For employment: MGNREGA (100 days guaranteed work), Pradhan Mantri Mudra Yojana (loans up to ₹10 lakh), E-Shram Portal.',
            'default': 'I can help you find government schemes based on your category. Just tell me: Student, Farmer, Women, Housing, Health, or Employment!',
            'deadline': 'Most government schemes have deadlines around March 2025. It\'s best to apply early. Would you like to see schemes with nearest deadlines?',
            'documents': 'Common documents needed: Aadhaar Card, Bank Account, Income Certificate, Category Certificate, Photo. Specific schemes may need additional documents.',
            'how_to_apply': 'Most schemes can be applied through: 1) Official government portals, 2) Nearest Common Service Center (CSC), 3) Bank branches. Would you like step-by-step guidance?',
            'eligibility': 'Eligibility depends on: Category, Age, Income, Gender, Residence. Would you like me to check your eligibility for specific schemes?',
            'help': 'I can help you with: 1) Finding schemes by category, 2) Checking eligibility, 3) Understanding documents needed, 4) Application process. What would you like to know?'
        },
        'hi': {
            'greeting': 'नमस्ते! मैं आपका सरकारी योजना सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?',
            'student': 'छात्रों के लिए, मैं राष्ट्रीय छात्रवृत्ति पोर्टल, PM YASASVI छात्रवृत्ति की सिफारिश करता हूं।',
            'farmer': 'किसानों के लिए प्रमुख योजनाएं: PM Kisan (₹6000/वर्ष), फसल बीमा योजना।',
            'women': 'महिलाओं के लिए: बेटी बचाओ बेटी पढ़ाओ, सुकन्या समृद्धि योजना।',
            'housing': 'आवास के लिए: प्रधानमंत्री आवास योजना।',
            'health': 'स्वास्थ्य के लिए: आयुष्मान भारत ₹5 लाख बीमा।',
            'employment': 'रोजगार के लिए: MGNREGA, मुद्रा योजना।',
            'default': 'मैं आपकी श्रेणी के आधार पर सरकारी योजनाएं खोजने में मदद कर सकता हूं।',
            'deadline': 'अधिकांश योजनाओं की समय सीमा मार्च 2025 के आसपास है।',
            'documents': 'आवश्यक दस्तावेज: आधार, बैंक खाता, आय प्रमाण पत्र।',
            'how_to_apply': 'आवेदन: ऑनलाइन पोर्टल, CSC केंद्र, बैंक शाखा।',
            'eligibility': 'पात्रता: श्रेणी, आयु, आय, लिंग पर निर्भर करती है।',
            'help': 'मैं मदद कर सकता हूं: योजनाएं खोजना, पात्रता जांचना, दस्तावेज।'
        },
        'mr': {
            'greeting': 'नमस्कार! मी तुमचा सरकारी योजना सहायक आहे. मी आज तुम्हाला कशी मदत करू शकतो?',
            'student': 'विद्यार्थ्यांसाठी: राष्ट्रीय शिष्यवृत्ती पोर्टल, PM YASASVI शिष्यवृत्ती.',
            'farmer': 'शेतकऱ्यांसाठी: PM किसान (₹6000/वर्ष), पीक विमा योजना.',
            'women': 'महिलांसाठी: मुली वाचवा मुली शिकवा, सुकन्या समृद्धी योजना.',
            'housing': 'घरासाठी: प्रधानमंत्री आवास योजना.',
            'health': 'आरोग्यासाठी: आयुष्मान भारत ₹5 लाख विमा.',
            'employment': 'रोजगारासाठी: MGNREGA, मुद्रा योजना.',
            'default': 'मी तुमच्या श्रेणीनुसार सरकारी योजना शोधण्यास मदत करू शकतो.',
            'deadline': 'बहुत योजनांची मुदत मार्च 2025 पर्यंत असते.',
            'documents': 'आवश्यक कागदपत्रे: आधार, बँक खाते, उत्पन्न प्रमाणपत्र.',
            'how_to_apply': 'अर्ज: ऑनलाइन पोर्टल, CSC केंद्र, बँक शाखा.',
            'eligibility': 'पात्रता: श्रेणी, वय, उत्पन्न, लिंगावर अवलंबून.',
            'help': 'मी मदत करू शकतो: योजना शोधणे, पात्रता तपासणे, कागदपत्रे.'
        }
    }
    
    lang_responses = responses.get(language, responses['en'])
    
    # Determine response
    response = lang_responses['default']
    
    if any(word in message for word in ['hello', 'hi', 'namaste', 'नमस्ते', 'नमस्कार']):
        response = lang_responses['greeting']
    elif any(word in message for word in ['student', 'student', 'छात्र', 'विद्यार्थी', 'scholarship', 'education']):
        response = lang_responses['student']
    elif any(word in message for word in ['farmer', 'किसान', 'शेतकरी', 'kisan', 'crop']):
        response = lang_responses['farmer']
    elif any(word in message for word in ['women', 'woman', 'महिला', 'girl', 'बेटी', 'मुलगी']):
        response = lang_responses['women']
    elif any(word in message for word in ['house', 'housing', 'आवास', 'घर', 'home']):
        response = lang_responses['housing']
    elif any(word in message for word in ['health', 'medical', 'स्वास्थ्य', 'आरोग्य', 'hospital', 'insurance']):
        response = lang_responses['health']
    elif any(word in message for word in ['job', 'employment', 'रोजगार', 'नोकरी', 'work']):
        response = lang_responses['employment']
    elif any(word in message for word in ['deadline', 'last date', 'समय सीमा', 'मुदत', 'due']):
        response = lang_responses['deadline']
    elif any(word in message for word in ['document', 'document', 'दस्तावेज', 'कागदपत्र', 'certificate']):
        response = lang_responses['documents']
    elif any(word in message for word in ['apply', 'how to apply', 'आवेदन', 'अर्ज', 'application']):
        response = lang_responses['how_to_apply']
    elif any(word in message for word in ['eligible', 'पात्र', 'पात्रता', 'eligibility', 'योग्य']):
        response = lang_responses['eligibility']
    elif any(word in message for word in ['help', 'मदत', 'help', 'सहायता']):
        response = lang_responses['help']
    
    return jsonify({
        'response': response,
        'language': language
    })

@app.route('/api/deadlines', methods=['GET'])
def get_deadlines():
    """Get schemes sorted by deadline"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM schemes WHERE deadline IS NOT NULL ORDER BY deadline ASC LIMIT 10")
    schemes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(schemes)

@app.route('/api/new-schemes', methods=['GET'])
def get_new_schemes():
    """Get newly launched schemes (recently added)"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get schemes sorted by creation date (newest first)
    cursor.execute("SELECT * FROM schemes ORDER BY created_at DESC LIMIT 10")
    schemes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(schemes)

# SMS Notification API Endpoints
@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """Update user profile with phone and SMS preferences"""
    data = request.json
    user_id = data.get('user_id')
    phone = data.get('phone')
    sms_notifications = data.get('sms_notifications', 0)
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID required'})
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET phone = ?, sms_notifications = ? WHERE id = ?
    ''', (phone, sms_notifications, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Profile updated'})

@app.route('/api/enable-sms', methods=['POST'])
def enable_sms():
    """Enable SMS notifications for user"""
    data = request.json
    user_id = data.get('user_id')
    phone = data.get('phone')
    
    if not user_id or not phone:
        return jsonify({'success': False, 'message': 'User ID and phone required'})
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET phone = ?, sms_notifications = 1 WHERE id = ?
    ''', (phone, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'SMS notifications enabled'})

@app.route('/api/disable-sms', methods=['POST'])
def disable_sms():
    """Disable SMS notifications"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID required'})
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET sms_notifications = 0 WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'SMS notifications disabled'})

@app.route('/api/send-sms-notification', methods=['POST'])
def send_sms_notification():
    """
    Send SMS notification to user (Mock implementation for demo)
    NOTE: For real SMS, integrate with Twilio/msg91/etc.
    """
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'User not found'})
    
    if not user['phone']:
        conn.close()
        return jsonify({'success': False, 'message': 'Phone number not registered'})
    
    if not user['sms_notifications']:
        conn.close()
        return jsonify({'success': False, 'message': 'SMS notifications disabled'})
    
    # Log notification (mock - in production use Twilio API)
    cursor.execute('''
        INSERT INTO notifications (user_id, phone, message, status)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user['phone'], message, 'sent'))
    
    conn.commit()
    conn.close()
    
    # Mock SMS response
    return jsonify({
        'success': True, 
        'message': f'SMS notification sent to {user["phone"]}',
        'mock': True,
        'note': 'This is a demo. For real SMS, integrate Twilio API'
    })

@app.route('/api/notify-new-scheme', methods=['POST'])
def notify_new_scheme():
    """
    Notify all users who have enabled SMS for a specific category
    (For demo: notifies users when new scheme is added)
    """
    data = request.json
    scheme_id = data.get('scheme_id')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get scheme details
    cursor.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,))
    scheme = cursor.fetchone()
    
    if not scheme:
        conn.close()
        return jsonify({'success': False, 'message': 'Scheme not found'})
    
    # Get users who want notifications for this category
    cursor.execute('''
        SELECT * FROM users 
        WHERE sms_notifications = 1 
        AND phone IS NOT NULL 
        AND phone != ''
    ''')
    users = cursor.fetchall()
    
    notification_count = 0
    for user in users:
        # Send notification to each user (mock)
        message = f"New Scheme Alert: {scheme['name']} - {scheme['description'][:100]}..."
        
        cursor.execute('''
            INSERT INTO notifications (user_id, phone, message, status)
            VALUES (?, ?, ?, ?)
        ''', (user['id'], user['phone'], message, 'sent'))
        
        notification_count += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'notifications_sent': notification_count,
        'scheme': scheme['name']
    })

@app.route('/api/user-notifications', methods=['GET'])
def get_user_notifications():
    """Get user's notification history"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID required'})
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY sent_at DESC 
        LIMIT 20
    ''', (user_id,))
    
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(notifications)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
