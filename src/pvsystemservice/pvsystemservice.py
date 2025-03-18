# -*- coding: utf-8 -*-
from datetime import datetime
from esdl import esdl
import helics as h
from dots_infrastructure.DataClasses import EsdlId, HelicsCalculationInformation, PublicationDescription, SubscriptionDescription, TimeStepInformation, TimeRequestType
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from dots_infrastructure.CalculationServiceHelperFunctions import get_single_param_with_name
from esdl import EnergySystem

class CalculationServicePVSystem(HelicsSimulationExecutor):

    def __init__(self):
        super().__init__()

        subscriptions_values = [
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                    input_name="solar_irradiance",
                                    input_unit="Wm2",
                                    input_type=h.HelicsDataType.VECTOR)
        ]

        publication_values = [
            PublicationDescription(global_flag=True,
                                   esdl_type="PVInstallation",
                                   output_name="potential_active_power",
                                   output_unit="W",
                                   data_type=h.HelicsDataType.VECTOR)
        ]

        pvsystem_period_in_seconds = 900

        calculation_information = HelicsCalculationInformation(
            time_period_in_seconds=pvsystem_period_in_seconds,
            offset=0,
            uninterruptible=False,
            wait_for_current_time_update=False,
            terminate_on_error=True,
            calculation_name="predict_solar_power",
            inputs=subscriptions_values,
            outputs=publication_values,
            calculation_function=self.predict_solar_power
        )
        self.add_calculation(calculation_information)

        subscriptions_values = [
            SubscriptionDescription("EnvironmentalProfiles", "solar_irradiance_up_to_next_day", "Wm2", h.HelicsDataType.VECTOR)
        ]

        publication_values = [
            PublicationDescription(True, "PVInstallation", "potential_active_power_up_to_next_day", "W", h.HelicsDataType.VECTOR)
        ]

        pvsystem_period_in_seconds = 900

        calculation_information_schedule = HelicsCalculationInformation(pvsystem_period_in_seconds, 0, False, False, True, "potential_active_power_up_to_next_day",subscriptions_values, publication_values, self.potential_active_power_up_to_next_day)
        self.add_calculation(calculation_information_schedule)

    def init_calculation_service(self, energy_system: esdl.EnergySystem):
        LOGGER.info("init calculation service")
        self.surface_area: dict[EsdlId, float] = {}
        self.panel_efficiency: dict[EsdlId, float] = {}

        for esdl_id in self.simulator_configuration.esdl_ids:
            for obj in energy_system.eAllContents():
                if hasattr(obj, "id") and obj.id == esdl_id:
                    pvsystem = obj

            self.surface_area[esdl_id]      = pvsystem.surfaceArea
            self.panel_efficiency[esdl_id]  = pvsystem.panelEfficiency


    def predict_solar_power(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        # Receive solar irradiance data from param_dict.
        solar_irradiance = get_single_param_with_name(param_dict, "solar_irradiance")
        surface_area = self.surface_area[esdl_id]
        panel_efficiency = self.panel_efficiency[esdl_id]

        assert surface_area > 0.0, "provide surface area with value bigger than 0"
        assert panel_efficiency > 0.0, "provide panel efficiency with value bigger than 0"

        solar_power = [panel_efficiency * surface_area * irr for irr in solar_irradiance]

        ret_val = {}
        ret_val["potential_active_power"] = solar_power

        return ret_val

    def potential_active_power_up_to_next_day(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):

        # Receive solar irradiance data from param_dict.
        solar_irradiance_up_to_next_day = get_single_param_with_name(param_dict, "solar_irradiance_up_to_next_day")
        if solar_irradiance_up_to_next_day:

            surface_area = self.surface_area[esdl_id]
            panel_efficiency = self.panel_efficiency[esdl_id]
            assert surface_area > 0.0, "provide surface area with value bigger than 0"
            assert panel_efficiency > 0.0, "provide panel efficiency with value bigger than 0"
            solar_power_up_to_next_day = [panel_efficiency * surface_area * irr for irr in solar_irradiance_up_to_next_day]
        else:
            solar_power_up_to_next_day = []

        ret_val = {}
        ret_val["potential_active_power_up_to_next_day"] = solar_power_up_to_next_day
        return ret_val

if __name__ == "__main__":
    helics_simulation_executor = CalculationServicePVSystem()
    helics_simulation_executor.start_simulation()
    helics_simulation_executor.stop_simulation()
