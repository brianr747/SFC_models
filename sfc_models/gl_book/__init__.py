"""
Models from Godley & Lavoie text.

[G&L 2012] "Monetary Economics: An Integrated Approach to credit, Money, Income, Production
and Wealth; Second Edition", by Wynne Godley and Marc Lavoie, Palgrave Macmillan, 2012.
ISBN 978-0-230-30184-9

Copyright 2016 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import sfc_models.models as models


class GL_book_model(object):
    """
    Base class for example models from [G&L 2012] for single-country models.

    Generates the sectors, either in a new model object, or an object that is passed in.

    The user supplies a country code.
    """

    def __init__(self, country_code, model=None, use_book_exogenous=True):
        """
        Constructor for an example model. Builds a single country, using a code that is passed in.

        If the user supplies an existing Model object, uses that. This allows us to embed in a multi-country model.

        :param country_code: str
        :param model: sfc_models.models.Model
        :param use_book_exo: bool
        """
        if model is None:
            model = models.Model()
        self.Model = model
        self.Country = models.Country(model, country_code, country_code)
        self.UseBookExogenous = use_book_exogenous

    def build_model(self):  # pragma: no cover   This is a virtual base class
        """
        Does the work of building the sectors within a country. Returns the Model object.

        :return: sfc_models.models.Model
        """
        return self.Model

    def expected_output(self):  # pragma: no cover  -- Virtual base class.
        """
        Returns a list of expected output. Used to validate the framework output.
        Uses the default exogenous series.

        Format:
        A list of tuples, that consist of the variable name, and (limited) time series of output.
        For example:
        [
        ('GOOD_SUP_GOOD', [0., 10., 12.]),
        ('HH_AfterTax', [0., 15., 18., 22.]),
        ]
        In this case, the variable 'GOOD_SUP_GOOD' is expected to be [0., 10., 12.] for the first 3 periods
        and
        'HH_AftterTax' is expected to be [0., 15., 18., 22.] over the fiest 4 periods.

        In other words, target outputs do not have to be the same length.
        :return: list
        """
        return []

