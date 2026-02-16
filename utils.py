import math
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

def get_recommendations(severity):
    """Generate health recommendations based on severity level"""
    recommendations = {
        'Mild': [
            "Monitor your blood pressure regularly at home",
            "Maintain a healthy diet with reduced sodium intake",
            "Exercise regularly for at least 30 minutes daily",
            "Manage stress through meditation or yoga",
            "Limit alcohol consumption",
            "Maintain a healthy weight"
        ],
        'Moderate': [
            "Check blood pressure daily and keep a log",
            "Strictly follow a low-sodium diet (<2300mg per day)",
            "Exercise 30-60 minutes daily (cardio and strength training)",
            "Consult with a healthcare provider about medications",
            "Reduce caffeine and alcohol intake significantly",
            "Practice stress management techniques",
            "Consider a weight management program"
        ],
        'Severe': [
            "Seek immediate medical attention if experiencing chest pain or shortness of breath",
            "Take prescribed medications as directed by your doctor",
            "Monitor blood pressure multiple times daily",
            "Follow a strict low-sodium diet strictly",
            "Avoid physical exertion until cleared by doctor",
            "Regular follow-up appointments with healthcare provider",
            "Keep emergency contacts handy",
            "Consider wearing a medical alert device"
        ]
    }
    return recommendations.get(severity, [])

def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI from height and weight"""
    if height_cm <= 0 or weight_kg <= 0:
        return None
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def calculate_risk_score(severity, age, history, patient_diagnosed, take_medication, 
                        systolic, diastolic, breath_shortness, visual_changes, bmi=None):
    """
    Calculate overall health risk score (0-100)
    Higher score = higher risk
    """
    risk_score = 0
    
    # Severity contribution (20 points max)
    severity_map = {'Mild': 5, 'Moderate': 15, 'Severe': 20}
    risk_score += severity_map.get(severity, 0)
    
    # Age contribution (15 points max)
    age_map = {
        '18-34': 2,
        '35-50': 8,
        '51-64': 12,
        '65+': 15
    }
    risk_score += age_map.get(age, 0)
    
    # History of hypertension (10 points)
    if history == 'Yes':
        risk_score += 10
    
    # Already diagnosed (5 points)
    if patient_diagnosed == 'Yes':
        risk_score += 5
    
    # Not taking medication (10 points)
    if take_medication == 'No':
        risk_score += 10
    
    # Blood pressure levels (20 points)
    systolic_map = {'100+': 2, '111 - 120': 5, '121 - 130': 12, '130+': 20}
    diastolic_map = {'70 - 80': 2, '81 - 90': 5, '91 - 100': 12, '100+': 15, '130+': 20}
    risk_score += systolic_map.get(systolic, 0)
    risk_score += diastolic_map.get(diastolic, 0)
    
    # Symptoms (10 points each)
    if breath_shortness == 'Yes':
        risk_score += 10
    if visual_changes == 'Yes':
        risk_score += 10
    
    # BMI contribution (10 points max)
    if bmi:
        if bmi > 30:  # Obese
            risk_score += 10
        elif bmi > 25:  # Overweight
            risk_score += 5
    
    return min(risk_score, 100)  # Cap at 100

def get_risk_level(risk_score):
    """Get risk level category"""
    if risk_score < 20:
        return "Low"
    elif risk_score < 40:
        return "Moderate"
    elif risk_score < 60:
        return "High"
    else:
        return "Very High"

def get_confidence_score(prediction_proba=None):
    """
    Get confidence score from model probability
    If proba not available, return default
    """
    if prediction_proba is None:
        return 0.75  # Default confidence
    
    # Return max probability as confidence
    return round(float(max(prediction_proba) * 100), 2)

def generate_pdf_report(user, prediction, recommendations):
    """Generate PDF report of prediction"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph("BLOOD PRESSURE PREDICTION REPORT", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # User info
        elements.append(Paragraph("Patient Information", heading_style))
        user_data = [
            ['Patient Name:', user.username],
            ['Email:', user.email],
            ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        user_table = Table(user_data, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(user_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Prediction results
        elements.append(Paragraph("Prediction Results", heading_style))
        result_data = [
            ['Blood Pressure Stage:', prediction.stage_label],
            ['Severity Level:', prediction.severity],
            ['Confidence Score:', f"{prediction.confidence_score}%"],
            ['Overall Risk Score:', f"{prediction.risk_score}/100 ({get_risk_level(prediction.risk_score)})"]
        ]
        result_table = Table(result_data, colWidths=[2*inch, 4*inch])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(result_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        if recommendations:
            elements.append(Paragraph("Recommendations", heading_style))
            rec_text = "<br/>".join([f"• {rec}" for rec in recommendations])
            elements.append(Paragraph(rec_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Input data
        elements.append(Paragraph("Patient Input Data", heading_style))
        input_data = [
            ['Parameter', 'Value'],
            ['Age', prediction.age],
            ['Gender', prediction.gender],
            ['Systolic/Diastolic', f"{prediction.systolic}/{prediction.diastolic}"],
            ['Hypertension History', prediction.history],
            ['Currently on Medication', prediction.take_medication],
            ['Height (cm)', str(prediction.height) if prediction.height else 'N/A'],
            ['Weight (kg)', str(prediction.weight) if prediction.weight else 'N/A'],
            ['Heart Rate', str(prediction.heart_rate) if prediction.heart_rate else 'N/A']
        ]
        input_table = Table(input_data, colWidths=[2.5*inch, 3.5*inch])
        input_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(input_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=0
        )
        elements.append(Paragraph(
            "<i>Disclaimer: This report is generated by an AI model and should not be used as a substitute for professional medical advice. "
            "Please consult with a healthcare provider for personalized medical guidance.</i>",
            disclaimer_style
        ))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
