from django.db import models


# Create your models here.
class Part(models.Model):
    image = models.ImageField(upload_to="Part_Images", null=True)
    product_type = models.CharField(null=True)
    brand = models.CharField(null=True)
    part = models.CharField(null=True)
    size = models.IntegerField(null=True)
    model = models.CharField(null=True)
    shelf = models.IntegerField(null=True)
    row = models.IntegerField(null=True)
    column = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.product_type}--{self.brand}--{self.part}"
