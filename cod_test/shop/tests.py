from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement

class ShopTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup dependencies
        self.user = User.objects.create_user(username='shopowner', password='password')
        
        self.cat_etab = CategorieEtablissement.objects.create(
            nom="Resto", 
            description="Description Resto"
        )
        
        self.cat_prod = CategorieProduit.objects.create(
            nom="Plats", 
            description="Description Plats", 
            categorie=self.cat_etab
        )
        
        self.etab = Etablissement.objects.create(
            user=self.user,
            nom="Chez Tonton",
            description="Best food",
            categorie=self.cat_etab,
            adresse="Cocody",
            pays="CI",
            contact_1="01020304",
            email="shop@test.com",
            logo="logo.png",
            couverture="cover.png",
            nom_du_responsable="Doe",
            prenoms_duresponsable="John"
        )
        
        self.produit = Produit.objects.create(
            nom="Attiéké",
            description="Bon",
            description_deal="Promo",
            prix=1500,
            categorie=self.cat_prod,
            etablissement=self.etab
        )

    def test_shop_url_resolves(self):
        url = reverse('shop')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_produit_model(self):
        """Test Product model logic and defaults"""
        self.assertEqual(self.produit.nom, "Attiéké")
        self.assertEqual(self.produit.prix, 1500)
        self.assertEqual(self.produit.prix_promotionnel, 0) # Default value check
        self.assertEqual(str(self.produit.categorie), "Plats")

    def test_shop_view_content(self):
        """Test Shop view integration"""
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Attiéké")
        self.assertTemplateUsed(response, 'shop.html')
        
    def test_product_detail_view(self):
        """Test Product Detail view"""
        # Ensure slug is generated
        self.assertIsNotNone(self.produit.slug)
        response = self.client.get(reverse('product_detail', args=[self.produit.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Attiéké")
        self.assertTemplateUsed(response, 'product-details.html')

    def test_toggle_favorite(self):
        """Test adding/removing favorites"""
        self.client.force_login(self.user)
        url = reverse('toggle_favorite', args=[self.produit.id])
        
        # Add to favorites
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Redirects
        self.assertTrue(self.user.favorites.filter(produit=self.produit).exists())
        
        # Remove from favorites
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user.favorites.filter(produit=self.produit).exists())

    def test_single_category_view(self):
        """Test category view"""
        # Test valid category slug
        self.assertIsNotNone(self.cat_prod.slug)
        url = reverse('categorie', args=[self.cat_prod.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cat_prod.nom)
        
        # Test invalid slug redirects to shop
        url_invalid = reverse('categorie', args=['invalid-slug'])
        response_invalid = self.client.get(url_invalid)
        self.assertEqual(response_invalid.status_code, 302)
        self.assertEqual(response_invalid.url, reverse('shop'))

    def test_cart_view(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_checkout_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')

    def test_paiement_success_view(self):
        self.client.force_login(self.user)
        # Need a customer for this view
        from customer.models import Customer
        if not hasattr(self.user, 'customer'):
            Customer.objects.create(user=self.user, adresse="Ad", contact_1="01")
        
        response = self.client.get(reverse('paiement_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'paiement.html')

    def test_dashboard_view(self):
        self.client.force_login(self.user)
        # User already has etab in setUp
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_article_management_views(self):
        self.client.force_login(self.user)
        
        # Test Article Detail (Management list)
        response = self.client.get(reverse('article-detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'article-detail.html')
        
        # Test Add Article (GET)
        response = self.client.get(reverse('ajout-article'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ajout-article.html')
        
        # Test Add Article (POST)
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpeg")
        data = {
            'nom': 'New Prod',
            'description': 'Desc',
            'prix': '2000',
            'quantite': '10',
            'categorie': self.cat_prod.id,
            'image': image,
            'image_2': image,
            'image_3': image
        }
        response = self.client.post(reverse('ajout-article'), data)
        self.assertEqual(response.status_code, 302) # Redirects to article-detail
        self.assertTrue(Produit.objects.filter(nom='New Prod').exists())

    def test_modifier_article(self):
        self.client.force_login(self.user)
        url = reverse('modifier', args=[self.produit.id])
        
        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modifier-article.html')
        
        # POST
        data = {
            'nom': 'Updated Name',
            'description': 'Updated Desc',
            'prix': '2500',
            'quantite': '5',
            'categorie': self.cat_prod.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.nom, 'Updated Name')

    def test_supprimer_article(self):
        self.client.force_login(self.user)
        url = reverse('supprimer-article', args=[self.produit.id])
        
        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirmer-suppression.html')
        
        # POST
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Produit.objects.filter(id=self.produit.id).exists())

    def test_commande_recu_views(self):
        self.client.force_login(self.user)
        
        # Create a customer and order for this etablissement's product
        from customer.models import Customer, Commande, ProduitPanier
        user_cust = User.objects.create_user('cust', 'pass')
        cust = Customer.objects.create(user=user_cust, adresse="Ad", contact_1="01")
        cmd = Commande.objects.create(customer=cust, transaction_id="T1", prix_total=1000)
        ProduitPanier.objects.create(commande=cmd, produit=self.produit, quantite=1)
        
        # List view
        response = self.client.get(reverse('commande-reçu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'commande-reçu.html')
        self.assertContains(response, self.produit.nom)
        
        # Detail view
        response = self.client.get(reverse('commande-reçu-detail', args=[cmd.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'commande-reçu-detail.html')

    def test_etablissement_parametre(self):
        self.client.force_login(self.user)
        url = reverse('etablissement-parametre')
        
        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'etablissement-parametre.html')
        
        # POST
        data = {
            'nom': 'New Etab Name',
            'nom_responsable': 'New Resp',
            'prenoms_responsable': 'New Pre',
            'contact': '01020304',
            'adresse': 'New Addr',
            'email': 'new@test.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.etab.refresh_from_db()
        self.assertEqual(self.etab.nom, 'New Etab Name')

    def test_post_paiement_details(self):
        # This view expects JSON body
        # And checks for Panier
        from customer.models import Panier, Customer, ProduitPanier
        if not hasattr(self.user, 'customer'):
            cust = Customer.objects.create(user=self.user, adresse="Ad", contact_1="01")
        else:
            cust = self.user.customer
            
        panier = Panier.objects.create(customer=cust)
        ProduitPanier.objects.create(panier=panier, produit=self.produit, quantite=1)
        
        data = {
            'transaction_id': 'TX123',
            'notify_url': 'http://notify',
            'return_url': 'http://return',
            'panier': panier.id
        }
        
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('paiement_detail'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertTrue(json_resp['success'])
