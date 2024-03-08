import maritime.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models


class SiteType(abstract.AbstractTagModel):
    # Represents the type of the site

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    
    class Meta:
        verbose_name = _("Site Type")
        verbose_name_plural = _("Site Types")


class SampleType(abstract.AbstractTagModel):
    # Represents the type of the sample

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    
    class Meta:
        verbose_name = _("Sample Type")
        verbose_name_plural = _("Sample Types")


class Site(abstract.AbstractBaseModel):
    # Represents the archaeological sites of interests

    site_id      = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Site ID"), help_text=_("Unique identifier for the site.")) 

    # Site name is a field that includes the name of the site and it can be used to search for the site
    # This feld can leave empty if the site name is not known
    site_name       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("sitename"), help_text=_("Free-form, non-indexed site name of the site."))
    ADM0       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("ADM0"), help_text=_("The country in which the site is located."))
    ADM1       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("ADM1"), help_text=_("The first administrative division in which the site is located."))
    ADM2       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("ADM2"), help_text=_("The second administrative division in which the site is located."))
    ADM3       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("ADM3"), help_text=_("The third administrative division in which the site is located."))
    coordinates  = models.PointField(null=True, blank=True, verbose_name=_("Coordinates"), help_text=_("Mid-point coordinates of the site."))


    def __str__(self) -> str:

        name_str = f"Sitename {self.site_name}"
    
    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")

class PlankBoats(abstract.AbstractBaseModel):
    # Represents the archaeological plank boats information

    plankboat_id      = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("PlankBoat ID"), help_text=_("Unique identifier for the plankboat.")) 
    plankboat_name       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("plankboatname"), help_text=_("Free-form, non-indexed plankboat name of the plankboat."))
    site      = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the plankboat is located."))
    location       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("location"), help_text=_("The location of the plankboat."))

    start_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("start_date"), help_text=_("The start date of the plankboat."))
    end_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("end_date"), help_text=_("The end date of the plankboat."))


    notes      = models.TextField(null=True, blank=True, verbose_name=_("notes"), help_text=_("The notes of the plankboat."))

    est_length       = models.FloatField(null=True, blank=True, verbose_name=_("plankboatlength"), help_text=_("The length of the plankboat."))
    est_width       = models.FloatField(null=True, blank=True, verbose_name=_("plankboatwidth"), help_text=_("The width of the plankboat."))
    est_height       = models.FloatField(null=True, blank=True, verbose_name=_("plankboatheight"), help_text=_("The height of the plankboat."))
    

    hull_material       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("hullmaterial"), help_text=_("The hull material of the plankboat."))
    thwarts_material       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("thwartsmaterial"), help_text=_("The thwarts material of the plankboat."))
    fastening_planks       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("fasteningplanks"), help_text=_("The fastening planks of the plankboat."))
    bottom_side_strakes       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("bottomsidestrakes"), help_text=_("The bottom side strakes of the plankboat."))
    outer_bottom_plank      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("outerbottomplank"), help_text=_("The outer bottom plank of the plankboat."))
    
    cauking       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("cauking"), help_text=_("The cauking of the plankboat."))

    cleat_number = models.IntegerField(null=True, blank=True, verbose_name=_("cleatnumber"), help_text=_("The number of cleats of the plankboat."))
    cleat_length       = models.FloatField(null=True, blank=True, verbose_name=_("plankboatcapacity"), help_text=_("The capacity of the plankboat."))
    cleat_width       = models.FloatField(null=True, blank=True, verbose_name=_("plankboatweight"), help_text=_("The weight of the plankboat."))
    cleat_heigth       = models.IntegerField(null=True, blank=True, verbose_name=_("plankboatcrew"), help_text=_("The crew of the plankboat."))

    shape_holes       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("shapeholes"), help_text=_("The shape holes of the plankboat."))
    diam_holes       = models.FloatField(null=True, blank=True, verbose_name=_("diamholes"), help_text=_("The diameter holes of the plankboat."))
    caprail       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("caprail"), help_text=_("The caprail of the plankboat."))
    tree_nails       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("treenails"), help_text=_("The treenails of the plankboat."))
    keel_bending       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("keelbending"), help_text=_("The keel bending of the plankboat."))
    outer_bending       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("outerbending"), help_text=_("The outer bending of the plankboat."))
    low_bending       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("lowbending"), help_text=_("The low bending of the plankboat."))
    longitudinal_bending       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("longitudinalbending"), help_text=_("The longitudinal bending of the plankboat."))
    longest_plank_length       = models.FloatField(null=True, blank=True, verbose_name=_("longestplanklength"), help_text=_("The longest plank length of the plankboat."))
    size_trees       = models.FloatField(null=True, blank=True, verbose_name=_("sizetrees"), help_text=_("The size trees of the plankboat."))
    tootlmarks       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("tootlmarks"), help_text=_("The tootl marks of the plankboat."))
    individual_lashings       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("individuallashings"), help_text=_("The individual lashings of the plankboat."))
    continuous_stiching       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("continuouslashings"), help_text=_("The continuous lashings of the plankboat."))

    comments       = models.TextField(null=True, blank=True, verbose_name=_("comments"), help_text=_("The comments of the plankboat."))
    references       = models.TextField(null=True, blank=True, verbose_name=_("references"), help_text=_("The references of the plankboat."))

    def __str__(self) -> str:

        name_str = f"Plankboatname {self.plankboat_name}"
        return name_str
    
    class Meta:
        verbose_name = _("PlankBoat")
        verbose_name_plural = _("PlankBoats")

class LogBoats(abstract.AbstractBaseModel):
    # Represents the archaeological log boats information

    logboat_id      = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("LogBoat ID"), help_text=_("Unique identifier for the logboat.")) 
    logboat_name       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("logboatname"), help_text=_("Free-form, non-indexed logboat name of the logboat."))
    site      = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the logboat is located."))
    context = models.ForeignKey(SiteType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("context"), help_text=_("The context of the logboat."))

    wood_species       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("woodspecies"), help_text=_("The wood species of the logboat."))
    period       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the logboat."))
    dendro_lab_code      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("dendrolabcode"), help_text=_("The dendro lab code of the logboat."))
    # Integer or date field ?
    dendro_bc_date      = models.IntegerField(null=True, blank=True, verbose_name=_("dendrobcdate"), help_text=_("The dendro bc date of the logboat."))
    dendro_std     = models.IntegerField(null=True, blank=True, verbose_name=_("dendrostd"), help_text=_("The dendro std of the logboat."))

    preservation       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("preservation"), help_text=_("The preservation of the logboat."))
    length       = models.FloatField(null=True, blank=True, verbose_name=_("logboatlength"), help_text=_("The length of the logboat."))
    width      = models.FloatField(null=True, blank=True, verbose_name=_("logboatwidth"), help_text=_("The width of the logboat."))
    depth       = models.FloatField(null=True, blank=True, verbose_name=_("logboatdepth"), help_text=_("The depth of the logboat."))

    est_length       = models.FloatField(null=True, blank=True, verbose_name=_("logboatlength"), help_text=_("The length of the logboat."))
    est_width       = models.FloatField(null=True, blank=True, verbose_name=_("logboatwidth"), help_text=_("The width of the logboat."))
    est_height       = models.FloatField(null=True, blank=True, verbose_name=_("logboatheight"), help_text=_("The height of the logboat."))
    
    bow_shape       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("bowshape"), help_text=_("The bow shape of the logboat."))
    stern_shape       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("sternshape"), help_text=_("The stern shape of the logboat."))
    hull_shape       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("hullshape"), help_text=_("The hull shape of the logboat."))
    basal      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("basal"), help_text=_("The basal of the logboat."))
    transerve_ridges       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("transerveridges"), help_text=_("The transerve ridges of the logboat."))
    other_features       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("otherfeatures"), help_text=_("The other features of the logboat."))
    repair      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("repair"), help_text=_("The repair of the logboat."))
    toolmarks       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("toolmarks"), help_text=_("The tool marks of the logboat."))
    burnt_mark      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("burntmark"), help_text=_("The burnt mark of the logboat."))
    other_material      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("othermaterial"), help_text=_("The other material of the logboat."))

    notes      = models.TextField(null=True, blank=True, verbose_name=_("notes"), help_text=_("The notes of the logboat."))
    refernce      = models.TextField(null=True, blank=True, verbose_name=_("refernce"), help_text=_("The refernce of the logboat."))


    def __str__(self) -> str:

        name_str = f"Logboatname {self.logboat_name}"
        return name_str
    
    class Meta:        
        verbose_name = _("LogBoat")
        verbose_name_plural = _("LogBoats")


class LandingPints(abstract.AbstractBaseModel):

    landing_id      = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Landing ID"), help_text=_("Unique identifier for the landing."))
    site      = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the landing is located."))
    period       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the landing."))
    start_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("start_date"), help_text=_("The start date of the landing."))
    end_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("end_date"), help_text=_("The end date of the landing."))
    materials       = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("materials"), help_text=_("The materials of the landing."))
    reason       = models.TextField(null=True, blank=True, verbose_name=_("reason"), help_text=_("The reason of the landing."))
    geographic      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("geographic"), help_text=_("The geographic of the landing."))

    def __str__(self) -> str:

        name_str = f"Landingname {self.landing_id}"
        return name_str
    
    class Meta:                
        verbose_name = _("LandingPint")
        verbose_name_plural = _("LandingPints")


class NewSamples(abstract.AbstractBaseModel):

    sample_id     = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Sample ID"), help_text=_("Unique identifier for the sample."))
    site      = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the sample is located."))
    Lead = models.BooleanField(null=True, blank=True, verbose_name=_("Pb"), help_text=_("The presence of Pb."))
    aDNA = models.BooleanField(null=True, blank=True, verbose_name=_("aDNA"), help_text=_("The presence of aDNA."))
    Carbon_14 = models.BooleanField(null=True, blank=True, verbose_name=_("C/14"), help_text=_("The presence of Carbon-14."))
    Strontium = models.BooleanField(null=True, blank=True, verbose_name=_("Sr"), help_text=_("The presence of Sr."))
    Carbon_to_nitrogen_ratio = models.BooleanField(null=True, blank=True, verbose_name=_("C/N"), help_text=_("The presence of C/N."))


    def __str__(self) -> str:

        name_str = f"Samplename {self.sample_id}"
        return name_str
    
    class Meta:                
        verbose_name = _("NewSample")
        verbose_name_plural = _("NewSamples")


class Radiocarbon(abstract.AbstractBaseModel):

    date_id     = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Date ID"), help_text=_("Unique identifier for the Radiocarbon."))
    site      = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the date is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("sample"), help_text=_("The sample of the Radiocarbon."))
    site_type = models.ForeignKey(SiteType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site_type"), help_text=_("The site type."))
    period      = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the sample."))
    lab_id     = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("lab_id"), help_text=_("The lab id of the sample."))
    c14_age = models.IntegerField(null=True, blank=True, verbose_name=_("c14_age"), help_text=_("The c14 age"))
    c14_std = models.IntegerField(null=True, blank=True, verbose_name=_("c14_std"), help_text=_("The c14 std"))
    material = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("material"), help_text=_("The material of the Radiocarbon."))
    species = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("species"), help_text=_("The species of the sample."))
    d13c = models.FloatField(null=True, blank=True, verbose_name=_("d13c"), help_text=_("The d13c of the sample."))
    d15n = models.FloatField(null=True, blank=True, verbose_name=_("d15n"), help_text=_("The d15n of the sample."))
    percentage_of_Carbon = models.FloatField(null=True, blank=True, verbose_name=_("percentage_of_Carbon"), help_text=_("The percentage of Carbon of the sample."))
    Carbon_ratio_to_Nitrogen = models.FloatField(null=True, blank=True, verbose_name=_("percentage_of_Nitrogen"), help_text=_("The percentage of the Carbon to Nitrogen."))
    percentage_of_Yield = models.FloatField(null=True, blank=True, verbose_name=_("percentage_of_Yield"), help_text=_("The percentage of the Yield of the sample."))
    Carbon_to_nitrogen_ratio = models.FloatField(null=True, blank=True, verbose_name=_("C/N"), help_text=_("The presence of C/N."))
    marine_reservoir = models.FloatField(null=True, blank=True, verbose_name=_("marine_reservoir"), help_text=_("The marine reservoir of the Radiocarbon."))
    notes = models.TextField(null=True, blank=True, verbose_name=_("notes"), help_text=_("The notes of the Radiocarbon."))
    reference = models.TextField(null=True, blank=True, verbose_name=_("reference"), help_text=_("The reference of the Radiocarbon."))
    source_database = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("source_database"), help_text=_("The source database of the Radiocarbon."))

    def __str__(self) -> str:

        name_str = f"Date {self.date_id}"
        return name_str

    class Meta:
        verbose_name = _("Radiocarbon")
        verbose_name_plural = _("Radiocarbons")


class LeadIsotopeRation(abstract.AbstractBaseModel):
    
        lead206_204Pb = models.FloatField(null=True, blank=True, verbose_name=_("lead206_204"), help_text=_("The lead206_204 of the sample."))
        lead207_204Pb = models.FloatField(null=True, blank=True, verbose_name=_("lead207_204"), help_text=_("The lead207_204 of the sample."))
        lead208_204Pb = models.FloatField(null=True, blank=True, verbose_name=_("lead208_204"), help_text=_("The lead208_204 of the sample."))
        lead207_206Pb = models.FloatField(null=True, blank=True, verbose_name=_("lead207_206"), help_text=_("The lead207_206 of the sample."))
        lead208_206Pb = models.FloatField(null=True, blank=True, verbose_name=_("lead208_206"), help_text=_("The lead208_206 of the sample."))
        lead208_207Pb = models.FloatField(null=True, blank=True, verbose_name=_("lead208_207"), help_text=_("The lead208_207 of the sample."))
    
        def __str__(self) -> str:            
            return "LeadIsotopeRation"
        
        class Meta:
            verbose_name = _("LeadIsotopeRation")
            verbose_name_plural = _("LeadIsotopeRations")


class  Element(abstract.AbstractBaseModel):
    elemant_name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("elemant_name"), help_text=_("The elemant name of the sample."))
    element_symbol = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("element_symbol"), help_text=_("The element symbol of the sample."))
    element_number = models.IntegerField(null=True, blank=True, verbose_name=_("element_number"), help_text=_("The element number of the sample."))

    def __str__(self) -> str:
        return self.elemant_name    

    class Meta:     
        verbose_name = _("Elemnt")
        verbose_name_plural = _("Elemnts")


class MetalAnalysis(abstract.AbstractBaseModel):
    metal_id     = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Metal ID"), help_text=_("Unique identifier for the metal."))
    site     = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the metal is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("sample"), help_text=_("The sample of the metal."))
    AMA = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("AMA"), help_text=_("The AMA of the metal."))
    context = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("context"), help_text=_("The context of the metal."))
    object_description = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("object_description"), help_text=_("The object description of the metal."))
    general_typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("general_typology"), help_text=_("The general typology of the metal."))
    typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("typology"), help_text=_("The typology of the metal."))
    start_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("start_date"), help_text=_("The start date of the metal."))
    end_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("end_date"), help_text=_("The end date of the metal."))
    isotope_ratio = models.ManyToManyField(LeadIsotopeRation, blank=True, verbose_name=_("isotope_ratio"), help_text=_("The isotope ratio of the metal."))
    elements = models.ManyToManyField(Element, blank=True, verbose_name=_("elements"), help_text=_("The elements of the metal."))

    def __str__(self) -> str:   
        name_str = f"Metal {self.metal_id}"
        return name_str
    
    class Meta:        
        verbose_name = _("MetalAnalysis")
        verbose_name_plural = _("MetalAnalyses")

class aDNA(abstract.AbstractBaseModel):
    aDNA_id     = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("aDNA ID"), help_text=_("Unique identifier for the aDNA."))
    site     = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the aDNA is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("sample"), help_text=_("The sample of the aDNA."))
    genetic_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("genetic_id"), help_text=_("The genetic id of the aDNA."))
    master_id = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("master_id"), help_text=_("The master id of the aDNA."))
    skeletal_code = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("skeletal_code"), help_text=_("The skeletal code of the aDNA."))
    skeletal_element = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("skeletal_element"), help_text=_("The skeletal element of the aDNA."))

    year_date = models.DateField()
    dating_method = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("dating_method"), help_text=_("The dating method of the aDNA."))
    age_at_seath = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("age_at_seath"), help_text=_("The age at seath of the aDNA."))
    period = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the aDNA."))
    cultural_group = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("cultural_group"), help_text=_("The cultural group of the aDNA."))
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"), help_text=_("The comments of the aDNA."))
    reference = models.TextField(null=True, blank=True, verbose_name=_("reference"), help_text=_("The reference of the aDNA."))

    def __str__(self) -> str:
        name_str = f"aDNA {self.aDNA_id}"
        return name_str
    
    class Meta:
        verbose_name = _("aDNA")
        verbose_name_plural = _("aDNAs")

class IsotopesBio(abstract.AbstractBaseModel):
    bio_id     = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Isotopes Bio ID"), help_text=_("Unique identifier for the Isotopes Bio."))
    site     = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the Isotopes Bio is located."))
    sample = models.ForeignKey(NewSamples, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("sample"), help_text=_("The sample of the Isotopes Bio."))
    individual_id = models.IntegerField(null=True, blank=True, verbose_name=_("individual_id"), help_text=_("The individual id of the Isotopes Bio."))
    smple_type = models.ForeignKey(SampleType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("smple_type"), help_text=_("The smple type of the Isotopes Bio."))
    species = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("species"), help_text=_("The species of the Isotopes Bio."))
    age = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("age"), help_text=_("The age of the Isotopes Bio."))
    sex = models.CharField(max_length=256, null=True, blank=True)
    d13c = models.FloatField(null=True, blank=True, verbose_name=_("d13c"), help_text=_("The d13c of the Isotopes Bio."))
    percentage_of_Carbon = models.FloatField(null=True, blank=True, verbose_name=_("percentage_of_Carbon"), help_text=_("The percentage of Carbon of the Isotopes Bio."))
    d13C_scale = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("d13C_scale"), help_text=_("The d13C scale of the Isotopes Bio."))
    d15N = models.FloatField(null=True, blank=True, verbose_name=_("d15N"), help_text=_("The d15N of the Isotopes Bio."))
    percentage_of_Nitrogen = models.FloatField(null=True, blank=True, verbose_name=_("percentage_of_Nitrogen"), help_text=_("The percentage of Nitrogen of the Isotopes Bio."))
    d15N_scale = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("d15N_scale"), help_text=_("The d15N scale of the Isotopes Bio."))
    Carbon_to_nitrogen_ratio = models.FloatField(null=True, blank=True, verbose_name=_("C/N"), help_text=_("The presence of C/N."))
    d34S = models.FloatField(null=True, blank=True, verbose_name=_("d34S"), help_text=_("The d34S of the Isotopes Bio."))
    Sr87_86Sr = models.FloatField(null=True, blank=True, verbose_name=_("Sr87_86Sr"), help_text=_("The Sr87_86Sr of the Isotopes Bio."))
    d180 = models.FloatField(null=True, blank=True, verbose_name=_("d180"), help_text=_("The d180 of the Isotopes Bio."))
    d180_scale = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("d180_scale"), help_text=_("The d180 scale of the Isotopes Bio."))
    d180_prep_method = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("d180_prep_method"), help_text=_("The d180 prep method of the Isotopes Bio."))
    notes = models.TextField(null=True, blank=True, verbose_name=_("notes"), help_text=_("The notes of the Isotopes Bio."))
    sample_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("sample_number"), help_text=_("The sample number of the Isotopes Bio."))
    reference = models.TextField(null=True, blank=True, verbose_name=_("reference"), help_text=_("The reference of the Isotopes Bio."))

    def __str__(self) -> str:
        name_str = f"IsotopesBio {self.bio_id}"
        return name_str
    
    class Meta:
        verbose_name = _("IsotopesBio")
        verbose_name_plural = _("IsotopesBios")


class LNHouses(abstract.AbstractBaseModel):
    house_id     = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("House ID"), help_text=_("Unique identifier for the House."))
    site     = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the House is located."))
    number_houses = models.IntegerField(null=True, blank=True, verbose_name=_("number_houses"), help_text=_("The number of houses of the House."))
    number_BA_houses = models.IntegerField(null=True, blank=True, verbose_name=_("number_BA_houses"), help_text=_("The number of BA houses of the House."))
    features = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("features"), help_text=_("The features of the House."))
    dating_method = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("dating_method"), help_text=_("The dating method of the House."))
    feature_house_K1 = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("feature_house_K1"), help_text=_("The feature house K1 of the House."))
    context_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("context_date"), help_text=_("The context date of the House."))
    aisle = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("aisle"), help_text=_("The aisle of the House."))
    aisle_type = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("aisle_type"), help_text=_("The aisle type of the House."))
    min_length = models.FloatField(null=True, blank=True, verbose_name=_("min_length"), help_text=_("The min length of the House."))
    max_length = models.FloatField(null=True, blank=True, verbose_name=_("max_length"), help_text=_("The max length of the House."))
    min_width = models.FloatField(null=True, blank=True, verbose_name=_("min_width"), help_text=_("The min width of the House."))
    max_width = models.FloatField(null=True, blank=True, verbose_name=_("max_width"), help_text=_("The max width of the House."))
    orientation = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("orientation"), help_text=_("The orientation of the House."))
    earliest_period_typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("earliest_period_typology"), help_text=_("The earliest period typology of the House."))
    latest_period_typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("latest_period_typology"), help_text=_("The latest period typology of the House."))
    prefered_dating_method = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("prefered_dating_method"), help_text=_("The prefered dating method of the House."))
    dating_typology = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("dating_typology"), help_text=_("The dating typology of the House."))
    dating_14C = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("dating_14C"), help_text=_("The dating 14C of the House."))
    final_date = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("final_date"), help_text=_("The final date of the House."))
    reason_exclusion = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("reason_exclusion"), help_text=_("The reason exclusion of the House."))
    references  = models.TextField(null=True, blank=True, verbose_name=_("references"), help_text=_("The references of the House."))
    url = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("url"), help_text=_("The url of the House."))

    def __str__(self) -> str:
        name_str = f"House {self.house_id}"
        return name_str
    
    class Meta:
        verbose_name = _("LNHouse")
        verbose_name_plural = _("LNHouses")

class NorwayDaggers(abstract.AbstractBaseModel):
    dagger_id    = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Dagger ID"), help_text=_("Unique identifier for the Dagger."))
    site     = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the Dagger is located."))
    type = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("type"), help_text=_("The type of the Dagger."))
    period = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the Dagger."))
    context = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("context"), help_text=_("The context of the Dagger."))
    comments = models.TextField(null=True, blank=True, verbose_name=_("comments"), help_text=_("The comments of the Dagger."))
    references = models.TextField(null=True, blank=True, verbose_name=_("references"), help_text=_("The references of the Dagger."))

    def __str__(self) -> str:
        name_str = f"Dagger {self.dagger_id}"
        return name_str
    
    class Meta:
        verbose_name = _("NorwayDagger")
        verbose_name_plural = _("NorwayDaggers")

class NorwayShaftHoleAxes(abstract.AbstractBaseModel):
    shaft_hole_axe_id    = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Shaft Hole Axe ID"), help_text=_("Unique identifier for the Shaft Hole Axe."))
    site     = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("site"), help_text=_("The site in which the Shaft Hole Axe is located."))
    museum = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("museum"), help_text=_("The museum of the Shaft Hole Axe."))
    museum_number = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("museum_number"), help_text=_("The museum number of the Shaft Hole Axe."))
    object_type = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("type"), help_text=_("The type of the Shaft Hole Axe."))   
    period = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("period"), help_text=_("The period of the Shaft Hole Axe."))
    form = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("form"), help_text=_("The form of the Shaft Hole Axe."))
    variant = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("variant"), help_text=_("The variant of the Shaft Hole Axe."))
    material = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("material"), help_text=_("The material of the Shaft Hole Axe."))

    def __str__(self) -> str:
        name_str = f"ShaftHoleAxe {self.shaft_hole_axe_id}"
        return name_str
    
    class Meta:
        verbose_name = _("NorwayShaftHoleAxe")
        verbose_name_plural = _("NorwayShaftHoleAxes")