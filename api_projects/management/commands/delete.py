import sys
import json
from django.core.management import BaseCommand
from django.db.models import fields
from api_projects.models import *
from django.utils.timezone import make_aware
from django.db import connection

class Migrator:
    def __init__(self, accountId):
        self.conn = connection
        self.accountId = accountId


    @staticmethod
    def make_tz_aware(data):
        if data is not None:
            return make_aware(data)

        return data

    def delete(self):

        self.delete_channel_click()
        self.delete_channel_group()
        self.delete_channel_member()
        self.delete_channel()
        self.delete_campaign()
        self.delete_form_field()
        self.delete_form()
        self.delete_project_product()
        self.delete_project_status()
        self.delete_custom_status()
        self.delete_project_status_duplicate()
        self.delete_project_team()
        self.delete_project_admin()
        self.delete_project()

    def delete_project(self):

        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_project where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete project from accountId {self.accountId}\n")
    
    def delete_project_admin(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_projectadmin where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete project admin from accountId {self.accountId}\n")

    def delete_project_team(self):
    
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_projectteam where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete project team from accountId {self.accountId}\n")

    def delete_project_status(self):
    
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_projectstatus where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete project status from accountId {self.accountId}\n")

    def delete_custom_status(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_customstatus where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete custom status from accountId {self.accountId}\n")
    
    def delete_project_status_duplicate(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_project_duplicatestatus where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete project duplicate status from accountId {self.accountId}\n")
    
    def delete_project_product(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM \"tbl_projectProduct\" where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete project product from accountId {self.accountId}\n")
    
    def delete_form(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_form where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete form from accountId {self.accountId}\n")

    def delete_form_field(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_formfield where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete form field from accountId {self.accountId}\n")
    
    def delete_channel_member(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_channelsettingmember where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete channel member from accountId {self.accountId}\n")

    def delete_channel_group(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_channelgroup where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete channel group from accountId {self.accountId}\n")
    
    def delete_channel_click(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_channelclick where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete channel click from accountId {self.accountId}\n")
    
    def delete_channel(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_channel where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete channel from accountId {self.accountId}\n")
    
    def delete_campaign(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM tbl_campaign where \"accountId\" =  %s """, [self.accountId])

            return sys.stdout.write(f"\t- Delete campaign from accountId {self.accountId}\n")

class Command(BaseCommand):
    help = "Delete by Account ID"

    def add_arguments(self, parser):
        parser.add_argument('accountId', nargs='+', type=int)

    def handle(self, *args, **options):
        for accountId in options['accountId']:
            # sys.stdout.write(f"Delete data for account id {accountId}\n")

            migrator = Migrator(accountId=accountId)
            migrator.delete()

        sys.stdout.write("Finish deleting data\n")
