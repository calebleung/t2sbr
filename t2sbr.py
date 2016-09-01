from bs4 import BeautifulSoup
import os
import phonenumbers
import time, datetime
import warnings

sms_backup_filename = './' + str(time.time()) + '-sms_backup.xml'

def main(sms_backup_filename):
    warnings.warn("user warnings", UserWarning)
    num_sms  = 0
    root_dir = input('Directory with Voice SMSes: (ex. ./Takeout/Voice/Calls/) ')

    if not os.path.lexists(root_dir):
        print('Can\'t find directory. Defaulting to current directory.')
        root_dir = '.'

    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            sms_filename = os.path.join(subdir, file)

            try:
                sms_file = open(sms_filename, 'r')
            except FileNotFoundError:
                continue

            if os.path.splitext(sms_filename)[1] != '.html':
                continue

            soup = BeautifulSoup(sms_file, 'html.parser')

            if not len(soup.findAll(attrs = {'class': 'hChatLog'})):
                continue

            authors_raw  = soup.find_all('cite')
            messages_raw = soup.find_all('q')
            times_raw    = soup.findAll(attrs = {'class': 'dt'})

            num_sms += len(messages_raw)

            sms_values = { 'phone' : get_phone(authors_raw) }

            for i in range(len(messages_raw)):
                sms_values['author']  = get_author(authors_raw[i])
                sms_values['message'] = get_message(messages_raw[i]) 
                sms_values['time']    = get_time(times_raw[i])

                sms_text = ('<sms protocol="0" address="%(phone)s" '
                            'date="%(time)s" type="%(author)s" '
                            'subject="null" body="%(message)s" '
                            'toa="null" sc_toa="null" service_center="null" '
                            'read="1" status="1" locked="0" /> \n' % sms_values)

                sms_backup_file = open(sms_backup_filename, 'a')
                sms_backup_file.write(sms_text)
                sms_backup_file.close()

    sms_backup_file = open(sms_backup_filename, 'a')
    sms_backup_file.write('</smses>')
    sms_backup_file.close()

    write_header(sms_backup_filename, num_sms)

def get_phone(authors_raw):

    for author_raw in authors_raw:
        if not author_raw.find_all('span'):
            continue

        try:
            phone_number = phonenumbers.parse(author_raw.a['href'][4:], None)
        except phonenumbers.phonenumberutil.NumberParseException:
            return author_raw.a['href'][4:]

        # '1' as in US country code, not b/c it's True
        if phone_number.country_code == 1:
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)[1:].replace(' ', '-')
        else:
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    
    return 0


def get_author(author_raw):
    if not author_raw.find_all('span'):
        return 2
    else:
        return 1

    return 0

def get_message(message_raw):
    return BeautifulSoup(message_raw.text, 'html.parser').prettify(formatter='html').strip()

def get_time(time_raw):
    timestamp = ''.join(time_raw['title'].rsplit(':', 1))

    return int(time.mktime(datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())) * 1000

def write_header(sms_backup_file, num_sms):
    sms_backup_file = open(sms_backup_filename, 'r')
    sms_backup_text = sms_backup_file.read()
    sms_backup_file.close()

    sms_backup_file = open(sms_backup_filename, 'w')
    sms_backup_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
    sms_backup_file.write('<!-- File created by Takeout to SMS Backup & Restore -->\n')
    sms_backup_file.write('<smses count="' + str(num_sms) + '">\n')
    sms_backup_file.write(sms_backup_text)
    sms_backup_file.close()

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    main(sms_backup_filename)

# <sms 
#    protocol="0" 
#    address="1-321-555-000"        (Phone number)
#    date="1352403022000"           (Add 3 zeroes at the end of a 'normal' unix timestamp; think they're for miliseconds)
#    type="2"                       (1 is received, 2 is sent)
#    subject="null" 
#    body="Hello world"             (The actual message) 
#    toa="null" 
#    sc_toa="null" 
#    service_center="null" 
#    read="1" 
#    status="1" 
#    locked="0" 
# /> 