from email.policy import default
from tabnanny import verbose
import maritime.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models


##### Nomenclature of Territorial Units for Statistics #####
# LAU2 -> LAU1 -> NUTS3 -> NUTS2 -> NUTS1
class Region(abstract.AbstractBaseModel):

    geometry = models.MultiPolygonField(verbose_name=_("geometry"), blank=True, null=True)
    name = models.CharField(max_length=256, verbose_name=_("name"), blank=True, null=True)
    code = models.CharField(max_length=24, verbose_name=_("code"), blank=True, null=True, help_text=_('Countries abbreviation'))
    year = models.IntegerField(blank=True, null=True, verbose_name=_("year"), default=0)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        abstract = True

class Country(Region):

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")


class NUTS1(Region):

    superregion = models.ForeignKey(Country, related_name='subregions', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))

    class Meta:
        verbose_name = _("nuts1")
        verbose_name_plural = _("nuts1")

class NUTS2(Region):

    superregion = models.ForeignKey(NUTS1, related_name="subregions", blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("nuts1"))
    
    class Meta:
        verbose_name = _("nuts2")
        verbose_name_plural = _("nuts2")

class NUTS3(Region):

    superregion = models.ForeignKey(NUTS2, related_name="subregions", blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("nuts2"))

    class Meta:
        verbose_name = _("nuts3")
        verbose_name_plural = _("nuts3")



class Province(Region):

    country = models.ForeignKey(Country, related_name='provinces', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))

    class Meta:
        verbose_name = _("Province(AMD1)")
        verbose_name_plural = _("Provinces(AMD1)")


class LocalAdministrativeUnit(Region):

    superregion    = models.ForeignKey(NUTS3, related_name="laus", blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("nuts3")) 

    class Meta:
        verbose_name = _("Local Administrative Unit(AMD3)")
        verbose_name_plural = _("Local Administrative Units(AMD3)")


class Parish(Region):
    
    country = models.ForeignKey(Country, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("country"))
    
    class Meta:
        verbose_name = _("Parish(AMD3)")
        verbose_name_plural = _("Parishes(AMD3)")


    