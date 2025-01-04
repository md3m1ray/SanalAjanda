from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Ajanda.forms import NoteForm
from django.http import JsonResponse
from sanalAjanda import settings
from cryptography.fernet import Fernet
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from Ajanda.models import Note
from django.core.serializers.json import DjangoJSONEncoder
import json


cipher = Fernet(settings.ENCRYPTION_KEY)

@login_required
def add_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)

            # Kullanıcının türünü kontrol et
            if request.user.user_type == "secretary" and request.user.master_user:
                note.user = request.user.master_user  # Sekreterse, master_user'a kaydet
            else:
                note.user = request.user  # Normal kullanıcı ise kendi adına kaydet

            note.created_by = request.user
            note.save()
            return redirect('calendar_view')  # Kullanıcıyı takvim görünümüne yönlendirin
    else:
        form = NoteForm()

    return render(request, 'notes/add_note.html', {'form': form})

@login_required
def list_notes(request):
    """
    Kullanıcının notlarını listeleme işlemi.
    """
    if request.user.user_type == "secretary" and request.user.master_user:
        notes = Note.objects.filter(user=request.user.master_user).order_by('-date', '-time')
    else:
        notes = Note.objects.filter(user=request.user).order_by('-date', '-time')

    # Şifrelenmiş içeriği çöz
    for note in notes:
        try:
            note.content = cipher.decrypt(note.content.encode()).decode()
        except Exception:
            note.content = "Hata: İçerik çözülemedi."
    return render(request, 'notes/list_notes.html', {'notes': notes})

@login_required
def edit_note(request, note_id):
    """
    Mevcut bir notu düzenleme işlemi.
    """
    if request.user.user_type == "secretary" and request.user.master_user:
        note = get_object_or_404(Note, id=note_id, user=request.user.master_user)
    else:
        note = get_object_or_404(Note, id=note_id, user=request.user)
    try:
        decrypted_content = cipher.decrypt(note.content.encode()).decode()
    except Exception:
        decrypted_content = ""

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)
            note.content = cipher.encrypt(form.cleaned_data['content'].encode()).decode()
            note.save()
            messages.success(request, "Not başarıyla güncellendi.")
            return redirect('list_notes')
    else:
        form = NoteForm(instance=note, initial={'content': decrypted_content})

    return render(request, 'notes/edit_note.html', {'form': form, 'note': note})

@login_required
def delete_note(request, note_id):
    """
    Mevcut bir notu silme işlemi.
    """
    if request.user.user_type == "secretary" and request.user.master_user:
        note = get_object_or_404(Note, id=note_id, user=request.user.master_user)
    else:
        note = get_object_or_404(Note, id=note_id, user=request.user)

    if request.method == "POST":
        note.delete()
        messages.success(request, "Not başarıyla silindi.")
        return redirect('list_notes')
    return render(request, 'notes/confirm_delete.html', {'note': note})

@login_required
def filter_notes(request):
    """
    Notları başlık veya içerik üzerinden filtreleme işlemi.
    """
    query = request.GET.get('query', '')
    if request.user.user_type == "secretary" and request.user.master_user:
        notes = Note.objects.filter(user=request.user.master_user, title__icontains=query).order_by('-date', '-time')
    else:
        notes = Note.objects.filter(user=request.user, title__icontains=query).order_by('-date', '-time')
    for note in notes:
        try:
            note.content = cipher.decrypt(note.content.encode()).decode()
        except Exception:
            note.content = "Hata: İçerik çözülemedi."
    return render(request, 'notes/filter_notes.html', {'notes': notes, 'query': query})

@login_required
def calendar_events(request):
    """
    Ajanda için JSON formatında etkinlikleri döner.
    """
    if request.user.user_type == "secretary" and request.user.master_user:
        notes = Note.objects.filter(user=request.user.master_user)
    else:
        notes = Note.objects.filter(user=request.user)

    events = []
    for note in notes:
        try:
            description = cipher.decrypt(note.content.encode()).decode()
        except Exception:
            description = "Hata: İçerik çözülemedi."
        events.append({
            "title": note.title,
            "start": note.date.isoformat(),
            "description": description,
        })
    return JsonResponse(events, safe=False)

@login_required
def calendar_view(request):
    return render(request, 'notes/calendar_view.html')

@login_required
def how_to_use(request):
    return render(request, 'notes/how_to_use.html')

@login_required
def version_info(request):
    return render(request, 'notes/version_info.html')

@login_required
def get_notes_by_date(request):
    date = request.GET.get('date')  # Tıklanan tarih
    if date:
        notes = Note.objects.filter(user=request.user, date=date)
        # Şifre çözme işlemi
        notes_data = []
        for note in notes:
            notes_data.append({
                'id': note.id,
                'title': note.title,
                'content': note.get_content()  # Şifre çözülmüş içerik
            })
        return JsonResponse({'success': True, 'notes': notes_data})
    return JsonResponse({'success': False, 'error': 'No date provided'})

@login_required
def note_dashboard(request):
    if request.user.user_type == 'secretary' and request.user.master_user:
        user = request.user.master_user
    else:
        user = request.user

    # Toplam Not Sayısı
    total_notes = Note.objects.filter(user=user).count()

    # Toplam Girilen Gün Sayısı
    total_days = Note.objects.filter(user=user).dates('date', 'day').count()

    # Yaklaşan Etkinlikler
    upcoming_events = Note.objects.filter(user=user, date__gt=now().date()).order_by('date')[:5]

    # Aylık İstatistikler
    monthly_stats = (
        Note.objects.filter(user=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Sekreterlerin Girdiği Notlar
    if request.user.user_type == 'master':
        secretary_notes = Note.objects.filter(user=user, created_by__user_type='secretary').count()
    else:
        secretary_notes = 0

    context = {
        'total_notes': total_notes,
        'total_days': total_days,
        'secretary_notes': secretary_notes,
        'upcoming_events': upcoming_events,
        'monthly_stats': json.dumps(list(monthly_stats), cls=DjangoJSONEncoder),
    }

    return render(request, 'notes/note_dashboard.html', context)