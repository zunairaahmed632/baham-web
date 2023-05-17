from collections import defaultdict

from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from baham.constants import COLOURS
from baham.enum_types import VehicleStatus
from baham.models import Vehicle, VehicleModel, UserProfile
from django.shortcuts import get_object_or_404


# Create your views here.
def view_index(request):
    template = loader.get_template('home.html')
    # Fetch the last 20 records
    vehicles = Vehicle.objects.filter(status=VehicleStatus.AVAILABLE.name).order_by('-date_added')[:18]
    all_vehicles = []
    current_user_id = request.user.id
    for vehicle in vehicles:
        owner = UserProfile.objects.get(pk=vehicle.owner.id)
        obj = {
            'vehicle_id': vehicle.vehicle_id,
            'registration_number': vehicle.registration_number,
            'colour': vehicle.colour,
            'vendor': vehicle.model.vendor,
            'model': vehicle.model.model,
            'type': vehicle.model.type,
            'owner_bio': owner.bio,
            'owner_town': owner.town,
            'owner_first_name': owner.user.first_name,
            'owner_last_name': owner.user.last_name,
            'picture1_url': vehicle.picture1
        }
        all_vehicles.append(obj)

    context = {
        "navbar": "home",
        "vehicles": all_vehicles
    }
    return HttpResponse(template.render(context, request))


def view_members(request):
    template = loader.get_template('members.html')
    context = {
        "navbar": "members"
    }
    return HttpResponse(template.render(context, request))


def view_vehicles(request):
    template = loader.get_template('vehicles.html')
    vehicles = Vehicle.objects.filter(status=VehicleStatus.AVAILABLE.name).order_by('-date_added')
    all_vehicles = []
    current_user_id = request.user.id
    for vehicle in vehicles:
        owner = UserProfile.objects.get(pk=vehicle.owner.id)
        obj = {
            'vehicle_id': vehicle.vehicle_id,
            'registration_number': vehicle.registration_number,
            'colour': vehicle.colour,
            'vendor': vehicle.model.vendor,
            'model': vehicle.model.model,
            'type': vehicle.model.type,
            'owner_town': owner.town,
            'owner_name': owner.user.username,
            'picture1_url': vehicle.picture1,
            'picture2_url': vehicle.picture2,
            'allow_edit': current_user_id == owner.id
        }
        all_vehicles.append(obj)

    context = {
        "navbar": "vehicles",
        "vehicles": all_vehicles
    }
    return HttpResponse(template.render(context, request))


def view_vehicle(request, id):
    template = loader.get_template('editvehicle.html')
    vehicle = Vehicle.objects.get(pk=id)
    current_user_id = request.user.id
    owner = UserProfile.objects.get(pk=vehicle.owner.id)
    obj = {
        'vehicle_id': vehicle.vehicle_id,
        'registration_number': vehicle.registration_number,
        'colour': vehicle.colour,
        'vendor': vehicle.model.vendor,
        'model': vehicle.model.model,
        'type': vehicle.model.type,
        'owner_town': owner.town,
        'owner_first_name': owner.user.first_name,
        'owner_last_name': owner.user.last_name,
        'picture1_url': vehicle.picture1,
        'picture2_url': vehicle.picture2,
        'allow_edit': current_user_id == owner.id
    }
    context = {
        "navbar": "vehicles",
        "vehicle": obj
    }
    return HttpResponse(template.render(context, request))


def create_vehicle(request):
    template = loader.get_template('createvehicle.html')
    models = VehicleModel.objects.all().values_list('model_id', 'vendor', 'model', 'type').order_by('type', 'vendor', 'model').values()
    # FIXME: Is the below even required if the client desires only the owner to be able to create/alter vehicles?
    users = User.objects.filter(is_superuser=False, is_active=True).all().values_list('id', 'first_name', 'last_name', 'email').order_by('first_name', 'last_name').values()
    context = {
        "navbar": "vehicles",
        "models": models,
        "users": users,
        "colours": COLOURS,
    }
    return HttpResponse(template.render(context, request))


def save_vehicle(request):
    registration_number = request.POST.get('registrationNumberText', None)
    colour = request.POST.get('colourSelection', None)
    model_id = request.POST.get('modelSelection', None)
    owner_id = request.user.id  # Since only the person who has logged in can be the owner
    status = request.POST.get('statusCheck', None)
    if not registration_number or not model_id or not owner_id:
        return HttpResponse('<h3 class="danger">Error! Required parameters are missing.<h3>')
    model = VehicleModel.objects.filter(pk=model_id).get()
    # FIXME: this is redundant, why not fetch the user directly?
    owner = UserProfile.objects.filter(pk=owner_id).get()

    obj = Vehicle(registration_number=registration_number, colour=colour, model=model,
                  owner=owner.user, status=status)
    if request.FILES.get('frontImage'):
        obj.picture1 = request.FILES.get('frontImage')
    if request.FILES.get('frontImage'):
        obj.picture2 = request.FILES.get('sideImage')
    obj.save()
    return HttpResponseRedirect(reverse(view_vehicles))

def delete_vehicle(request, id):
    obj = get_object_or_404(Vehicle, pk = id)
    obj.delete(voided_by=request.user)
    return HttpResponseRedirect(reverse(view_vehicles))

def undelete_vehicle(request, id):
    obj = get_object_or_404(Vehicle, pk = id)
    obj.undelete()
    return HttpResponseRedirect(reverse(view_vehicles))

def view_aboutus(request):
    template = loader.get_template('aboutus.html')
    context = {
        "navbar": "aboutus"
    }
    return HttpResponse(template.render(context, request))
