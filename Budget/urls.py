from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    
    # Authentification
    path('', connexion, name='connexion'),
    path('code', code, name='code'),
    path('verification', verification, name='verification'),
    path('deconnexion/', deconnexion, name='deconnexion'),
    
    # Admin
    path('adminIndex', adminIndex, name="adminIndex"),
    path('adminUser', adminUser, name='adminUtilisateur'),
    path("supprimer/<int:id>/", supprimer_utilisateur, name="supprimer_utilisateur"),
    path("depense/<int:id>/", supprimer_depense, name="supprimer_depense"),
    path('adminSuivi', adminSuivi, name='adminSuivi'),
    path('adminStatistique', Stat, name='adminStatistique'),
    path('adminInfo/<int:id>/', adminInfo, name='adminInfo'),
    path('changercode', changercode, name='changercode'),
    path('changerbudget', changerbudget, name='changerbudget'),
    path("supprimer_budget/<int:id>/", supprimer_budget, name="supprimer_budget"),
    path('modife/<int:id>/', modifebudget, name='modifebudget'),
    path('changeradmin', changeradmin, name='changeradmin'),
    path('adminInfoparmois', adminInfoparmois, name='adminInfoparmois'),
    path('changerutilisateur/<int:id>/', changerutilisateur, name='changerutilisateur'),
    
    
    # COMPTABLE
    path('comptaIndex', comptaIndex, name="comptaIndex"),
    path('comptaSaisie', comptaSaisie, name="comptaSaisie"),
    path("supprimer_depense/<int:id>/", supprimer_depense, name="supprimer_depense"),
    path('comptaSuivi', comptaSuivi, name="comptaSuivi"),
    path('comptaStatistique', Stat1, name="comptaStatistique"),
    
    # Page 404 connexion
    path('page404', erreur404, name="page404"),
    path('admin404', admin404, name="admin404"),
    path('compta404', compta404, name="compta404"),
]

