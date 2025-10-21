# This final fixture will return the properly configured backend client, to be used in tests

###########################
### CONFIGURATION START ###
###########################

#########################
### CONFIGURATION END ###
#########################

# Pull all features from the base ragger conftest using the overridden configuration
pytest_plugins = ("ragger.conftest.base_conftest", )
