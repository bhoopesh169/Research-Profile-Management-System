from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import contact_info, UserProfile
from .forms import FileUploadForm, UserProfileForm
from .models import UploadedFile
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import contact_info
from django.http import Http404, HttpResponseNotAllowed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from plotly.offline import plot
import plotly.graph_objs as go
import numpy as np



# Create your views here.
def home(request):
    return render(request, 'RPMS/home.html')
    # return HttpResponse('Home Page')

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'RPMS/loginuser.html', {'form':AuthenticationForm()})
    else:
        a = request.POST.get('username')
        b = request.POST.get('password')
        user = authenticate(request, username=a, password=b)
        if user is None:
            return render(request,'RPMS/loginuser.html', {'form':AuthenticationForm(), 'error':'Invalid Credentials'})
        else:
            login(request, user)
            return redirect('home')


def registration(request):
        if request.method == 'GET':
            return render(request, 'RPMS/registration.html', {'form':UserCreationForm()})
        else:
            a = request.POST.get('username')
            b = request.POST.get('password1')
            c = request.POST.get('password2')
            d = request.POST.get('name')
            e = request.POST.get('department')
            f = request.POST.get('position')
            g = request.POST.get('education')
            h = request.POST.get('research_interests')
            i = request.FILES['profile_photo']
            j = request.POST.get('email')
            if b==c:
                #Check whether user name is unique
                if (User.objects.filter(username = a)):
                    return render(request, 'RPMS/registration.html', {'error':'Username Already Exists Try again with different username'})
                else:
                    user = User.objects.create_user(username = a, password=b)
                    user.save()
                    usrp = UserProfile(user=user,name=d,department=e,position=f,education=g,research_interests=h, profile_photo=i, email=j)
                    usrp.save()
                    login(request,user)
                    return redirect('home')
            else:
                return render(request, 'RPMS/registration.html', {'form':UserCreationForm(), 'error':'Password Mismatch Try Again'})
        
def logoutuser(request):
    if request.method == 'GET':
        logout(request)
        return redirect('home')
    
def aboutus(request):
    return render(request, 'RPMS/aboutus.html')

def contact(request):
    # return HttpResponse('<h1>this is the contact page</h1>')
    if request.method == 'GET':
        return render(request, 'RPMS/contact.html')
    elif request.method == 'POST':
        email = request.POST.get('user_email')
        message = request.POST.get('message')
        x = contact_info(u_email=email, u_message=message)
        x.save()
        print(email)
        print(message)
        return render(request,'RPMS/contact.html',{'feedback':'Your message has been recorded'})

@login_required(login_url='loginuser')   
def profile(request):
    user = request.user
    profile = UserProfile.objects.get(user=user) 
    uploaded_files = UploadedFile.objects.filter(user=request.user)
    return render(request, 'RPMS/profile.html', {'uploaded_files': uploaded_files, 'user': user, 'profile': profile})

@login_required(login_url='loginuser')
def edit_profile(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Loop through form fields and update profile fields accordingly
            for field in form.cleaned_data:
                setattr(profile, field, form.cleaned_data[field])
            profile.save()
            return redirect('profile')  # Redirect back to profile page
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'RPMS/edit_profile.html', {'form': form})

@login_required(login_url='loginuser')
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.user = request.user
            uploaded_file.save()
            
            # Increment user points
            user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
            user_profile.points += 1
            user_profile.save()
            
            return redirect('profile')
    else:
        form = FileUploadForm()
    return render(request, 'RPMS/upload_file.html', {'form': form})


def charts(request):
    points_range = [(0, 10), (11, 20), (21, 30), (31,40), (41,50)]  # Define points range
    users_data = []
    labels = []

    for start, end in points_range:
        users_count = UserProfile.objects.filter(points__range=(start, end)).count()
        users_data.append(int(users_count))  # Cast to integer
        labels.append(f"{start}-{end}")

    return JsonResponse({'labels': labels, 'usersData': users_data})


    
def download_contact_info(request):
    contact_information = contact_info.objects.all()
    content = "\n".join([f"{info.u_email}, {info.u_message}" for info in contact_information])
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_info.csv"'
    return response

@user_passes_test(lambda u: u.is_superuser, login_url='/')
def logistics(request):
    if request.method == 'GET':
        contact_information = contact_info.objects.all()
        return render(request, 'RPMS/logistics.html', {'contact_information': contact_information})
    else:
        raise Http404()
    

@user_passes_test(lambda u: u.is_superuser, login_url='/')
def delete_message(request, message_id):
    if request.method == 'DELETE':
        try:
            message = contact_info.objects.get(pk=message_id)
            message.delete()
            return JsonResponse({'message': 'Message deleted successfully'}, status=200)
        except contact_info.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def leaderboard(request):
    user_profiles = UserProfile.objects.order_by('-points')
    paginator = Paginator(user_profiles, 5)  # Show 5 user profiles per page

    page_number = request.GET.get('page')
    try:
        user_profiles = paginator.page(page_number)
    except PageNotAnInteger:
        user_profiles = paginator.page(1)
    except EmptyPage:
        user_profiles = paginator.page(paginator.num_pages)

    # Calculate starting rank for each page
    start_rank = (user_profiles.number - 1) * paginator.per_page + 1

    return render(request, 'RPMS/leaderboard.html', {'user_profiles': user_profiles, 'start_rank': start_rank})


def user_profile(request, user_id):
    y=get_object_or_404(User, pk=user_id)
    z=get_object_or_404(UserProfile, user=y)
    uploaded_files = UploadedFile.objects.filter(user=z.user)
    return render(request, 'RPMS/user_profile.html', {"z":z, 'uploaded_files': uploaded_files})

@login_required(login_url='loginuser')
def delete_profile(request, user_id):
    if request.method == 'POST':
        # Fetch the user by ID
        user = get_object_or_404(User, id=user_id)
        
        # Delete the user's profile and associated data
        user.delete()
        
        # Redirect to the home page or any other page
        return redirect('home')
    else:
        # Handle other request methods appropriately
        # For example, return a 405 Method Not Allowed response
        return HttpResponseNotAllowed(['POST'])


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def stats(request):
    if request.method == 'GET':
        # Fetch all users
        all_users = User.objects.all()

        # Create a list to store user statistics
        user_stats = []
        for user in all_users:
            date_joined = user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else "Never"
            user_stat = {'id': user.id, 'username': user.username, 'date_joined': date_joined, 'last_login': last_login}
            user_stats.append(user_stat)

        return render(request, 'RPMS/stats.html', {'user_stats': user_stats})
    else:
        raise Http404()
    

def chart_data(request):
    x_values = np.linspace(0, 10, 100)  # Sample x values
    y_values = np.sin(x_values)          # Sample y values

    # Line Plot
    line_plot = go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines',
        name='Line Plot'
    )

    # Bar Chart
    bar_chart = go.Bar(
        x=['A', 'B', 'C', 'D'],
        y=[10, 20, 15, 25],
        name='Bar Chart'
    )

    # Scatter Plot
    scatter_plot = go.Scatter(
        x=np.random.rand(50),
        y=np.random.rand(50),
        mode='markers',
        name='Scatter Plot'
    )

    # Pie Chart
    labels = ['A', 'B', 'C', 'D']
    values = [25, 35, 20, 20]
    pie_chart = go.Pie(
        labels=labels,
        values=values,
        name='Pie Chart'
    )

    # Create subplots
    fig = go.Figure(data=[line_plot, bar_chart, scatter_plot, pie_chart])

    # Update layout
    fig.update_layout(
        title='Plotly Charts Example',
        xaxis=dict(title='X Axis'),
        yaxis=dict(title='Y Axis'),
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Generate HTML for the plots
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render(request, 'RPMS/charts.html', context={'plot_div': plot_div})

def allprofiles(request):
    user_profiles = UserProfile.objects.all()
    return render(request, 'RPMS/allprofiles.html', {'user_profiles': user_profiles})