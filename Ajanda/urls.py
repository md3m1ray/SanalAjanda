from django.urls import path
from Ajanda.views import add_note, list_notes, edit_note, delete_note, filter_notes, calendar_events, calendar_view, \
    get_notes_by_date, note_dashboard, how_to_use, version_info

urlpatterns = [
    path('notes/add/', add_note, name='add_note'),
    path('notes/', list_notes, name='list_notes'),
    path('notes/edit/<int:note_id>/', edit_note, name='edit_note'),
    path('notes/delete/<int:note_id>/', delete_note, name='delete_note'),
    path('notes/filter/', filter_notes, name='filter_notes'),
    path('api/calendar-events/', calendar_events, name='calendar_events'),
    path('calendar/', calendar_view, name='calendar_view'),
    path('dashboard/', note_dashboard, name='note_dashboard'),
    path('how-to-use/', how_to_use, name='how_to_use'),
    path('version-info/', version_info, name='version_info'),
    path('get-notes/', get_notes_by_date, name='get_notes_by_date'),
]
