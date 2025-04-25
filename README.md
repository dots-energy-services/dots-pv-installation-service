# Calculation service for esdl_type PVInstallation:

This calculation service calculates the active power produced by a PV installation based upon the weather.

## Calculations

### predict solar power 

Send the potential active power produced by the pv installation depending on the input from the weather service.
#### Input parameters
|Name            |esdl_type            |data_type            |unit            |description            |
|----------------|---------------------|---------------------|----------------|-----------------------|
|solar_irradiance|EnvironmentalProfiles|VECTOR|Wm2|The expected solar irradiance for the coming 12 hours as predicted by the weather service.|
#### Output values
|Name             |data_type             |unit             |description             |
|-----------------|----------------------|-----------------|------------------------|
|potential_active_power|VECTOR|W|The potential active power produced by the PV installation for the coming 12 hours based upon the weather.|

### Relevant links
|Link             |description             |
|-----------------|------------------------|
|[PVInstallation](https://energytransition.github.io/#router/doc-content/687474703a2f2f7777772e746e6f2e6e6c2f6573646c/PVInstallation.html)|Details on the PVInstallation esdl type|
