from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Customer
import json

class CustomerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.customer = Customer.objects.create(
            user=self.user,
            adresse="Abidjan",
            contact_1="01020304"
        )

    def test_login_url_resolves(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_customer_creation(self):
        """Test Customer model creation"""
        self.assertEqual(self.customer.user.username, 'testuser')
        self.assertEqual(self.customer.contact_1, "01020304")
        self.assertEqual(str(self.customer), "testuser")

    def test_islogin_ajax_success(self):
        """Test AJAX login with correct credentials"""
        url = reverse('post')
        data = {
            'username': 'testuser',
            'password': 'password'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_islogin_ajax_fail(self):
        """Test AJAX login with incorrect credentials"""
        url = reverse('post')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])

    def test_inscription_ajax(self):
        """Test AJAX signup logic"""
        url = reverse('inscription')
        
        # Prepare valid data
        data = {
            'username': 'newuser',
            'nom': 'New',
            'prenoms': 'User',
            'email': 'new@test.com',
            'phone': '05050505',
            'ville': '1', # Assuming city ID 1 exists or handled
            'adresse': 'Plateau',
            'password': 'password123',
            'passwordconf': 'password123'
        }
        
        # Need to mock City or handle it. The view does: City.objects.get(id=int(ville))
        # So we need a City object
        from cities_light.models import City, Country
        country = Country.objects.create(name='CI', continent='Africa', phone=225)
        city = City.objects.create(name='Abidjan', country=country)
        data['ville'] = str(city.id)
        
        # Since the view expects POST data (request.POST.get), not JSON body for this specific view based on code reading
        # "nom = request.POST.get('nom')" -> This implies Form data, not JSON body
        # However, line 149 "request.FILES['file']" implies file upload.
        # Let's mock a file too.
        from django.core.files.uploadedfile import SimpleUploadedFile
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        file = SimpleUploadedFile("avatar.jpg", image_content, content_type="image/jpeg")
        data['file'] = file
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_add_to_cart(self):
        """Test adding item to cart (AJAX)"""
        # Create dependencies
        from shop.models import Produit, CategorieEtablissement, CategorieProduit, Etablissement
        from customer.models import Panier
        from django.contrib.sessions.models import Session
        
        # Setup Product
        cat_etab = CategorieEtablissement.objects.create(nom="Resto")
        cat_prod = CategorieProduit.objects.create(nom="Plats", categorie=cat_etab)
        etab = Etablissement.objects.create(
            user=User.objects.create_user('shopowner', 'pass', first_name='O', last_name='D'),
            nom="Resto1", categorie=cat_etab, contact_1="01", email="e@e.com", logo="l.png", couverture="c.png",
            nom_du_responsable="Responsable", prenoms_duresponsable="Prenom"
        )
        produit = Produit.objects.create(nom="P1", prix=1000, categorie=cat_prod, etablissement=etab)
        
        # Setup Panier (requires Session or Customer)
        panier = Panier.objects.create(customer=self.customer)
        
        url = reverse('add_to_cart')
        data = {
            'panier': panier.id,
            'produit': produit.id,
            'quantite': 2
        }
        
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(panier.produit_panier.count(), 1)
        self.assertEqual(panier.produit_panier.first().quantite, 2)

    def test_delete_from_cart(self):
        """Test deleting item from cart (AJAX)"""
        # Dependencies
        from shop.models import Produit, CategorieEtablissement, CategorieProduit, Etablissement
        from customer.models import Panier, ProduitPanier
        
        # Setup Product & Panier
        cat_etab = CategorieEtablissement.objects.create(nom="RestoDel")
        cat_prod = CategorieProduit.objects.create(nom="PlatsDel", categorie=cat_etab)
        etab = Etablissement.objects.create(
            user=User.objects.create_user('delowner', 'pass', first_name='O', last_name='D'),
            nom="RestoDel", categorie=cat_etab, contact_1="01", email="e@e.com", logo="l.png", couverture="c.png",
            nom_du_responsable="Responsable", prenoms_duresponsable="Prenom"
        )
        produit = Produit.objects.create(nom="PDel", prix=1000, categorie=cat_prod, etablissement=etab)
        panier = Panier.objects.create(customer=self.customer)
        produit_panier = ProduitPanier.objects.create(panier=panier, produit=produit, quantite=1)
        
        url = reverse('delete_from_cart')
        data = {
            'panier': panier.id,
            'produit_panier': produit_panier.id
        }
        
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(panier.produit_panier.count(), 0)

    def test_add_coupon(self):
        """Test adding coupon to cart (AJAX)"""
        from customer.models import CodePromotionnel, Panier
        
        coupon = CodePromotionnel.objects.create(
            libelle="Test Coupon",
            code_promo="TEST20",
            reduction=0.20,
            date_fin="2030-01-01",
            etat=True
        )
        panier = Panier.objects.create(customer=self.customer)
        
        url = reverse('add_coupon')
        data = {
            'panier': panier.id,
            'coupon': "TEST20"
        }
        
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        panier.refresh_from_db()
        self.assertEqual(panier.coupon, coupon)

    def test_update_cart(self):
        """Test updating cart quantity (AJAX)"""
        from shop.models import Produit, CategorieEtablissement, CategorieProduit, Etablissement
        from customer.models import Panier, ProduitPanier
        
        cat_etab = CategorieEtablissement.objects.create(nom="RestoUpd")
        cat_prod = CategorieProduit.objects.create(nom="PlatsUpd", categorie=cat_etab)
        etab = Etablissement.objects.create(
            user=User.objects.create_user('updowner', 'pass', first_name='O', last_name='D'),
            nom="RestoUpd", categorie=cat_etab, contact_1="01", email="e@e.com", logo="l.png", couverture="c.png",
            nom_du_responsable="Responsable", prenoms_duresponsable="Prenom"
        )
        produit = Produit.objects.create(nom="PUpd", prix=1000, categorie=cat_prod, etablissement=etab)
        panier = Panier.objects.create(customer=self.customer)
        produit_panier = ProduitPanier.objects.create(panier=panier, produit=produit, quantite=1)
        
        url = reverse('update_cart')
        data = {
            'panier': panier.id,
            'produit': produit.id,
            'quantite': 5
        }
        
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        produit_panier.refresh_from_db()
        self.assertEqual(produit_panier.quantite, 5)

    def test_forgot_password_view(self):
        url = reverse('forgot_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot-password.html')
