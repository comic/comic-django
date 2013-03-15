from django.shortcuts import redirect

import pdb
import userena.views as userena_views


def profile(request):
    """
    Redirect to the profile page of the currently signed in user.
    """
    if request.user.is_authenticated():
        print "username: ", request.user.username
        return redirect('/accounts/'+request.user.username)
    else:
        return redirect('/accounts/signin')

