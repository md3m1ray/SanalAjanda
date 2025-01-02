from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import NoteForm
from .models import Note
from django.http import JsonResponse
from sanalAjanda import settings
from cryptography.fernet import Fernet
from django.contrib import messages

cipher = Fernet(settings.ENCRYPTION_KEY)

@login_required
def add_note(request):
    """
    Yeni bir not ekleme işlemi.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            # İçeriği şifrele
            note.content = cipher.encrypt(form.cleaned_data['content'].encode()).decode()
            note.save()
            messages.success(request, "Not başarıyla eklendi.")
            return redirect('calendar_view')
    else:
        form = NoteForm()
    return render(request, 'notes/add_note.html', {'form': form})

@login_required
def list_notes(request):
    """
    Kullanıcının notlarını listeleme işlemi.
    """
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
    """
    Ajanda görünümü için template render eder.
    """
    return render(request, 'notes/calendar_view.html')

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