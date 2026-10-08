from datetime import datetime, timedelta
from pathlib import Path
import unittest
from dots_infrastructure.DataClasses import SimulatorConfiguration, SimulaitonDataPoint, TimeStepInformation
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
import helics as h
import numpy as np
import pvlib
from esdl.esdl_handler import EnergySystemHandler

from dots_infrastructure import CalculationServiceHelperFunctions

from PvInstallationCalculationService.pv_installation_calculation_service import CalculationServicePVSystem

BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 960


def simulator_environment_e_connection():
    return SimulatorConfiguration("PVInstallation", ["03443715-c345-45b2-9b95-bd6906ac9c83"], "Mock-PVInstallation", "127.0.0.1", BROKER_TEST_PORT, "3a7d4da8-3104-4640-ab70-b6a2b28986fc", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

class Test(unittest.TestCase):

    def setUp(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        esh = EnergySystemHandler()
        esh.load_file(str(Path(__file__).parent / 'test.esdl'))
        energy_system = esh.get_energy_system()
        self.energy_system = energy_system

    def test_predict_solar_power(self):

        # Arrange
        service = CalculationServicePVSystem()
        service.influx_connector = InfluxDBMock()
        pv_dispatch_params = {}

        pv_dispatch_params["solar_irradiance"] = [238.6666667, 295.6666667, 455, 366.3333333, 165, 228, 799, 808.3333333, 316.6666667, 335.3333333, 556.3333333, 650.3333333, 519, 656, 868, 889.6666667, 882.6666667, 888.3333333, 910.3333333, 902.3333333, 844.6666667, 830, 826.6666667, 783, 772.6666667, 705.3333333, 340.3333333, 430.6666667, 607, 507.6666667, 488.3333333, 458.6666667, 483.3333333, 439.3333333, 405.3333333, 295.6666667, 237.6666667, 234.3333333, 185.3333333, 245.3333333, 166, 142.3333333, 100, 68, 17, 12, 5, 2.333333333]
        simulation_time = datetime(2026, 5, 20, 8, 0)
        service.init_calculation_service(self.energy_system)
        pv_system = service.pv_systems["03443715-c345-45b2-9b95-bd6906ac9c83"]

        # Execute
        ret_val = service.predict_solar_power(pv_dispatch_params, simulation_time, TimeStepInformation(1,2), "03443715-c345-45b2-9b95-bd6906ac9c83", self.energy_system)

        # Assert
        self.assertEqual(len(ret_val.potential_active_power), 48)


    def test_current_pv_power_production(self):

        # Arrange
        service = CalculationServicePVSystem()
        service.influx_connector = InfluxDBMock()
        pv_dispatch_params = {}

        pv_dispatch_params["current_solar_irradiance"] = 238.6666667
        simulation_time = datetime(2026, 5, 20, 8, 0)
        service.init_calculation_service(self.energy_system)
        pv_system = service.pv_systems["03443715-c345-45b2-9b95-bd6906ac9c83"]

        # Execute
        ret_val = service.current_pv_power_production(pv_dispatch_params, simulation_time, TimeStepInformation(1,2), "03443715-c345-45b2-9b95-bd6906ac9c83", self.energy_system)

        # Assert
        self.assertGreater(ret_val.pv_active_power, 0.0)

if __name__ == '__main__':
    unittest.main()
