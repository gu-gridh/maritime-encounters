import maritime.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models
import apps.geography.models as geography
from django.contrib.postgres.fields import ArrayField


class Location(abstract.AbstractBaseModel):
    # Represents the location of the site
    site = models.ForeignKey('Site', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the location is located."))
    location_name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "location_name"), help_text=_("The name of the location."))
    location_detail = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "location_detail"), help_text=_("The description of the location."))
    location_detail_eng = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "location_detail_eng"), help_text=_("The english translation of location detail."))
    coordinates = models.PointField(null=True, blank=True, verbose_name=_(
        "Coordinates"), help_text=_("Mid-point coordinates of the location."))

    def __str__(self) -> str:
        return self.location_name or self.location_detail or self.site.name or ''

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class SiteType(abstract.AbstractTagModel):
    # Represents the type of the site

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Site Type")
        verbose_name_plural = _("Site Types")


class Sampler(abstract.AbstractBaseModel):
    # Represents the sampler of the sample
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "name"), help_text=_("The name of the sampler."))
    affiliation = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "affiliation"), help_text=_("The affiliation of the sampler."))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Sampler")
        verbose_name_plural = _("Samplers")


class Context(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Context")
        verbose_name_plural = _("Contexts")


class ObjectCategories(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Object Category")
        verbose_name_plural = _("Object Categories")


class ObjectSubcategories(models.Model):
    # category = models.ForeignKey(ObjectCategories, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
    #     "category"), help_text=_("The category of the object, e.g. Weapon, Vessel."))
    subcategory = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "subcategory"), help_text=_("The subcategory of the object, e.g. Sword, Ring."))

    if subcategory:
        def __str__(self) -> str:
            return self.subcategory
    else:
        def __str__(self) -> str:
            return ''

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Object Subcategory")
        verbose_name_plural = _("Object Subcategories")


class ObjectMaterials(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Object Material")
        verbose_name_plural = _("Object Materials")


class ObjectDescription(abstract.AbstractBaseModel):
    category = models.ManyToManyField(ObjectCategories, blank=True, verbose_name=_(
        "category"), help_text=_("The category of the object, e.g. Weapon, Vessel."))
    subcategory = models.ForeignKey(ObjectSubcategories, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "subcategory"), help_text=_("The subcategory of the object."))

    # material = models.ManyToManyField(ObjectMaterials, verbose_name=_(
    #     "material"), help_text=_("The material(s) of the object."))

    def __str__(self) -> str:
        def category_list(self):
            categories = ','.join([category.text for category in self.category.all()])
        name_str = f"{self.subcategory}" or 'No Info'
        return name_str

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Object Description")
        verbose_name_plural = _("Object Descriptions")


class EntryNum(abstract.AbstractBaseModel):
    entry_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "entry_num"), help_text=_("The entry number of the object."))

    def __str__(self) -> str:
        name_str = f"{self.entry_number}"
        return name_str

    class Meta:
        verbose_name = _("Entry Number")
        verbose_name_plural = _("Entry Numbers")


class SampleType(abstract.AbstractTagModel):
    # Represents the type of the sample

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Sample Type")
        verbose_name_plural = _("Sample Types")


class Fastening(abstract.AbstractTagModel):
    # Represents the fastening of the sample

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Fastening")
        verbose_name_plural = _("Fastenings")


class Phase(abstract.AbstractTagModel):
    # Represents the phase of the site

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Phase")
        verbose_name_plural = _("Phases")


class Period(abstract.AbstractBaseModel):
    # Represents the period of the site
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "name"), help_text=_("The name of the period."))
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='period_phase', verbose_name=_("phase"), help_text=_("The phase of the period."))
    start_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "start_date"), help_text=_("The start date of the period."))
    end_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "end_date"), help_text=_("The end date of the period."))

    def __str__(self) -> str:
        if self.phase:
            return f"{self.name} - {self.phase}"
        else:
            return self.name

    def __repr__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")


class PeriodActivity(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Period Activity")
        verbose_name_plural = _("Period Activities")


class Species(abstract.AbstractTagModel):
    # Represents the species of the sample

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Species")
        verbose_name_plural = _("Species")


class Shape(abstract.AbstractTagModel):
    # Represents the shape of the sample
    type = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "type"), help_text=_("The type of the Shape."))

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Shape")
        verbose_name_plural = _("Shapes")


class Feature(abstract.AbstractTagModel):
    # Represents the feature of the sample

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Feature")
        verbose_name_plural = _("Features")


class Cleat(abstract.AbstractBaseModel):

    cleat_number = models.IntegerField(null=True, blank=True, verbose_name=_(
        "cleatnumber"), help_text=_("The number of cleats of the boat."))
    cleat_length = models.FloatField(null=True, blank=True, verbose_name=_(
        "boatcapacity"), help_text=_("The capacity of the boat."))
    cleat_width = models.FloatField(null=True, blank=True, verbose_name=_(
        "boatweight"), help_text=_("The weight of the boat."))
    cleat_heigth = models.IntegerField(null=True, blank=True, verbose_name=_(
        "boatcrew"), help_text=_("The crew of the boat."))

    def __str__(self) -> str:
        return self.cleat_number

    class Meta:
        verbose_name = _("Cleat")
        verbose_name_plural = _("Cleats")


class Element(abstract.AbstractBaseModel):
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "element_name"), help_text=_("The element name of the sample."))
    symbol = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "element_symbol"), help_text=_("The element symbol of the sample."))
    atomic_number = models.IntegerField(null=True, blank=True, verbose_name=_(
        "element_number"), help_text=_("The atomic number of the sample."))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Element")
        verbose_name_plural = _("Elements")


class ElementRatio(abstract.AbstractBaseModel):
    elemant_name = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_(
        "element_name"), help_text=_("The element name of the sample."))
    element_ratio = models.FloatField(null=True, blank=True, verbose_name=_(
        "element_ratio"), help_text=_("The element ratio of the sample."))

    def __str__(self) -> str:
        return self.elemant_name

    class Meta:
        verbose_name = _("Element Ratio")
        verbose_name_plural = _("Elements Ratio")


class Material(abstract.AbstractTagModel):
    # Represents the material of the sample
    type = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "type"), help_text=_("The type of the sample."))

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")


class LeadIsotope(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    class Meta:
        verbose_name = _("Lead Isotope")
        verbose_name_plural = _("Lead Isotope")


class Carbon_Nitrogen_Ratio(abstract.AbstractBaseModel):
    carbon_to_nitrogen_ratio = models.FloatField(null=True, blank=True, verbose_name=_(
        "carbon_to_nitrogen_ratio"), help_text=_("The carbon to nitrogen ratio of the sample."))

    def __str__(self) -> str:
        return self.carbon_to_nitrogen_ratio

    class Meta:
        verbose_name = _("Carbon/Nitrogen Ratio")
        verbose_name_plural = _("Carbon/Nitrogen Ratios")


class CulturalGroup(abstract.AbstractTagModel):
    # Represents the cultural group of the sample

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Cultural Group")
        verbose_name_plural = _("Cultural Groups")


class DatingMethod(abstract.AbstractTagModel):
    # Represents the dating method of the sample

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Dating Method")
        verbose_name_plural = _("Dating Methods")


class Site(abstract.AbstractBaseModel):
    # Represents the archaeological sites of interests

    # Site name is a field that includes the name of the site and it can be used to search for the site
    # This feld can leave empty if the site name is not known
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "sitename"), help_text=_("Free-form, non-indexed site name of the site."))
    # Location
    coordinates = models.PointField(null=True, blank=True, verbose_name=_(
        "Coordinates"), help_text=_("Mid-point coordinates of the site."))
    ADM0 = models.ForeignKey(geography.ADM0, null=True, blank=True,
                             related_name='sites', on_delete=models.SET_NULL)
    ADM1 = models.ForeignKey(geography.ADM1, null=True, blank=True,  related_name="sites",
                             on_delete=models.SET_NULL, verbose_name=_("AMD1"), help_text=_("ADM1"))
    ADM2 = models.ForeignKey(geography.ADM2, null=True, blank=True,  related_name="sites",
                             on_delete=models.SET_NULL, verbose_name=_("AMD2"), help_text=_("ADM2"))
    ADM3 = models.ForeignKey(geography.ADM3, null=True, blank=True,  related_name="sites",
                             on_delete=models.SET_NULL, verbose_name=_("AMD3"), help_text=_("ADM3"))
    ADM4 = models.ForeignKey(geography.ADM4, null=True, blank=True,  related_name="sites",
                             on_delete=models.SET_NULL, verbose_name=_("AMD4"), help_text=_("ADM4"))
    Province = models.ForeignKey(geography.Province, null=True, blank=True,  related_name="sites",
                                 on_delete=models.SET_NULL, verbose_name=_("Landskap (Province)"), help_text=_("Swedish landskap/province"))
    Parish = models.ForeignKey(geography.Parish, null=True, blank=True,  related_name="sites",
                               on_delete=models.SET_NULL, verbose_name=_("Socken (Parish)"), help_text=_("Swedish socken/parish"))
    # Placename is particularly used outside of Sweden
    placename = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Placename"), help_text=_("Free-form, non-indexed placename of the site."))

    def __str__(self) -> str:

        if self.name:
            name_str = f"{self.name}"
        elif self.placename:
            name_str = f"{self.placename}"
        else:
            name_str = ''
        return name_str

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")


class PlankBoats(abstract.AbstractBaseModel):
    # Represents the archaeological  boats information

    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "boatname"), help_text=_("Free-form, non-indexed boat name of the boat."))
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the boat is located."))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "location"), help_text=_("The location of the boat."))

    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "period"), help_text=_("The period of the boat."))

    est_length = models.FloatField(null=True, blank=True, verbose_name=_(
        "boatlength"), help_text=_("The length of the boat."))
    est_width = models.FloatField(null=True, blank=True, verbose_name=_(
        "boatwidth"), help_text=_("The width of the boat."))
    est_height = models.FloatField(null=True, blank=True, verbose_name=_(
        "boatheight"), help_text=_("The height of the boat."))

    hull = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='hull_material',
                             null=True, blank=True, verbose_name=_("material"), help_text=_("The material of the boat."))
    thwarts = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='thwarts_material', null=True,
                                blank=True, verbose_name=_("thwarts_material"), help_text=_("The thwarts material of the boat."))
    fastening = models.ForeignKey(Fastening, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "fastening"), help_text=_("The fastening of the boat."))
    bottom_side_strakes = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='bottom_side_strakes_shape',
                                            null=True, blank=True, verbose_name=_("bottom_side_strakes"), help_text=_("The bottom side strakes of the boat."))
    outer_bottom_plank = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='outer_bottom_plank_shape',
                                           null=True, blank=True, verbose_name=_("outer_bottom_plank"), help_text=_("The outer bottom plank of the boat."))
    shape_holes = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='holes_shape',
                                    null=True, blank=True, verbose_name=_("shape"), help_text=_("The shape of the boat."))
    diam_holes = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='diam_holes_shape',
                                   null=True, blank=True, verbose_name=_("diam"), help_text=_("The diam of the boat."))
    cauking = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "cauking"), help_text=_("The cauking of the boat."))

    cleat = models.ForeignKey(Cleat, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "cleat"), help_text=_("The cleat of the boat."))

    caprail = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "caprail"), help_text=_("The caprail of the boat."))
    tree_nails = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "treenails"), help_text=_("The treenails of the boat."))
    keel_bending = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "keelbending"), help_text=_("The keel bending of the boat."))
    outer_bending = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "outerbending"), help_text=_("The outer bending of the boat."))
    low_bending = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "lowbending"), help_text=_("The low bending of the boat."))
    longitudinal_bending = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "longitudinalbending"), help_text=_("The longitudinal bending of the boat."))
    longest_length = models.FloatField(null=True, blank=True, verbose_name=_(
        "longestlength"), help_text=_("The longest  length of the boat."))
    size_trees = models.FloatField(null=True, blank=True, verbose_name=_(
        "sizetrees"), help_text=_("The size trees of the boat."))
    tootlmarks = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "tootlmarks"), help_text=_("The tootl marks of the boat."))
    individual_lashings = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "individuallashings"), help_text=_("The individual lashings of the boat."))
    continuous_stiching = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "continuouslashings"), help_text=_("The continuous lashings of the boat."))

    comments = models.TextField(null=True, blank=True, verbose_name=_(
        "comments"), help_text=_("The comments of the boat."))
    notes = models.TextField(null=True, blank=True, verbose_name=_(
        "notes"), help_text=_("The notes of the boat."))
    references = models.TextField(null=True, blank=True, verbose_name=_(
        "references"), help_text=_("The references of the boat."))

    def __str__(self) -> str:

        name_str = f"{self.name}"
        return name_str

    class Meta:
        verbose_name = _("Plank Boat")
        verbose_name_plural = _("Plank Boats")


class LogBoats(abstract.AbstractBaseModel):
    # Represents the archaeological log boats information

    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "logboatname"), help_text=_("Free-form, non-indexed logboat name of the logboat."))
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the logboat is located."))
    context = models.ForeignKey(SiteType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "context"), help_text=_("The context of the logboat."))

    wood_species = models.ForeignKey(Species, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "woodspecies"), help_text=_("The wood species of the logboat."))

    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='loag_boat_period',
                               null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the logboat."))
    dendro_lab_code = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "dendrolabcode"), help_text=_("The dendro lab code of the logboat."))
    dendro_date = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='dendro_period', null=True,
                                    blank=True, verbose_name=_("dendrobcdate"), help_text=_("The dendro bc date of the logboat."))

    preservation = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "preservation"), help_text=_("The preservation of the logboat."))

    length = models.FloatField(null=True, blank=True, verbose_name=_(
        "logboatlength"), help_text=_("The length of the logboat."))
    width = models.FloatField(null=True, blank=True, verbose_name=_(
        "logboatwidth"), help_text=_("The width of the logboat."))
    depth = models.FloatField(null=True, blank=True, verbose_name=_(
        "logboatdepth"), help_text=_("The depth of the logboat."))

    est_length = models.FloatField(null=True, blank=True, verbose_name=_(
        "logboatlength"), help_text=_("The length of the logboat."))
    est_width = models.FloatField(null=True, blank=True, verbose_name=_(
        "logboatwidth"), help_text=_("The width of the logboat."))
    est_height = models.FloatField(null=True, blank=True, verbose_name=_(
        "logboatheight"), help_text=_("The height of the logboat."))

    bow = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='bow_shape', null=True,
                            blank=True, verbose_name=_("bowshape"), help_text=_("The bow shape of the logboat."))
    stern = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='stern_shape', null=True,
                              blank=True, verbose_name=_("sternshape"), help_text=_("The stern shape of the logboat."))
    hull = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='hull_shape', null=True,
                             blank=True, verbose_name=_("hullshape"), help_text=_("The hull shape of the logboat."))
    basal = models.ForeignKey(Shape, on_delete=models.CASCADE, related_name='basel_shape',
                              null=True, blank=True, verbose_name=_("basal"), help_text=_("The basal of the logboat."))

    transerve_ridges = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "transerveridges"), help_text=_("The transerve ridges of the logboat."))
    other_features = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "otherfeatures"), help_text=_("The other features of the logboat."))
    repair = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "repair"), help_text=_("The repair of the logboat."))
    toolmarks = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "toolmarks"), help_text=_("The tool marks of the logboat."))
    burnt_mark = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "burntmark"), help_text=_("The burnt mark of the logboat."))
    other_material = models.ManyToManyField(Material, blank=True, verbose_name=_(
        "othermaterial"), help_text=_("The other material of the logboat."))

    notes = models.TextField(null=True, blank=True, verbose_name=_(
        "notes"), help_text=_("The notes of the logboat."))
    refernce = models.TextField(null=True, blank=True, verbose_name=_(
        "refernce"), help_text=_("The refernce of the logboat."))

    def __str__(self) -> str:

        name_str = f" {self.name}"
        return name_str

    class Meta:
        verbose_name = _("Log Boat")
        verbose_name_plural = _("Log Boats")


class LandingPoints(abstract.AbstractBaseModel):

    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Site"), help_text=_("The site (general location) in which the landing site is located."))
    period = models.ManyToManyField(Period, blank=True, verbose_name=_(
        "Period(s) of Activity"), help_text=_("The period(s) of activity at the landing site."))

    related_finds = models.ManyToManyField(Material, blank=True, verbose_name=_(
        "Related Sites/Material"), help_text=_("The related sites/finds and supporting material."))
    reason = models.TextField(null=True, blank=True, verbose_name=_(
        "Rationale"), help_text=_("The rationale for selecting the site as a landing site."))
    geographic = models.TextField(null=True, blank=True, verbose_name=_(
        "Geographic Significance"), help_text=_("The geographic of the landing."))
    start_date = models.IntegerField(null=True, blank=True, verbose_name=_("Start Date"), help_text=_("The start date of activity at the site as an integer.  Use a negative integer for BC dates."))
    end_date = models.IntegerField(null=True, blank=True, verbose_name=_("End Date"), help_text=_("The end date of activity at the site as an integer.  Use a negative integer for BC dates."))

    def __str__(self) -> str:
        
        def periods_list(self):
            periods = ','.join([period.name for period in self.period.all()])

        name_str = f" {self.site.name}"
        return name_str

    class Meta:
        verbose_name = _("Landing Point")
        verbose_name_plural = _("Landing Points")


class RelPresentActivityLandingPoints(models.Model):
    landing_point = models.ForeignKey(
        LandingPoints, on_delete=models.CASCADE, null=True, blank=True)
    period_activity = models.ForeignKey(
        PeriodActivity, on_delete=models.CASCADE, null=True, blank=True)
    present_activity = models.BooleanField(null=True, blank=True)


class NewSamples(abstract.AbstractBaseModel):

    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the sample is located."))
    aDNA = models.ForeignKey("aDNA", on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "aDNA"), help_text=_("The aDNA of the sample."))
    Carbon_to_nitrogen_ratio = models.ForeignKey(
        Carbon_Nitrogen_Ratio, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("C/N"), help_text=_("The presence of C/N."))
    metal = models.ForeignKey(Element, on_delete=models.CASCADE, null=True,
                              blank=True, verbose_name=_("metal"), help_text=_("The metal element"))
    drilled_location = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "drilled_location"), help_text=_("The drilled location of the sample."))
    weight = models.CharField(max_length=128, null=True, blank=True, verbose_name=_(
        "weight"), help_text=_("The weight of the metal."))
    pictures = models.CharField(max_length=512, null=True, blank=True, verbose_name=_(
        "Pictures"), help_text=_("The pictures of the metal."))
    sampler = models.ForeignKey(Sampler, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "sampler"), help_text=_("The sampler of the metal."))
    date = models.DateField(null=True, blank=True, verbose_name=_(
        "date"), help_text=_("The date of the metal."))
    note = models.TextField(null=True, blank=True, verbose_name=_(
        "note"), help_text=_("The note of the metal."))

    def __str__(self) -> str:
        if self.metal and self.sampler:
            name_str = f" {self.metal.name} - {self.sampler.name}"
        if self.metal:
            name_str = f" {self.metal.name}"
        if self.sampler:
            name_str = f" {self.sampler.name}"
        return name_str

    class Meta:
        verbose_name = _("New Sample")
        verbose_name_plural = _("New Samples")


class Radiocarbon(abstract.AbstractBaseModel):

    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the date is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "sample"), help_text=_("The sample of the Radiocarbon."))
    context = models.ManyToManyField(Context, blank=True, verbose_name=_(
        "contexts"), help_text=_("The context of site type."))
    lab_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "lab_id"), help_text=_("The lab id of the sample."))

    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "period"), help_text=_("The period of the Radiocarbon."))

    start_date = models.CharField(max_length=256, null=True, blank=True, help_text=_("The start date of the Radiocarbon."))
    end_date = models.CharField(max_length=256, null=True, blank=True, help_text=_("The end date of the Radiocarbon."))

    c14_age = models.IntegerField(null=True, blank=True, verbose_name=_(
        "c14_age"), help_text=_("The radiocarbion age"))
    c14_std = models.IntegerField(null=True, blank=True, verbose_name=_(
        "c14_std"), help_text=_("The radiocarbion deviation"))
    density = models.FloatField(null=True, blank=True, verbose_name=_(
        "density"), help_text=_("The quality measure of the measurement)."))

    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "material"), help_text=_("The material of the Radiocarbon."))
    species = models.ForeignKey(Species, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "species"), help_text=_("The species of the Radiocarbon."))

    d13c = models.FloatField(null=True, blank=True, verbose_name=_(
        "d13c"), help_text=_("The delta 13c of the sample."))
    d15n = models.FloatField(null=True, blank=True, verbose_name=_(
        "d15n"), help_text=_("The d15n of the sample."))

    feature = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "feature"), help_text=_("The feature of the Radiocarbon."))

    percentage_of_Carbon = models.FloatField(null=True, blank=True, verbose_name=_(
        "percentage_of_Carbon"), help_text=_("The percentage of Carbon of the sample."))
    Carbon_ratio_to_Nitrogen = models.FloatField(null=True, blank=True, verbose_name=_(
        "percentage_of_Nitrogen"), help_text=_("The percentage of the Carbon to Nitrogen."))
    percentage_of_Yield = models.FloatField(null=True, blank=True, verbose_name=_(
        "percentage_of_Yield"), help_text=_("The percentage of the Yield of the sample."))
    Carbon_to_nitrogen_ratio = models.ForeignKey(
        Carbon_Nitrogen_Ratio, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("C/N"), help_text=_("The presence of C/N."))
    marine_reservoir = models.FloatField(null=True, blank=True, verbose_name=_(
        "marine_reservoir"), help_text=_("The marine reservoir of the Radiocarbon."))

    notes = models.TextField(null=True, blank=True, verbose_name=_(
        "notes"), help_text=_("The notes of the Radiocarbon."))
    reference = models.TextField(null=True, blank=True, verbose_name=_(
        "reference"), help_text=_("The reference of the Radiocarbon."))
    source_database = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "source_database"), help_text=_("The source database of the Radiocarbon."))

    def __str__(self) -> str:

        name_str = f"{self.site.name} - {self.lab_id}"
        return name_str

    class Meta:
        verbose_name = _("Radiocarbon")
        verbose_name_plural = _("Radiocarbons")


class MetalAnalysis(abstract.AbstractBaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the metal is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "sample"), help_text=_("The sample of the metal."))

    museum_entry = models.ForeignKey("AccessionNum", on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "museum entries"), help_text=_("The AMA of the metal."))
    context = models.ForeignKey(Context, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "context"), help_text=_("The context of the metal."))
    object_description = models.ForeignKey(ObjectDescription, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "object_description"), help_text=_("The object description of the metal."))
    general_typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "general_typology"), help_text=_("The general typology of the metal."))
    typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "typology"), help_text=_("The typology of the metal."))
    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "period"), help_text=_("The period of the metal."))

    def __str__(self) -> str:
        name_str = f"{self.museum_entry}-{self.context}"
        return name_str

    class Meta:
        verbose_name = _("Metal Analysis")
        verbose_name_plural = _("Metal Analyses")


class MetalElement(models.Model):
    metal = models.ForeignKey(
        MetalAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    elemnt = models.ForeignKey(
        Element, on_delete=models.CASCADE, null=True, blank=True)
    element_ratio = models.FloatField(null=True, blank=True, verbose_name=_(
        "element_ratio"), help_text=_("The element ratio of the sample."))


class MetalIsotop(models.Model):
    metal = models.ForeignKey(
        MetalAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    lead_isotope = models.ForeignKey(
        LeadIsotope, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Lead_isotope"))
    lead_isotope_ratio = models.FloatField(
        null=True, blank=True, help_text=_("The isotope ratio of the metal."))


class aDNA(abstract.AbstractBaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the aDNA is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True,
                               blank=True, verbose_name=_("sample"), help_text=_("The sample of the aDNA."))
    genetic_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "genetic_id"), help_text=_("The genetic id of the aDNA."))
    master_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "master_id"), help_text=_("The master id of the aDNA."))
    skeletal_code = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "skeletal_code"), help_text=_("The skeletal code of the aDNA."))
    skeletal_element = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "skeletal_element"), help_text=_("The skeletal element of the aDNA."))

    year_date = models.IntegerField(null=True, blank=True, verbose_name=_(
        "year_date"), help_text=_("The year date of the aDNA."))
    dating_method = models.ForeignKey(DatingMethod, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "dating_method"), help_text=_("The dating method of the aDNA."))
    age_at_seath = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "age_at_death"), help_text=_("The age at death of the aDNA."))
    period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "period"), help_text=_("The period of the aDNA."))
    cultural_group = models.ForeignKey(CulturalGroup, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "cultural_group"), help_text=_("The cultural group of the aDNA."))

    comments = models.TextField(null=True, blank=True, verbose_name=_(
        "comments"), help_text=_("The comments of the aDNA."))
    reference = models.TextField(null=True, blank=True, verbose_name=_(
        "reference"), help_text=_("The reference of the aDNA."))

    def __str__(self) -> str:
        name_str = f"{self.genetic_id}"
        return name_str

    class Meta:
        verbose_name = _("aDNA")
        verbose_name_plural = _("aDNAs")


class IsotopesBio(abstract.AbstractBaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the Isotopes Bio is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "sample"), help_text=_("The sample of the Isotopes Bio."))
    individual_id = models.IntegerField(null=True, blank=True, verbose_name=_(
        "individual_id"), help_text=_("The individual id of the Isotopes Bio."))
    smple_type = models.ForeignKey(SampleType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "smple_type"), help_text=_("The smple type of the Isotopes Bio."))

    species = models.ForeignKey(Species, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "species"), help_text=_("The species of the Isotopes Bio."))
    age = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "age"), help_text=_("The age of the Isotopes Bio."))
    sex = models.CharField(max_length=256, null=True, blank=True)
    d13c = models.FloatField(null=True, blank=True, verbose_name=_(
        "d13c"), help_text=_("The d13c of the Isotopes Bio."))
    percentage_of_Carbon = models.FloatField(null=True, blank=True, verbose_name=_(
        "percentage_of_Carbon"), help_text=_("The percentage of Carbon of the Isotopes Bio."))
    d13C_scale = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "d13C_scale"), help_text=_("The d13C scale of the Isotopes Bio."))
    d15N = models.FloatField(null=True, blank=True, verbose_name=_(
        "d15N"), help_text=_("The d15N of the Isotopes Bio."))
    percentage_of_Nitrogen = models.FloatField(null=True, blank=True, verbose_name=_(
        "percentage_of_Nitrogen"), help_text=_("The percentage of Nitrogen of the Isotopes Bio."))
    d15N_scale = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "d15N_scale"), help_text=_("The d15N scale of the Isotopes Bio."))
    Carbon_to_nitrogen_ratio = models.ForeignKey(
        Carbon_Nitrogen_Ratio, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("C/N"), help_text=_("The presence of C/N."))

    d34S = models.FloatField(null=True, blank=True, verbose_name=_(
        "d34S"), help_text=_("The d34S of the Isotopes Bio."))
    Sr87_86Sr = models.FloatField(null=True, blank=True, verbose_name=_(
        "Sr87_86Sr"), help_text=_("The Sr87_86Sr of the Isotopes Bio."))
    d180 = models.FloatField(null=True, blank=True, verbose_name=_(
        "d180"), help_text=_("The d180 of the Isotopes Bio."))
    d180_scale = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "d180_scale"), help_text=_("The d180 scale of the Isotopes Bio."))
    d180_prep_method = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "d180_prep_method"), help_text=_("The d180 prep method of the Isotopes Bio."))
    notes = models.TextField(null=True, blank=True, verbose_name=_(
        "notes"), help_text=_("The notes of the Isotopes Bio."))
    sample_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "sample_number"), help_text=_("The sample number of the Isotopes Bio."))

    reference = models.TextField(null=True, blank=True, verbose_name=_(
        "reference"), help_text=_("The reference of the Isotopes Bio."))

    def __str__(self) -> str:
        name_str = f"{self.individual_id}"
        return name_str

    class Meta:
        verbose_name = _("Isotopes Bio")
        verbose_name_plural = _("Isotopes Bios")


class LNHouses(abstract.AbstractBaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "site"), help_text=_("The site in which the House is located."))
    number_houses = models.IntegerField(null=True, blank=True, verbose_name=_(
        "number_houses"), help_text=_("The number of houses of the House."))
    number_BA_houses = models.IntegerField(null=True, blank=True, verbose_name=_(
        "number_BA_houses"), help_text=_("The number of BA houses of the House."))
    features = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "features"), help_text=_("The features of the House."))
    dating_method = models.ForeignKey(DatingMethod, on_delete=models.CASCADE, related_name='dating_method_type',
                                      null=True, blank=True, verbose_name=_("dating_method"), help_text=_("The dating method of the House."))
    feature_house_K1 = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "feature_house_K1"), help_text=_("The feature house K1 of the House."))
    context_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "context_date"), help_text=_("The context date of the House."))
    aisle = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "aisle"), help_text=_("The aisle of the House."))
    aisle_type = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "aisle_type"), help_text=_("The aisle type of the House."))
    min_length = models.FloatField(null=True, blank=True, verbose_name=_(
        "min_length"), help_text=_("The min length of the House."))
    max_length = models.FloatField(null=True, blank=True, verbose_name=_(
        "max_length"), help_text=_("The max length of the House."))
    min_width = models.FloatField(null=True, blank=True, verbose_name=_(
        "min_width"), help_text=_("The min width of the House."))
    max_width = models.FloatField(null=True, blank=True, verbose_name=_(
        "max_width"), help_text=_("The max width of the House."))
    orientation = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "orientation"), help_text=_("The orientation of the House."))
    earliest_period_typology = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='earliest_period_typology_time', null=True, blank=True, verbose_name=_(
        "earliest_period_typology"), help_text=_("The earliest period typology of the House."))
    latest_period_typology = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='latest_period_typology_time', null=True, blank=True, verbose_name=_(
        "latest_period_typology"), help_text=_("The latest period typology of the House."))
    prefered_dating_method = models.ForeignKey(DatingMethod, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "prefered_dating_method"), help_text=_("The prefered dating method of the House."))
    dating_typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "dating_typology"), help_text=_("The dating typology of the House."))
    dating_14C = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "dating_14C"), help_text=_("The dating 14C of the House."))
    final_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "final_date"), help_text=_("The final date of the House."))
    reason_exclusion = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "reason_exclusion"), help_text=_("The reason exclusion of the House."))

    references = models.TextField(null=True, blank=True, verbose_name=_(
        "references"), help_text=_("The references of the House."))
    url = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "url"), help_text=_("The url of the House."))

    def __str__(self) -> str:
        name_str = f" {self.number_houses}-{self.site.name}"
        return name_str

    class Meta:
        verbose_name = _("Late Neolithic House")
        verbose_name_plural = _("Late Neolithic Houses")


class Form(abstract.AbstractBaseModel):
    name = models.CharField(max_length=254, null=True, blank=True, verbose_name=_(
        "Name"), help_text=_("The form of an object, e.g. shafthole axe, miniature, etc."))

    def __str__(self) -> str:
        return self.name or 'Not specified'

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")


class Variant(abstract.AbstractBaseModel):
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Name"), help_text=_("The variant of an object form, e.g. simple (enkel), Type A, etc."))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Variant")
        verbose_name_plural = _("Variants")


class ObjectIds(abstract.AbstractBaseModel):
    art_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Art ID"), help_text=_("Norweigian ID of the object."))
    systemnr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Systemnr"), help_text=_("Danish ID systemnr."))
    stednr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Stednr"), help_text=_("Danish ID stednr."))
    loknr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Loknr"), help_text=_("Danish ID loknr."))
    frednr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Frednr"), help_text=_("Danish ID frednr."))
    other_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Other ID"), help_text=_("Any other ID of the object."))

    def __str__(self) -> str:
        if self.art_id:
            return self.art_id
        elif self.systemnr and self.stednr and self.loknr and self.frednr:
            return f"{self.systemnr} {self.stednr} {self.loknr} {self.frednr}"
        else:
            return self.other_id

    class Meta:
        verbose_name = _("Object ID")
        verbose_name_plural = _("Object IDs")


class MuseumMeta(abstract.AbstractBaseModel):
    museum = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Museum"), help_text=_("The museum that holds or recorded the object."))
    museum_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Museum Number/ID"), help_text=_("The number (or short identifier) of the museum that holds or recorded the object."))

    def __str__(self) -> str:
        if self.museum:
            name_str = self.museum
        else:
            name_str = self.museum_number
        return name_str

    class Meta:
        verbose_name = _("Museum")
        verbose_name_plural = _("Museums")


class MuseumCollection(abstract.AbstractBaseModel):
    museum = models.ForeignKey(MuseumMeta, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Museum"), help_text=_("The museum that holds or recorded the object."))
    collection = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Collection"), help_text=_("The title of the museum or personal collection."))

    def __str__(self) -> str:
        name_str = f"{self.collection}"
        return name_str

    class Meta:
        verbose_name = _("Museum Collection")
        verbose_name_plural = _("Museum Collections")


class LiteratureNum(abstract.AbstractBaseModel):
    literature_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "literature_num"), help_text=_("The literature number of the object."))

    def __str__(self) -> str:
        name_str = f"{self.literature_number}"
        return name_str

    class Meta:
        verbose_name = _("Literature Number")
        verbose_name_plural = _("Literatures Numbers")


class AccessionNum(abstract.AbstractBaseModel):
    accession_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "accession_num"), help_text=_("The accession number of the object."))

    def __str__(self) -> str:
        name_str = f"{self.accession_number}"
        return name_str

    class Meta:
        verbose_name = _("Accession Number")
        verbose_name_plural = _("Accession Numbers")


class FindContext(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Find Context")
        verbose_name_plural = _("Find Contexts")


class ContextDetail(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Context - Detailed")
        verbose_name_plural = _("Contexts - Detailed")


class ContextKeywords(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Context Keyword")
        verbose_name_plural = _("Context Keywords")


class ContextFindsCategories(abstract.AbstractTagModel):

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Context Find Category")
        verbose_name_plural = _("Context Find Categories")


class ContextFindsSubcategories(abstract.AbstractTagModel):
    category = models.ForeignKey(ContextFindsCategories, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "category"), help_text=_("The category of the object, e.g. Weapon, Vessel."))

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    class Meta:
        verbose_name = _("Context Find Subcategory")
        verbose_name_plural = _("Context Find Subcategories")


class Metalwork(abstract.AbstractBaseModel):
    entry_num = models.ForeignKey(EntryNum, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Entry Number"), help_text=_("The entry number of the object."))
    literature_num = models.ForeignKey(LiteratureNum, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Literature Number"), help_text=_("The literature number of the object."))
    accession_num = models.ForeignKey(AccessionNum, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Accession Number"), help_text=_("The accession number of the object."))
    accession_certain = models.BooleanField(blank=True, verbose_name=_("Accession Number Certainty"), help_text=_(
        "Check if the accession number is certain and does not need review later."), default=True)
    museum = models.ManyToManyField(MuseumMeta, blank=True, verbose_name=_(
        "Museum"), help_text=_("The museum that holds or recorded the object."))
    collection = models.ManyToManyField(MuseumCollection, blank=True, verbose_name=_(
        "Collection"), help_text=_("The title of the museum or personal collection."))
    museum_certain = models.BooleanField(blank=True, verbose_name=_("Museum/Collection Certainty"), help_text=_(
        "Check if the museum/collection is certain and does not need review later."), default=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Location"), help_text=_("The location of the object."))
    location_certain = models.BooleanField(blank=True, verbose_name=_(
        "Location Certainty"), help_text=_("The certainty of the coordinate."), default=True)
    coord_system = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Coordinate System"), help_text=_("The EPSG code of the original coordinate system."))
    orig_coords = ArrayField(models.CharField(), size=2, null=True, blank=True, verbose_name=_(
        "Original Coordinates"), help_text=_("The original coordinates that were converted to lat/long.  Include if you are unsure of the accuracy of the conversion."))
    main_context = models.ForeignKey(Context, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Main Context"), help_text=_("The site or excavation context."))
    main_context_certain = models.BooleanField(blank=True, verbose_name=_("Main Context Certainty"), help_text=_(
        "Check if the primary context is certain and does not need review later."), default=True)
    find_context = models.ForeignKey(FindContext, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Find Context"), help_text=_("The context of the find. Should provide more detail than the primary context."))
    find_context_certain = models.BooleanField(blank=True, verbose_name=_("Find Context Certainty"), help_text=_(
        "Check if the find context is certain and does not need review later."), default=True)
    context_detail = models.ForeignKey(ContextDetail, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Context Detail"), help_text=_("The detailed context of the find. E.g., a specific layer or feature."))
    context_detail_certain = models.BooleanField(blank=True, verbose_name=_("Context Detail Certainty"), help_text=_(
        "Check if the context detail is certain and does not need review later."), default=True)
    context_keywords = models.ManyToManyField(ContextKeywords, blank=True, verbose_name=_(
        "Context Keywords"), help_text=_("Keywords that describe the context of the find."))
    multiperiod = models.BooleanField(blank=True, verbose_name=_("Multiperiod"), help_text=_(
        "Check if the site is associated with multiple periods."))
    dating = models.ManyToManyField(Period, blank=True, verbose_name=_(
        "Period(s) of activity"), help_text=_("The period(s) of activity of the site."))
    date_string = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Original Dating Text"), help_text=_("The dating text from the original file."))
    dating_certain = models.BooleanField(blank=True, verbose_name=_("Dating Certainty"), help_text=_(
        "Check if the dating is certain and does not need review later."), default=True)
    dendro_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Dendro Date"), help_text=_("The dendrochronological date of the object."))
    radiocarbon_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Radiocarbon Date"), help_text=_("The radiocarbon date of the object."))
    radiocarbon_years = models.CharField(max_length=256, blank=True, null=True, verbose_name=_(
        "Radiocarbon Year(s)"), help_text=_("The radiocarbon year(s) of the object."))
    radiocarbon_std = models.CharField(null=True, blank=True, verbose_name=_(
        "Radiocarbon StD"), help_text=_("The radiocarbon standard deviation of the object."))
    comments = models.TextField(null=True, blank=True, verbose_name=_(
        "Comments"), help_text=_("General comments about the entry."))
    certain_context_descriptors = models.ManyToManyField(ContextFindsSubcategories, blank=True, related_name=('certain_context_descriptors_subcategories'), verbose_name=_(
        "Related Finds/Materials - Certain"), help_text=_("Objects, etc. that were found at the site and do not need review later. Relates to presence/absence fields in original dataset."))
    uncertain_context_descriptors = models.ManyToManyField(ContextFindsSubcategories, blank=True, related_name=('uncertain_context_descriptors_subcategories'), verbose_name=_(
        "Related Finds/Materials - Possible"), help_text=_("Objects, etc. that were found at the site and need review later. Relates to presence/absence fields in original dataset."))

    def __str__(self) -> str:
        if self.entry_num and self.literature_num:
            name_str = f"{self.entry_num} - {self.literature_num}"
        else:
            name_str = self.entry_num or self.literature_num or self.accession_num or self.collection or ''
        return name_str

    class Meta:
        verbose_name = _("Metalwork")
        verbose_name_plural = _("Metalworks")


class ObjectCount(models.Model):
    metal = models.ForeignKey(
        Metalwork, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
            "Metalwork Object"), help_text=_("The corresponding metalwork object."))
    object = models.ForeignKey(
        ObjectDescription, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ManyToManyField(ObjectMaterials, blank=True, verbose_name=_(
        "material"), help_text=_("The material(s) of the object."))
    count = models.IntegerField(null=True, blank=True, verbose_name=_(
        "Number of objects"), help_text=_("The number of objects of this type with the same entry number, literature number, and accession number."))
    certainty = models.BooleanField(blank=True, verbose_name=_("Count Certainty"), help_text=_(
        "Check if the count is certain and does not need review later."), default=True)

    def __str__(self) -> str:
        def materials_list(self):
            materials = ','.join([material.text for material in self.material.all()])
        if self.metal and self.object:
            name_str = f"{self.metal.entry_num} - {self.object.subcategory}"
        else:
            name_str = self.metal.entry_num or self.metal.literature_num or self.metal.accession_num or self.metal.collection or 'No Info'
        return name_str

    class Meta:
        verbose_name = _("Object Count")
        verbose_name_plural = _("Object Counts")


class IndividualObjects(abstract.AbstractBaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Site"), help_text=_("The site in which the object was located."))
    accession_number = models.ForeignKey(AccessionNum, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Accession Number"), help_text=_("The accession number of the object."))
    museum = models.ForeignKey(MuseumMeta, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Museum"), help_text=_("The museum that holds or recorded the object."))
    object_type = models.ForeignKey(ObjectDescription, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Object Type"), help_text=_("The type of the object."))
    type_original = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        'Object Type (pre-translation)'), help_text=_('The object type text before translation to English.'))
    form = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Form"), help_text=_("The form of the object."))
    form_translation = models.TextField(max_length=1000, null=True,blank=True,verbose_name=_(
        'Form (Long Description)'), help_text=_('The form text before translation to English.'))
    form_original = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_(
        'Form (Pre-translation)'), help_text=_('The form text before translation to English.'))
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Variant"), help_text=_("The variant of the object."))
    variant_original = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        'Variant (pre-translation)'), help_text=_('The variant text before translation to English.'))
    count = models.IntegerField(null=True, blank=True, verbose_name=_(
        "Count"), help_text=_("The number of objects."))
    material = models.ManyToManyField(ObjectMaterials, blank=True, verbose_name=_(
        "Material"), help_text=_("The material of the object."))
    material_original = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        'Material (pre-translation)'), help_text=_('The material text before translation to English.'))
    period = models.ManyToManyField(Period, blank=True, verbose_name=_(
        "Period"), help_text=_("The period of the object."))
    period_original = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        'Period (pre-translation)'), help_text=_('The period text before translation to English.'))
    orig_coords = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Original Coords"), help_text=_("The original coordinates of the object."))
    orig_crs = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(
        "Original CRS"), help_text=_("The original CRS of the object."))
    # start_date = models.CharField(max_length=256,null=True, blank=True, verbose_name=_(
    #     "Start Date"), help_text=_("The start date of the object."))
    # end_date = models.CharField(max_length=256,null=True, blank=True, verbose_name=_(
    #     "End Date"), help_text=_("The end date of the object."))
    dating_original = models.CharField(max_length=256,null=True,blank=True,verbose_name=_("Dating (pre-translation)"), help_text=_("The original dating string before translation and processing."))
    object_id = models.ForeignKey(ObjectIds, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_(
        "Object ID"), help_text=_("The ID of the object in the relevant national database."))

    def __str__(self) -> str:
        if self.accession_number:
            return self.accession_number.accession_number
        else:
            return 'Item missing accession number'

    class Meta:
        verbose_name = _("Individual Find")
        verbose_name_plural = _("Individual Finds")
