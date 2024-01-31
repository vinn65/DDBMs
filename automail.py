import yagmail
import os
import datetime
date = datetime.date.today().strftime("%B %d, %Y")
path = 'Attendance'
os.chdir(path)
files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
newest = files[-1]
filename = newest
sub = "Attendance Report for " + str(date)
# mail information
yag = yagmail.SMTP("Vinniev960@gmail.com", "password")

# sent the mail
yag.send(
    to="vinnie_m_15@students.uonbi.ac.ke",
    subject="Subject", # email subject
    contents="PFA",  # email body
    attachments= filename  # file attached
)
print("Email Sent!")
