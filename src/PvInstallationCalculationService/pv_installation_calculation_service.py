# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from esdl import esdl
import helics as h
import numpy as np
import pvlib
from dots_infrastructure.DataClasses import EsdlId, TimeStepInformation
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from dots_infrastructure.CalculationServiceHelperFunctions import get_single_param_with_name
from esdl import EnergySystem, PVInstallation

from PvInstallationCalculationService.pv_installation_calculation_service_base import PvInstallationCalculationServiceBase
from PvInstallationCalculationService.pv_installation_calculation_service_dataclasses import CurrentPvPowerProductionOutput, PredictSolarPowerOutput

FORECAST_INTERVAL_SECONDS = 900

class CalculationServicePVSystem(PvInstallationCalculationServiceBase):

    def init_calculation_service(self, energy_system: esdl.EnergySystem):
        LOGGER.info("init calculation service")
        self.pv_systems: dict[EsdlId, PVInstallation] = {}

        for obj in energy_system.eAllContents():
            if hasattr(obj, "id") and obj.id in self.simulator_configuration.esdl_ids:
                pvsystem = obj
                self.pv_systems[obj.id]      = pvsystem


    def _calculate_pv_power(self, ghi_values: list[float], simulation_time: datetime, pv_system: PVInstallation) -> list[float]:
        surface_area = pv_system.surfaceArea
        panel_efficiency = pv_system.panelEfficiency
        assert surface_area > 0.0, "provide surface area with value bigger than 0"
        assert panel_efficiency > 0.0, "provide panel efficiency with value bigger than 0"
        if not ghi_values:
            return []

        timestamps = [
            simulation_time + timedelta(seconds=FORECAST_INTERVAL_SECONDS * index)
            for index in range(len(ghi_values))
        ]
        solar_position = pvlib.solarposition.get_solarposition(
            timestamps,
            latitude=pv_system.geometry.lat,
            longitude=pv_system.geometry.lon,
        )
        irradiance_components = pvlib.irradiance.erbs(
            np.asarray(ghi_values),
            solar_position["apparent_zenith"],
            solar_position.index,
        )
        plane_of_array = pvlib.irradiance.get_total_irradiance(
            surface_tilt=pv_system.angle,
            surface_azimuth=pv_system.orientation,
            solar_zenith=solar_position["apparent_zenith"],
            solar_azimuth=solar_position["azimuth"],
            dni=irradiance_components["dni"],
            ghi=np.asarray(ghi_values),
            dhi=irradiance_components["dhi"],
        )
        return (plane_of_array["poa_global"] * surface_area * panel_efficiency).tolist()


    def predict_solar_power(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        solar_irradiance = get_single_param_with_name(param_dict, "solar_irradiance")
        solar_power = self._calculate_pv_power(solar_irradiance, simulation_time, self.pv_systems[esdl_id])

        ret_val = PredictSolarPowerOutput(solar_power)

        return ret_val


    def current_pv_power_production(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        solar_irradiance = get_single_param_with_name(param_dict, "current_solar_irradiance")
        solar_power = self._calculate_pv_power(
            [solar_irradiance],
            simulation_time,
            self.pv_systems[esdl_id],
        )[0]

        ret_val = CurrentPvPowerProductionOutput(solar_power)

        self.influx_connector.set_time_step_data_point(esdl_id, "current_pv_power_production", simulation_time, solar_power)

        return ret_val

if __name__ == "__main__":
    helics_simulation_executor = CalculationServicePVSystem()
    helics_simulation_executor.start_simulation()
    helics_simulation_executor.stop_simulation()
