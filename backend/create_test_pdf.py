#!/usr/bin/env python3
"""
Create a test PDF file for resume upload testing
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_test_pdf():
    """Create a test PDF with technical skills"""
    
    # Create the PDF document
    doc = SimpleDocTemplate("test_resume.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    story.append(Paragraph("JOHN DOE", title_style))
    story.append(Paragraph("Software Developer", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Contact info
    story.append(Paragraph("john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", styles['Heading2']))
    story.append(Paragraph("Experienced software developer with 3+ years of experience in web development, proficient in JavaScript, React, and Node.js. Skilled in building responsive web applications and working with modern development tools.", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", styles['Heading2']))
    story.append(Paragraph("Programming Languages: JavaScript, Python, HTML, CSS", styles['Normal']))
    story.append(Paragraph("Frameworks & Libraries: React, Node.js, Express, Bootstrap", styles['Normal']))
    story.append(Paragraph("Databases: MongoDB, SQL, PostgreSQL", styles['Normal']))
    story.append(Paragraph("Tools & Platforms: Git, GitHub, Docker, AWS", styles['Normal']))
    story.append(Paragraph("Other: REST APIs, Agile methodologies, CI/CD", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Work Experience
    story.append(Paragraph("WORK EXPERIENCE", styles['Heading2']))
    story.append(Paragraph("Software Developer | Tech Company Inc. | 2021 - Present", styles['Heading3']))
    story.append(Paragraph("• Developed and maintained web applications using React and Node.js", styles['Normal']))
    story.append(Paragraph("• Worked with MongoDB and PostgreSQL databases", styles['Normal']))
    story.append(Paragraph("• Implemented REST APIs for mobile applications", styles['Normal']))
    story.append(Paragraph("• Used Git for version control and collaborated with team using GitHub", styles['Normal']))
    story.append(Paragraph("• Deployed applications using Docker and AWS", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Junior Developer | Startup XYZ | 2020 - 2021", styles['Heading3']))
    story.append(Paragraph("• Built responsive websites using HTML, CSS, and JavaScript", styles['Normal']))
    story.append(Paragraph("• Worked with Bootstrap for UI components", styles['Normal']))
    story.append(Paragraph("• Assisted in database design and SQL queries", styles['Normal']))
    story.append(Paragraph("• Participated in Agile development processes", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Education
    story.append(Paragraph("EDUCATION", styles['Heading2']))
    story.append(Paragraph("Bachelor of Science in Computer Science", styles['Normal']))
    story.append(Paragraph("University of Technology | 2020", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Projects
    story.append(Paragraph("PROJECTS", styles['Heading2']))
    story.append(Paragraph("E-commerce Platform", styles['Heading3']))
    story.append(Paragraph("• Built a full-stack e-commerce application using React, Node.js, and MongoDB", styles['Normal']))
    story.append(Paragraph("• Implemented user authentication and payment processing", styles['Normal']))
    story.append(Paragraph("• Deployed on AWS using Docker containers", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Task Management App", styles['Heading3']))
    story.append(Paragraph("• Created a React-based task management application", styles['Normal']))
    story.append(Paragraph("• Used Express.js for backend API development", styles['Normal']))
    story.append(Paragraph("• Integrated with PostgreSQL database", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Certifications
    story.append(Paragraph("CERTIFICATIONS", styles['Heading2']))
    story.append(Paragraph("• AWS Certified Developer Associate", styles['Normal']))
    story.append(Paragraph("• MongoDB Certified Developer", styles['Normal']))
    story.append(Paragraph("• React Developer Certification", styles['Normal']))
    
    # Build the PDF
    doc.build(story)
    print("✅ Test PDF created: test_resume.pdf")
    print("📄 This PDF contains technical skills that should be detected by the parser")

if __name__ == "__main__":
    create_test_pdf() 