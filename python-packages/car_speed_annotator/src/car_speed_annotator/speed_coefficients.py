#!/usr/bin/env python3


"""Speed coefficients (in relation to speed limit) for the Helsinki metropolitan region."""


from .ykr_vyohykkeet import YkrVyöhyke


__all__ = ["SPEED_COEFFICIENTS"]


# Actually driven speeds as a fraction of the speed limit

# These data are recreated with the methods presented in Eero Perola’s MSc
# thesis, in which he used TomTom floating car data to compare speed limit and
# measured speeds
#
# Perola, E. (2023) Driving speed deviation from the speed limits - an analysis
# using floating car data in the Helsinki Metropolitan Area. MSc thesis,
# University of Helsinki. http://hdl.handle.net/10138/358181.

# Times of the day, as used below, refer to floating car
# data averaged over the following time windows:
#   - average:      5:00-6:00, 9:00-10:00, 15:00-16:00,
#                   17:00-18:00, 21:00-22:00
#   - midday:       10:00-15:00
#   - nighttime:     0:00-05:00
#   - rush-hour:    7:00-9:00

# The speed limits are in km/h


SPEED_COEFFICIENTS = {
    YkrVyöhyke.ALAKESKUKSEN_JALANKULKUVYÖHYKE: {
        "average": {
            50: 0.8605,
            60: 1.1025,
            80: 1.0136,
            100: 0.9352,
        },
        "midday": {
            50: 0.8699,
            60: 1.1127,
            80: 1.0322,
            100: 0.9443,
        },
        "nighttime": {
            50: 0.9712,
            60: 1.1524,
            80: 0.9911,
            100: 0.9316,
        },
        "rush-hour": {
            50: 0.8937,
            60: 1.0944,
            80: 1.0027,
            100: 0.9275,
        },
    },
    YkrVyöhyke.ALAKESKUKSEN_JALANKULKUVYÖHYKE_INTENSIIVINEN_JOUKKOLIIKENNE: {
        "average": {
            30: 0.9568,
            40: 0.9002,
            50: 0.7616,
            60: 0.8688,
            70: 0.898,
            80: 0.9908,
            100: 0.9591,
        },
        "midday": {
            30: 0.9548,
            40: 0.9047,
            50: 0.765,
            60: 0.8857,
            70: 0.9076,
            80: 1.0007,
            100: 0.9648,
        },
        "nighttime": {
            30: 1.1111,
            40: 1.0161,
            50: 0.8906,
            60: 0.9296,
            70: 0.9426,
            80: 1.0026,
            100: 0.948,
        },
        "rush-hour": {
            30: 0.9356,
            40: 0.8898,
            50: 0.7647,
            60: 0.8769,
            70: 0.888,
            80: 0.9915,
            100: 0.9494,
        },
    },
    YkrVyöhyke.ALAKESKUKSEN_JALANKULKUVYÖHYKE_JOUKKOLIIKENNE: {
        "average": {
            30: 1.0471,
            40: 0.9316,
            50: 0.752,
            60: 0.8283,
            70: 0.8994,
            80: 0.9326,
        },
        "midday": {
            30: 1.0553,
            40: 0.9327,
            50: 0.7587,
            60: 0.828,
            70: 0.9088,
            80: 0.9349,
        },
        "nighttime": {
            30: 1.1481,
            40: 0.9797,
            50: 0.856,
            60: 0.9101,
            70: 0.9369,
            80: 0.9427,
        },
        "rush-hour": {
            30: 0.9922,
            40: 0.9178,
            50: 0.7474,
            60: 0.8193,
            70: 0.9149,
            80: 0.9347,
        },
    },
    YkrVyöhyke.AUTOVYÖHYKE: {
        "average": {
            30: 0.8967,
            40: 1.0111,
            50: 0.9779,
            60: 0.966,
            70: 1.0203,
            80: 0.9827,
            100: 0.9663,
            120: 0.8482,
        },
        "midday": {
            30: 0.9149,
            40: 1.022,
            50: 0.9903,
            60: 0.9743,
            70: 1.024,
            80: 0.9889,
            100: 0.9697,
            120: 0.8541,
        },
        "nighttime": {
            30: 0.9228,
            40: 1.0651,
            50: 1.0324,
            60: 1.0019,
            70: 1.0324,
            80: 0.997,
            100: 0.9452,
            120: 0.8254,
        },
        "rush-hour": {
            30: 0.8836,
            40: 0.992,
            50: 0.9621,
            60: 0.9596,
            70: 1.0159,
            80: 0.9814,
            100: 0.9669,
            120: 0.8421,
        },
    },
    YkrVyöhyke.INTENSIIVINEN_JOUKKOLIIKENNEVYÖHYKE: {
        "average": {
            30: 0.8087,
            40: 0.8277,
            50: 0.8357,
            60: 0.8359,
            70: 0.9587,
            80: 0.9568,
            100: 0.9647,
        },
        "midday": {
            30: 0.8235,
            40: 0.8336,
            50: 0.8413,
            60: 0.8413,
            70: 0.9642,
            80: 0.9652,
            100: 0.9681,
        },
        "nighttime": {
            30: 0.9029,
            40: 0.9415,
            50: 0.932,
            60: 0.9317,
            70: 0.9666,
            80: 0.9697,
            100: 0.9518,
        },
        "rush-hour": {
            30: 0.7767,
            40: 0.8129,
            50: 0.8236,
            60: 0.8382,
            70: 0.961,
            80: 0.9559,
            100: 0.9656,
        },
    },
    YkrVyöhyke.JOUKKOLIIKENNEVYÖHYKE: {
        "average": {
            30: 0.9688,
            40: 0.9789,
            50: 0.8899,
            60: 0.9272,
            70: 0.9766,
            80: 0.9861,
            100: 0.9572,
            120: 0.8556,
        },
        "midday": {
            30: 0.9797,
            40: 0.9865,
            50: 0.8928,
            60: 0.9326,
            70: 0.9808,
            80: 0.9915,
            100: 0.9602,
            120: 0.8617,
        },
        "nighttime": {
            30: 1.0472,
            40: 1.0496,
            50: 0.93,
            60: 0.9868,
            70: 0.9906,
            80: 0.9993,
            100: 0.9383,
            120: 0.8342,
        },
        "rush-hour": {
            30: 0.9334,
            40: 0.9681,
            50: 0.8815,
            60: 0.9189,
            70: 0.9765,
            80: 0.9876,
            100: 0.9565,
            120: 0.8455,
        },
    },
    YkrVyöhyke.KESKUSTAN_JALANKULKUVYÖHYKE: {
        "average": {
            30: 0.6751,
            40: 0.7391,
            50: 0.7155,
            60: 0.6688,
            80: 0.8364,
        },
        "midday": {
            30: 0.6626,
            40: 0.7435,
            50: 0.7228,
            60: 0.675,
            80: 0.8501,
        },
        "nighttime": {
            30: 0.8564,
            40: 0.937,
            50: 0.8465,
            60: 0.8212,
            80: 0.854,
        },
        "rush-hour": {
            30: 0.6974,
            40: 0.7562,
            50: 0.7107,
            60: 0.5854,
            80: 0.8252,
        },
    },
    YkrVyöhyke.KESKUSTAN_REUNAVYÖHYKE: {
        "average": {
            30: 0.679,
            40: 0.9703,
            50: 0.8179,
            70: 0.985,
            80: 1.0146,
        },
        "midday": {
            30: 0.649,
            40: 0.9735,
            50: 0.8226,
            70: 0.99,
            80: 1.0233,
        },
        "nighttime": {
            30: 0.6777,
            40: 1.1342,
            50: 0.9278,
            70: 1.0007,
            80: 1.0233,
        },
        "rush-hour": {
            30: 0.7165,
            40: 0.9735,
            50: 0.8066,
            70: 0.985,
            80: 1.0271,
        },
    },
    YkrVyöhyke.KESKUSTAN_REUNAVYÖHYKE_INTENSIIVINEN_JOUKKOLIIKENNE: {
        "average": {
            20: 2.44,
            30: 0.8425,
            40: 0.7764,
            50: 0.7798,
            60: 0.9738,
            70: 1.0182,
            80: 0.9608,
        },
        "midday": {
            20: 2.415,
            30: 0.8264,
            40: 0.7826,
            50: 0.7819,
            60: 0.9827,
            70: 1.0204,
            80: 0.9667,
        },
        "nighttime": {
            20: 2.595,
            30: 1.0402,
            40: 0.953,
            50: 0.9166,
            60: 1.0112,
            70: 1.0224,
            80: 0.9686,
        },
        "rush-hour": {
            20: 2.365,
            30: 0.8265,
            40: 0.7704,
            50: 0.7753,
            60: 0.9707,
            70: 1.0242,
            80: 0.9627,
        },
    },
    YkrVyöhyke.KESKUSTAN_REUNAVYÖHYKE_JOUKKOLIIKENNE: {
        "average": {
            30: 0.8396,
            40: 0.7696,
            50: 0.765,
            60: 0.5526,
        },
        "midday": {
            30: 0.7979,
            40: 0.741,
            50: 0.7704,
            60: 0.5614,
        },
        "nighttime": {
            30: 0.9412,
            40: 1.0294,
            50: 0.8928,
            60: 0.5912,
        },
        "rush-hour": {
            30: 0.8392,
            40: 0.7185,
            50: 0.7276,
            60: 0.5507,
        },
    },
}
