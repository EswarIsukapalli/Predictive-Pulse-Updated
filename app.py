import pandas as pd
import joblib
import os
from flask import (
    Flask,
    url_for,
    render_template,
    redirect,
    request,
    send_file,
    flash,
    session
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import logging
from datetime import datetime
from functools import wraps

from config import Config
from models import db, User, Prediction
from forms import InputForm, RegistrationForm, LoginForm
from utils import (
    calculate_bmi,
    calculate_risk_score,
    get_risk_level,
    get_confidence_score,
    generate_pdf_report,
    get_recommendations
)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Load model
try:
    model = joblib.load("model.joblib")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route("/")
@app.route("/home")
def home():
    """Home page"""
    try:
        return render_template("home.html", title="Home")
    except Exception as e:
        logger.error(f"Error on home page: {e}")
        return render_template("error.html", error="An error occurred"), 500

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {form.username.data}")
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {e}")
            flash('An error occurred during registration.', 'danger')
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                logger.info(f"User logged in: {form.username.data}")
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred during login.', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard with prediction history"""
    try:
        page = request.args.get('page', 1, type=int)
        predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).paginate(page=page, per_page=10)
        return render_template("dashboard.html", title="Dashboard", predictions=predictions)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard.', 'danger')
        return redirect(url_for('home'))

@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    """Prediction page with form"""
    form = InputForm()
    recommendations = []
    stage_label = None
    stage_class = None
    confidence_score = 0
    risk_score = 0
    bmi = None
    risk_level = "Unknown"
    
    if form.validate_on_submit():
        try:
            if model is None:
                flash('Model is not loaded properly.', 'danger')
                return render_template("predict.html", title="Predict", form=form)
            
            # Prepare data for prediction
            x_new = pd.DataFrame(dict(
                Gender=[form.Gender.data],
                Age=[form.Age.data],
                History=[form.History.data],
                Patient=[form.Patient.data],
                TakeMedication=[form.TakeMedication.data],
                Severity=[form.Severity.data],
                BreathShortness=[form.BreathShortness.data],
                VisualChanges=[form.VisualChanges.data],
                NoseBleeding=[form.NoseBleeding.data],
                Whendiagnoused=[form.Whendiagnoused.data],
                Systolic=[form.Systolic.data],
                Diastolic=[form.Diastolic.data],
                ControlledDiet=[form.ControlledDiet.data]
            ))

            # Make prediction
            prediction = model.predict(x_new)[0]
            
            # Get prediction probability for confidence
            try:
                proba = model.predict_proba(x_new)[0]
                confidence_score = get_confidence_score(proba)
            except:
                confidence_score = 75.0
            
            # Map prediction to stage
            stage_map = {
                0: ("NORMAL", "stage-normal"),
                1: ("HYPERTENSION (Stage-1)", "stage-1"),
                2: ("HYPERTENSION (Stage-2)", "stage-2"),
                3: ("HYPERTENSIVE CRISIS", "stage-crisis")
            }
            stage_label, stage_class = stage_map.get(prediction, ("Unknown", ""))
            
            # Calculate BMI if height and weight provided
            if form.Height.data and form.Weight.data:
                bmi = calculate_bmi(form.Height.data, form.Weight.data)
            
            # Calculate risk score
            risk_score = calculate_risk_score(
                form.Severity.data,
                form.Age.data,
                form.History.data,
                form.Patient.data,
                form.TakeMedication.data,
                form.Systolic.data,
                form.Diastolic.data,
                form.BreathShortness.data,
                form.VisualChanges.data,
                bmi
            )
            risk_level = get_risk_level(risk_score)
            
            # Get recommendations
            severity = form.Severity.data
            recommendations = get_recommendations(severity)
            
            # Save prediction to database
            pred_record = Prediction(
                user_id=current_user.id,
                gender=form.Gender.data,
                age=form.Age.data,
                history=form.History.data,
                patient=form.Patient.data,
                take_medication=form.TakeMedication.data,
                severity=form.Severity.data,
                breath_shortness=form.BreathShortness.data,
                visual_changes=form.VisualChanges.data,
                nose_bleeding=form.NoseBleeding.data,
                whendiagnoused=form.Whendiagnoused.data,
                systolic=form.Systolic.data,
                diastolic=form.Diastolic.data,
                controlled_diet=form.ControlledDiet.data,
                height=form.Height.data,
                weight=form.Weight.data,
                heart_rate=form.HeartRate.data,
                stage_label=stage_label,
                stage_class=stage_class,
                confidence_score=confidence_score,
                risk_score=risk_score,
                notes=form.Notes.data
            )
            db.session.add(pred_record)
            db.session.commit()
            logger.info(f"Prediction saved for user {current_user.username}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Prediction error: {e}")
            flash(f'Error making prediction: {str(e)}', 'danger')
            return render_template("predict.html", title="Predict", form=form)

    return render_template("predict.html", 
        title="Predict", 
        form=form, 
        stage_label=stage_label, 
        stage_class=stage_class,
        confidence_score=confidence_score,
        risk_score=risk_score,
        risk_level=risk_level,
        bmi=bmi,
        recommendations=recommendations
    )

@app.route("/prediction/<int:pred_id>")
@login_required
def view_prediction(pred_id):
    """View detailed prediction"""
    try:
        prediction = Prediction.query.get_or_404(pred_id)
        if prediction.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard'))
        
        recommendations = get_recommendations(prediction.severity)
        return render_template("prediction_detail.html", 
            title="Prediction Details", 
            prediction=prediction,
            recommendations=recommendations
        )
    except Exception as e:
        logger.error(f"Error viewing prediction: {e}")
        flash('Prediction not found.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/export-pdf/<int:pred_id>")
@login_required
def export_pdf(pred_id):
    """Export prediction as PDF"""
    try:
        prediction = Prediction.query.get_or_404(pred_id)
        if prediction.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard'))
        
        recommendations = get_recommendations(prediction.severity)
        pdf_buffer = generate_pdf_report(current_user, prediction, recommendations)
        
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"BP_Report_{prediction.created_at.strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        else:
            flash('Error generating PDF.', 'danger')
            return redirect(url_for('view_prediction', pred_id=pred_id))
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        flash('Error exporting PDF.', 'danger')
        return redirect(url_for('dashboard'))

@app.route("/delete-prediction/<int:pred_id>", methods=["POST"])
@login_required
def delete_prediction(pred_id):
    """Delete a prediction"""
    try:
        prediction = Prediction.query.get_or_404(pred_id)
        if prediction.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard'))
        
        db.session.delete(prediction)
        db.session.commit()
        logger.info(f"Prediction deleted: {pred_id}")
        flash('Prediction deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting prediction: {e}")
        flash('Error deleting prediction.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {error}")
    return render_template("error.html", error="Internal server error"), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
