import pandas as pd
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SubmitField,
    StringField,
    PasswordField,
    FloatField,
    IntegerField,
    TextAreaField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User

train = pd.read_csv('data/patient_data.csv')
X_data = train.drop(columns=['Stages'])

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InputForm(FlaskForm):
    """Main prediction form"""
    Gender = SelectField(
        label="Gender",
        choices = ['Male',"Female"],
        validators=[DataRequired()]
    )
     
    Age = SelectField(
        label="Age",
        choices = ['18-34', '35-50', '51-64', '65+'],
        validators=[DataRequired()]
    )

    History = SelectField(
        label="History of Hypertension",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    Patient = SelectField(
        label="Diagnosed Patient",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    TakeMedication = SelectField(
        label=" Medication for Hypertension",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    Severity = SelectField(
        label="Severity of the condition",
        choices = ['Mild', 'Moderate', 'Severe'],
        validators=[DataRequired()]
    )

    BreathShortness = SelectField(
        label="Experience shortness of breath",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    VisualChanges = SelectField(
        label="Vision problems",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    NoseBleeding = SelectField(
        label="Nose Bleeds",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    Whendiagnoused = SelectField(
        label="How long ago the condition was diagnosed",
        choices = ['<1 Year', '1 - 5 Years', '>5 Years'],
        validators=[DataRequired()]
    )

    Systolic = SelectField(
        label="Systolic blood pressure range",
        choices = ['100+', '111 - 120', '121 - 130', '130+'],
        validators=[DataRequired()]
    )

    Diastolic = SelectField(
        label="Diastolic blood pressure range",
        choices = ['70 - 80', '81 - 90', '91 - 100', '100+', '130+'],
        validators=[DataRequired()]
    )

    ControlledDiet	 = SelectField(
        label="Conrtolled Diet",
        choices = ['Yes',"No"],
        validators=[DataRequired()]
    )

    # New health metrics (optional)
    Height = FloatField(
        label="Height (in cm)",
        validators=[Optional(), NumberRange(min=100, max=250)]
    )

    Weight = FloatField(
        label="Weight (in kg)",
        validators=[Optional(), NumberRange(min=20, max=200)]
    )

    HeartRate = IntegerField(
        label="Heart Rate (beats per minute)",
        validators=[Optional(), NumberRange(min=40, max=200)]
    )

    Notes = TextAreaField(
        label="Additional Notes",
        validators=[Optional(), Length(max=500)]
    )

    submit = SubmitField("Predict")