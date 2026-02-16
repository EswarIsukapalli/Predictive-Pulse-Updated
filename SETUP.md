# Predictive Pulse - Setup Guide

## New Features Implemented

All 10 features have been successfully integrated:

1. ✅ **Error Handling & Validation** - Try-catch blocks, input validation, and graceful error handling
2. ✅ **Database Integration** - SQLite database with prediction history tracking  
3. ✅ **Prediction Confidence Score** - Shows model confidence percentage for each prediction
4. ✅ **Risk Assessment Score** - Calculates overall health risk (0-100) with health indicators
5. ✅ **Export Functionality** - Download predictions as PDF reports with all details
6. ✅ **User Accounts & History** - User registration/login with prediction history dashboard
7. ✅ **Additional Health Metrics** - Height, weight, BMI calculation, heart rate tracking
8. ✅ **Real-time Form Validation** - WTForms validation with error messages
9. ✅ **Better Visualization** - Color-coded risk scores, confidence bars, health dashboards
10. ✅ **Mobile Responsive Design** - Fully responsive UI for all screen sizes

## Installation & Setup

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- flask-sqlalchemy (database ORM)
- flask-login (user authentication)
- flask-migrate (database migrations)
- reportlab (PDF generation)
- email-validator (email validation)

### 2. Initialize the Database

Run the app for the first time to create the database automatically:

```bash
python app.py
```

The database file `predictive_pulse.db` will be created in the project root.

### 3. Access the Application

Navigate to: `http://localhost:10000`

## Using the Application

### First Time Setup
1. Go to Register page to create an account
2. Log in with your credentials
3. Access the Predict page from the dashboard

### Features Overview

#### **1. User Authentication**
- Register new account (username, email, password)
- Secure login with password hashing
- Protected routes that require authentication

#### **2. Make Predictions**
- Fill out comprehensive health questionnaire
- 4 sections: Personal Info, Medical History, Symptoms, Blood Pressure & Lifestyle
- Optional fields: Height, Weight, Heart Rate, Additional Notes
- Multi-step form with progress tracking

#### **3. View Results**
- **Blood Pressure Stage** - Color-coded (Green/Orange/Red/Critical)
- **Confidence Score** - How confident the model is (0-100%)
- **Risk Score** - Overall health risk assessment (0-100)
- **Risk Level** - Low/Moderate/High/Very High
- **BMI Calculation** - If height/weight provided
- **Personalized Recommendations** - Based on severity level

#### **4. Prediction History (Dashboard)**
- View all past predictions with timestamps
- See trends over time
- Sort by date, stage, severity, confidence
- Pagination (10 per page)

#### **5. Detailed Prediction View**
- Click "View" to see full prediction details
- All health indicators and metrics
- Medical history
- Personalized recommendations
- Export to PDF from this page

#### **6. Export as PDF**
- Download complete prediction report
- Includes all health data
- Professional formatting
- Can be shared with doctors

#### **7. Risk Assessment**
Calculated based on:
- Condition severity (20 points)
- Age group (15 points)
- Hypertension history (10 points)
- Blood pressure levels (20 points)
- Symptoms (20 points)
- BMI (10 points)
- Medication status (10 points)
- **Total: 0-100 score**

#### **8. Mobile Responsive**
- Works on all screen sizes
- Touch-friendly interface
- Optimized for phones and tablets
- Responsive tables and forms

## File Structure

```
c:\Predictive-pulse new\
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models (User, Prediction)
├── forms.py               # WTForms form definitions
├── utils.py               # Helper functions (PDF, risk calc, BMI)
├── models.joblib          # Trained ML model
├── predictive_pulse.db    # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
│
├── templates/
│   ├── layout.html        # Base template
│   ├── home.html          # Home page
│   ├── login.html         # Login page (NEW)
│   ├── register.html      # Registration page (NEW)
│   ├── predict.html       # Prediction form (UPDATED)
│   ├── dashboard.html     # Prediction history (NEW)
│   ├── prediction_detail.html  # Prediction details (NEW)
│   └── error.html         # Error pages (NEW)
│
├── static/               # CSS, JS, images
└── data/
    ├── patient_data.csv
    └── patient_data1.csv
```

## API Routes

```
GET  /                    - Home page
GET  /home                - Home page (alias)
GET  /register            - Registration page
POST /register            - Register new user
GET  /login               - Login page
POST /login               - Login user
GET  /logout              - Logout user
GET  /dashboard           - User dashboard with history
GET  /predict             - Prediction form
POST /predict             - Make prediction
GET  /prediction/<id>     - View prediction details
GET  /export-pdf/<id>     - Download PDF report
POST /delete-prediction/<id> - Delete prediction
```

## Database Schema

### User Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- created_at

### Prediction Table
- id (Primary Key)
- user_id (Foreign Key)
- gender, age, history, patient, medication, etc.
- height, weight, heart_rate (optional)
- stage_label, stage_class
- confidence_score
- risk_score
- created_at
- notes

## Security Features

- Password hashing with werkzeug
- Form CSRF protection with flask-wtf
- Database relationships and proper ORM usage
- Input validation on all forms
- Error handling and logging
- Protected routes with login_required

## Troubleshooting

### Database Issues
If you encounter database errors, delete `predictive_pulse.db` and restart the app:
```bash
rm predictive_pulse.db
python app.py
```

### Missing New Pages
If you see 404 errors, ensure all template files are in the `templates/` folder:
- login.html
- register.html
- dashboard.html
- prediction_detail.html
- error.html

### Model Loading Error
Ensure `model.joblib` is in the project root directory. If missing, predictions will show an error.

### Port Already in Use
Change the port in app.py:
```python
app.run(debug=True, port=8080)  # Change 10000 to another port
```

## Performance Tips

1. Use the dashboard to see prediction history
2. PDF export works best for professional sharing
3. Risk scores update in real-time based on input
4. Database queries are optimized with pagination
5. Static assets are cached for faster loading

## Future Enhancements

Consider adding:
- Email notifications for high-risk predictions
- Data export to CSV
- API for mobile apps
- Advanced analytics/charts
- Doctor integration
- Multi-language support
- Wearable device integration

## Support

For issues or questions:
1. Check the error messages in the app
2. Review the logs in app.py output
3. Verify all dependencies are installed
4. Ensure database file has write permissions

---

**Version**: 2.0 (All 10 features implemented)
**Last Updated**: February 16, 2026
