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
    name_translation = models.CharField(max_length=256, verbose_name=_("name_translation"), blank=True, null=True)
    type = models.CharField(max_length=256, verbose_name=_("type"), blank=True, null=True)
    type_translation = models.CharField(max_length=256, verbose_name=_("type_translation"), blank=True, null=True)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        abstract = True

class ADM0(Base):

    class Meta:
        verbose_name = _("ADM0")
        verbose_name_plural = _("ADM0")
    
    def simplified_geometry(self, tolerance=0.1):
        return self.geometry.simplify(tolerance, preserve_topology=True)
    
    def __str__(self) -> str:
        return str(self.name)
    

# ADM1: Region
class ADM1(Base):

    ADM0 = models.ForeignKey(ADM0, related_name='region', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("ADM0"))

    class Meta:
        verbose_name = _("ADM1")
        verbose_name_plural = _("ADM1")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.ADM0.name} "


# ADM2: Counties
class ADM2(Base):

    ADM1 = models.ForeignKey(ADM1, related_name='counties', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("ADM1"))
    class Meta:
        verbose_name = _("ADM2")
        verbose_name_plural = _("ADM2")
    
    def __str__(self) -> str:
        try:
            return f"{self.name} - {self.ADM1.name}"
        except:
            return 'MISSING FROM GEOGRAPHY'

# ADM3: Municipality
class ADM3(Base):

    ADM2 = models.ForeignKey(ADM2, related_name='municipalities', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("ADM2"))
    class Meta:
        verbose_name = _("ADM3")
        verbose_name_plural = _("ADM3")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.ADM2.name}"
    

# ADM4: Local Administrative Units
class ADM4(Base):

    ADM3 = models.ForeignKey(ADM3, related_name='laus', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("ADM3"))

    class Meta:
        verbose_name = _("ADM4")
        verbose_name_plural = _("ADM4")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.ADM3.name}  "
    

# # ADM5: Communes
# class ADM5(Base):

#     ADM4 = models.ForeignKey(ADM4, related_name='communes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("ADM4"))
#     class Meta:
#         verbose_name = _("ADM5")
#         verbose_name_plural = _("ADM5")
    
#     def __str__(self) -> str:
#         return f"{self.name} - {self.ADM4.name} "
    

class Province(Base):

    country = models.ForeignKey(ADM0, related_name='provinces', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Country"))

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")

    def __str__(self) -> str:
        return f"{self.name} - {self.country.name}"
class Parish(Base):
    
    country = models.ForeignKey(ADM0, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Country"))
    county = models.ForeignKey(ADM1, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("County"))
    municipality = models.ForeignKey(ADM2, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Municipality"))
    province = models.ForeignKey(Province, related_name='parishes', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("Province"))

    class Meta:
        verbose_name = _("Parish")
        verbose_name_plural = _("Parishes")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.province.name} - {self.country.name}"


    