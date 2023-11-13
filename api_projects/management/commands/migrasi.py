import sys
import json
from django.core.management import BaseCommand
from django.db.models import fields
from api_projects.models import *
from django.utils.timezone import make_aware
from django.db import connections, connection

from api_projects.services import ExternalService


class Migrator:
    def __init__(self, account_id, force):
        self.conn = connections['old']
        self.account_id = account_id
        self.force = force

    def fetchall(self, cursor):
        """
        Return all rows from a cursor as a dict
        """
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    @staticmethod
    def make_tz_aware(data):
        if data is not None:
            return make_aware(data)

        return data

    def migrate(self):
        # migrate tabel dimensi/master
        self.migrate_master_lead_category()
        self.migrate_master_lead_status()
        self.migrate_master_form_field()
        self.migrate_project_master_channel_media()
        self.migrate_form()

        self.migrate_project()
        self.migrate_duplicate_lead()
        self.migrate_project_campaign()
        self.migrate_project_channel()
        self.migrate_channel_click()
        self.migrate_channel_team()

        self.migrate_project_lead_status()
        self.migrate_project_team()
        self.migrate_channel_member()
        self.migrate_custom_status()
        self.migrate_form_field()

        self.migrate_project_admin()
        self.migrate_all_project_admin()

    def migrate_duplicate_lead(self):
        """
        Get tabel _setting
        filter WHERE tenantid = self.account_id
        return all setting
        """
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT 
                *
                FROM _setting 
                where tenantid = %s and setting_id = 4 """,
                (self.account_id,))

            for row in self.fetchall(cursor):
                a = json.loads(row['value'])

                if(a['salesDuplicateLevel'] == 'project') :
                    sys.stdout.write(f"\t- Update duplicate lead tbl_project for account_id {row['tenantid']}\n")
                    Project.objects.filter(accountId=self.account_id).update(duplicate_lead=True)

                    # mbulet
                    # save status duplicate
                    proj = Project.objects.filter(accountId = self.account_id)
                    for p in proj:

                        pstatus = ProjectStatus.objects.filter(project_id=p.id, category_id=5).values()
                        singlep = list(pstatus)
                        
                        if singlep != [] :
                            pduplicatestatus = ProjectDuplicateStatus(
                                accountId = self.account_id,
                                name = singlep[0]['name'],
                                color = singlep[0]['color'],
                                category_id = singlep[0]['category_id'],
                                project_id = p.id,
                            
                            )
                            pduplicatestatus.save()

            # return project_ids

    def migrate_project(self):
        """
        Get tabel _project
        filter WHERE tenantid = self.account_id
        return all project_id
        """
        project_ids = []
        with self.conn.cursor() as cursor:
            cursor.execute(
                """SELECT
                    id, 
                    name,
                    detail,
                    modifiedby,
                    modifiedat,
                    createdby,
                    createdat,
                    tenantid,
                    periodstart,
                    periodend,
                    status
                FROM 
                    _project
                WHERE
                    tenantid = %s""",
                (self.account_id,)
            )

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t- Migrate from _project to tbl_project for project id {row['id']}\n")
                project = Project(
                    id=row['id'],
                    name=row['name'],
                    detail=row['detail'],
                    modifiedBy=row['modifiedby'],
                    modifiedAt=self.make_tz_aware(row['modifiedat']),
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    periodStart=self.make_tz_aware(row['periodstart']),
                    periodEnd=self.make_tz_aware(row['periodend']),
                    status=row['status']
                )
                project.save()
                project_ids.append(project.id)

            return project_ids

    def migrate_project_product(self):
        """
        migrate table -projectproduct
        filter WHERE tenantid = self.account_id
        return tidak ada karena tidak diperlukan oleh tabel lain
        """
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT 
                id, 
                createdby,
                createdat,
                tenantid,
                project_id,
                product_id
            FROM
                _projectproduct
            WHERE 
                tenantid = %s
            """, (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t- Migrate from _projectproduct to tbl_projectproduct "
                                 f"for product id {row['id']}\n")
                project_product = ProjectProduct(
                    id=row['id'],
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    project=Project.objects.get(id=row['project_id']),
                    productId=row['product_id']
                )
                project_product.save()

    def migrate_project_campaign(self):
        """
        migrate table _projectcampaign
        filter WHERE tenantid = self.account_id
        """
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                name,
                picture,
                modifiedby,
                modifiedat,
                createdby,
                createdat,
                tenantid,
                project_id,
                periodstart,
                periodend,
                status
            FROM
                _projectcampaign
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t- Migrate from _projectcampaign to tbl_campaign for campaign id {row['id']}\n")
                campaign = Campaign(
                    id=row['id'],
                    name=row['name'],
                    picture=row['picture'],
                    modifiedAt=self.make_tz_aware(row['modifiedat']),
                    modifiedBy=row['modifiedby'],
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    project=Project.objects.get(pk=row['project_id']),
                    periodStart=self.make_tz_aware(row['periodstart']),
                    periodEnd=self.make_tz_aware(row['periodend']),
                    status=row['status']
                )
                campaign.save()

    def migrate_setting(self):
        """
        migrate table _setting
        filter WHERE tenantid = self.account_id and setting_id = 1
        """
        sys.stdout.write("\t- Migrate from _setting to tbl_channel\n")
        with self.conn.cursor() as cursor:          
            cursor.execute("""SELECT
                *
            FROM
                _setting
            WHERE
                setting_id = 1 and tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                if (row != None) :
                    return row

    def migrate_project_channel(self):
        """
        migrate table _projectchannel
        filter WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _projectchannel to tbl_channel\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                name,
                detail,
                picture,
                uniquecode,
                modifiedby,
                modifiedat,
                createdby,
                createdat,
                tenantid,
                campaign_id,
                media_id,
                periodstart,
                periodend,
                click,
                form_id,
                redirecturl,
                status,
                defaultchannel
            FROM
                _projectchannel
            WHERE
                tenantid = %s""", (self.account_id,))
            
            res = self.migrate_setting()
            
            setting = None
            if (res != None) :
                setting = json.loads(res['value'])

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate channel id {row['id']}, account id {row['tenantid']}\n")
                channel = Channel(
                    id=row['id'],
                    name=row['name'],
                    detail=row['detail'],
                    picture=row['picture'],
                    uniqueCode=row['uniquecode'],
                    modifiedBy=row['modifiedby'],
                    modifiedAt=self.make_tz_aware(row['modifiedat']),
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    campaign=Campaign.objects.get(id=row['campaign_id']),
                    media=Media.objects.get(id=row['media_id']),
                    periodStart=self.make_tz_aware(row['periodstart']),
                    periodEnd=self.make_tz_aware(row['periodend']),
                    click=row['click'],
                    form=Form.objects.get(id=row['form_id']) if row['form_id'] else None,
                    redirectUrl=row['redirecturl'],
                    status=row['status'],
                    distributionType='roundRobin',
                    enableRedistribution = setting['enabled'] if setting else False,
                    idleDuration = setting['idleDuration'] if setting else "30",
                    startTime = setting['startTime'] if setting else "08:00:00",
                    endTime = setting['endTime'] if setting else "17:00:00"
                    # defaultchannel is not used,
                    # media name is not used,
                )
                channel.save()

    def migrate_project_master_channel_media(self):
        """
        migrate table _masterchannelmedia
        filter WHERE id = [media_id] dari migrate_project_channel()
        """
        # gal jadi pakek ini biar custom media gak ke skip
        # if Media.objects.count() > 0 and not self.force:
        #     sys.stdout.write("\t- Master Media (tbl_mastermedia) is already migrated, skip\n")
        #     return

        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                name,
                type,
                sort,
                picture,
                isactive,
                tenantid
            FROM
                _masterchannelmedia
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _mastermedia {row['id']}, account id {row['tenantid']}\n")
                media = Media(
                    id=row['id'],
                    name=row['name'],
                    type=row['type'],
                    sort=row['sort'],
                    picture=row['picture'],
                    isActive=row['isactive'],
                    accountId = row['tenantid']
                )
                media.save()

    def migrate_channel_click(self):
        """
        migrate table _channelclick
        filter WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _channelclick to tbl_channelclick\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                createdby,
                createdat,
                tenantid,
                channel_id
            FROM
                _channelclick
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _channelclick id {row['id']}, account id {row['tenantid']}\n")
                channel_click = ChannelClick(
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    channel=Channel.objects.get(id=row['channel_id'])
                )
                channel_click.save()

    def migrate_channel_team(self):
        """
        migrate table _channelteam
        filter: WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _channelteam to tbl_channelgroup\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                createdby,
                createdat,
                tenantid,
                channel_id,
                team_id
            FROM
                _channelteam
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _channelteam id {row['id']}, account id {row['tenantid']}\n")
                channel_group = ChannelGroup(
                    id=row['id'],
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    channel=Channel.objects.get(id=row['channel_id']),
                    teamId=row['team_id']
                )
                channel_group.save()

    def migrate_project_team(self):
        """
        migrate table _channelteam ct
        filter: WHERE ct.tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _channelteam ct to tbl_projectteam\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                ca.project_id,
                ct.team_id,
                ct.tenantid
            FROM
                _channelteam ct
            JOIN
                _projectchannel ch on ct.channel_id = ch.id
            JOIN
                _projectcampaign ca on ch.campaign_id = ca.id
            WHERE
                ct.tenantid = %s
            GROUP BY
                ca.project_id, ct.team_id, ct.tenantid
            ORDER BY
                ca.project_id, ct.team_id, ct.tenantid""", (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _channelteam project_id {row['project_id']}, team_id {row['team_id']}, account id {row['tenantid']}\n")
                channel_group = ProjectTeam(
                    # id=row['id'],
                    teamId=row['team_id'],
                    project_id=row['project_id'],
                    accountId=row['tenantid'],
                    # createdAt=self.make_tz_aware(row['createdat']),
                    # createdBy=row['createdby']      
                )
                channel_group.save()

    def migrate_channel_member(self):
        """
        migrate table _teammember tm
        filter: WHERE tm.tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _teammember ct to tbl_channelsettingmember\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                tm.user_id,
                tm.team_id,
                ct.channel_id,
                ct.tenantid
            FROM
                _teammember tm
            JOIN
                _channelteam ct on tm.team_id = ct.team_id
            WHERE
                ct.tenantid = %s
            GROUP BY
                tm.user_id, tm.team_id, ct.channel_id, ct.tenantid
            ORDER BY
                tm.user_id, tm.team_id, ct.channel_id, ct.tenantid""", (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _teammember channel_id {row['channel_id']}, user_id {row['user_id']}, team_id {row['team_id']}, account id {row['tenantid']}\n")
                channel_group = ChannelSettingMember(
                    # id=row['id'],
                    channel_id=row['channel_id'],
                    userId=row['user_id'],
                    teamId=row['team_id'],
                    accountId=row['tenantid'],
                    # createdAt=self.make_tz_aware(row['createdat']),
                    # createdBy=row['createdby']      
                )
                channel_group.save()

    def migrate_project_lead_status(self):
        """
        migrate table _projectleadstatus
        filter WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _projectleadstatus to tbl_projectstatus\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                point,
                modifiedby,
                modifiedat,
                createdby,
                createdat,
                tenantid,
                project_id,
                name,
                detail,
                sort,
                color,
                category_id
            FROM
                _projectleadstatus
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                project_status = ProjectStatus(
                    id=row['id'],
                    point=row['point'],
                    modifiedBy=row['modifiedby'],
                    modifiedAt=self.make_tz_aware(row['modifiedat']),
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    project=Project.objects.get(pk=row['project_id']),
                    name=row['name'],
                    # detail is not migrated
                    sort=row['sort'],
                    color=row['color'],
                    category=Category.objects.get(pk=row['category_id'])
                )
                project_status.save()

    def migrate_master_lead_category(self):
        """
        migrate table _masterleadcategory
        filter: WHERE id = category_id from migrate_project_lead_status()
        """
        if Category.objects.count() > 0 and not self.force:
            sys.stdout.write(f"\t- Category (tbl_mastercategory) is already migrated, skip\n")
            return

        sys.stdout.write(f"\t- Migrate from _masterleadcategory to tbl_category\n")

        with self.conn.cursor() as cursor:
                cursor.execute(
                    """SELECT
                    id,
                    name,
                    sort,
                    color,
                    availability,
                    picture,
                    isactive
                FROM
                    _masterleadcategory"""
                )

                for old_category in self.fetchall(cursor):
                    category = Category(
                        id=old_category['id'],
                        name=old_category['name'],
                        sort=old_category['sort'],
                        color=old_category['color'],
                        availability=old_category['availability'],
                        picture=old_category['picture'],
                        isActive=old_category['isactive']
                    )
                    category.save()

    def migrate_master_lead_status(self):
        """
        migrate table _masterleadstatus
        filter: WHERE category_id = category_id from mgirate_project_lead_status()
        """
        if Status.objects.count() > 0 and not self.force:
            sys.stdout.write("\t- Master Status (tbl_masterstatus) is already migrated, skipped\n")
            return

        sys.stdout.write("\t- Migrate from _masterleadstatus to tbl_masterstatus\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                tenantcategory,
                name,
                detail,
                sort,
                point,
                color,
                category_id,
                isactive
            FROM    
                _masterleadstatus""")

            for row in self.fetchall(cursor):
                master_status = Status(
                    id=row['id'],
                    tenantCategory=row['tenantcategory'],
                    name=row['name'],
                    detail=row['detail'],
                    sort=row['sort'],
                    point=row['point'],
                    color=row['color'],
                    category=Category.objects.get(id=row['category_id']),
                    isActive=row['isactive']
                )
                master_status.save()

    def migrate_form(self):
        """
        migrate table _form
        filter: WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _form to tbl_form\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                name,
                detail,
                type,
                pageurl,
                modifiedby,
                modifiedat,
                createdby,
                createdat,
                tenantid
            FROM 
                _form
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                form = Form(
                    id=row['id'],
                    name=row['name'],
                    detail=row['detail'],
                    type=row['type'],
                    pageUrl=row['pageurl'],
                    modifiedBy=row['modifiedby'],
                    modifiedAt=self.make_tz_aware(row['modifiedat']),
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid']
                )
                form.save()

    def migrate_form_field(self):
        """
        migrate table _formfield
        filter: WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _formfield to tbl_formfield\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                createdby,
                createdat,
                tenantid,
                field_id,
                form_id
            FROM
                _formfield
            WHERE
                tenantid = %s""", (self.account_id,))

            for row in self.fetchall(cursor):
                form_field = FormField(
                    id=row['id'],
                    createdBy=row['createdby'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    accountId=row['tenantid'],
                    field=Field.objects.get(id=row['field_id']),
                    form=Form.objects.get(id=row['form_id']),
                )

                form_field.save()

    def migrate_master_form_field(self):
        """
        migrate table _masterformfield
        proses migrasi akan dilakukan 1 kali karena ini merupakan tabel dimensi,
        akan ada argument force sehingga proses migrasi bisa dijalankan kembali
        """
        total = Field.objects.count()

        if total > 0 and not self.force:
            sys.stdout.write("\t- Master Form Field (tbl_field) is already migrated, user --force argument to update\n")
            return

        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                id,
                name,
                type,
                mandatory,
                displayedas,
                alias,
                parameters
            FROM
                _masterformfield""")

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t- Migrate from _masterformfield to tbl_field for field id {row['id']}\n")
                field = Field(
                    id=row['id'],
                    name=row['name'],
                    type=row['type'],
                    mandatory=row['mandatory'],
                    displayedas=row['displayedas'],
                    alias=row['alias'],
                    parameters=row['parameters']
                )
                field.save()
    
    def migrate_custom_status(self):
        """
        migrate table _projectleadstatus ct
        filter: WHERE tenantid = self.account_id, name not in (select distinct name from "_masterleadstatus" )
        """
        sys.stdout.write("\t- Migrate from _projectleadstatus ct to tbl_customstatus\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                name,
                detail,
                point,
                category_id,
                sort,
                color,
                tenantid
            FROM
                _projectleadstatus
            WHERE
                tenantid = %s and name not in ( select distinct name from "_masterleadstatus" )
            GROUP BY
                name,
                detail,
                point,
                category_id,
                sort,
                color,
                tenantid
            """, (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _projectleadstatus {row['name']}, account id {row['tenantid']}\n")
                custom_status = CustomStatus(
                    name=row['name'],
                    detail=row['detail'],
                    accountId=row['tenantid'],
                    color=row['color'],
                    sort=row['sort'],
                    point=row['point'],
                    category_id=row['category_id']
                )
                custom_status.save()

    def migrate_project_admin(self):
        """
        migrate table _userproject up
        filter: WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _userproject ct to tbl_projectadmin\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                u.user_id,
                u.project_id,
                u2.role,
                u.tenantid,
                u.createdby,
                u.createdat,
                u2.status,
                u2.email
            FROM
                _userproject u
            JOIN
                _user u2 on u2.id = u.user_id
            WHERE
                u.tenantid = %s and u2.role = 'admin'

            """, (self.account_id,))

            for row in self.fetchall(cursor):
                sys.stdout.write(f"\t\t- Migrate _userproject {row['project_id']}, account id {row['tenantid']}\n")
                p_admin = ProjectAdmin(
                    userId=row['user_id'],
                    project_id=row['project_id'],
                    accountId=row['tenantid'],
                    status=row['status'],
                    email=row['email'],
                    createdAt=self.make_tz_aware(row['createdat']),
                    createdBy=row['createdby']
                )
                p_admin.save()
    
    def migrate_all_project_admin(self):
        """
        migrate table _userproject up
        filter: WHERE tenantid = self.account_id
        """
        sys.stdout.write("\t- Migrate from _userproject ct to tbl_projectadmin\n")
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT
                u.id, 
                u.email, 
                u.role,
                u.tenantid,
                u.createdat,
                u.createdby,
                u.status
            FROM
                _user u
            LEFT JOIN
                _userproject u2 ON u.id = u2.user_id 
            WHERE
                u.tenantid = %s and u.role = 'admin' and u2.user_id IS NULL

            """, (self.account_id,))

            project = Project.objects.filter(accountId = self.account_id).values_list('id', flat=True)
             
            for row in self.fetchall(cursor):  
                sys.stdout.write(f"\t\tMigrate all project for user id {row['id']}\n")             
                for p in list(project):
                    
                    sys.stdout.write(f"\t\t- Migrate _userproject {row['id']}, project id {p}\n")
                    p_admin = ProjectAdmin(
                        userId=row['id'],
                        project_id=p,
                        accountId=row['tenantid'],
                        email=row['email'],
                        status=row['status'],
                        createdAt=self.make_tz_aware(row['createdat']),
                        createdBy=row['createdby']
                    )
                    p_admin.save()

                # for p in list(project):


    def script_patch_admin(self):
        
        with connection.cursor() as cursor:
            cursor.execute("""SELECT
                *
            FROM
                tbl_projectadmin
            WHERE
                \"accountId\" = %s

            """, (self.account_id,))
            
            getuserId = ExternalService().get_user_by_account_id(account_id=self.account_id)
            for row in self.fetchall(cursor):

                sys.stdout.write(f"\t\t- update email {row['userId']}, account id {row['accountId']}\n")
                chann = next((x for x in getuserId if x['id'] == row['userId']), 0)
                if (chann != 0) :
                    ProjectAdmin.objects.filter(accountId=self.account_id, userId=chann['id']).update(email=chann['email'])

class Command(BaseCommand):
    help = "Migrasi data dari database lama ke database baru berdasarkan Account ID (Tenant ID)"

    def add_arguments(self, parser):
        parser.add_argument('account_id', nargs='+', type=int)
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        for account_id in options['account_id']:
            sys.stdout.write(f"Migrate data for account id {account_id}\n")

            migrator = Migrator(account_id=account_id, force=options['force'])
            migrator.migrate()

        sys.stdout.write("Finish migrating data\n")
