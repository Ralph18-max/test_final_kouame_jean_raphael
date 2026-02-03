
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Customer

@pytest.mark.django_db
def test_profil_view_requires_login(client):
    url = reverse('profil')
    response = client.get(url)
    assert response.status_code == 302  # Redirects to login
    login_url = reverse('login')
    assert login_url in response.url

from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_profil_view_authenticated(client):
    # Setup user and customer
    user = User.objects.create_user(username='testuser', password='password')
    
    # Create a dummy image for the photo field
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    uploaded_image = SimpleUploadedFile(name='test_image.jpg', content=image_content, content_type='image/jpeg')
    
    Customer.objects.create(user=user, adresse="Abidjan", contact_1="01020304", photo=uploaded_image)
    
    client.login(username='testuser', password='password')
    
    url = reverse('profil')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'profil.html' in [t.name for t in response.templates]
    assert response.context['user'] == user

from customer.models import Commande, ProduitPanier
from shop.models import Produit, CategorieEtablissement, CategorieProduit, Etablissement

@pytest.mark.django_db
def test_commande_view(client):
    # Setup
    user = User.objects.create_user(username='testuser_cmd', password='password')
    
    # Create dummy image for customer photo
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    uploaded_image = SimpleUploadedFile(name='test_image_cmd.jpg', content=image_content, content_type='image/jpeg')
    
    customer = Customer.objects.create(user=user, adresse="Abidjan", contact_1="01020304", photo=uploaded_image)
    
    # Create dependencies for Order
    cat_etab = CategorieEtablissement.objects.create(nom="Resto")
    cat_prod = CategorieProduit.objects.create(nom="Plats", categorie=cat_etab)
    etab = Etablissement.objects.create(
        user=User.objects.create_user('owner', 'pass', first_name='Owner', last_name='Test'),
        nom="Resto1", categorie=cat_etab, contact_1="01", email="e@e.com", logo="l.png", couverture="c.png",
        nom_du_responsable="Responsable", prenoms_duresponsable="Prenom"
    )
    prod = Produit.objects.create(nom="P1", prix=1000, categorie=cat_prod, etablissement=etab)
    
    # Create Order
    commande = Commande.objects.create(customer=customer, transaction_id="TRANS123", prix_total=2000)
    ProduitPanier.objects.create(commande=commande, produit=prod, quantite=2)
    
    client.login(username='testuser_cmd', password='password')
    
    # Test List View
    url = reverse('commande')
    response = client.get(url)
    assert response.status_code == 200
    assert 'TRANS123' in str(response.content)
    
    # Test Detail View
    url_detail = reverse('commande-detail', args=[commande.id])
    response_detail = client.get(url_detail)
    assert response_detail.status_code == 200
    assert 'commande-detail.html' in [t.name for t in response_detail.templates]

@pytest.mark.django_db
def test_souhait_view(client):
    user = User.objects.create_user(username='test_souhait', password='password')
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    uploaded_image = SimpleUploadedFile(name='test.jpg', content=image_content, content_type='image/jpeg')
    Customer.objects.create(user=user, adresse="Abidjan", contact_1="01", photo=uploaded_image)
    
    client.login(username='test_souhait', password='password')
    url = reverse('liste-souhait')
    response = client.get(url)
    assert response.status_code == 200
    assert 'liste-souhait.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_parametre_view(client):
    user = User.objects.create_user(username='test_param', password='password')
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    uploaded_image = SimpleUploadedFile(name='test.jpg', content=image_content, content_type='image/jpeg')
    Customer.objects.create(user=user, adresse="Abidjan", contact_1="01", photo=uploaded_image)
    
    client.login(username='test_param', password='password')
    url = reverse('parametre')
    
    # GET
    response = client.get(url)
    assert response.status_code == 200
    assert 'parametre.html' in [t.name for t in response.templates]
    
    # POST
    # Need a City for this
    from cities_light.models import City, Country
    country = Country.objects.create(name='CI', continent='Africa', phone=225)
    city = City.objects.create(name='Abidjan', country=country)
    
    data = {
        'first_name': 'NewFirst',
        'last_name': 'NewLast',
        'contact': '01020304',
        'city': str(city.id),
        'address': 'NewAddr'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == 'NewFirst'

from unittest.mock import patch

@pytest.mark.django_db
def test_invoice_pdf_view(client):
    # Setup
    user = User.objects.create_user(username='test_invoice', password='password')
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    uploaded_image = SimpleUploadedFile(name='test.jpg', content=image_content, content_type='image/jpeg')
    cust = Customer.objects.create(user=user, adresse="Abidjan", contact_1="01", photo=uploaded_image)
    
    # Need Order
    from customer.models import Commande
    from website.models import SiteInfo
    SiteInfo.objects.create(email="site@test.com", logo="logo.png")
    
    cmd = Commande.objects.create(customer=cust, transaction_id="TINV", prix_total=1000)
    
    client.login(username='test_invoice', password='password')
    url = reverse('invoice_pdf', args=[cmd.id])
    
    # Mock playwright
    with patch('client.views.sync_playwright') as mock_playwright:
        mock_browser = mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value
        mock_page = mock_browser.new_page.return_value
        mock_page.pdf.return_value = b'%PDF-1.4...'
        
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
