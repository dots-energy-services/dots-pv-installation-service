from datetime import datetime
import unittest
from pvsystemservice.pvsystemservice import CalculationServicePVSystem
from dots_infrastructure.DataClasses import SimulatorConfiguration, SimulaitonDataPoint, TimeStepInformation
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
import helics as h
from esdl.esdl_handler import EnergySystemHandler

from dots_infrastructure import CalculationServiceHelperFunctions

BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 960

def simulator_environment_e_connection():
    return SimulatorConfiguration("PVInstallation", ["3a7d4da8-3104-4640-ab70-b6a2b28986fc"], "Mock-PVInstallation", "127.0.0.1", BROKER_TEST_PORT, "3a7d4da8-3104-4640-ab70-b6a2b28986fc", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

class Test(unittest.TestCase):

    def setUp(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        esh = EnergySystemHandler()
        esh.load_file('test.esdl')
        energy_system = esh.get_energy_system()
        self.energy_system = energy_system

    def test_predict_solar_power(self):

        # Arrange
        service = CalculationServicePVSystem()
        service.influx_connector = InfluxDBMock()
        pv_dispatch_params = {}

        pv_dispatch_params["solar_irradiance"] = [8.333333333333334, 16.666666666666668, 25.0, 33.333333333333336, 59.72222222222223, 86.11111111111111, 112.5, 138.88888888888889, 174.99999999999997, 211.1111111111111, 247.22222222222223, 283.3333333333333, 308.3333333333333, 333.3333333333333, 358.33333333333326, 383.3333333333333, 376.38888888888886, 369.44444444444446, 362.5, 355.55555555555554, 309.72222222222223, 263.8888888888889, 218.0555555555556, 172.22222222222223, 188.19444444444443, 204.16666666666663, 220.13888888888889, 236.11111111111111, 223.6111111111111, 211.1111111111111, 198.61111111111111, 186.1111111111111, 202.77777777777777, 219.44444444444443, 236.11111111111111, 252.77777777777777, 270.1388888888889, 287.5, 304.8611111111111, 322.22222222222223, 334.0277777777778, 345.8333333333333, 357.63888888888886, 369.44444444444446, 340.2777777777778, 311.1111111111111, 281.94444444444446, 252.77777777777777, 213.19444444444449]
        service.init_calculation_service(self.energy_system)

        # Execute
        ret_val = service.predict_solar_power(pv_dispatch_params, datetime(2024,1,1), TimeStepInformation(1,2), "3a7d4da8-3104-4640-ab70-b6a2b28986fc", self.energy_system)

        # Assert
        expected_outcome = [0.2 * 14 * irr for irr in pv_dispatch_params["solar_irradiance"]]
        self.assertListEqual(ret_val["potential_active_power"], expected_outcome)

    def test_potential_active_power_up_to_next_day(self):

        # Arrange
        service = CalculationServicePVSystem()
        service.influx_connector = InfluxDBMock()
        pv_dispatch_params = {}

        pv_dispatch_params["solar_irradiance_up_to_next_day"] = [8.333333333333334, 16.666666666666668, 25.0, 33.333333333333336, 59.72222222222223, 86.11111111111111, 112.5, 138.88888888888889, 174.99999999999997, 211.1111111111111, 247.22222222222223, 283.3333333333333, 308.3333333333333, 333.3333333333333, 358.33333333333326, 383.3333333333333, 376.38888888888886, 369.44444444444446, 362.5, 355.55555555555554, 309.72222222222223, 263.8888888888889, 218.0555555555556, 172.22222222222223, 188.19444444444443, 204.16666666666663, 220.13888888888889, 236.11111111111111, 223.6111111111111, 211.1111111111111, 198.61111111111111, 186.1111111111111, 202.77777777777777, 219.44444444444443, 236.11111111111111, 252.77777777777777, 270.1388888888889, 287.5, 304.8611111111111, 322.22222222222223, 334.0277777777778, 345.8333333333333, 357.63888888888886, 369.44444444444446, 340.2777777777778, 311.1111111111111, 281.94444444444446, 252.77777777777777, 213.19444444444449]
        service.init_calculation_service(self.energy_system)

        # Execute
        ret_val = service.potential_active_power_up_to_next_day(pv_dispatch_params, datetime(2024,1,1), TimeStepInformation(1,2), "3a7d4da8-3104-4640-ab70-b6a2b28986fc", self.energy_system)

        # Assert
        expected_outcome = [0.2 * 14 * irr for irr in pv_dispatch_params["solar_irradiance_up_to_next_day"]]
        self.assertListEqual(ret_val["potential_active_power_up_to_next_day"], expected_outcome)

if __name__ == '__main__':
    unittest.main()
