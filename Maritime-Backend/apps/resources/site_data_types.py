"""The "kinds of data a site has" tags, kept as SiteType rows on Site.site_type.

These are different from the archaeological site types (settlement, hoard, ...):
they say which resource tables hold rows for a site, so the map can colour or
filter markers by available data.

Single source of truth for both upload_scripts/fill_data_site_types.py and the
`data_types` field in the site serializers.

The keys are the reverse accessor on Site (the lowercase model name), the values
are the SiteType.text to use. Rename a value here if the label should differ from
what the mining sites already use - the text must match exactly, since SiteType.text
is unique and matched case-sensitively.
"""

# Model name -> SiteType.text
DATA_TYPE_LABELS = {
	"Radiocarbon": "Radiocarbon",
	"IndividualObjects": "Findspot",
	"Metalwork": "Metalwork",
	"MetalAnalysis": "Metal Analysis",
	"aDNA": "aDNA",
	"IsotopesBio": "Isotopes",
	"NewSamples": "Samples",
	"Boat": "Boat",
	"LNHouses": "Late Neolithic House",
	"LandingPoints": "Landing Point",
}

# Types that were tagged by hand before this existed (e.g. mining sites). They are
# not derived from a resource table, so the fill script never adds or removes them,
# but the API still reports them as data types.
MANUAL_DATA_TYPES = ["Mining site"]

DATA_TYPE_NAMES = frozenset(DATA_TYPE_LABELS.values()) | frozenset(MANUAL_DATA_TYPES)
