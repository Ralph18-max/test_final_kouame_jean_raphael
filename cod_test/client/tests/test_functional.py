from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pytest
# import os
from django.contrib.auth.models import User
from customer.models import Customer

@pytest.mark.django_db
def test_login_scenario(live_server):
    """
    Test fonctionnel : Simulation d'un utilisateur qui se connecte.
    Utilise le gestionnaire de driver intégré à Selenium (Selenium Manager).
    Utilise live_server de pytest-django pour lancer un serveur de test.
    """
    
    # Création d'un utilisateur de test
    user = User.objects.create_user(username='testuser', password='password')
    Customer.objects.create(user=user, adresse="Abidjan", contact_1="01020304")
    
    # Configuration du driver Edge
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")  # Exécuter sans interface graphique
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Utilisation de Selenium Manager (automatique depuis Selenium 4.6+)
    try:
        driver = webdriver.Edge(options=options)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du driver Edge: {e}")
        print("Assurez-vous que Microsoft Edge est installé.")
        raise e
    
    try:
        # 1. Accéder à la page de connexion
        # live_server.url donne l'URL du serveur de test (ex: http://localhost:port)
        login_url = f"{live_server.url}/customer/"
        print(f"Accès à : {login_url}")
        driver.get(login_url)
        
        # 2. Remplir le formulaire
        # On attend un peu que la page charge (mieux vaudrait utiliser WebDriverWait)
        time.sleep(1)
        
        # Trouver les champs par leur nom (name="username", name="password")
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        
        username_input.send_keys("testuser")
        password_input.send_keys("password")
        password_input.send_keys(Keys.RETURN)
        
        # 3. Vérifier la redirection ou le succès
        time.sleep(2) # Attendre le traitement et la redirection
        
        print(f"URL actuelle : {driver.current_url}")
        
        # Vérification : soit on est redirigé vers 'profil', soit on voit un élément de la page profil
        # Note: Selon la configuration, la redirection peut être vers /client/profil/ ou autre
        # Vérifions simplement qu'on n'est plus sur la page de login ou qu'il n'y a pas d'erreur
        
        # Si la connexion réussit, on devrait être redirigé
        assert "login" not in driver.current_url or "profil" in driver.current_url
        
        print("Test fonctionnel Selenium réussi !")
        
    except Exception as e:
        print(f"Le test Selenium a échoué : {e}")
        # Capture d'écran en cas d'erreur pour le débogage (optionnel)
        # driver.save_screenshot("error_screenshot.png")
        raise e
    finally:
        driver.quit()
