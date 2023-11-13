from django.urls import path
from api_projects.views.distribution_user import UserCampaignListCreateView, UserCityListCreateView
from api_projects.views.group_channel import AssignGroupChannelsListView
from api_projects.views.metadata import ChannelMetadata
from api_projects.views.multiple_channel import CreateMultipleChannel
from api_projects.views.project_admin import ListProjectAdminView, ProjectAdmiInviteListCreateViewclass, ProjectAdminAccountListCreateView, ProjectAdminListCreateView, ProjectAdminRetrieveUpdateDeleteView
from api_projects.views.project_check import ProjectCheckCreateView
from api_projects.views.projects_creation import ProjectChannelsCreationView, ProjectCreationView

from .views.master_category import CategoryListCreateView, CategoryRetrieveUpdateDeleteView, CategoryStatusListCreateView
from .views.master_status import StatusListCreateView, StatusRetrieveUpdateDeleteView
from .views.master_media import ChannelMediaView, MediaListCreateView, MediaRetrieveUpdateDeleteView
from .views.fields import FieldListCreateView, FieldRetrieveUpdateDeleteView
from .views.forms import FormChannelView, FormFieldView, FormListCreateView, FormRetreiveUpdateDeleteView
from .views.project import AllStatusListCreateView, MinimalisCatView, MinimalisView, ProjectChannelListCreateView, ProjectDuplicateStatusListView, ProjectListCreateView, ProjectMetadataView, ProjectRetrieveUpdateDeleteView, ProjectStatusListView
from .views.campaign import CampaignListCreateView, CampaignRetrieveUpdateDeleteView, ProjectCampaignListCreateView
from .views.channel import CampaignChannelListCreateView, ChannelGroupListView, ChannelListCreateView, ChannelNameView, ChannelRetreiveUpdateDeleteView, ChannelByCodeView, MemberView, StatusMemberView
from .views.group_poject import GroupProjectListView, OngoingProjectListView, ProjectGroupListView, ProjectSalesListView
from .views.internal_check import InternalCheckView

urlpatterns = [   
   # metadata
   path('channels/metadata', ChannelMetadata.as_view()),

   #master categories
   path('master/categories', CategoryListCreateView.as_view()),
   path('master/categories/<int:pk>', CategoryRetrieveUpdateDeleteView.as_view()),
   path('master/categories/<int:pk>/statuses', CategoryStatusListCreateView.as_view()),

   #master status
   path('master/status', StatusListCreateView.as_view()),
   path('master/status/<int:pk>', StatusRetrieveUpdateDeleteView.as_view()),
   path('master/custom_status', ProjectMetadataView.as_view()),

   #master media
   path('master/medias', MediaListCreateView.as_view()),
   path('master/medias/<int:pk>', MediaRetrieveUpdateDeleteView.as_view()),

   #field
   path('rest/fields', FieldListCreateView.as_view()),
   path('rest/fields/<int:pk>', FieldRetrieveUpdateDeleteView.as_view()),

   # forms
   path('rest/forms', FormListCreateView.as_view()),
   path('rest/forms/<int:pk>', FormRetreiveUpdateDeleteView.as_view()),
   path('rest/forms/<int:pk>/fields', FormFieldView.as_view()),
   path('rest/forms/<int:pk>/channels', FormChannelView.as_view()),

   # #projects
   path('rest/projects', ProjectListCreateView.as_view()),
   path('rest/projects/<int:pk>', ProjectRetrieveUpdateDeleteView.as_view()),
   path('rest/projects/<int:pk>/campaigns', ProjectCampaignListCreateView.as_view()),
   path('rest/projects/<int:pk>/channels', ProjectChannelListCreateView.as_view()),
   path('rest/projects/<int:pk>/statuses', ProjectStatusListView.as_view()),
   path('rest/projects/<int:pk>/duplicate_status', ProjectDuplicateStatusListView.as_view()),
   path('rest/projects/<int:pk>/groups', ProjectGroupListView.as_view()),
   path('rest/ongoing_projects', OngoingProjectListView.as_view()),
   path('rest/projects/<int:pk>/sales', ProjectSalesListView.as_view()),
   
   # groups
   path('rest/groups/<int:pk>/channels', AssignGroupChannelsListView.as_view()),
   path('rest/groups/<int:pk>/projects', GroupProjectListView.as_view()),

   # project admin
   path('rest/projects/<int:pk>/admin', ProjectAdminListCreateView.as_view()),
   path('rest/projects/invite_admin', ProjectAdmiInviteListCreateViewclass.as_view()),
   path('rest/projects/exists_admin', ProjectAdminAccountListCreateView.as_view()),
   path('rest/projects/admin', ListProjectAdminView.as_view()),
   path('rest/projects/admin/<int:pk>', ProjectAdminRetrieveUpdateDeleteView.as_view()),

   # status
   path('statuses', AllStatusListCreateView.as_view()),

   # #campaigns
   path('rest/campaigns', CampaignListCreateView.as_view()),
   path('rest/campaigns/<int:pk>', CampaignRetrieveUpdateDeleteView.as_view()),
   path('rest/campaigns/<int:pk>/channels', CampaignChannelListCreateView.as_view()),

   # #channel
   path('rest/channels', ChannelListCreateView.as_view()),
   path('rest/channels/<int:pk>', ChannelRetreiveUpdateDeleteView.as_view()),
   path('rest/channels/<int:pk>/groups', ChannelGroupListView.as_view()),
   path('rest/channels/<int:pk>/members', MemberView.as_view()),
   path('rest/channels/<int:channel_pk>/members/<int:pk>', StatusMemberView.as_view()),
   path('rest/channels/name', ChannelNameView.as_view()),

   # click
   path('function/get_channel_by_code', ChannelByCodeView.as_view()),

   # minimalis
   path('minimal/project', MinimalisView.as_view()),
   path('minimal/category', MinimalisCatView.as_view()),

   # internal chehk
   path('internal/check', InternalCheckView.as_view()),

   # check
   path('projects/notif', ProjectCheckCreateView.as_view()),

   # endpoint leads creation
   path('creation/projects', ProjectCreationView.as_view()),
   path('creation/projects/<int:pk>/channels', ProjectChannelsCreationView.as_view()),

   # endpoint create banyak channel sekaligus
   path('create_multiple_channels', CreateMultipleChannel.as_view()),

   # user distribution focus
   path('user/<int:pk>/distribution_campaigns', UserCampaignListCreateView.as_view()),
   path('user/<int:pk>/distribution_city', UserCityListCreateView.as_view()),

]
