from __future__ import print_function
from sfc_models.objects import *
from sfc_models.sector import Sector

mod = Model()
ExternalSector(mod)
ca = Country(mod, 'CA', currency='CAD')
us = Country(mod, 'US', currency='USD')

hh_ca = Sector(ca, 'HH', has_F=True)
hh_ca.AddVariable('GIFT', 'Sending money..', '5.')
hh_us = Sector(us, 'HH', has_F=True)
mod.RegisterCashFlow(hh_ca, hh_us, 'GIFT')
mod.main()
mod.TimeSeriesCutoff=1
series_list = ('CA_HH__F', 'US_HH__F', 'EXT_FX__NET_CAD', 'EXT_FX__NET_USD')
for s in series_list:
    print(s, mod.GetTimeSeries(s)[1])


print('Try #2 - Add GoldStandardGovernment objects')
mod = Model()
ExternalSector(mod)
ca = Country(mod, 'CA', currency='CAD')
us = Country(mod, 'US', currency='USD')
gov_ca = GoldStandardGovernment(ca, 'GOV')
gov_us = GoldStandardGovernment(us, 'GOV')
# The need for the next step may be fixed...
gov_ca.AddVariable('T', 'Taxes', '0.')
gov_us.AddVariable('T', 'Taxes', '0.')


hh_ca = Sector(ca, 'HH', has_F=True)
hh_ca.AddVariable('GIFT', 'Sending money..', '5.')
hh_us = Sector(us, 'HH', has_F=True)
mod.RegisterCashFlow(hh_ca, hh_us, 'GIFT')
mod.main()
mod.TimeSeriesCutoff=1
series_list = ('CA_HH__F', 'US_HH__F', 'EXT_FX__NET_CAD', 'EXT_FX__NET_USD')
print('Net balance fixed')
for s in series_list:
    print(s, mod.GetTimeSeries(s)[1])

series_list = ('CA_GOV__GOLDPURCHASES', 'US_GOV__GOLDPURCHASES', )
print('Net balance fixed')
for s in series_list:
    print(s, mod.GetTimeSeries(s)[1])



