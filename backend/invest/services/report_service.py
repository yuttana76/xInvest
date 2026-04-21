import os
import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pypdf import PdfReader, PdfWriter
from django.conf import settings
from django.core.mail import EmailMessage
from ..models import Investor, InvestorAccount, AccountBalance
from stt_fundconnext.models import CustomerIndividual

class ReportService:
    def __init__(self):
        self.logo_text = "xinvest"
        self.styles = getSampleStyleSheet()
        
    def generate_statement_pdf(self, investor):
        """
        Generates an encrypted PDF statement for the investor.
        Returns the absolute path to the generated encrypted PDF.
        """
        # 1. Fetch data
        accounts = investor.accounts.filter(status='Active')
        balances = []
        total_value = 0
        
        for account in accounts:
            acc_balances = account.balances.all()
            for bal in acc_balances:
                balances.append({
                    'account_id': account.accountID,
                    'fund_code': bal.fundCode,
                    'units': float(bal.unitBalance),
                    'nav': float(bal.NAV),
                    'value': float(bal.amount)
                })
                total_value += float(bal.amount)
        
        # 2. Get encryption key (card number)
        ci = CustomerIndividual.objects.filter(card_number=investor.custCode).first()
        password = ci.card_number if ci else investor.custCode # Fallback to custCode if CI not found
        
        # 3. Create PDF in memory (first pass)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Header
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor("#003366")
        )
        elements.append(Paragraph("Investor Statement", title_style))
        
        # Investor Info
        info_data = [
            [f"Name: {investor.fullNameEn}"],
            [f"Date: {datetime.date.today().strftime('%d %b %Y')}"]
        ]
        info_table = Table(info_data, colWidths=[450])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Table Headers
        table_data = [['Account No', 'Fund Name', 'Units', 'NAV', 'Value']]
        
        # Table Rows
        for bal in balances:
            table_data.append([
                bal['account_id'],
                bal['fund_code'],
                f"{bal['units']:,.4f}",
                f"{bal['nav']:,.4f}",
                f"{bal['value']:,.2f}"
            ])
            
        # Summary Row
        table_data.append(['', '', '', 'Total Value', f"{total_value:,.2f}"])
        
        # Style the table
        summary_table = Table(table_data, colWidths=[100, 150, 90, 70, 90])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E6F2FF")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#003366")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F5F5F5")),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#CCE5FF")),
            ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ]))
        elements.append(summary_table)
        
        # Footer
        elements.append(Spacer(1, 40))
        footer_text = "Thank you for investing with xinvest. This is a computer generated report and is password protected."
        elements.append(Paragraph(footer_text, self.styles['Italic']))
        
        # Build PDF
        doc.build(elements)
        
        # 4. Encrypt the PDF
        buffer.seek(0)
        reader = PdfReader(buffer)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password)
        
        # 5. Save to file
        report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"statement_{timestamp}.pdf"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, "wb") as f:
            writer.write(f)
            
        return filepath

    def send_statement_report(self, investor):
        """
        Generates and sends the statement PDF via email.
        """
        try:
            pdf_path = self.generate_statement_pdf(investor)
            
            subject = f"Your Investment Statement - {datetime.date.today().strftime('%B %Y')}"
            message = f"""
Dear {investor.fullNameEn},

Please find attached your investment statement report.
The PDF is password protected for your security. 
Please use your ID card number as the password to open the file.

Should you have any questions, please contact our support team.

Best Regards,
xinvest team
            """
            
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [investor.email],
            )
            email.attach_file(pdf_path)
            email.send()
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)
