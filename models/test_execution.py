class TestExecution:
    def __init__(
        self,
        id_test_execution: int = None,
        serial_number: int = None,
        id_test_step: int = None,
        date_start=None,
        date_end=None,
        result: str = None,
        id_equipment: int = None,
        test_step_name: str = None,
        equipment_name: str = None,
    ):
        self.id_test_execution = id_test_execution
        self.serial_number = serial_number
        self.id_test_step = id_test_step
        self.date_start = date_start
        self.date_end = date_end
        self.result = result
        self.id_equipment = id_equipment
        self.test_step_name = test_step_name
        self.equipment_name = equipment_name
