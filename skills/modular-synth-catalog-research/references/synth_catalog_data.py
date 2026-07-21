"""
Synth Catalog bridge for PatchHive.

Source: Completed research (767 brands + detailed major modules).
Provenance: OBSERVED/INFERRED via 20-source rotation.
ABX-Core v1.3 aligned.
"""

MAJOR_BRANDS = [
    "2hp", "4ms Company", "ALM Busy Circuits", "Acid Rain Technology",
    "ADDAC System", "Befaco", "Doepfer", "Bastl Instruments", "Cwejman",
    "Dreadbox", "Erica Synths", "Endorphin.es", "Expert Sleepers",
    "Intellijel", "Make Noise", "Mutable Instruments", "Behringer",
    "Noise Engineering", "Pittsburgh Modular", "Qu-Bit Electronix",
    "Rossum Electro-Music", "TipTop Audio", "Verbos Electronics", "WMD",
    "Winterbloom", "Xaoc Devices", "Zlob Modular", "ZVEX Modular", "Instruo",
]

SYNTH_CATALOG_MODULES = [
    {
        "brand": "Noise Engineering",
        "name": "Basimilus Iteritas Alter",
        "hp": 10,
        "module_type": "VCO",
        "power_12v_ma": 70,
        "power_neg12v_ma": 10,
        "io_ports": [
            {"name": "Pitch", "type": "cv_in"},
            {"name": "Trig", "type": "gate_in"},
            {"name": "Out", "type": "audio_out"},
        ],
        "tags": ["drum", "percussion", "digital"],
        "description": "Digital drum voice",
        "manufacturer_url": "https://noiseengineering.us/",
        "source": "SynthCatalogResearch",
        "source_reference": "phase2-major-brands.md",
    },
    {
        "brand": "Make Noise",
        "name": "Maths",
        "hp": 20,
        "module_type": "UTIL",
        "power_12v_ma": 60,
        "power_neg12v_ma": 50,
        "io_ports": [
            {"name": "CH1", "type": "cv_in"},
            {"name": "SUM", "type": "cv_out"},
        ],
        "tags": ["function generator"],
        "description": "Analog computer / function generator",
        "manufacturer_url": "https://www.makenoisemusic.com/",
        "source": "SynthCatalogResearch",
    },
    {
        "brand": "Instruo",
        "name": "arbhar",
        "hp": 18,
        "module_type": "SAMP",
        "power_12v_ma": 120,
        "power_neg12v_ma": 15,
        "io_ports": [
            {"name": "In", "type": "audio_in"},
            {"name": "Out", "type": "audio_out"},
        ],
        "tags": ["granular"],
        "description": "Granular processor",
        "manufacturer_url": "https://www.instruomodular.com/",
        "source": "SynthCatalogResearch",
    },
]
