"""TCC destination definitions — 330 destinations with extraction strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types import TccDestination

# Each destination tuple fields (positional):
#   [0] tcc_index : int          — TCC destination number (1-330)
#   [1] name      : str          — TCC destination name
#   [2] region    : str          — TCC region name
#   [3] iso_a2    : str | None   — ISO 3166-1 alpha-2 code (None for sub-national)
#   [4] iso_a3    : str | None   — ISO 3166-1 alpha-3 code (None for sub-national)
#   [5] iso_n3    : int | None   — ISO 3166-1 numeric code (None for sub-national)
#   [6] sovereign : str          — Sovereign state name
#   [7] type      : str          — Feature type: "country" | "territory" | "disputed"
#                                               | "subnational" | "antarctic"
#
# EXTRACTIONS dict fields (per-entry keys vary by strategy):
#   strategy       : str   — Extraction strategy (see strategy comments below)
#   adm0_a3        : str   — NE ADM0_A3 / SU_A3 code for the parent country
#   su_a3          : str   — NE SU_A3 code (strategy="subunit")
#   admin1         : list  — Province names to dissolve (strategy="admin1")
#   subtract_admin1: list  — Province names to subtract (strategy="remainder")
#   subtract_disputed: list — Disputed layer feature names to subtract
#   merge_disputed : list  — Disputed layer feature names to merge in
#   parent_adm0_a3 : str   — Parent country A3 code (strategy="island_bbox")
#   parent_admin1  : str   — Parent province name (strategy="island_bbox")
#   bbox           : tuple — (west, south, east, north) for bbox extraction
#   side           : str   — "europe" or "asia" (strategy="clip")
#   lon_west/lon_east: float — Sector bounds (strategy="antarctic")
#   sectors        : list  — Multi-sector defs (strategy="antarctic")
#   lat, lon       : float — Point coordinates (strategy="point")

type _DestRow = tuple[int, str, str, str | None, str | None, int | None, str, str]

DESTINATIONS: list[_DestRow] = [
    # === PACIFIC OCEAN (1-40) ===
    (1, "Austral Islands", "Pacific Ocean", None, None, None, "France", "territory"),
    (2, "Australia", "Pacific Ocean", "AU", "AUS", 36, "Australia", "country"),
    (3, "Chatham Islands", "Pacific Ocean", None, None, None, "New Zealand", "territory"),
    (4, "Cook Islands", "Pacific Ocean", "CK", "COK", 184, "Cook Islands", "country"),
    (5, "Easter Island", "Pacific Ocean", None, None, None, "Chile", "territory"),
    (6, "Fiji Islands", "Pacific Ocean", "FJ", "FJI", 242, "Fiji", "country"),
    (7, "French Polynesia", "Pacific Ocean", "PF", "PYF", 258, "France", "territory"),
    (8, "Galapagos Islands", "Pacific Ocean", None, None, None, "Ecuador", "subnational"),
    (9, "Guam", "Pacific Ocean", "GU", "GUM", 316, "United States", "territory"),
    (10, "Hawaiian Islands", "Pacific Ocean", None, None, None, "United States", "subnational"),
    (11, "Juan Fernandez Islands", "Pacific Ocean", None, None, None, "Chile", "territory"),
    (12, "Kiribati", "Pacific Ocean", "KI", "KIR", 296, "Kiribati", "country"),
    (13, "Line/Phoenix Islands", "Pacific Ocean", None, None, None, "Kiribati", "territory"),
    (14, "Lord Howe Island", "Pacific Ocean", None, None, None, "Australia", "territory"),
    (15, "Marquesas Islands", "Pacific Ocean", None, None, None, "France", "territory"),
    (16, "Marshall Islands", "Pacific Ocean", "MH", "MHL", 584, "Marshall Islands", "country"),
    (17, "Micronesia", "Pacific Ocean", "FM", "FSM", 583, "Micronesia", "country"),
    (18, "Midway Island", "Pacific Ocean", None, None, None, "United States", "territory"),
    (19, "Nauru", "Pacific Ocean", "NR", "NRU", 520, "Nauru", "country"),
    (20, "New Caledonia & Dependencies", "Pacific Ocean", "NC", "NCL", 540, "France", "territory"),
    (21, "New Zealand", "Pacific Ocean", "NZ", "NZL", 554, "New Zealand", "country"),
    (22, "Niue", "Pacific Ocean", "NU", "NIU", 570, "Niue", "country"),
    (23, "Norfolk Island", "Pacific Ocean", "NF", "NFK", 574, "Australia", "territory"),
    (24, "Northern Marianas", "Pacific Ocean", "MP", "MNP", 580, "United States", "territory"),
    (25, "Ogasawara", "Pacific Ocean", None, None, None, "Japan", "territory"),
    (26, "Palau", "Pacific Ocean", "PW", "PLW", 585, "Palau", "country"),
    (27, "Papua New Guinea", "Pacific Ocean", "PG", "PNG", 598, "Papua New Guinea", "country"),
    (
        28,
        "Papua New Guinea \u2013 Islands Region",
        "Pacific Ocean",
        None,
        None,
        None,
        "Papua New Guinea",
        "subnational",
    ),
    (29, "Pitcairn Island", "Pacific Ocean", "PN", "PCN", 612, "United Kingdom", "territory"),
    (30, "Ryukyu Islands", "Pacific Ocean", None, None, None, "Japan", "subnational"),
    (31, "Samoa American", "Pacific Ocean", "AS", "ASM", 16, "United States", "territory"),
    (32, "Samoa", "Pacific Ocean", "WS", "WSM", 882, "Samoa", "country"),
    (33, "Solomon Islands", "Pacific Ocean", "SB", "SLB", 90, "Solomon Islands", "country"),
    (34, "Tasmania", "Pacific Ocean", None, None, None, "Australia", "subnational"),
    (35, "Tokelau Islands", "Pacific Ocean", "TK", "TKL", 772, "New Zealand", "territory"),
    (36, "Tonga", "Pacific Ocean", "TO", "TON", 776, "Tonga", "country"),
    (37, "Tuvalu", "Pacific Ocean", "TV", "TUV", 798, "Tuvalu", "country"),
    (38, "Vanuatu", "Pacific Ocean", "VU", "VUT", 548, "Vanuatu", "country"),
    (39, "Wake Island", "Pacific Ocean", None, None, None, "United States", "territory"),
    (40, "Wallis & Futuna Islands", "Pacific Ocean", "WF", "WLF", 876, "France", "territory"),
    # === NORTH AMERICA (41-46) ===
    (41, "Alaska", "North America", None, None, None, "United States", "subnational"),
    (42, "Canada", "North America", "CA", "CAN", 124, "Canada", "country"),
    (43, "Mexico", "North America", "MX", "MEX", 484, "Mexico", "country"),
    (44, "Prince Edward Island", "North America", None, None, None, "Canada", "subnational"),
    (45, "St. Pierre & Miquelon", "North America", "PM", "SPM", 666, "France", "territory"),
    (
        46,
        "United States (Contiguous)",
        "North America",
        "US",
        "USA",
        840,
        "United States",
        "country",
    ),
    # === CENTRAL AMERICA (47-53) ===
    (47, "Belize", "Central America", "BZ", "BLZ", 84, "Belize", "country"),
    (48, "Costa Rica", "Central America", "CR", "CRI", 188, "Costa Rica", "country"),
    (49, "El Salvador", "Central America", "SV", "SLV", 222, "El Salvador", "country"),
    (50, "Guatemala", "Central America", "GT", "GTM", 320, "Guatemala", "country"),
    (51, "Honduras", "Central America", "HN", "HND", 340, "Honduras", "country"),
    (52, "Nicaragua", "Central America", "NI", "NIC", 558, "Nicaragua", "country"),
    (53, "Panama", "Central America", "PA", "PAN", 591, "Panama", "country"),
    # === SOUTH AMERICA (54-67) ===
    (54, "Argentina", "South America", "AR", "ARG", 32, "Argentina", "country"),
    (55, "Bolivia", "South America", "BO", "BOL", 68, "Bolivia", "country"),
    (56, "Brazil", "South America", "BR", "BRA", 76, "Brazil", "country"),
    (57, "Chile", "South America", "CL", "CHL", 152, "Chile", "country"),
    (58, "Colombia", "South America", "CO", "COL", 170, "Colombia", "country"),
    (59, "Ecuador", "South America", "EC", "ECU", 218, "Ecuador", "country"),
    (60, "French Guiana", "South America", "GF", "GUF", 254, "France", "territory"),
    (61, "Guyana", "South America", "GY", "GUY", 328, "Guyana", "country"),
    (62, "Nueva Esparta", "South America", None, None, None, "Venezuela", "subnational"),
    (63, "Paraguay", "South America", "PY", "PRY", 600, "Paraguay", "country"),
    (64, "Peru", "South America", "PE", "PER", 604, "Peru", "country"),
    (65, "Suriname", "South America", "SR", "SUR", 740, "Suriname", "country"),
    (66, "Uruguay", "South America", "UY", "URY", 858, "Uruguay", "country"),
    (67, "Venezuela", "South America", "VE", "VEN", 862, "Venezuela", "country"),
    # === CARIBBEAN (68-98) ===
    (68, "Anguilla", "Caribbean", "AI", "AIA", 660, "United Kingdom", "territory"),
    (69, "Antigua & Barbuda", "Caribbean", "AG", "ATG", 28, "Antigua and Barbuda", "country"),
    (70, "Aruba", "Caribbean", "AW", "ABW", 533, "Netherlands", "territory"),
    (71, "Bahamas", "Caribbean", "BS", "BHS", 44, "Bahamas", "country"),
    (72, "Barbados", "Caribbean", "BB", "BRB", 52, "Barbados", "country"),
    (73, "Bonaire", "Caribbean", None, "BES", None, "Netherlands", "territory"),
    (74, "Cayman Islands", "Caribbean", "KY", "CYM", 136, "United Kingdom", "territory"),
    (75, "Cuba", "Caribbean", "CU", "CUB", 192, "Cuba", "country"),
    (76, "Curacao", "Caribbean", "CW", "CUW", 531, "Netherlands", "territory"),
    (77, "Dominica", "Caribbean", "DM", "DMA", 212, "Dominica", "country"),
    (78, "Dominican Republic", "Caribbean", "DO", "DOM", 214, "Dominican Republic", "country"),
    (79, "Grenada & Dependencies", "Caribbean", "GD", "GRD", 308, "Grenada", "country"),
    (80, "Guadeloupe & Dependencies", "Caribbean", "GP", "GLP", 312, "France", "territory"),
    (81, "Haiti", "Caribbean", "HT", "HTI", 332, "Haiti", "country"),
    (82, "Jamaica", "Caribbean", "JM", "JAM", 388, "Jamaica", "country"),
    (83, "Martinique", "Caribbean", "MQ", "MTQ", 474, "France", "territory"),
    (84, "Montserrat", "Caribbean", "MS", "MSR", 500, "United Kingdom", "territory"),
    (85, "Nevis", "Caribbean", None, None, None, "Saint Kitts and Nevis", "subnational"),
    (86, "Puerto Rico", "Caribbean", "PR", "PRI", 630, "United States", "territory"),
    (87, "Saba & Sint Eustatius", "Caribbean", None, "BES", None, "Netherlands", "territory"),
    (88, "St. Barth\u00e9lemy", "Caribbean", "BL", "BLM", 652, "France", "territory"),
    (89, "St. Kitts", "Caribbean", None, None, None, "Saint Kitts and Nevis", "subnational"),
    (90, "St. Lucia", "Caribbean", "LC", "LCA", 662, "Saint Lucia", "country"),
    (91, "St. Martin", "Caribbean", "MF", "MAF", 663, "France", "territory"),
    (
        92,
        "St. Vincent & the Grenadines",
        "Caribbean",
        "VC",
        "VCT",
        670,
        "Saint Vincent and the Grenadines",
        "country",
    ),
    (93, "San Andres & Providencia", "Caribbean", None, None, None, "Colombia", "subnational"),
    (94, "Sint Maarten", "Caribbean", "SX", "SXM", 534, "Netherlands", "territory"),
    (95, "Trinidad & Tobago", "Caribbean", "TT", "TTO", 780, "Trinidad and Tobago", "country"),
    (96, "Turks & Caicos Islands", "Caribbean", "TC", "TCA", 796, "United Kingdom", "territory"),
    (97, "Virgin Islands British", "Caribbean", "VG", "VGB", 92, "United Kingdom", "territory"),
    (98, "Virgin Islands U.S.", "Caribbean", "VI", "VIR", 850, "United States", "territory"),
    # === ATLANTIC OCEAN (99-112) ===
    (99, "Ascension", "Atlantic Ocean", None, None, None, "United Kingdom", "territory"),
    (100, "Azores Islands", "Atlantic Ocean", None, None, None, "Portugal", "subnational"),
    (101, "Bermuda", "Atlantic Ocean", "BM", "BMU", 60, "United Kingdom", "territory"),
    (102, "Canary Islands", "Atlantic Ocean", None, None, None, "Spain", "subnational"),
    (103, "Cape Verde Islands", "Atlantic Ocean", "CV", "CPV", 132, "Cape Verde", "country"),
    (104, "Falkland Islands", "Atlantic Ocean", "FK", "FLK", 238, "United Kingdom", "territory"),
    (105, "Faroe Islands", "Atlantic Ocean", "FO", "FRO", 234, "Denmark", "territory"),
    (106, "Fernando de Noronha", "Atlantic Ocean", None, None, None, "Brazil", "territory"),
    (107, "Greenland", "Atlantic Ocean", "GL", "GRL", 304, "Denmark", "territory"),
    (108, "Iceland", "Atlantic Ocean", "IS", "ISL", 352, "Iceland", "country"),
    (109, "Madeira", "Atlantic Ocean", None, None, None, "Portugal", "subnational"),
    (
        110,
        "South Georgia & the South Sandwich Islands",
        "Atlantic Ocean",
        "GS",
        "SGS",
        239,
        "United Kingdom",
        "territory",
    ),
    (111, "St. Helena", "Atlantic Ocean", None, None, None, "United Kingdom", "territory"),
    (112, "Tristan da Cunha", "Atlantic Ocean", None, None, None, "United Kingdom", "territory"),
    # === EUROPE & MEDITERRANEAN (113-180) ===
    (113, "Aland Islands", "Europe & Mediterranean", "AX", "ALA", 248, "Finland", "subnational"),
    (114, "Albania", "Europe & Mediterranean", "AL", "ALB", 8, "Albania", "country"),
    (115, "Andorra", "Europe & Mediterranean", "AD", "AND", 20, "Andorra", "country"),
    (116, "Austria", "Europe & Mediterranean", "AT", "AUT", 40, "Austria", "country"),
    (117, "Balearic Islands", "Europe & Mediterranean", None, None, None, "Spain", "subnational"),
    (118, "Belarus", "Europe & Mediterranean", "BY", "BLR", 112, "Belarus", "country"),
    (119, "Belgium", "Europe & Mediterranean", "BE", "BEL", 56, "Belgium", "country"),
    (
        120,
        "Bosnia & Herzegovina",
        "Europe & Mediterranean",
        "BA",
        "BIH",
        70,
        "Bosnia and Herzegovina",
        "country",
    ),
    (121, "Bulgaria", "Europe & Mediterranean", "BG", "BGR", 100, "Bulgaria", "country"),
    (122, "Corsica", "Europe & Mediterranean", None, None, None, "France", "subnational"),
    (123, "Crete", "Europe & Mediterranean", None, None, None, "Greece", "subnational"),
    (124, "Croatia", "Europe & Mediterranean", "HR", "HRV", 191, "Croatia", "country"),
    (
        125,
        "Cyprus British Sovereign Base Areas",
        "Europe & Mediterranean",
        None,
        None,
        None,
        "United Kingdom",
        "territory",
    ),
    (126, "Cyprus Republic", "Europe & Mediterranean", "CY", "CYP", 196, "Cyprus", "country"),
    (
        127,
        "Cyprus Turkish Fed. State",
        "Europe & Mediterranean",
        None,
        None,
        None,
        "Cyprus",
        "disputed",
    ),
    (
        128,
        "Czech Republic",
        "Europe & Mediterranean",
        "CZ",
        "CZE",
        203,
        "Czech Republic",
        "country",
    ),
    (129, "Denmark", "Europe & Mediterranean", "DK", "DNK", 208, "Denmark", "country"),
    (130, "England", "Europe & Mediterranean", None, None, None, "United Kingdom", "subnational"),
    (131, "Estonia", "Europe & Mediterranean", "EE", "EST", 233, "Estonia", "country"),
    (132, "Finland", "Europe & Mediterranean", "FI", "FIN", 246, "Finland", "country"),
    (133, "France", "Europe & Mediterranean", "FR", "FRA", 250, "France", "country"),
    (134, "Germany", "Europe & Mediterranean", "DE", "DEU", 276, "Germany", "country"),
    (135, "Gibraltar", "Europe & Mediterranean", "GI", "GIB", 292, "United Kingdom", "territory"),
    (136, "Greece", "Europe & Mediterranean", "GR", "GRC", 300, "Greece", "country"),
    (
        137,
        "Greek Aegean Islands",
        "Europe & Mediterranean",
        None,
        None,
        None,
        "Greece",
        "subnational",
    ),
    (
        138,
        "Guernsey & Dependencies",
        "Europe & Mediterranean",
        "GG",
        "GGY",
        831,
        "United Kingdom",
        "territory",
    ),
    (139, "Hungary", "Europe & Mediterranean", "HU", "HUN", 348, "Hungary", "country"),
    (140, "Ionian Islands", "Europe & Mediterranean", None, None, None, "Greece", "subnational"),
    (141, "Ireland", "Europe & Mediterranean", "IE", "IRL", 372, "Ireland", "country"),
    (
        142,
        "Ireland Northern",
        "Europe & Mediterranean",
        None,
        None,
        None,
        "United Kingdom",
        "subnational",
    ),
    (143, "Isle of Man", "Europe & Mediterranean", "IM", "IMN", 833, "United Kingdom", "territory"),
    (144, "Italy", "Europe & Mediterranean", "IT", "ITA", 380, "Italy", "country"),
    (145, "Jersey", "Europe & Mediterranean", "JE", "JEY", 832, "United Kingdom", "territory"),
    (146, "Kaliningrad", "Europe & Mediterranean", None, None, None, "Russia", "subnational"),
    (147, "Kosovo", "Europe & Mediterranean", "XK", "XKX", None, "Kosovo", "disputed"),
    (148, "Lampedusa", "Europe & Mediterranean", None, None, None, "Italy", "territory"),
    (149, "Latvia", "Europe & Mediterranean", "LV", "LVA", 428, "Latvia", "country"),
    (150, "Liechtenstein", "Europe & Mediterranean", "LI", "LIE", 438, "Liechtenstein", "country"),
    (151, "Lithuania", "Europe & Mediterranean", "LT", "LTU", 440, "Lithuania", "country"),
    (152, "Luxembourg", "Europe & Mediterranean", "LU", "LUX", 442, "Luxembourg", "country"),
    (153, "Malta", "Europe & Mediterranean", "MT", "MLT", 470, "Malta", "country"),
    (154, "Moldova", "Europe & Mediterranean", "MD", "MDA", 498, "Moldova", "country"),
    (155, "Monaco", "Europe & Mediterranean", "MC", "MCO", 492, "Monaco", "country"),
    (156, "Montenegro", "Europe & Mediterranean", "ME", "MNE", 499, "Montenegro", "country"),
    (157, "Netherlands", "Europe & Mediterranean", "NL", "NLD", 528, "Netherlands", "country"),
    (
        158,
        "North Macedonia",
        "Europe & Mediterranean",
        "MK",
        "MKD",
        807,
        "North Macedonia",
        "country",
    ),
    (159, "Norway", "Europe & Mediterranean", "NO", "NOR", 578, "Norway", "country"),
    (160, "Poland", "Europe & Mediterranean", "PL", "POL", 616, "Poland", "country"),
    (161, "Portugal", "Europe & Mediterranean", "PT", "PRT", 620, "Portugal", "country"),
    (162, "Romania", "Europe & Mediterranean", "RO", "ROU", 642, "Romania", "country"),
    (163, "Russia", "Europe & Mediterranean", "RU", "RUS", 643, "Russia", "country"),
    (164, "San Marino", "Europe & Mediterranean", "SM", "SMR", 674, "San Marino", "country"),
    (165, "Sardinia", "Europe & Mediterranean", None, None, None, "Italy", "subnational"),
    (166, "Scotland", "Europe & Mediterranean", None, None, None, "United Kingdom", "subnational"),
    (167, "Serbia", "Europe & Mediterranean", "RS", "SRB", 688, "Serbia", "country"),
    (168, "Sicily", "Europe & Mediterranean", None, None, None, "Italy", "subnational"),
    (169, "Slovakia", "Europe & Mediterranean", "SK", "SVK", 703, "Slovakia", "country"),
    (170, "Slovenia", "Europe & Mediterranean", "SI", "SVN", 705, "Slovenia", "country"),
    (171, "Spain", "Europe & Mediterranean", "ES", "ESP", 724, "Spain", "country"),
    (172, "Spitsbergen", "Europe & Mediterranean", None, "SJM", 744, "Norway", "territory"),
    (
        173,
        "Srpska",
        "Europe & Mediterranean",
        None,
        None,
        None,
        "Bosnia and Herzegovina",
        "subnational",
    ),
    (174, "Sweden", "Europe & Mediterranean", "SE", "SWE", 752, "Sweden", "country"),
    (175, "Switzerland", "Europe & Mediterranean", "CH", "CHE", 756, "Switzerland", "country"),
    (176, "Transnistria", "Europe & Mediterranean", None, None, None, "Moldova", "disputed"),
    (177, "Turkey in Europe", "Europe & Mediterranean", None, None, None, "Turkey", "subnational"),
    (178, "Ukraine", "Europe & Mediterranean", "UA", "UKR", 804, "Ukraine", "country"),
    (179, "Vatican City", "Europe & Mediterranean", "VA", "VAT", 336, "Vatican City", "country"),
    (180, "Wales", "Europe & Mediterranean", None, None, None, "United Kingdom", "subnational"),
    # === ANTARCTICA (181-187) ===
    (181, "Argentine Antarctica", "Antarctica", None, None, None, "Argentina", "antarctic"),
    (
        182,
        "Australian Antarctic Territory",
        "Antarctica",
        None,
        None,
        None,
        "Australia",
        "antarctic",
    ),
    (
        183,
        "British Antarctic Territory",
        "Antarctica",
        None,
        None,
        None,
        "United Kingdom",
        "antarctic",
    ),
    (184, "Chilean Antarctic Territory", "Antarctica", None, None, None, "Chile", "antarctic"),
    (185, "French Antarctica", "Antarctica", None, None, None, "France", "antarctic"),
    (186, "New Zealand Antarctica", "Antarctica", None, None, None, "New Zealand", "antarctic"),
    (187, "Norwegian Dependencies", "Antarctica", None, None, None, "Norway", "antarctic"),
    # === AFRICA (188-242) ===
    (188, "Algeria", "Africa", "DZ", "DZA", 12, "Algeria", "country"),
    (189, "Angola", "Africa", "AO", "AGO", 24, "Angola", "country"),
    (190, "Benin", "Africa", "BJ", "BEN", 204, "Benin", "country"),
    (191, "Botswana", "Africa", "BW", "BWA", 72, "Botswana", "country"),
    (192, "Burkina Faso", "Africa", "BF", "BFA", 854, "Burkina Faso", "country"),
    (193, "Burundi", "Africa", "BI", "BDI", 108, "Burundi", "country"),
    (194, "Cabinda", "Africa", None, None, None, "Angola", "subnational"),
    (195, "Cameroon", "Africa", "CM", "CMR", 120, "Cameroon", "country"),
    (
        196,
        "Central African Republic",
        "Africa",
        "CF",
        "CAF",
        140,
        "Central African Republic",
        "country",
    ),
    (197, "Chad", "Africa", "TD", "TCD", 148, "Chad", "country"),
    (
        198,
        "Congo Democratic Republic",
        "Africa",
        "CD",
        "COD",
        180,
        "Democratic Republic of the Congo",
        "country",
    ),
    (199, "Congo Republic", "Africa", "CG", "COG", 178, "Republic of the Congo", "country"),
    (200, "C\u00f4te d'Ivoire", "Africa", "CI", "CIV", 384, "C\u00f4te d'Ivoire", "country"),
    (201, "Djibouti", "Africa", "DJ", "DJI", 262, "Djibouti", "country"),
    (202, "Egypt in Africa", "Africa", "EG", "EGY", 818, "Egypt", "country"),
    (
        203,
        "Equatorial Guinea Bioko",
        "Africa",
        None,
        None,
        None,
        "Equatorial Guinea",
        "subnational",
    ),
    (
        204,
        "Equatorial Guinea Rio Muni",
        "Africa",
        None,
        None,
        None,
        "Equatorial Guinea",
        "subnational",
    ),
    (205, "Eritrea", "Africa", "ER", "ERI", 232, "Eritrea", "country"),
    (206, "Eswatini", "Africa", "SZ", "SWZ", 748, "Eswatini", "country"),
    (207, "Ethiopia", "Africa", "ET", "ETH", 231, "Ethiopia", "country"),
    (208, "Gabon", "Africa", "GA", "GAB", 266, "Gabon", "country"),
    (209, "Gambia", "Africa", "GM", "GMB", 270, "Gambia", "country"),
    (210, "Ghana", "Africa", "GH", "GHA", 288, "Ghana", "country"),
    (211, "Guinea", "Africa", "GN", "GIN", 324, "Guinea", "country"),
    (212, "Guinea-Bissau", "Africa", "GW", "GNB", 624, "Guinea-Bissau", "country"),
    (213, "Kenya", "Africa", "KE", "KEN", 404, "Kenya", "country"),
    (214, "Lesotho", "Africa", "LS", "LSO", 426, "Lesotho", "country"),
    (215, "Liberia", "Africa", "LR", "LBR", 430, "Liberia", "country"),
    (216, "Libya", "Africa", "LY", "LBY", 434, "Libya", "country"),
    (217, "Malawi", "Africa", "MW", "MWI", 454, "Malawi", "country"),
    (218, "Mali", "Africa", "ML", "MLI", 466, "Mali", "country"),
    (219, "Mauritania", "Africa", "MR", "MRT", 478, "Mauritania", "country"),
    (220, "Morocco", "Africa", "MA", "MAR", 504, "Morocco", "country"),
    (221, "Morocco Spanish", "Africa", None, None, None, "Spain", "territory"),
    (222, "Mozambique", "Africa", "MZ", "MOZ", 508, "Mozambique", "country"),
    (223, "Namibia", "Africa", "NA", "NAM", 516, "Namibia", "country"),
    (224, "Niger", "Africa", "NE", "NER", 562, "Niger", "country"),
    (225, "Nigeria", "Africa", "NG", "NGA", 566, "Nigeria", "country"),
    (226, "Rwanda", "Africa", "RW", "RWA", 646, "Rwanda", "country"),
    (227, "Sao Tome & Principe", "Africa", "ST", "STP", 678, "Sao Tome and Principe", "country"),
    (228, "Senegal", "Africa", "SN", "SEN", 686, "Senegal", "country"),
    (229, "Sierra Leone", "Africa", "SL", "SLE", 694, "Sierra Leone", "country"),
    (230, "Somalia", "Africa", "SO", "SOM", 706, "Somalia", "country"),
    (231, "Somaliland", "Africa", None, None, None, "Somalia", "disputed"),
    (232, "South Africa", "Africa", "ZA", "ZAF", 710, "South Africa", "country"),
    (233, "South Sudan", "Africa", "SS", "SSD", 728, "South Sudan", "country"),
    (234, "Sudan", "Africa", "SD", "SDN", 729, "Sudan", "country"),
    (235, "Tanzania", "Africa", "TZ", "TZA", 834, "Tanzania", "country"),
    (236, "Togo", "Africa", "TG", "TGO", 768, "Togo", "country"),
    (237, "Tunisia", "Africa", "TN", "TUN", 788, "Tunisia", "country"),
    (238, "Uganda", "Africa", "UG", "UGA", 800, "Uganda", "country"),
    (239, "Western Sahara", "Africa", "EH", "ESH", 732, "Western Sahara", "disputed"),
    (240, "Zambia", "Africa", "ZM", "ZMB", 894, "Zambia", "country"),
    (241, "Zanzibar", "Africa", None, None, None, "Tanzania", "subnational"),
    (242, "Zimbabwe", "Africa", "ZW", "ZWE", 716, "Zimbabwe", "country"),
    # === MIDDLE EAST (243-263) ===
    (243, "Abu Dhabi", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (244, "Ajman", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (245, "Bahrain", "Middle East", "BH", "BHR", 48, "Bahrain", "country"),
    (246, "Dubai", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (247, "Egypt in Asia", "Middle East", None, None, None, "Egypt", "subnational"),
    (248, "Fujairah", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (249, "Iran", "Middle East", "IR", "IRN", 364, "Iran", "country"),
    (250, "Iraq", "Middle East", "IQ", "IRQ", 368, "Iraq", "country"),
    (251, "Israel", "Middle East", "IL", "ISR", 376, "Israel", "country"),
    (252, "Jordan", "Middle East", "JO", "JOR", 400, "Jordan", "country"),
    (253, "Kuwait", "Middle East", "KW", "KWT", 414, "Kuwait", "country"),
    (254, "Lebanon", "Middle East", "LB", "LBN", 422, "Lebanon", "country"),
    (255, "Oman", "Middle East", "OM", "OMN", 512, "Oman", "country"),
    (256, "Palestine", "Middle East", "PS", "PSE", 275, "Palestine", "disputed"),
    (257, "Qatar", "Middle East", "QA", "QAT", 634, "Qatar", "country"),
    (258, "Ras Al Khaimah", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (259, "Saudi Arabia", "Middle East", "SA", "SAU", 682, "Saudi Arabia", "country"),
    (260, "Sharjah", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (261, "Syria", "Middle East", "SY", "SYR", 760, "Syria", "country"),
    (262, "Umm Al Qaiwain", "Middle East", None, None, None, "United Arab Emirates", "subnational"),
    (263, "Yemen", "Middle East", "YE", "YEM", 887, "Yemen", "country"),
    # === INDIAN OCEAN (264-278) ===
    (264, "Andaman-Nicobar Islands", "Indian Ocean", None, None, None, "India", "subnational"),
    (
        265,
        "British Indian Ocean Territory",
        "Indian Ocean",
        "IO",
        "IOT",
        86,
        "United Kingdom",
        "territory",
    ),
    (266, "Christmas Island", "Indian Ocean", "CX", "CXR", 162, "Australia", "territory"),
    (267, "Cocos Islands", "Indian Ocean", "CC", "CCK", 166, "Australia", "territory"),
    (268, "Comoros", "Indian Ocean", "KM", "COM", 174, "Comoros", "country"),
    (269, "Lakshadweep", "Indian Ocean", None, None, None, "India", "subnational"),
    (270, "Madagascar", "Indian Ocean", "MG", "MDG", 450, "Madagascar", "country"),
    (271, "Maldives", "Indian Ocean", "MV", "MDV", 462, "Maldives", "country"),
    (272, "Mauritius & Dependencies", "Indian Ocean", "MU", "MUS", 480, "Mauritius", "country"),
    (273, "Mayotte", "Indian Ocean", "YT", "MYT", 175, "France", "territory"),
    (274, "Reunion", "Indian Ocean", "RE", "REU", 638, "France", "territory"),
    (275, "Rodrigues Island", "Indian Ocean", None, None, None, "Mauritius", "territory"),
    (276, "Seychelles", "Indian Ocean", "SC", "SYC", 690, "Seychelles", "country"),
    (277, "Socotra", "Indian Ocean", None, None, None, "Yemen", "territory"),
    (278, "Zil Elwannyen Sesel", "Indian Ocean", None, None, None, "Seychelles", "territory"),
    # === ASIA (279-330) ===
    (279, "Abkhazia", "Asia", None, None, None, "Georgia", "disputed"),
    (280, "Afghanistan", "Asia", "AF", "AFG", 4, "Afghanistan", "country"),
    (281, "Armenia", "Asia", "AM", "ARM", 51, "Armenia", "country"),
    (282, "Azerbaijan", "Asia", "AZ", "AZE", 31, "Azerbaijan", "country"),
    (283, "Bangladesh", "Asia", "BD", "BGD", 50, "Bangladesh", "country"),
    (284, "Bhutan", "Asia", "BT", "BTN", 64, "Bhutan", "country"),
    (285, "Brunei", "Asia", "BN", "BRN", 96, "Brunei", "country"),
    (286, "Cambodia", "Asia", "KH", "KHM", 116, "Cambodia", "country"),
    (287, "China People's Republic", "Asia", "CN", "CHN", 156, "China", "country"),
    (288, "Georgia", "Asia", "GE", "GEO", 268, "Georgia", "country"),
    (289, "Hainan Island", "Asia", None, None, None, "China", "subnational"),
    (290, "Hong Kong", "Asia", "HK", "HKG", 344, "China", "territory"),
    (291, "India", "Asia", "IN", "IND", 356, "India", "country"),
    (292, "Indonesia Java", "Asia", None, None, None, "Indonesia", "subnational"),
    (293, "Japan", "Asia", "JP", "JPN", 392, "Japan", "country"),
    (294, "Jeju Island", "Asia", None, None, None, "South Korea", "subnational"),
    (295, "Kalimantan", "Asia", None, None, None, "Indonesia", "subnational"),
    (296, "Kashmir", "Asia", None, None, None, "Disputed", "disputed"),
    (297, "Kazakhstan", "Asia", "KZ", "KAZ", 398, "Kazakhstan", "country"),
    (298, "Korea North", "Asia", "KP", "PRK", 408, "North Korea", "country"),
    (299, "Korea South", "Asia", "KR", "KOR", 410, "South Korea", "country"),
    (300, "Kyrgyzstan", "Asia", "KG", "KGZ", 417, "Kyrgyzstan", "country"),
    (301, "Laos", "Asia", "LA", "LAO", 418, "Laos", "country"),
    (302, "Lesser Sunda Islands", "Asia", None, None, None, "Indonesia", "subnational"),
    (303, "Macau", "Asia", "MO", "MAC", 446, "China", "territory"),
    (304, "Malaysia", "Asia", "MY", "MYS", 458, "Malaysia", "country"),
    (305, "Maluku Islands", "Asia", None, None, None, "Indonesia", "subnational"),
    (306, "Mongolia", "Asia", "MN", "MNG", 496, "Mongolia", "country"),
    (307, "Myanmar", "Asia", "MM", "MMR", 104, "Myanmar", "country"),
    (308, "Nakhchivan", "Asia", None, None, None, "Azerbaijan", "subnational"),
    (309, "Nepal", "Asia", "NP", "NPL", 524, "Nepal", "country"),
    (310, "Pakistan", "Asia", "PK", "PAK", 586, "Pakistan", "country"),
    (311, "Papua", "Asia", None, None, None, "Indonesia", "subnational"),
    (312, "Philippines", "Asia", "PH", "PHL", 608, "Philippines", "country"),
    (313, "Russia in Asia", "Asia", None, None, None, "Russia", "subnational"),
    (314, "Sabah", "Asia", None, None, None, "Malaysia", "subnational"),
    (315, "Sarawak", "Asia", None, None, None, "Malaysia", "subnational"),
    (316, "Sikkim", "Asia", None, None, None, "India", "subnational"),
    (317, "Singapore", "Asia", "SG", "SGP", 702, "Singapore", "country"),
    (318, "South Ossetia", "Asia", None, None, None, "Georgia", "disputed"),
    (319, "Sri Lanka", "Asia", "LK", "LKA", 144, "Sri Lanka", "country"),
    (320, "Sulawesi", "Asia", None, None, None, "Indonesia", "subnational"),
    (321, "Sumatra", "Asia", None, None, None, "Indonesia", "subnational"),
    (322, "Taiwan", "Asia", "TW", "TWN", 158, "Taiwan", "country"),
    (323, "Tajikistan", "Asia", "TJ", "TJK", 762, "Tajikistan", "country"),
    (324, "Thailand", "Asia", "TH", "THA", 764, "Thailand", "country"),
    (325, "Tibet", "Asia", None, None, None, "China", "subnational"),
    (326, "Timor-Leste", "Asia", "TL", "TLS", 626, "Timor-Leste", "country"),
    (327, "Turkey in Asia", "Asia", None, None, None, "Turkey", "subnational"),
    (328, "Turkmenistan", "Asia", "TM", "TKM", 795, "Turkmenistan", "country"),
    (329, "Uzbekistan", "Asia", "UZ", "UZB", 860, "Uzbekistan", "country"),
    (330, "Vietnam", "Asia", "VN", "VNM", 704, "Vietnam", "country"),
]

# Extraction strategies. Destinations NOT listed here use the default "direct" strategy,
# which matches from NE admin_0_map_subunits/map_units by iso_a3 code.
#
# Strategy types:
# - "direct": (default) Match from admin_0 layers by iso_a3. No entry needed.
# - "subunit": Match from map_subunits by su_a3 code
# - "admin1": Select and dissolve admin_1 provinces by name
# - "remainder": admin_0 feature minus specified admin1 provinces
# - "group_remainder": admin_0 feature minus other TCC destinations' geometries
# - "clip": Clip country with Europe-Asia boundary line
# - "disputed": From NE breakaway_disputed_areas layer
# - "disputed_remainder": admin_0 minus disputed area polygons
# - "disputed_subtract": admin_0 minus specific disputed layer features
# - "island_bbox": Extract polygons within bbox from parent MultiPolygon
# - "antarctic": Generate sector wedge from South Pole to 60°S
# - "point": Point marker for tiny islands

EXTRACTIONS: dict[int, dict[str, Any]] = {
    # =========================================================================
    # PACIFIC OCEAN
    # =========================================================================
    # 1 - Austral Islands: extract from French Polynesia by bbox
    1: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "PYF",
        "bbox": [-155, -28, -144, -20],
    },
    # 2 - Australia: mainland minus Tasmania (admin1 subtracted)
    2: {
        "strategy": "remainder",
        "adm0_a3": "AUS",
        "subtract_admin1": ["Tasmania"],
    },
    # 3 - Chatham Islands: extract from NZ by bbox
    3: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "NZL",
        "bbox": [-177.5, -45, -175, -43],
    },
    # 4 - Cook Islands: direct (COK)
    # 5 - Easter Island: extract from Chile by bbox
    5: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "CHL",
        "bbox": [-110, -28, -108, -26],
    },
    # 6 - Fiji: direct (FJI)
    # 7 - French Polynesia: PYF minus Austral and Marquesas
    7: {
        "strategy": "group_remainder",
        "adm0_a3": "PYF",
        "subtract_indices": [1, 15],
    },
    # 8 - Galapagos Islands: admin1 from Ecuador
    8: {
        "strategy": "admin1",
        "adm0_a3": "ECU",
        "admin1": ["Gal\u00e1pagos"],
    },
    # 9 - Guam: direct (GUM)
    # 10 - Hawaiian Islands: admin1 from USA
    10: {
        "strategy": "admin1",
        "adm0_a3": "USA",
        "admin1": ["Hawaii"],
    },
    # 11 - Juan Fernandez Islands: extract from Chile by bbox
    11: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "CHL",
        "bbox": [-81, -35, -78, -32],
    },
    # 12 - Kiribati: KIR minus Line/Phoenix Islands
    12: {
        "strategy": "group_remainder",
        "adm0_a3": "KIR",
        "subtract_indices": [13],
    },
    # 13 - Line/Phoenix Islands: extract from Kiribati by bbox
    13: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "KIR",
        "bbox": [-175, -15, -148, 7],
    },
    # 14 - Lord Howe Island: extract from Australia by bbox
    14: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "AUS",
        "bbox": [158, -32.5, 160, -31],
    },
    # 15 - Marquesas Islands: extract from French Polynesia by bbox
    15: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "PYF",
        "bbox": [-141, -12, -138, -7],
    },
    # 16 - Marshall Islands: direct (MHL)
    # 17 - Micronesia: direct (FSM)
    # 18 - Midway Island: subunit (MQI)
    18: {
        "strategy": "subunit",
        "su_a3": "MQI",
    },
    # 19 - Nauru: direct (NRU)
    # 20 - New Caledonia: direct (NCL)
    # 21 - New Zealand: NZL minus Chatham Islands
    21: {
        "strategy": "group_remainder",
        "adm0_a3": "NZL",
        "subtract_indices": [3],
    },
    # 22 - Niue: direct (NIU)
    # 23 - Norfolk Island: direct (NFK)
    # 24 - Northern Marianas: direct (MNP)
    # 25 - Ogasawara: extract from Japan by bbox
    25: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "JPN",
        "bbox": [141, 24, 143, 28],
    },
    # 26 - Palau: direct (PLW)
    # 27 - Papua New Guinea: PNG minus Islands Region
    27: {
        "strategy": "group_remainder",
        "adm0_a3": "PNG",
        "subtract_indices": [28],
    },
    # 28 - Papua New Guinea Islands Region: extract from PNG by bbox
    28: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "PNG",
        "bbox": [147, -8, 160, -1],
    },
    # 29 - Pitcairn Island: direct (PCN)
    # 30 - Ryukyu Islands (Okinawa): admin1 from Japan
    30: {
        "strategy": "admin1",
        "adm0_a3": "JPN",
        "admin1": ["Okinawa"],
    },
    # 31 - Samoa American: direct (ASM)
    # 32 - Samoa: direct (WSM)
    # 33 - Solomon Islands: direct (SLB)
    # 34 - Tasmania: admin1 from Australia
    34: {
        "strategy": "admin1",
        "adm0_a3": "AUS",
        "admin1": ["Tasmania"],
    },
    # 35 - Tokelau Islands: direct (TKL)
    # 36 - Tonga: direct (TON)
    # 37 - Tuvalu: direct (TUV)
    # 38 - Vanuatu: direct (VUT)
    # 39 - Wake Island: subunit (WQI)
    39: {
        "strategy": "subunit",
        "su_a3": "WQI",
    },
    # 40 - Wallis & Futuna: direct (WLF)
    # =========================================================================
    # NORTH AMERICA
    # =========================================================================
    # 41 - Alaska: admin1 from USA
    41: {
        "strategy": "admin1",
        "adm0_a3": "USA",
        "admin1": ["Alaska"],
    },
    # 42 - Canada: CAN minus Prince Edward Island
    42: {
        "strategy": "remainder",
        "adm0_a3": "CAN",
        "subtract_admin1": ["Prince Edward Island"],
    },
    # 43 - Mexico: direct (MEX)
    # 44 - Prince Edward Island: admin1 from Canada
    44: {
        "strategy": "admin1",
        "adm0_a3": "CAN",
        "admin1": ["Prince Edward Island"],
    },
    # 45 - St. Pierre & Miquelon: direct (SPM)
    # 46 - United States (Contiguous): USA minus Alaska and Hawaii
    46: {
        "strategy": "remainder",
        "adm0_a3": "USA",
        "subtract_admin1": ["Alaska", "Hawaii"],
    },
    # =========================================================================
    # CENTRAL AMERICA (47-53): all direct
    # =========================================================================
    # =========================================================================
    # SOUTH AMERICA
    # =========================================================================
    # 54 - Argentina: direct (ARG)
    # 55 - Bolivia: direct (BOL)
    # 56 - Brazil: BRA minus Fernando de Noronha
    56: {
        "strategy": "group_remainder",
        "adm0_a3": "BRA",
        "subtract_indices": [106],
    },
    # 57 - Chile: CHL minus Easter Island and Juan Fernandez
    57: {
        "strategy": "group_remainder",
        "adm0_a3": "CHL",
        "subtract_indices": [5, 11],
    },
    # 58 - Colombia: COL minus San Andres & Providencia
    58: {
        "strategy": "remainder",
        "adm0_a3": "COL",
        "subtract_admin1": ["San Andr\u00e9s y Providencia"],
    },
    # 59 - Ecuador: ECU minus Galapagos
    59: {
        "strategy": "remainder",
        "adm0_a3": "ECU",
        "subtract_admin1": ["Gal\u00e1pagos"],
    },
    # 60 - French Guiana: direct (GUF)
    # 61 - Guyana: direct (GUY)
    # 62 - Nueva Esparta: admin1 from Venezuela
    62: {
        "strategy": "admin1",
        "adm0_a3": "VEN",
        "admin1": ["Nueva Esparta"],
    },
    # 63 - Paraguay: direct (PRY)
    # 64 - Peru: direct (PER)
    # 65 - Suriname: direct (SUR)
    # 66 - Uruguay: direct (URY)
    # 67 - Venezuela: VEN minus Nueva Esparta
    67: {
        "strategy": "remainder",
        "adm0_a3": "VEN",
        "subtract_admin1": ["Nueva Esparta"],
    },
    # =========================================================================
    # CARIBBEAN
    # =========================================================================
    # 68 - Anguilla: direct (AIA)
    # 69 - Antigua & Barbuda: direct (ATG)
    # 70 - Aruba: direct (ABW)
    # 71 - Bahamas: direct (BHS)
    # 72 - Barbados: direct (BRB)
    # 73 - Bonaire: admin1 from Netherlands
    73: {
        "strategy": "admin1",
        "adm0_a3": "NLD",
        "admin1": ["Bonaire"],
    },
    # 74 - Cayman Islands: direct (CYM)
    # 75 - Cuba: direct (CUB)
    # 76 - Curacao: direct (CUW)
    # 77 - Dominica: direct (DMA)
    # 78 - Dominican Republic: direct (DOM)
    # 79 - Grenada: direct (GRD)
    # 80 - Guadeloupe: direct (GLP)
    # 81 - Haiti: direct (HTI)
    # 82 - Jamaica: direct (JAM)
    # 83 - Martinique: direct (MTQ)
    # 84 - Montserrat: direct (MSR)
    # 85 - Nevis: extract from KNA by bbox
    85: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "KNA",
        "bbox": [-62.7, 17.05, -62.4, 17.25],
    },
    # 86 - Puerto Rico: direct (PRI)
    # 87 - Saba & Sint Eustatius: admin1 from Netherlands
    87: {
        "strategy": "admin1",
        "adm0_a3": "NLD",
        "admin1": ["Saba", "St. Eustatius"],
    },
    # 88 - St. Barthelemy: direct (BLM)
    # 89 - St. Kitts: extract from KNA by bbox
    89: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "KNA",
        "bbox": [-62.9, 17.2, -62.5, 17.45],
    },
    # 90 - St. Lucia: direct (LCA)
    # 91 - St. Martin: direct (MAF)
    # 92 - St. Vincent & the Grenadines: direct (VCT)
    # 93 - San Andres & Providencia: admin1 from Colombia
    93: {
        "strategy": "admin1",
        "adm0_a3": "COL",
        "admin1": ["San Andr\u00e9s y Providencia"],
    },
    # 94 - Sint Maarten: direct (SXM)
    # 95 - Trinidad & Tobago: direct (TTO)
    # 96 - Turks & Caicos: direct (TCA)
    # 97 - Virgin Islands British: direct (VGB)
    # 98 - Virgin Islands U.S.: direct (VIR)
    # =========================================================================
    # ATLANTIC OCEAN
    # =========================================================================
    # 99 - Ascension: extract from SHN by bbox
    99: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "SHN",
        "bbox": [-15, -8.5, -14, -7],
    },
    # 100 - Azores Islands: admin1 from Portugal
    100: {
        "strategy": "admin1",
        "adm0_a3": "PRT",
        "admin1": ["Azores"],
    },
    # 101 - Bermuda: direct (BMU)
    # 102 - Canary Islands: admin1 from Spain
    102: {
        "strategy": "admin1",
        "adm0_a3": "ESP",
        "admin1": ["Las Palmas", "Santa Cruz de Tenerife"],
    },
    # 103 - Cape Verde: direct (CPV)
    # 104 - Falkland Islands: direct (FLK)
    # 105 - Faroe Islands: direct (FRO)
    # 106 - Fernando de Noronha: extract from Brazil by bbox
    106: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "BRA",
        "bbox": [-33, -4.5, -32, -3],
    },
    # 107 - Greenland: direct (GRL)
    # 108 - Iceland: direct (ISL)
    # 109 - Madeira: admin1 from Portugal
    109: {
        "strategy": "admin1",
        "adm0_a3": "PRT",
        "admin1": ["Madeira"],
    },
    # 110 - South Georgia & South Sandwich Islands: direct (SGS)
    # 111 - St. Helena: extract from SHN by bbox
    111: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "SHN",
        "bbox": [-6.5, -16.5, -5, -15],
    },
    # 112 - Tristan da Cunha: extract from SHN by bbox
    112: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "SHN",
        "bbox": [-13, -38, -12, -36.5],
    },
    # =========================================================================
    # EUROPE & MEDITERRANEAN
    # =========================================================================
    # 113 - Aland Islands: separate entity in NE (ADM0_A3=ALD)
    113: {
        "strategy": "direct",
        "adm0_a3": "ALD",
    },
    # 114 - Albania: direct (ALB)
    # 115 - Andorra: direct (AND)
    # 116 - Austria: direct (AUT)
    # 117 - Balearic Islands: admin1 from Spain
    117: {
        "strategy": "admin1",
        "adm0_a3": "ESP",
        "admin1": ["Baleares"],
    },
    # 118 - Belarus: direct (BLR)
    # 119 - Belgium: direct (BEL)
    # 120 - Bosnia & Herzegovina: BIH minus Srpska
    120: {
        "strategy": "group_remainder",
        "adm0_a3": "BIH",
        "subtract_indices": [173],
    },
    # 121 - Bulgaria: direct (BGR)
    # 122 - Corsica: subunit from map_subunits
    122: {
        "strategy": "subunit",
        "su_a3": "FXC",
    },
    # 123 - Crete: admin1 from Greece
    123: {
        "strategy": "admin1",
        "adm0_a3": "GRC",
        "admin1": ["Kriti"],
    },
    # 124 - Croatia: direct (HRV)
    # 125 - Cyprus British Sovereign Base Areas: direct by name/code
    125: {
        "strategy": "direct",
        "adm0_a3": "WSB",
    },
    # 126 - Cyprus Republic: CYP minus N. Cyprus disputed area
    126: {
        "strategy": "disputed_subtract",
        "adm0_a3": "CYP",
        "subtract_disputed": ["N. Cyprus"],
    },
    # 127 - Cyprus Turkish Fed. State: from disputed layer
    127: {
        "strategy": "disputed",
        "name": "N. Cyprus",
    },
    # 128 - Czech Republic: direct (CZE)
    # 129 - Denmark: direct (DNK)
    # 130 - England: subunit from map_subunits
    130: {
        "strategy": "subunit",
        "su_a3": "ENG",
    },
    # 131 - Estonia: direct (EST)
    # 132 - Finland: direct (Aland is already separate in NE)
    # No extraction needed — default direct strategy with iso_a3=FIN
    # 133 - France: subunit (metro France, excluding Corsica)
    133: {
        "strategy": "subunit",
        "su_a3": "FXM",
    },
    # 134 - Germany: direct (DEU)
    # 135 - Gibraltar: direct (GIB)
    # 136 - Greece: GRC minus Crete, Ionian, Aegean islands
    136: {
        "strategy": "remainder",
        "adm0_a3": "GRC",
        "subtract_admin1": ["Kriti", "Ionioi Nisoi", "Voreio Aigaio", "Notio Aigaio"],
    },
    # 137 - Greek Aegean Islands: admin1 merge
    137: {
        "strategy": "admin1",
        "adm0_a3": "GRC",
        "admin1": ["Voreio Aigaio", "Notio Aigaio"],
    },
    # 138 - Guernsey & Dependencies: direct (GGY)
    # 139 - Hungary: direct (HUN)
    # 140 - Ionian Islands: admin1 from Greece
    140: {
        "strategy": "admin1",
        "adm0_a3": "GRC",
        "admin1": ["Ionioi Nisoi"],
    },
    # 141 - Ireland: direct (IRL)
    # 142 - Ireland Northern: subunit from map_subunits
    142: {
        "strategy": "subunit",
        "su_a3": "NIR",
    },
    # 143 - Isle of Man: direct (IMN)
    # 144 - Italy: ITA minus Sardinia and Sicily provinces
    144: {
        "strategy": "remainder",
        "adm0_a3": "ITA",
        "subtract_admin1": [
            "Cagliari",
            "Carbonia-Iglesias",
            "Medio Campidano",
            "Nuoro",
            "Ogliastra",
            "Olbia-Tempio",
            "Oristrano",
            "Sassari",
            "Agrigento",
            "Caltanissetta",
            "Catania",
            "Enna",
            "Messina",
            "Palermo",
            "Ragusa",
            "Siracusa",
            "Trapani",
        ],
    },
    # 145 - Jersey: direct (JEY)
    # 146 - Kaliningrad: admin1 from Russia
    146: {
        "strategy": "admin1",
        "adm0_a3": "RUS",
        "admin1": ["Kaliningrad"],
    },
    # 147 - Kosovo: direct (XKX in admin_0)
    147: {
        "strategy": "direct",
        "adm0_a3": "KOS",
    },
    # 148 - Lampedusa: extract from Agrigento province by bbox
    148: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "ITA",
        "parent_admin1": "Agrigento",
        "bbox": [12, 35, 13, 36],
    },
    # 149 - Latvia: direct (LVA)
    # 150 - Liechtenstein: direct (LIE)
    # 151 - Lithuania: direct (LTU)
    # 152 - Luxembourg: direct (LUX)
    # 153 - Malta: direct (MLT)
    # 154 - Moldova: MDA minus Transnistria
    154: {
        "strategy": "disputed_remainder",
        "adm0_a3": "MDA",
        "subtract_disputed": ["Transnistria"],
    },
    # 155 - Monaco: direct (MCO)
    # 156 - Montenegro: direct (MNE)
    # 157 - Netherlands: direct (NLD)
    # 158 - North Macedonia: direct (MKD)
    # 159 - Norway: direct (NOR)
    # 160 - Poland: direct (POL)
    # 161 - Portugal: PRT minus Madeira and Azores
    161: {
        "strategy": "remainder",
        "adm0_a3": "PRT",
        "subtract_admin1": ["Madeira", "Azores"],
    },
    # 162 - Romania: direct (ROU)
    # 163 - Russia (European part): clip with Europe-Asia boundary, minus Kaliningrad & Crimea
    163: {
        "strategy": "clip",
        "adm0_a3": "RUS",
        "side": "europe",
        "absorb_lon_range": [30, 59],
        "subtract_indices": [146],
        "subtract_su_a3": ["RUC"],
    },
    # 164 - San Marino: direct (SMR)
    # 165 - Sardinia: admin1 merge of Sardinia provinces
    165: {
        "strategy": "admin1",
        "adm0_a3": "ITA",
        "admin1": [
            "Cagliari",
            "Carbonia-Iglesias",
            "Medio Campidano",
            "Nuoro",
            "Ogliastra",
            "Olbia-Tempio",
            "Oristrano",
            "Sassari",
        ],
    },
    # 166 - Scotland: subunit from map_subunits
    166: {
        "strategy": "subunit",
        "su_a3": "SCT",
    },
    # 167 - Serbia: direct (SRB)
    # 168 - Sicily: admin1 merge of Sicily provinces
    168: {
        "strategy": "admin1",
        "adm0_a3": "ITA",
        "admin1": [
            "Agrigento",
            "Caltanissetta",
            "Catania",
            "Enna",
            "Messina",
            "Palermo",
            "Ragusa",
            "Siracusa",
            "Trapani",
        ],
    },
    # 169 - Slovakia: direct (SVK)
    # 170 - Slovenia: direct (SVN)
    # 171 - Spain: ESP minus Balearic, Canary, Ceuta, Melilla
    171: {
        "strategy": "remainder",
        "adm0_a3": "ESP",
        "subtract_admin1": ["Baleares", "Las Palmas", "Santa Cruz de Tenerife", "Ceuta", "Melilla"],
    },
    # 172 - Spitsbergen (Svalbard): direct from NE map_units
    172: {
        "strategy": "direct",
        "adm0_a3": "SJM",
    },
    # 173 - Srpska: subunit from map_subunits (SU_A3=BIS)
    173: {
        "strategy": "subunit",
        "su_a3": "BIS",
    },
    # 174 - Sweden: direct (SWE)
    # 175 - Switzerland: direct (CHE)
    # 176 - Transnistria: from disputed layer
    176: {
        "strategy": "disputed",
        "ne_name": "Transnistria",
    },
    # 177 - Turkey in Europe: clip with Europe-Asia boundary
    177: {
        "strategy": "clip",
        "adm0_a3": "TUR",
        "side": "europe",
    },
    # 178 - Ukraine: UKR + Crimea (RUC subunit)
    178: {
        "strategy": "direct",
        "adm0_a3": "UKR",
        "merge_a3": ["RUC"],
    },
    # 179 - Vatican City: direct (VAT)
    # 180 - Wales: subunit from map_subunits
    180: {
        "strategy": "subunit",
        "su_a3": "WLS",
    },
    # =========================================================================
    # ANTARCTICA
    # =========================================================================
    # 181 - Argentine Antarctica: non-overlapping sector
    181: {
        "strategy": "antarctic",
        "lon_west": -53,
        "lon_east": -25,
    },
    # 182 - Australian Antarctic Territory: two sectors
    182: {
        "strategy": "antarctic",
        "sectors": [
            {"lon_west": 44.63, "lon_east": 136},
            {"lon_west": 142, "lon_east": 160},
        ],
    },
    # 183 - British Antarctic Territory: non-overlapping sector
    183: {
        "strategy": "antarctic",
        "lon_west": -25,
        "lon_east": -20,
    },
    # 184 - Chilean Antarctic Territory: non-overlapping sector
    184: {
        "strategy": "antarctic",
        "lon_west": -90,
        "lon_east": -53,
    },
    # 185 - French Antarctica (Adelie Land): sector wedge
    185: {
        "strategy": "antarctic",
        "lon_west": 136,
        "lon_east": 142,
    },
    # 186 - New Zealand Antarctica (Ross Dependency): crosses date line
    186: {
        "strategy": "antarctic",
        "lon_west": 160,
        "lon_east": -150,
    },
    # 187 - Norwegian Dependencies (Queen Maud Land + Bouvet + Peter I)
    187: {
        "strategy": "antarctic",
        "lon_west": -20,
        "lon_east": 44.63,
        "extra_points": [
            {"name": "Bouvet Island", "lat": -54.43, "lon": 3.38},
            {"name": "Peter I Island", "lat": -68.78, "lon": -90.58},
        ],
    },
    # =========================================================================
    # AFRICA
    # =========================================================================
    # 188 - Algeria: direct (DZA)
    # 189 - Angola: AGO minus Cabinda
    189: {
        "strategy": "remainder",
        "adm0_a3": "AGO",
        "subtract_admin1": ["Cabinda"],
    },
    # 190 - Benin: direct (BEN)
    # 191 - Botswana: direct (BWA)
    # 192 - Burkina Faso: direct (BFA)
    # 193 - Burundi: direct (BDI)
    # 194 - Cabinda: admin1 from Angola
    194: {
        "strategy": "admin1",
        "adm0_a3": "AGO",
        "admin1": ["Cabinda"],
    },
    # 195 - Cameroon: direct (CMR)
    # 196 - Central African Republic: direct (CAF)
    # 197 - Chad: direct (TCD)
    # 198 - Congo DR: direct (COD)
    # 199 - Congo Republic: direct (COG)
    # 200 - Cote d'Ivoire: direct (CIV)
    # 201 - Djibouti: direct (DJI)
    # 202 - Egypt in Africa: EGY minus Sinai governorates, plus Bir Tawil
    202: {
        "strategy": "remainder",
        "adm0_a3": "EGY",
        "subtract_admin1": ["North Sinai", "South Sinai"],
        "merge_disputed": ["Bir Tawil"],
    },
    # 203 - Equatorial Guinea Bioko: admin1
    203: {
        "strategy": "admin1",
        "adm0_a3": "GNQ",
        "admin1": ["Bioko Norte", "Bioko Sur"],
    },
    # 204 - Equatorial Guinea Rio Muni: admin1 (mainland)
    204: {
        "strategy": "admin1",
        "adm0_a3": "GNQ",
        "admin1": ["Centro Sur", "Kié-Ntem", "Litoral", "Wele-Nzas"],
    },
    # 205 - Eritrea: direct (ERI)
    # 206 - Eswatini: direct (SWZ)
    # 207 - Ethiopia: direct (ETH)
    # 208 - Gabon: direct (GAB)
    # 209 - Gambia: direct (GMB)
    # 210 - Ghana: direct (GHA)
    # 211 - Guinea: direct (GIN)
    # 212 - Guinea-Bissau: direct (GNB)
    # 213 - Kenya: direct (KEN)
    # 214 - Lesotho: direct (LSO)
    # 215 - Liberia: direct (LBR)
    # 216 - Libya: direct (LBY)
    # 217 - Malawi: direct (MWI)
    # 218 - Mali: direct (MLI)
    # 219 - Mauritania: direct (MRT)
    # 220 - Morocco: direct (MAR)
    # 221 - Morocco Spanish (Ceuta & Melilla): admin1 from Spain
    221: {
        "strategy": "admin1",
        "adm0_a3": "ESP",
        "admin1": ["Ceuta", "Melilla"],
    },
    # 222 - Mozambique: direct (MOZ)
    # 223 - Namibia: direct (NAM)
    # 224 - Niger: direct (NER)
    # 225 - Nigeria: direct (NGA)
    # 226 - Rwanda: direct (RWA)
    # 227 - Sao Tome & Principe: direct (STP)
    # 228 - Senegal: direct (SEN)
    # 229 - Sierra Leone: direct (SLE)
    # 230 - Somalia: SOM minus Somaliland
    230: {
        "strategy": "disputed_remainder",
        "adm0_a3": "SOM",
        "subtract_disputed": ["Somaliland"],
    },
    # 231 - Somaliland: from disputed layer
    231: {
        "strategy": "disputed",
        "name": "Somaliland",
    },
    # 232 - South Africa: direct (ZAF)
    # 233 - South Sudan: direct (SSD)
    # 234 - Sudan: direct (SDN)
    # 235 - Tanzania: TZA minus Zanzibar
    235: {
        "strategy": "remainder",
        "adm0_a3": "TZA",
        "subtract_admin1": [
            "Zanzibar North",
            "Zanzibar South and Central",
            "Zanzibar West",
            "Zanzibar Urban/West",
        ],
        "subtract_admin1_match": "Zanzibar",
    },
    # 236 - Togo: direct (TGO)
    # 237 - Tunisia: direct (TUN)
    # 238 - Uganda: direct (UGA)
    # 239 - Western Sahara: direct (ESH)
    # 240 - Zambia: direct (ZMB)
    # 241 - Zanzibar: admin1 from Tanzania
    241: {
        "strategy": "admin1",
        "adm0_a3": "TZA",
        "admin1": [
            "Zanzibar North",
            "Zanzibar South and Central",
            "Zanzibar West",
            "Zanzibar Urban/West",
        ],
        "admin1_match": "Zanzibar",
    },
    # 242 - Zimbabwe: direct (ZWE)
    # =========================================================================
    # MIDDLE EAST
    # =========================================================================
    # 243 - Abu Dhabi: admin1 from UAE
    243: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Abu Dhabi"],
    },
    # 244 - Ajman: admin1 from UAE
    244: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Ajman"],
    },
    # 245 - Bahrain: direct (BHR)
    # 246 - Dubai: admin1 from UAE
    246: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Dubay"],
    },
    # 247 - Egypt in Asia (Sinai): admin1 from Egypt
    247: {
        "strategy": "admin1",
        "adm0_a3": "EGY",
        "admin1": ["North Sinai", "South Sinai"],
    },
    # 248 - Fujairah: admin1 from UAE
    248: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Fujayrah"],
    },
    # 249 - Iran: direct (IRN)
    # 250 - Iraq: direct (IRQ)
    # 251 - Israel: direct (ISR)
    # 252 - Jordan: direct (JOR)
    # 253 - Kuwait: direct (KWT)
    # 254 - Lebanon: direct (LBN)
    # 255 - Oman: direct (OMN)
    # 256 - Palestine: NE uses ADM0_A3=PSX
    256: {
        "strategy": "direct",
        "adm0_a3": "PSX",
    },
    # 257 - Qatar: direct (QAT)
    # 258 - Ras Al Khaimah: admin1 from UAE
    258: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Ras Al Khaymah"],
    },
    # 259 - Saudi Arabia: direct (SAU)
    # 260 - Sharjah: admin1 from UAE
    260: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Sharjah"],
    },
    # 261 - Syria: direct (SYR)
    # 262 - Umm Al Qaiwain: admin1 from UAE
    262: {
        "strategy": "admin1",
        "adm0_a3": "ARE",
        "admin1": ["Umm Al Qaywayn"],
    },
    # 263 - Yemen: YEM minus Socotra
    263: {
        "strategy": "group_remainder",
        "adm0_a3": "YEM",
        "subtract_indices": [277],
    },
    # =========================================================================
    # INDIAN OCEAN
    # =========================================================================
    # 264 - Andaman-Nicobar Islands: admin1 from India
    264: {
        "strategy": "admin1",
        "adm0_a3": "IND",
        "admin1": ["Andaman and Nicobar"],
    },
    # 265 - British Indian Ocean Territory: direct (IOT)
    # 266 - Christmas Island: direct (CXR)
    # 267 - Cocos Islands: direct (CCK)
    # 268 - Comoros: direct (COM)
    # 269 - Lakshadweep: admin1 from India
    269: {
        "strategy": "admin1",
        "adm0_a3": "IND",
        "admin1": ["Lakshadweep"],
    },
    # 270 - Madagascar: direct (MDG)
    # 271 - Maldives: direct (MDV)
    # 272 - Mauritius & Dependencies: MUS minus Rodrigues
    272: {
        "strategy": "group_remainder",
        "adm0_a3": "MUS",
        "subtract_indices": [275],
    },
    # 273 - Mayotte: direct (MYT)
    # 274 - Reunion: direct (REU)
    # 275 - Rodrigues Island: extract from Mauritius by bbox
    275: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "MUS",
        "bbox": [63, -20.5, 64, -19],
    },
    # 276 - Seychelles: SYC minus Zil Elwannyen Sesel (outer islands)
    276: {
        "strategy": "group_remainder",
        "adm0_a3": "SYC",
        "subtract_indices": [278],
    },
    # 277 - Socotra: extract from Yemen by bbox
    277: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "YEM",
        "bbox": [52, 11, 55, 13],
    },
    # 278 - Zil Elwannyen Sesel: extract outer Seychelles islands by bbox
    278: {
        "strategy": "island_bbox",
        "parent_adm0_a3": "SYC",
        "bbox": [52, -10, 57, -3],
    },
    # =========================================================================
    # ASIA
    # =========================================================================
    # 279 - Abkhazia: from disputed layer
    279: {
        "strategy": "disputed",
        "name": "Abkhazia",
    },
    # 280 - Afghanistan: direct (AFG)
    # 281 - Armenia: direct (ARM)
    # 282 - Azerbaijan: AZE minus Nakhchivan
    282: {
        "strategy": "remainder",
        "adm0_a3": "AZE",
        "subtract_admin1": ["Nax\u00e7\u0131van"],
    },
    # 283 - Bangladesh: direct (BGD)
    # 284 - Bhutan: direct (BTN)
    # 285 - Brunei: direct (BRN)
    # 286 - Cambodia: direct (KHM)
    # 287 - China: CHN minus Hainan and Tibet
    287: {
        "strategy": "remainder",
        "adm0_a3": "CHN",
        "subtract_admin1": ["Hainan", "Xizang"],
    },
    # 288 - Georgia: GEO minus Abkhazia and South Ossetia
    288: {
        "strategy": "disputed_remainder",
        "adm0_a3": "GEO",
        "subtract_disputed": ["Abkhazia", "South Ossetia"],
    },
    # 289 - Hainan Island: admin1 from China
    289: {
        "strategy": "admin1",
        "adm0_a3": "CHN",
        "admin1": ["Hainan"],
    },
    # 290 - Hong Kong: direct (HKG)
    # 291 - India: IND minus Sikkim, Andaman-Nicobar, Lakshadweep, Kashmir
    291: {
        "strategy": "remainder",
        "adm0_a3": "IND",
        "subtract_admin1": ["Sikkim", "Andaman and Nicobar", "Lakshadweep"],
        "subtract_disputed": ["Kashmir"],
    },
    # 292 - Indonesia Java: admin1 merge
    292: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": [
            "Jakarta Raya",
            "Banten",
            "Jawa Barat",
            "Jawa Tengah",
            "Jawa Timur",
            "Yogyakarta",
        ],
    },
    # 293 - Japan: JPN minus Okinawa (and Ogasawara extracted separately)
    293: {
        "strategy": "remainder",
        "adm0_a3": "JPN",
        "subtract_admin1": ["Okinawa"],
    },
    # 294 - Jeju Island: admin1 from South Korea
    294: {
        "strategy": "admin1",
        "adm0_a3": "KOR",
        "admin1": ["Jeju"],
    },
    # 295 - Kalimantan: admin1 merge from Indonesia
    295: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": [
            "Kalimantan Barat",
            "Kalimantan Selatan",
            "Kalimantan Tengah",
            "Kalimantan Timur",
            "Kalimantan Utara",
        ],
    },
    # 296 - Kashmir: from disputed layer, plus Siachen Glacier
    296: {
        "strategy": "disputed",
        "name": "Kashmir",
        "also_merge": ["Siachen Glacier"],
    },
    # 297 - Kazakhstan: KAZ + KAB (Baikonur Cosmodrome lease area)
    297: {
        "strategy": "direct",
        "adm0_a3": "KAZ",
        "merge_a3": ["KAB"],
    },
    # 298 - Korea North: direct (PRK)
    # 299 - Korea South: KOR minus Jeju
    299: {
        "strategy": "remainder",
        "adm0_a3": "KOR",
        "subtract_admin1": ["Jeju"],
    },
    # 300 - Kyrgyzstan: direct (KGZ)
    # 301 - Laos: direct (LAO)
    # 302 - Lesser Sunda Islands: admin1 merge from Indonesia
    302: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
    },
    # 303 - Macau: direct (MAC)
    # 304 - Malaysia: MYS minus Sabah and Sarawak
    304: {
        "strategy": "remainder",
        "adm0_a3": "MYS",
        "subtract_admin1": ["Sabah", "Sarawak"],
    },
    # 305 - Maluku Islands: admin1 merge from Indonesia
    305: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": ["Maluku", "Maluku Utara"],
    },
    # 306 - Mongolia: direct (MNG)
    # 307 - Myanmar: direct (MMR)
    # 308 - Nakhchivan: admin1 from Azerbaijan
    308: {
        "strategy": "admin1",
        "adm0_a3": "AZE",
        "admin1": ["Nax\u00e7\u0131van"],
    },
    # 309 - Nepal: direct (NPL)
    # 310 - Pakistan: PAK minus Kashmir
    310: {
        "strategy": "disputed_remainder",
        "adm0_a3": "PAK",
        "subtract_disputed": ["Kashmir"],
    },
    # 311 - Papua (Indonesian): admin1 merge from Indonesia
    311: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": ["Papua", "Papua Barat"],
    },
    # 312 - Philippines: direct (PHL)
    # 313 - Russia in Asia: clip with Europe-Asia boundary
    313: {
        "strategy": "clip",
        "adm0_a3": "RUS",
        "side": "asia",
        "absorb_lon_range": [30, 59],
    },
    # 314 - Sabah: admin1 from Malaysia
    314: {
        "strategy": "admin1",
        "adm0_a3": "MYS",
        "admin1": ["Sabah"],
    },
    # 315 - Sarawak: admin1 from Malaysia
    315: {
        "strategy": "admin1",
        "adm0_a3": "MYS",
        "admin1": ["Sarawak"],
    },
    # 316 - Sikkim: admin1 from India
    316: {
        "strategy": "admin1",
        "adm0_a3": "IND",
        "admin1": ["Sikkim"],
    },
    # 317 - Singapore: direct (SGP)
    # 318 - South Ossetia: from disputed layer
    318: {
        "strategy": "disputed",
        "name": "South Ossetia",
    },
    # 319 - Sri Lanka: direct (LKA)
    # 320 - Sulawesi: admin1 merge from Indonesia
    320: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": [
            "Sulawesi Barat",
            "Sulawesi Selatan",
            "Sulawesi Tengah",
            "Sulawesi Tenggara",
            "Sulawesi Utara",
            "Gorontalo",
        ],
    },
    # 321 - Sumatra: admin1 merge from Indonesia
    321: {
        "strategy": "admin1",
        "adm0_a3": "IDN",
        "admin1": [
            "Aceh",
            "Bengkulu",
            "Jambi",
            "Kepulauan Bangka Belitung",
            "Kepulauan Riau",
            "Lampung",
            "Riau",
            "Sumatera Barat",
            "Sumatera Selatan",
            "Sumatera Utara",
        ],
    },
    # 322 - Taiwan: direct (TWN)
    # 323 - Tajikistan: direct (TJK)
    # 324 - Thailand: direct (THA)
    # 325 - Tibet: admin1 from China
    325: {
        "strategy": "admin1",
        "adm0_a3": "CHN",
        "admin1": ["Xizang"],
    },
    # 326 - Timor-Leste: direct (TLS)
    # 327 - Turkey in Asia: clip with Europe-Asia boundary
    327: {
        "strategy": "clip",
        "adm0_a3": "TUR",
        "side": "asia",
    },
    # 328 - Turkmenistan: direct (TKM)
    # 329 - Uzbekistan: direct (UZB)
    # 330 - Vietnam: direct (VNM)
}


def get_destinations() -> list[TccDestination]:
    """Return all 330 destinations as dicts with merged extraction config.

    Each dict contains the base destination fields from ``DESTINATIONS``
    plus any strategy-specific keys from ``EXTRACTIONS``.  Destinations not
    listed in ``EXTRACTIONS`` receive ``{"strategy": "direct"}`` as the default.

    Returns:
        List of 330 merged destination config dicts, one per TCC entry.
    """
    results: list[TccDestination] = []
    for idx, name, region, a2, a3, n3, sovereign, dtype in DESTINATIONS:
        d: TccDestination = {
            "tcc_index": idx,
            "name": name,
            "region": region,
            "iso_a2": a2,
            "iso_a3": a3,
            "iso_n3": n3,
            "sovereign": sovereign,
            "type": dtype,
        }
        ext = EXTRACTIONS.get(idx, {"strategy": "direct"})
        d.update(ext)
        results.append(d)
    return results
