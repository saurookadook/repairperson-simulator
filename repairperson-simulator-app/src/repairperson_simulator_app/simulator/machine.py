import simpy

from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.randomizer import Randomizer


class Machine:
    """A machine produces parts and may get broken every now and then.

    If it breaks, it requests a *repairperson* and continues the production
    after the it is repaired.

    A machine has a *name* and a number of *parts_made* thus far.

    """

    def __init__(
        self, env: simpy.Environment, id: int, name: str, randomizer: Randomizer
    ):
        self.env = env
        self.id = id
        self.name = name
        self.is_broken = False
        self.parts_made = 0
        self.randomizer = randomizer

    def start_work(self, repairperson: Operator):
        """Start the machine's operation."""
        self.working_process = self.env.process(self.working(repairperson))
        self.env.process(self.intermittently_break())

    def working(self, repairperson: Operator):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairperson when this happens.

        """
        while True:
            done_in = self.randomizer.time_per_part()
            while done_in:
                start = self.env.now
                try:
                    yield self.env.timeout(done_in)
                    done_in = 0  # Set to 0 to exit while loop.

                except simpy.Interrupt:
                    self.broken = True
                    done_in -= self.env.now - start

                    with repairperson.request(priority=1) as req:
                        yield req
                        # TODO: get job details and pass "remaining_duration"
                        yield self.env.timeout()

                    self.broken = False

            self.parts_made += 1

    def intermittently_break(self):
        """Break the machine at random intervals."""
        while True:
            time_until_failure = self.randomizer.time_to_failure()
            yield self.env.timeout(time_until_failure)
            if not self.broken:
                self.working_process.interrupt()
