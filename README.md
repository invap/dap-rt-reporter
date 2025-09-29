# dap-rt-reporter

Python library to configure, execute the SUT and then report the execution trace

## Useful links

* <https://github.com/tomlin7/debug-adapter-client>

## Using docker

1. First build the image

    ``` sh
    docker build . -t dap-rt-reporter-env
    ```

1. Then

    ``` sh
    docker run -it -v$PWD:/home/workspace dap-rt-reporter-env
    ```

    Once inside the container:

    ``` sh
    poetry install
    ```

    To execute the unit tests:

    ``` sh
    poetry env activate
    poetry run python -m unittest discover -s tests/integration
    ```

    To execute the program:

    ``` sh
    poetry env activate
    poetry run python -m dap_rt_reporter\
      --sut tests/integration/resources/simple_test/target/debug/simple_test \
      --desc tests/integration/resources/simple_test_config.csv --log execute.log
    ```

## Usage

The project can be used as a library which you can use to add events
programmatically, as shown below.

```python
from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.event.checkpoint_reached_event import CheckpointReachedEvent
from dap_rt_reporter.event.variable_value_assigned_event import (
    VariableValueAssignedEvent,
)

# Binary, log paths and source
sut_path = "tests/integration/resources/simple_test/target/debug/simple_test"
execution_log = "execute.log"
source_path = "tests/integration/resources/simple_test/src/main.rs"
# Initialize reporter
reporter = Reporter(
    executable_path=sut_path, execution_trace_log_path=execution_log
)

# Set checkpoint event on line 12
reporter.set_event(
    CheckpointReachedEvent(
        source_path=source_path,
        line=12,
        before=True,
        name="test_checkpoint",
    )
)

# Set variable value assign event on line 17, reads the value of 'x'
reporter.set_event(
    VariableValueAssignedEvent(
        source_path=source_path,
        line=17,
        before=True,
        name="var_x",
        expression="x",
    )
)

# Start program execution and reporting
terminated = reporter.execute()
reporter.close()
```

It can also be used as a program instead, to run use the following command.

``` sh
python -m dap_rt_reporter --sut sut_binary \
--desc process_descriptor_file --log log_file
```

In order to run the program you need the following things:

1. A compiled binary with debugging symbols.
1. A csv file with the execution report specification which is described below.
1. A path to the resulting log. If the log file already exists you must use -f
flag to overwrite it.

## Execution report specification

In order to specify the program execution a file with the following format is needed:

```csv
[SOURCE]:[LINE]:[b|a],[EVENT],[EVENT_NAME],[*ARGS]
```

Each line of the descriptor file represents an event which is correlated with the SUT. The reporter takes as input this descriptor and uses it to output the behavior of the SUT, this log file is then used by the monitor to assert if the behavior matches the modeled behavior.

The events are described by:

1. SOURCE: Source file in which the event happens.
1. LINE: Line which correlates with the event.
1. Before|After: indicates if the event should be reported before or after line execution.
1. EVENT: current accepted events are specified below.
1. EVENT_NAME: name used when reporting.
1. *ARGS: extra arguments used by certain events.

### Events

The currently supported events are:

1. Process events:
    1. checkpoint_reached: Represents arriving at a checkpoint.

        ```csv
        source:20:b,checkpoint_reached,loop_inv_chk
        ```

    1. task_started: Marks the beginning of a task.

        ```csv
        source:16:b,task_started,loop
        ```

    1. task_finished: Marks the end of a task.

        ```csv
        source:22:b,task_finished,loop
        ```

1. State events:
    1. variable_value_assigned: Check the value of a variable or expression
    in current stack frame.

        ```csv
        source:17:b,variable_value_assigned,var_x,x
        ```

        It takes as an extra argument the variable or expression you want to evaluate.
1. Timed events:
    1. clock_start: Start a clock which can be used to track time.

        ```csv
        source:14:b,clock_start,sleep_clk
        ```

    1. clock_pause: Pause an active clock.

        ```csv
        source:14:b,clock_pause,sleep_clk
        ```

    1. clock_resume: Resume a paused clock.

        ```csv
        source:25:b,clock_start,sleep_clk
        ```

    1. clock_reset: Reset a clock and start counting.

        ```csv
        source:22:b,clock_reset,sleep_clk
        ```

1. Component events:
    1. component_event: Indicates a component function call. For more information on component events and digital twins please refer to the [rt-monitor](https://github.com/invap/rt-monitor).

        ```csv
        source:20:b,component_event,component,component_func,x,y
        ```

        It takes as extra arguments the component function that is being called and the arguments of the call.

After running the example project with simple_test_config.csv the output log should resemble:

```csv
1745842785066343,state_event,variable_value_assigned,var_x,1
1745842785068949,state_event,variable_value_assigned,var_y,1
1745842785070587,timed_event,clock_start,sleep_clk
1745842785070587,timed_event,clock_pause,sleep_clk
1745842785071511,state_event,variable_value_assigned,var_i,0
1745842785071511,process_event,task_started,loop
1745842785072929,state_event,variable_value_assigned,var_x,2
1745842785074289,state_event,variable_value_assigned,var_y,3
1745842785075630,process_event,checkpoint_reached,loop_inv_chk
1745842785075630,component_event,component,component_func,2,3
1745842785077140,process_event,task_finished,loop
1745842785077140,timed_event,clock_reset,sleep_clk
1745842787078188,timed_event,clock_pause,sleep_clk
1745842787078188,process_event,checkpoint_reached,chk
...

```

The output format contains:

```csv
[TIMESTAMP],[EVENT_TYPE],[EVENT],[EVENT_NAME],[*ARGS]
```

1. TIMESTAMP: The moment in which the event took place in microseconds since epoch.
1. EVENT_TYPE: The type of event (process, state).
1. EVENT: The event in question as described above.
1. EVENT_NAME: The name used to report the event.
1. *ARGS: Extra arguments used for the event.

## Complete work suite

For more information on the complete work suite check [here.](SUITE.md)

## Contributing

Contributions are what make the open source community such an amazing
place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork
the repo and create a pull request. You can also simply open an
issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
1. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the Branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request
