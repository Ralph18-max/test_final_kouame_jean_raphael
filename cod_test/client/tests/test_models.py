
import pytest
from customer.models import Panier, ProduitPanier, CodePromotionnel
from shop.models import Produit, CategorieProduit, CategorieEtablissement, Etablissement
from django.contrib.auth.models import User
from django.utils import timezone

@pytest.mark.django_db
class TestPanierModels:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Dependencies for Produit
        self.cat_etab = CategorieEtablissement.objects.create(nom="Resto", description="Desc")
        self.cat_prod = CategorieProduit.objects.create(nom="Plats", description="Desc", categorie=self.cat_etab)
        self.user = User.objects.create_user(username="shopowner", password="password")
        
        self.etab = Etablissement.objects.create(
            user=self.user,
            nom="Chez Tonton",
            description="Best food",
            categorie=self.cat_etab,
            adresse="Cocody",
            pays="CI",
            contact_1="01020304",
            email="shop@test.com",
            ville=None,
            logo="logo.png",
            couverture="cover.png",
            nom_du_responsable="Doe",
            prenoms_duresponsable="John"
        )

    def create_product(self, nom="Test Product", prix=1000):
        return Produit.objects.create(
            nom=nom,
            prix=prix,
            quantite=10,
            status=True,
            description="Desc",
            description_deal="Deal",
            categorie=self.cat_prod,
            etablissement=self.etab
        )

    def test_panier_total_calculation(self):
        product = self.create_product(prix=1000)
        panier = Panier.objects.create()
        ProduitPanier.objects.create(produit=product, panier=panier, quantite=2)
        assert panier.total == 2000

    def test_panier_with_coupon(self):
        product = self.create_product(prix=1000)
        
        # Create coupon (10% reduction)
        coupon = CodePromotionnel.objects.create(
            libelle="PROMO10",
            etat=True,
            date_fin=timezone.now().date(),
            reduction=0.1,
            code_promo="PROMO10"
        )
        
        panier = Panier.objects.create(coupon=coupon)
        
        ProduitPanier.objects.create(
            produit=product,
            panier=panier,
            quantite=1
        )
        
        # Total = 1000. Reduction = 1000 * 0.1 = 100. Final = 900.
        assert panier.total_with_coupon == 900

    def test_check_empty_cart(self):
        panier = Panier.objects.create()
        assert panier.check_empty is False
        
        product = self.create_product()
        ProduitPanier.objects.create(produit=product, panier=panier, quantite=1)
        
        assert panier.check_empty is True
