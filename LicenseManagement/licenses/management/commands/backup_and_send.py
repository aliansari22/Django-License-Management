from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess
import zipfile
import os


class Command(BaseCommand):
	help = 'Backup database and send to Telegram'

	def handle(self, *args, **kwargs):
		# Call dbbackup command
		pass
		#call_command('dbbackup')
		# Call the script to send the latest backup to Telegram
		#subprocess.run(['python', 'send_backup_to_telegram.py'])
