# Takeout to SMS Backup & Restore

## Generally speaking...
Python script to convert SMSes from [Google Voice](http://www.google.com/voice) to [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore)

1. Get a [Google Takeout](https://www.google.com/settings/takeout) of your Google Voice data.
2. Extract zip file
3. Run t2sbr.py
4. Specify directory with Voice's SMS files (ex. ./Takeout/Voice/Calls/)
5. SMS Backup & Restore-compatibile xml file is created in t2sbr.py's directory

## Requirements

* Python 3
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers)
