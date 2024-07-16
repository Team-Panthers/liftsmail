from django.urls import path
from .views import GroupListCreateView, GroupDetailView, AddContactsView, ProcessEmailsView, ContactListCreateView, ContactDetailView

urlpatterns = [
    # URL pattern for listing all groups or creating a new group
    path('', GroupListCreateView.as_view(), name='group-list-create'),

    # URL pattern for retrieving, updating, or deleting a specific group
    path('<int:pk>/', GroupDetailView.as_view(), name='group-detail'),

    # URL pattern for adding contacts to a specific group by json
    path('<int:pk>/add-contacts/', AddContactsView.as_view(), name='add-contacts'),

    # URL pattern for processing emails to add contacts to a specific group by csv file or json file
    path('<int:pk>/process-emails/', ProcessEmailsView.as_view(), name='process-emails'),

    # URL pattern for listing all contacts in a specific group or creating a new contact within the group
    path('<int:pk>/contacts/', ContactListCreateView.as_view(), name='contact-list-create'),

    # URL pattern for retrieving, updating, or deleting a specific contact within a specific group
    path('<int:group_id>/contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
]
