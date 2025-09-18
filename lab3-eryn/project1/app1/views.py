from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from .models import Mahasiswa 

def mahasiswa(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            Mahasiswa.objects.create(
                nim = request.POST.get('nim'),
                firstname = request.POST.get('firstname'),
                lastname = request.POST.get('lastname'),
                jurusan = request.POST.get('jurusan')
            )

        elif action == 'update':
            mhs = Mahasiswa.objects.get(id=request.POST.get('id'))
            mhs.nim = request.POST.get('nim')
            mhs.firstname = request.POST.get('firstname')
            mhs.lastname = request.POST.get('lastname')
            mhs.jurusan = request.POST.get('jurusan')
            mhs.save()

        elif action == 'delete':
            Mahasiswa.objects.filter(id=request.POST.get('id')).delete()
            return redirect('mahasiswa')

    mymahasiswa = Mahasiswa.objects.all().values()
    no_data = not mymahasiswa 
    template = loader.get_template('index.html')
    context = {
        'mymahasiswa': mymahasiswa,
        'no_data': no_data,
    }
    return HttpResponse(template.render(context, request))
