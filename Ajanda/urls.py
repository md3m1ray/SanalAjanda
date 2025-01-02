from django.urls import path
from .views import add_note, list_notes, edit_note, delete_note, filter_notes, calendar_events, calendar_view, \
    get_notes_by_date

urlpatterns = [
    path('notes/add/', add_note, name='add_note'),
    path('notes/', list_notes, name='list_notes'),
    path('notes/edit/<int:note_id>/', edit_note, name='edit_note'),
    path('notes/delete/<int:note_id>/', delete_note, name='delete_note'),
    path('notes/filter/', filter_notes, name='filter_notes'),
    path('api/calendar-events/', calendar_events, name='calendar_events'),
    path('calendar/', calendar_view, name='calendar_view'),
    path('get-notes/', get_notes_by_date, name='get_notes_by_date'),
]
