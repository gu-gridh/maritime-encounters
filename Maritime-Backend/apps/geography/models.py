from email.policy import default
from tabnanny import verbose
import maritime.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models


#####  Administrative geoBoundaries #####
# ADM0 -> ADM1 -> ADM2 -> ADM3 -> ADM4 -> ADM5 -> ADM6 

# ADM0: Country
class Base(abstract.AbstractBaseModel):

    geometry = models.MultiPolygonField(verbose_name=_("geometry"), blank=True, null=True)
    name = models.CharField(max_length=256, verbose_name=_("name"), blank=True, null=True)
    code = models.CharField(max_length=24, verbose_name=_("code"), blank=True, null=True, help_text=_('Countries abbreviation'))
    year = models.IntegerField(blank=True, null=True, verbose_name=_("year"), default=0)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        abstract = True

class Country(Base):

    class Meta:
        verbose_name = _("Country (ADM0)")
        verbose_name_plural = _("Countries (ADM0)")
    
    def __str__(self) -> str:
        return str(self.name)
    

# ADM1: Region
class Region(Base):

    country = models.ForeignKey(Country, related_name='region', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))

    class Meta:
        verbose_name = _("Region (ADM1)")
        verbose_name_plural = _("Regions (ADM1)")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.country.name}"


# ADM2: Counties
class Counties(Base):

    country = models.ForeignKey(Country, related_name='counties', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))
    region = models.ForeignKey(Region, related_name='counties', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("region"))
    class Meta:
        verbose_name = _("Counties (ADM2)")
        verbose_name_plural = _("Counties (ADM2)")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.region.name} - {self.country.name}"

# ADM3: Municipality
class Municipality(Base):

    country = models.ForeignKey(Country, related_name='municipalities', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))
    region = models.ForeignKey(Region, related_name='municipalities', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("region"))
    counties = models.ForeignKey(Counties, related_name='municipalities', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("county"))
    class Meta:
        verbose_name = _("Municipality (ADM3)")
        verbose_name_plural = _("Municipalities (ADM3)")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.counties.name} - {self.region.name} - {self.country.name}"
    

# ADM4: Local Administrative Units
class LAU(Base):

    country = models.ForeignKey(Country, related_name='laus', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))
    region = models.ForeignKey(Region, related_name='laus', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("region"))
    counties = models.ForeignKey(Counties, related_name='laus', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("county"))
    municipality = models.ForeignKey(Municipality, related_name='laus', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("municipality"))

    class Meta:
        verbose_name = _("Local Administrative Units (ADM4)")
        verbose_name_plural = _("Local Administrative Units (ADM4)")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.municipality.name} - {self.counties.name} - {self.region.name} - {self.country.name}"
    

# ADM5: Communes
class Commune(Base):

    country = models.ForeignKey(Country, related_name='communes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))
    region = models.ForeignKey(Region, related_name='communes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("region"))
    counties = models.ForeignKey(Counties, related_name='communes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("county"))
    municipality = models.ForeignKey(Municipality, related_name='communes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("municipality"))
    lau = models.ForeignKey(LAU, related_name='communes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("lau"))
    class Meta:
        verbose_name = _("Commune (ADM5)")
        verbose_name_plural = _("Communes (ADM5)")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.lau.name} - {self.municipality.name} - {self.counties.name} - {self.region.name} - {self.country.name}"
    

class Province(Base):

    country = models.ForeignKey(Country, related_name='provinces', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")

class Parish(Base):
    
    country = models.ForeignKey(Country, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))
    province = models.ForeignKey(Province, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("province"))
    class Meta:
        verbose_name = _("Parish")
        verbose_name_plural = _("Parishes")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.province.name} - {self.country.name}"


    