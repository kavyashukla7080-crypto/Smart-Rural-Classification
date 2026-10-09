# Create your views here.
from django.shortcuts import redirect, render
from django.contrib import messages
from users.models import UserRegistrationModel

def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        if usrid == 'admin' and pswd == 'admin':
            request.session['admin_logged_in'] = True
            request.session['admin_id'] = usrid
            messages.success(request, 'Login Successful!')
            return redirect('AdminHome') 
        elif usrid == 'Admin' and pswd == 'Admin':
            request.session['admin_logged_in'] = True
            request.session['admin_id'] = usrid
            messages.success(request, 'Login Successful!')
            return redirect('AdminHome') 
        else:
            messages.warning(request, 'Please Check Your Login Details')
            return render(request, 'AdminLogin.html', {})
    
    return render(request, 'AdminLogin.html', {})


def ViewRegisteredUsers(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/RegisteredUser.html', {'data': data})


def AdminActivaUsers(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/RegisteredUser.html', {'data': data})


def AdminHome(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    total_users = UserRegistrationModel.objects.count()
    active_users = UserRegistrationModel.objects.filter(status='activated').count()
    pending_approvals = UserRegistrationModel.objects.filter(status='waiting').count()

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'admins/AdminHome.html', context)

def DeleteUsers(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    if request.method == 'GET':
        id = request.GET.get('uid')
        UserRegistrationModel.objects.filter(id=id).delete()
        data = UserRegistrationModel.objects.all()
        return redirect('ViewRegisteredUsers')

def AdminLogout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('AdminLogin')
