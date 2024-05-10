from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from .models import *
from .forms import budgetForm
from django.db.models import Sum
from datetime import datetime
import pytz

def erreur404(request):
    return render(request, '404.html')

# Authentification
def connexion(request):
    request.session.flush()
    
    if request.method == "POST":
        pseudo = request.POST.get("pseudo")
        mdp = request.POST.get("mdp")
        
        # Utilisation de Django ORM pour récupérer l'utilisateur correspondant
        try:
            us = Utilisateurs.objects.get(pseudo=pseudo, mdp=mdp)
        except Utilisateurs.DoesNotExist:
            return render(request, 'Authentification/connexion.html', {'error_message': "Nom ou mot de passe incorrect.", 'pseudo':pseudo})
        
        role = us.role  # Récupérer le rôle de l'utilisateur à partir du modèle Utilisateur
        
        # Création de la session pour l'utilisateur connecté
        
        if role == 'Admin':
            request.session['admin_id'] = us.id
            return redirect('adminIndex')
        elif role == 'Comptable':
            request.session['comptable_id'] = us.id
            return redirect('comptaIndex')
    
    return render(request, 'Authentification/connexion.html')

def deconnexion(request):
    # Supprimer toutes les données de session
    request.session.flush()
    # Rediriger l'utilisateur vers la page de connexion ou toute autre page appropriée
    return redirect('connexion')

def verification(request):
    request.session.flush()
    code_v = Code_valid_comptable.objects.get(pk=1)
    
    if request.method == "POST":     
        pseudo = request.POST.get('pseudo')
        mdp = request.POST.get('mdp')
        mdp2 = request.POST.get('mdp2')
        contact = request.POST.get('contact')
        
        # Vérification que les mots de passe correspondent
        if mdp != mdp2 or str(mdp).isspace():
            return render(request, 'Authentification/verification.html', {'error_message': "Les mots de passe ne correspondent pas.", 'code_v':code_v, 'pseudo':pseudo, 'contact':contact})
        
        if str(pseudo).isspace():
            return render(request, 'Authentification/verification.html', {'error_message': "On ne peut pas avoir un pseudo invalid", 'code_v':code_v, 'pseudo':pseudo, 'contact':contact})
        
        # Vérification si le pseudo est déjà utilisé
        if Utilisateurs.objects.filter(pseudo=pseudo).exists():
            return render(request, 'Authentification/verification.html', {'error_message': "Ce nom est déjà utilisé.", 'code_v':code_v})
        # Création de l'objet Utilisateur avec le mot de passe hashé
        utilisateurs = Utilisateurs(pseudo=pseudo, mdp=mdp, contact=contact, role='Comptable')
        utilisateurs.save()
        
        # Création de la session pour l'utilisateur nouvellement inscrit
        request.session['comptable_id'] = utilisateurs.id
        
        return redirect('comptaIndex')
    
    return render(request, 'Authentification/verification.html', {'code_v':code_v})

def code(request):
    if request.method == "POST":
        code_v = Code_valid_comptable.objects.get(pk=1)
        verife = request.POST.get('verife')
        
        # Vérification que les mots de passe correspondent
        if verife != code_v.code:
            return render(request, 'Authentification/code.html', {'message': "Le code de verification est incorrect"})
        else:
            return redirect('inscription')
    return render(request, 'Authentification/code.html')

# Supprimer utilisateur
def supprimer_utilisateur(request, id):
    if request.method == 'POST':
        Utilisateur = Utilisateurs.objects.get(pk=id)
        Utilisateur.delete()
    
    return redirect('adminUtilisateur')

def supprimer_depense(request, id):
    if request.method == 'POST':
        Depense = Depense_budget.objects.get(pk=id)
        Depense.delete()
    
    return redirect('adminSuivi')

# Admin
def admin404(request):
    try:    
        pass
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/404.html')
 
def compta404(request):
    try:
        pass
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/404.html')

def adminIndex(request):
    try:   
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            utilisateur = Utilisateurs.objects.get(id=1)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
            
            code_valid = Code_valid_comptable.objects.all()
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/index.html', {'users':users, 'solde':solde, 'budget': budget, 'total_montant': total_montant, 'total_depense': total_depense, 'code_valid': code_valid, 'utilisateur':utilisateur} )

def adminUser(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            utilisateurs = Utilisateurs.objects.exclude(id=1).all()
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/Utilisateur.html', {'utilisateurs':utilisateurs, 'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde})

def adminSuivi(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all().order_by('-id')
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
    # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/Suivi.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'depense':depense})

def adminInfoparmois(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            mois_annee = request.GET.get('mois')
            mois, selected_year = mois_annee.split("-")

            # Dictionnaire pour mapper le nom du mois à son numéro
            mois_dict = {
                "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
            }

            # Convertir le nom du mois en minuscules et obtenir son numéro
            mois_int = mois_dict.get(mois.lower())

            # Récupérer les dépenses pour le mois et l'année spécifiés
            depenses = Depense_budget.objects.filter(date__month=mois_int, date__year=selected_year)



    except Utilisateurs.DoesNotExist:
    # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/infoparmois.html', {'mois':mois, 'depenses':depenses})

def adminInfo(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:     
            depense1 = Depense_budget.objects.get(pk=id)    
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all().order_by('-id')
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/info.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'depense':depense, 'depense1':depense1})

# Statistique
def Stat(request):
    try:   
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            selected_year = request.GET.get('selected_year')
            if selected_year:
                selected_year = int(selected_year)
            else:
                # Si aucune année n'est sélectionnée, utilisez l'année actuelle
                selected_year = timezone.now().year

            # Récupération de tous les objets Valeur_budget
            budget_initial = Valeur_budget.objects.filter(date_budget__year=selected_year).aggregate(Sum('budget_initial'))['budget_initial__sum'] or 0

            # Liste des mois en français
            mois_fr = {
                1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
                5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
                9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
            }

            # Initialisation du dictionnaire pour stocker les totaux par mois
            depenses_par_mois = {mois: 0 for mois in mois_fr.values()}

            # Récupération des dépenses pour chaque mois et l'année sélectionnée
            for mois_num in range(1, 13):
                # Filtrage des dépenses pour le mois en cours et l'année sélectionnée
                depenses_mois = Depense_budget.objects.filter(date__year=selected_year, date__month=mois_num)
                # Calcul du total des dépenses pour le mois en cours
                total_mois = depenses_mois.aggregate(total=Sum('montant'))['total'] or 0
                # Stockage du total dans le dictionnaire
                depenses_par_mois[mois_fr[mois_num]] = total_mois

            # Calcul du pourcentage des dépenses par rapport au budget initial
            depenses_en_pourcentage = {}
            for mois, total in depenses_par_mois.items():
                if budget_initial != 0:
                    pourcentage = (total / budget_initial) * 100
                else:
                    pourcentage = 0
                depenses_en_pourcentage[mois] = pourcentage
                
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    
    return render(request, 'Administrateur/Statistique.html', {'depenses_en_pourcentage': depenses_en_pourcentage, 'selected_year': selected_year, 'budget_initial': budget_initial, 'depenses_mois': depenses_mois})

def changercode(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else: 
            if request.method == "POST":     
                verifec = request.POST.get('verifec')
                code_modifier = Code_valid_comptable.objects.get(pk=1)
                code_modifier.code = verifec
                code_modifier.save()
                return redirect('adminIndex')
            code_modifie = Code_valid_comptable.objects.get(pk=1)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/changercode.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'code_modifie':code_modifie})

def changerutilisateur(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else: 
            if request.method == "POST":     
                pseudo = request.POST.get('pseudo')
                contact = request.POST.get('contact')
                mdp = request.POST.get('mdp')
                user_modifier = Utilisateurs.objects.get(pk=id)
                user_modifier.pseudo = pseudo
                user_modifier.contact = contact
                user_modifier.mdp = mdp
                user_modifier.save()
                return redirect('adminUtilisateur')
            utilisateur = Utilisateurs.objects.get(pk=id)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/changerutilisateur.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'utilisateur':utilisateur})

def changeradmin(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else: 
            if request.method == "POST":
                pseudo = request.POST.get('pseudo')
                mdp = request.POST.get('mdp')
                contact = request.POST.get('contact')
                admin_modifier = Utilisateurs.objects.get(pk=1)
                admin_modifier.pseudo = pseudo
                admin_modifier.mdp = mdp
                admin_modifier.contact = contact
                
                admin_modifier.save()
                return redirect('adminIndex')
            admin_info = Utilisateurs.objects.get(pk=1) 
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/changeradmin.html', {'total_montant': total_montant, 'total_depense': total_depense, 'solde':solde, 'admin_info':admin_info })

# Ajout budget
def changerbudget(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            if request.method == "POST":
                budget_initial = request.POST.get('budget_initial')
                
                # Obtenir le fuseau horaire de Madagascar
                fuseau_horaire_madagascar = pytz.timezone('Indian/Antananarivo')
        
                # Obtenir la date et l'heure actuelles dans le fuseau horaire de Madagascar
                date_budget = datetime.now(fuseau_horaire_madagascar)
                
                # Obtenir l'heure actuelle dans le fuseau horaire de Madagascar
                time_budget = date_budget.time()
                
                # Vérifier si le budget initial est supérieur à zéro
                if float(budget_initial) <= 0:
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return HttpResponse("Le budget initial doit être supérieur à zéro.")
                else:
                    insert = Valeur_budget(budget_initial=budget_initial, date_budget=date_budget, time=time_budget)
                    insert.save()       
                    return redirect('adminIndex')
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/changerbudget.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde})

# Supprimer budget
def supprimer_budget(request, id):
    if 'comptable_id' in request.session:
        # Accéder à la valeur de la clé 'comptable_id'
        comptable_id = request.session['comptable_id']
        return redirect("page404")
    # Faites ce que vous devez faire avec comptable_id
    else:
        if request.method == 'POST':
            budget = Valeur_budget.objects.get(pk=id)
            budget.delete()
        
    return redirect('adminIndex')

def modifebudget(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            budget = Valeur_budget.objects.get(pk=id)
            if request.method == "POST":  
                budget_initial = request.POST.get('budget_initial')
                
                 # Vérifier si le budget initial est supérieur à zéro
                if float(budget_initial) <= 0:
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return HttpResponse("Le budget initial doit être supérieur à zéro.")
                else:
                    budget_modifier = Valeur_budget.objects.get(pk=id)
                    budget_modifier.budget_initial = budget_initial

                    budget_modifier.save()
                    return redirect('adminIndex')
                
            budget1 = Valeur_budget.objects.get(pk=id)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']   
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/modifebudget.html', {'budget':budget, 'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'budget1':budget1})

# COMPTABLE
def comptaIndex(request):
    try:
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin_id_id'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']     
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            # Session
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense  
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/index.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde})


def comptaSaisie(request):
    try:
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin_id_id'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            affichedepense = Depense_budget.objects.all().order_by('-id')
            
            solde = total_montant - total_depense
            # Session
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            if request.method == "POST":     
                rubrique = request.POST.get('rubrique')
                ligne = request.POST.get('ligne')
                montant = request.POST.get('montant')
                obs = request.POST.get('obs')
                
                # Vérifier si le budget initial est supérieur à zéro
                if float(montant) <= 0:
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return HttpResponse("Le montant doit être supérieur à zéro.")
                else:
                    # Obtenir le fuseau horaire de Madagascar
                    fuseau_horaire_madagascar = pytz.timezone('Indian/Antananarivo')
            
                    # Obtenir la date et l'heure actuelles dans le fuseau horaire de Madagascar
                    date = datetime.now(fuseau_horaire_madagascar)
            
                    # Obtenir l'heure actuelle dans le fuseau horaire de Madagascar
                    times = date.time()
                    
                    # Calculer le nouveau solde après l'insertion de la dépense
                    nouveau_solde = solde - int(montant)
                    
                    # Vérifier si le nouveau solde est négatif
                    if nouveau_solde >= 0:
                        # Créer et enregistrer l'objet de dépense uniquement si le solde n'est pas négatif
                        depense = Depense_budget(rubrique=rubrique, ligne=ligne, date=date, times=times, montant=montant, obs=obs, users_id=users)
                        depense.save()
                        return redirect('comptaSaisie')
                    else:
                        # Si le solde devient négatif après l'insertion de la dépense, renvoyer une réponse HTTP 403 (Forbidden)
                        return render(request, "Comptable/Saisie.html", {'error_message': "votre budget est atteint, vous ne pouvez pas inserer.", 'total_montant': total_montant, 'affichedepense': affichedepense, 'total_depense': total_depense , 'solde':solde})
   
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/Saisie.html', {'total_montant': total_montant, 'affichedepense': affichedepense, 'total_depense': total_depense , 'solde':solde})


def comptaSuivi(request):
    try:
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin_id_id'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all().order_by('-id')
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            # Session
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
                
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/Suivi.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde , 'depense':depense})

def Stat1(request):
    try:   
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            selected_year = request.GET.get('selected_year')
            if selected_year:
                selected_year = int(selected_year)
            else:
                # Si aucune année n'est sélectionnée, utilisez l'année actuelle
                selected_year = timezone.now().year

            # Récupération du budget initial
            budget_initial_obj = Valeur_budget.objects.first()  # Supposons qu'il n'y a qu'un seul objet dans le modèle
            budget_initial = budget_initial_obj.budget_initial

            # Liste des mois en français
            mois_fr = {
                1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
                5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
                9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
            }

            # Initialisation du dictionnaire pour stocker les totaux par mois
            depenses_par_mois = {mois: 0 for mois in mois_fr.values()}

            # Récupération des dépenses pour chaque mois et l'année sélectionnée
            for mois_num in range(1, 13):
                # Filtrage des dépenses pour le mois en cours et l'année sélectionnée
                depenses_mois = Depense_budget.objects.filter(date__year=selected_year, date__month=mois_num)
                # Calcul du total des dépenses pour le mois en cours
                total_mois = depenses_mois.aggregate(total=Sum('montant'))['total'] or 0
                # Stockage du total dans le dictionnaire
                depenses_par_mois[mois_fr[mois_num]] = total_mois

            # Calcul du pourcentage des dépenses par rapport au budget initial
            depenses_en_pourcentage = {mois: (total / budget_initial) * 100 for mois, total in depenses_par_mois.items()}
            # Couleurs d'arrière-plan pour chaque mois

    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/Statistique.html', {'depenses_en_pourcentage': depenses_en_pourcentage, 'selected_year': selected_year})

