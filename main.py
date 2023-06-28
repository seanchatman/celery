from dotenv import load_dotenv

from ddd.application.feedback_service import FeedbackService
from ddd.application.report_processing_service import ReportProcessingService
from ddd.domain.email import Email
from ddd.domain.employee import Employee
from ddd.infrastructure.email_service import EmailService
from ddd.infrastructure.repositories import EmployeeRepository, FeedbackRepository, EmailRepository

load_dotenv('/Users/seanchatman/dev/celery/.env')

if __name__ == '__main__':
    # for e in EmployeeRepository().get_all():
    #     e.report_submitted = False
    #     EmployeeRepository().save(e)

    emails = EmailService().get_days_emails()

    # emails = [Email(id='Angel Cajalne', to='Anne Lackey at HireSmart <Anne@hiresmartvirtualemployees.com>, Julia\r\n Roberts at HireSmart <Julia@hiresmartvirtualemployees.com>', from_='Training <Training@hiresmartvirtualemployees.com>', subject='COB for June 6, 2023', body='Hi Team, Here are the things that I did for today: * Coached all 9 trainees\nabout their Day 1 performance * Focused on Rocky and Diana. I have coached\nthem about improving their communication and attentiveness and they committed\nto their action plan not to miss activities or check-ins. * Rocky, Cha and\nChai missed their surprise activity, during our coaching they made sure not to\nmiss their surprise activity again by being more attentive of the time and\nnotifications. * Monitored their check-ins * No missed check-ins today! *\nChecked the surprise activity * Tony will get the 15 min credit. * Rocky, Cha\nand Chai missed their surprise activity, during our coaching they made sure\nnot to miss their surprise activity again by being more attentive of the time\nand notifications. * Graded the Day 2 training materials * All of them were\nable to get good grades. No retakes for Day 2 so far. * Checked if the\ntrainees if they followed the break notification process * Created the Day 2\nprogress report To-do on Wednesday: * Monitor the 9 trainees in sending their\ncheck-ins and attentiveness * Send the surprise activity * Grade the Day 3\ntraining activities Best, Angel Cajalne Training Team | HireSmart Virtual\nEmployees angel@hiresmartvirtualemployees.com [HSVE_3-Logo-300x90]\n\n', sent=False),
    #           Email(id='Shannen Jaucian', to='Julia Roberts at HireSmart <Julia@hiresmartvirtualemployees.com>', from_='HireSmart Customer Care <CustomerService@hiresmartvirtualemployees.com>', subject='COB 6/6', body='Hi Julia – Greetings! Thank you so much for the opportunity. I’d rate today a\n4.5! Had a great check-in today, got a few no-shows and resched but still a\ngood day A) HIRESMART * Reviewed Trello board (5star/HSVE) * PENDING: *\nHOMESMART – Unpaid invoice for Monitor Advance * HUMPHREYS – Pending client\ncontract * NOVA – Pending VE Contract * Skype Management * Monitored Tawk.to *\nEmergency Email Management * Pear Accounting/Sheena - Sick * AM Huddle *\nPlanned for Monday’s Escalation Calls * Invited VE for CST Escalation Call *\nSent Birthday/Anniversary Messages to VEs * VE Check-ins * Sent invites *\nConfirmed time slots for VEs * Sent Zoom link to VEs * Attended Zoom calls *\nUploaded Check-In sheet to m.c * Uploaded recording to db * Scrubbed remaining\nresume from Monday interview * Sent followup emails to clients B) VEs *\nAttended Check-Ins: * Hydee Camoro * Jacklyn Benson * Laiza Banda * Jhoanna\nFausto * Maribeth Canete * Ariann Barcelona * Lucky Labto * Thabita Sabile *\nAlmay Alano * Nico Tumbagahan * No-Shows: * Gino Garcia * Gilda Declaro *\nKaren Geologo * Michelle Catedral * Reschedule: * Jessica Toledo Thank you,\nShannen Jaucian Clients Relationship Manager | HireSmart Virtual Employees\nShannen@hiresmartvirtualemployees.com Direct: (470) 866-4770 Book a time to\nmeet with our team! HOURS OF SUPPORT Monday – Thursday 8:30 AM EST to 6:30 PM\nEST Friday – 8:30 AM EST to 5:30 PM EST\n\n'),
    #           Email(id='Pamela Cruz', to='Julia Roberts at HireSmart <Julia@hiresmartvirtualemployees.com>', from_='HireSmart Customer Care <CustomerService@hiresmartvirtualemployees.com>', subject='COB - June 6, 2023', body='Hi Julia, Thank you for today! Here’s what I did for you today: 1\\\\. Responded\nto emails and filed them as needed. 2\\\\. Filed DocuSign contracts 3\\\\. Initial\npresentation for the initial deck for best practices in Client Interviews 4\\\\.\nMonitored Tawk.to 5\\\\. Processed bonuses/raises 6\\\\. Processed new orders 7\\\\.\nClient Interviews – CAMCO, Seabreeze, and TYCO – 3 VEs hired! 8\\\\. Drafted CI\nSchedules for next week Any pending items: 1\\\\. No pending items for today.\nWhat I need your assistance with: 1\\\\. ALL GOOD!! 😊 How I would rate my day:\n5/5 – It was a great, busy day! 😊 Good night! Thank you, Pamela Cruz Client\nRelationship Manager Your Customer Service & Support Team Julia | Anne | Pam |\nShannen CustomerService@hiresmartvirtualemployees.com Direct: (678) 894-9557\nBook a time to meet with our team! HOURS OF SUPPORT Monday – Thursday 8:30 AM\nEST to 6:30 PM EST Friday – 8:30 AM EST to 5:30 PM EST Emails/ Inquiries\noutside these hours will be addressed the next business day.\n\n'),
    #           Email(id='Alex Plant', to='anne@hiresmartvirtualemployees.com', from_='Alex Plant <alexathsve@gmail.com>', subject='COB 06/06/2023', body="Hello Boss, Happy Tuesday! Here's how my day went: \\\\- FB inquiry clean-up\n(comments and messenger) \\\\- Reviewed image assets for repurposing \\\\- Made 2\nsocial video assets \\\\- Produced 4 job opp image assets \\\\- Updated and\nrepurposed 2 image assets \\\\- Uploaded files in GDrive Things needed to work\non tomorrow: \\\\- HSVE PH Community Best Regards, Alex Plant Social Media\nManager for Hire Smart Virtual Employees [image: Text, logo Description\nautomatically generated]\n\n")]
    # emails[0].body += "\n1 person quit"
    feedbacks = FeedbackService().gen_feedbacks(emails)

    ReportProcessingService().process_reports(feedbacks)
    print('Done')
